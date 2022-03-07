import sys
import time
from typing import List, Optional

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QBrush, QFontMetrics
from PyQt6.QtWidgets import QApplication, QTableView, QAbstractItemView, QHeaderView, QStyleOptionViewItem, QStyle, \
    QStyledItemDelegate

import global_timer
from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import get_artwork_pixmap


class TrackTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        self._tracks: List[Track] = []
        self.is_playing = False
        self.playing_track_index: Optional[int] = None

        self.playing_speaker_pixmap = QPixmap("icons/speaker_playing.png").scaled(
            16, 22,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

        self.muted_speaker_pixmap = QPixmap("icons/speaker_muted.png").scaled(
            16, 22,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

    def set_tracks(self, tracks: List[Track]) -> None:
        # global_timer.print_elapsed_time()
        self.layoutAboutToBeChanged.emit()
        self._tracks = tracks
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))
        # global_timer.print_elapsed_time()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not self._tracks:
            return None

        if index.column() == 0:
            ...
            # print(index.row())

        if role == Qt.ItemDataRole.TextAlignmentRole and not index.column():
            return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.DecorationRole:
            # return None
            if not index.column():  # TODO can probably be improved
                track = self._tracks[index.row()]
                artwork_pixmap = track.artwork_pixmap
                if artwork_pixmap is None:
                    new_pixmap = get_artwork_pixmap(track.file_path)
                    track.artwork_pixmap = new_pixmap if new_pixmap else ""
                    artwork_pixmap = track.artwork_pixmap
                if not artwork_pixmap:
                    return None
                return artwork_pixmap
                # icon = QIcon(artwork_pixmap)
                # icon.addPixmap(artwork_pixmap, QtGui.QIcon.Mode.Selected)
                # return icon if icon else None
            elif index.column() == 1:
                if self.playing_track_index is None:
                    return
                if index.row() == self.playing_track_index:
                    if self.is_playing:
                        return self.playing_speaker_pixmap
                    elif not self.is_playing:
                        return self.muted_speaker_pixmap

        if role == Qt.ItemDataRole.DisplayRole and not index.data(Qt.ItemDataRole.DecorationRole):
            if not index.column():
                return "-"

            value = self.column_names[index.column()].lower()
            return getattr(self._tracks[index.row()], value) if value else None

    def rowCount(self, index: QModelIndex = QModelIndex):
        return len(self._tracks)

    def columnCount(self, index: QModelIndex = QModelIndex):
        return len(self.column_names)

    def set_paused(self) -> None:
        self.is_playing = False
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(self.playing_track_index, 1), self.index(self.playing_track_index, 1))

    def set_unpaused(self) -> None:
        self.is_playing = True
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(self.playing_track_index, 1), self.index(self.playing_track_index, 1))

    def set_playing_track_index(self, index: Optional[int]) -> None:
        self.playing_track_index = index
        # print("Playing track index: ", index)
        if self.playing_track_index is not None:
            # print("Set playing")
            self.dataChanged.emit(self.index(0, 1),
                                  self.index(self.rowCount(), 1))


class TrackTableItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        # self._tracks: List[Track] = []
        # self._playing_track_index = None
        # self.is_playing = False
        # self.loaded_pixmap_indexes = []
        # self.track_info_widgets_mapping = {}

        self.pixmap_width = 16
        self.pixmap_height = 16

        # self.playing_pixmap = QPixmap("icons/speaker_playing.png").scaled(self.pixmap_width, self.pixmap_height,
        #                                                                   Qt.AspectRatioMode.IgnoreAspectRatio,
        #                                                                   Qt.TransformationMode.SmoothTransformation)
        # self.paused_pixmap = QPixmap("icons/speaker_muted.png").scaled(self.pixmap_width, self.pixmap_height,
        #                                                                Qt.AspectRatioMode.IgnoreAspectRatio,
        #                                                                Qt.TransformationMode.SmoothTransformation)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        if option.state & QStyle.StateFlag.State_Selected:
            if self._table_view.hasFocus():
                fill_color = SELECTION_QCOLOR
                border_color = SELECTION_QCOLOR_BORDER
            else:
                fill_color = LOST_FOCUS_QCOLOR
                border_color = fill_color
            painter.setBrush(fill_color)
            painter.drawRect(option.rect)
            painter.setPen(QPen(QBrush(border_color), 1))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            # painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))
        # painter.drawRect(option.rect)

        if index.data(Qt.ItemDataRole.DecorationRole):
            decoration_value = index.data(Qt.ItemDataRole.DecorationRole)
            rect = option.rect
            rect.setRect(rect.left() + 1, rect.top() + 1,
                         rect.width() - 2, rect.height() - 2)

            if index.column() == 1:
                height = rect.height()
                rect.setHeight(rect.width())
                rect.translate(0, (height - rect.width()) / 2)

            pixmap = decoration_value.scaled(rect.width(), rect.width(),
                                             Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)

            painter.drawPixmap(rect, pixmap)

        if index.data(Qt.ItemDataRole.DisplayRole):
            painter.setPen(QPen(Qt.GlobalColor.black))
            text = index.data(Qt.ItemDataRole.DisplayRole)
            if text:
                elided_text = QFontMetrics(option.font).elidedText(str(text), Qt.TextElideMode.ElideRight,
                                                                   option.rect.width())
                painter.drawText(option.rect, Qt.AlignmentFlag.AlignVCenter, elided_text)


class TrackTableView(QTableView):
    set_new_tracks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        self._table_model = TrackTableModel(self)
        self._table_delegate = TrackTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)

    def set_tracks(self, tracks: List[Track]) -> None:
        self._table_model.set_tracks(tracks)
        self.set_new_tracks.emit()

    def set_playing_track_index(self, index: Optional[int]) -> None:
        self._table_model.set_playing_track_index(index)

    def set_paused(self) -> None:
        self._table_model.set_paused()

    def set_unpaused(self) -> None:
        self._table_model.set_unpaused()

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(SELECTION_STYLESHEET)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(LOST_FOCUS_STYLESHEET)
        super().focusOutEvent(event)


class TestMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table_widget = TrackTableView(self)

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
    mainWindow = TestMainWindow()
    mainWindow.show()
    sys.exit(app.exec())
