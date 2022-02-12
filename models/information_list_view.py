from time import sleep
from typing import List, Tuple, Union

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QRect, QItemSelectionModel, QItemSelection, QAbstractItemModel
from PyQt6.QtWidgets import QListView, QTableView, QStyledItemDelegate, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QFrame, QPushButton

from constants import *
from data_models.track import Track
from utils import ElidedLabel, format_seconds


class InformationTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self.table_view = parent
        self._tracks = []
        self._playing_track_index = None

        self.loaded_indexes: List[int] = []
        self.old_indexes: List[int] = []

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not self._tracks:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignTop

        if role == Qt.ItemDataRole.DecorationRole:
            if not index.column():
                print(index.row())
                artwork_pixmap = self._tracks[index.row()].artwork_pixmap
                artwork_pixmap = artwork_pixmap if artwork_pixmap else QPixmap(f"icons/album.png")
                icon = QIcon(artwork_pixmap)
                return icon if icon else None

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() != 1:
                return None
            # if index.column() == 1 and index.row() in self.old_indexes:
            #     try:
            #         self.table_view.indexWidget(index).deleteLater()
            #     except AttributeError:
            #         pass
            track = self._tracks[index.row()]
            widget_id = f"{track.title}{track.artist}{format_seconds(track.length)}"

            index_widget = self.table_view.indexWidget(index)

            if not index_widget or index_widget.id != widget_id:
                self.loaded_indexes.append(index.row())
                # index.id = hash(tuple(track.track_id for track in self._tracks))


                self.table_view.setIndexWidget(index, CustomLabelWidget(track.title,
                                                                        track.artist,
                                                                        format_seconds(track.length)))
            # elif index.column() == 1 and self.table_view.indexWidget(index):
            #     if index.id == hash(tuple(track.track_id for track in self._tracks)):
            #         return None
            #
            #     index.id = hash(tuple(track.track_id for track in self._tracks))
            #
            #     track = self._tracks[index.row()]
            #     self.table_view.setIndexWidget(index, CustomLabelWidget(track.title,
            #                                                             track.artist,
            #                                                             format_seconds(track.length)))

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
        print(len(self._tracks))
        # self.old_indexes.extend(self.loaded_indexes)
        # self.loaded_indexes = []

    def set_currently_playing_track_index(self, index: int) -> None:
        self._playing_track_index = index


class MyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks: List[Track] = []

    def createEditor(self, parent, option, index):
        track: Track = self._tracks[index.row()]
        return CustomLabelWidget(track.title,
                                 track.artist,
                                 format_seconds(track.length))

    def setModelData(self, editor, model, index):
        print(model, index)
        super().setModelData(editor, model, index)

    # def setEditorData(self, editor, model):
    #     pass

    def paint(self, painter, option, index):
        track: Track = self._tracks[index.row()]
        label = CustomLabelWidget(track.title,
                                  track.artist,
                                  format_seconds(track.length))
        # label.render()


    def set_tracks(self, tracks: List[Track]) -> None:
        self._tracks = tracks


class CustomLabelWidget(QWidget):
    def __init__(self, title: str, artist: str, duration: str, parent=None):
        super().__init__(parent)
        # self.setMinimumSize(100, 100)
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.h_layout = QHBoxLayout()

        self.id = f"{title}{artist}{duration}"

        title_label = ElidedLabel(title)
        title_label.setMinimumHeight(20)

        dur_label = QLabel(duration)
        dur_label.setMinimumHeight(20)
        dur_label.setFixedWidth(30)

        self.h_layout.addWidget(title_label)
        self.h_layout.addWidget(dur_label)
        self.upper_widget = QWidget()
        self.upper_widget.setMinimumHeight(40)
        self.upper_widget.setLayout(self.h_layout)

        self.v_layout.addWidget(self.upper_widget)
        self.v_layout.addWidget(ElidedLabel(artist))


class InformationTableView(QTableView):
    set_new_tracks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_model = InformationTableModel(self)
        self._table_delegate = MyDelegate()
        self.setModel(self._table_model)
        # self.setItemDelegateForColumn(1, self._table_delegate)

    def set_tracks(self, tracks: List[Track]) -> None:
        self._table_model.set_tracks(tracks)
        # self._table_delegate.set_tracks(tracks)
        # for i, track in enumerate(tracks[:700]):
        #     print(i)
        #     # if not i:
        #     #     frame = QFrame()
        #     #     layout = QVBoxLayout(frame)
        #     #
        #     #     layout.addWidget(CustomLabelWidget(track.title,
        #     #                       track.artist,
        #     #                       format_seconds(track.length)))
        #     #     frame.setMinimumSize(300, 300)
        #     #     frame.show()
        #     # sleep(1000)
        #
        #     # self.setIndexWidget(self._table_model.index(i, 1), QPushButton("TTTT"))
        #
        #
        #     self.setIndexWidget(self._table_model.index(i, 1), CustomLabelWidget(track.title,
        #                                                                          track.artist,
        #                                                                          format_seconds(track.length)))
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