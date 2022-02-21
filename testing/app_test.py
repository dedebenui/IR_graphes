from PyQt5 import QtWidgets
import sys
import string
import random

from emsapp.config import Config
from emsapp.i18n import _


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout()
        mw = QtWidgets.QWidget(self)
        self.setCentralWidget(mw)
        mw.setLayout(layout)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(_("&File"))
        test_action = file_menu.addAction(_("&Open..."))
        test_action.setShortcut("Ctrl+O")
        test_action.setStatusTip(_("Open a database"))
        test_action.triggered.connect(self.ask_random)

        self.button = QtWidgets.QPushButton("Test")
        self.button.clicked.connect(test_action.trigger)

        layout.addWidget(self.button)

    def ask_random(self):
        key = "".join(random.choice(string.ascii_letters) for _ in range(2))
        print(Config().user_data.get(key, validate_test))


def validate_test(s: str) -> str:
    """a valid random string must have a a or a b in it"""
    if not (set(s.lower()) & {"a", "b"}):
        raise ValueError("entered value does not contain a or b")
    return s.upper()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
