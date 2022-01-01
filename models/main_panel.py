from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QVBoxLayout

from constants import *
from data_models.track import Track
from models.track_view_widget import TrackViewWidget
from repositories.tracks_repository import TracksRepository
from tag_manager import TagManager


class MainPanel(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("MainPanel {background-color: rgba(255, 255, 0, 0.3)}")
        self.setMinimumWidth(MAIN_PANEL_MIN_WIDTH)
        self.tag_manager = TagManager()

        self.track_view_widget = TrackViewWidget()

        self.view_options = {
            0: "Tracks",
            1: "Album and Tracks",
            2: "Album Covers",
            3: "Artists",
        }

        self.view_options_combo_box = QComboBox()
        self.view_options_combo_box.setFixedWidth(150)
        self.view_options_combo_box.currentIndexChanged.connect(self.view_key_changed)
        self.view_options_combo_box.addItems(self.view_options.values())

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.view_options_combo_box)
        self.main_layout.addWidget(self.track_view_widget)

        self.display_tracks(TracksRepository().get_tracks())

    def view_key_changed(self):
        ...

    def display_tracks(self, tracks: List[Track]):
        self.track_view_widget.set_tracks(tracks)
