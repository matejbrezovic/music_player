from random import shuffle
from typing import List


class AudioPlaylist:
    def __init__(self):
        self.playlist = []
        self.ordered_playlist = []
        self.playlist_index = 0
        self.already_played = []
        self.mode = 1  # 1 ordered, 2 shuffle, 3 repeat one

    def set_playlist(self, playlist: List[str]):
        self.playlist = playlist.copy()
        self.ordered_playlist = playlist.copy()
        self.playlist_index = 0

    def set_playlist_index(self, playlist_index: int):
        self.playlist_index = playlist_index

    def set_mode(self, mode: int):
        self.mode = mode
        if mode == 1:
            self.playlist = self.ordered_playlist.copy()
        elif mode == 2:
            shuffle(self.playlist)
            while self.playlist[self.playlist_index + 1] == self.ordered_playlist[self.playlist_index]:
                shuffle(self.playlist)
        elif mode == 3:
            self.playlist = [self.playlist[self.playlist_index]]
        else:
            raise Exception(f"Incorrect playlist mode: {mode}")

    def change_mode(self):
        self.set_mode(self.mode + 1 if self.mode <= 2 else 1)

    def set_next(self):
        self.playlist_index = self.playlist_index + 1 if len(self.playlist) - 1 > self.playlist_index else 0
        # return self.playlist[self.playlist_index]

    def set_prev(self):
        self.playlist_index = self.playlist_index - 1 if self.playlist_index > 0 else len(self.playlist) - 1
        # return self.playlist[self.playlist_index]

    def get_current(self):
        return self.playlist[self.playlist_index]
