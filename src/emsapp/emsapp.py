import sys

import pkg_resources
from PyQt5 import QtGui, QtWidgets, QtCore


def main():
    app = QtWidgets.QApplication(sys.argv)
    pixmap = QtGui.QPixmap(
        pkg_resources.resource_filename("emsapp", "package_data/covid19.jpg")
    )
    splash = QtWidgets.QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    from emsapp import startup
    from emsapp.i18n import _
    from emsapp.widgets import exception_hook
    from emsapp.widgets.main_window import MainWindow

    splash.showMessage(_("Loading data..."))

    win = MainWindow()
    win.sig_loading_event.connect(splash.showMessage)
    win.show()
    splash.finish(win)
    QtCore.QTimer.singleShot(0, win.load_and_process)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
