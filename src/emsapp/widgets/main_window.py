import datetime
from typing import Any, Optional

import pkg_resources
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QShowEvent, QIcon, QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QWidget,
)

from emsapp import i18n
from emsapp.config import Config, LegendLoc, PlotConfig
from emsapp.const import PLOT_MAX_WIDTH, PLOT_MIN_WIDTH
from emsapp.data import DataSet
from emsapp.data.loading import Entries, load_data
from emsapp.data.process import Process
from emsapp.i18n import N_, _
from emsapp.plotting.plotter import Plotter
from emsapp.utils import get_logger
from emsapp.widgets.common import ExtendedComboBox, ValuesSelector
from emsapp.widgets.config_form import ConfigForm, ControlSpecs, set_value
from emsapp.widgets.importation import configure_db
from emsapp.widgets.info_box import InfoBox
from emsapp.widgets.preview import PlotPreview

logger = get_logger()

CONFIG_SPECS = [
    ControlSpecs(
        name=N_("show_periods_info"),
        dtype=bool,
        default=Config().plot.show_periods_info,
        tooltip=N_("Display duration and number of affected people on the plot"),
    ),
    ControlSpecs(
        name=N_("show_today"),
        dtype=bool,
        default=Config().plot.show_today,
        tooltip=N_("Show a red line on today's date"),
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
        tooltip=N_("Width of the plot when exported"),
        needs_refresh=False,
    ),
    ControlSpecs(
        name=N_("plot_height"),
        dtype=float,
        min=PLOT_MIN_WIDTH,
        max=PLOT_MAX_WIDTH,
        default=Config().plot.plot_height,
        tooltip=N_("Height of the plot when exported"),
        needs_refresh=False,
    ),
    ControlSpecs(
        name=N_("show_everything"),
        dtype=bool,
        default=Config().plot.show_everything,
        tooltip=N_(
            "Show every data point possible. If this is unchecked, the "
            "dates specified below will be used to limit the plot area"
        ),
    ),
    ControlSpecs(
        name=N_("date_start"),
        dtype=datetime.date,
        default=Config().plot.date_start,
        tooltip=N_("choose on which day the plot starts"),
    ),
    ControlSpecs(
        name=N_("date_end"),
        dtype=datetime.date,
        default=Config().plot.date_end,
        tooltip=N_("choose on which day the plot ends"),
    ),
]


class MainWindow(QMainWindow):

    processed_data: dict[str, DataSet] = None
    sig_loading_event = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sig_loading_event.emit(_("opening database..."))
        self.setWindowIcon(
            QIcon(
                pkg_resources.resource_filename(
                    "emsapp", "package_data/building_icon.png"
                )
            )
        )
        layout = QGridLayout()
        mw = QWidget(self)
        mw.setLayout(layout)
        self.setCentralWidget(mw)

        select_layout = QHBoxLayout()
        w_selection = QWidget()
        w_selection.setLayout(select_layout)

        self.status_bar = self.statusBar()
        self.config_specs: dict[str, ControlSpecs] = {c.name: c for c in CONFIG_SPECS}

        menu_bar = self.menuBar()
        self.m_file = menu_bar.addMenu("")
        self.a_open = self.m_file.addAction("")
        self.a_open.setShortcut("Ctrl+O")
        self.a_open.triggered.connect(self.load_new_database)

        self.a_logs = self.m_file.addAction("")
        self.a_logs.triggered.connect(self.show_logs)

        self.m_plot = menu_bar.addMenu("")
        self.a_copy_plot = self.m_plot.addAction("")
        self.a_copy_plot.setShortcut("Ctrl+C")

        self.a_show_data = self.m_plot.addAction("")
        self.a_next_plot = self.m_plot.addAction("")
        self.a_prev_plot = self.m_plot.addAction("")

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
        self.b_copy_plot = QPushButton()
        self.b_show_data = QPushButton()
        self.b_reset_config = QPushButton()
        self.b_next_plot = QPushButton(">")
        self.b_prev_plot = QPushButton("<")
        self.p_config_options = ConfigForm(
            *self.config_specs.values(), self.b_reset_config
        )

        select_layout.addWidget(self.data_selector)
        select_layout.addWidget(self.b_prev_plot)
        select_layout.addWidget(self.b_next_plot)
        select_layout.setStretchFactor(self.data_selector, 1)
        select_layout.setStretchFactor(self.b_next_plot, 0)
        select_layout.setStretchFactor(self.b_prev_plot, 0)

        layout.addWidget(w_selection, 0, 0, 1, 1)
        layout.addWidget(self.preview, 1, 0, 2, 1)
        layout.addWidget(self.p_config_options, 0, 1, 2, 2)
        layout.addWidget(self.b_copy_plot, 2, 1, 1, 1)
        layout.addWidget(self.b_show_data, 2, 2, 1, 1)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)
        # self.resize(1000, 700)

        i18n.register(self)

        self.process = Process.from_config()

        self.data_selector.sig_selection_changed.connect(self.update_ui)
        self.p_config_options.sig_value_changed.connect(self.plot_config_changed)
        self.a_copy_plot.triggered.connect(self.copy_plot)
        self.a_show_data.triggered.connect(self.show_data)
        self.b_copy_plot.clicked.connect(self.a_copy_plot.trigger)
        self.b_show_data.clicked.connect(self.a_show_data.trigger)
        self.b_reset_config.clicked.connect(self.reset_plot_config)
        self.a_next_plot.triggered.connect(self.show_next)
        self.b_next_plot.clicked.connect(self.a_next_plot.trigger)
        self.a_prev_plot.triggered.connect(self.show_prev)
        self.b_prev_plot.clicked.connect(self.a_prev_plot.trigger)

        self.focusWidget()

    def update_text(self):
        self.set_title()

        self.m_file.setTitle(_("&File"))
        self.m_plot.setTitle(_("&Plot"))

        self.a_open.setText(_("&Open..."))
        self.a_open.setToolTip(_("Open a database"))
        self.a_logs.setText(_("Show &logs"))
        self.a_logs.setToolTip(_("Open the logs to attempt to solve a problem"))

        self.a_copy_plot.setText(_("&Copy plot"))
        self.a_copy_plot.setToolTip(_("Copy current plot to clip board"))
        self.a_show_data.setText(_("&Show data"))
        self.a_show_data.setToolTip(_("Show current data as text"))
        self.a_next_plot.setText(_("&Next"))
        self.a_next_plot.setToolTip(_("Show next plot"))
        self.a_prev_plot.setText(_("&Previous"))
        self.a_prev_plot.setToolTip(_("Show previous plot"))

        self.b_copy_plot.setText(self.a_copy_plot.text())
        self.b_copy_plot.setToolTip(self.a_copy_plot.toolTip())
        self.b_show_data.setText(self.a_show_data.text())
        self.b_show_data.setToolTip(self.a_show_data.toolTip())
        self.b_reset_config.setText(_("reset plot config"))
        self.b_next_plot.setToolTip(self.a_next_plot.toolTip())
        self.b_prev_plot.setToolTip(self.a_prev_plot.toolTip())

        self.m_option.setTitle(_("&Options"))
        self.m_lang.setTitle(_("&Language"))
        for action, lang in zip(self.a_lang_list, i18n.AVAILABLE):
            action.setToolTip(
                _("Change the current language to {lang}").format(lang=lang)
            )

    def set_title(self):
        if self.processed_data:
            self.setWindowTitle(
                _("emsapp - Plots of the Covid-19 in retirement homes - Fribourg")
            )
        else:
            self.setWindowTitle(_("emsapp - Loading..."))

    def plot_config_changed(self, config_name: str, value: Any):
        setattr(Config().plot, config_name, value)
        if self.config_specs[config_name].needs_refresh:
            self.update_ui()

    def change_language_callback(self, lang: str):
        def change_lang():
            i18n.set_lang(lang)
            self.update_ui()

        return change_lang

    def showEvent(self, a0: QShowEvent) -> None:
        super().showEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        Config().save()
        return super().closeEvent(a0)

    def load_new_database(self) -> Entries:
        if configure_db(self):
            self.processed_data = None
            self.set_title()
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
                if not configure_db(self):
                    self.close()
                    return
        self.processed_data = {}
        for ds in self.process(entries):
            self.processed_data[ds.title] = ds
        self.sig_loading_event.emit(_("data processed"))
        self.data_selector.update_values(
            sorted(self.processed_data), Config().data.last_selected
        )
        self.update_ui()

    def get_selected_data(self) -> Optional[DataSet]:
        """returns an optional dataset representing the current user selection"""
        if not self.data_selector.valid:
            return
        selected = self.data_selector.value
        Config().data.last_selected = selected
        return self.processed_data.get(selected)

    def update_ui(self):
        self.p_config_options.controls["date_start"].setDisabled(
            Config().plot.show_everything
        )
        self.p_config_options.controls["date_end"].setDisabled(
            Config().plot.show_everything
        )
        self.update_preview()
        self.set_title()

    def update_preview(self):
        """refreshes the plot based on the current user selection"""
        dataset = self.get_selected_data()
        if not dataset:
            return
        Config().save()
        self.preview.plot(dataset)

    def reset_plot_config(self):
        Config().plot = PlotConfig(**Config.default().plot.dict())
        for name, control in self.p_config_options.controls.items():
            set_value(control, getattr(Config().plot, name))
        self.update_ui()

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

    def show_next(self):
        """Show the next plot in the list"""
        i = self.data_selector.box.currentIndex() + 1
        if i < len(self.data_selector.values):
            self.data_selector.box.setCurrentIndex(i)

    def show_prev(self):
        """Show the next plot in the list"""
        i = self.data_selector.box.currentIndex() - 1
        if i >= 0:
            self.data_selector.box.setCurrentIndex(i)
