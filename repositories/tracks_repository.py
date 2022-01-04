import json
from typing import List

from constants import *
from data_models.track import Track
from tag_manager import TagManager


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

    @staticmethod
    def convert_file_paths_to_tracks(file_paths: List[str]) -> List[Track]:
        tracks = []
        tag_manager = TagManager()
        for i, file_path in enumerate(file_paths):
            loaded_file = tag_manager.load_file(file_path)
            tracks.append(Track(
                i,
                file_path,
                file_path.rsplit("/")[-1],
                loaded_file["album"].first,
                loaded_file["artist"].first,
                loaded_file["composer"].first,
                loaded_file["genre"].first,
                loaded_file["year"].first if loaded_file["year"].first else None,
                int(loaded_file["#length"].first),
                ""  # get_artwork_pixmap(file_path, "album")
            ))
        return tracks

        