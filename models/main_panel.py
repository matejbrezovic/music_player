import time
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout

from constants import *
from data_models.track import Track
from models.track_view_widget import TrackViewWidget
from tag_manager import TagManager
from utils import TransparentComboBox


class MainPanel(QtWidgets.QFrame):
    track_clicked = pyqtSignal(Track, int)
    track_double_clicked = pyqtSignal(Track, int)
    play_now_triggered = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks = []
        self.setStyleSheet("MainPanel {background-color: rgba(0, 0, 0, 0.3)}")
        self.setMinimumWidth(MAIN_PANEL_MIN_WIDTH)
        self.tag_manager = TagManager()
        self.track_view_widget = TrackViewWidget(self)
        self.track_view_widget.track_clicked.connect(self.track_clicked.emit)
        self.track_view_widget.track_double_clicked.connect(self.track_double_clicked.emit)
        self.track_view_widget.play_now_triggered.connect(self.play_now_triggered.emit)

        self.view_options = {
            0: "Tracks",
            1: "Album and Tracks",
            2: "Album Covers",
            3: "Artists",
        }

        self.view_options_combo_box = TransparentComboBox(self)
        self.view_options_combo_box.setFixedSize(150, 24)
        self.view_options_combo_box.currentIndexChanged.connect(self.view_key_changed)
        self.view_options_combo_box.addItems(self.view_options.values())

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.view_options_combo_box)
        self.main_layout.addWidget(self.track_view_widget)

    def view_key_changed(self) -> None:
        ...

    def display_tracks(self, tracks: List[Track]) -> None:
        # global_timer.print_elapsed_time()
        start = time.time()
        if self.displayed_tracks == tracks:
            return
        self.track_view_widget.set_tracks(tracks)
        self.displayed_tracks = tracks
        print("Tracks displayed in:", time.time() - start)

    def select_track(self, track: Track) -> None:
        self.track_view_widget.select_row_by_track(track)

    def set_playing_track(self, track: Track) -> None:
        # print("SET")
        self.track_view_widget.set_playing_track(track)

    def pause_playing_track(self) -> None:
        self.track_view_widget.pause_playing_track()

    def unpause_playing_track(self) -> None:
        self.track_view_widget.unpause_playing_track()
