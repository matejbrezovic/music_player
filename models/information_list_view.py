from typing import List

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtWidgets import QListView, QTableView

from constants import *
from data_models.track import Track


class InformationTableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._tracks = []
        self._playing_track_index = None

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not self._tracks:
            return None

        if role == Qt.ItemDataRole.DecorationRole:
            if not index.column():
                artwork_pixmap = self._tracks[index.row()].artwork_pixmap
                artwork_pixmap = artwork_pixmap if artwork_pixmap else QPixmap(f"icons/album.png")
                icon = QIcon(artwork_pixmap)
                return icon if icon else None

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 1:
                return self._tracks[index.row()].title

    def rowCount(self, index: QModelIndex = QModelIndex):
        return len(self._tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex) -> int:
        return 3

    def set_tracks(self, tracks: List[Track]) -> None:
        self.layoutAboutToBeChanged.emit()
        self._tracks = tracks
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))

    def set_currently_playing_track_index(self, index: int) -> None:
        self._playing_track_index = index


class InformationTableView(QTableView):
    set_new_tracks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_model = InformationTableModel()
        self.setModel(self._table_model)

    def set_tracks(self, tracks: List[Track]) -> None:
        self._table_model.set_tracks(tracks)
        self.set_new_tracks.emit()

    def set_currently_playing_track_index(self, index: int) -> None:
        self._table_model.set_currently_playing_track_index(index)

    def set_paused(self) -> None:
        ...

    def set_unpaused(self) -> None:
        ...

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(SELECTION_STYLESHEET)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(LOST_FOCUS_STYLESHEET)
        super().focusOutEvent(event)