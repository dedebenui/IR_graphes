from __future__ import annotations
from dataclasses import dataclass

from enum import Enum
from typing import Any, Callable, Generic, TypeVar, Union

from numpy import dtype

from emsapp import i18n
from emsapp.i18n import _
from emsapp.widgets.common import TranslatableComboBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QCheckBox, QFormLayout, QLabel, QWidget, QLineEdit

T = TypeVar("T")


class ConfigForm(QWidget):
    sig_value_changed = pyqtSignal(str, object)
    labels: dict[str, QLabel]
    controls: dict[str, QWidget]
    tooltip = None

    def __init__(self, *specs: Union[QWidget, ControlSpecs]):
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        self.labels = {}
        self.controls = {}
        for spec in specs:
            if isinstance(spec, QWidget):
                layout.addRow(spec)
                continue
            self.tooltip = spec.tooltip or None
            qlabel = QLabel("")
            self.labels[spec.name] = qlabel
            self.controls[spec.name] = create_control(
                spec, self.create_callback(spec.name)
            )
            layout.addRow(qlabel, self.controls[spec.name])

        i18n.register(self)

    def __getitem__(self, key: str) -> QWidget:
        return self.controls[key]

    def update_text(self):
        self.setToolTip(_(self.tooltip))
        for lbl, qlabel in self.labels.items():
            qlabel.setText(_(lbl))

    def create_callback(self, name: str):
        def callback(val):
            self.sig_value_changed.emit(name, val)

        return callback


@dataclass
class ControlSpecs(Generic[T]):
    name: str
    dtype: type[T]
    default: Any
    tooltip: str = None
    min: Any = None
    max: Any = None
    needs_refresh: bool = True


def create_control(specs: ControlSpecs, callback: Callable[[T], None]) -> QWidget:
    """
    Creates a Qwidget adapted to the provided type and connects
    the provided callback
    """
    if specs.dtype is float:
        control = QLineEdit()
        validator = QDoubleValidator()
        validator.setDecimals(3)
        if specs.max:
            validator.setTop(specs.max)
        if specs.min:
            validator.setBottom(specs.min)
        control.setValidator(validator)
        control.setText(str(specs.default) or "")
        control.textEdited.connect(lambda txt: callback(specs.dtype(txt)))
    elif specs.dtype is bool:
        control = QCheckBox()
        control.setChecked(specs.default)
        control.stateChanged.connect(callback)
    elif issubclass(specs.dtype, Enum):
        vals = list(specs.dtype._value2member_map_)
        dft_index = vals.index(specs.default.value)
        control = TranslatableComboBox(vals)
        control.setCurrentIndex(dft_index)
        control.currentRawTextChanged.connect(lambda txt: callback(specs.dtype(txt)))
    else:
        raise TypeError(f"No available control for type {specs.dtype}")
    return control