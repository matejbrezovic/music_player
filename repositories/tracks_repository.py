import sqlite3
from typing import List

from base_repository import BaseRepository
from models.track import Track


class TracksRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        
    def add_track(self, track: Track):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?)''', (None,
                                                                            track.name,
                                                                            track.album,
                                                                            track.artist,
                                                                            track.composer,
                                                                            track.genre,
                                                                            track.artwork_path))

    def get_all_tracks(self) -> List[Track]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks")

        tracks: List[Track] = []
        for row in cursor.fetchall():
            tracks.append(Track(
                track_id=row["track_id"],
                name=row["name"],
                album=row["album"],
                artist=row["artist"],
                composer=row["composer"],
                genre=row["genre"],
                artwork_path=row["artwork_path"]
            )
            )

        return tracks

    def get_track_by_name(self, name: str) -> Track:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        selected_track = cursor.execute(f"SELECT * FROM tracks WHERE name LIKE '%{name}%'").fetchone()

        return Track(
            track_id=selected_track["track_id"],
            name=selected_track["name"],
            album=selected_track["album"],
            artist=selected_track["artist"],
            composer=selected_track["composer"],
            genre=selected_track["genre"],
            artwork_path=selected_track["artwork_path"]
        )

    def get_track_by_id(self, track_id: int) -> Track:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        row = cursor.execute("SELECT * FROM tracks WHERE track_id = ?", (track_id,)).fetchall()[0]

        return Track(
            track_id=row["track_id"],
            name=row["name"],
            album=row["album"],
            artist=row["artist"],
            composer=row["composer"],
            genre=row["genre"],
            artwork_path=row["artwork_path"]
        )

    def drop_track_by_id(self, track_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE track_id = ?", (track_id,))
        conn.commit()
        conn.close()
