from __future__ import annotations

from typing import Iterable, Optional, TypeVar

from PyQt5.QtCore import QSortFilterProxyModel, Qt, pyqtSignal, QObject, QEvent
from PyQt5.QtGui import QMouseEvent, QShowEvent, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from emsapp import i18n
from emsapp.i18n import _

T = TypeVar("T")


class QWidgetWithHelp(QWidget):
    show_tool_tip: bool = False
    __tttxt: str = ""

    @property
    def tool_tip_txt(self) -> str:
        return self.__tttxt

    @tool_tip_txt.setter
    def tool_tip_txt(self, txt: str):
        self.__tttxt = txt
        self.setMouseTracking(bool(txt))

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        super().mouseMoveEvent(e)
        if self.__tttxt:
            p = self.mapToGlobal(e.pos())
            QToolTip.showText(p, self.__tttxt)


class TranslatableComboBox(QComboBox):
    """
    combobox that displays translated text, but adds a signal
    to return the original, non translated value
    """

    currentRawTextChanged = pyqtSignal(str)

    def __init__(self, values: Iterable[str]):
        super().__init__()
        self.raw_values = list(values)
        self.currentIndexChanged.connect(
            lambda i: self.currentRawTextChanged.emit(self.raw_values[i])
        )
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        i18n.register(self)

    def update_text(self):
        selected = self.currentIndex()
        self.blockSignals(True)
        self.clear()
        self.insertItems(0, [_(el) for el in self.raw_values])
        self.setCurrentIndex(selected)
        self.blockSignals(False)


class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self._completer = QCompleter(self.pFilterModel, self)
        self._completer.popup().installEventFilter(self)
        self.lineEdit().setCompleter(self._completer)
        # # always show all (filtered) completions
        self._completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self._completer)

        # # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self._completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self._completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self._completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


class ValuesSelector(QWidgetWithHelp):
    values: list[str]
    sig_selection_changed = pyqtSignal(str)
    valid: bool = False
    box: QComboBox

    def __init__(
        self,
        label: str,
        values: list[str] = None,
        selection: str = None,
        ComboBoxClass: type[QComboBox] = QComboBox,
    ):
        super().__init__()
        self.name = label
        self.values = values or []
        layout = QFormLayout()
        self.setLayout(layout)
        self.label = QLabel("", self)
        self.box = ComboBoxClass(self)
        layout.addRow(self.label, self.box)
        self.box.currentTextChanged.connect(self.sig_selection_changed.emit)
        self.update_values(self.values, selection)
        i18n.register(self)

    @property
    def value(self) -> str:
        return self.box.currentText()

    @property
    def index(self) -> str:
        return self.box.currentIndex()

    def update_values(
        self, values: list[str], selection: str = None, always_emit=False
    ):
        """update the possible values in the dropdown box

        Parameters
        ----------
        values : list[str]
            list of possible values. Will override any existing ones
        selection : str, optional
            if given, selects this value
        always_emit : bool, optional
            if the current selection is present in the new list of values, sig_selection_changed
            will not emit unless this flag is set to True
        """
        selected = selection or self.box.currentText()
        self.values = values
        if selected in self.values:
            new_index = self.values.index(selected)
            must_emit = always_emit
        else:
            new_index = 0
            must_emit = True

        self.box.blockSignals(True)
        self.box.clear()
        self.box.insertItems(0, self.values)
        self.box.setDisabled(not self.valid)
        self.box.setCurrentIndex(new_index)
        self.box.blockSignals(False)

        if must_emit:
            self.sig_selection_changed.emit(self.value)

    def update_text(self):
        self.label.setText(_(self.name))

    @property
    def valid(self) -> bool:
        return bool(self.values)

    def set_text(self, lbl: str):
        self.label.setText(lbl)


class AcceptCancel(QWidget):

    sig_clicked = pyqtSignal(bool)

    def __init__(self, horizontal=True):
        super().__init__()
        if horizontal:
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()
        self.setLayout(layout)

        self.ok_button = QPushButton(_("Ok"))
        self.cancel_button = QPushButton(_("Cancel"))

        self.ok_button.clicked.connect(lambda: self.sig_clicked.emit(True))
        self.cancel_button.clicked.connect(lambda: self.sig_clicked.emit(False))

        layout.addWidget(self.cancel_button)
        layout.addWidget(self.ok_button)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setDefault(False)
        self.ok_button.setAutoDefault(True)
        self.ok_button.setDefault(True)


class UserInput(QDialog):
    value: Optional[str] = None

    def __init__(self, msg: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(msg)
        self.line_edit = QLineEdit()
        self.line_edit.setText(self.value)
        finish_button = AcceptCancel()
        finish_button.sig_clicked.connect(self.finish)

        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(finish_button)
        self.setWindowTitle("EMSapp")

    def finish(self, accept: bool):
        if accept:
            self.value = self.line_edit.text()
        else:
            self.value = None
        self.close()


def get_user_input(msg: str, parent=None) -> Optional[str]:
    input_win = UserInput(msg)
    input_win.exec_()
    if parent:
        parent.activateWindow()
    return input_win.value
