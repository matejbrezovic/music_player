from typing import List, Optional, Tuple

from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtWidgets import QVBoxLayout, QFrame

from constants import *
from data_models.track import Track
from gui.widgets.track_view_widget import TrackViewWidget
from repositories.cached_tracks_repository import CachedTracksRepository
from tag_manager import TagManager


class MainPanel(QFrame):
    track_clicked = pyqtSignal(Track, int)
    track_double_clicked = pyqtSignal(Track, int)
    play_now_triggered = pyqtSignal(list)
    output_to_triggered = pyqtSignal(str)
    queue_next_triggered = pyqtSignal(list)
    queue_last_triggered = pyqtSignal(list)
    tracks_deleted = pyqtSignal(list)

    def __init__(self, *args):
        super().__init__(*args)
        self.displayed_tracks = []
        self.cached_tracks_repository = CachedTracksRepository()
        self.setStyleSheet("MainPanel {background-color: rgba(0, 0, 0, 0.3)}")
        self.setMinimumWidth(MAIN_PANEL_MIN_WIDTH)
        self.tag_manager = TagManager()
        self.track_view_widget = TrackViewWidget(self)
        self.track_view_widget.track_clicked.connect(self.track_clicked.emit)
        self.track_view_widget.track_double_clicked.connect(self.track_double_clicked.emit)
        self.track_view_widget.play_now_triggered.connect(self.play_now_triggered.emit)
        self.track_view_widget.queue_next_triggered.connect(self.queue_next_triggered.emit)
        self.track_view_widget.queue_last_triggered.connect(self.queue_last_triggered.emit)
        self.track_view_widget.output_to_triggered.connect(self.output_to_triggered.emit)
        self.track_view_widget.tracks_deleted.connect(self.tracks_deleted.emit)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.track_view_widget)

        self._display_key = None
        self._display_value = None

    def view_key_changed(self) -> None:
        ...

    @pyqtSlot(list)
    def display_tracks(self, tracks: List[Track],
                       key_value_tuple: Tuple[Optional[str], Optional[str]] = (None, None)) -> None:
        if (self._display_key, self._display_value) == key_value_tuple:
            return
        self._display_key, self._display_value = key_value_tuple
        self.track_view_widget.set_tracks(tracks)
        self.displayed_tracks = tracks

    @pyqtSlot(Track)
    def set_playing_track(self, track: Track) -> None:
        self.track_view_widget.set_playing_track(track)

    @pyqtSlot()
    def pause_playing_track(self) -> None:
        self.track_view_widget.pause_playing_track()

    @pyqtSlot()
    def unpause_playing_track(self) -> None:
        self.track_view_widget.unpause_playing_track()

    @pyqtSlot(list)
    def added_tracks(self, tracks: List[Track]) -> None:
        self.track_view_widget.added_tracks(tracks)

    @pyqtSlot()
    def stop_playing(self) -> None:
        self.track_view_widget.stop_playing()

    # def tracks_deleted(self, deleted_tracks: List[Track]) -> None:
    #     self.cached_tracks_repository.drop_tracks(deleted_tracks)
        # self.cached_tracks_repository.cached_counts[(self._display_key, self._display_value)] -= len(deleted_tracks)