import re
from emsapp.data.loading import Entry, RawData, DataLoader, DataLoaderFactory
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
import sys

from emsapp.config import Config
from emsapp.widgets.common import ValuesSelector, AcceptCancel
from emsapp import const
from emsapp.i18n import _, ngettext
from emsapp.logging import get_logger

logger = get_logger()


class DataLoadingError(ValueError):
    ...


class FileSelector(QtWidgets.QWidget):
    file_path: Path
    sig_path_changed = QtCore.pyqtSignal(Path)

    def __init__(self, parent=None, default_path: os.PathLike = None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.file_path = default_path or Config().data.db_path
        self.file_path_label = QtWidgets.QLabel(str(self.file_path))
        self.choose_path_button = QtWidgets.QPushButton(_("Select path"))
        self.choose_path_button.clicked.connect(self.choose_path)
        self.choose_path_button.setMaximumWidth(120)

        layout.addWidget(self.choose_path_button)
        layout.addWidget(self.file_path_label)

    def choose_path(self) -> Path:
        filter = f"{_('database files')} ({' '.join(f'*{ext}' for ext in DataLoaderFactory.all_extensions())})"
        out = QtWidgets.QFileDialog.getOpenFileName(
            self, _("Choose a database file"), str(self.file_path.parent), filter
        )[0]
        if out:
            self.file_path = Config().data.db_path = Path(out)
            self.file_path_label.setText(str(self.file_path))
            self.sig_path_changed.emit(self.file_path)


class TableSelector(ValuesSelector):
    def __init__(self, values: list[str] = None):
        super().__init__("Table", values, Config().data.table_name)
        self.sig_selection_changed.connect(self.table_changed)

    def update_values(self, values: list[str], selection: str = None):
        super().update_values(values, selection)
        Config().dump()
        if not self.valid:
            self.tool_tip_txt = _(
                "No table found in {path}. Please ensure tables are defined in this file."
            ).format(path=Config().data.db_path.name)
        else:
            self.tool_tip_txt = ""

    def table_changed(self, new_table: str):
        Config().data.table_name = new_table


class ColumnSelector(QtWidgets.QWidget):
    selectors: list[ValuesSelector]
    did_change: bool

    sig_column_changed = QtCore.pyqtSignal(str, str)

    def __init__(self, headers: list[str] = None):
        super().__init__()

        headers = headers or []
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.selectors = [
            ValuesSelector(key, headers, getattr(Config().data, f"col_{key}"))
            for key in Entry.fields()
        ]
        self.did_change = False
        for selector in self.selectors:
            layout.addWidget(selector)
            selector.sig_selection_changed.connect(
                self.column_changed_callback(selector)
            )

    def update_headers(self, headers: list[str]):
        for selector in self.selectors:
            selector.update_values(
                headers, getattr(Config().data, f"col_{selector.name}")
            )

    def column_changed_callback(self, selector: ValuesSelector):
        def column_changed(new_name: str):
            if selector.valid:
                setattr(Config().data, "col_" + selector.name, new_name)
                self.sig_column_changed.emit(selector.name, new_name)

        return column_changed

    @property
    def valid(self) -> bool:
        return all(s.valid for s in self.selectors)

    def current_selection(self) -> list[str]:
        return [selector.value for selector in self.selectors]


class ImportWindow(QtWidgets.QDialog):
    did_accept: bool
    data_loader: DataLoader = None

    def __init__(self, default_path: os.PathLike = None):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.did_accept = False

        self.file_selector = FileSelector(default_path=default_path)
        self.table_selector = TableSelector()
        self.column_selector = ColumnSelector()
        self.finish_buttons = AcceptCancel()

        self.file_selector.sig_path_changed.connect(self.file_changed)
        self.table_selector.sig_selection_changed.connect(self.table_changed)
        self.column_selector.sig_column_changed.connect(self.columns_changed)
        self.finish_buttons.sig_clicked.connect(self.finish_import)

        layout.addWidget(self.file_selector)
        layout.addWidget(self.table_selector)
        layout.addWidget(self.column_selector)
        layout.addWidget(self.finish_buttons)

        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, False)

        self.file_changed(Config().data.db_path)
        if self.data_loader is None:
            self.file_selector.choose_path()

    def file_changed(self, new_path: Path):
        tables = None
        if DataLoaderFactory.valid(new_path):
            try:
                self.data_loader = DataLoaderFactory.create(new_path)
                tables = self.data_loader.tables(Config().data)
            except Exception:
                pass
        if not tables:
            self.data_loader = None
            tables = []
        self.finish_buttons.ok_button.setDisabled(self.data_loader is None)
        self.table_selector.update_values(tables, Config().data.table_name)
        self.table_changed()

    def table_changed(self):
        if self.data_loader:
            self.column_selector.update_headers(self.data_loader.headers(Config().data))
        self.update_ok_button()

    def columns_changed(self, col_key: str, new_name: str):
        logger.debug(f"Column changed : {col_key} = {new_name}")
        self.update_ok_button()

    def update_ok_button(self):
        valid = (
            self.data_loader is not None
            and self.table_selector.valid
            and self.column_selector.valid
        )
        self.finish_buttons.ok_button.setDisabled(not valid)

    def finish_import(self, accept: bool):
        self.did_accept = accept
        self.close()


def configure_db(parent: QtWidgets.QWidget = None) -> DataLoader:
    with Config().hold():
        import_win = ImportWindow()
        import_win.exec_()
        if import_win.did_accept:
            Config().commit()
    if parent:
        parent.activateWindow()
    Config().dump()
    if import_win.did_accept:
        return import_win.data_loader


def main():
    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            menu_bar = self.menuBar()

            file_menu = menu_bar.addMenu("&File")
            open_action = file_menu.addAction("&Open...")
            open_action.setShortcut("Ctrl+O")
            open_action.setStatusTip("Open a database")
            open_action.triggered.connect(self.open_db)

            self.button = QtWidgets.QPushButton(open_action.text())
            self.button.clicked.connect(open_action.trigger)

            self.setCentralWidget(self.button)

        def open_db(self) -> DataLoader:
            with Config().hold():
                import_win = ImportWindow()
                import_win.exec_()
                if import_win.did_accept:
                    Config().commit()
            self.activateWindow()
            Config().dump()

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    try:
        app.exec()
    except Exception:
        print(Config().json(indent=2))
        raise


if __name__ == "__main__":
    main()
