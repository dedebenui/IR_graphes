from PyQt5 import QtWidgets


class PlotPreview(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 350)