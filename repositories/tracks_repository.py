import json
from typing import List

from constants import *
from data_models.track import Track


class TracksRepository:
    def __init__(self):
        ...

    def get_tracks(self) -> List[Track]:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "r") as f:
            try:
                loaded_json = json.loads(f.read())
                return [self._decode_track(t) for t in loaded_json]

            except json.decoder.JSONDecodeError:
                return []

    def save_tracks(self, tracks: List[Track]) -> None:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "w") as f:
            json.dump([self._encode_track(t) for t in tracks], f)

    @staticmethod
    def _encode_track(track: Track):
        return track.__dict__

    @staticmethod
    def _decode_track(encoded_track: dict):
        return Track(*encoded_track.values())

        