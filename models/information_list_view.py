from typing import List

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QTableView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QFrame

from constants import *
from data_models.track import Track
from utils import ElidedLabel, format_seconds


class InformationTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self.table_view = parent
        self._tracks = []
        self._playing_track_index = None

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not self._tracks:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignTop

        if role == Qt.ItemDataRole.DecorationRole:
            if not index.column():
                # print(index.row())
                artwork_pixmap = self._tracks[index.row()].artwork_pixmap
                artwork_pixmap = artwork_pixmap if artwork_pixmap else QPixmap(f"icons/album.png")
                icon = QIcon(artwork_pixmap)
                return icon if icon else None

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() != 1:
                return None
            track = self._tracks[index.row()]
            widget_id = f"{track.title}{track.artist}{format_seconds(track.length)}"
            index_widget = self.table_view.indexWidget(index)

            if not index_widget or index_widget.id != widget_id:
                self.table_view.setIndexWidget(index, TrackInfoWidget(track.title,
                                                                      track.artist,
                                                                      format_seconds(track.length)))

            return QtCore.QVariant()

    def rowCount(self, index: QModelIndex = QModelIndex):
        return len(self._tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex) -> int:
        return 2

    def set_tracks(self, tracks: List[Track]) -> None:
        self.layoutAboutToBeChanged.emit()
        self._tracks = tracks
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))

    def set_currently_playing_track_index(self, index: int) -> None:
        self._playing_track_index = index


class TrackInfoWidget(QWidget):
    def __init__(self, title: str, artist: str, duration: str, parent=None):
        super().__init__(parent)
        # self.setMinimumSize(100, 100)
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 0, 5, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        self.id = f"{title}{artist}{duration}"

        title_label = ElidedLabel(title)
        title_label.setContentsMargins(0, 0, 0, 0)
        title_label.setMinimumHeight(20)

        dur_label = QLabel(duration)
        dur_label.setContentsMargins(0, 0, 0, 0)
        dur_label.setMinimumHeight(20)
        dur_label.setFixedWidth(30)

        self.h_layout.addWidget(title_label, Qt.AlignmentFlag.AlignLeft)
        self.h_layout.addWidget(dur_label)
        self.upper_widget = QWidget()
        self.upper_widget.setContentsMargins(0, 0, 0, 0)
        self.upper_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        self.upper_widget.setLayout(self.h_layout)

        self.v_layout.addWidget(self.upper_widget)
        self.v_layout.addWidget(ElidedLabel(artist))


class InformationTableView(QTableView):
    set_new_tracks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_model = InformationTableModel(self)
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