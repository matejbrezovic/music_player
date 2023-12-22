import json
from typing import List

import mutagen.mp3
from PyQt6 import QtWidgets

from constants import ROOT
from data_models.track import Track
from utils import TagManager

DEFAULT_LOADED_TRACKS_FILE_PATH = f"{ROOT}/tracks.txt"


class JsonTracksRepository:
    def get_tracks(self) -> List[Track]:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "r") as f:
            try:
                loaded_json = json.loads(f.read())
                tracks = [self._decode_track(t) for t in loaded_json]
                if QtWidgets.QApplication.instance() is not None:
                    for track in tracks:
                        track.artwork_pixmap = get_embedded_artwork_pixmap(track.file_path)

                tracks = tracks * 100
                # for i, track in enumerate(tracks):
                #     track.track_id = i
                #     tracks[i] = track
                return tracks
            except json.decoder.JSONDecodeError:
                return []

    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        for track in self.get_tracks():
            if track.track_id == track_id:
                return track
        return None

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
                    5 # placeholder for rating
                ))
            except (mutagen.mp3.HeaderNotFoundError, NotImplementedError, ValueError):
                # TODO cannot convert '2020-10-26T20:39:57-04:00' to int type for year so ValueError (can be improved)
                continue

        return tracks