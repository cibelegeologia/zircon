"""Janela principal do Zircon."""
import sys
from pathlib import Path

import pandas as pd
from .qt import QSettings, Qt, QTimer, QUrl
from .qt import QAction, QDesktopServices, QIcon, QKeySequence
from .qt import (QAbstractItemView, QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
                               QFormLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMessageBox,
                               QPlainTextEdit, QPushButton, QScrollArea, QSplitter, QTableView, QTabWidget,
                               QVBoxLayout, QWidget)

from .. import __version__
from ..nucleo import calculo, exportacao, grupos, metodologia
from ..nucleo.importacao import importar
from ..nucleo.projeto import EXTENSAO, Projeto
from . import graficos
from .dialogos import BoasVindas, ConfereImportacao, ExportaPublicacao, Registro, sobre_texto
from .modelos import ModeloTabela

FILTRO_PLANILHA = "Planilhas (*.xlsx *.xls *.ods *.csv *.txt *.tsv);;Todos os arquivos (*)"
FILTRO_PROJETO = f"Projeto Zircon (*{EXTENSAO})"
REF = {
    "efeitos_aleatorios": "Vermeesch (2018a), Geoscience Frontiers 9:1479-1493",
    "rejeitar_outliers": "Chauvenet generalizado: Vermeesch (2018a)",
    "corte_76": "Spencer, Kirkland e Taylor (2016); Gehrels (2014)",
    "limite_discordancia": "Spencer, Kirkland e Taylor (2016), Geoscience Frontiers 7:581-589",
    "media_de": "Wendt e Carl (1991), Chemical Geology 86:275-285",
    "agrupar": grupos.REFERENCIAS["populacoes"],
    "pb_comum": "Stacey e Kramers (1975); Williams (1998)",
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
        self._menus()
        self._layout()
        self._atualiza_titulo()

    # ---------- montagem ----------
    def _acao(self, menu, texto, func, atalho=None):
        a = QAction(texto, self)
        if atalho:
            a.setShortcut(atalho)
        a.triggered.connect(func)
        menu.addAction(a)
        return a

    def _menus(self):
        m = self.menuBar().addMenu("&Arquivo")
        self._acao(m, "&Novo projeto (importar planilha)...", self.novo, QKeySequence.New)
        self._acao(m, "&Abrir projeto...", self.abrir, QKeySequence.Open)
        self.menu_recentes = m.addMenu("Projetos recentes")
        m.addSeparator()
        self._acao(m, "&Salvar", self.salvar, QKeySequence.Save)
        self._acao(m, "Salvar &como...", self.salvar_como, QKeySequence.SaveAs)
        m.addSeparator()
        self._acao(m, "Exportar para publicação (figuras, Excel, interativo, metodologia)...",
                   self.exportar_publicacao, "Ctrl+E")
        self._acao(m, "Exportar planilha Excel formatada...", self.exportar_resultados)
        self._acao(m, "Exportar gráfico atual...", self.exportar_grafico)
        self._acao(m, "Exportar gráficos interativos (HTML)...", self.exportar_interativo)
        self._acao(m, "Exportar metodologia (Markdown ou texto)...", self.exportar_metodologia)
        m.addSeparator()
        self._acao(m, "Sai&r", self.close, QKeySequence.Quit)
        m = self.menuBar().addMenu("&Grupos")
        self._acao(m, "Colocar linhas selecionadas no grupo...", self.atribuir_grupo)
        self._acao(m, "Voltar às cores automáticas", lambda: self._muda_agrupamento("classe"))
        m = self.menuBar().addMenu("Aj&uda")
        self._acao(m, "Registrar o Zircon...", lambda: Registro(self).exec())
        self._acao(m, "Sobre o Zircon", lambda: QMessageBox.about(self, "Sobre", sobre_texto()))
        self._atualiza_recentes()

    def _layout(self):
        divisor = QSplitter()
        divisor.addWidget(self._painel_opcoes())
        self.abas = QTabWidget()
        self.tabela = QTableView()
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSortingEnabled(False)
        self.abas.addTab(self.tabela, "Dados e idades por grão")
        self.graf_conc = graficos.Grafico()
        self.abas.addTab(self.graf_conc, "Concórdia ou isócrona")
        self.graf_media = graficos.Grafico()
        self.abas.addTab(self.graf_media, "Média ponderada")
        self.graf_dens = graficos.Grafico()
        self.abas.addTab(self.graf_dens, "Distribuição de idades")
        res = QWidget()
        lr = QVBoxLayout(res)
        self.tabela_res = QTableView()
        lr.addWidget(self.tabela_res)
        self.avisos = QPlainTextEdit()
        self.avisos.setReadOnly(True)
        self.avisos.setMaximumHeight(140)
        lr.addWidget(QLabel("Avisos e interpretação"))
        lr.addWidget(self.avisos)
        self.abas.addTab(res, "Resultados")
        self.metodologia = QPlainTextEdit()
        self.metodologia.setReadOnly(True)
        self.abas.addTab(self.metodologia, "Metodologia (texto para o artigo)")
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.abas.addTab(self.log, "Registro da importação")
        divisor.addWidget(self.abas)
        divisor.setStretchFactor(1, 1)
        divisor.setSizes([460, 820])
        self.setCentralWidget(divisor)
        for g in (self.graf_conc, self.graf_media, self.graf_dens):
            g.limpar()

    def _com_ref(self, widget, chave):
        caixa = QWidget()
        l = QVBoxLayout(caixa)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(widget)
        r = QLabel(f"<small><i>Ref.: {REF[chave]}</i></small>")
        r.setWordWrap(True)
        l.addWidget(r)
        widget.setToolTip(REF[chave])
        return caixa

    def _painel_opcoes(self):
        op = calculo.OPCOES_PADRAO
        w = QWidget()
        lay = QVBoxLayout(w)
        g1 = QGroupBox("O que calcular")
        f1 = QFormLayout(g1)
        self.c_media = QComboBox()
        for texto, v in (("Melhor idade por grão", "melhor"), ("206Pb/238U", "68"), ("207Pb/206Pb", "76")):
            self.c_media.addItem(texto, v)
        f1.addRow("Média ponderada de", self._com_ref(self.c_media, "media_de"))
        self.c_corte = QDoubleSpinBox(maximum=4600, decimals=0, singleStep=100, suffix=" Ma", value=op["corte_76"])
        f1.addRow("Usar 207Pb/206Pb acima de", self._com_ref(self.c_corte, "corte_76"))
        self.c_diagrama = QComboBox()
        self.c_diagrama.addItem("Wetherill", "wetherill")
        self.c_diagrama.addItem("Tera-Wasserburg", "tw")
        self.c_diagrama.currentIndexChanged.connect(self._desenha)
        f1.addRow("Diagrama concórdia", self.c_diagrama)
        self.c_pbc = QComboBox()
        for texto, v in (("Stacey e Kramers (1975)", "stacey_kramers"), ("Composição fixa (Canyon Diablo)", "fixo"),
                         ("Não corrigir", "nenhuma")):
            self.c_pbc.addItem(texto, v)
        f1.addRow("Pb comum (se houver 204Pb)", self._com_ref(self.c_pbc, "pb_comum"))
        lay.addWidget(g1)

        g2 = QGroupBox("Como selecionar os grãos")
        f2 = QFormLayout(g2)
        self.c_disc = QDoubleSpinBox(maximum=100, decimals=1, suffix=" %", value=op["limite_discordancia"])
        f2.addRow("Discordância máxima", self._com_ref(self.c_disc, "limite_discordancia"))
        self.c_usar_disc = QCheckBox("Incluir discordantes na média")
        f2.addRow(self.c_usar_disc)
        self.c_outliers = QCheckBox("Rejeitar outliers automaticamente")
        self.c_outliers.setChecked(op["rejeitar_outliers"])
        f2.addRow(self._com_ref(self.c_outliers, "rejeitar_outliers"))
        self.c_ef = QCheckBox("Considerar dispersão geológica (efeitos aleatórios)")
        self.c_ef.setChecked(op["efeitos_aleatorios"])
        f2.addRow(self._com_ref(self.c_ef, "efeitos_aleatorios"))
        lay.addWidget(g2)

        g3 = QGroupBox("Cores nos gráficos")
        f3 = QFormLayout(g3)
        self.c_agrupar = QComboBox()
        for texto, v in (("Concordante / discordante / rejeitado", "classe"),
                         ("Populações de idade (automático)", "populacoes"),
                         ("Grupos que eu escolher", "manual")):
            self.c_agrupar.addItem(texto, v)
        f3.addRow("Colorir por", self._com_ref(self.c_agrupar, "agrupar"))
        self.c_minpop = QDoubleSpinBox(minimum=1, maximum=100, decimals=0, value=op["minimo_por_populacao"])
        f3.addRow("Mínimo de grãos por população", self.c_minpop)
        lay.addWidget(g3)

        self.b_calcular = QPushButton("Calcular")
        self.b_calcular.setMinimumHeight(40)
        self.b_calcular.setStyleSheet("font-weight: bold;")
        self.b_calcular.clicked.connect(self.calcular)
        lay.addWidget(self.b_calcular)
        lay.addStretch()
        rolagem = QScrollArea()
        rolagem.setWidget(w)
        rolagem.setWidgetResizable(True)
        rolagem.setMinimumWidth(440)
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
        r = QMessageBox.question(self, "Salvar alterações?", "O projeto atual tem alterações não salvas. Salvar agora?",
                                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if r == QMessageBox.Save:
            return self.salvar()
        return r == QMessageBox.Discard

    def novo(self, caminho=None):
        if not self._pode_descartar():
            return
        if not caminho:
            caminho, _ = QFileDialog.getOpenFileName(self, "Importar planilha do laboratório",
                                                     self.config.value("pasta", str(Path.home())), FILTRO_PLANILHA)
        if not caminho:
            return
        self.config.setValue("pasta", str(Path(caminho).parent))
        try:
            imp = importar(caminho)
        except Exception as e:  # mostra o problema ao usuário em vez de fechar o programa
            QMessageBox.warning(self, "Não consegui ler o arquivo", f"{Path(caminho).name}:\n{e}")
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
            caminho, _ = QFileDialog.getOpenFileName(self, "Abrir projeto",
                                                     self.config.value("pasta", str(Path.home())), FILTRO_PROJETO)
        if not caminho:
            return
        try:
            self.projeto = Projeto.abrir(caminho)
        except Exception as e:
            QMessageBox.warning(self, "Não consegui abrir o projeto", str(e))
            return
        self._lembra_recente(caminho)
        self._aplica_opcoes(self.projeto.opcoes)
        self._carrega_projeto(alterado=False)

    def _carrega_projeto(self, alterado):
        p = self.projeto
        self.log.setPlainText("\n".join(p.log))
        self.alterado = alterado
        if p.tipo == "desconhecido":
            QMessageBox.information(self, "Tipo de dado", "Não reconheci razões U-Pb, Pb-Pb, Th-Pb nem idades "
                                    "nesta planilha. Isócronas U-Th ainda não são calculadas nesta versão.")
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
        self.statusBar().showMessage(f"Projeto salvo em {self.projeto.caminho}", 5000)
        return True

    def salvar_como(self):
        if self.projeto is None:
            return False
        sugestao = str(Path(self.config.value("pasta", str(Path.home()))) / (self.projeto.nome + EXTENSAO))
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar projeto", sugestao, FILTRO_PROJETO)
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
        cits = [r["Referência"] for r in self.resultado.conjunto] + [REF[k] for k in REF]
        return exportacao.referencias_abnt(cits, arquivo_referencias())

    def _pede_arquivo(self, titulo, sufixo, filtro):
        if self.resultado is None:
            QMessageBox.information(self, titulo, "Calcule primeiro (botão Calcular).")
            return None
        pasta = Path(self.config.value("pasta", str(Path.home())))
        caminho, _ = QFileDialog.getSaveFileName(self, titulo, str(pasta / (self.projeto.nome + sufixo)), filtro)
        return caminho or None

    def exportar_resultados(self):
        caminho = self._pede_arquivo("Exportar planilha", "_tabelas.xlsx", "Excel (*.xlsx)")
        if caminho:
            exportacao.excel(caminho, self.projeto, self.resultado, self.opcoes(), self._referencias())
            self.statusBar().showMessage(f"Planilha salva em {caminho}", 5000)

    def exportar_interativo(self):
        caminho = self._pede_arquivo("Exportar gráficos interativos", "_graficos_interativos.html", "HTML (*.html)")
        if caminho:
            exportacao.interativo(caminho, self.resultado, self.opcoes(), f"Zircon - {self.projeto.nome}")
            self.statusBar().showMessage(f"Gráficos interativos salvos em {caminho}", 5000)

    def exportar_metodologia(self):
        caminho = self._pede_arquivo("Exportar metodologia", "_metodologia.md",
                                     "Markdown (*.md);;Texto (*.txt)")
        if caminho:
            texto = self.metodologia.toPlainText()
            if caminho.endswith(".txt"):
                texto = texto.replace("**", "").replace("*", "").replace("# ", "")
            Path(caminho).write_text(texto, encoding="utf-8")
            self.statusBar().showMessage(f"Metodologia salva em {caminho}", 5000)

    def exportar_publicacao(self):
        if self.resultado is None:
            QMessageBox.information(self, "Exportar", "Calcule primeiro (botão Calcular).")
            return
        d = ExportaPublicacao(self)
        if d.exec() != ExportaPublicacao.Accepted:
            return
        pasta = QFileDialog.getExistingDirectory(self, "Escolha a pasta onde salvar",
                                                 self.config.value("pasta", str(Path.home())))
        if not pasta:
            return
        destino = Path(pasta) / f"{self.projeto.nome}_publicacao"
        exportacao.pacote(destino, self.projeto, self.resultado, self.opcoes(), d.largura(), d.formatos(),
                          self._referencias(), arquivo_referencias())
        QMessageBox.information(self, "Exportado", f"Arquivos salvos em:\n{destino}")
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(destino)))

    def exportar_grafico(self):
        atual = self.abas.currentWidget()
        if not isinstance(atual, graficos.Grafico):
            QMessageBox.information(self, "Exportar gráfico", "Abra a aba do gráfico que quer exportar.")
            return
        caminho, _ = QFileDialog.getSaveFileName(self, "Exportar gráfico", "grafico.png",
                                                 "PNG (*.png);;SVG (*.svg);;PDF (*.pdf)")
        if caminho:
            atual.figura.savefig(caminho, dpi=300)

    # ---------- cálculo e grupos ----------
    def calcular(self):
        if self.projeto is None or self.projeto.dados is None:
            QMessageBox.information(self, "Calcular", "Primeiro importe uma planilha (Arquivo > Novo projeto).")
            return
        op = self.opcoes()
        manual = self.projeto.grupo_manual if op["agrupar"] == "manual" else None
        if op["agrupar"] == "manual" and manual is None:
            manual = [1] * len(self.projeto.dados)
            self.projeto.grupo_manual = manual
        try:
            self.resultado = calculo.calcular(self.projeto.dados, self.projeto.tipo, op, manual)
        except Exception as e:
            QMessageBox.warning(self, "Erro no cálculo", str(e))
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
        res = pd.DataFrame(self.resultado.conjunto)
        self.tabela_res.setModel(ModeloTabela(res))
        self.tabela_res.resizeColumnsToContents()
        self.avisos.setPlainText("\n".join(self.resultado.avisos) or "Sem avisos.")
        self.metodologia.setPlainText(metodologia.gerar(self.projeto, self.resultado, op, arquivo_referencias()))
        self._desenha()
        self._atualiza_titulo()

    def _desenha(self):
        if self.resultado is None:
            return
        g, op = self.resultado.graos, self.opcoes()
        if self.resultado.isocrona:
            graficos.isocrona(self.graf_conc, g, self.resultado.isocrona)
            self.graf_media.limpar("Isócrona: veja a aba Concórdia ou isócrona")
            self.graf_dens.limpar("Isócrona: sem idades por grão")
            return
        if "r75" in g:
            from ..nucleo import estatistica
            disc = None
            if len(g) >= 3:
                disc = estatistica.discordia(g.r75, g.s75, g.r68, g.s68, g.rho)
            graficos.concordia(self.graf_conc, g, op["diagrama"], op["agrupar"], disc)
        else:
            self.graf_conc.limpar("A planilha só tem idades: o diagrama concórdia precisa das razões isotópicas")
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
            QMessageBox.information(self, "Grupos", "Selecione as linhas na tabela de dados (clique no número "
                                    "da linha; use Ctrl ou Shift para várias).")
            return
        n, ok = QInputDialog.getInt(self, "Grupo", "Número do grupo para as linhas selecionadas:", 2, 1, 8)
        if not ok:
            return
        if self.projeto.grupo_manual is None:
            self.projeto.grupo_manual = [1] * len(self.projeto.dados)
        for i in linhas:
            self.projeto.grupo_manual[i] = n
        self.alterado = True
        self._muda_agrupamento("manual")

    def _atualiza_titulo(self):
        nome = self.projeto.nome if self.projeto else "sem projeto"
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


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Zircon")
    app.setOrganizationName("Zircon")
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
