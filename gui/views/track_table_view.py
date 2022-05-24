from __future__ import annotations

import sys
import typing
from typing import List, Optional, Any, Union

from PyQt6.QtCore import (QModelIndex, pyqtSignal, pyqtSlot, QSize, QAbstractItemModel, QRect, QAbstractTableModel, Qt,
                          QSortFilterProxyModel)
from PyQt6.QtGui import (QPixmap, QPainter, QPen, QBrush, QFontMetrics, QAction, QKeySequence, QShortcut,
                         QContextMenuEvent, QFocusEvent, QMouseEvent, QCursor, QColor)
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import (QApplication, QTableView, QAbstractItemView, QHeaderView, QStyleOptionViewItem, QStyle,
                             QStyledItemDelegate, QMenu, QVBoxLayout, QPushButton, QWidget, QFrame, QMainWindow,
                             QAbstractScrollArea, QDialog)

from constants import MAIN_PANEL_COLUMN_NAMES, SELECTION_QCOLOR, LOST_FOCUS_QCOLOR, ROOT
from data_models.track import Track
from gui.dialogs.delete_track_dialog import DeleteTracksDialog
from gui.star.star_delegate import StarDelegate
from gui.star.star_rating import StarRating
from repositories.tracks_repository import TracksRepository
from utils import get_formatted_time_in_mins


class TrackTableHeader(QHeaderView):
    def __init__(self, orientation: Qt.Orientation, track_table_view: TrackTableView = None):
        super().__init__(orientation, track_table_view)
        self.padding = track_table_view.padding
        self.setSectionsClickable(True)
        self.setSortIndicatorShown(True)
        self.setSectionsMovable(True)
        self.setFirstSectionMovable(False)
        self.setSortIndicatorShown(True)

        self.sortIndicatorChanged.connect(self.sort_indicator_changed)
        self.sectionMoved.connect(self.section_moved)
        self.sectionResized.connect(self.section_resized)
        self.__section_moved_recursions = 0

        self.section_text = MAIN_PANEL_COLUMN_NAMES

        self.minimum_last_section_size = self.padding * 2 + self.fontMetrics().horizontalAdvance(self.section_text[-1])

        self.setStyleSheet("""
        QHeaderView {
        border-bottom: 1px solid gray;
        border-top: 0px;
        border-right: 0px;
        border-left: 0px;
        }
        """)

    @pyqtSlot(int, int, int)
    def section_resized(self, logical_index: int, _: int, new_size: int) -> None:
        """Sets minimum size for the last section."""
        if logical_index == self.count() - 1 and new_size < self.minimum_last_section_size:
            self.resizeSection(self.count() - 1, self.minimum_last_section_size)

    @pyqtSlot(int, int, int)
    def section_moved(self, _: int, old_visual_index: int, new_visual_index: int) -> None:
        """Prevents section 1 from moving."""
        if self.__section_moved_recursions:
            self.__section_moved_recursions = 0
            return
        if {0, 1} & {old_visual_index, new_visual_index}:
            self.__section_moved_recursions += 1
            self.moveSection(new_visual_index, old_visual_index)

    @pyqtSlot(int, Qt.SortOrder)
    def sort_indicator_changed(self, logical_index: int, order: Qt.SortOrder) -> None:
        self.setSortIndicator(logical_index, order)

    def text(self, section: int):
        if isinstance(self.model(), QAbstractItemModel):
            return self.section_text[section]

    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:
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


class TrackTableModel(QAbstractTableModel):
    def __init__(self, parent: TrackTableView = None):
        super().__init__(parent)
        self._table_view: TrackTableView = parent
        self.tracks: List[Track] = []
        self.is_playing = False
        self.playing_track_index: Optional[int] = None

        self.playing_speaker_pixmap = QPixmap(f"{ROOT}/icons/speaker-playing.png")
        self.muted_speaker_pixmap = QPixmap(f"{ROOT}/icons/speaker-not-playing.png")

        self.general_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self.layoutAboutToBeChanged.emit()
        self.tracks = tracks
        self.layoutChanged.emit()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self.tracks or index.row() >= len(self.tracks):
            return None
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                track = self.tracks[index.row()]
                artwork_pixmap: Optional[QPixmap] = track.artwork_pixmap
                if not artwork_pixmap or artwork_pixmap.isNull():
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
                return self.tracks[index.row()].length
            elif value == "rating":
                return StarRating(self.tracks[index.row()].rating)

            return getattr(self.tracks[index.row()], value) if value else None

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self.tracks)

    def columnCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(MAIN_PANEL_COLUMN_NAMES)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return MAIN_PANEL_COLUMN_NAMES[section]
            return f"{section}"
        return None

    def flags(self, index: QModelIndex):
        if index.column() == self._table_view.rating_column:
            return self.general_flags | Qt.ItemFlag.ItemIsEditable
        return self.general_flags

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> bool:
        if isinstance(value, StarRating):
            self.tracks[index.row()].rating = value.star_count()

        return super().setData(index, value, role)

    @pyqtSlot()
    def set_paused(self) -> None:
        self.is_playing = False
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))

    @pyqtSlot()
    def set_unpaused(self) -> None:
        self.is_playing = True
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))

    @pyqtSlot(int)
    def set_playing_track_index(self, index: Optional[int]) -> None:
        self.playing_track_index = index
        self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))

    def delete_tracks(self, tracks: List[Track]) -> None:
        for track in self.tracks.copy():
            if track in tracks:
                self.tracks.remove(track)
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))


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
            else:
                fill_color = LOST_FOCUS_QCOLOR
            painter.setBrush(fill_color)
            painter.drawRect(option.rect)
        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))

        display_role: Union[str, int] = index.data(Qt.ItemDataRole.DisplayRole)
        decoration_role: QPixmap = index.data(Qt.ItemDataRole.DecorationRole)
        if display_role:
            if MAIN_PANEL_COLUMN_NAMES[index.column()].lower() == "time":
                display_role = get_formatted_time_in_mins(display_role)

            if option.state & QStyle.StateFlag.State_Selected and self._table_view.hasFocus():
                painter.setPen(QColor(option.palette.highlightedText()))
            else:
                painter.setPen(QColor(option.palette.text()))
            text = f"{display_role}"
            if text:
                elided_text = QFontMetrics(option.font).elidedText(str(text), Qt.TextElideMode.ElideRight,
                                                                   max(option.rect.width() - self.padding * 2, 18))

                if index.column():
                    alignment = Qt.AlignmentFlag.AlignVCenter
                    if index.column() == len(MAIN_PANEL_COLUMN_NAMES) - 1:
                        alignment |= Qt.AlignmentFlag.AlignRight
                else:
                    alignment = Qt.AlignmentFlag.AlignCenter

                option.rect.setLeft(option.rect.left() + self.padding)
                option.rect.setRight(option.rect.right() - self.padding)
                painter.drawText(option.rect, alignment, elided_text)

        if decoration_role and not decoration_role.isNull():
            pixmap = decoration_role
            rect = option.rect
            rect.setRect(rect.left() + 1, rect.top() + 1,
                         rect.width() - 2, rect.height() - 2)

            if index.column() == 1:
                height = rect.height()
                width = rect.width()
                rect.setHeight(width)
                rect.translate(0, (height - width) // 2)

                pixmap = pixmap.scaled(width, width,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(rect, pixmap)


class TrackTableSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, table_view: TrackTableView, *args, **kwargs):
        super().__init__(table_view, *args, **kwargs)
        self._sort_order = Qt.SortOrder.AscendingOrder
        self._sort_key = None
        self._source_model: Optional[TrackTableModel] = None
        self._table_view = table_view

    def setSourceModel(self, source_model: TrackTableModel) -> None:
        self._source_model = source_model
        self._source_model.dataChanged.connect(self.dataChanged.emit)
        self._source_model.layoutAboutToBeChanged.connect(self.layoutAboutToBeChanged.emit)
        self._source_model.layoutChanged.connect(self.layoutChanged.emit)
        super().setSourceModel(source_model)

    def sort(self, column: int, _: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        if column not in (0, 1):
            self._sort_key = MAIN_PANEL_COLUMN_NAMES[column].lower()
            if self._sort_key == "time":
                self._sort_key = "length"
            self._source_model.layoutAboutToBeChanged.emit()
            if self._sort_order == Qt.SortOrder.AscendingOrder:
                self._sort_order = Qt.SortOrder.DescendingOrder
                self._source_model.tracks.sort(key=self._sort_func)

            else:
                self._sort_order = Qt.SortOrder.AscendingOrder
                self._source_model.tracks.sort(key=self._sort_func, reverse=True)

            self._table_view._tracks = self._source_model.tracks
            self._source_model.set_playing_track_index(self._table_view.get_playing_track_index())

        self.layoutChanged.emit()
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def _sort_func(self, track: Track) -> Any:
        output = getattr(track, self._sort_key)
        if output is None and self._sort_key not in ("year", "length"):
            return ""
        elif output is None:
            return 0
        elif self._sort_key in ("year", "length"):
            return output
        else:
            return str(output)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        return self.sourceModel().data(index, role)


class TrackTableView(QTableView):
    new_tracks_set = pyqtSignal()
    play_now_triggered = pyqtSignal(list)
    output_to_triggered = pyqtSignal(str)
    queue_next_triggered = pyqtSignal(list)
    queue_last_triggered = pyqtSignal(list)
    tracks_deleted = pyqtSignal(list)
    track_clicked = pyqtSignal(Track, int)
    track_double_clicked = pyqtSignal(Track, int)

    def __init__(self, *args):
        super().__init__(*args)
        self._tracks: List[Track] = []
        self.playing_track = None

        self.padding = 4
        self.rating_column = 7
        self.prev_index = QModelIndex()

        self._table_model = TrackTableModel(self)
        self._table_delegate = TrackTableItemDelegate(self)
        self._star_delegate = StarDelegate(self)
        self._table_header = TrackTableHeader(Qt.Orientation.Horizontal, self)
        self._table_header.sectionClicked.connect(self.header_section_clicked)
        self.clicked.connect(self.row_clicked)
        self.doubleClicked.connect(self.row_double_clicked)

        self._proxy_sort_model = TrackTableSortFilterProxyModel(self)
        self._proxy_sort_model.setSourceModel(self._table_model)

        self.setModel(self._proxy_sort_model)
        self.setItemDelegate(self._table_delegate)
        self.setItemDelegateForColumn(7, self._star_delegate)
        self.setHorizontalHeader(self._table_header)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)

        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self._setup_context_menu()
        self._setup_shortcuts()

    def row_double_clicked(self, model_index: QModelIndex) -> None:
        playing_track_index = model_index.row()
        self.playing_track = self._tracks[playing_track_index]
        self.track_double_clicked.emit(self.playing_track, playing_track_index)

    def row_clicked(self, model_index: QModelIndex) -> None:
        index = model_index.row()
        track = self._tracks[index]
        self.track_clicked.emit(track, index)

    def header_section_clicked(self, logical_index: int) -> None:
        if logical_index not in (0, 1):
            # selected_tracks = self.get_selected_tracks()
            self.sortByColumn(logical_index, Qt.SortOrder.AscendingOrder)
            self.clearSelection()
            # self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

            # for t in selected_tracks:
            #     self.selectRow(self._tracks.index(t))
            #     print("SELECTED ROW:", self._tracks.index(t))
            # self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def get_selected_tracks(self) -> List[Track]:
        tracks = []
        for i in self.selectedIndexes():
            tracks.append(self._tracks[i.row()])
        return tracks

    def get_playing_track_index(self) -> Optional[int]:
        try:
            return self._tracks.index(self.playing_track)
        except ValueError:
            return None

    def _setup_context_menu(self):
        self.context_menu = QMenu(self)
        self.context_menu.setContentsMargins(0, 0, 0, 0)

        self.play_now_action = QAction("Play Now", self)
        self.play_now_action.setShortcut(QKeySequence("Alt+Enter"))
        self.play_now_action.triggered.connect(self.play_now_action_triggered)
        self.context_menu.addAction(self.play_now_action)

        self.queue_next_action = QAction("Queue Next", self)
        self.queue_next_action.setShortcut(QKeySequence("Ctrl+Shift+Enter"))
        self.queue_next_action.triggered.connect(self.queue_next_action_triggered)
        self.context_menu.addAction(self.queue_next_action)

        self.queue_last_action = QAction("Queue Last", self)
        self.queue_last_action.setShortcut(QKeySequence("Ctrl+Enter"))
        self.queue_last_action.triggered.connect(self.queue_last_action_triggered)
        self.context_menu.addAction(self.queue_last_action)

        self.play_more_menu = self.context_menu.addMenu("Play More...")
        self.output_to_menu = self.play_more_menu.addMenu("Output To")

        self.audio_output_actions = []
        for audio_output in ["Primary Sound Driver", *[a.description() for a in QMediaDevices.audioOutputs()]]:
            action = QAction(audio_output, self)
            action.triggered.connect(lambda _: self.output_to_action_triggered())
            self.output_to_menu.addAction(action)

        self.context_menu.addSeparator()

        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence("Del"))
        self.delete_action.triggered.connect(self.delete_action_triggered)
        self.context_menu.addAction(self.delete_action)

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

        self.delete_shortcut = QShortcut(QKeySequence("Del"), self)
        self.delete_shortcut.activated.connect(self.delete_action_triggered)
        self.delete_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)

    def selectionChanged(self, selected, deselected) -> None:
        for index in deselected.indexes():
            if index.column() == self.rating_column:
                typing.cast(StarDelegate, self.itemDelegateForColumn(self.rating_column)).commit_and_close_editor(index)
        for index in selected.indexes():
            if index.column() == self.rating_column:
                self.openPersistentEditor(index)

        super().selectionChanged(selected, deselected)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        super().mousePressEvent(e)
        index = self.indexAt(e.pos())
        if index.column() == self.rating_column and index not in self.selectedIndexes():
            self.openPersistentEditor(index)
        self.prev_index = index

    def contextMenuEvent(self, e: QContextMenuEvent) -> None:
        self.context_menu.popup(QCursor.pos())

    @pyqtSlot()
    def output_to_action_triggered(self) -> None:
        audio_output = self.sender().text()
        self.output_to_triggered.emit(audio_output)

    def play_now_action_triggered(self) -> None:
        if not self._tracks:
            return

        selected_track_indexes = sorted(set([i.row() for i in self.selectionModel().selection().indexes()]))
        self.play_now_triggered.emit([self._tracks[i] for i in selected_track_indexes])

    def queue_next_action_triggered(self) -> None:
        if not self._tracks:
            return
        selected_track_indexes = sorted(set([i.row() for i in self.selectionModel().selection().indexes()]))
        print(selected_track_indexes)
        self.queue_next_triggered.emit([self._tracks[i] for i in selected_track_indexes])

    def queue_last_action_triggered(self) -> None:
        if not self._tracks:
            return
        selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        self.queue_last_triggered.emit([self._tracks[i] for i in selected_track_indexes])

    def delete_action_triggered(self) -> None:
        selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        selected_tracks = [self._tracks[i] for i in selected_track_indexes]
        d = DeleteTracksDialog(selected_tracks)
        code = d.exec()
        if code == QDialog.DialogCode.Accepted:
            self._table_model.delete_tracks(selected_tracks)
            self.tracks_deleted.emit(selected_tracks)

        self.selectRow(sorted(selected_track_indexes)[0])

    @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        for index in self.selectedIndexes():
            if index.column() == self.rating_column:
                self._star_delegate.commit_and_close_editor(index)
        self.clearSelection()
        self._tracks = tracks
        self._table_model.set_tracks(tracks)
        self.new_tracks_set.emit()

    @pyqtSlot(int)
    def set_playing_track_index(self, index: Optional[int]) -> None:
        self.playing_track_index = index
        self._table_model.set_playing_track_index(index)

    @pyqtSlot()
    def set_paused(self) -> None:
        self._table_model.set_paused()

    @pyqtSlot()
    def set_unpaused(self) -> None:
        self._table_model.set_unpaused()

    @pyqtSlot(list)
    def added_tracks(self, tracks: List[Track]):
        ...

    @pyqtSlot()
    def stop_playing(self) -> None:
        self.set_playing_track_index(None)

    def focusInEvent(self, event: QFocusEvent) -> None:
        # It's important to clear selection for better visuals, but to do it before opening new editor
        if QApplication.mouseButtons() & Qt.MouseButton.LeftButton:
            self.clearSelection()
        for index in self.selectedIndexes():
            if index.column() == self.rating_column:
                self.openPersistentEditor(index)

        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        for index in self.selectedIndexes():
            if index.column() == self.rating_column:
                typing.cast(StarDelegate, self.itemDelegateForColumn(self.rating_column)).commit_and_close_editor(index)
        super().focusOutEvent(event)


class TestMainWindow(QMainWindow):
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
        self.table_view.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
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

        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

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
