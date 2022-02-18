from PyQt5 import QtWidgets, QtCore, QtGui

from emsapp.i18n import _


class QWidgetWithHelp(QtWidgets.QWidget):
    show_tool_tip: bool = False
    __tttxt: str = ""

    @property
    def tool_tip_txt(self) -> str:
        return self.__tttxt

    @tool_tip_txt.setter
    def tool_tip_txt(self, txt: str):
        self.__tttxt = txt
        self.setMouseTracking(bool(txt))

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(e)
        if self.__tttxt:
            p = self.mapToGlobal(e.pos())
            QtWidgets.QToolTip.showText(p, self.__tttxt)


class ValuesSelector(QWidgetWithHelp):
    sig_selection_changed = QtCore.pyqtSignal(str)
    valid: bool = False

    def __init__(self, label: str, values: list[str] = None, selection: str = None):
        super().__init__()
        self.name = label
        values = values or []
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.label = QtWidgets.QLabel(_(label), self)
        self.box = QtWidgets.QComboBox(self)
        layout.addWidget(self.label)
        layout.addWidget(self.box)
        self.box.currentTextChanged.connect(self.sig_selection_changed.emit)
        self.update_values(values, selection)

    @property
    def value(self) -> str:
        return self.box.currentText()

    def update_values(self, values: list[str], selection: str = None):
        """update the possible values in the dropdown box

        Parameters
        ----------
        values : list[str]
            list of possible values. Will override any existing ones
        selection : str, optional
            if given, selects this value
        """
        selected = selection or self.box.currentText()
        if selected in values:
            new_index = values.index(selected)
            must_emit = False
        else:
            new_index = 0
            must_emit = True

        self.box.blockSignals(True)
        self.box.clear()
        self.box.insertItems(0, values)
        self.valid = bool(values)
        self.box.setDisabled(not self.valid)
        self.box.setCurrentIndex(new_index)
        self.box.blockSignals(False)

        if must_emit:
            self.sig_selection_changed.emit(self.value)


class AcceptCancel(QtWidgets.QWidget):

    sig_clicked = QtCore.pyqtSignal(bool)

    def __init__(self, horizontal=True):
        super().__init__()
        if horizontal:
            layout = QtWidgets.QHBoxLayout()
        else:
            layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.ok_button = QtWidgets.QPushButton("ok")
        self.cancel_button = QtWidgets.QPushButton("cancel")

        self.ok_button.clicked.connect(lambda: self.sig_clicked.emit(True))
        self.cancel_button.clicked.connect(lambda: self.sig_clicked.emit(False))

        layout.addWidget(self.cancel_button)
        layout.addWidget(self.ok_button)
