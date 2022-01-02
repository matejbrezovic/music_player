from random import shuffle
from typing import List, Union

from data_models.track import Track


class AudioPlaylist:
    def __init__(self):
        self.playlist = []
        self.ordered_playlist = []
        self.playlist_index = 0
        self.already_played = []
        self.mode = 1  # 1 ordered, 2 shuffle, 3 repeat one
        self.currently_playing = ""

    def set_playlist(self, playlist: List[Track]):
        self.playlist = playlist.copy()
        self.ordered_playlist = playlist.copy()
        self.currently_playing = self.ordered_playlist[0]
        self.playlist_index = 0

    def set_playlist_index(self, playlist_index: int):
        self.currently_playing = self.ordered_playlist[playlist_index]
        self.playlist_index = playlist_index

    def index(self, track: Track):
        return self.ordered_playlist.index(track)

    def set_mode(self, mode: int):
        self.mode = mode
        if mode == 1:
            self.playlist_index = self.ordered_playlist.index(self.currently_playing)
            self.playlist = self.ordered_playlist.copy()
        elif mode == 2:
            shuffle(self.playlist)
            while self.playlist[self.playlist_index + 1] == self.ordered_playlist[self.playlist_index]:
                shuffle(self.playlist)
        elif mode == 3:
            pass  # self.playlist = [self.playlist[self.playlist_index]] * len(self.playlist)
        else:
            raise Exception(f"Incorrect playlist mode: {mode}")

    def change_mode(self):
        self.set_mode(self.mode + 1 if self.mode <= 2 else 1)

    def set_next(self):
        self.playlist_index = self.playlist_index if self.mode == 3 else \
            self.playlist_index + 1 if len(self.playlist) - 1 > self.playlist_index else 0
        self.update_currently_playing()

    def set_prev(self):
        self.playlist_index = self.playlist_index if self.mode == 3 else \
            self.playlist_index - 1 if self.playlist_index > 0 else len(self.playlist) - 1
        self.update_currently_playing()

    def update_currently_playing(self):
        self.currently_playing = self.playlist[self.playlist_index]


