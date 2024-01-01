import os
import sqlite3
from typing import List, Union, Iterable, Tuple, Optional

import eyed3
from PyQt6.QtWidgets import QApplication

from constants import SUPPORTED_AUDIO_FORMATS
from data_models.track import Track
from repositories import BaseRepository
from utils import get_embedded_artwork_pixmap, Singleton


class TracksRepository(BaseRepository, metaclass=Singleton):
    def add_track(self, track: Track) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (None,
                        track.file_path,
                        track.title,
                        track.album,
                        track.artist,
                        track.composer,
                        track.genre,
                        track.year,
                        track.length,
                        track.size,
                        track.rating
                        ))
        conn.commit()
        conn.close()

    def add_tracks(self, tracks: Iterable[Track]) -> None:
        for track in tracks:
            self.add_track(track)

    def add_new_tracks(self, tracks: Iterable[Track]) -> None:  # TODO remove?
        existing_tracks = self.get_tracks()
        tracks_to_add = []
        for track in tracks:
            if track not in existing_tracks:
                tracks_to_add.append(track)
        self.add_tracks(tracks_to_add)

    def get_track_counts_grouped_by_key(self, group_key: str) -> List[Tuple[str, int]]:
        conn = self.get_connection()
        cursor = conn.cursor()

        if group_key.lower() == "folder":
            conn.create_function("get_folder_path", 1, lambda s: s.rsplit("/", 1)[0])
            group_key = "get_folder_path(file_path)"

        track_counts = cursor.execute(f"SELECT {group_key}, COUNT (*) "
                                      f"FROM tracks "
                                      f"GROUP BY {group_key}").fetchall()

        conn.close()
        return track_counts

    def get_tracks_by(self, key: str, value: Optional[Union[str, int]]) -> List[Track]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if value == "all":
            return self.get_tracks()
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
                title=str(row["title"]),
                album=row["album"],
                artist=row["artist"],
                composer=row["composer"],
                genre=row["genre"],
                year=row["year"],
                length=row["length"],
                size=row["size"],
                rating=row["rating"] if row["rating"] else 0,
                artwork_pixmap=get_embedded_artwork_pixmap(row["file_path"])
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
                length=row["length"],
                size=row["size"],
                rating=row["rating"] if row["rating"] else 0,
                artwork_pixmap=get_embedded_artwork_pixmap(row["file_path"])
                )
            )

        if QApplication.instance() is not None:
            for track in tracks:
                track.artwork_pixmap = get_embedded_artwork_pixmap(track.file_path)

        return tracks

    def get_track_count(self) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()

        track_count = cursor.execute("SELECT Count(track_id) FROM tracks").fetchone()[0]
        return track_count

    def delete_track_by(self, key: str, value: Union[int, float, str]) -> None:
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
                file_paths_in_database = [track[0] for track in file_paths_in_database]

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
            self.delete_track_by("file_path", file_path_to_remove)

        return tracks_to_add, tracks_to_remove

    @staticmethod
    def convert_file_paths_to_tracks(file_paths: List[str]) -> List[Track]:
        converted_tracks = []
        for i, file_path in enumerate(file_paths):
            print(file_path)
            if not os.path.splitext(file_path)[-1] in SUPPORTED_AUDIO_FORMATS:
                continue

            audio_file = eyed3.load(file_path)

            if not audio_file.tag:
                audio_file.initTag()

            title = audio_file.tag.title
            artist = audio_file.tag.artist
            if not title and not artist:
                title = os.path.splitext(os.path.basename(file_path))[0]
                split = title.split(" - ", 1)
                if len(split) == 2:
                    artist, title = split
                else:
                    title = split[0]
                if artist:
                    artist = artist.strip()
                title = title.strip()
            elif not title:
                title = os.path.splitext(os.path.basename(file_path))[0]
            elif not artist:
                pass

            rating = None
            for popm in audio_file.tag.popularities:
                if popm.rating:
                    if popm.rating == 255:
                        rating = 5
                    elif popm.rating >= 186:
                        rating = 4
                    elif popm.rating >= 128:
                        rating = 3
                    elif popm.rating >= 64:
                        rating = 2
                    elif popm.rating >= 32:
                        rating = 1
                    else:
                        rating = 0
                    break

            tr = Track(
                i,  # temporary id
                file_path,
                str(title),
                audio_file.tag.album,
                artist,
                audio_file.tag.composer,
                audio_file.tag.genre,
                audio_file.tag.recording_date.year if audio_file.tag.recording_date else None,
                int(audio_file.info.time_secs),
                int(audio_file.info.size_bytes),
                rating if rating else 0,
                get_embedded_artwork_pixmap(file_path) if QApplication.instance() else None
            )
            converted_tracks.append(tr)

        return converted_tracks
