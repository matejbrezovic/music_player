import sqlite3
import time
from typing import List, Union, Iterable

from PyQt6 import QtWidgets

from repositories.base_repository import BaseRepository
from data_models.track import Track
from utils import get_artwork_pixmap

import pandas as pd


class TracksRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        
    def add_track(self, track: Track) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (None,
                                                                                 track.file_path,
                                                                                 track.title,
                                                                                 track.album,
                                                                                 track.artist,
                                                                                 track.composer,
                                                                                 track.genre,
                                                                                 track.year,
                                                                                 track.length
                                                                                 ))
        conn.commit()
        conn.close()

    def add_tracks(self, tracks: Iterable[Track]) -> None:
        for track in tracks:
            self.add_track(track)

    def get_track_counts_grouped_by(self, group_key: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        track_counts = cursor.execute(f"SELECT {group_key}, COUNT (*) "
                                      f"FROM tracks "
                                      # f"WHERE {group_key} IS NOT NULL "
                                      f"GROUP BY {group_key}").fetchall()
        print(track_counts)
        return track_counts

    def get_tracks_by(self, key: str, value: Union[str, int]) -> List[Track]:
        start = time.time()

        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if value:
            cursor.execute(f"SELECT * FROM tracks WHERE {key} = '{value}'")
        else:
            cursor.execute(f"SELECT * FROM tracks WHERE {key} IS NULL")
        # print(f"SELECT * FROM tracks WHERE {key} = '{value if value }'")

        # for row in cursor.fetchall():
        #     print(row)

        tracks: List[Track] = []
        rows = cursor.fetchall()
        for row in rows:
            # print(row)
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

            tracks.append(track)

            # if QtWidgets.QApplication.instance() is not None:
            #     for track in tracks:
            #         track.artwork_pixmap = get_artwork_pixmap(track.file_path)

        print("Tracks loaded in:", time.time() - start)
        return tracks

    def get_tracks(self) -> List[Track]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks")

        # for row in cursor.fetchall():
        #     print(row)

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

    def get_track_by_title(self, title: str) -> Track:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        selected_row = cursor.execute(f"SELECT * FROM tracks WHERE name LIKE '%{title}%'").fetchone()

        track = Track(
            track_id=selected_row["track_id"],
            file_path=selected_row["file_path"],
            title=selected_row["title"],
            album=selected_row["album"],
            artist=selected_row["artist"],
            composer=selected_row["composer"],
            genre=selected_row["genre"],
            year=selected_row["year"],
            length=selected_row["length"]
        )

        if QtWidgets.QApplication.instance() is not None:
            track.artwork_pixmap = get_artwork_pixmap(track.file_path)

        return track

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
