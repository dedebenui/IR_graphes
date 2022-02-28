from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from emsapp.data import DataSet
from emsapp.plotting.plotter import Plotter


class MplCanvas(FigureCanvasQTAgg):
    fig: Figure
    ax: Axes

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class PlotPreview(QtWidgets.QWidget):
    plotter:Plotter = None
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 350)
        self.canvas = MplCanvas()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def plot(self, data_set: DataSet):
        self.canvas.ax.clear()
        self.plotter = Plotter(data_set, self.canvas.ax)
        self.canvas.draw()
        self.toolbar.update()
