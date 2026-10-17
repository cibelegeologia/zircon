"""Janela do Guia do Zircon."""
from .qt import QDialog, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QSplitter, QTextBrowser, Qt, QVBoxLayout

from .. import ajuda, idiomas
from ..idiomas import tr

_aberta = None


class JanelaAjuda(QDialog):
    def __init__(self, parent=None, arquivo_referencias=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Guia do Zircon"))
        self.resize(980, 680)
        self.arquivo_referencias = arquivo_referencias
        self.idioma = idiomas.atual()
        lay = QVBoxLayout(self)
        self.busca = QLineEdit()
        self.busca.setPlaceholderText(tr("Buscar no guia (ex.: MSWD, discordância, Pb comum)"))
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(self._filtra)
        lay.addWidget(self.busca)
        divisor = QSplitter()
        self.lista = QListWidget()
        self.lista.currentItemChanged.connect(self._mostra)
        self.texto = QTextBrowser()
        self.texto.setOpenExternalLinks(True)
        self.busca.setAccessibleName(tr("Buscar no guia"))
        self.lista.setAccessibleName(tr("Tópicos do guia"))
        self.texto.setAccessibleName(tr("Texto do tópico"))
        divisor.addWidget(self.lista)
        divisor.addWidget(self.texto)
        divisor.setStretchFactor(1, 1)
        divisor.setSizes([280, 700])
        lay.addWidget(divisor)
        self._filtra("")

    def _filtra(self, texto):
        atual = self.lista.currentItem().data(Qt.UserRole) if self.lista.currentItem() else None
        self.lista.blockSignals(True)
        self.lista.clear()
        titulos = dict(ajuda.topicos())
        for id_ in ajuda.busca(texto):
            item = QListWidgetItem(titulos[id_])
            item.setData(Qt.UserRole, id_)
            self.lista.addItem(item)
        self.lista.blockSignals(False)
        if self.lista.count():
            self.abrir(atual if atual in ajuda.busca(texto) else self.lista.item(0).data(Qt.UserRole))
        else:
            self.texto.setHtml(f"<p>{tr('Nada encontrado.')}</p>")

    def _mostra(self, item, _anterior=None):
        if item is not None:
            self.texto.setHtml(ajuda.html_do_topico(item.data(Qt.UserRole), self.arquivo_referencias))

    def abrir(self, id_):
        for i in range(self.lista.count()):
            if self.lista.item(i).data(Qt.UserRole) == id_:
                self.lista.setCurrentRow(i)
                self._mostra(self.lista.item(i))
                return


def mostrar(parent, id_="inicio", arquivo_referencias=None):
    """Abre o guia no tópico pedido (uma janela só, que fica aberta ao lado do programa)."""
    global _aberta
    if _aberta is None or _aberta.parent() is not parent or _aberta.idioma != idiomas.atual():
        if _aberta is not None:
            _aberta.close()
        _aberta = JanelaAjuda(parent, arquivo_referencias)
    _aberta.busca.clear()
    _aberta.abrir(id_)
    _aberta.show()
    _aberta.raise_()
    _aberta.activateWindow()
    return _aberta
