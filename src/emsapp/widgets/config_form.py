from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, Protocol, TypeVar, Union

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QFormLayout,
    QLabel,
    QLineEdit,
    QWidget,
)

from emsapp import i18n
from emsapp.i18n import _
from emsapp.widgets.common import TranslatableComboBox

T = TypeVar("T")


class ConfigForm(QWidget):
    sig_value_changed = pyqtSignal(str, object)
    labels: dict[str, QLabel]
    controls: dict[str, QWidget]
    tooltip = None

    def __init__(self, *specs: Union[QWidget, tuple[QLabel, QWidget], ControlSpecs]):
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        self.labels = {}
        self.controls = {}
        for spec in specs:
            if (
                isinstance(spec, QWidget)
                or isinstance(spec, tuple)
                and isinstance(spec[0], QLabel)
            ):
                layout.addRow(spec)
                continue
            qlabel = QLabel("")
            control = create_control(spec, self.create_callback(spec.name))
            layout.addRow(qlabel, control)
            if spec.tooltip:
                qlabel.setToolTip(_(spec.tooltip))
                control.setToolTip(_(spec.tooltip))
            self.labels[spec.name] = qlabel
            self.controls[spec.name] = control

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
        control.editingFinished.connect(lambda: callback(specs.dtype(control.text())))
    elif specs.dtype is datetime.date:
        control = QDateEdit()
        control.setCalendarPopup(True)
        control.setDate(specs.default)
        control.dateChanged.connect(
            lambda date: callback(datetime.date(date.year(), date.month(), date.day()))
        )
    elif specs.dtype is bool:
        control = QCheckBox()
        control.setChecked(specs.default)
        control.stateChanged.connect(lambda state: callback(specs.dtype(state)))
    elif issubclass(specs.dtype, Enum):
        vals = list(specs.dtype._value2member_map_)
        dft_index = vals.index(specs.default.value)
        control = TranslatableComboBox(vals)
        control.setCurrentIndex(dft_index)
        control.currentRawTextChanged.connect(lambda txt: callback(specs.dtype(txt)))
    else:
        raise TypeError(f"No available control for type {specs.dtype}")
    return control


def set_value(control: QWidget, value):
    if isinstance(control, QLineEdit):
        control.setText(str(value))
    elif isinstance(control, QDateEdit):
        control.setDate(value)
    elif isinstance(control, QCheckBox):
        control.setChecked(bool(value))
    elif isinstance(control, TranslatableComboBox):
        if isinstance(value, Enum):
            vals = list(value.__class__._value2member_map_)
            value = vals.index(value.value)
        elif isinstance(value, str):
            value = control.raw_values.index(value)
        control.setCurrentIndex(value)
