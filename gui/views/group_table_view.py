from typing import List, Any, Union, Dict, Tuple, Optional

from PyQt6.QtCore import QModelIndex, pyqtSignal, pyqtSlot, QAbstractTableModel, Qt
from PyQt6.QtGui import QPen, QBrush, QPainter, QFont, QFocusEvent, QPalette, QColor
from PyQt6.QtWidgets import (QTableView, QWidget, QVBoxLayout, QStyledItemDelegate, QStyle,
                             QStyleOptionViewItem, QApplication, QAbstractItemView)

from constants import SELECTION_QCOLOR, LOST_FOCUS_QCOLOR
from data_models import TrackGroup
from repositories import CachedTracksRepository
from utils import ElidedLabel


class GroupTableView(QTableView):
    set_new_groups = pyqtSignal()
    group_clicked = pyqtSignal(list, tuple)
    group_double_clicked = pyqtSignal(list, tuple)

    def __init__(self, *args):
        super().__init__(*args)
        self.group_key: Optional[str] = None
        self.last_group_key = self.group_key
        self.last_group_title = None
        self._table_model = GroupTableModel(self)
        self._table_delegate = GroupTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        palette = self.palette()
        palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.BrightText, QColor(79, 180, 242))
        self.setPalette(palette)

        self.clicked.connect(self._group_clicked)
        self.doubleClicked.connect(self._group_double_clicked)

    @pyqtSlot(str)
    def set_group_key(self, key: str) -> None:
        self.group_key = key

    @pyqtSlot(list)
    def set_groups(self, groups: List[TrackGroup]) -> None:
        self._table_model.set_groups(groups)

    @property
    def groups(self) -> List[TrackGroup]:
        return self._table_model.groups

    @pyqtSlot(QModelIndex)
    def _group_clicked(self, index: QModelIndex) -> None:
        if not self._table_model.groups:
            return

        self.last_group_key = self.group_key
        self.last_group_title = self._table_model.groups[index.row()].title
        tracks = CachedTracksRepository().get_tracks_by(self.group_key, self.last_group_title)

        self.group_clicked.emit(tracks, (self.group_key, self.last_group_title))

    def currentChanged(self, current: QModelIndex, previous: QModelIndex) -> None:
        self._group_clicked(current)
        super().currentChanged(current, previous)

    @pyqtSlot(QModelIndex)
    def _group_double_clicked(self, index: QModelIndex) -> None:
        tracks = CachedTracksRepository().get_tracks_by(self.group_key, self.last_group_title)
        if not tracks:
            return

        self.last_group_key = self.group_key
        self.last_group_title = self._table_model.groups[index.row()].title
        self.group_double_clicked.emit(tracks, (self.group_key, self.last_group_title))

    def focusInEvent(self, event: QFocusEvent) -> None:
        if QApplication.mouseButtons() & Qt.MouseButton.LeftButton:
            self.clearSelection()
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        return super().focusOutEvent(event)


class GroupTableModel(QAbstractTableModel):
    def __init__(self, parent: GroupTableView = None):
        super().__init__(parent)
        self.table_view = parent
        self.groups: List[TrackGroup] = []

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self.groups:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignTop

        if role == Qt.ItemDataRole.DecorationRole:
            if not index.column():
                return self.groups[index.row()].pixmap

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self.groups)

    def columnCount(self, parent: QModelIndex = QModelIndex) -> int:
        return 2

    @pyqtSlot(list)
    def set_groups(self, groups: List[TrackGroup]) -> None:
        self.layoutAboutToBeChanged.emit()
        self.groups = groups
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))


class GroupTableItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: GroupTableView = None):
        super().__init__(parent)
        self._table_view: GroupTableView = parent

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

        decoration_role = index.data(Qt.ItemDataRole.DecorationRole)
        if decoration_role and not index.column():
            rect = option.rect
            rect.setRect(option.rect.left() + 2, option.rect.top() + 2,
                         option.rect.width() - 4, option.rect.height() - 4)

            pixmap = decoration_role.scaled(rect.width(), rect.height(),
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)

            painter.drawPixmap(rect, pixmap)

        if index.column() == 1:
            track_group = self._table_view.groups[index.row()]
            group_widget = GroupItemWidget(track_group.visual_title, track_group.tracks_num)

            group_widget.setGeometry(option.rect)

            painter.save()
            painter.translate(option.rect.x(), option.rect.y())
            if option.state & QStyle.StateFlag.State_Selected and self._table_view.hasFocus():
                group_widget.set_text_colors(option.palette.highlightedText(), option.palette.brightText())
            else:
                group_widget.set_text_colors(Qt.GlobalColor.black, Qt.GlobalColor.darkGray)

            group_widget.render(painter)
            painter.restore()


class GroupItemWidget(QWidget):
    def __init__(self, title: str, tracks_num: int, *args):
        super().__init__(*args)

        self.group_id = f"{title}{tracks_num}"
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 0, 5, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.v_layout.setSpacing(0)

        self.title_label = ElidedLabel(title)
        self.title_label.setContentsMargins(0, 0, 0, 0)

        if tracks_num == 0:
            tracks_label_text = "No tracks"
        else:
            tracks_label_text = f"{tracks_num} {'tracks' if tracks_num > 1 else 'track'}"

        self.tracks_label = ElidedLabel(tracks_label_text)
        self.tracks_label.setFont(QFont(self.tracks_label.font().family(), 8))
        self.tracks_label.setContentsMargins(0, 0, 0, 0)

        self.v_layout.addWidget(self.title_label)
        self.v_layout.addWidget(self.tracks_label)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_text_colors(self, top: Union[QColor, Qt.GlobalColor, int, str],
                        bottom: Union[QColor, Qt.GlobalColor, int, str]) -> None:
        top = QColor(top)
        bottom = QColor(bottom)

        self.title_label.setStyleSheet(f"color: {top.name()}")
        self.tracks_label.setStyleSheet(f"color: {bottom.name()}")
