from random import shuffle
from typing import List, Optional

from PyQt6.QtCore import pyqtSignal, QObject

from data_models.track import Track
from gui.audio.enums import *


class AudioPlaylist(QObject):
    updated_playlist = pyqtSignal(list)
    last_track_playing = pyqtSignal()
    first_track_playing = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist = []
        self.ordered_playlist = []
        self.playing_track_index = 0
        self.already_played = []
        self._is_shuffled = False
        self._repeat_mode = RepeatMode.RepeatOff
        self._playlist_ended = False
        self.playing_track: Optional[Track] = None

    def __bool__(self):
        return bool(self.playlist)

    def __len__(self):
        return len(self.playlist)

    def has_valid_tracks(self) -> bool:
        return any(track.is_valid() for track in self.playlist)

    def set_playlist(self, playlist: List[Track]) -> None:
        if playlist != self.playlist:
            self.playlist = playlist.copy()
            self.ordered_playlist = playlist.copy()
        self.playing_track = self.ordered_playlist[0] if self.ordered_playlist else None
        self.playing_track_index = 0
        self._playlist_ended = False

    def set_playlist_index(self, playlist_index: int) -> None:
        self.playing_track = self.playlist[playlist_index]
        self.playing_track_index = playlist_index

    def index(self, track: Track) -> int:
        return self.playlist.index(track)

    def set_shuffled(self) -> None:
        if len(self.playlist) <= 2:
            self.playlist.reverse()
            return

        self.playing_track_index = 0
        shuffle(self.playlist)

        self.playlist.remove(self.playing_track)
        self.playlist.insert(0, self.playing_track)

    def set_ordered(self) -> None:
        if self.playing_track:
            self.playing_track_index = self.ordered_playlist.index(self.playing_track)
        self.playlist = self.ordered_playlist.copy()

    def change_audio_order(self) -> None:
        self._is_shuffled = not self._is_shuffled
        if self._is_shuffled:
            self.set_shuffled()
        else:
            self.set_ordered()

    def set_repeat_on(self) -> None:
        self._repeat_mode = RepeatMode.RepeatOn

    def set_repeat_off(self) -> None:
        self._repeat_mode = RepeatMode.RepeatOff

    def set_repeat_one(self) -> None:
        self._repeat_mode = RepeatMode.RepeatOne

    def set_next(self) -> None:
        if self._repeat_mode == RepeatMode.RepeatOff:
            if len(self.playlist) - 1 > self.playing_track_index:
                if self.has_ended():
                    self.playing_track_index = 0
                else:
                    self.playing_track_index += 1
                self._playlist_ended = False
                if self.playing_track_index == len(self.playlist) - 1:
                    self.last_track_playing.emit()
                self.update_currently_playing()
            else:
                self._playlist_ended = True
        elif self._repeat_mode == RepeatMode.RepeatOn:
            self._playlist_ended = False
            if len(self.playlist) - 1 > self.playing_track_index:
                self.playing_track_index += 1
            else:
                self.playing_track_index = 0
            self.update_currently_playing()
        elif self._repeat_mode == RepeatMode.RepeatOne:
            self._playlist_ended = False
            self.update_currently_playing()

    def set_prev(self) -> None:
        if self._repeat_mode == RepeatMode.RepeatOff:
            if self.playing_track_index > 0:
                if self.has_ended():
                    self.playing_track_index = len(self.playlist) - 1
                else:
                    self.playing_track_index -= 1
                self._playlist_ended = False
                if self.playing_track_index == 0:
                    self.last_track_playing.emit()
                self.update_currently_playing()
            else:
                self._playlist_ended = True
        elif self._repeat_mode == RepeatMode.RepeatOn:
            self._playlist_ended = False
            if self.playing_track_index > 0:
                self.playing_track_index -= 1
            else:
                self.playing_track_index = len(self.playlist) - 1
            self.update_currently_playing()
        elif self._repeat_mode == RepeatMode.RepeatOne:
            self._playlist_ended = False
            self.update_currently_playing()

    def update_currently_playing(self) -> None:
        self.playing_track = self.playlist[self.playing_track_index]

    def has_ended(self) -> bool:
        return self._playlist_ended
