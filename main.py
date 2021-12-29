import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import *

from audio_controller import AudioController
from constants import *
from information_panel import InformationPanel
from main_panel import MainPanel
from navigation_panel import NavigationPanel
from dialogs import *


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._setup_ui()

        self.setWindowTitle('music player v0.0.3')
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setMinimumSize(MAIN_PANEL_MIN_WIDTH + 2 * PANEL_MIN_WIDTH + 550, 600)

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget_layout)
        self.setCentralWidget(self.central_widget)

        self._setup_menu_bar()
        self._setup_panels()

    # noinspection PyTypeChecker
    def _setup_menu_bar(self):
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu("&File", self)
        add_files_action = QAction("&Add Files to Library", self)
        scan_folders_action = QAction("&Scan Folders for New Files", self)
        scan_folders_action.triggered.connect(lambda: ScanFoldersDialog().exec())
        file_menu.addAction(add_files_action)
        file_menu.addAction(scan_folders_action)

        self.menu_bar.addMenu(file_menu)

    def _setup_panels(self):
        self.navigation_panel = NavigationPanel()
        self.main_panel = MainPanel()
        self.information_panel = InformationPanel()
        self.audio_controller = AudioController()

        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.horizontal_splitter.addWidget(self.navigation_panel)
        self.horizontal_splitter.addWidget(self.main_panel)
        self.horizontal_splitter.addWidget(self.information_panel)
        self.horizontal_splitter.setSizes([int(PANEL_MIN_WIDTH * 1.5), MAIN_PANEL_MIN_WIDTH * 2,
                                           int(PANEL_MIN_WIDTH * 1.5)])

        self.central_widget_layout.addWidget(self.horizontal_splitter)
        self.central_widget_layout.addWidget(self.audio_controller)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowUi()
    # mainWindow.show()
    SelectFoldersDialog().exec()

    sys.exit(app.exec())
