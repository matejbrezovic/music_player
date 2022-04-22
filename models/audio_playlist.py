from random import shuffle
from typing import List, Optional

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject

from data_models.track import Track


class AudioPlaylist(QObject):
    updated_playlist = pyqtSignal(list)
    playlist_ended = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist = []
        self.ordered_playlist = []
        self.playing_track_index = 0
        self.already_played = []
        # self.mode = 1  # 1 ordered, 2 shuffle, 3 repeat one
        self._is_shuffled = False
        self._repeat_mode = "repeat_off"
        self.playing_track: Optional[Track] = None

    def __bool__(self):
        return bool(self.playlist)

    def has_valid_tracks(self) -> bool:
        return any(track.is_valid() for track in self.playlist)

    @pyqtSlot(list)
    def queue_next(self, tracks: List[Track]) -> None:
        insert_index = self.playing_track_index + 1
        self.playlist[insert_index:insert_index] = tracks
        self.updated_playlist.emit(self.playlist)

    @pyqtSlot(list)
    def queue_last(self, tracks: List[Track]) -> None:
        self.playlist.extend(tracks)
        self.updated_playlist.emit(self.playlist)

    def set_playlist(self, playlist: List[Track]) -> None:
        if playlist != self.playlist:
            self.playlist = playlist.copy()
            self.ordered_playlist = playlist.copy()
        self.playing_track = self.ordered_playlist[0] if self.ordered_playlist else None
        self.playing_track_index = 0

    def set_playlist_index(self, playlist_index: int) -> None:
        self.playing_track = self.ordered_playlist[playlist_index]
        self.playing_track_index = playlist_index

    def index(self, track: Track) -> int:
        return self.ordered_playlist.index(track)

    def set_shuffled(self) -> None:
        shuffle(self.playlist)
        while self.playlist[self.playing_track_index + 1] == self.ordered_playlist[self.playing_track_index]:
            shuffle(self.playlist)

    def set_ordered(self) -> None:
        self.playing_track_index = self.ordered_playlist.index(self.playing_track)
        self.playlist = self.ordered_playlist.copy()

    def change_mode(self) -> None:
        self._is_shuffled = not self._is_shuffled
        if self._is_shuffled:
            self.set_shuffled()
        else:
            self.set_ordered()

    def set_repeat_on(self) -> None:
        self._repeat_mode = "repeat_on"

    def set_repeat_off(self) -> None:
        self._repeat_mode = "repeat_off"

    def set_repeat_one(self) -> None:
        self._repeat_mode = "repeat_one"

    def set_next(self) -> None:
        if self._repeat_mode == "repeat_off":
            if len(self.playlist) - 1 > self.playing_track_index:
                self.playing_track_index += 1
                self.update_currently_playing()
            else:
                self.playlist_ended.emit()
        elif self._repeat_mode == "repeat_on":
            if len(self.playlist) - 1 > self.playing_track_index:
                self.playing_track_index += 1
            else:
                self.playing_track_index = 0
            self.update_currently_playing()
        elif self._repeat_mode == "repeat_one":
            self.update_currently_playing()

    def set_prev(self) -> None:
        if self._repeat_mode == "repeat_off":
            if self.playing_track_index > 0:
                self.playing_track_index -= 1
                self.update_currently_playing()
            else:
                self.playlist_ended.emit()
        elif self._repeat_mode == "repeat_on":
            if self.playing_track_index > 0:
                self.playing_track_index -= 1
            else:
                self.playing_track_index = len(self.playlist) - 1
            self.update_currently_playing()
        elif self._repeat_mode == "repeat_one":
            self.update_currently_playing()

    def update_currently_playing(self) -> None:
        self.playing_track = self.playlist[self.playing_track_index]
