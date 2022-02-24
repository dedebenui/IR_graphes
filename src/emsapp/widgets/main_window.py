from PyQt5 import QtCore, QtWidgets

from emsapp.config import Config
from emsapp.data import DataSet
from emsapp.data.loading import Entries, load_data
from emsapp.data.process import Process
from emsapp.i18n import _
from emsapp.logging import get_logger
from emsapp.widgets.importation import configure_db
from emsapp.widgets.preview import PlotPreview
from emsapp.widgets.common import ExtendedComboBox, ValuesSelector


logger = get_logger()


class MainWindow(QtWidgets.QMainWindow):

    processed_data: dict[str, DataSet] = None

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout()
        mw = QtWidgets.QWidget(self)
        mw.setLayout(layout)
        self.setCentralWidget(mw)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_("&File"))
        open_action = file_menu.addAction(_("&Open..."))
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip(_("Open a database"))
        open_action.triggered.connect(self.load_new_database)

        self.preview = PlotPreview()
        self.data_selector = ValuesSelector(
            _("Select data to preview"), ComboBoxClass=ExtendedComboBox
        )
        self.data_selector.sig_selection_changed.connect(self.update_preview)

        layout.addWidget(self.data_selector)
        layout.addWidget(self.preview)

        self.process = Process.from_config()

        self.load_and_process()

    def load_new_database(self) -> Entries:
        configure_db(self)
        self.load_and_process()

    def load_and_process(self):
        while True:
            try:
                entries = load_data()
                break
            except ValueError:
                logger.info(_("couldn't load {path}").format(path=Config().data.db_path))
                configure_db(self)
        self.processed_data = {}
        for ds in self.process(entries):
            self.processed_data[ds.title] = ds

        self.data_selector.update_values(sorted(self.processed_data))

    def update_preview(self):
        if not self.data_selector.valid:
            return
        selected = self.data_selector.value
        dataset = self.processed_data.get(selected)
        if not dataset:
            return
        self.preview.plot(dataset)
