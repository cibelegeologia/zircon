"""Acessibilidade: tamanho da letra, tema (claro, escuro, alto contraste) e cores dos gráficos.

As escolhas ficam nas preferências do usuário (QSettings) e valem para a
janela e para os gráficos da tela. As figuras exportadas para publicação
usam sempre fundo branco, mas seguem a paleta e os padrões escolhidos.
"""
from .qt import QApplication, QColor, QPalette

from ..idiomas import N_
from ..nucleo import grupos

TAMANHOS = {"normal": (N_("Normal"), 1.0), "grande": (N_("Grande"), 1.25), "muito_grande": (N_("Muito grande"), 1.5),
            "enorme": (N_("Enorme"), 2.0)}
TEMAS = {"sistema": N_("Como o sistema"), "claro": N_("Claro"), "escuro": N_("Escuro"),
         "alto_contraste": N_("Alto contraste (fundo preto)"), "alto_contraste_claro": N_("Alto contraste (fundo branco)")}
ACESSIVEIS = ("okabe_ito", "tol", "cividis", "cinza")
PALETAS = {"comum": N_("Cores comuns"),
           "okabe_ito": N_("Okabe-Ito (segura para daltonismo)"),
           "tol": N_("Tol (cores vivas, segura para daltonismo)"),
           "cividis": N_("Cividis (azul e amarelo, para todos os tipos de daltonismo)"),
           "cinza": N_("Tons de cinza (impressão em preto e branco)")}
PADRAO = {"tamanho": "normal", "tema": "sistema", "paleta": "comum", "padroes": False}

# Cores de cada tema: fundo, texto, campos, texto dos campos, botão, destaque, texto do destaque, link
_CORES = {
    "claro": ("#F4F4F4", "#111111", "#FFFFFF", "#111111", "#E6E6E6", "#0072B2", "#FFFFFF", "#0060A0"),
    "escuro": ("#1E1E1E", "#EAEAEA", "#2A2A2A", "#F0F0F0", "#333333", "#56B4E9", "#000000", "#7CC8F2"),
    "alto_contraste": ("#000000", "#FFFFFF", "#000000", "#FFFFFF", "#000000", "#FFD700", "#000000", "#FFFF00"),
    "alto_contraste_claro": ("#FFFFFF", "#000000", "#FFFFFF", "#000000", "#FFFFFF", "#0000C0", "#FFFFFF", "#0000C0"),
}
_estilo_original = {}


def ler(config):
    def valor(chave, tipo=str):
        try:
            v = config.value(chave, PADRAO[chave], type=tipo)
        except TypeError:
            v = config.value(chave, PADRAO[chave])
        return v
    a = {"tamanho": valor("tamanho"), "tema": valor("tema"), "paleta": valor("paleta"),
         "padroes": valor("padroes", bool)}
    a["tamanho"] = a["tamanho"] if a["tamanho"] in TAMANHOS else "normal"
    a["tema"] = a["tema"] if a["tema"] in TEMAS else "sistema"
    a["paleta"] = a["paleta"] if a["paleta"] in PALETAS else "comum"
    return a


def aplicar(app, a):
    """Aplica letra, tema e paleta ao programa inteiro."""
    if not _estilo_original:
        _estilo_original.update(fonte=QApplication.font(), estilo=app.style().objectName(),
                                paleta=QApplication.palette())
    escala = TAMANHOS[a["tamanho"]][1]
    fonte = _estilo_original["fonte"]
    fonte = type(fonte)(fonte)
    if fonte.pointSizeF() > 0:
        fonte.setPointSizeF(fonte.pointSizeF() * escala)
    else:
        fonte.setPixelSize(round(fonte.pixelSize() * escala))
    app.setFont(fonte)
    grupos.definir_paleta(a["paleta"], a["padroes"])
    if a["tema"] == "sistema":
        app.setStyle(_estilo_original["estilo"] or "Fusion")
        app.setPalette(_estilo_original["paleta"])
        app.setStyleSheet("")
        return
    fundo, texto, campo, texto_campo, botao, destaque, texto_destaque, link = _CORES[a["tema"]]
    app.setStyle("Fusion")  # o estilo nativo do Windows ignora parte das cores escolhidas
    p = QPalette()
    for papel, cor in ((QPalette.Window, fundo), (QPalette.WindowText, texto), (QPalette.Base, campo),
                       (QPalette.AlternateBase, botao), (QPalette.Text, texto_campo), (QPalette.Button, botao),
                       (QPalette.ButtonText, texto), (QPalette.ToolTipBase, campo), (QPalette.ToolTipText, texto),
                       (QPalette.Highlight, destaque), (QPalette.HighlightedText, texto_destaque),
                       (QPalette.Link, link), (QPalette.BrightText, destaque), (QPalette.PlaceholderText, texto)):
        p.setColor(papel, QColor(cor))
    for papel in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, papel, QColor("#808080"))
    app.setPalette(p)
    if a["tema"].startswith("alto_contraste"):
        # bordas grossas e foco bem visível para quem enxerga pouco
        app.setStyleSheet(
            f"QWidget:focus {{ border: 3px solid {destaque}; }}"
            f"QPushButton, QComboBox, QLineEdit, QDoubleSpinBox, QSpinBox, QTableView, QPlainTextEdit "
            f"{{ border: 2px solid {texto}; }}"
            f"QTabBar::tab:selected {{ background: {destaque}; color: {texto_destaque}; }}"
            f"QGroupBox {{ border: 2px solid {texto}; margin-top: 1.2em; padding-top: 0.4em; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; }}"
            f"QCheckBox::indicator, QMenu::indicator {{ width: 1em; height: 1em; border: 2px solid {texto}; "
            f"background: {campo}; }}"
            f"QCheckBox::indicator:checked, QMenu::indicator:checked {{ background: {destaque}; }}")
    else:
        app.setStyleSheet("")


def escala(a):
    return TAMANHOS[a["tamanho"]][1]


def rc_tela(a):
    """Estilo do matplotlib para os gráficos da janela, com a letra e o tema escolhidos."""
    escala = TAMANHOS[a["tamanho"]][1]
    rc = {"font.size": 10 * escala, "lines.linewidth": 1.5 * escala ** 0.5, "axes.linewidth": 0.8 * escala ** 0.5}
    if a["tema"] in ("sistema", "claro"):
        return rc
    fundo, texto = _CORES[a["tema"]][0], _CORES[a["tema"]][1]
    if a["tema"] == "alto_contraste_claro":
        fundo = "#FFFFFF"
    rc.update({"figure.facecolor": fundo, "axes.facecolor": fundo, "savefig.facecolor": fundo,
               "text.color": texto, "axes.labelcolor": texto, "axes.edgecolor": texto, "xtick.color": texto,
               "ytick.color": texto, "legend.facecolor": fundo, "legend.edgecolor": texto,
               "hatch.color": texto})
    if a["tema"].startswith("alto_contraste"):
        rc.update({"axes.linewidth": 2 * escala ** 0.5, "lines.linewidth": 2.5 * escala ** 0.5})
    return rc
