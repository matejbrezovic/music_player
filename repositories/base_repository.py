import sqlite3
from typing import List

from constants import *


class BaseRepository:
    def __init__(self):
        print(DATABASE_PATH)

    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DATABASE_PATH)
        return conn

    def get_all_table_names(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        table_names = [elem[0] for elem in
                       cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        return table_names

    def get_all_table_rows(self, table_name: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        table_rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        return table_rows

    def get_all_table_columns(self, table_name: str):
        conn = self.get_connection()
        cursor = conn.execute(f"SELECT * FROM {table_name}")

        table_columns = list(cursor.description)
        for index, column in enumerate(table_columns):
            table_columns[index] = column[0]

        return table_columns

    def drop_all_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        table_names = self.get_all_table_names()
        if table_names:
            for name in table_names:
                cursor.execute(f"DROP TABLE {name}")

    def create_table(self, table_name: str, table_columns: List):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(table_columns)})''')
        conn.commit()

    def reset_table(self, table_name: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"DELETE * FROM {table_name};")

        conn.commit()
        conn.close()
