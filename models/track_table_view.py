from __future__ import annotations

import sys
from typing import List, Optional, Any

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QFontMetrics, QAction, QKeySequence, QShortcut
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import QApplication, QTableView, QAbstractItemView, QHeaderView, QStyleOptionViewItem, QStyle, \
    QStyledItemDelegate, QMenu, QVBoxLayout, QPushButton, QWidget, QStyleOptionHeader, QFrame

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
                    print("Got artwork pixmap:", index.row())
                    track.artwork_pixmap = new_pixmap if new_pixmap else ""
                    artwork_pixmap = track.artwork_pixmap
                if not artwork_pixmap:
                    return None
                return artwork_pixmap
                    # .scaled(self._table_view.columnWidth(index.column()),
                    #                          self._table_view.columnWidth(index.column()),
                    #                          Qt.AspectRatioMode.IgnoreAspectRatio,
                    #                          Qt.TransformationMode.SmoothTransformation)
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

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: QtCore.Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # print(f"Got data:", section)
                return MAIN_PANEL_COLUMN_NAMES[section]
            return f"{section}"
        return None

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


class TrackTableItemDelegate(QStyledItemDelegate):  # TODO optimize pixmap drawing speed
    def __init__(self, parent: TrackTableView = None):
        super().__init__(parent)
        self._table_view: TrackTableView = parent
        self.last_height = self._table_view.height()

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

        if index.data(Qt.ItemDataRole.DisplayRole):
            painter.setPen(QPen(Qt.GlobalColor.black))
            text = f"{index.data(Qt.ItemDataRole.DisplayRole)}"
            if text:
                elided_text = QFontMetrics(option.font).elidedText(str(text), Qt.TextElideMode.ElideRight,
                                                                   option.rect.width())
                alignment = Qt.AlignmentFlag.AlignVCenter if index.column() else Qt.AlignmentFlag.AlignCenter

                # padding = 4
                option.rect.setLeft(option.rect.left() + self._table_view.padding)
                painter.drawText(option.rect, alignment, elided_text)

        # if self.last_height == self._table_view.height():
        #     return
        # else:
        #     self.last_height = self._table_view.height()


        if index.data(Qt.ItemDataRole.DecorationRole):
            pixmap = index.data(Qt.ItemDataRole.DecorationRole)
            rect = option.rect
            rect.setRect(rect.left() + 1, rect.top() + 1,
                         rect.width() - 2, rect.height() - 2)

            if index.column() == 1:
                height = rect.height()
                rect.setHeight(rect.width())
                rect.translate(0, (height - rect.width()) / 2)

            pixmap = pixmap.scaled(rect.width(), rect.height(),
                                   Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            # print("Painted pixmap")

            painter.drawPixmap(rect, pixmap)


class TrackTableHeader(QHeaderView):
    def __init__(self, orientation: Qt.Orientation, parent: TrackTableView = None):
        super().__init__(orientation, parent)
        self.padding = parent.padding
        self.setSectionsClickable(True)
        self.setSortIndicatorShown(True)
        self.setSectionsMovable(True)
        self.setFirstSectionMovable(False)

        self.section_text = MAIN_PANEL_COLUMN_NAMES

    def text(self, section: int):
        if isinstance(self.model(), QtCore.QAbstractItemModel):
            return self.section_text[section]

    def initStyleOptionForIndex(self, option: QStyleOptionHeader, section_index: int) -> None:
        text = self.section_text[section_index]
        elided_text: str = self.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, self.sectionSize(section_index))
        option.text = elided_text
        # print(section_index, option.text, self.sectionSize(section_index))
        super().initStyleOptionForIndex(option, section_index)

    # def paintSection(self, painter: QtGui.QPainter, rect: QtCore.QRect, logicalIndex: int) -> None:
    #     elided_text: str = QFontMetrics(self.font()).elidedText(self.text(logicalIndex), Qt.TextElideMode.ElideRight,
    #                                                             self.sectionSize(logicalIndex))
    #     rect.setLeft(rect.left() + self.padding)
    #     painter.drawText(rect, Qt.AlignmentFlag.AlignLeft, elided_text)


class TrackTableView(QTableView):
    set_new_tracks = pyqtSignal()
    play_now_triggered = pyqtSignal(list)
    output_to_triggered = pyqtSignal(str)
    queue_next_triggered = pyqtSignal(list)
    queue_last_triggered = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks: List[Track] = []

        self.padding = 4

        self._table_model = TrackTableModel(self)
        self._table_delegate = TrackTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)
        self._table_header = TrackTableHeader(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(self._table_header)

        self.horizontalHeader().setStyleSheet(f"QHeaderView::item {{padding {self.padding};}}")
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self._setup_context_menu()

    def _setup_context_menu(self):
        self.context_menu = QMenu(self)
        self.context_menu.setContentsMargins(0, 0, 0, 0)

        self.play_now_action = QAction("Play Now", self)
        self.play_now_shortcut_enter = QShortcut(QKeySequence("Alt+Enter"), self)
        self.play_now_shortcut_enter.activated.connect(self.play_now_action_triggered)
        self.play_now_shortcut_enter.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.play_now_shortcut_return = QShortcut(QKeySequence("Alt+Return"), self)
        self.play_now_shortcut_return.activated.connect(self.play_now_action_triggered)
        self.play_now_shortcut_return.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.play_now_action.setShortcut(QKeySequence("Alt+Enter"))

        self.play_now_action.triggered.connect(lambda event: self.play_now_action_triggered(event))
        self.context_menu.addAction(self.play_now_action)

        self.queue_next_action = QAction("Queue Next", self)
        self.queue_next_action.triggered.connect(lambda event: self.queue_next_action_triggered(event))
        self.context_menu.addAction(self.queue_next_action)

        self.queue_last_action = QAction("Queue Last", self)
        self.queue_last_action.triggered.connect(lambda event: self.queue_last_action_triggered(event))
        self.context_menu.addAction(self.queue_last_action)

        self.play_more_menu = self.context_menu.addMenu("Play More...")
        self.output_to_menu = self.play_more_menu.addMenu("Output To")

        self.audio_output_actions = []
        for audio_output in (a.description() for a in QMediaDevices.audioOutputs()):
            action = QAction(audio_output, self)
            action.triggered.connect(lambda _: self.output_to_action_triggered())
            self.output_to_menu.addAction(action)

    @pyqtSlot()
    def output_to_action_triggered(self) -> None:
        audio_output = self.sender().text()
        print()
        self.output_to_triggered.emit(audio_output)

    def contextMenuEvent(self, event):
        self.context_menu.popup(QtGui.QCursor.pos())

    def play_now_action_triggered(self, e=None):
        print("play")
        if not self._tracks:
            return

        print(e)
        selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        self.play_now_triggered.emit([self._tracks[i] for i in selected_track_indexes])

    def queue_next_action_triggered(self, _=None):
        if not self._tracks:
            return
        selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        self.queue_next_triggered.emit([self._tracks[i] for i in selected_track_indexes])

    def queue_last_action_triggered(self, _=None):
        if not self._tracks:
            return
        selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        self.queue_last_triggered.emit([self._tracks[i] for i in selected_track_indexes])

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
        # self.table_view.horizontalHeader().setVisible(False)

        self.table_view.setShowGrid(False)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setFrameShape(QFrame.Shape.NoFrame)

        # self.view = QTableView(self)
        # self.view.setModel(self.tableModel)
        # self.table_view.horizontalHeader().setResizeMode(QHeaderView.Interactive)
        # Added these two lines
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.horizontalHeader().setStretchLastSection(True)

        # start = time.time()
        self.table_view.set_tracks(TracksRepository().get_tracks_by("album", None))
        # print(f"Test loaded in: {time.time() - start:.6f} s")

        self.vbox.addWidget(self.table_view)
        self.vbox.addWidget(QPushButton())

        self.setCentralWidget(self.widget)

        # ===== ADDITION

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Mode set to Interactive to allow resizing
        self.table_view.horizontalHeader().setMinimumSectionSize(10)

        hide_button = QPushButton('Hide Column')
        hide_button.clicked.connect(self.hide_column)

        unhide_button = QPushButton('Unhide Column')
        unhide_button.clicked.connect(self.unhide_column)

    def hide_column(self):
        self.table_view.model().setColumnCount(1)

    def unhide_column(self):
        self.table_view.model().setColumnCount(10)

    # Added a reimplementation of the resize event
    def resizeEvent(self, event):
        super().resizeEvent(event)
        table_size = self.table_view.width()
        side_header_width = self.table_view.verticalHeader().width()
        table_size -= side_header_width
        number_of_columns = self.table_view.model().columnCount()

        remaining_width = table_size % number_of_columns
        for column_num in range(self.table_view.model().columnCount()):
            if remaining_width > 0:
                self.table_view.setColumnWidth(column_num, int(table_size / number_of_columns) + 1)
                remaining_width -= 1
            else:
                self.table_view.setColumnWidth(column_num, int(table_size / number_of_columns))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = TestMainWindow()
    mainWindow.show()
    sys.exit(app.exec())
