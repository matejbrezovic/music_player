import sys
from typing import List

from PyQt6.QtGui import QPixmap
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtWidgets import QApplication, QTableView, QLabel

import time
import string

from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import SpeakerLabel, ImageLabel

BATCH_SIZE = 100


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, tracks: List[Track]):
        super().__init__()
        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        self._tracks = tracks
        self.items = []
        self.total_count = len(tracks)
        self.loaded_count = 0

    def data(self, index: QModelIndex, role: Qt.ItemDataRole.DisplayRole):
        if not self._tracks:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            value = self.column_names[index.column()].lower()
            return getattr(self._tracks[index.row()], value) if value else None

    def rowCount(self, index):
        return len(self._tracks)

    def columnCount(self, index):
        return len(self.column_names)

    # def canFetchMore(self, parent=QModelIndex()):
    #     return self.loaded_count < self.total_count
    #
    # def fetchMore(self, parent=QModelIndex()):
    #     remainder = self.total_count - self.loaded_count
    #     fetch_count = min(BATCH_SIZE, remainder)
    #     print(f"Fetch count: {fetch_count}")
    #
    #     for i in range(fetch_count):
    #         self.items.append(len(self.items))
    #
    #     self.beginInsertRows(parent, self.loaded_count,
    #                          self.loaded_count + fetch_count - 1)
    #     self.loaded_count += fetch_count
    #     self.endInsertRows()


class TableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        # self.table_model = TableModel([])
        # self.table_model.setHeaderData(3, Qt.Orientation.Horizontal, "Title")
        # self.setModel(self.table_model)

    def set_tracks(self, tracks: List[Track]) -> None:
        # data = []
        #
        # start = time.time()
        # for i, track in enumerate(tracks):
        #     track_data = []
        #     for j in range(len(self.column_names)):
        #         try:
        #             track_data.append(getattr(track, self.column_names[j].lower()))
        #         except AttributeError:
        #             pass
        #
        #     # # speaker_label = SpeakerLabel()
        #     # # # speaker_label.setFixedSize(22, 16)
        #     # # speaker_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #     # image_label = QLabel()
        #     # image_label.setFixedSize(22, 22)
        #     # image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #     # if track.artwork_pixmap:
        #     #     image_label.setPixmap(QPixmap(track.artwork_pixmap).scaledToHeight(self.height(), Qt.TransformationMode.SmoothTransformation))
        #     # else:
        #     #     image_label.setText("-")
        #     # track_data = ["", ""] + track_data
        #     data.append(track_data)
        # print(f"Data created in: {time.time() - start}")

        self.table_model = TableModel(tracks)
        self.table_model.setHeaderData(3, Qt.Orientation.Horizontal, "Title")
        self.setModel(self.table_model)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = TableView()

        # data = [["asdsadsdas", "assgdbsrswe", 3, "asdsadsda", 123, "nosrujgbopwse"] for _ in range(3000)]

        # self.model = TableModel(data)
        # self.table.setModel(self.model)

        start = time.time()
        self.table.set_tracks(TracksRepository().get_tracks() * 10000)
        print(f"Test loaded in: {time.time() - start:.6f} s")

        self.setCentralWidget(self.table)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
