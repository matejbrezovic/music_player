from typing import List, Tuple

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QRect, QItemSelectionModel, QItemSelection
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

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignTop

        if index.row() % 2 == 1:
            if index.column() == 1 and role == Qt.ItemDataRole.DisplayRole:
                return self._tracks[index.row()].artist
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
        return len(self._tracks) * 2

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
        self.clicked.connect(lambda index: self.selectionModel().select(*self.get_selection_params(index)))

    def get_selection_params(self, index: QModelIndex) -> Tuple[QItemSelection, QItemSelectionModel.SelectionFlag]:
        if index.row() % 2 == 0:
            return (QItemSelection(self._table_model.index(index.row(), 0),
                    self._table_model.index(index.row() + 1, 2)),
                    QItemSelectionModel.SelectionFlag.Select)
        else:
            return (QItemSelection(self._table_model.index(index.row() - 1, 0),
                    self._table_model.index(index.row(), 2)),
                    QItemSelectionModel.SelectionFlag.Select)

    def set_tracks(self, tracks: List[Track]) -> None:
        self._table_model.set_tracks(tracks)
        self.set_new_tracks.emit()
        #
        for i in range(len(tracks)):
            self.setSpan(i * 2, 0, 2, 1)
            # self.setSpan(i * 2, 1, 2, 1)

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