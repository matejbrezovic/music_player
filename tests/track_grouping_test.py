import sys
from itertools import groupby
from operator import attrgetter

from PyQt6.QtWidgets import QApplication

from repositories.tracks_repository import TracksRepository

def key_getter(attr="album"):
    if attr == "file_path":
        return str(attrgetter(cls, attr)).split("/" if "/" in cls.file_path else "\\")[-2]

    return attrgetter(attr)


def main():
    tracks = TracksRepository().get_tracks()

    group_key = "album"
    groups = []

    grouped = groupby(sorted(tracks, key=key_getter()))
    for group, data in grouped:
        print(group)
        print(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main()

    sys.exit(app.exec())