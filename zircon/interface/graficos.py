"""Widget de gráfico da interface; o desenho fica em nucleo/desenho.py."""
from matplotlib.figure import Figure
from .qt import FigureCanvasQTAgg, NavigationToolbar2QT, QCursor, QToolTip, QVBoxLayout, QWidget

from ..idiomas import N_, figura, tr
from ..nucleo.desenho import concordia, densidade, isocrona, media_ponderada  # noqa: F401 (usados pela janela)


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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figura = Figure(figsize=(7, 5), layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figura)
        lay = QVBoxLayout(self)
        barra = NavigationToolbar2QT(self.canvas, self)
        for nome, dica in DICAS_BARRA.items():
            acao = getattr(barra, "_actions", {}).get(nome)
            if acao is not None:
                acao.setToolTip(tr(dica))
                acao.setWhatsThis(tr(dica))
        lay.addWidget(barra)
        lay.addWidget(self.canvas)
        self._mostrando = False
        self.canvas.mpl_connect("motion_notify_event", self._mouse)

    def _info(self, x, y):
        """Resumo do grão no ponto (x, y) em pixels da figura, ou None."""
        from matplotlib.backend_bases import MouseEvent
        for ax in self.figura.axes:
            info_ax = getattr(ax, "zircon_info", None)
            if not info_ax:
                continue
            evento = MouseEvent("motion_notify_event", self.canvas, x, y)
            for artista, info in info_ax:
                ok, detalhe = artista.contains(evento)
                if ok:
                    return info if isinstance(info, str) else info[detalhe["ind"][0]]
        return None

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


