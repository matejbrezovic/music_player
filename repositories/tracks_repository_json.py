import json
from collections import defaultdict
from random import randint
from typing import List

import mutagen.mp3
from PyQt6 import QtWidgets

from constants import *
from utils import *
from data_models.track import Track
from tag_manager import TagManager


class TracksRepository:
    # def __init__(self):
    #
    #     self.group_options = {
    #         0: "Album",
    #         1: "Artist",
    #         2: "Composer",
    #         3: "Folder",
    #         4: "Genre",
    #         5: "Year"
    #     }
    #
    # def create_groups(self) -> None:
    #     tracks = self.get_tracks()
    #     for track in tracks:
    #         ALBUM_GROUPS[track.album].append(track)
    #         ARTIST_GROUPS[track.artist].append(track)
    #         COMPOSER_GROUPS[track.composer].append(track)
    #         FOLDER_GROUPS[track.file_path.split("/" if "/" in track.file_path else "\\")[-2]].append(track)
    #         GENRE_GROUPS[track.genre].append(track)

    def get_tracks(self) -> List[Track]:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "r") as f:
            try:
                loaded_json = json.loads(f.read())
                tracks = [self._decode_track(t) for t in loaded_json]
                if QtWidgets.QApplication.instance() is not None:
                    for track in tracks:
                        track.artwork_pixmap = get_artwork_pixmap(track.file_path)

                tracks = tracks * 10000
                # for i, track in enumerate(tracks):
                #     track.track_id = i
                #     tracks[i] = track
                return tracks
            except json.decoder.JSONDecodeError:
                return []

    # def get_groups(self, group_key: str) -> List[List[Track]]:
    #     groups = defaultdict(list)
    #
    # def update_groups(self):
    #

    # def get_track_ids(self) -> List[int]:  # TODO maybe redundant
    #     return [track.track_id for track in self.get_tracks()]

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
                    ""  # get_artwork_pixmap(file_path, "album")
                ))
            except (mutagen.mp3.HeaderNotFoundError, NotImplementedError, ValueError):
                # TODO cannot convert '2020-10-26T20:39:57-04:00' to int type for year so ValueError (can be improved)
                continue

        return tracks

        