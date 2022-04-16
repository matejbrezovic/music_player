import os
import sqlite3
from typing import List, Union, Iterable, Tuple

import mutagen.mp3
from PyQt6 import QtWidgets

from data_models.track import Track
from repositories.base_repository import BaseRepository
from tag_manager import TagManager
from utils import get_artwork_pixmap, Singleton


class TracksRepository(BaseRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

    def add_track(self, track: Track) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (None,
                                                                                    track.file_path,
                                                                                    track.title,
                                                                                    track.album,
                                                                                    track.artist,
                                                                                    track.composer,
                                                                                    track.genre,
                                                                                    track.year,
                                                                                    track.length,
                                                                                    track.rating
                                                                                    ))
        conn.commit()
        conn.close()

    def add_tracks(self, tracks: Iterable[Track]) -> None:
        for track in tracks:
            self.add_track(track)

    def add_new_tracks(self, tracks: Iterable[Track]) -> None:
        existing_tracks = self.get_tracks()
        tracks_to_add = []
        for track in tracks:
            if track not in existing_tracks:
                tracks_to_add.append(track)
        self.add_tracks(tracks_to_add)

    def set_tracks(self, tracks: Iterable[Track]) -> None:
        self.reset_table("tracks")
        self.add_tracks(tracks)

    def get_track_counts_grouped_by(self, group_key: str) -> List[Tuple[str, int]]:
        conn = self.get_connection()
        cursor = conn.cursor()

        if group_key.lower() == "folder":
            conn.create_function("get_folder_path", 1, lambda s: s.rsplit("/", 1)[0])
            track_counts = cursor.execute(f"SELECT get_folder_path(file_path), COUNT (*) "
                                          f"FROM tracks "
                                          # f"WHERE {group_key} IS NOT NULL "
                                          f"GROUP BY get_folder_path(file_path)").fetchall()
        else:
            track_counts = cursor.execute(f"SELECT {group_key}, COUNT (*) "
                                          f"FROM tracks "
                                          # f"WHERE {group_key} IS NOT NULL "
                                          f"GROUP BY {group_key}").fetchall()

        return track_counts

    def get_tracks_by(self, key: str, value: Union[str, int]) -> List[Track]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if key.lower() == "folder":
            conn.create_function("get_folder_path", 1, lambda s: s.rsplit("/", 1)[0])
            cursor.execute(f"SELECT * FROM tracks WHERE get_folder_path(file_path) = ?", (value, ))

        elif value:
            if isinstance(value, str):
                value = value.replace("'", "''")
            cursor.execute(f"SELECT * FROM tracks WHERE {key} = '{value}'")
        else:
            cursor.execute(f"SELECT * FROM tracks WHERE {key} IS NULL")

        tracks: List[Track] = []
        rows = cursor.fetchall()
        for row in rows:
            track = Track(
                track_id=row["track_id"],
                file_path=row["file_path"],
                title=row["title"],
                album=row["album"],
                artist=row["artist"],
                composer=row["composer"],
                genre=row["genre"],
                year=row["year"],
                length=row["length"],
                # artwork_pixmap=get_artwork_pixmap(row["file_path"])
            )

            tracks.append(track)
        return tracks

    def get_tracks(self) -> List[Track]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks")

        tracks: List[Track] = []
        for row in cursor.fetchall():
            tracks.append(Track(
                track_id=row["track_id"],
                file_path=row["file_path"],
                title=row["title"],
                album=row["album"],
                artist=row["artist"],
                composer=row["composer"],
                genre=row["genre"],
                year=row["year"],
                length=row["length"]
                )
            )

        if QtWidgets.QApplication.instance() is not None:
            for track in tracks:
                track.artwork_pixmap = get_artwork_pixmap(track.file_path)

        return tracks

    def get_track_by_id(self, track_id: int) -> Track:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        row = cursor.execute("SELECT * FROM tracks WHERE track_id = ?", (track_id,)).fetchall()[0]

        track = Track(
            track_id=row["track_id"],
            file_path=row["file_path"],
            title=row["title"],
            album=row["album"],
            artist=row["artist"],
            composer=row["composer"],
            genre=row["genre"],
            year=row["year"],
            length=row["length"]
        )

        if QtWidgets.QApplication.instance() is not None:
            track.artwork_pixmap = get_artwork_pixmap(track.file_path)

        return track

    def drop_track_by_id(self, track_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE track_id = ?", (track_id,))
        conn.commit()
        conn.close()

    def drop_track_by(self, key: str, value: Union[int, float, str]) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM tracks WHERE {key} = ?", (value, ))
        conn.commit()
        conn.close()

    def update_track(self, track: Track, column: str, value: Union[int, float, str]) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tracks SET {column} = ? WHERE track_id = ?", (value, track.track_id))
        conn.commit()
        conn.close()

    def update_tracks_by_folder(self, folder_path: str, new_file_paths: List[str]) -> Tuple[List[Track], List[Track]]:
        """Adds new tracks to database if they're already not there and removes tracks from database
        if they're not in new tracks."""
        tracks_in_database = self.get_tracks_by("folder", folder_path)
        file_paths_in_database = [track.file_path for track in tracks_in_database]

        if not tracks_in_database:
            to_add = new_file_paths
            to_remove = []
        else:
            if isinstance(file_paths_in_database[0], tuple):
                file_paths_in_database = [t[0] for t in file_paths_in_database]

            to_add = list(set(new_file_paths) - set(file_paths_in_database))
            to_remove = list(set(file_paths_in_database) - set(new_file_paths))

        # print("FOLDER:", folder_path)
        # print("CURRENTLY IN FOLDER:", new_file_paths)
        # print("NEW FILE PATHS:", set(new_file_paths))
        # print("IN DATABASE:", set(file_paths_in_database))
        # print("TO ADD:", to_add)
        # print("TO REMOVE:", to_remove)

        tracks_to_add = self.convert_file_paths_to_tracks(to_add)
        tracks_to_remove = [track for track in tracks_in_database if track.file_path in to_remove]

        self.add_tracks(tracks_to_add)

        for file_path_to_remove in to_remove:
            self.drop_track_by("file_path", file_path_to_remove)

        return tracks_to_add, tracks_to_remove

    @staticmethod
    def convert_file_paths_to_tracks(file_paths: List[str]) -> List[Track]:
        tracks = []
        tag_manager = TagManager()
        for i, file_path in enumerate(file_paths):
            try:
                loaded_file = tag_manager.load_file(file_path)

                title = loaded_file["title"].first
                if not title:
                    title = os.path.basename(file_path).split("-", 1)[-1].strip()

                tracks.append(Track(
                    i,  # temporary id
                    file_path,
                    title,
                    loaded_file["album"].first,
                    loaded_file["artist"].first,
                    loaded_file["composer"].first,
                    loaded_file["genre"].first,
                    int(loaded_file["year"]) if int(loaded_file["year"]) else None,
                    int(loaded_file["#length"].first),
                    # get_artwork_pixmap(file_path, "album")
                ))
            except (mutagen.mp3.HeaderNotFoundError, NotImplementedError, ValueError):
                # TODO cannot convert '2020-10-26T20:39:57-04:00' to int type for year so ValueError (can be improved)
                continue

        return tracks

