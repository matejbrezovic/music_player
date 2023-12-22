from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from random import randint, choice
from string import ascii_letters
from typing import Any, Optional
from typing import List

from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt6.QtGui import QFocusEvent
from PyQt6.QtWidgets import QApplication, QTableView, QHeaderView, QVBoxLayout, QPushButton, QWidget, QMainWindow

# from PySide6.QtCore import Qt, QModelIndex, Slot, QAbstractTableModel
# from PySide6.QtGui import QFocusEvent
# from PySide6.QtWidgets import QApplication, QTableView, QHeaderView, QVBoxLayout, QPushButton, QWidget, QMainWindow

# from constants import ROOT

DEFAULT_LOADED_TRACKS_FILE_PATH = f"/tracks.txt"
MAIN_PANEL_COLUMN_NAMES = ("", "", "Artist", "Title", "Album", "Year", "Genre", "Rating", "Time")


@dataclass
class Track:
    track_id: int
    file_path: str = field(repr=False)
    title: str
    album: str
    artist: str
    composer: str = field(repr=False)
    genre: str = field(repr=False)
    year: int = field(repr=False)
    length: int = field(repr=False)
    rating: int = field(repr=False, default=0)
    artwork_pixmap: Any = field(repr=False, default=None)


def random_string():
    return ''.join(choice(ascii_letters + " ") for _ in range(randint(10, 40)))

def get_random_color():
    return choice(["red", "yellow", "blue", "green", "orange", "purple"])


def generate_random_track():
    return Track(
        randint(1, 100000),
        random_string(),
        random_string(),
        random_string(),
        random_string(),
        random_string(),
        random_string(),
        randint(2000, 2022),
        randint(60, 3600),
        randint(0, 10),
    )


class JsonTracksRepository:
    def get_tracks(self) -> List[Track]:
        with open(DEFAULT_LOADED_TRACKS_FILE_PATH, "r") as f:
            try:
                loaded_json = json.loads(f.read())
                tracks = [self._decode_track(t) for t in loaded_json]

                return tracks
            except json.decoder.JSONDecodeError:
                return []

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


class TrackTableModel(QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self._tracks: List[Track] = []

        self.dataChanged.connect(self.data_changed_slot)
        self.layoutChanged.connect(self.layout_changed_slot)

    def data_changed_slot(self):
        print("Data changed")

    def layout_changed_slot(self):
        print("Layout changed")

    # @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self.layoutAboutToBeChanged.emit()
        self._tracks = tracks
        self.layoutChanged.emit()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self._tracks:
            return None
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column():
                return Qt.AlignmentFlag.AlignCenter


        if role == Qt.ItemDataRole.DisplayRole and not index.data(Qt.ItemDataRole.DecorationRole):
            if index.column() == 0:
                return "-"

            value = MAIN_PANEL_COLUMN_NAMES[index.column()].lower()
            if value == "time":
                value = "length"
            return getattr(self._tracks[index.row()], value) if value else None

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self._tracks)

    def columnCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(MAIN_PANEL_COLUMN_NAMES)


class TrackTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks: List[Track] = []

        self._table_model = TrackTableModel(self)
        self.setModel(self._table_model)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)

        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

    # @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self._tracks = tracks
        self._table_model.set_tracks(tracks)

    def focusInEvent(self, event: QFocusEvent) -> None:
        if QApplication.mouseButtons() & Qt.MouseButton.LeftButton:
            self.clearSelection()
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        return super().focusOutEvent(event)


TRACKS = JsonTracksRepository().get_tracks()

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumHeight(100)
        self.resize(self.width(), 500)

        self.widget = QWidget()

        self.vbox = QVBoxLayout(self.widget)

        self.table_view = TrackTableView(self)

        self.table_view.horizontalHeader().setMinimumSectionSize(20)
        self.table_view.verticalHeader().setVisible(False)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)

        self.vbox.addWidget(self.table_view)
        self.vbox.addWidget(self.refresh_button)

        self.setCentralWidget(self.widget)

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setMinimumSectionSize(10)

        # self.tracks = JsonTracksRepository().get_tracks()
        # self.random_tracks = [generate_random_track() for _ in range(10000)]
        # self.refresh()
        # self.refresh_button.setStyleSheet("QPushButton::clicked {background-color: blue;}")
        # print(TRACKS)

    def refresh(self):
        # self.refresh_button.setStyleSheet(f"background: {get_random_color()};")
        self.table_view.setStyleSheet(f"background: {get_random_color()};")
        self.table_view.set_tracks(TRACKS) # change random_tracks to tracks to see the difference
        self.table_view.scrollToTop()
        print("Refreshed!")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    # with cProfile.Profile() as pr:
    mainWindow = TestMainWindow()
    mainWindow.show()
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()
    sys.exit(app.exec())
