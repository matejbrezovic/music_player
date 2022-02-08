import json
from typing import List

import mutagen.mp3

from constants import *
from utils import *
from data_models.track import Track
from tag_manager import TagManager


class TracksRepository:
    def __init__(self):
        ...

    def get_tracks(self) -> List[Track]:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "r") as f:
            try:
                loaded_json = json.loads(f.read())
                tracks = [self._decode_track(t) for t in loaded_json]
                for track in tracks:
                    track.artwork_pixmap = get_artwork_pixmap(track.file_path)
                return tracks * 100
            except json.decoder.JSONDecodeError:
                return []

    def save_tracks(self, tracks: List[Track]) -> None:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "w") as f:
            json.dump([self._encode_track(t) for t in tracks], f)

    @staticmethod
    def _encode_track(track: Track) -> dict:
        return track.__dict__

    @staticmethod
    def _decode_track(encoded_track: dict) -> Track:
        return Track(*encoded_track.values())

    @staticmethod
    def convert_file_paths_to_tracks(file_paths: List[str]) -> List[Track]:
        tracks = []
        tag_manager = TagManager()
        for i, file_path in enumerate(file_paths):
            try:
                loaded_file = tag_manager.load_file(file_path)
                tracks.append(Track(
                    i,
                    file_path,
                    file_path.rsplit("/")[-1],
                    loaded_file["album"].first,
                    loaded_file["artist"].first,
                    loaded_file["composer"].first,
                    loaded_file["genre"].first,
                    int(loaded_file["year"]) if int(loaded_file["year"]) else None,
                    int(loaded_file["#length"].first),
                    ""  # get_artwork_pixmap(file_path, "album")
                ))
            except (mutagen.mp3.HeaderNotFoundError, NotImplementedError, ValueError):
                # TODO cannot convert '2020-10-26T20:39:57-04:00' to int type for year so ValueError (can be improved)
                continue

        return tracks

        