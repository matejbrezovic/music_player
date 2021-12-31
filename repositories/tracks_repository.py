from json import JSONDecoder
from typing import List

from constants import *
import json

from data_models.track import Track


class TracksRepository:
    def __init__(self):
        ...

    def get_tracks(self) -> List[Track]:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "r") as f:
            try:
                return [self.decode_track(t) for t in json.load(f)]
            except json.decoder.JSONDecodeError:
                return []

    def save_tracks(self, tracks: List[Track]) -> None:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "w") as f:
            json.dump([self.encode_track(t) for t in tracks], f)

    def encode_track(self, track: Track):
        return track.__dict__

    def decode_track(self, encoded_track):
        def from_json(json_object):
            return Track(*json_object.values())
        return JSONDecoder().decode(str(encoded_track))

        