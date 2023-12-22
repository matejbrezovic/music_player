from random import choice
from typing import List, Optional

from PyQt6.QtCore import pyqtSignal, QObject

from data_models.track import Track
from gui.audio.enums import *
from utils import TrackNotInPlaylistError


class AudioPlaylist(QObject):
    playlist_updated = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._playing_track_index = 0
        self._is_shuffled = False
        self._repeat_mode = RepeatMode.RepeatOff
        self.playlist_ended = False

        self.playlist: List[Track] = []
        self.playing_track: Optional[Track] = None

        self.played_tracks: List[Track] = []
        self._index_in_played_tracks: int = 0

        # tracks added to queue manually by user
        self.user_queued_next_tracks: List[Track] = []
        self.user_queued_last_tracks: List[Track] = []

    def __bool__(self):
        return (bool(self.played_tracks) or
                bool(self.playlist) or
                bool(self.playing_track))

    def __len__(self):
        return len(self.played_tracks) + len(self.playlist) + bool(self.playing_track)

    def has_valid_tracks(self) -> bool:
        return ((self.playing_track.is_valid() if self.playing_track else False) or
                any(track.is_valid() for track in self.played_tracks) or
                any(track.is_valid() for track in self.playlist))

    def set_playlist(self, playlist: List[Track]) -> None:
        self.played_tracks = []
        self.playlist = playlist.copy()
        self.playlist_ended = False
        self.user_queued_next_tracks = []
        self.user_queued_last_tracks = []

    def queue_next(self, tracks: List[Track]) -> None:
        self.user_queued_next_tracks.extend(tracks)
        self.playlist_ended = False

    def queue_last(self, tracks: List[Track]) -> None:
        self.user_queued_last_tracks.extend(tracks)
        self.playlist_ended = False

    def set_playlist_index(self, playlist_index: int) -> None:
        self._playing_track_index = playlist_index
        self.update_currently_playing(self.playlist[self._playing_track_index] if self.playlist else None)

    def index(self, track: Track) -> int:
        return self.playlist.index(track)

    def change_audio_order(self) -> None:
        self._is_shuffled = not self._is_shuffled
        self.played_tracks = []
        self._index_in_played_tracks = 0
        self.playlist_ended = False

    def set_repeat_on(self) -> None:
        self._repeat_mode = RepeatMode.RepeatOn

    def set_repeat_off(self) -> None:
        self._repeat_mode = RepeatMode.RepeatOff

    def set_repeat_one(self) -> None:
        self._repeat_mode = RepeatMode.RepeatOne

    def set_next(self) -> None:
        if ((len(self.played_tracks) == len(self.playlist) and self._repeat_mode == RepeatMode.RepeatOff or
                self._playing_track_index == len(self.playlist) - 1) and
                not self.user_queued_next_tracks and not self.user_queued_last_tracks):
            self.playlist_ended = True
            return

        if self.user_queued_next_tracks:
            new_playing_track = self.user_queued_next_tracks.pop(0)
            self.update_currently_playing(new_playing_track)
            return

        if self._index_in_played_tracks <= -1:
            self._index_in_played_tracks += 1
            if self._index_in_played_tracks < 0:
                self.update_currently_playing(self.played_tracks[self._index_in_played_tracks])
                return

        self.playlist_ended = False
        tracks_left_to_play = list(set(self.playlist).symmetric_difference(set(self.played_tracks)))
        if not tracks_left_to_play and not self.user_queued_next_tracks and not self.user_queued_last_tracks:
            self._index_in_played_tracks = 0
            self.update_currently_playing(self.played_tracks[self._index_in_played_tracks])
            return

        if self._is_shuffled:
            new_playing_track = choice(tracks_left_to_play)
        elif tracks_left_to_play:
            if self._repeat_mode == RepeatMode.RepeatOn or self._repeat_mode == RepeatMode.RepeatOne:
                self.playlist_ended = False
                if len(self.playlist) - 1 > self._playing_track_index:
                    self._playing_track_index += 1
                else:
                    self._playing_track_index = 0
            new_playing_track = self.playlist[self._playing_track_index + 1]
            self._playing_track_index = self.playlist.index(new_playing_track)
        else:
            new_playing_track = self.user_queued_last_tracks.pop(0)

        self.update_currently_playing(new_playing_track)

    def set_prev(self) -> None:
        if (self._index_in_played_tracks == -len(self.played_tracks) and self._index_in_played_tracks != 0 or
                not self.played_tracks and (self._is_shuffled or self._playing_track_index == 0)):
            self.playlist_ended = True
            return

        self.playlist_ended = False

        if self._is_shuffled:
            self._index_in_played_tracks -= 1
            new_playing_track = self.played_tracks[self._index_in_played_tracks]
        else:
            if self._playing_track_index == 0:
                self.playlist_ended = True
                new_playing_track = self.playing_track
            else:
                self._playing_track_index -= 1
                self._index_in_played_tracks -= 1
                new_playing_track = self.playlist[self._playing_track_index]

        self.update_currently_playing(new_playing_track, prev=True)

    def update_currently_playing(self, new_playing_track: Track, prev: bool = False) -> None:
        if self.playing_track != new_playing_track:
            if self.playing_track is not None:
                if self._index_in_played_tracks != 0:
                    self.played_tracks.insert(self._index_in_played_tracks, new_playing_track)
                    if not prev:
                        self._index_in_played_tracks += 1
                else:
                    self.played_tracks.append(self.playing_track)
            self._playing_track_index = self.playlist.index(new_playing_track)
            self.playing_track = new_playing_track

        print(self.played_tracks)

    def set_playing_track(self, track: Track) -> None:
        if track not in self.playlist:
            raise TrackNotInPlaylistError

        self.playing_track = track
        self.set_playlist_index(self.playlist.index(self.playing_track))

    def has_ended(self) -> bool:
        return self.playlist_ended

    def is_shuffled(self) -> bool:
        return self._is_shuffled
