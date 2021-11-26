import sys

from PySide6 import *
from PySide6 import QtWidgets
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from constants import *


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._setup_ui()

        self.setWindowTitle('music player v0.0.1')
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget_layout)
        self.setCentralWidget(self.central_widget)

        self._setup_panels()

    def _setup_panels(self):
        self.navigation_panel = QFrame()
        self.navigation_panel.setStyleSheet("background-color: red")
        self.main_panel = QFrame()
        self.information_panel = QFrame()
        self.audio_controller = QFrame()

        self.horizontal_splitter = QSplitter(Qt.Horizontal)
        self.vertical_splitter = QSplitter(Qt.Vertical)

        self.horizontal_splitter.addWidget(self.navigation_panel)
        self.horizontal_splitter.addWidget(self.main_panel)
        self.horizontal_splitter.addWidget(self.information_panel)
        # self.vertical_splitter.addWidget(self.horizontal_splitter)
        # self.vertical_splitter.addWidget(self.audio_controller)

        self.central_widget_layout.addWidget(self.horizontal_splitter)
        self.central_widget_layout.addWidget(self.audio_controller)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowUi()
    mainWindow.show()

    sys.exit(app.exec())
