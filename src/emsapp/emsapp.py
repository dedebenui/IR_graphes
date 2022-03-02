import pkg_resources
from PyQt5 import QtWidgets, QtGui
import sys


def main():
    app = QtWidgets.QApplication(sys.argv)
    pixmap = QtGui.QPixmap(
        pkg_resources.resource_filename("emsapp", "package_data/covid19.jpg")
    )
    splash = QtWidgets.QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    from emsapp import startup
    from emsapp.widgets import exception_hook
    from emsapp.widgets.main_window import MainWindow
    from emsapp.i18n import _

    splash.showMessage(_("Loading data..."))

    win = MainWindow()
    win.sig_loading_event.connect(splash.showMessage)
    win.show()
    splash.finish(win)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
