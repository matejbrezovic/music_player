import sys
import time
from typing import List

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QTableView, QAbstractItemView

from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, tracks: List[Track]):
        super().__init__()
        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        self._tracks = tracks
        self.items = []
        self.total_count = len(tracks)
        self.loaded_count = 0

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not self._tracks:
            return None
        if role == Qt.ItemDataRole.DecorationRole:
            if not index.column():
                icon = QIcon(self._tracks[index.row()].artwork_pixmap)
                return icon
        if role == Qt.ItemDataRole.DisplayRole:
            value = self.column_names[index.column()].lower()
            return getattr(self._tracks[index.row()], value) if value else None

    def rowCount(self, index: QModelIndex = QModelIndex):
        return len(self._tracks)

    def columnCount(self, index: QModelIndex = QModelIndex):
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
    set_new_tracks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().setDefaultSectionSize(22)
        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]

    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_model = TableModel(tracks)
        # self.table_model.setHeaderData(3, Qt.Orientation.Horizontal, "Title")
        self.setModel(self.table_model)

        self.set_new_tracks.emit()

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(SELECTION_STYLESHEET)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(LOST_FOCUS_STYLESHEET)
        super().focusOutEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table_widget = TableView()

        self.table_widget.horizontalHeader().setMinimumSectionSize(20)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        self.table_widget.setStyleSheet(SELECTION_STYLESHEET)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        start = time.time()
        self.table_widget.set_tracks(TracksRepository().get_tracks() * 10000)
        print(f"Test loaded in: {time.time() - start:.6f} s")

        self.setCentralWidget(self.table_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
