"""Modelo de tabela do Qt para DataFrames, com cor de fundo por grupo."""
import numpy as np
import pandas as pd
from .qt import QAbstractTableModel, QModelIndex, Qt
from .qt import QColor

from ..idiomas import N_, tr

NOMES = {
    "amostra": N_("Amostra"), "analise": N_("Análise"), "r75": "207Pb/235U", "s75": "± 1σ", "r68": "206Pb/238U",
    "s68": "± 1σ", "rho": "rho", "r86": "238U/206Pb", "s86": "± 1σ", "r76": "207Pb/206Pb", "s76": "± 1σ",
    "t75": N_("Idade 7/35 (Ma)"), "s_t75": "± 1σ", "t68": N_("Idade 6/38 (Ma)"), "s_t68": "± 1σ",
    "t76": N_("Idade 7/6 (Ma)"), "s_t76": "± 1σ", "melhor": N_("Melhor idade (Ma)"), "s_melhor": "± 1σ",
    "discordancia": N_("Discordância (%)"), "classe": N_("Classe"), "grupo": N_("Grupo"), "valido": N_("Usado na média"),
    "idade": N_("Idade (Ma)"), "s_idade": "± 1σ", "tconc": N_("Idade concórdia (Ma)"), "sconc": "± 1σ",
}


class ModeloTabela(QAbstractTableModel):
    def __init__(self, df=None, cores=None, parent=None):
        super().__init__(parent)
        self.df = df if df is not None else pd.DataFrame()
        self.cores = cores

    def rowCount(self, parent=QModelIndex()):
        return len(self.df)

    def columnCount(self, parent=QModelIndex()):
        return len(self.df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.df) or index.column() >= len(self.df.columns):
            return None
        v = self.df.iat[index.row(), index.column()]
        if role == Qt.DisplayRole:
            if isinstance(v, (bool, np.bool_)):
                return tr("sim") if v else tr("não")
            if isinstance(v, (float, np.floating)):
                if np.isnan(v):
                    return ""
                return f"{v:.6g}"
            if self.df.columns[index.column()] == "classe":
                return tr(str(v))
            return str(v)
        if role == Qt.BackgroundRole and self.cores is not None:
            return QColor(self.cores[index.row()] + "40")
        if role == Qt.TextAlignmentRole and isinstance(v, (float, np.floating, int)):
            return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    def headerData(self, sec, orient, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orient == Qt.Horizontal and sec >= len(self.df.columns):
            return None
        if orient == Qt.Horizontal:
            c = str(self.df.columns[sec])
            return tr(NOMES.get(c, c))
        return str(sec + 1)
