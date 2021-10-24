import sys

from PySide6 import QtWidgets
from PySide6.QtWidgets import QHBoxLayout

from constants import *


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._setup_ui()

        self.setWindowTitle("music player test")
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

    def _setup_ui(self):
        self.central_widget = QtWidgets.QWidget()
        self.central_widget_layout = QHBoxLayout()

        self.play_button = QtWidgets.QPushButton("Play")
        self.next_button = QtWidgets.QPushButton("Next")
        self.prev_button = QtWidgets.QPushButton("Previous")

        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowUi()
    mainWindow.show()

    sys.exit(app.exec())
