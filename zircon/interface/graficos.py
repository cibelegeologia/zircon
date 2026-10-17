"""Widget de gráfico da interface; o desenho fica em nucleo/desenho.py."""
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..nucleo.desenho import concordia, densidade, media_ponderada  # noqa: F401 (usados pela janela)


class Grafico(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figura = Figure(figsize=(7, 5), layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figura)
        lay = QVBoxLayout(self)
        lay.addWidget(NavigationToolbar2QT(self.canvas, self))
        lay.addWidget(self.canvas)

    def limpar(self, texto="Importe uma planilha e clique em Calcular"):
        self.figura.clear()
        ax = self.figura.add_subplot()
        ax.text(0.5, 0.5, texto, ha="center", va="center", color="#666666")
        ax.set_axis_off()
        self.canvas.draw_idle()


