from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from constants import *
from PyQt6.QtWidgets import *


class InformationPanel(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("information_panel")
        self.setStyleSheet("QFrame#information_panel {background-color: rgba(255, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

        self.main_layout = QVBoxLayout(self)

        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.playing_tracks_widget = QFrame()
        self.track_info_widget = QFrame()


        self.vertical_splitter.addWidget(self.track_info_widget)
        self.vertical_splitter.addWidget(self.playing_tracks_widget)
        self.main_layout.addWidget(self.vertical_splitter)
