from emsapp.widgets.main_window import MainWindow
from PyQt5 import QtWidgets
from emsapp.config import Config
import sys


def main():
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