from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets

from emsapp.config import Config
from emsapp.data import DataSet
from emsapp.plotting.plotter import Plotter


class MplCanvas(FigureCanvasQTAgg):
    fig: Figure
    ax: Axes
    fig_size: QtCore.QSize

    def __init__(self, parent=None):
        w, h = Config().plot.figsize
        self.fig = Figure(figsize=(w, h), tight_layout=True)
        dpi = self.fig.dpi
        self.ax = self.fig.add_subplot(111)
        self.fig_size = QtCore.QSize(int(self.fig.dpi * w), int(self.fig.dpi * h))
        super().__init__(self.fig)


class PlotPreview(QtWidgets.QWidget):
    plotter: Plotter = None

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


def main():
    import sys

    from PyQt5.QtWidgets import QApplication

    import emsapp.startup

    app = QApplication(sys.argv)
    win = PlotPreview()
    win.show()
    print(win.canvas.fig.get_size_inches())
    win.canvas.resize_fig(20, 10)
    print(win.canvas.fig.get_size_inches())
    app.exec()


if __name__ == "__main__":
    main()
