from __future__ import annotations

import sys
import typing
from typing import List, Optional, Any, Union, Dict

from PyQt6.QtCore import (QModelIndex, pyqtSignal, pyqtSlot, QSize, QAbstractItemModel, QRect, QAbstractTableModel, Qt,
                          QSortFilterProxyModel)
from PyQt6.QtGui import (QPixmap, QPainter, QPen, QBrush, QFontMetrics, QAction, QKeySequence, QShortcut,
                         QContextMenuEvent, QFocusEvent, QMouseEvent, QCursor, QColor, QIcon)
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import (QApplication, QTableView, QAbstractItemView, QHeaderView, QStyleOptionViewItem, QStyle,
                             QStyledItemDelegate, QMenu, QVBoxLayout, QPushButton, QWidget, QFrame, QMainWindow,
                             QAbstractScrollArea, QDialog, QStyleOptionHeaderV2, QProxyStyle)

from constants import MAIN_PANEL_COLUMN_NAMES, SELECTION_QCOLOR, LOST_FOCUS_QCOLOR, ROOT
from data_models.track import Track
from gui.dialogs.delete_track_dialog import DeleteTracksDialog
from gui.star.star_delegate import StarDelegate
from gui.star.star_rating import StarRating
from repositories.tracks_repository import TracksRepository
from utils import get_formatted_time_in_mins, change_pixmap_color


class TrackTableView(QTableView):
    new_tracks_set = pyqtSignal()
    play_now_triggered = pyqtSignal(list)
    output_to_triggered = pyqtSignal(str)
    queue_next_triggered = pyqtSignal(list)
    queue_last_triggered = pyqtSignal(list)
    tracks_deleted = pyqtSignal(list)
    track_clicked = pyqtSignal(Track)
    track_double_clicked = pyqtSignal(Track)

    def __init__(self, *args):
        super().__init__(*args)
        self.playing_track = None

        self.padding = 4
        self.rating_column = 7
        self.prev_index = QModelIndex()

        self._table_model = TrackTableModel(self)
        self._table_delegate = TrackTableItemDelegate(self)
        self._star_delegate = StarDelegate(self)
        self._table_header = TrackTableHeader(Qt.Orientation.Horizontal, self)
        self._table_header.sectionClicked.connect(self.sort_by_column)
        self.clicked.connect(self.row_clicked)
        self.doubleClicked.connect(self.row_double_clicked)
        self._table_header.sectionResized.connect(lambda: self._table_delegate.clear_cache())

        self._proxy_sort_model = TrackTableSortFilterProxyModel(self)
        self._proxy_sort_model.setSourceModel(self._table_model)
        self._sort_order = Qt.SortOrder.AscendingOrder
        self._old_sort_indicator_section_index = None

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
        self.playing_track = self._table_model.tracks[model_index.row()]
        self.track_double_clicked.emit(self.playing_track)

    def row_clicked(self, model_index: QModelIndex) -> None:
        track = self._table_model.tracks[model_index.row()]
        self.track_clicked.emit(track)

    def sort_by_column(self, logical_index: int, order: Optional[Qt.SortOrder] = None) -> None:
        self._table_delegate.clear_cache()
        if logical_index not in {0, 1}:
            if self._sort_order == Qt.SortOrder.AscendingOrder:
                self._sort_order = Qt.SortOrder.DescendingOrder
            else:
                self._sort_order = Qt.SortOrder.AscendingOrder

            if not self._table_header.isSortIndicatorShown():
                self._table_header.setSortIndicatorShown(True)
                self._sort_order = Qt.SortOrder.AscendingOrder

            if self._old_sort_indicator_section_index != logical_index:
                self._old_sort_indicator_section_index = logical_index
                self._sort_order = Qt.SortOrder.AscendingOrder
            if order:
                self._sort_order = order

            self.clearSelection()
            self.sortByColumn(logical_index, self._sort_order)

    def get_playing_track_index(self) -> Optional[int]:
        try:
            return self._table_model.tracks.index(self.playing_track)
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
        if not self._table_model.tracks:
            return

        selected_track_indexes = sorted(set([i.row() for i in self.selectionModel().selection().indexes()]))
        self.play_now_triggered.emit([self._table_model.tracks[i] for i in selected_track_indexes])

    def queue_next_action_triggered(self) -> None:
        if not self._table_model.tracks:
            return
        selected_track_indexes = sorted(set([i.row() for i in self.selectionModel().selection().indexes()]))
        self.queue_next_triggered.emit([self._table_model.tracks[i] for i in selected_track_indexes])

    def queue_last_action_triggered(self) -> None:
        if not self._table_model.tracks:
            return
        selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        self.queue_last_triggered.emit([self._table_model.tracks[i] for i in selected_track_indexes])

    def delete_action_triggered(self) -> None:
        selected_track_indexes = set([i.row() for i in self.selectionModel().selection().indexes()])
        selected_tracks = [self._table_model.tracks[i] for i in selected_track_indexes]
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
        self._table_model.set_tracks(tracks)
        self._table_delegate.set_tracks(tracks)
        self.new_tracks_set.emit()
        self.sort_by_column(self._table_header.sortIndicatorSection(), self._sort_order)

    @pyqtSlot(int)
    def set_playing_track_index(self, index: Optional[int]) -> None:
        self._table_model.set_playing_track_index(index)

    @pyqtSlot()
    def set_paused(self) -> None:
        self._table_model.set_paused()

    @pyqtSlot()
    def set_unpaused(self) -> None:
        self._table_model.set_unpaused()

    def displayed_tracks(self) -> List[Track]:
        return self._table_model.tracks

    @pyqtSlot()
    def set_stopped(self) -> None:
        self._table_model.set_stopped()

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


class TrackTableSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, table_view: TrackTableView):
        super().__init__(table_view)
        self._sort_order = Qt.SortOrder.AscendingOrder
        self.sort_key = None
        self._source_model: Optional[TrackTableModel] = None
        self._table_view = table_view

    def setSourceModel(self, source_model: TrackTableModel) -> None:
        self._source_model = source_model
        self._source_model.dataChanged.connect(self.dataChanged.emit)
        self._source_model.layoutAboutToBeChanged.connect(self.layoutAboutToBeChanged.emit)
        self._source_model.layoutChanged.connect(self.layoutChanged.emit)
        super().setSourceModel(source_model)

    def sort(self, column: int, sort_order: Qt.SortOrder = Qt.SortOrder) -> None:
        if column not in (0, 1):
            self.sort_key = MAIN_PANEL_COLUMN_NAMES[column].lower()
            if self.sort_key == "time":
                self.sort_key = "length"
            self._source_model.layoutAboutToBeChanged.emit()
            if sort_order == Qt.SortOrder.AscendingOrder:
                self._source_model.tracks.sort(key=self._sort_func)
            else:
                self._source_model.tracks.sort(key=self._sort_func, reverse=True)

            self._table_view._tracks = self._source_model.tracks
            self._source_model.set_playing_track_index(self._table_view.get_playing_track_index())

        self.layoutChanged.emit()
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def _sort_func(self, track: Track) -> Any:
        output = getattr(track, self.sort_key)
        if output is None and self.sort_key not in ("year", "length"):
            return ""
        elif output is None:
            return 0
        elif self.sort_key in ("year", "length"):
            if isinstance(output, str):
                output = output.lower()
            return output
        else:
            return str(output).lower()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        return self.sourceModel().data(index, role)


class TrackTableModel(QAbstractTableModel):
    def __init__(self, parent: TrackTableView = None):
        super().__init__(parent)
        self._table_view: TrackTableView = parent
        self.tracks: List[Track] = []
        self.is_paused = True
        self.is_stopped = True
        self.playing_track_index: Optional[int] = None
        self.playing_track: Optional[Track] = None

        self._speaker_pixmap_width = 16
        self._speaker_pixmap_height = 12

        self.speaker_playing_pixmap = QPixmap(f"{ROOT}/icons/speaker-playing.png")
        self.speaker_paused_pixmap = QPixmap(f"{ROOT}/icons/speaker-paused.png")

        self.speaker_playing_pixmap = change_pixmap_color(self.speaker_playing_pixmap, Qt.GlobalColor.red)
        self.speaker_paused_pixmap = change_pixmap_color(self.speaker_paused_pixmap, Qt.GlobalColor.red)

        self.speaker_playing_pixmap = self.speaker_playing_pixmap.scaled(
            self._speaker_pixmap_width, self._speaker_pixmap_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.speaker_paused_pixmap = self.speaker_paused_pixmap.scaled(
            self._speaker_pixmap_width, self._speaker_pixmap_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

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
                artwork_pixmap: Optional[QPixmap] = track.artwork_pixmap  # todo cache this
                if not artwork_pixmap or artwork_pixmap.isNull():
                    return None
                return artwork_pixmap.scaled(self._table_view.columnWidth(index.column()),
                                             self._table_view.columnWidth(index.column()),
                                             Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
            elif index.column() == 1:
                if self.playing_track_index is None or self.is_stopped:
                    return None
                if index.row() == self.playing_track_index:
                    if not self.is_paused:
                        return self.speaker_playing_pixmap
                    elif self.is_paused:
                        return self.speaker_paused_pixmap

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
        self.is_stopped = False
        self.is_paused = True
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))

    @pyqtSlot()
    def set_unpaused(self) -> None:
        self.is_stopped = False
        self.is_paused = False
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))

    @pyqtSlot()
    def set_stopped(self):
        self.is_stopped = True
        self.is_paused = True
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))

    @pyqtSlot(int)
    def set_playing_track_index(self, index: Optional[int]) -> None:
        self.playing_track_index = index
        self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 1))

    def delete_tracks(self, tracks: List[Track]) -> None:
        self.layoutAboutToBeChanged.emit()
        for track in self.tracks.copy():
            if track in tracks:
                self.tracks.remove(track)
        self.layoutChanged.emit()
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))


class TrackTableItemDelegate(QStyledItemDelegate):
    def __init__(self, track_table_view: TrackTableView = None):
        super().__init__(track_table_view)
        self.padding = track_table_view.padding
        self._table_view: TrackTableView = track_table_view
        self._tracks: List[Track] = []

        self._cached_elided_texts: Dict[QModelIndex, str] = {}
        self._cached_column_widths: Dict[int, int] = {}  # column index, column width
        self._cached_pixmaps: Dict[QModelIndex, QPixmap] = {}

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

        if decoration_role and not decoration_role.isNull():
            rect = option.rect
            rect.setRect(rect.left() + 1, rect.top() + 1,
                         rect.width() - 2, rect.height() - 2)

            if index in self._cached_pixmaps and index.column() != 1:
                painter.drawPixmap(rect, self._cached_pixmaps[index])
            else:
                pixmap = decoration_role
                if index.column() == 1:
                    old_height = rect.height()
                    rect.setHeight(pixmap.height())
                    rect.setWidth(pixmap.width())
                    rect.translate(0, (old_height - rect.height()) // 2)

                painter.drawPixmap(rect, pixmap)
                self._cached_pixmaps[index] = pixmap

        elif display_role:
            if option.state & QStyle.StateFlag.State_Selected and self._table_view.hasFocus():
                painter.setPen(QColor(option.palette.highlightedText()))
            else:
                painter.setPen(QColor(option.palette.text()))
            if (index in self._cached_elided_texts and
                    self._table_view.columnWidth(index.column()) == self._cached_column_widths[index.column()]):
                if index.column():
                    alignment = Qt.AlignmentFlag.AlignVCenter
                    if index.column() == len(MAIN_PANEL_COLUMN_NAMES) - 1:
                        alignment |= Qt.AlignmentFlag.AlignRight
                else:
                    alignment = Qt.AlignmentFlag.AlignCenter

                option.rect.setLeft(option.rect.left() + self.padding)
                option.rect.setRight(option.rect.right() - self.padding)
                painter.drawText(option.rect, alignment, self._cached_elided_texts[index])
            else:
                self._cached_column_widths[index.column()] = self._table_view.columnWidth(index.column())
                if MAIN_PANEL_COLUMN_NAMES[index.column()].lower() == "time":
                    display_role = get_formatted_time_in_mins(display_role)

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

                    self._cached_elided_texts[index] = f"{elided_text}"
                    return
                self._cached_elided_texts[index] = ""

    @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self._tracks = tracks
        self.clear_cache()

    def clear_cache(self) -> None:
        self._cached_elided_texts = {}
        self._cached_pixmaps = {}


class TrackTableHeader(QHeaderView):
    def __init__(self, orientation: Qt.Orientation, track_table_view: TrackTableView = None):
        super().__init__(orientation, track_table_view)
        self._table_view = track_table_view
        self.padding = self._table_view.padding
        self.setSectionsClickable(True)
        self.setSortIndicatorShown(True)
        self.setSectionsMovable(True)
        self.setFirstSectionMovable(False)
        self.setSortIndicatorShown(True)
        self.setStyle(HeaderProxyStyle(self.style()))

        self.sortIndicatorChanged.connect(self.sort_indicator_changed)
        self.sectionResized.connect(self.section_resized)
        self.section_texts = MAIN_PANEL_COLUMN_NAMES

        self.minimum_last_section_size = self.padding * 2 + self.fontMetrics().horizontalAdvance(self.section_texts[-1])

        self.setStyleSheet("""
        QHeaderView {
            border-bottom: 1px solid gray;
            border-top: 0px;
            border-right: 0px;
            border-left: 0px;
        }
        """)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        # prevents first 2 sections from moving
        if (self._table_view.columnViewportPosition(0) <= e.pos().x() <=
                self._table_view.columnViewportPosition(1) + self._table_view.columnWidth(1)):
            return

        super().mousePressEvent(e)

    @pyqtSlot(int, int, int)
    def section_resized(self, logical_index: int, _: int, new_size: int) -> None:
        """Sets minimum size for the last section."""
        if logical_index == self.count() - 1 and new_size < self.minimum_last_section_size:
            self.resizeSection(self.count() - 1, self.minimum_last_section_size)

    @pyqtSlot(int, Qt.SortOrder)
    def sort_indicator_changed(self, logical_index: int, order: Qt.SortOrder) -> None:
        if logical_index not in {0, 1}:
            self.setSortIndicator(logical_index, order)

    def text(self, section: int):
        if isinstance(self.model(), QAbstractItemModel):
            return self.section_texts[section]

    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:
        if not self.rect().isValid():
            return

        elided_text: str = QFontMetrics(self.font()).elidedText(self.text(logical_index),
                                                                Qt.TextElideMode.ElideRight,
                                                                self.sectionSize(logical_index) - self.padding)
        opt = QStyleOptionHeaderV2()
        old_brush_origin = painter.brushOrigin()

        self.initStyleOption(opt)
        self.initStyleOptionForIndex(opt, logical_index)

        opt.text = elided_text
        opt.rect = rect
        if logical_index == self.count() - 1:
            opt.textAlignment = Qt.AlignmentFlag.AlignRight
        else:
            opt.textAlignment = Qt.AlignmentFlag.AlignLeft

        if logical_index in {0, 1}:
            opt.sortIndicator = opt.SortIndicator.None_

        painter.setBrushOrigin(opt.rect.topLeft())
        self.style().drawControl(QStyle.ControlElement.CE_Header, opt, painter, self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorHeaderArrow, opt, painter, self)
        painter.setBrushOrigin(old_brush_origin)


class HeaderProxyStyle(QProxyStyle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_arrow_width = 10
        self.padding = 2

    def drawPrimitive(self, element: QStyle.PrimitiveElement, option: QStyleOptionHeaderV2, painter: QPainter,
                      widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.PrimitiveElement.PE_IndicatorHeaderArrow:
            return
        else:
            super().drawPrimitive(element, option, painter, widget)

    def drawControl(self, control: QStyle.ControlElement, option: QStyleOptionHeaderV2, painter: QPainter,
                    widget: Optional[QWidget] = ...) -> None:
        if control == QStyle.ControlElement.CE_HeaderLabel:
            option.rect.setTop(option.rect.top() - 2)
            painter.setPen(self.standardPalette().text().color())

            text_width = option.fontMetrics.horizontalAdvance(option.text)
            text_height = option.fontMetrics.height()

            space_between_text_and_arrow = 4

            sort_pixmap = None
            sort_rect = None
            if option.sortIndicator == option.SortIndicator.SortUp:
                sort_pixmap = QIcon(ROOT + "/icons/downward-arrow.png").pixmap(10, 10)
            elif option.sortIndicator == option.SortIndicator.SortDown:
                sort_pixmap = QIcon(ROOT + "/icons/upward-arrow.png").pixmap(10, 10)

            if sort_pixmap:
                if option.textAlignment == Qt.AlignmentFlag.AlignRight:
                    sort_rect = QRect(option.rect.right() - sort_pixmap.width() - self.padding +
                                      space_between_text_and_arrow,
                                      option.rect.top() + (text_height - sort_pixmap.height()) // 2,
                                      sort_pixmap.width(), sort_pixmap.height())
                else:
                    sort_rect = QRect(option.rect.left() + text_width + space_between_text_and_arrow,
                                      option.rect.top() + (text_height - sort_pixmap.height()) // 2,
                                      sort_pixmap.width(), sort_pixmap.height())

                if option.rect.width() > text_width + sort_rect.width():
                    painter.drawPixmap(sort_rect, sort_pixmap)

            text_rect = option.rect
            if option.textAlignment == Qt.AlignmentFlag.AlignRight and sort_pixmap and \
                    option.rect.width() > text_width + sort_rect.width():
                text_rect.setRight(text_rect.right() - sort_pixmap.width() - space_between_text_and_arrow)

            painter.drawText(text_rect, option.textAlignment, option.text)

        elif control == QStyle.ControlElement.CE_HeaderSection:
            super().drawControl(control, option, painter, widget)
            rect = option.rect
            top = rect.topRight()
            top.setY(top.y() + 1)
            bottom = rect.bottomRight()
            bottom.setY(bottom.y() - 2)

            painter.setPen(Qt.GlobalColor.gray)
            painter.drawLine(top, bottom)
        else:
            super().drawControl(control, option, painter, widget)


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
