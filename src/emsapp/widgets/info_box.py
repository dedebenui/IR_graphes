from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Iterable, Optional, TypeVar, Union

from PyQt5.QtCore import QSortFilterProxyModel, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)

from emsapp.const import MSG_DURATION
from emsapp.i18n import _
from emsapp.utils import get_logger

logger = get_logger(__name__)


class InfoBox(QDialog):
    header: str
    msg: str
    b_copy: QPushButton
    b_ok: QPushButton

    def __init__(self, header: str, msg: str, parent=None):
        super().__init__(parent)
        self.header = header
        self.msg = msg
        msg_field = QTextEdit()
        msg_field.setReadOnly(True)
        msg_field.setPlainText(msg)

        self.b_copy = QPushButton(_("Copy"))
        self.b_ok = QPushButton(_("ok"))

        self.b_ok.clicked.connect(self.close)
        self.b_copy.clicked.connect(self.copy)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel(header), 0, 0, 1, 2)
        layout.addWidget(msg_field, 1, 0, 1, 2)
        layout.addWidget(self.b_copy, 2, 0, 1, 1)
        layout.addWidget(self.b_ok, 2, 1, 1, 1)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)

        self.resize(800, 600)
        self.setWindowTitle(_("Plot data"))

    def copy(self):
        QApplication.clipboard().setText(self.msg)
        logger.debug(f"InfoBox({self.header})'s content copied to the clipboard")
        self.b_copy.setText(_("Copied !"))
        QTimer.singleShot(MSG_DURATION, lambda: self.b_copy.setText(_("Copy")))
