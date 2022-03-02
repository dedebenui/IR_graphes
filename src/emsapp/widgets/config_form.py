from __future__ import annotations

from enum import Enum
from typing import Any, Callable, TypeVar, Union

from emsapp import i18n
from emsapp.i18n import _
from emsapp.widgets.common import TranslatableComboBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLabel,
    QWidget,
)

T = TypeVar("T")


class ConfigForm(QWidget):
    sig_value_changed = pyqtSignal(str, object)
    labels: dict[str, QLabel]
    controls: dict[str, QWidget]

    def __init__(self, *specs: Union[QWidget, tuple[str, type, Any]]):
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        self.labels = {}
        self.controls = {}
        for spec in specs:
            if isinstance(spec, QWidget):
                layout.addRow(spec)
                continue
            lbl, tpe, dft = spec
            qlabel = QLabel("")
            self.labels[lbl] = qlabel
            self.controls[lbl] = create_control(tpe, dft, self.create_callback(lbl))
            layout.addRow(qlabel, self.controls[lbl])
        i18n.register(self)

    def __getitem__(self, key: str) -> QWidget:
        return self.controls[key]

    def update_text(self):
        for lbl, qlabel in self.labels.items():
            qlabel.setText(_(lbl))

    def create_callback(self, name: str):
        def callback(val):
            self.sig_value_changed.emit(name, val)

        return callback


def create_control(tpe: type[T], dft: T, callback: Callable[[T], None]) -> QWidget:
    """
    Creates a Qwidget adapted to the provided type and connects
    the provided callback
    """
    if tpe is bool:
        control = QCheckBox()
        control.setChecked(dft)
        control.stateChanged.connect(callback)
    elif issubclass(tpe, Enum):
        vals = list(tpe._value2member_map_)
        dft_index = vals.index(dft.value)
        control = TranslatableComboBox(vals)
        control.setCurrentIndex(dft_index)
        control.currentRawTextChanged.connect(lambda txt: callback(tpe(txt)))
    else:
        raise TypeError(f"No available control for type {tpe}")
    return control
