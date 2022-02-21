import sqlite3
from typing import List

from repositories.base_repository import BaseRepository
from data_models.track import Track


class TracksRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        
    def add_track(self, track: Track) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (None,
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

    def get_tracks_grouped_by(self, group_key: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        output = cursor.execute(f"SELECT * FROM tracks GROUP BY '%{group_key}%'")
        print(output)
        for row in cursor.fetchall():
            print(row)

    def get_all_tracks(self) -> List[Track]:
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
                # artwork_path=row["artwork_path"]
            )
            )

        return tracks

    def get_track_by_title(self, title: str) -> Track:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        selected_row = cursor.execute(f"SELECT * FROM tracks WHERE name LIKE '%{title}%'").fetchone()

        return Track(
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

    def get_track_by_id(self, track_id: int) -> Track:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        row = cursor.execute("SELECT * FROM tracks WHERE track_id = ?", (track_id,)).fetchall()[0]

        return Track(
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

    def drop_track_by_id(self, track_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE track_id = ?", (track_id,))
        conn.commit()
        conn.close()
