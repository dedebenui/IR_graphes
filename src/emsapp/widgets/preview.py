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
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 350)
        self.canvas = MplCanvas()
        toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

    def plot(self, data_set:DataSet):
        self.canvas.ax.clear()
        plotter = Plotter(self.canvas.ax)
        plotter.plot(data_set)
        self.canvas.draw()