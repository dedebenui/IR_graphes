from typing import Any, Optional
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QApplication,
    QMessageBox,
    QPushButton,
)
from PyQt5.QtGui import QShowEvent, QImage
from PyQt5.QtCore import pyqtSignal
import pkg_resources
from emsapp import data

from emsapp.config import Config, LegendLoc
from emsapp.const import PLOT_MAX_WIDTH, PLOT_MIN_WIDTH
from emsapp.data import DataSet
from emsapp.data.loading import Entries, load_data
from emsapp.data.process import Process
from emsapp import i18n
from emsapp.i18n import N_, _
from emsapp.logging import get_logger
from emsapp.plotting.plotter import Plotter
from emsapp.widgets.importation import configure_db
from emsapp.widgets.preview import PlotPreview
from emsapp.widgets.common import ExtendedComboBox, ValuesSelector
from emsapp.widgets.config_form import ConfigForm, ControlSpecs
from emsapp.widgets.info_box import InfoBox


logger = get_logger()

config_specs = [
    ControlSpecs(
        name=N_("show_periods_info"),
        dtype=bool,
        default=Config().plot.show_periods_info,
        tooltip=N_("Display duration and number of affected people on the plot"),
    ),
    ControlSpecs(
        name=N_("legend_loc"),
        dtype=LegendLoc,
        default=Config().plot.legend_loc,
        tooltip=N_("Choose where to display the legend"),
    ),
    ControlSpecs(
        name=N_("plot_width"),
        dtype=float,
        min=PLOT_MIN_WIDTH,
        max=PLOT_MAX_WIDTH,
        default=Config().plot.plot_width,
        tooltip=N_("Specify the width of the plot"),
        needs_refresh=False,
    ),
    ControlSpecs(
        name=N_("plot_height"),
        dtype=float,
        min=PLOT_MIN_WIDTH,
        max=PLOT_MAX_WIDTH,
        default=Config().plot.plot_height,
        tooltip=N_("Specify the height of the plot"),
        needs_refresh=False,
    ),
]


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

        self.status_bar = self.statusBar()
        self.config_specs = {c.name: c for c in config_specs}

        menu_bar = self.menuBar()
        self.m_file = menu_bar.addMenu("")
        self.a_open = self.m_file.addAction("")
        self.a_open.setShortcut("Ctrl+O")
        self.a_open.triggered.connect(self.load_new_database)

        self.a_logs = self.m_file.addAction("")
        self.a_logs.triggered.connect(self.show_logs)

        self.m_data = menu_bar.addMenu("")
        self.a_copy_plot = self.m_data.addAction("")
        self.a_copy_plot.setShortcut("Ctrl+C")
        self.a_copy_plot.triggered.connect(self.copy_plot)

        self.a_show_data = self.m_data.addAction("")
        self.a_show_data.triggered.connect(self.show_data)

        self.m_option = menu_bar.addMenu("")
        self.m_lang = self.m_option.addMenu("")
        self.a_lang_list = []
        for lang in i18n.AVAILABLE:
            action = self.m_lang.addAction(lang)
            action.triggered.connect(self.change_language_callback(lang))
            self.a_lang_list.append(action)

        self.preview = PlotPreview()
        self.data_selector = ValuesSelector(
            N_("Select data to preview"), ComboBoxClass=ExtendedComboBox
        )
        self.p_config_options = ConfigForm(*self.config_specs.values())
        self.b_copy_plot = QPushButton()
        self.b_show_data = QPushButton()

        self.data_selector.sig_selection_changed.connect(self.update_preview)
        self.p_config_options.sig_value_changed.connect(self.plot_config_changed)
        self.b_copy_plot.clicked.connect(self.a_copy_plot.trigger)
        self.b_show_data.clicked.connect(self.a_show_data.trigger)

        layout.addWidget(self.data_selector, 0, 0, 1, 1)
        layout.addWidget(self.preview, 1, 0, 2, 1)
        layout.addWidget(self.p_config_options, 0, 1, 2, 2)
        layout.addWidget(self.b_copy_plot, 2, 1, 1, 1)
        layout.addWidget(self.b_show_data, 2, 2, 1, 1)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        # self.resize(1000, 700)

        i18n.register(self)

    def update_text(self):
        self.m_file.setTitle(_("&File"))
        self.m_data.setTitle(_("&Data"))

        self.a_open.setText(_("&Open..."))
        self.a_open.setToolTip(_("Open a database"))
        self.a_logs.setText(_("Show &logs"))
        self.a_logs.setToolTip(_("Open the logs to attempt to solve a problem"))

        self.a_copy_plot.setText(_("&Copy plot"))
        self.a_copy_plot.setToolTip(_("Copy current plot to clip board"))
        self.a_show_data.setText(_("&Show data"))
        self.a_show_data.setToolTip(_("Show current data as text"))

        self.b_copy_plot.setText(self.a_copy_plot.text())
        self.b_show_data.setText(self.a_show_data.text())

        self.m_option.setTitle(_("&Options"))
        self.m_lang.setTitle(_("&Language"))
        for action, lang in zip(self.a_lang_list, i18n.AVAILABLE):
            action.setToolTip(
                _("Change the current language to {lang}").format(lang=lang)
            )

    def plot_config_changed(self, config_name: str, value: Any):
        setattr(Config().plot, config_name, value)
        if self.config_specs[config_name].needs_refresh:
            self.update_preview()

    def change_language_callback(self, lang: str):
        def change_lang():
            i18n.set_lang(lang)
            self.update_preview()

        return change_lang

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
                logger.info(
                    _("couldn't load {path}").format(path=Config().data.db_path)
                )
                configure_db(self)
        self.processed_data = {}
        for ds in self.process(entries):
            self.processed_data[ds.title] = ds
        self.sig_loading_event.emit(_("data processed"))

        self.data_selector.update_values(sorted(self.processed_data), Config().data.last_selected)

    def get_selected_data(self) -> Optional[DataSet]:
        """returns an optional dataset representing the current user selection"""
        if not self.data_selector.valid:
            return
        selected = self.data_selector.value
        Config().data.last_selected = selected
        return self.processed_data.get(selected)

    def update_preview(self):
        """refreshes the plot based on the current user selection"""
        dataset = self.get_selected_data()
        if not dataset:
            return
        self.preview.plot(dataset)

    def copy_plot(self) -> bool:
        """Puts the currently displayed plot in the clipboard as a png image"""
        data_set = self.get_selected_data()
        if not data_set:
            self.status_bar.showMessage(_("Could not copy plot"), 3000)
            return False
        plotter = Plotter(data_set)
        buffer = plotter.as_bytes()
        QApplication.clipboard().setImage(QImage.fromData(buffer))
        self.status_bar.showMessage(_("Plot copied !"), 3000)
        return True

    def show_data(self):
        """opens a dialog box with the current data"""
        msg = InfoBox(self.data_selector.value, self.preview.plotter.extra_info)
        msg.exec()
        self.focusWidget()

    def show_logs(self):
        """opens a dialog box with the logs of the program"""
        msg = InfoBox(
            _("Most recent logs"),
            pkg_resources.resource_string("emsapp", "logs/emsapp.log").decode(),
        )
        msg.exec()
        self.focusWidget()
