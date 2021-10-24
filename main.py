import sys

from PySide6 import QtWidgets

from constants import *


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._setup_ui()

        self.setWindowTitle('music player v0.0.1')
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

    def _setup_ui(self):
        ...


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowUi()
    mainWindow.show()

    sys.exit(app.exec())
