"""Janelas auxiliares: boas-vindas, conferência da importação, registro e sobre."""
import json
import platform
import uuid
from pathlib import Path
from urllib.parse import quote

from .qt import QStandardPaths, Qt, QUrl
from .qt import QDesktopServices, QGuiApplication
from .qt import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPlainTextEdit, QPushButton, QTableView, QVBoxLayout)

from .. import __version__, idiomas
from ..idiomas import N_, tr
from .modelos import ModeloTabela

# Endereço do formulário de registro (a criar pela autora). Vazio = só e-mail.
URL_FORMULARIO = ""
EMAIL_REGISTRO = "cibelegeologia@gmail.com"


def pasta_config():
    p = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    p.mkdir(parents=True, exist_ok=True)
    return p


class BoasVindas(QDialog):
    """Primeira tela: novo projeto, abrir projeto ou abrir um exemplo."""
    NOVO, ABRIR, EXEMPLO = 1, 2, 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Bem-vindo ao Zircon"))
        self.escolha = 0
        lay = QVBoxLayout(self)
        self.idioma = None
        linha_idioma = QHBoxLayout()
        linha_idioma.addWidget(QLabel("Idioma / Language / 语言 / भाषा / اللغة:"))
        self.c_idioma = QComboBox()
        for cod, nome in idiomas.IDIOMAS.items():
            self.c_idioma.addItem(nome, cod)
        self.c_idioma.setCurrentIndex(self.c_idioma.findData(idiomas.atual()))
        self.c_idioma.currentIndexChanged.connect(self._muda_idioma)
        linha_idioma.addWidget(self.c_idioma)
        lay.addLayout(linha_idioma)
        titulo = QLabel(f"<h2>Zircon {__version__}</h2>"
                        "<p>" + tr("Idades U-Pb, Th-Pb e Pb-Pb em zircão, com a referência de cada método.") + "</p>"
                        "<p>" + tr("Comece importando a planilha do laboratório. Os resultados e as escolhas ficam "
                                   "salvos num arquivo de projeto (.zircon) no seu computador.") + "</p>")
        titulo.setWordWrap(True)
        lay.addWidget(titulo)
        for texto, valor in ((tr("Novo projeto a partir de uma planilha..."), self.NOVO),
                             (tr("Abrir projeto salvo..."), self.ABRIR),
                             (tr("Abrir um exemplo para conhecer o programa"), self.EXEMPLO)):
            b = QPushButton(texto)
            b.setMinimumHeight(36)
            b.clicked.connect(lambda _=False, v=valor: self._escolhe(v))
            lay.addWidget(b)
        reg = QPushButton(tr("Registrar o Zircon (opcional, você confere antes de enviar)"))
        reg.setFlat(True)
        reg.clicked.connect(lambda: Registro(self).exec())
        lay.addWidget(reg)
        self.nao_mostrar = QCheckBox(tr("Não mostrar esta tela ao abrir"))
        lay.addWidget(self.nao_mostrar)
        fechar = QPushButton(tr("Fechar"))
        fechar.clicked.connect(self.reject)
        lay.addWidget(fechar, alignment=Qt.AlignRight)

    def _muda_idioma(self):
        # a janela principal troca o idioma e abre esta tela de novo, já traduzida
        self.idioma = self.c_idioma.currentData()
        self.reject()

    def _escolhe(self, v):
        self.escolha = v
        self.accept()


class ConfereImportacao(QDialog):
    """Mostra como o arquivo foi lido antes de aceitar."""

    def __init__(self, imp, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Conferir importação"))
        self.resize(820, 560)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<b>" + tr("Confira se as colunas foram reconhecidas corretamente.") + "</b> "
                             + tr("Erros são convertidos para 1σ absoluto.")))
        log = QPlainTextEdit("\n".join(imp.log))
        log.setReadOnly(True)
        log.setMaximumHeight(200)
        lay.addWidget(log)
        tabela = QTableView()
        tabela.setModel(ModeloTabela(imp.dados.head(50)))
        lay.addWidget(tabela)
        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.button(QDialogButtonBox.Ok).setText(tr("Usar estes dados"))
        botoes.button(QDialogButtonBox.Cancel).setText(tr("Cancelar"))
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        lay.addWidget(botoes)


class Registro(QDialog):
    """Registro voluntário.

    O programa não se conecta à internet. Os dados ficam só neste computador
    até o usuário decidir enviá-los, pelo navegador ou por e-mail.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Registrar o Zircon"))
        self.arquivo = pasta_config() / "registro.json"
        dados = self.ler()
        lay = QVBoxLayout(self)
        aviso = QLabel(tr("O registro é voluntário e ajuda a autora a saber onde o programa é usado.") + " <b>"
                       + tr("O Zircon nunca se conecta à internet sozinho.") + "</b> "
                       + tr("Nada é enviado até você clicar em um dos botões abaixo, e você vê o texto antes de "
                            "enviar. Todos os campos são opcionais."))
        aviso.setWordWrap(True)
        lay.addWidget(aviso)
        form = QFormLayout()
        self.campos = {}
        for chave, rotulo in (("nome", N_("Nome")), ("instituicao", N_("Instituição")), ("pais", N_("País")),
                              ("email", N_("E-mail (para avisos de nova versão)")),
                              ("uso", N_("Para que vai usar"))):
            c = QLineEdit(dados.get(chave, ""))
            form.addRow(tr(rotulo), c)
            self.campos[chave] = c
        lay.addLayout(form)
        self.id_instalacao = dados.get("id") or uuid.uuid4().hex[:12]
        lay.addWidget(QLabel(tr("Código anônimo desta instalação: {id}").format(id=self.id_instalacao)))
        linha = QHBoxLayout()
        for texto, func in ((N_("Enviar pelo navegador"), self.navegador), (N_("Enviar por e-mail"), self.email),
                            (N_("Copiar texto"), self.copiar), (N_("Salvar sem enviar"), self.accept)):
            b = QPushButton(tr(texto))
            b.clicked.connect(func)
            linha.addWidget(b)
        lay.addLayout(linha)
        self.accepted.connect(self.salvar)

    def ler(self):
        try:
            return json.loads(self.arquivo.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def salvar(self):
        d = {k: c.text().strip() for k, c in self.campos.items()}
        d.update(id=self.id_instalacao, versao=__version__)
        self.arquivo.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    def texto(self):
        linhas = [f"{k}: {c.text().strip()}" for k, c in self.campos.items() if c.text().strip()]
        linhas += [f"id: {self.id_instalacao}", f"versao: {__version__}", f"sistema: {platform.system()}"]
        return "\n".join(linhas)

    def navegador(self):
        if not URL_FORMULARIO:
            return self.email()
        campos = {k: c.text().strip() for k, c in self.campos.items()}
        campos.update(id=self.id_instalacao, versao=__version__)
        QDesktopServices.openUrl(QUrl(URL_FORMULARIO.format(**{k: quote(v) for k, v in campos.items()})))
        self.accept()

    def email(self):
        QDesktopServices.openUrl(QUrl(f"mailto:{EMAIL_REGISTRO}?subject={quote('Registro Zircon')}"
                                      f"&body={quote(self.texto())}"))
        self.accept()

    def copiar(self):
        QGuiApplication.clipboard().setText(self.texto())


def sobre_texto():
    return (f"<h3>Zircon {__version__}</h3>"
            "<p>" + tr("Software livre (CC0) para calcular idades por isótopos de U, Th e Pb em zircão.") + "</p>"
            "<p>" + tr("Cálculos conferidos com o IsoplotR 7.1 (Vermeesch 2018).") + "</p>"
            "<p>" + tr("Funciona sem internet e não coleta dados.") + "</p>"
            "<p>" + tr("Código e referências:") + " github.com/cibelegeologia/zircon</p>")


class ExportaPublicacao(QDialog):
    """Escolha da largura das figuras e dos formatos."""

    def __init__(self, parent=None, titulo=None, com_projeto=True):
        from ..nucleo.exportacao import LARGURAS_MM
        super().__init__(parent)
        self.setWindowTitle(titulo or tr("Exportar tudo do projeto"))
        lay = QVBoxLayout(self)
        texto = QLabel(tr("Gera uma pasta com: figuras nos formatos escolhidos; planilha Excel formatada com as "
                          "referências; gráficos interativos em HTML (material suplementar, abrem sem internet); "
                          "dados em CSV com LEIAME para repositório (Mendeley Data, Zenodo, PANGAEA); e o texto de "
                          "metodologia com as citações, no idioma escolhido e em inglês."))
        texto.setWordWrap(True)
        lay.addWidget(texto)
        form = QFormLayout()
        self.c_largura = QComboBox()
        for nome, mm in LARGURAS_MM.items():
            self.c_largura.addItem(tr(nome), mm)
        form.addRow(tr("Largura das figuras"), self.c_largura)
        lay.addLayout(form)
        self.c_fmt = {}
        for fmt, desc in (("png", N_("PNG 600 dpi (apresentações, Word)")),
                          ("tif", N_("TIFF 600 dpi (exigido por várias revistas)")),
                          ("pdf", N_("PDF vetorial")), ("svg", N_("SVG vetorial (editável no Inkscape/Illustrator)")),
                          ("eps", N_("EPS (revistas antigas; sem transparência)"))):
            c = QCheckBox(tr(desc))
            c.setChecked(fmt != "eps")
            lay.addWidget(c)
            self.c_fmt[fmt] = c
        nota = QLabel("<small>" + tr("Larguras e resoluções seguem as instruções de figuras da Elsevier.") + "</small>")
        lay.addWidget(nota)
        self.c_por_conjunto = QCheckBox(tr("Também uma concórdia e uma média de cada conjunto (quando o cálculo é "
                                           "por conjunto)"))
        self.c_por_conjunto.setChecked(True)
        self.c_por_conjunto.setVisible(com_projeto)
        lay.addWidget(self.c_por_conjunto)
        self.c_projeto = QCheckBox(tr("Incluir o projeto .zircon e a planilha original do laboratório"))
        self.c_projeto.setChecked(com_projeto)
        self.c_projeto.setVisible(com_projeto)
        lay.addWidget(self.c_projeto)
        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.button(QDialogButtonBox.Ok).setText(tr("Escolher pasta e exportar"))
        botoes.button(QDialogButtonBox.Cancel).setText(tr("Cancelar"))
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        lay.addWidget(botoes)

    def largura(self):
        return self.c_largura.currentData()

    def formatos(self):
        return tuple(f for f, c in self.c_fmt.items() if c.isChecked())


class JuntaAmostras(QDialog):
    """Uma linha por amostra da planilha, com a unidade em que ela entra no cálculo.

    Amostras com a mesma unidade viram um conjunto só (por exemplo, várias amostras de uma camada).
    A decisão é do pesquisador: o Zircon só separa pela coluna Amostra.
    """

    def __init__(self, contagem, unidades, parent=None):
        from .qt import QAbstractItemView, QInputDialog, QTableWidget, QTableWidgetItem
        super().__init__(parent)
        self._pede_nome = QInputDialog.getText
        self.setWindowTitle(tr("Juntar amostras em unidades"))
        self.resize(560, 460)
        lay = QVBoxLayout(self)
        texto = QLabel(tr("Cada amostra da planilha é um conjunto, com cor própria. Para tratar várias amostras como "
                          "uma coisa só (por exemplo, várias amostras da mesma camada ao longo de um perfil), "
                          "selecione-as e clique em \"Juntar as selecionadas...\". Elas passam a ser uma unidade, "
                          "com uma cor e uma idade. As amostras continuam identificadas na tabela de dados."))
        texto.setWordWrap(True)
        lay.addWidget(texto)
        self.tabela = QTableWidget(len(contagem), 3)
        self.tabela.setHorizontalHeaderLabels([tr("Amostra"), tr("Análises"), tr("Unidade")])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        for i, (amostra, n) in enumerate(contagem.items()):
            for j, v in enumerate((amostra, str(n), unidades.get(amostra, ""))):
                item = QTableWidgetItem(v)
                if j < 2:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabela.setItem(i, j, item)
        self.tabela.resizeColumnsToContents()
        self.tabela.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.tabela)
        linha = QHBoxLayout()
        b_juntar = QPushButton(tr("Juntar as selecionadas..."))
        b_juntar.clicked.connect(self._juntar)
        b_separar = QPushButton(tr("Separar as selecionadas"))
        b_separar.clicked.connect(lambda: self._marca(""))
        linha.addWidget(b_juntar)
        linha.addWidget(b_separar)
        linha.addStretch()
        lay.addLayout(linha)
        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.button(QDialogButtonBox.Ok).setText(tr("Usar estas unidades"))
        botoes.button(QDialogButtonBox.Cancel).setText(tr("Cancelar"))
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        lay.addWidget(botoes)

    def _linhas(self):
        return sorted({i.row() for i in self.tabela.selectionModel().selectedRows()})

    def _marca(self, nome):
        for i in self._linhas():
            self.tabela.item(i, 2).setText(nome)

    def _juntar(self):
        linhas = self._linhas()
        if not linhas:
            return
        sugestao = self.tabela.item(linhas[0], 2).text() or self.tabela.item(linhas[0], 0).text()
        nome, ok = self._pede_nome(self, tr("Juntar amostras"), tr("Nome da unidade (por exemplo, a camada):"),
                                   QLineEdit.Normal, sugestao)
        if ok and nome.strip():
            self._marca(nome.strip())

    def unidades(self):
        """{amostra: unidade} só das amostras que foram juntadas."""
        u = {}
        for i in range(self.tabela.rowCount()):
            amostra, unidade = self.tabela.item(i, 0).text(), self.tabela.item(i, 2).text().strip()
            if unidade and unidade != amostra:
                u[amostra] = unidade
        return u
