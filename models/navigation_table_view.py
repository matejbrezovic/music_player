from typing import List, Any

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QVariant
from PyQt6.QtGui import QIcon, QPen, QBrush, QPainter
from PyQt6.QtWidgets import QTableView, QWidget, QVBoxLayout, QHBoxLayout, QStyledItemDelegate, QStyle, \
    QStyleOptionViewItem

import global_timer
from constants import *
from data_models.navigation_group import NavigationGroup
from repositories.cached_tracks_repository import CachedTracksRepository
from utils import ElidedLabel


class NavigationListModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self.table_view = parent
        self._groups: List[NavigationGroup] = []

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self._groups:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignTop

        if role == Qt.ItemDataRole.DecorationRole:
            if not index.column():
                artwork_pixmap = self._groups[index.row()].pixmap
                # artwork_pixmap = artwork_pixmap if artwork_pixmap else QPixmap(f"icons/album.png")
                icon = QIcon(artwork_pixmap)
                icon.addPixmap(artwork_pixmap, QtGui.QIcon.Mode.Selected)
                return icon

        # if role == Qt.ItemDataRole.DisplayRole:
        #     if index.column() != 1:
        #         return None
        #     group = self._groups[index.row()]
        #     group_id = f"{group.title}{group.tracks_num}"
        #     index_widget = self.table_view.indexWidget(index)
        #     # self.table_view.setIndexWidget(index, NavigationGroupWidget(group.title, group.tracks_num))
        #
        #     if not index_widget or index_widget.group_id != group_id:
        #         self.table_view.setIndexWidget(index, NavigationGroupWidget(group.title, group.tracks_num))
        #     return QVariant()

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self._groups)

    def columnCount(self, parent: QModelIndex = QModelIndex) -> int:
        return 2

    def set_groups(self, groups: List[NavigationGroup]) -> None:
        self.layoutAboutToBeChanged.emit()
        self._groups = groups
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))


class NavigationTableItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self._groups: List[NavigationGroup] = []

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        super().paint(painter, option, index)
        # painter.save()
        # set background color
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        if option.state & QStyle.StateFlag.State_Selected:
            if self._table_view.hasFocus():
                painter.setBrush(QBrush(SELECTION_QCOLOR))
            else:
                painter.setBrush(QBrush(LOST_FOCUS_QCOLOR))
        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawRect(option.rect)

        if index.data(Qt.ItemDataRole.DecorationRole):
            decoration_value = index.data(Qt.ItemDataRole.DecorationRole).pixmap(50, 50)
            rect = option.rect
            rect.setRect(option.rect.left() + 2, option.rect.top() + 2,
                         option.rect.width() - 4, option.rect.height() - 4)

            pixmap = decoration_value.scaled(rect.width(), rect.height(),
                                             Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)

            painter.drawPixmap(rect, pixmap)

        if index.column() == 1:
            navigation_group = self._groups[index.row()]
            navigation_group_widget = NavigationGroupWidget(navigation_group.title, navigation_group.tracks_num)

            navigation_group_widget.setGeometry(option.rect)

            painter.save()
            painter.translate(option.rect.x(), option.rect.y())
            navigation_group_widget.render(painter)
            painter.restore()

    def set_groups(self, groups: List[NavigationGroup]) -> None:
        self._groups = groups


class NavigationTableView(QTableView):
    set_new_groups = pyqtSignal()
    group_clicked = pyqtSignal(list)
    group_double_clicked = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups: List[NavigationGroup] = []
        self.group_key = None
        self._table_model = NavigationListModel(self)
        self._table_delegate = NavigationTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)

        self.clicked.connect(self.temp)
        self.doubleClicked.connect(lambda index: self.group_double_clicked.emit(
            CachedTracksRepository().get_tracks_by(self.group_key, self.groups[index.row()].title)))

    def temp(self, index):
        tracks = CachedTracksRepository().get_tracks_by(self.group_key, self.groups[index.row()].title)
        # print(tracks)
        # TEST_TRACKS = tracks
        global_timer.timer_init()
        global_timer.start()
        self.group_clicked.emit(tracks)

    def set_group_key(self, key: str) -> None:
        self.group_key = key

    def set_groups(self, groups: List[NavigationGroup]) -> None:
        self.groups = groups
        self._table_model.set_groups(groups)
        self._table_delegate.set_groups(groups)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(SELECTION_STYLESHEET)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(LOST_FOCUS_STYLESHEET)
        super().focusOutEvent(event)


class NavigationGroupWidget(QWidget):
    def __init__(self, title: str, tracks_num: int, parent=None):
        super().__init__(parent)

        self.group_id = f"{title}{tracks_num}"
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 0, 5, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        title_label = ElidedLabel(title)
        title_label.setContentsMargins(0, 0, 0, 0)
        title_label.setMinimumHeight(20)

        tracks_label = ElidedLabel(f"{tracks_num} {'Tracks' if tracks_num > 1 else 'Track'}")
        tracks_label.setContentsMargins(0, 0, 0, 0)
        tracks_label.setMinimumHeight(20)

        self.v_layout.addWidget(title_label)
        self.v_layout.addWidget(tracks_label)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
