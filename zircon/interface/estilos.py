"""Janela para escolher a cor, o símbolo e o padrão de cada conjunto de grãos."""
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from .qt import (QCheckBox, QColor, QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QIcon, QLabel,
                 QLineEdit, QPixmap, QPushButton, QSize, QVBoxLayout)
from ..idiomas import tr
from ..nucleo import grupos

TAMANHO_ICONE = 22


def _icone(desenha):
    """Ícone pequeno desenhado pelo matplotlib, igual ao que sai nos gráficos."""
    fig = Figure(figsize=(0.32, 0.32), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    desenha(ax)
    buf = io.BytesIO()
    FigureCanvasAgg(fig).print_png(buf)
    pix = QPixmap()
    pix.loadFromData(buf.getvalue(), "PNG")
    return QIcon(pix)


def icone_simbolo(simbolo, cor="#333333"):
    def desenha(ax):
        if simbolo in grupos.SIMBOLOS and simbolo != "nenhum":
            extra = (dict(color=cor, markeredgewidth=1.5) if simbolo in grupos.SIMBOLOS_DE_TRACO
                     else dict(markerfacecolor=cor, markeredgecolor="#000000", markeredgewidth=0.6))
            ax.plot([0.5], [0.5], marker=simbolo, markersize=12, linestyle="none", **extra)
    return _icone(desenha)


def icone_padrao(hachura, cor="#666666"):
    def desenha(ax):
        ax.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, facecolor=cor + "80", edgecolor="#000000",
                               hatch=hachura or None, lw=0.8))
    return _icone(desenha)


def icone_cor(cor):
    pix = QPixmap(TAMANHO_ICONE, TAMANHO_ICONE)
    pix.fill(QColor(cor))
    return QIcon(pix)


def combo_simbolo(atual, nome):
    w = QComboBox()
    w.setIconSize(QSize(TAMANHO_ICONE, TAMANHO_ICONE))
    for cod, (nome_s, _) in grupos.SIMBOLOS.items():
        w.addItem(icone_simbolo(cod), tr(nome_s), cod)
    w.setCurrentIndex(max(0, w.findData(atual)))
    w.setAccessibleName(tr("Símbolo de {conjunto}").format(conjunto=nome))
    return w


def combo_hachura(atual, nome):
    w = QComboBox()
    w.setIconSize(QSize(TAMANHO_ICONE, TAMANHO_ICONE))
    for cod, nome_h in grupos.NOMES_HACHURA.items():
        w.addItem(icone_padrao(cod), tr(nome_h), cod)
    w.setCurrentIndex(max(0, w.findData(atual)))
    w.setAccessibleName(tr("Padrão de preenchimento de {conjunto}").format(conjunto=nome))
    return w


class _EscolheCor:
    """Escolha de cor: livre no modo comum, só a paleta segura no modo para daltônicos."""
    so_paleta = False

    def _escolha_cor(self, chave, nome, cor):
        nome_acessivel = tr("Cor de {conjunto}").format(conjunto=nome)
        if self.so_paleta:
            w = QComboBox()
            w.setIconSize(QSize(TAMANHO_ICONE, TAMANHO_ICONE))
            for c in grupos.cores_seguras():
                w.addItem(icone_cor(c), c.upper(), c)
            w.setCurrentIndex(max(0, w.findText(cor.upper())))
        else:
            w = QPushButton()
            w.setIconSize(QSize(TAMANHO_ICONE, TAMANHO_ICONE))
            w.cor = cor
            self._mostra_cor(w)
            w.clicked.connect(lambda _=False, b=w, n=nome: self._pede_cor(b, n))
        w.setAccessibleName(nome_acessivel)
        return w

    def _mostra_cor(self, botao):
        botao.setIcon(icone_cor(botao.cor))
        botao.setText(botao.cor.upper())
        botao.setToolTip(tr("Clique para escolher outra cor"))

    def _pede_cor(self, botao, nome):
        c = QColorDialog.getColor(QColor(botao.cor), self, tr("Cor de {conjunto}").format(conjunto=nome))
        if c.isValid():
            botao.cor = c.name()
            self._mostra_cor(botao)

    def _cor(self, w):
        return w.currentData() if isinstance(w, QComboBox) else w.cor


class EstilosConjuntos(_EscolheCor, QDialog):
    """Uma linha por conjunto (classe, grupo, população ou amostra): se entra no cálculo, cor, símbolo e padrão.

    No modo para daltônicos a cor só pode ser escolhida entre as da paleta segura;
    o símbolo e o padrão são livres nos dois modos, porque não dependem da cor.
    """

    def __init__(self, conjuntos, estilos, so_paleta, parent=None, destaque=None, desligados=(), fixos=()):
        super().__init__(parent)
        self.setWindowTitle(tr("Conjuntos: usar no cálculo, cores e símbolos"))
        self.so_paleta = so_paleta
        self.estilos = {k: dict(v) for k, v in (estilos or {}).items()}
        self.desligados = [k for k, _ in conjuntos if k in set(desligados)]
        lay = QVBoxLayout(self)
        aviso = (tr("Modo para daltônicos: as cores vêm só da paleta segura escolhida. O símbolo e o padrão "
                    "ajudam a separar os conjuntos sem depender da cor.") if so_paleta else
                 tr("Modo de cores comuns: qualquer cor pode ser escolhida. Para quem tem daltonismo, prefira "
                    "o modo de cores acessíveis no painel e diferencie os conjuntos também pelo símbolo."))
        rotulo = QLabel(tr("Desmarque \"No cálculo\" para tirar um conjunto de todas as contas, por exemplo os "
                           "concordantes, para calcular a concórdia ou a discórdia só com os discordantes. Os grãos "
                           "dele continuam nos gráficos, em cinza.") + "\n\n" + aviso)
        rotulo.setWordWrap(True)
        lay.addWidget(rotulo)
        grade = QGridLayout()
        for col, titulo in enumerate((tr("No cálculo"), tr("Conjunto"), tr("Cor"), tr("Símbolo"),
                                      tr("Padrão de preenchimento"))):
            grade.addWidget(QLabel("<b>" + titulo + "</b>"), 0, col)
        self.usar = {}
        self.linhas = {}
        self.cor_guardada = {}  # cor livre do modo comum, mantida quando o modo para daltônicos a esconde
        for i, (chave, nome) in enumerate(conjuntos, 1):
            cor_p, simb_p, hach_p = grupos.estilo_padrao(chave)
            e = self.estilos.get(chave, {})
            cor = e.get("cor") or cor_p
            if so_paleta and cor.upper() not in {c.upper() for c in grupos.cores_seguras()}:
                cor = cor_p
            usar = QCheckBox()
            usar.setChecked(chave not in self.desligados)
            usar.setAccessibleName(tr("Usar {conjunto} no cálculo").format(conjunto=nome))
            if chave in fixos:
                usar.setEnabled(False)
                usar.setToolTip(tr("Os rejeitados são os outliers que o próprio cálculo tirou."))
            self.usar[chave] = usar
            grade.addWidget(usar, i, 0)
            rotulo_nome = QLabel(("<b>▶ " + nome + "</b>") if chave == destaque else nome)
            grade.addWidget(rotulo_nome, i, 1)
            w_cor = self._escolha_cor(chave, nome, cor)
            grade.addWidget(w_cor, i, 2)
            w_simb = combo_simbolo(e.get("simbolo") or simb_p, nome)
            grade.addWidget(w_simb, i, 3)
            w_hach = combo_hachura(e.get("hachura", hach_p), nome)
            grade.addWidget(w_hach, i, 4)
            self.linhas[chave] = (w_cor, w_simb, w_hach, (cor_p, simb_p, hach_p))
            self.cor_guardada[chave] = e.get("cor")
            if chave == destaque:
                w_cor.setFocus()
        lay.addLayout(grade)
        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Reset)
        botoes.button(QDialogButtonBox.Ok).setText(tr("Usar estas escolhas"))
        botoes.button(QDialogButtonBox.Cancel).setText(tr("Cancelar"))
        botoes.button(QDialogButtonBox.Reset).setText(tr("Auto (cores da paleta)"))
        botoes.button(QDialogButtonBox.Reset).setToolTip(
            tr("Volta às cores, símbolos e padrões automáticos da paleta escolhida no painel ou no menu Acessibilidade."))
        botoes.button(QDialogButtonBox.Reset).clicked.connect(self._padrao)
        botoes.accepted.connect(self._aceita)
        botoes.rejected.connect(self.reject)
        lay.addWidget(botoes)

    def _padrao(self):
        self.cor_guardada.clear()
        for w_cor, w_simb, w_hach, (cor_p, simb_p, hach_p) in self.linhas.values():
            if isinstance(w_cor, QComboBox):
                w_cor.setCurrentIndex(max(0, w_cor.findText(cor_p.upper())))
            else:
                w_cor.cor = cor_p
                self._mostra_cor(w_cor)
            w_simb.setCurrentIndex(max(0, w_simb.findData(simb_p)))
            w_hach.setCurrentIndex(max(0, w_hach.findData(hach_p)))

    def _aceita(self):
        """Guarda só o que difere do padrão, para a paleta continuar valendo no resto."""
        for chave, (w_cor, w_simb, w_hach, (cor_p, simb_p, hach_p)) in self.linhas.items():
            e = {}
            if self._cor(w_cor).upper() != cor_p.upper():
                e["cor"] = self._cor(w_cor)
            elif self.so_paleta and self.cor_guardada.get(chave) and self.cor_guardada[chave].upper() not in {
                    c.upper() for c in grupos.cores_seguras()}:
                e["cor"] = self.cor_guardada[chave]
            if w_simb.currentData() != simb_p:
                e["simbolo"] = w_simb.currentData()
            if w_hach.currentData() != hach_p:
                e["hachura"] = w_hach.currentData()
            if e:
                self.estilos[chave] = e
            else:
                self.estilos.pop(chave, None)
        self.desligados = [k for k, w in self.usar.items() if w.isEnabled() and not w.isChecked()]
        self.accept()


class EstiloDoGrao(_EscolheCor, QDialog):
    """Cor, símbolo e padrão de um grão, aplicados ao conjunto dele ("Grupo") ou só a ele ("Ponto")."""
    GRUPO, PONTO, TIRAR = 1, 2, 3

    def __init__(self, analise, nome_conjunto, atual, destacado, so_paleta, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Cor e símbolo do grão {analise}").format(analise=analise))
        self.so_paleta = so_paleta
        self.escolha = None
        lay = QVBoxLayout(self)
        texto = QLabel(tr("Escolha a cor, o símbolo e o padrão. Depois decida: \"Grupo\" muda o conjunto todo "
                          "({conjunto}); \"Ponto\" muda só este grão, para destacar um núcleo, uma borda ou uma "
                          "forma curiosa, e ele ganha uma linha própria na legenda.").format(conjunto=nome_conjunto))
        texto.setWordWrap(True)
        lay.addWidget(texto)
        form = QFormLayout()
        self.w_cor = self._escolha_cor(None, analise, atual["cor"])
        self.w_simb = combo_simbolo(atual["simbolo"], analise)
        self.w_hach = combo_hachura(atual["hachura"], analise)
        self.w_rotulo = QLineEdit(atual.get("rotulo") or analise)
        self.w_rotulo.setAccessibleName(tr("Nome na legenda"))
        form.addRow(tr("Cor"), self.w_cor)
        form.addRow(tr("Símbolo"), self.w_simb)
        form.addRow(tr("Padrão de preenchimento"), self.w_hach)
        form.addRow(tr("Nome na legenda (só para o ponto)"), self.w_rotulo)
        lay.addLayout(form)
        botoes = QDialogButtonBox()
        b_grupo = botoes.addButton(tr("Grupo"), QDialogButtonBox.AcceptRole)
        b_grupo.setToolTip(tr("Aplica ao conjunto todo: {conjunto}").format(conjunto=nome_conjunto))
        b_ponto = botoes.addButton(tr("Ponto"), QDialogButtonBox.AcceptRole)
        b_ponto.setToolTip(tr("Aplica só a este grão, que aparece em destaque na legenda"))
        b_grupo.clicked.connect(lambda: self._fecha(self.GRUPO))
        b_ponto.clicked.connect(lambda: self._fecha(self.PONTO))
        if destacado:
            b_tirar = botoes.addButton(tr("Tirar o destaque"), QDialogButtonBox.ResetRole)
            b_tirar.setToolTip(tr("O grão volta a ter a cor e o símbolo do seu conjunto"))
            b_tirar.clicked.connect(lambda: self._fecha(self.TIRAR))
        botoes.addButton(tr("Cancelar"), QDialogButtonBox.RejectRole).clicked.connect(self.reject)
        lay.addWidget(botoes)

    def estilo(self):
        return {"cor": self._cor(self.w_cor), "simbolo": self.w_simb.currentData(),
                "hachura": self.w_hach.currentData(), "rotulo": self.w_rotulo.text().strip()}

    def _fecha(self, escolha):
        self.escolha = escolha
        self.accept()
