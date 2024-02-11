import os
import sqlite3
from sqlite3 import Error

from constants import DATABASE_PATH


def _create_connection() -> None:
    """ create a database connection to a SQLite database """
    conn = None
    try:
        if not os.path.exists(os.path.dirname(DATABASE_PATH)):
            os.mkdir(os.path.dirname(DATABASE_PATH))

        conn = sqlite3.connect(DATABASE_PATH)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def _create_tables() -> None:
    create_tracks_table_query = '''
    CREATE TABLE "tracks" (
        "track_id"	INTEGER NOT NULL UNIQUE,
        "file_path"	TEXT NOT NULL,
        "title"	NUMERIC,
        "album"	TEXT,
        "artist"	TEXT,
        "composer"	TEXT,
        "genre"	TEXT,
        "year"	INTEGER,
        "length"	INTEGER,
        "size"	INTEGER DEFAULT 0,
        "rating"	REAL DEFAULT 0,
        PRIMARY KEY("track_id" AUTOINCREMENT)
    );'''

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(create_tracks_table_query)

    conn.commit()
    conn.close()


def setup_database() -> None:
    _create_connection()
    _create_tables()
