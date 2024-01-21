import copy
from random import choice
from typing import List, Optional

from PyQt6.QtCore import pyqtSignal, QObject

from data_models import Track
from gui.audio import AudioRepeatMode
from utils import TrackNotInQueueError, QtSingleton


class AudioQueue(QObject, metaclass=QtSingleton):
    queue_updated = pyqtSignal(list)
    playing_track_updated = pyqtSignal(Track)

    def __init__(self):
        super().__init__()
        self.is_shuffled = False
        self.queue_ended = False
        self.repeat_mode = AudioRepeatMode.RepeatOff

        self._playing_track: Optional[Track] = None
        self._index_in_played_tracks: int = 0
        self.played_tracks: List[Track] = []
        self.tracks_to_play: List[Track] = []

        # tracks added to queue manually by user
        self._user_queued_next_tracks: List[Track] = []
        self._user_queued_last_tracks: List[Track] = []
        self._next_enqueued_tracks_end_index = 0
        self._last_enqueued_tracks_start_index = 0
        self._track_before_queue: Optional[Track] = None

        # used for differentiating duplicate tracks in queue
        self._queue_id_counter = 100  # arbitrary number bigger than 0, because 0 is default

    @property
    def playing_track(self) -> Track:
        return self._playing_track

    @playing_track.setter
    def playing_track(self, value: Track) -> None:
        self._playing_track = value
        self.playing_track_updated.emit(copy.deepcopy(self._playing_track))

    def __bool__(self):
        return (bool(self.played_tracks) or
                bool(self.tracks_to_play))

    def __len__(self):
        return len(self.played_tracks) + len(self.tracks_to_play)

    def get_queue(self) -> list[Track]:
        return [*self.played_tracks, *self.tracks_to_play]

    def has_valid_tracks(self) -> bool:
        return ((self.playing_track.is_valid() if self.playing_track else False) or
                any(track.is_valid() for track in self.played_tracks) or
                any(track.is_valid() for track in self.tracks_to_play))

    def set_queue(self, tracks: List[Track]) -> None:
        self._queue_id_counter = 100

        self.played_tracks = []
        self._playing_track = None
        self.tracks_to_play = tracks.copy()
        self.queue_ended = False
        self._user_queued_next_tracks = []
        self._user_queued_last_tracks = []
        self.queue_updated.emit(self.get_queue())

    def enqueue_next(self, tracks: List[Track]) -> None:
        tracks = copy.deepcopy(tracks)
        for track in tracks:
            track.queue_id = self._queue_id_counter
            self._queue_id_counter += 1

        self.tracks_to_play[self._next_enqueued_tracks_end_index:self._next_enqueued_tracks_end_index] = tracks

        self._next_enqueued_tracks_end_index += len(tracks)

        self._user_queued_next_tracks.extend(tracks)
        self.queue_ended = False
        self.queue_updated.emit(self.get_queue())

    def enqueue_last(self, tracks: List[Track]) -> None:
        for track in tracks:
            track.queue_id = self._queue_id_counter
            self._queue_id_counter += 1

        self.tracks_to_play.extend(tracks)
        self._user_queued_last_tracks.extend(tracks)
        self.queue_ended = False
        self.queue_updated.emit(self.get_queue())
        self._last_enqueued_tracks_start_index = len(self.tracks_to_play) - len(self._user_queued_last_tracks) - 1

    def index(self, track: Track) -> int:
        return self.get_queue().index(track)

    def change_audio_order(self) -> None:
        self.is_shuffled = not self.is_shuffled
        if self.is_shuffled:
            self.tracks_to_play = [*self.played_tracks.copy(), *self.tracks_to_play.copy()]
            if self.playing_track:
                self.tracks_to_play.remove(self.playing_track)

        self.played_tracks = [self.playing_track] if self.playing_track else []
        self._index_in_played_tracks = 0
        self.queue_ended = False

    def set_next(self) -> None:
        if (len(self.tracks_to_play) == 0 and self.repeat_mode == AudioRepeatMode.RepeatOff and
                self._playing_track in self.played_tracks and
                self.played_tracks.index(self._playing_track) == len(self.played_tracks) - 1):
            self.queue_ended = True
            return

        if len(self.tracks_to_play) == 0 and self.repeat_mode != AudioRepeatMode.RepeatOff:
            self._index_in_played_tracks = 0
            self.tracks_to_play = self.played_tracks.copy()

            for track in self.tracks_to_play:
                track.queue_id = self._queue_id_counter
                self._queue_id_counter += 1

            self.update_currently_playing(self.tracks_to_play[0])
            return

        if self._user_queued_next_tracks:
            new_playing_track = self.tracks_to_play.pop(0)
            self._user_queued_next_tracks.pop(0)
            self._next_enqueued_tracks_end_index -= 1
            self._last_enqueued_tracks_start_index -= 1
            self.update_currently_playing(new_playing_track)
            return

        if (self.playing_track in self.played_tracks and
                self.played_tracks.index(self.playing_track) != len(self.played_tracks) - 1 and
                len(self.played_tracks) > 1):
            self.update_currently_playing(self.played_tracks[self.played_tracks.index(self.playing_track) + 1])
            return

        if len(self.tracks_to_play) == len(self._user_queued_last_tracks):
            new_playing_track = self._user_queued_last_tracks.pop(0)
            self.tracks_to_play.pop(0)
            self._last_enqueued_tracks_start_index -= 1
            self.update_currently_playing(new_playing_track)
            return

        self.queue_ended = False

        if self.is_shuffled:
            if not self._last_enqueued_tracks_start_index:
                new_playing_track = choice(self.tracks_to_play)
            else:
                new_playing_track = choice(self.tracks_to_play[:self._last_enqueued_tracks_start_index])
            self.tracks_to_play.remove(new_playing_track)
        else:
            new_playing_track = self.tracks_to_play.pop(0)

        self.update_currently_playing(new_playing_track)

    def set_prev(self) -> None:
        queue = self.get_queue()
        if (self.playing_track in self.played_tracks and self.played_tracks.index(self.playing_track) == 0
                or not self.played_tracks and self.is_shuffled):
            self.queue_ended = True
            return

        self.queue_ended = False

        if self.is_shuffled:
            new_playing_track = self.played_tracks[self.played_tracks.index(self.playing_track) - 1]
        elif queue.index(self.playing_track) == 0:
            self.queue_ended = True
            new_playing_track = self.playing_track
        else:
            new_playing_track = self.played_tracks[self.played_tracks.index(self.playing_track) - 1]

        self.update_currently_playing(new_playing_track)

    def update_currently_playing(self, new_playing_track: Track) -> None:
        ind = self.played_tracks.index(self.playing_track) + 1 if (
                self.playing_track in self.played_tracks) else len(self.played_tracks)
        if new_playing_track not in self.played_tracks:
            self.played_tracks.insert(ind, new_playing_track)
        self.playing_track = new_playing_track

        if not self._user_queued_next_tracks:
            self._track_before_queue = self.playing_track

    def set_playing_track(self, track: Track) -> None:
        if track not in self.get_queue():
            raise TrackNotInQueueError

        if track in self.tracks_to_play:
            ind = self.tracks_to_play.index(track) - len(self.played_tracks)

            if not self.is_shuffled:
                self.played_tracks.extend(self.tracks_to_play[:ind])
                self.tracks_to_play = self.tracks_to_play[ind + 1:]
            else:
                self.tracks_to_play.pop(ind)
        self.update_currently_playing(track)

    def update_track_rating(self, track: Track, rating: float) -> None:
        if self.playing_track and track.file_path == self.playing_track.file_path:
            self.playing_track.rating = rating

        for t in self.get_queue():
            if t.file_path == track.file_path:
                t.rating = rating
