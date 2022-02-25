from typing import Optional
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QApplication
from PyQt5.QtGui import QShowEvent, QImage
from PyQt5.QtCore import pyqtSignal
from emsapp import data

from emsapp.config import Config
from emsapp.data import DataSet
from emsapp.data.loading import Entries, load_data
from emsapp.data.process import Process
from emsapp.i18n import _
from emsapp.logging import get_logger
from emsapp.plotting.plotter import Plotter
from emsapp.widgets.importation import configure_db
from emsapp.widgets.preview import PlotPreview
from emsapp.widgets.common import ExtendedComboBox, ValuesSelector


logger = get_logger()


class MainWindow(QMainWindow):

    processed_data: dict[str, DataSet] = None
    sig_loading_event = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sig_loading_event.emit(_("opening database..."))
        layout = QGridLayout()
        mw = QWidget(self)
        mw.setLayout(layout)
        self.setCentralWidget(mw)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_("&File"))
        open_action = file_menu.addAction(_("&Open..."))
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip(_("Open a database"))
        open_action.triggered.connect(self.load_new_database)

        copy_action = file_menu.addAction(_("&Copy"))
        copy_action.setShortcut("Ctrl+c")
        copy_action.setToolTip(_("Copy current plot to clip board"))
        copy_action.triggered.connect(self.copy_plot)

        self.preview = PlotPreview()
        self.data_selector = ValuesSelector(
            _("Select data to preview"), ComboBoxClass=ExtendedComboBox
        )
        

        self.data_selector.sig_selection_changed.connect(self.update_preview)

        layout.addWidget(self.data_selector, 0, 0, 1, 4)
        layout.addWidget(self.preview, 1, 0, 1, 4)


    def showEvent(self, a0: QShowEvent) -> None:
        super().showEvent(a0)
        self.process = Process.from_config()
        self.load_and_process()

    def load_new_database(self) -> Entries:
        configure_db(self)
        self.load_and_process()

    def load_and_process(self):
        while True:
            try:
                entries = load_data()
                self.sig_loading_event.emit(_("data loaded"))
                break
            except ValueError:
                logger.info(_("couldn't load {path}").format(path=Config().data.db_path))
                configure_db(self)
        self.processed_data = {}
        for ds in self.process(entries):
            self.processed_data[ds.title] = ds
        self.sig_loading_event.emit(_("data processed"))

        self.data_selector.update_values(sorted(self.processed_data))

    def get_selected_data(self) -> Optional[DataSet]:
        if not self.data_selector.valid:
            return
        selected = self.data_selector.value
        return self.processed_data.get(selected)

    def update_preview(self):
        dataset = self.get_selected_data()
        if not dataset:
            return
        self.preview.plot(dataset)

    def copy_plot(self) -> bool:
        data_set = self.get_selected_data()
        if not data_set:
            return False
        plotter = Plotter()
        plotter.plot(data_set)
        buffer = plotter.as_bytes()
        QApplication.clipboard().setImage(QImage.fromData(buffer))
        return True
