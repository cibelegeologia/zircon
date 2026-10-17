"""Janelas auxiliares: boas-vindas, conferência da importação, registro e sobre."""
import json
import platform
import uuid
from pathlib import Path
from urllib.parse import quote

from .qt import QStandardPaths, Qt, QUrl
from .qt import QDesktopServices, QGuiApplication
from .qt import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPlainTextEdit, QPushButton, QTableView, QVBoxLayout)

from .. import __version__
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
        self.setWindowTitle("Bem-vindo ao Zircon")
        self.escolha = 0
        lay = QVBoxLayout(self)
        titulo = QLabel(f"<h2>Zircon {__version__}</h2>"
                        "<p>Idades U-Pb, Th-Pb e Pb-Pb em zircão, com a referência de cada método.</p>"
                        "<p>Comece importando a planilha do laboratório. Os resultados e as escolhas ficam "
                        "salvos num arquivo de projeto (.zircon) no seu computador.</p>")
        titulo.setWordWrap(True)
        lay.addWidget(titulo)
        for texto, valor in (("Novo projeto a partir de uma planilha...", self.NOVO),
                             ("Abrir projeto salvo...", self.ABRIR),
                             ("Abrir um exemplo para conhecer o programa", self.EXEMPLO)):
            b = QPushButton(texto)
            b.setMinimumHeight(36)
            b.clicked.connect(lambda _=False, v=valor: self._escolhe(v))
            lay.addWidget(b)
        reg = QPushButton("Registrar o Zircon (opcional, você confere antes de enviar)")
        reg.setFlat(True)
        reg.clicked.connect(lambda: Registro(self).exec())
        lay.addWidget(reg)
        self.nao_mostrar = QCheckBox("Não mostrar esta tela ao abrir")
        lay.addWidget(self.nao_mostrar)
        fechar = QPushButton("Fechar")
        fechar.clicked.connect(self.reject)
        lay.addWidget(fechar, alignment=Qt.AlignRight)

    def _escolhe(self, v):
        self.escolha = v
        self.accept()


class ConfereImportacao(QDialog):
    """Mostra como o arquivo foi lido antes de aceitar."""

    def __init__(self, imp, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conferir importação")
        self.resize(820, 560)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<b>Confira se as colunas foram reconhecidas corretamente.</b> "
                             "Erros são convertidos para 1σ absoluto."))
        log = QPlainTextEdit("\n".join(imp.log))
        log.setReadOnly(True)
        log.setMaximumHeight(200)
        lay.addWidget(log)
        tabela = QTableView()
        tabela.setModel(ModeloTabela(imp.dados.head(50)))
        lay.addWidget(tabela)
        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.button(QDialogButtonBox.Ok).setText("Usar estes dados")
        botoes.button(QDialogButtonBox.Cancel).setText("Cancelar")
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
        self.setWindowTitle("Registrar o Zircon")
        self.arquivo = pasta_config() / "registro.json"
        dados = self.ler()
        lay = QVBoxLayout(self)
        aviso = QLabel("O registro é voluntário e ajuda a autora a saber onde o programa é usado. "
                       "<b>O Zircon nunca se conecta à internet sozinho.</b> Nada é enviado até você "
                       "clicar em um dos botões abaixo, e você vê o texto antes de enviar. "
                       "Todos os campos são opcionais.")
        aviso.setWordWrap(True)
        lay.addWidget(aviso)
        form = QFormLayout()
        self.campos = {}
        for chave, rotulo in (("nome", "Nome"), ("instituicao", "Instituição"), ("pais", "País"),
                              ("email", "E-mail (para avisos de nova versão)"), ("uso", "Para que vai usar")):
            c = QLineEdit(dados.get(chave, ""))
            form.addRow(rotulo, c)
            self.campos[chave] = c
        lay.addLayout(form)
        self.id_instalacao = dados.get("id") or uuid.uuid4().hex[:12]
        lay.addWidget(QLabel(f"Código anônimo desta instalação: {self.id_instalacao}"))
        linha = QHBoxLayout()
        for texto, func in (("Enviar pelo navegador", self.navegador), ("Enviar por e-mail", self.email),
                            ("Copiar texto", self.copiar), ("Salvar sem enviar", self.accept)):
            b = QPushButton(texto)
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
            "<p>Software livre (CC0) para calcular idades por isótopos de U, Th e Pb em zircão.</p>"
            "<p>Cálculos conferidos com o IsoplotR 7.1 (Vermeesch 2018).</p>"
            "<p>Funciona sem internet e não coleta dados.</p>"
            "<p>Código e referências: github.com/cibelegeologia/zircon</p>")


class ExportaPublicacao(QDialog):
    """Escolha da largura das figuras e dos formatos."""

    def __init__(self, parent=None):
        from ..nucleo.exportacao import LARGURAS_MM
        from .qt import QComboBox
        super().__init__(parent)
        self.setWindowTitle("Exportar para publicação")
        lay = QVBoxLayout(self)
        texto = QLabel("Gera uma pasta com: figuras nos formatos escolhidos; planilha Excel formatada com as "
                       "referências; gráficos interativos em HTML (material suplementar, abrem sem internet); "
                       "dados em CSV com LEIAME para repositório (Mendeley Data, Zenodo, PANGAEA); e o texto de "
                       "metodologia com as citações, em português e inglês.")
        texto.setWordWrap(True)
        lay.addWidget(texto)
        form = QFormLayout()
        self.c_largura = QComboBox()
        for nome, mm in LARGURAS_MM.items():
            self.c_largura.addItem(nome, mm)
        form.addRow("Largura das figuras", self.c_largura)
        lay.addLayout(form)
        self.c_fmt = {}
        for fmt, desc in (("png", "PNG 600 dpi (apresentações, Word)"), ("tif", "TIFF 600 dpi (exigido por várias revistas)"),
                          ("pdf", "PDF vetorial"), ("svg", "SVG vetorial (editável no Inkscape/Illustrator)"),
                          ("eps", "EPS (revistas antigas; sem transparência)")):
            c = QCheckBox(desc)
            c.setChecked(fmt != "eps")
            lay.addWidget(c)
            self.c_fmt[fmt] = c
        nota = QLabel("<small>Larguras e resoluções seguem as instruções de figuras da Elsevier.</small>")
        lay.addWidget(nota)
        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.button(QDialogButtonBox.Ok).setText("Escolher pasta e exportar")
        botoes.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        lay.addWidget(botoes)

    def largura(self):
        return self.c_largura.currentData()

    def formatos(self):
        return tuple(f for f, c in self.c_fmt.items() if c.isChecked())
