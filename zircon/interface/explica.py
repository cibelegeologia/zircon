"""Modo explicação: com o botão "?" ligado, o mouse vira uma interrogação.

Passando sobre botões, menus, abas, opções e grãos dos gráficos aparece uma
legenda curta. Clicando num item a legenda fica parada; o próximo clique com
o botão esquerdo a fecha. Esc ou o próprio "?" desligam o modo.
"""
from .qt import QApplication, QCursor, QDockWidget, QEvent, QFrame, QLabel, QMenu, QMenuBar, QObject, Qt, QTabBar, QToolButton
from .qt import QPalette, QTimer, QToolTip, QVBoxLayout

from ..idiomas import tr


class _Nota(QFrame):
    """Legenda que fica parada até o próximo clique."""

    def __init__(self):
        super().__init__(None, Qt.ToolTip)
        self.setFrameShape(QFrame.Box)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ToolTipBase)
        lay = QVBoxLayout(self)
        self.rotulo = QLabel()
        self.rotulo.setWordWrap(True)
        self.rotulo.setForegroundRole(QPalette.ToolTipText)
        self.rotulo.setMaximumWidth(440)
        lay.addWidget(self.rotulo)

    def mostrar(self, texto, pos):
        self.rotulo.setText(texto + "<br><small><i>" + tr("Clique para fechar") + "</i></small>")
        self.rotulo.setTextFormat(Qt.RichText)
        self.adjustSize()
        self.move(pos.x() + 16, pos.y() + 16)
        self.show()
        self.raise_()


def _html(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")


def texto_em(pos):
    """Explicação curta do que está sob o ponto pos (coordenadas da tela)."""
    w = QApplication.widgetAt(pos)
    while w is not None:
        if isinstance(w, QTabBar):
            i = w.tabAt(w.mapFromGlobal(pos))
            if i >= 0 and w.tabWhatsThis(i):
                return w.tabWhatsThis(i)
            if i >= 0:  # abas de janelas encaixadas: a explicação está na própria janela
                janela = w.window()
                for doca in janela.findChildren(QDockWidget):
                    if doca.windowTitle() == w.tabText(i) and doca.whatsThis():
                        return doca.whatsThis()
        if isinstance(w, (QMenu, QMenuBar)):
            a = w.actionAt(w.mapFromGlobal(pos))
            if a is not None:
                return a.whatsThis() or a.toolTip().replace("&", "")
        if isinstance(w, QToolButton) and w.defaultAction() is not None and w.defaultAction().whatsThis():
            return w.defaultAction().whatsThis()
        info = getattr(w, "info_no_ponto", None)
        if info is not None:
            t = info(pos)
            if t:
                return t
        if w.whatsThis():
            return w.whatsThis()
        if w.toolTip() and not isinstance(w, QMenu):
            return w.toolTip()
        w = w.parentWidget()
    return None


class ModoExplicacao(QObject):
    def __init__(self, botao):
        super().__init__(botao)
        self.botao = botao
        self.ativo = False
        self.nota = _Nota()
        self._engoliu_clique = False
        self._ultimo = None
        # o Qt só avisa o movimento do mouse a quem pede; aqui o cursor é conferido a cada instante
        self.relogio = QTimer(self)
        self.relogio.setInterval(150)
        self.relogio.timeout.connect(self._acompanha)
        botao.toggled.connect(self.ativar)

    def _acompanha(self):
        pos = QCursor.pos()
        if self.nota.isVisible() or pos == self._ultimo:
            return
        self._ultimo = pos
        texto = texto_em(pos)
        if texto:
            QToolTip.showText(pos, texto)
        else:
            QToolTip.hideText()

    def ativar(self, ligar):
        app = QApplication.instance()
        if ligar == self.ativo:
            return
        self.ativo = ligar
        if ligar:
            app.installEventFilter(self)
            app.setOverrideCursor(QCursor(Qt.WhatsThisCursor))
            self._ultimo = None
            self.relogio.start()
        else:
            app.removeEventFilter(self)
            app.restoreOverrideCursor()
            self.relogio.stop()
            self.nota.hide()
            QToolTip.hideText()
        if self.botao.isChecked() != ligar:
            self.botao.setChecked(ligar)

    def _no_botao(self, pos):
        w = QApplication.widgetAt(pos)
        return w is self.botao or (w is not None and w.parentWidget() is self.botao)

    def eventFilter(self, obj, ev):
        t = ev.type()
        if t == QEvent.KeyPress and ev.key() == Qt.Key_Escape:
            self.ativar(False)
            return True
        if t == QEvent.MouseButtonPress and ev.button() == Qt.LeftButton:
            pos = QCursor.pos()
            if self._no_botao(pos):
                return False  # deixa o "?" desligar o modo
            if self.nota.isVisible():
                self.nota.hide()
                self._engoliu_clique = True
                return True
            texto = texto_em(pos)
            if texto:
                QToolTip.hideText()
                self.nota.mostrar(_html(texto), pos)
                self._engoliu_clique = True
                return True
        if t in (QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick) and self._engoliu_clique:
            if t == QEvent.MouseButtonRelease:
                self._engoliu_clique = False
            return True
        return False
