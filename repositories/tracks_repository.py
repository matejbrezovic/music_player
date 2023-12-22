import os
import sqlite3
from typing import List, Union, Iterable, Tuple, Optional

import mutagen.mp3
from PyQt6.QtWidgets import QApplication

from data_models.track import Track
from repositories.base_repository import BaseRepository
from utils import get_embedded_artwork_pixmap, Singleton, TagManager


class TracksRepository(BaseRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

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

    def set_tracks(self, tracks: Iterable[Track]) -> None:
        self.reset_table("tracks")
        self.add_tracks(tracks)

    def get_track_counts_grouped_by(self, group_key: str) -> List[Tuple[str, int]]:
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
                rating=0,
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
                rating=0,
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
            self.drop_track_by("file_path", file_path_to_remove)

        return tracks_to_add, tracks_to_remove

    @staticmethod
    def convert_file_paths_to_tracks(file_paths: List[str]) -> List[Track]:
        converted_tracks = []
        tag_manager = TagManager()
        for i, file_path in enumerate(file_paths):
            try:
                loaded_file = tag_manager.load_file(file_path)

                title = loaded_file["title"].first
                artist = loaded_file["artist"].first
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

                converted_tracks.append(Track(
                    i,  # temporary id
                    file_path,
                    str(title),
                    loaded_file["album"].first,
                    artist,
                    loaded_file["composer"].first,
                    loaded_file["genre"].first,
                    int(loaded_file["year"]) if int(loaded_file["year"]) else None,
                    int(loaded_file["#length"].first),
                    int(os.path.getsize(file_path)),
                    0,
                    get_embedded_artwork_pixmap(file_path)
                ))
            except (mutagen.mp3.HeaderNotFoundError, NotImplementedError, ValueError) as e:
                print(e)
                # TODO cannot convert '2020-10-26T20:39:57-04:00' to int type for year so ValueError (can be improved)
                continue

        return converted_tracks


if __name__ == "__main__":
    t = TracksRepository()

    def test():
        global t
        root = "C:\\home\\matey\\Music\\"
        files = ["Nanatsu no Taizai OST - ELIEtheBEST.mp3",
                 "My Hero Academia -You Say Run- (Orchestral Arrangement) - 10K SPECIAL.mp3",
                 "y2mate.com - - - SAO II OST Track 01 - Gunland_OS-UjCmrJh0.mp3",
                 "Eminem Rap God (Explicit).mp3",
                 "Black Clover Rover & Catcher.mp3"]

        file_paths = [root + file for file in files]

        tracks = t.convert_file_paths_to_tracks(file_paths)

        for track in tracks:
            print(f"{track.artist} ||| {track.title}")

    print(t.get_track_count())
