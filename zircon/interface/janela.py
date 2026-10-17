"""Janela principal do Zircon."""
import sys
from pathlib import Path

import matplotlib
import pandas as pd
from .qt import QLibraryInfo, QLocale, QSettings, Qt, QTimer, QTranslator, QUrl
from .qt import QAction, QDesktopServices, QIcon, QKeySequence
from .qt import (QAbstractItemView, QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
                               QFormLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMessageBox,
                               QPlainTextEdit, QPushButton, QRadioButton, QScrollArea, QSplitter, QTableView, QTabWidget, QToolBar, QToolButton, QStyle,
                               QVBoxLayout, QWidget)

from .. import __version__, idiomas
from ..idiomas import N_, tr
from ..nucleo import calculo, exportacao, grupos, metodologia
from ..nucleo.importacao import importar
from ..nucleo.projeto import EXTENSAO, Projeto
from . import ajuda as janela_ajuda, aparencia, graficos
from .explica import ModoExplicacao
from .. import ajuda
from .dialogos import BoasVindas, ConfereImportacao, ExportaPublicacao, Registro, sobre_texto
from .modelos import ModeloTabela

FILTRO_PLANILHA = N_("Planilhas (*.xlsx *.xls *.ods *.csv *.txt *.tsv);;Todos os arquivos (*)")
FILTRO_PROJETO = N_("Projeto Zircon (*.zircon)")
REF = {
    "efeitos_aleatorios": "Vermeesch (2018a), Geoscience Frontiers 9:1479-1493",
    "rejeitar_outliers": N_("Chauvenet generalizado: Vermeesch (2018a)"),
    "corte_76": N_("Spencer, Kirkland e Taylor (2016); Gehrels (2014)"),
    "limite_discordancia": N_("Spencer, Kirkland e Taylor (2016), Geoscience Frontiers 7:581-589"),
    "media_de": N_("Wendt e Carl (1991), Chemical Geology 86:275-285"),
    "agrupar": grupos.REFERENCIAS["populacoes"],
    "pb_comum": N_("Stacey e Kramers (1975); Williams (1998)"),
}


def pasta_exemplos():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    for p in (base / "exemplos", base / "testes" / "modulo2" / "entrada"):
        if p.exists():
            return p
    return Path.home()


def arquivo_referencias():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base / "docs" / "referencias_abnt.md"


class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = QSettings("Zircon", "Zircon")
        self.projeto = None
        self.resultado = None
        self.alterado = False
        self.resize(1280, 800)
        self.aparencia = aparencia.ler(self.config)
        self._menus()
        with self._estilo_graficos():
            self._layout()
        self._atualiza_titulo()

    def _estilo_graficos(self):
        return matplotlib.rc_context(aparencia.rc_tela(self.aparencia))

    # ---------- montagem ----------
    def _acao(self, menu, texto, func, atalho=None, explica=None):
        a = QAction(texto, self)
        if explica:
            a.setWhatsThis(tr(explica))
            a.setStatusTip(tr(explica))
        if atalho:
            a.setShortcut(atalho)
        a.triggered.connect(func)
        menu.addAction(a)
        return a

    def _menus(self):
        m = self.menuBar().addMenu(tr("&Arquivo"))
        self._acao(m, tr("&Novo projeto (importar planilha)..."), self.novo, QKeySequence.New,
                   explica=N_("Começa um projeto novo a partir da planilha do laboratório."))
        self._acao(m, tr("&Abrir projeto..."), self.abrir, QKeySequence.Open,
                   explica=N_("Abre um projeto .zircon salvo, com os dados e as escolhas."))
        self.menu_recentes = m.addMenu(tr("Projetos recentes"))
        m.addSeparator()
        self._acao(m, tr("&Salvar"), self.salvar, QKeySequence.Save,
                   explica=N_("Salva o projeto atual no arquivo .zircon."))
        self._acao(m, tr("Salvar &como..."), self.salvar_como, QKeySequence.SaveAs,
                   explica=N_("Salva o projeto com outro nome ou em outra pasta."))
        m.addSeparator()
        self._acao(m, tr("Exportar para publicação (figuras, Excel, interativo, metodologia)..."),
                   self.exportar_publicacao, "Ctrl+E",
                   explica=N_("Gera de uma vez tudo para o artigo: figuras, planilha, gráficos interativos, "
                              "dados e metodologia."))
        self._acao(m, tr("Exportar planilha Excel formatada..."), self.exportar_resultados,
                   explica=N_("Salva as tabelas de resultados e de idades por grão numa planilha Excel."))
        self._acao(m, tr("Exportar gráfico atual..."), self.exportar_grafico,
                   explica=N_("Salva como imagem o gráfico da aba aberta."))
        self._acao(m, tr("Exportar gráficos interativos (HTML)..."), self.exportar_interativo,
                   explica=N_("Gráficos que abrem no navegador e mostram os dados de cada grão (material suplementar)."))
        self._acao(m, tr("Exportar metodologia (Markdown ou texto)..."), self.exportar_metodologia,
                   explica=N_("Salva o texto de métodos com as citações, pronto para revisar e colar no artigo."))
        m.addSeparator()
        self._acao(m, tr("Sai&r"), self.close, QKeySequence.Quit,
                   explica=N_("Fecha o Zircon (pergunta antes se há alterações não salvas)."))
        m = self.menuBar().addMenu(tr("&Grupos"))
        self._acao(m, tr("Colocar linhas selecionadas no grupo..."), self.atribuir_grupo,
                   explica=N_("Põe as linhas selecionadas na tabela num grupo seu, com cor própria."))
        self._acao(m, tr("Voltar às cores automáticas"), lambda: self._muda_agrupamento("classe"),
                   explica=N_("Volta a pintar os grãos por concordante, discordante ou rejeitado."))
        m = self.menuBar().addMenu(tr("Aj&uda"))
        self._acao(m, tr("Guia do Zircon (o que é cada recurso e como usar)"), lambda: self.guia("inicio"),
                   QKeySequence.HelpContents)
        self._acao(m, tr("Primeiros passos"), lambda: self.guia("inicio"),
                   explica=N_("Mostra o caminho básico: importar, conferir, calcular e exportar."))
        m.addSeparator()
        self._acao(m, tr("Registrar o Zircon..."), lambda: Registro(self).exec(),
                   explica=N_("Registro voluntário: você vê o texto e decide se envia."))
        self._acao(m, tr("Sobre o Zircon"), lambda: QMessageBox.about(self, tr("Sobre"), sobre_texto()),
                   explica=N_("Versão, licença e onde achar o código e as referências."))
        self._menu_acessibilidade()
        # o nome do menu também em inglês, para quem escolheu por engano um idioma que não lê
        titulo = tr("&Idioma") + ("" if idiomas.atual() == "en" else " (Language)")
        m = self.menuBar().addMenu(titulo)
        for cod, nome in idiomas.IDIOMAS.items():
            a = self._acao(m, nome, lambda _=False, c=cod: self._troca_idioma(c))
            a.setCheckable(True)
            a.setChecked(cod == idiomas.atual())
        self._atualiza_recentes()
        self._barra()

    def _barra(self):
        """Barra com os botões mais usados e o "?" do modo explicação."""
        if getattr(self, "barra", None) is not None:
            if getattr(self, "modo_explicacao", None) is not None:
                self.modo_explicacao.ativar(False)
            self.removeToolBar(self.barra)
            self.barra.deleteLater()
        self.barra = QToolBar(tr("Barra principal"))
        self.barra.setObjectName("barra")
        self.barra.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        estilo = self.style()
        for icone, texto, func, explica in (
                (QStyle.SP_FileIcon, N_("Novo"), self.novo, N_("Começa um projeto novo a partir da planilha do laboratório.")),
                (QStyle.SP_DialogOpenButton, N_("Abrir"), self.abrir, N_("Abre um projeto .zircon salvo, com os dados e as escolhas.")),
                (QStyle.SP_DialogSaveButton, N_("Salvar"), self.salvar, N_("Salva o projeto atual no arquivo .zircon.")),
                (QStyle.SP_BrowserReload, N_("Calcular"), self.calcular, N_("Faz todos os cálculos com as opções escolhidas no painel.")),
                (QStyle.SP_DriveFDIcon, N_("Exportar"), self.exportar_publicacao,
                 N_("Gera de uma vez tudo para o artigo: figuras, planilha, gráficos interativos, "
                    "dados e metodologia.")),
                (QStyle.SP_DialogHelpButton, N_("Guia"), lambda: self.guia("inicio"),
                 N_("Abre o Guia do Zircon: para que serve cada recurso, onde ler mais e como usar."))):
            a = self.barra.addAction(estilo.standardIcon(icone), tr(texto))
            a.triggered.connect(lambda _=False, f=func: f())
            a.setToolTip(tr(explica))
            a.setWhatsThis(tr(explica))
        self.barra.addSeparator()
        self.b_explica = QToolButton()
        self.b_explica.setText("?  " + tr("O que é isto?"))
        self.b_explica.setCheckable(True)
        self.b_explica.setToolTip(tr("Liga o modo explicação: passe o mouse sobre qualquer coisa para ver o que é; "
                                     "clique para fixar a legenda. Esc desliga."))
        self.b_explica.setStyleSheet("font-weight: bold;")
        self.barra.addWidget(self.b_explica)
        self.modo_explicacao = ModoExplicacao(self.b_explica)
        self.addToolBar(self.barra)

    def _menu_acessibilidade(self):
        m = self.menuBar().addMenu(tr("A&cessibilidade"))
        a = self.aparencia

        def grupo_de_opcoes(titulo, opcoes, chave):
            sub = m.addMenu(tr(titulo))
            for valor, rotulo in opcoes.items():
                texto = rotulo[0] if isinstance(rotulo, tuple) else rotulo
                acao = self._acao(sub, tr(texto), lambda _=False, v=valor: self._muda_aparencia(chave, v))
                acao.setCheckable(True)
                acao.setChecked(a[chave] == valor)
            return sub

        grupo_de_opcoes(N_("Tamanho da letra"), aparencia.TAMANHOS, "tamanho")
        self._acao(m, tr("Aumentar a letra"), lambda: self._passo_letra(1), QKeySequence.ZoomIn,
                   explica=N_("Deixa os textos maiores (também Ctrl +)."))
        self._acao(m, tr("Diminuir a letra"), lambda: self._passo_letra(-1), QKeySequence.ZoomOut,
                   explica=N_("Deixa os textos menores (também Ctrl -)."))
        m.addSeparator()
        grupo_de_opcoes(N_("Tema e contraste"), aparencia.TEMAS, "tema")
        sub = grupo_de_opcoes(N_("Cores dos gráficos (daltonismo)"), aparencia.PALETAS, "paleta")
        sub.setToolTipsVisible(True)
        for acao, chave in zip(sub.actions(), aparencia.PALETAS):
            acao.setToolTip(tr(grupos.REFERENCIAS.get(chave, "")))
        padroes = self._acao(m, tr("Padrões além das cores (listras e pontos nos grupos)"),
                             lambda v: self._muda_aparencia("padroes", bool(v)))
        padroes.setCheckable(True)
        padroes.setChecked(a["padroes"])

    def _opcoes_de_cor(self, form):
        """Escolha rápida entre cores comuns e acessíveis, e padrões além da cor."""
        a = self.aparencia
        linha = QWidget()
        lh = QVBoxLayout(linha)
        lh.setContentsMargins(0, 0, 0, 0)
        self.r_comuns = QRadioButton(tr("Cores comuns"))
        self.r_acessiveis = QRadioButton(tr("Cores acessíveis (daltonismo)"))
        acessivel = a["paleta"] in aparencia.ACESSIVEIS
        (self.r_acessiveis if acessivel else self.r_comuns).setChecked(True)
        lh.addWidget(self.r_comuns)
        lh.addWidget(self.r_acessiveis)
        form.addRow(linha)
        self.c_paleta = QComboBox()
        for chave in aparencia.ACESSIVEIS:
            self.c_paleta.addItem(tr(aparencia.PALETAS[chave]), chave)
            self.c_paleta.setItemData(self.c_paleta.count() - 1, tr(grupos.REFERENCIAS.get(chave, "")),
                                      Qt.ToolTipRole)
        self.c_paleta.setCurrentIndex(max(0, self.c_paleta.findData(a["paleta"] if acessivel
                                                                    else a.get("ultima_acessivel", "okabe_ito"))))
        self.c_paleta.setEnabled(acessivel)
        form.addRow(tr("Paleta acessível"), self.c_paleta)
        self.c_padroes = QCheckBox(tr("Padrões além das cores (listras e pontos nos grupos)"))
        self.c_padroes.setChecked(a["padroes"])
        form.addRow(self.c_padroes)

        def escolhe_paleta():
            self._muda_aparencia("paleta", self.c_paleta.currentData() if self.r_acessiveis.isChecked() else "comum")
        self.r_acessiveis.toggled.connect(lambda _=False: escolhe_paleta())
        self.c_paleta.currentIndexChanged.connect(lambda _=0: escolhe_paleta())
        self.c_padroes.toggled.connect(lambda v: self._muda_aparencia("padroes", bool(v)))

    def _passo_letra(self, passo):
        ordem = list(aparencia.TAMANHOS)
        i = min(max(ordem.index(self.aparencia["tamanho"]) + passo, 0), len(ordem) - 1)
        self._muda_aparencia("tamanho", ordem[i])

    def _muda_aparencia(self, chave, valor):
        if self.aparencia[chave] == valor:
            return
        self.aparencia[chave] = valor
        self.config.setValue(chave, valor)
        if chave == "paleta" and valor in aparencia.ACESSIVEIS:
            self.aparencia["ultima_acessivel"] = valor
        aparencia.aplicar(QApplication.instance(), self.aparencia)
        if chave in ("paleta", "padroes"):
            # só as cores mudam: atualiza menus e painel e redesenha, sem refazer a janela
            self.menuBar().clear()
            self._menus()
            for w, v in ((self.r_acessiveis, self.aparencia["paleta"] in aparencia.ACESSIVEIS),
                         (self.r_comuns, self.aparencia["paleta"] not in aparencia.ACESSIVEIS),
                         (self.c_padroes, self.aparencia["padroes"])):
                w.blockSignals(True)
                w.setChecked(v)
                w.blockSignals(False)
            self.c_paleta.setEnabled(self.r_acessiveis.isChecked())
            if self.aparencia["paleta"] in aparencia.ACESSIVEIS:
                self.c_paleta.blockSignals(True)
                self.c_paleta.setCurrentIndex(self.c_paleta.findData(self.aparencia["paleta"]))
                self.c_paleta.blockSignals(False)
            if self.resultado is not None:
                alterado = self.alterado
                self.calcular()
                self.alterado = alterado
        else:
            QTimer.singleShot(0, self._remonta)  # depois que o menu que chamou terminar

    def _layout(self):
        divisor = QSplitter()
        divisor.addWidget(self._painel_opcoes())
        self.abas = QTabWidget()
        self.tabela = QTableView()
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSortingEnabled(False)
        self.abas.addTab(self.tabela, tr("Dados e idades por grão"))
        self.graf_conc = graficos.Grafico()
        self.abas.addTab(self.graf_conc, tr("Concórdia ou isócrona"))
        self.graf_media = graficos.Grafico()
        self.abas.addTab(self.graf_media, tr("Média ponderada"))
        self.graf_dens = graficos.Grafico()
        self.abas.addTab(self.graf_dens, tr("Distribuição de idades"))
        res = QWidget()
        lr = QVBoxLayout(res)
        self.tabela_res = QTableView()
        lr.addWidget(self.tabela_res)
        self.avisos = QPlainTextEdit()
        self.avisos.setReadOnly(True)
        self.avisos.setMaximumHeight(140)
        lr.addWidget(QLabel(tr("Avisos e interpretação")))
        lr.addWidget(self.avisos)
        self.abas.addTab(res, tr("Resultados"))
        self.metodologia = QPlainTextEdit()
        self.metodologia.setReadOnly(True)
        self.abas.addTab(self.metodologia, tr("Metodologia (texto para o artigo)"))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.abas.addTab(self.log, tr("Registro da importação"))
        divisor.addWidget(self.abas)
        divisor.setStretchFactor(1, 1)
        divisor.setSizes([int(470 * aparencia.escala(self.aparencia)), 820])
        self.setCentralWidget(divisor)
        for g in (self.graf_conc, self.graf_media, self.graf_dens):
            g.limpar()
        self._explica_widgets()

    def _explica_widgets(self):
        """Legendas curtas do modo explicação ("?") para opções, abas e tabelas."""
        for w, texto in (
                (self.c_media, N_("Escolhe qual idade de cada grão entra na média ponderada.")),
                (self.c_corte, N_("Acima desta idade, a melhor idade do grão passa a ser a 207Pb/206Pb, "
                                  "mais precisa em grãos antigos.")),
                (self.c_diagrama, N_("Escolhe o diagrama concórdia: Wetherill (207Pb/235U x 206Pb/238U) ou "
                                     "Tera-Wasserburg (238U/206Pb x 207Pb/206Pb).")),
                (self.c_pbc, N_("Como descontar o chumbo comum (não radiogênico) quando a planilha tem 204Pb.")),
                (self.c_disc, N_("Grãos mais discordantes que este valor ficam fora das idades da amostra.")),
                (self.c_usar_disc, N_("Marque para usar também os grãos discordantes na média.")),
                (self.c_outliers, N_("Retira da média os grãos que fogem muito dos outros (critério de Chauvenet).")),
                (self.c_ef, N_("Estima a dispersão real entre os grãos, além do erro de medida.")),
                (self.c_agrupar, N_("Como pintar os grãos nos gráficos e na tabela.")),
                (self.c_minpop, N_("Populações com menos grãos que isto são juntadas à vizinha.")),
                (self.r_comuns, N_("Cores comuns dos gráficos.")),
                (self.r_acessiveis, N_("Cores que pessoas com daltonismo distinguem.")),
                (self.c_paleta, N_("Qual paleta acessível usar; cada uma tem a sua referência.")),
                (self.c_padroes, N_("Acrescenta listras e pontos aos grupos, para separá-los sem depender da cor.")),
                (self.b_calcular, N_("Faz todos os cálculos com as opções escolhidas no painel.")),
                (self.tabela, N_("Uma linha por análise, com as idades calculadas. A cor da linha é a do grupo; "
                                 "selecione linhas para pô-las num grupo (menu Grupos).")),
                (self.tabela_res, N_("Idades da amostra: média ponderada, concórdia e discórdia, com MSWD, p e "
                                     "a referência de cada método.")),
                (self.avisos, N_("Avisos sobre os dados e os resultados, para ajudar a interpretar.")),
                (self.metodologia, N_("Texto de métodos com as citações, para revisar e colar no artigo.")),
                (self.log, N_("Como a planilha foi lida: colunas reconhecidas, separadores e erros convertidos."))):
            w.setWhatsThis(tr(texto))
        abas = (N_("Tabela com os dados importados e as idades de cada grão."),
                N_("Diagrama concórdia (ou isócrona) com a elipse de erro 2σ de cada grão. Passe o mouse "
                   "sobre uma elipse para ver o grão."),
                N_("Idade de cada grão com barra de erro 2σ e a faixa da média ponderada."),
                N_("Histograma e curva de densidade (KDE) das idades; mostra as populações."),
                N_("Idades da amostra e avisos."),
                N_("Texto de metodologia para o artigo, no idioma escolhido e em inglês."),
                N_("Registro de como a planilha foi lida."))
        for i, texto in enumerate(abas):
            self.abas.setTabWhatsThis(i, tr(texto))
            self.abas.setTabToolTip(i, tr(texto))
        self._nomes_para_leitor_de_tela()

    def _nomes_para_leitor_de_tela(self):
        """Nome e descrição de cada campo para NVDA, JAWS, Narrador, VoiceOver e Orca.

        O Qt passa esses textos ao leitor de tela do sistema. Os campos do painel
        ficam dentro de caixas (com o "?" e a referência), então o rótulo da linha
        não chega sozinho ao campo; aqui ele é copiado.
        """
        for form in self.findChildren(QFormLayout):
            for linha in range(form.rowCount()):
                rotulo = form.itemAt(linha, QFormLayout.LabelRole)
                campo = form.itemAt(linha, QFormLayout.FieldRole)
                if rotulo is None or campo is None or rotulo.widget() is None or campo.widget() is None:
                    continue
                nome = rotulo.widget().text().replace("&", "")
                alvos = [campo.widget()] + campo.widget().findChildren(QWidget)
                for w in alvos:
                    if isinstance(w, (QComboBox, QDoubleSpinBox)):
                        w.setAccessibleName(nome)
                    elif isinstance(w, QToolButton) and w.text() == "?":
                        w.setAccessibleName(tr("Ajuda sobre: {opcao}").format(opcao=nome))
        for w in self.findChildren(QWidget):
            descricao = " ".join(t for t in (w.whatsThis(), w.toolTip()) if t)
            if descricao and not w.accessibleDescription():
                w.setAccessibleDescription(descricao)
        for w, nome in ((self.tabela, N_("Tabela de dados")), (self.tabela_res, N_("Tabela de resultados")),
                        (self.avisos, N_("Avisos")), (self.metodologia, N_("Metodologia")), (self.log, N_("Registro"))):
            w.setAccessibleName(tr(nome))
        for g, nome in ((self.graf_conc, N_("Concórdia ou isócrona")), (self.graf_media, N_("Média ponderada")),
                        (self.graf_dens, N_("Distribuição de idades"))):
            g.canvas.setAccessibleName(tr("Gráfico: {nome}").format(nome=tr(nome)))
            g.canvas.setFocusPolicy(Qt.StrongFocus)  # o leitor de tela chega ao gráfico com Tab

    def _descreve_graficos(self):
        """Resumo em texto dos gráficos, lido pelo leitor de tela (quem não vê a imagem ouve o resultado)."""
        g = self.resultado.graos
        partes = [tr("{n} análises.").format(n=len(g))]
        if "classe" in g:
            contagem = g["classe"].value_counts()
            partes.append(", ".join(f"{contagem[c]} {tr(c)}" for c in ("concordante", "discordante", "rejeitado")
                                    if c in contagem) + ".")
        for r in self.resultado.conjunto:
            partes.append(f"{tr(r['Cálculo'])}: {idiomas.num(r['Idade (Ma)'])} ± {idiomas.num(r['± 2σ (Ma)'])} "
                          f"Ma (2σ), MSWD {idiomas.num(r['MSWD'])}, n = {r['n']}.")
        resumo = " ".join(partes) + " " + tr("Os valores de cada grão estão na aba de dados.")
        for graf in (self.graf_conc, self.graf_media, self.graf_dens):
            graf.canvas.setAccessibleDescription(resumo)

    def _com_ref(self, widget, chave):
        caixa = QWidget()
        l = QVBoxLayout(caixa)
        l.setContentsMargins(0, 0, 0, 0)
        linha = QHBoxLayout()
        linha.addWidget(widget, 1)
        linha.addWidget(self._botao_ajuda(ajuda.TOPICO_DA_OPCAO.get(chave, "inicio")))
        l.addLayout(linha)
        r = QLabel(f"<small><i>{tr('Ref.:')} {tr(REF[chave])}</i></small>")
        r.setWordWrap(True)
        l.addWidget(r)
        widget.setToolTip(tr(REF[chave]))
        return caixa

    def _botao_ajuda(self, topico):
        """Botão "?" que abre o guia na explicação desta opção."""
        b = QToolButton()
        b.setText("?")
        b.setToolTip(tr("O que é isto? Abre a explicação no Guia do Zircon"))
        b.setAccessibleName(tr("Ajuda sobre esta opção"))
        b.clicked.connect(lambda: self.guia(topico))
        return b

    def guia(self, topico="inicio"):
        janela_ajuda.mostrar(self, topico, arquivo_referencias())

    def _painel_opcoes(self):
        op = calculo.OPCOES_PADRAO
        w = QWidget()
        lay = QVBoxLayout(w)
        g1 = QGroupBox(tr("O que calcular"))
        f1 = QFormLayout(g1)
        self.c_media = QComboBox()
        for texto, v in ((tr("Melhor idade por grão"), "melhor"), ("206Pb/238U", "68"), ("207Pb/206Pb", "76")):
            self.c_media.addItem(texto, v)
        f1.addRow(tr("Média ponderada de"), self._com_ref(self.c_media, "media_de"))
        self.c_corte = QDoubleSpinBox(maximum=4600, decimals=0, singleStep=100, suffix=" Ma", value=op["corte_76"])
        f1.addRow(tr("Usar 207Pb/206Pb acima de"), self._com_ref(self.c_corte, "corte_76"))
        self.c_diagrama = QComboBox()
        self.c_diagrama.addItem("Wetherill", "wetherill")
        self.c_diagrama.addItem("Tera-Wasserburg", "tw")
        self.c_diagrama.currentIndexChanged.connect(self._desenha)
        f1.addRow(tr("Diagrama concórdia"), self.c_diagrama)
        self.c_pbc = QComboBox()
        for texto, v in ((tr("Stacey e Kramers (1975)"), "stacey_kramers"), (tr("Composição fixa (Canyon Diablo)"), "fixo"),
                         (tr("Não corrigir"), "nenhuma")):
            self.c_pbc.addItem(texto, v)
        f1.addRow(tr("Pb comum (se houver 204Pb)"), self._com_ref(self.c_pbc, "pb_comum"))
        lay.addWidget(g1)

        g2 = QGroupBox(tr("Como selecionar os grãos"))
        f2 = QFormLayout(g2)
        self.c_disc = QDoubleSpinBox(maximum=100, decimals=1, suffix=" %", value=op["limite_discordancia"])
        f2.addRow(tr("Discordância máxima"), self._com_ref(self.c_disc, "limite_discordancia"))
        self.c_usar_disc = QCheckBox(tr("Incluir discordantes na média"))
        f2.addRow(self.c_usar_disc)
        self.c_outliers = QCheckBox(tr("Rejeitar outliers automaticamente"))
        self.c_outliers.setChecked(op["rejeitar_outliers"])
        f2.addRow(self._com_ref(self.c_outliers, "rejeitar_outliers"))
        self.c_ef = QCheckBox(tr("Considerar dispersão geológica (efeitos aleatórios)"))
        self.c_ef.setChecked(op["efeitos_aleatorios"])
        f2.addRow(self._com_ref(self.c_ef, "efeitos_aleatorios"))
        lay.addWidget(g2)

        g3 = QGroupBox(tr("Cores nos gráficos"))
        f3 = QFormLayout(g3)
        self.c_agrupar = QComboBox()
        for texto, v in ((tr("Concordante / discordante / rejeitado"), "classe"),
                         (tr("Populações de idade (automático)"), "populacoes"),
                         (tr("Grupos que eu escolher"), "manual")):
            self.c_agrupar.addItem(texto, v)
        f3.addRow(tr("Colorir por"), self._com_ref(self.c_agrupar, "agrupar"))
        self.c_minpop = QDoubleSpinBox(minimum=1, maximum=100, decimals=0, value=op["minimo_por_populacao"])
        f3.addRow(tr("Mínimo de grãos por população"), self.c_minpop)
        self._opcoes_de_cor(f3)
        lay.addWidget(g3)

        self.b_calcular = QPushButton(tr("Calcular"))
        self.b_calcular.setMinimumHeight(40)
        self.b_calcular.setStyleSheet("font-weight: bold;")
        self.b_calcular.clicked.connect(self.calcular)
        lay.addWidget(self.b_calcular)
        lay.addStretch()
        rolagem = QScrollArea()
        rolagem.setWidget(w)
        rolagem.setWidgetResizable(True)
        rolagem.setMinimumWidth(int(440 * aparencia.escala(self.aparencia)))
        return rolagem

    # ---------- opções ----------
    def opcoes(self):
        return {"media_de": self.c_media.currentData(), "corte_76": self.c_corte.value(),
                "limite_discordancia": self.c_disc.value(), "usar_discordantes": self.c_usar_disc.isChecked(),
                "rejeitar_outliers": self.c_outliers.isChecked(), "efeitos_aleatorios": self.c_ef.isChecked(),
                "agrupar": self.c_agrupar.currentData(), "minimo_por_populacao": int(self.c_minpop.value()),
                "diagrama": self.c_diagrama.currentData(), "pb_comum": self.c_pbc.currentData()}

    def _aplica_opcoes(self, op):
        def escolhe(combo, v):
            i = combo.findData(v)
            if i >= 0:
                combo.setCurrentIndex(i)
        o = {**calculo.OPCOES_PADRAO, **op}
        escolhe(self.c_media, o["media_de"])
        escolhe(self.c_agrupar, o["agrupar"])
        escolhe(self.c_diagrama, o.get("diagrama", "wetherill"))
        escolhe(self.c_pbc, o["pb_comum"])
        self.c_corte.setValue(o["corte_76"])
        self.c_disc.setValue(o["limite_discordancia"])
        self.c_usar_disc.setChecked(o["usar_discordantes"])
        self.c_outliers.setChecked(o["rejeitar_outliers"])
        self.c_ef.setChecked(o["efeitos_aleatorios"])
        self.c_minpop.setValue(o["minimo_por_populacao"])

    # ---------- arquivo ----------
    def _pode_descartar(self):
        if not self.alterado:
            return True
        r = QMessageBox.question(self, tr("Salvar alterações?"), tr("O projeto atual tem alterações não salvas. Salvar agora?"),
                                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if r == QMessageBox.Save:
            return self.salvar()
        return r == QMessageBox.Discard

    def novo(self, caminho=None):
        if not self._pode_descartar():
            return
        if not caminho:
            caminho, _ = QFileDialog.getOpenFileName(self, tr("Importar planilha do laboratório"),
                                                     self.config.value("pasta", str(Path.home())), tr(FILTRO_PLANILHA))
        if not caminho:
            return
        self.config.setValue("pasta", str(Path(caminho).parent))
        try:
            imp = importar(caminho)
        except Exception as e:  # mostra o problema ao usuário em vez de fechar o programa
            QMessageBox.warning(self, tr("Não consegui ler o arquivo"), f"{Path(caminho).name}:\n{e}")
            return
        if ConfereImportacao(imp, self).exec() != ConfereImportacao.Accepted:
            return
        self.projeto = Projeto(nome=Path(caminho).stem, tipo=imp.tipo, dados=imp.dados, mapa=imp.mapa, log=imp.log,
                               arquivo_original=Path(caminho).name, bytes_original=Path(caminho).read_bytes())
        self._carrega_projeto(alterado=True)

    def abrir(self, caminho=None):
        if not self._pode_descartar():
            return
        if not caminho:
            caminho, _ = QFileDialog.getOpenFileName(self, tr("Abrir projeto"),
                                                     self.config.value("pasta", str(Path.home())), tr(FILTRO_PROJETO))
        if not caminho:
            return
        try:
            self.projeto = Projeto.abrir(caminho)
        except Exception as e:
            QMessageBox.warning(self, tr("Não consegui abrir o projeto"), str(e))
            return
        self._lembra_recente(caminho)
        self._aplica_opcoes(self.projeto.opcoes)
        self._carrega_projeto(alterado=False)

    def _carrega_projeto(self, alterado):
        p = self.projeto
        self.log.setPlainText("\n".join(p.log))
        self.alterado = alterado
        if p.tipo == "desconhecido":
            QMessageBox.information(self, tr("Tipo de dado"), tr("Não reconheci razões U-Pb, Pb-Pb, Th-Pb nem idades "
                                       "nesta planilha. Isócronas U-Th ainda não são calculadas nesta versão."))
            self.tabela.setModel(ModeloTabela(p.dados))
            return
        self.calcular()

    def salvar(self):
        if self.projeto is None:
            return False
        if not self.projeto.caminho:
            return self.salvar_como()
        self.projeto.opcoes = self.opcoes()
        self.projeto.salvar(self.projeto.caminho)
        self.alterado = False
        self._atualiza_titulo()
        self.statusBar().showMessage(tr("Projeto salvo em {caminho}").format(caminho=self.projeto.caminho), 5000)
        return True

    def salvar_como(self):
        if self.projeto is None:
            return False
        sugestao = str(Path(self.config.value("pasta", str(Path.home()))) / (self.projeto.nome + EXTENSAO))
        caminho, _ = QFileDialog.getSaveFileName(self, tr("Salvar projeto"), sugestao, tr(FILTRO_PROJETO))
        if not caminho:
            return False
        self.projeto.caminho = str(Path(caminho).with_suffix(EXTENSAO))
        self.projeto.nome = Path(caminho).stem
        self._lembra_recente(self.projeto.caminho)
        return self.salvar()

    def _lembra_recente(self, caminho):
        rec = [r for r in (self.config.value("recentes", []) or []) if r != caminho]
        self.config.setValue("recentes", [caminho] + rec[:7])
        self._atualiza_recentes()

    def _atualiza_recentes(self):
        self.menu_recentes.clear()
        for r in self.config.value("recentes", []) or []:
            self._acao(self.menu_recentes, r, lambda _=False, c=r: self.abrir(c))

    def _referencias(self):
        cits = [r["Referência"] for r in self.resultado.conjunto] + list(REF.values())
        return exportacao.referencias_abnt(cits, arquivo_referencias())

    def _pede_arquivo(self, titulo, sufixo, filtro):
        if self.resultado is None:
            QMessageBox.information(self, titulo, tr("Calcule primeiro (botão Calcular)."))
            return None
        pasta = Path(self.config.value("pasta", str(Path.home())))
        caminho, _ = QFileDialog.getSaveFileName(self, titulo, str(pasta / (self.projeto.nome + sufixo)), filtro)
        return caminho or None

    def exportar_resultados(self):
        caminho = self._pede_arquivo(tr("Exportar planilha"), "_tabelas.xlsx", "Excel (*.xlsx)")
        if caminho:
            exportacao.excel(caminho, self.projeto, self.resultado, self.opcoes(), self._referencias())
            self.statusBar().showMessage(tr("Planilha salva em {caminho}").format(caminho=caminho), 5000)

    def exportar_interativo(self):
        caminho = self._pede_arquivo(tr("Exportar gráficos interativos"), "_graficos_interativos.html", "HTML (*.html)")
        if caminho:
            exportacao.interativo(caminho, self.resultado, self.opcoes(), f"Zircon - {self.projeto.nome}")
            self.statusBar().showMessage(tr("Gráficos interativos salvos em {caminho}").format(caminho=caminho), 5000)

    def exportar_metodologia(self):
        caminho = self._pede_arquivo(tr("Exportar metodologia"), "_metodologia.md",
                                     tr("Markdown (*.md);;Texto (*.txt)"))
        if caminho:
            texto = self.metodologia.toPlainText()
            if caminho.endswith(".txt"):
                texto = texto.replace("**", "").replace("*", "").replace("# ", "")
            Path(caminho).write_text(texto, encoding="utf-8")
            self.statusBar().showMessage(tr("Metodologia salva em {caminho}").format(caminho=caminho), 5000)

    def exportar_publicacao(self):
        if self.resultado is None:
            QMessageBox.information(self, tr("Exportar"), tr("Calcule primeiro (botão Calcular)."))
            return
        d = ExportaPublicacao(self)
        if d.exec() != ExportaPublicacao.Accepted:
            return
        pasta = QFileDialog.getExistingDirectory(self, tr("Escolha a pasta onde salvar"),
                                                 self.config.value("pasta", str(Path.home())))
        if not pasta:
            return
        destino = Path(pasta) / f"{self.projeto.nome}_publicacao"
        exportacao.pacote(destino, self.projeto, self.resultado, self.opcoes(), d.largura(), d.formatos(),
                          self._referencias(), arquivo_referencias())
        QMessageBox.information(self, tr("Exportado"), tr("Arquivos salvos em:") + f"\n{destino}")
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(destino)))

    def exportar_grafico(self):
        atual = self.abas.currentWidget()
        if not isinstance(atual, graficos.Grafico):
            QMessageBox.information(self, tr("Exportar gráfico"), tr("Abra a aba do gráfico que quer exportar."))
            return
        caminho, _ = QFileDialog.getSaveFileName(self, tr("Exportar gráfico"), "grafico.png",
                                                 tr("PNG (*.png);;SVG (*.svg);;PDF (*.pdf)"))
        if caminho:
            atual.figura.savefig(caminho, dpi=300)

    # ---------- cálculo e grupos ----------
    def calcular(self):
        if self.projeto is None or self.projeto.dados is None:
            QMessageBox.information(self, tr("Calcular"), tr("Primeiro importe uma planilha (Arquivo > Novo projeto)."))
            return
        op = self.opcoes()
        manual = self.projeto.grupo_manual if op["agrupar"] == "manual" else None
        if op["agrupar"] == "manual" and manual is None:
            manual = [1] * len(self.projeto.dados)
            self.projeto.grupo_manual = manual
        try:
            self.resultado = calculo.calcular(self.projeto.dados, self.projeto.tipo, op, manual)
        except Exception as e:
            QMessageBox.warning(self, tr("Erro no cálculo"), str(e))
            return
        if self.projeto.opcoes != op:
            self.alterado = self.alterado or bool(self.projeto.opcoes)
        self.projeto.opcoes = op
        g = self.resultado.graos
        visiveis = [c for c in ("amostra", "analise", "melhor", "s_melhor", "discordancia", "classe", "grupo",
                                "valido", "t68", "s_t68", "t75", "s_t75", "t76", "s_t76",
                                "r75", "s75", "r68", "s68", "r64", "s64", "r74", "s74", "r24", "s24",
                                "r84", "s84", "rho") if c in g]
        self.tabela.setModel(ModeloTabela(g[visiveis].reset_index(drop=True), list(g.cor)))
        self.tabela.resizeColumnsToContents()
        res = exportacao.tabela_resultados(self.resultado.conjunto)
        self.tabela_res.setModel(ModeloTabela(res))
        self.tabela_res.resizeColumnsToContents()
        self.avisos.setPlainText("\n".join(self.resultado.avisos) or tr("Sem avisos."))
        self.metodologia.setPlainText(metodologia.gerar(self.projeto, self.resultado, op, arquivo_referencias()))
        self._desenha()
        self._atualiza_titulo()

    def _desenha(self):
        if self.resultado is None:
            return
        with self._estilo_graficos():
            self._desenha_graficos()
        self._descreve_graficos()

    def _desenha_graficos(self):
        g, op = self.resultado.graos, self.opcoes()
        if self.resultado.isocrona:
            graficos.isocrona(self.graf_conc, g, self.resultado.isocrona)
            self.graf_media.limpar(N_("Isócrona: veja a aba Concórdia ou isócrona"))
            self.graf_dens.limpar(N_("Isócrona: sem idades por grão"))
            return
        if "r75" in g:
            from ..nucleo import estatistica
            disc = None
            if len(g) >= 3:
                disc = estatistica.discordia(g.r75, g.s75, g.r68, g.s68, g.rho)
            graficos.concordia(self.graf_conc, g, op["diagrama"], op["agrupar"], disc)
        else:
            self.graf_conc.limpar(N_("A planilha só tem idades: o diagrama concórdia precisa das razões isotópicas"))
        coluna = {"68": "t68", "76": "t76", "melhor": "melhor"}[op["media_de"]]
        media = next((r for r in self.resultado.conjunto if r["Cálculo"].startswith("Média ponderada")), None)
        if coluna in g:
            graficos.media_ponderada(self.graf_media, g, coluna, media, op["agrupar"])
        graficos.densidade(self.graf_dens, g, "melhor", op["agrupar"])

    def _muda_agrupamento(self, v):
        self.c_agrupar.setCurrentIndex(self.c_agrupar.findData(v))
        self.calcular()

    def atribuir_grupo(self):
        if self.projeto is None:
            return
        linhas = sorted({i.row() for i in self.tabela.selectionModel().selectedRows()})
        if not linhas:
            QMessageBox.information(self, tr("Grupos"), tr("Selecione as linhas na tabela de dados (clique no número "
                                       "da linha; use Ctrl ou Shift para várias)."))
            return
        n, ok = QInputDialog.getInt(self, tr("Grupo"), tr("Número do grupo para as linhas selecionadas:"), 2, 1, 8)
        if not ok:
            return
        if self.projeto.grupo_manual is None:
            self.projeto.grupo_manual = [1] * len(self.projeto.dados)
        for i in linhas:
            self.projeto.grupo_manual[i] = n
        self.alterado = True
        self._muda_agrupamento("manual")

    def _troca_idioma(self, cod):
        """Muda o idioma e remonta a janela, mantendo o projeto e as opções."""
        if cod == idiomas.atual():
            return
        self.config.setValue("idioma", cod)
        aplica_idioma(cod)
        self.setLocale(QLocale())  # os campos herdam da janela, não do padrão novo
        self._remonta()

    def _remonta(self):
        """Refaz menus, painéis e gráficos (depois de mudar idioma, letra, tema ou cores)."""
        op = self.opcoes()
        self.menuBar().clear()
        self._menus()
        with self._estilo_graficos():
            self._layout()
        self._aplica_opcoes(op)
        if self.projeto is not None:
            self.log.setPlainText("\n".join(self.projeto.log))
            if self.resultado is not None:
                alterado = self.alterado
                self.calcular()
                self.alterado = alterado
        self._atualiza_titulo()

    def _atualiza_titulo(self):
        nome = self.projeto.nome if self.projeto else tr("sem projeto")
        self.setWindowTitle(f"Zircon {__version__} - {nome}{' *' if self.alterado else ''}")

    def closeEvent(self, ev):
        if self._pode_descartar():
            ev.accept()
        else:
            ev.ignore()

    def boas_vindas(self):
        if self.config.value("sem_boas_vindas", False, type=bool):
            return
        d = BoasVindas(self)
        d.exec()
        if d.idioma:
            self._troca_idioma(d.idioma)
            return self.boas_vindas()
        if d.nao_mostrar.isChecked():
            self.config.setValue("sem_boas_vindas", True)
        if d.escolha == BoasVindas.NOVO:
            self.novo()
        elif d.escolha == BoasVindas.ABRIR:
            self.abrir()
        elif d.escolha == BoasVindas.EXEMPLO:
            ex = pasta_exemplos() / "UPb1.xlsx"
            if ex.exists():
                self.novo(str(ex))


def aplica_idioma(cod):
    """Idioma dos textos, direção da escrita (árabe da direita para a esquerda) e botões do Qt."""
    idiomas.definir(cod)
    app = QApplication.instance()
    app.setLayoutDirection(Qt.RightToLeft if idiomas.direita_para_esquerda() else Qt.LeftToRight)
    for t in getattr(app, "_tradutores", []):
        app.removeTranslator(t)
    app._tradutores = []
    nome_qt = {"pt_BR": "pt_BR", "pt_PT": "pt_PT", "zh": "zh_CN"}.get(cod, cod)
    # caixas de número com a vírgula ou o ponto do idioma (algarismos ocidentais em todos)
    QLocale.setDefault(QLocale(nome_qt) if idiomas.decimal() == "," else QLocale(QLocale.English))
    try:
        pasta = (QLibraryInfo.path(QLibraryInfo.TranslationsPath) if hasattr(QLibraryInfo, "path")
                 else QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    except Exception:  # sem traduções do Qt: os botões padrão ficam em inglês
        return
    for pasta in (pasta,):
        for base in ("qtbase", "qt"):
            t = QTranslator(app)
            if t.load(f"{base}_{nome_qt}", pasta) or t.load(f"{base}_{nome_qt.split('_')[0]}", pasta):
                app.installTranslator(t)
                app._tradutores.append(t)
                break


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Zircon")
    app.setOrganizationName("Zircon")
    aparencia.aplicar(app, aparencia.ler(QSettings("Zircon", "Zircon")))
    escolhido = QSettings("Zircon", "Zircon").value("idioma", "")
    aplica_idioma(escolhido or idiomas.codigo_do_sistema(QLocale.system().name()))
    app.setDesktopFileName("zircon")  # liga a janela ao atalho no Linux (GNOME, COSMIC, KDE)
    icone = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2] / "instalador")) / "zircon.png"
    if icone.exists():
        app.setWindowIcon(QIcon(str(icone)))
    j = Janela()
    j.show()
    if "--teste-inicio" in sys.argv:  # usado na montagem para conferir que o programa abre
        QTimer.singleShot(3000, app.quit)
        return app.exec()
    arq = next((a for a in sys.argv[1:] if a.endswith(EXTENSAO)), None)
    if "--registrar" in sys.argv:
        Registro(j).exec()
    if arq:
        j.abrir(arq)
    else:
        j.boas_vindas()
    return app.exec()
