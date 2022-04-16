from random import shuffle
from typing import List, Optional

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject

from data_models.track import Track


class AudioPlaylist(QObject):
    updated_playlist = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist = []
        self.ordered_playlist = []
        self.playing_track_index = 0
        self.already_played = []
        self.mode = 1  # 1 ordered, 2 shuffle, 3 repeat one
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

    def set_mode(self, mode: int) -> None:
        self.mode = mode
        if mode == 1:
            self.playing_track_index = self.ordered_playlist.index(self.playing_track)
            self.playlist = self.ordered_playlist.copy()
        elif mode == 2:
            shuffle(self.playlist)
            while self.playlist[self.playing_track_index + 1] == self.ordered_playlist[self.playing_track_index]:
                shuffle(self.playlist)
        elif mode == 3:
            pass  # self.playlist = [self.playlist[self.playlist_index]] * len(self.playlist)
        else:
            raise Exception(f"Incorrect playlist mode: {mode}")

    def change_mode(self) -> None:
        self.set_mode(self.mode + 1 if self.mode <= 2 else 1)

    def set_next(self) -> None:
        self.playing_track_index = self.playing_track_index if self.mode == 3 else \
            self.playing_track_index + 1 if len(self.playlist) - 1 > self.playing_track_index else 0
        self.update_currently_playing()

    def set_prev(self) -> None:
        self.playing_track_index = self.playing_track_index if self.mode == 3 else \
            self.playing_track_index - 1 if self.playing_track_index > 0 else len(self.playlist) - 1
        self.update_currently_playing()

    def update_currently_playing(self) -> None:
        self.playing_track = self.playlist[self.playing_track_index]
