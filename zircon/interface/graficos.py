"""Widget de gráfico da interface; o desenho fica em nucleo/desenho.py."""
import warnings

import matplotlib
from matplotlib.figure import Figure
from .qt import FigureCanvasQTAgg, NavigationToolbar2QT, QApplication, QCursor, Qt, QToolTip, QVBoxLayout, QWidget, Signal

from ..idiomas import N_, figura, tr
from ..nucleo.desenho import concordia, densidade, isocrona, media_ponderada  # noqa: F401 (usados pela janela)


# janela escondida atrás de outra aba ou minimizada: o aviso do matplotlib não ajuda ninguém
warnings.filterwarnings("ignore", message="constrained_layout not applied")

# Dicas dos botões da barra do gráfico (o matplotlib só as tem em inglês)
DICAS_BARRA = {
    "home": N_("Voltar à vista inicial do gráfico"), "back": N_("Vista anterior"), "forward": N_("Próxima vista"),
    "pan": N_("Mover o gráfico: arraste com o botão esquerdo; com o direito, amplia ou reduz"),
    "zoom": N_("Ampliar: desenhe um retângulo sobre a área que quer ver"),
    "configure_subplots": N_("Ajustar as margens do gráfico"),
    "edit_parameters": N_("Editar eixos, títulos e curvas"),
    "save_figure": N_("Salvar este gráfico como imagem (PNG, SVG, PDF...)"),
}


class Grafico(QWidget):
    # grãos clicados (índices da tabela) e se o clique foi com Ctrl/Shift (somar à seleção)
    clicou_graos = Signal(list, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figura = Figure(figsize=(7, 5), layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figura)
        # janela escondida atrás de outra aba não pode ter tamanho zero: o matplotlib antigo falha ao desenhar
        self.canvas.setMinimumSize(240, 180)
        lay = QVBoxLayout(self)
        barra = NavigationToolbar2QT(self.canvas, self)
        for nome, dica in DICAS_BARRA.items():
            acao = getattr(barra, "_actions", {}).get(nome)
            if acao is not None:
                acao.setToolTip(tr(dica))
                acao.setWhatsThis(tr(dica))
        lay.addWidget(barra)
        lay.addWidget(self.canvas)
        self.barra = barra
        self._mostrando = False
        self._marcas = []
        self._destaque = set()
        self.canvas.mpl_connect("motion_notify_event", self._mouse)
        self.canvas.mpl_connect("button_press_event", self._clique)

    def _alvo(self, x, y):
        """(resumo, índice do grão) no ponto (x, y) em pixels da figura, ou (None, None)."""
        from matplotlib.backend_bases import MouseEvent
        for ax in self.figura.axes:
            info_ax = getattr(ax, "zircon_info", None)
            if not info_ax:
                continue
            evento = MouseEvent("motion_notify_event", self.canvas, x, y)
            for (artista, info), ident in zip(info_ax, ax.zircon_ids):
                ok, detalhe = artista.contains(evento)
                if ok:
                    if isinstance(info, str):
                        return info, ident
                    i = detalhe["ind"][0]
                    return info[i], ident[i]
        return None, None

    def _info(self, x, y):
        return self._alvo(x, y)[0]

    def _clique(self, evento):
        """Clique num grão seleciona-o na tabela e nos outros gráficos; clique no vazio limpa a seleção."""
        if evento.button != 1 or evento.inaxes is None or str(getattr(self.barra, "mode", "")):
            return  # botão direito, fora dos eixos ou durante zoom/mover
        _, ident = self._alvo(evento.x, evento.y)
        somar = bool(QApplication.keyboardModifiers() & (Qt.ControlModifier | Qt.ShiftModifier))
        self.clicou_graos.emit([] if ident is None else [ident], somar)

    def destacar(self, ids):
        """Realça os grãos selecionados (borda grossa) e marca as idades deles no histograma."""
        ids = set(ids)
        for marca in self._marcas:
            if marca.axes is not None and marca.axes in self.figura.axes:
                marca.remove()  # depois de redesenhar, as marcas antigas já sumiram com a figura
        self._marcas = []
        tinta = matplotlib.rcParams["text.color"]
        for ax in self.figura.axes:
            for (artista, _), ident in zip(getattr(ax, "zircon_info", []), getattr(ax, "zircon_ids", [])):
                if not hasattr(artista, "zircon_original"):
                    artista.zircon_original = (artista.get_linewidth(), artista.get_edgecolor())
                if isinstance(ident, list):  # pontos: um artista para todos os grãos
                    larg = [3 if i in ids else 0.5 for i in ident]
                    artista.set_linewidths(larg)
                    artista.set_edgecolors([tinta if i in ids else "none" for i in ident])
                    continue
                lw, cor = artista.zircon_original
                artista.set_linewidth(lw * 3 + 1 if ident in ids else lw)
                artista.set_edgecolor(tinta if ident in ids else cor)
                artista.set_zorder(5 if ident in ids else 1)
            idades = getattr(ax, "zircon_idades", None)
            if idades:
                for ident in list(ids)[:200]:
                    if ident in idades:
                        self._marcas.append(ax.axvline(idades[ident], color=tinta, lw=2, ls=":"))
        self._destaque = ids
        self.canvas.draw_idle()

    def info_no_ponto(self, pos):
        """Usado pelo modo explicação: resumo do grão sob o ponto pos da tela."""
        local = self.canvas.mapFromGlobal(pos)
        if not self.canvas.rect().contains(local):
            return None
        razao = getattr(self.canvas, "device_pixel_ratio", 1) or 1
        return self._info(local.x() * razao, (self.canvas.height() - local.y()) * razao)

    def _mouse(self, evento):
        """Com o mouse sobre um grão, mostra o resumo dele (amostra, idade, erro, discordância...)."""
        texto = self._info(evento.x, evento.y) if evento.inaxes is not None else None
        if texto:
            QToolTip.showText(QCursor.pos(), texto, self.canvas)
            self._mostrando = True
        elif self._mostrando:
            QToolTip.hideText()
            self._mostrando = False

    def limpar(self, texto=N_("Importe uma planilha e clique em Calcular")):
        self.figura.clear()
        ax = self.figura.add_subplot()
        ax.text(0.5, 0.5, figura(texto), ha="center", va="center", color="#666666")
        ax.set_axis_off()
        self.canvas.draw_idle()


