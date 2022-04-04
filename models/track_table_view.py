from __future__ import annotations

import sys
from typing import List, Optional, Any

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QFontMetrics, QAction, QKeySequence, QShortcut
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import (QApplication, QTableView, QAbstractItemView, QHeaderView, QStyleOptionViewItem, QStyle,
                             QStyledItemDelegate, QMenu, QVBoxLayout, QPushButton, QWidget, QFrame)

from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import get_artwork_pixmap, get_formatted_time_in_mins


class TrackTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self._tracks: List[Track] = []
        self.is_playing = False
        self.playing_track_index: Optional[int] = None

        self.playing_speaker_pixmap = QPixmap("icons/speaker_playing.png")

        self.muted_speaker_pixmap = QPixmap("icons/speaker_muted.png")

        self.data_called = 0
        self.last_index = QModelIndex()
        self.last_index_called = 0

    @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self.layoutAboutToBeChanged.emit()
        self._tracks = tracks
        self.layoutChanged.emit()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self._tracks:
            return None
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                track = self._tracks[index.row()]
                artwork_pixmap = track.artwork_pixmap
                if artwork_pixmap is None:
                    new_pixmap = get_artwork_pixmap(track.file_path)
                    track.artwork_pixmap = new_pixmap if new_pixmap else ""
                    artwork_pixmap = track.artwork_pixmap
                if not artwork_pixmap:
                    return None
                return artwork_pixmap.scaled(self._table_view.columnWidth(index.column()),
                                             self._table_view.columnWidth(index.column()),
                                             Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
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
                return get_formatted_time_in_mins(self._tracks[index.row()].length)
            return getattr(self._tracks[index.row()], value) if value else None

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self._tracks)

    def columnCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(MAIN_PANEL_COLUMN_NAMES)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: QtCore.Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return MAIN_PANEL_COLUMN_NAMES[section]
            return f"{section}"
        return None

    @pyqtSlot()
    def set_paused(self) -> None:
        self.is_playing = False
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(self.playing_track_index, 1), self.index(self.playing_track_index, 1))

    @pyqtSlot()
    def set_unpaused(self) -> None:
        self.is_playing = True
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(self.playing_track_index, 1), self.index(self.playing_track_index, 1))

    @pyqtSlot(int)
    def set_playing_track_index(self, index: Optional[int]) -> None:
        self.playing_track_index = index
        self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))


class TrackTableItemDelegate(QStyledItemDelegate):  # TODO optimize pixmap drawing speed
    def __init__(self, parent: TrackTableView = None):
        super().__init__(parent)
        self.padding = parent.padding
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
        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))

        display_role = index.data(Qt.ItemDataRole.DisplayRole)
        decoration_role = index.data(Qt.ItemDataRole.DecorationRole)
        if display_role:
            painter.setPen(QPen(Qt.GlobalColor.black))
            text = f"{display_role}"
            if text:
                elided_text = QFontMetrics(option.font).elidedText(str(text), Qt.TextElideMode.ElideRight,
                                                                   max(option.rect.width() - self.padding * 2, 18))

                if index.column():
                    alignment = Qt.AlignmentFlag.AlignVCenter
                    if index.column() == len(MAIN_PANEL_COLUMN_NAMES) - 1:
                        alignment = Qt.AlignmentFlag.AlignRight
                else:
                    alignment = Qt.AlignmentFlag.AlignCenter

                option.rect.setLeft(option.rect.left() + self.padding)
                option.rect.setRight(option.rect.right() - self.padding)
                painter.drawText(option.rect, alignment, elided_text)

        if decoration_role:
            pixmap = decoration_role
            rect = option.rect
            rect.setRect(rect.left() + 1, rect.top() + 1,
                         rect.width() - 2, rect.height() - 2)

            if index.column() == 1:
                height = rect.height()
                width = rect.width()
                rect.setHeight(width)
                rect.translate(0, (height - width) / 2)

                pixmap = pixmap.scaled(width, width,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(rect, pixmap)


class TrackTableHeader(QHeaderView):
    def __init__(self, orientation: Qt.Orientation, parent: TrackTableView = None):
        super().__init__(orientation, parent)
        self.padding = parent.padding
        self.setSectionsClickable(True)
        self.setSortIndicatorShown(True)
        self.setSectionsMovable(True)
        self.setFirstSectionMovable(False)

        self.sectionMoved.connect(self.section_moved)
        self.sectionResized.connect(self.section_resized)
        self.__section_moved_recursions = 0

        self.section_text = MAIN_PANEL_COLUMN_NAMES

        self.minimum_last_section_size = self.padding * 2 + self.fontMetrics().horizontalAdvance("Time")

        self.setStyleSheet("""
        QHeaderView {
        border-bottom: 1px solid gray;
        border-top: 0px;
        border-right: 0px;
        border-left: 0px;
        }
        """)

    @pyqtSlot(int, int, int)
    def section_resized(self, logical_index: int, old_size: int, new_size: int) -> None:
        """Sets minimum size for the last section."""
        if logical_index == self.count() - 1 and new_size < self.minimum_last_section_size:
            self.resizeSection(self.count() - 1, self.minimum_last_section_size)

    @pyqtSlot(int, int, int)
    def section_moved(self, logical_index: int, old_visual_index: int, new_visual_index: int) -> None:
        """Prevents section 1 from moving."""
        if self.__section_moved_recursions:
            self.__section_moved_recursions = 0
            return
        if {0, 1} & {old_visual_index, new_visual_index}:
            self.__section_moved_recursions += 1
            self.moveSection(new_visual_index, old_visual_index)

    def text(self, section: int):
        if isinstance(self.model(), QtCore.QAbstractItemModel):
            return self.section_text[section]

    def paintSection(self, painter: QtGui.QPainter, rect: QtCore.QRect, logical_index: int) -> None:
        elided_text: str = QFontMetrics(self.font()).elidedText(self.text(logical_index),
                                                                Qt.TextElideMode.ElideRight,
                                                                self.sectionSize(logical_index) - self.padding)

        top = rect.topRight()
        top.setY(top.y() + 1)
        bottom = rect.bottomRight()
        bottom.setY(bottom.y() - 2)

        painter.setPen(Qt.GlobalColor.gray)
        painter.drawLine(top, bottom)

        painter.setPen(Qt.GlobalColor.black)
        rect.setLeft(rect.left() + self.padding)
        rect.setRight(rect.right() - self.padding)

        if logical_index == self.count() - 1:
            painter.drawText(rect, Qt.AlignmentFlag.AlignRight, elided_text)
        else:
            painter.drawText(rect, Qt.AlignmentFlag.AlignLeft, elided_text)


class TrackTableView(QTableView):
    new_tracks_set = pyqtSignal()
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
        self.setTextElideMode(Qt.TextElideMode.ElideRight)

        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self._setup_context_menu()
        self._setup_shortcuts()

    def _setup_context_menu(self):
        self.context_menu = QMenu(self)
        self.context_menu.setContentsMargins(0, 0, 0, 0)

        self.play_now_action = QAction("Play Now", self)
        self.play_now_action.setShortcut(QKeySequence("Alt+Enter"))
        self.play_now_action.triggered.connect(lambda event: self.play_now_action_triggered(event))
        self.context_menu.addAction(self.play_now_action)

        self.queue_next_action = QAction("Queue Next", self)
        self.queue_next_action.setShortcut(QKeySequence("Ctrl+Shift+Enter"))
        self.queue_next_action.triggered.connect(lambda event: self.queue_next_action_triggered(event))
        self.context_menu.addAction(self.queue_next_action)

        self.queue_last_action = QAction("Queue Last", self)
        self.queue_last_action.setShortcut(QKeySequence("Ctrl+Enter"))
        self.queue_last_action.triggered.connect(lambda event: self.queue_last_action_triggered(event))
        self.context_menu.addAction(self.queue_last_action)

        self.play_more_menu = self.context_menu.addMenu("Play More...")
        self.output_to_menu = self.play_more_menu.addMenu("Output To")

        self.audio_output_actions = []
        for audio_output in ["Primary Sound Driver", *[a.description() for a in QMediaDevices.audioOutputs()]]:
            action = QAction(audio_output, self)
            action.triggered.connect(lambda _: self.output_to_action_triggered())
            self.output_to_menu.addAction(action)

    def _setup_shortcuts(self):
        self.play_now_shortcut_enter = QShortcut(QKeySequence("Alt+Enter"), self)
        self.play_now_shortcut_enter.activated.connect(self.play_now_action_triggered)
        self.play_now_shortcut_enter.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.play_now_shortcut_return = QShortcut(QKeySequence("Alt+Return"), self)
        self.play_now_shortcut_return.activated.connect(self.play_now_action_triggered)
        self.play_now_shortcut_return.setContext(Qt.ShortcutContext.WidgetShortcut)

        self.queue_next_shortcut_enter = QShortcut(QKeySequence("Ctrl+Shift+Enter"), self)
        self.queue_next_shortcut_enter.activated.connect(self.queue_next_action_triggered)
        self.queue_next_shortcut_enter.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.queue_next_shortcut_return = QShortcut(QKeySequence("Ctrl+Shift+Return"), self)
        self.queue_next_shortcut_return.activated.connect(self.queue_next_action_triggered)
        self.queue_next_shortcut_return.setContext(Qt.ShortcutContext.WidgetShortcut)

        self.queue_last_shortcut_enter = QShortcut(QKeySequence("Ctrl+Enter"), self)
        self.queue_last_shortcut_enter.activated.connect(self.queue_last_action_triggered)
        self.queue_last_shortcut_enter.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.queue_last_shortcut_return = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.queue_last_shortcut_return.activated.connect(self.queue_last_action_triggered)
        self.queue_last_shortcut_return.setContext(Qt.ShortcutContext.WidgetShortcut)

    @pyqtSlot()
    def output_to_action_triggered(self) -> None:
        audio_output = self.sender().text()
        self.output_to_triggered.emit(audio_output)

    def contextMenuEvent(self, event):
        self.context_menu.popup(QtGui.QCursor.pos())

    def play_now_action_triggered(self, e=None):
        if not self._tracks:
            return

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

    @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self._tracks = tracks
        self._table_model.set_tracks(tracks)
        self.new_tracks_set.emit()

    @pyqtSlot(int)
    def set_playing_track_index(self, index: Optional[int]) -> None:
        self._table_model.set_playing_track_index(index)

    @pyqtSlot()
    def set_paused(self) -> None:
        self._table_model.set_paused()

    @pyqtSlot()
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

        self.setMinimumHeight(100)
        self.resize(self.width(), 500)

        self.widget = QWidget()

        self.vbox = QVBoxLayout(self.widget)

        self.table_view = TrackTableView(self)

        self.table_view.horizontalHeader().setMinimumSectionSize(20)
        self.table_view.verticalHeader().setVisible(False)
        # self.table_view.horizontalHeader().setVisible(False)

        self.table_view.setShowGrid(False)
        self.table_view.horizontalHeader().setMinimumSectionSize(4)
        self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.table_view.verticalHeader().setOffset(-20)
        # print(self.table_view.verticalOffset())
        self.table_view.verticalHeader().setVisible(False)
        # self.table_view.horizontalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table_view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table_view.setIconSize(QSize(22, 22))
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setFrameShape(QFrame.Shape.NoFrame)

        first_col_width = 26
        second_col_width = 20
        rating_col_width = 50

        self.table_view.setColumnWidth(0, first_col_width)
        self.table_view.setColumnWidth(1, second_col_width)
        self.table_view.setColumnWidth(7, rating_col_width)
        self.table_view.horizontalHeader().resizeSection(0, first_col_width)
        self.table_view.horizontalHeader().resizeSection(1, second_col_width)
        self.table_view.horizontalHeader().resizeSection(7, rating_col_width)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        # self.view = QTableView(self)
        # self.view.setModel(self.tableModel)
        # self.table_view.horizontalHeader().setResizeMode(QHeaderView.Interactive)
        # Added these two lines
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.table_view.horizontalHeader().setStretchLastSection(True)

        # start = time.time()
        # self.table_view.set_tracks(TracksRepository().get_tracks_by("album", None))
        # print(f"Test loaded in: {time.time() - start:.6f} s")

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)

        self.vbox.addWidget(self.table_view)
        self.vbox.addWidget(self.refresh_button)

        self.setCentralWidget(self.widget)

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setMinimumSectionSize(10)
        self.tracks = TracksRepository().get_tracks_by("album", None)

        self.counter = 1

    def refresh(self):
        self.table_view.set_tracks(self.tracks[:self.counter * 30])
        self.table_view.scrollToTop()
        self.counter += 1
        # print(self.counter)
        # print("Refreshed!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = TestMainWindow()
    mainWindow.show()
    sys.exit(app.exec())
