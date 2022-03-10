import sys
import time
from typing import List, Optional, Any

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QEvent, QItemSelectionModel
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QFontMetrics, QAction
from PyQt6.QtWidgets import QApplication, QTableView, QAbstractItemView, QHeaderView, QStyleOptionViewItem, QStyle, \
    QStyledItemDelegate, QToolButton, QMenu, QVBoxLayout, QPushButton, QWidget

from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import get_artwork_pixmap, format_seconds


class TrackTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
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

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self._tracks:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole and not index.column():
            return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.DecorationRole:
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

            value = MAIN_PANEL_COLUMN_NAMES[index.column()].lower()
            if value == "time":
                return format_seconds(getattr(self._tracks[index.row()], "length"))
            return getattr(self._tracks[index.row()], value) if value else None

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self._tracks)

    def columnCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(MAIN_PANEL_COLUMN_NAMES)

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

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        if option.state & QStyle.StateFlag.State_Selected:
            if self._table_view.hasFocus():
                fill_color = SELECTION_QCOLOR
                border_color = SELECTION_QCOLOR_BORDER
            else:
                fill_color = LOST_FOCUS_QCOLOR
                border_color = LOST_FOCUS_QCOLOR_BORDER
            painter.setBrush(fill_color)
            painter.drawRect(option.rect)
            painter.setPen(QPen(QBrush(border_color), 1))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            # bottom_left = option.rect.bottomLeft() # buggy
            # bottom_left.setY(bottom_left.y())
            # bottom_right = option.rect.bottomRight()
            # bottom_right.setY(bottom_right.y())
            # painter.drawLine(bottom_left, bottom_right)
            # print(index.row(), len(self._table_view.selectedIndexes()) // len(MAIN_PANEL_COLUMN_NAMES) - 1)
            # if index.row() == self._table_view.selectedIndexes()[-1].row():  # might be ruining performance
            #     painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))

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
            text = f"{index.data(Qt.ItemDataRole.DisplayRole)}"
            if text:
                elided_text = QFontMetrics(option.font).elidedText(str(text), Qt.TextElideMode.ElideRight,
                                                                   option.rect.width())
                alignment = Qt.AlignmentFlag.AlignVCenter if index.column() else Qt.AlignmentFlag.AlignCenter
                painter.drawText(option.rect, alignment, elided_text)


class TrackTableView(QTableView):
    set_new_tracks = pyqtSignal()
    play_now_triggered = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks: List[Track] = []
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        self._table_model = TrackTableModel(self)
        # self.setSelectionModel(QItemSelectionModel())
        self._table_delegate = TrackTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)
        # self.clicked.connect(lambda index: print(index.row()))

        self.context_menu = QMenu(self)
        self.context_menu.setContentsMargins(0, 0, 0, 0)
        self.play_now_action = QAction("Play Now", self)
        self.play_now_action.triggered.connect(lambda event: self.play_now_action_triggered(event))
        self.context_menu.addAction(self.play_now_action)


    # def eventFilter(self, source: QTableView, event) -> bool:
    #     if event.type() == QEvent.Type.ContextMenu and source is self:
    #         menu = QMenu()
    #         menu.addAction('Action 1')
    #         menu.addAction('Action 2')
    #         menu.addAction('Action 3')
    #
    #         if menu.exec(event.globalPos()):
    #             item = source.itemAt(event.pos())
    #             print(item.text())
    #         return True
    #     return super().eventFilter(source, event)

    def contextMenuEvent(self, event):
        # self.menu = QMenu(self)
        # renameAction = QAction('Rename', self)
        # renameAction.triggered.connect(lambda: self.play_now_action_triggered(event))
        # self.menu.addAction(renameAction)
        # add other required actions
        self.context_menu.popup(QtGui.QCursor.pos())

    def play_now_action_triggered(self, event):
        self.selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        # print(self.selected_track_indexes)
        # print([self._tracks[i] for i in self.selected_track_indexes])
        self.play_now_triggered.emit([self._tracks[i] for i in self.selected_track_indexes])

    def set_tracks(self, tracks: List[Track]) -> None:
        self._tracks = tracks
        self._table_model.set_tracks(tracks)
        self.set_new_tracks.emit()

    def set_playing_track_index(self, index: Optional[int]) -> None:
        self._table_model.set_playing_track_index(index)

    def set_paused(self) -> None:
        self._table_model.set_paused()

    def set_unpaused(self) -> None:
        self._table_model.set_unpaused()

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        if QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton:
            self.clearSelection()
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        return super().focusOutEvent(event)


class TestMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget()

        self.vbox = QVBoxLayout(self.widget)

        self.table_view = TrackTableView(self)

        self.table_view.horizontalHeader().setMinimumSectionSize(20)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.setStyleSheet(SELECTION_STYLESHEET)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        start = time.time()
        self.table_view.set_tracks(TracksRepository().get_tracks_by("album", None))
        print(f"Test loaded in: {time.time() - start:.6f} s")

        self.vbox.addWidget(self.table_view)
        self.vbox.addWidget(QPushButton())

        self.setCentralWidget(self.widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = TestMainWindow()
    mainWindow.show()
    sys.exit(app.exec())
