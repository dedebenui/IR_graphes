import os
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
import sys



class FileSelector(QtWidgets.QWidget):
    file_path: Path
    sig_path_changed = QtCore.pyqtSignal(Path)

    def __init__(self, parent=None, default_path: os.PathLike = None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.file_path = default_path or Path.cwd()
        self.file_path_label = QtWidgets.QLabel(str(self.file_path))
        self.choose_path_button = QtWidgets.QPushButton("select_path")
        self.choose_path_button.clicked.connect(self.choose_path)

        layout.addWidget(self.file_path_label)
        layout.addWidget(self.choose_path_button)

    def choose_path(self) -> Path:
        out = QtWidgets.QFileDialog.getOpenFileName()[0]
        if out:
            self.file_path = Path(out)
            self.file_path_label.setText(str(self.file_path))
            self.sig_path_changed.emit(self.file_path)


class FileSelectorDialog(QtWidgets.QDialog):
    def __init__(self, default_path: os.PathLike = None):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.selector = FileSelector(default_path=default_path)

        ok_button = QtWidgets.QPushButton("ok")
        ok_button.clicked.connect(self.close)

        layout.addWidget(self.selector)
        layout.addWidget(ok_button)

        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, False)

    def showEvent(self, a0: QtGui.QShowEvent):
        super().showEvent(a0)
        self.selector.choose_path()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        open_action = file_menu.addAction("&Open...")
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a database")
        open_action.triggered.connect(self.open_dialog)

        self.button = QtWidgets.QPushButton(open_action.text())
        self.button.clicked.connect(open_action.trigger)

        self.setCentralWidget(self.button)

    def open_dialog(self):
        d = FileSelectorDialog()
        d.exec_()
        print(d.selector.file_path)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
