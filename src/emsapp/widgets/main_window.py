from PyQt5 import QtCore, QtWidgets
from emsapp.config import Config
from emsapp.logging import get_logger
from emsapp.i18n import _, ngettext
from emsapp.widgets.importation import configure_db
from emsapp.widgets.preview import PlotPreview

logger = get_logger()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout()
        mw = QtWidgets.QWidget(self)
        self.setCentralWidget(mw)
        mw.setLayout(layout)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_("&File"))
        open_action = file_menu.addAction(_("&Open..."))
        open_action.setShortcut(_("Ctrl+O"))
        open_action.setStatusTip(_("Open a database"))
        open_action.triggered.connect(configure_db)

        self.preview = PlotPreview()

        layout.addWidget(self.preview)
