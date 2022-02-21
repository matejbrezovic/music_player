from typing import List, Any

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QVariant
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QListView, QTableView, QWidget, QVBoxLayout, QHBoxLayout

from constants import *
from data_models.navigation_group import NavigationGroup
from repositories.tracks_repository import TracksRepository
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

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() != 1:
                return None
            group = self._groups[index.row()]
            group_id = f"{group.title}{group.tracks_num}"
            index_widget = self.table_view.indexWidget(index)
            # self.table_view.setIndexWidget(index, NavigationGroupWidget(group.title, group.tracks_num))

            if not index_widget or index_widget.group_id != group_id:
                self.table_view.setIndexWidget(index, NavigationGroupWidget(group.title, group.tracks_num))
            return QVariant()

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


class NavigationGroupWidget(QWidget):
    def __init__(self, title: str, tracks_num: int, parent=None):
        super().__init__(parent)

        self.group_id = f"{title}{tracks_num}"
        # return
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 0, 5, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        # self.id = f"{title}{artist}{duration}"

        title_label = ElidedLabel(title)
        title_label.setContentsMargins(0, 0, 0, 0)
        title_label.setMinimumHeight(20)

        tracks_label = ElidedLabel(f"{tracks_num} {'Tracks' if tracks_num > 1 else 'Track'}")
        tracks_label.setContentsMargins(0, 0, 0, 0)
        tracks_label.setMinimumHeight(20)

        self.v_layout.addWidget(title_label)
        self.v_layout.addWidget(tracks_label)


class NavigationTableView(QTableView):
    set_new_groups = pyqtSignal()
    group_clicked = pyqtSignal(list)
    group_double_clicked = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups: List[NavigationGroup] = []
        self.group_key = None
        self._table_model = NavigationListModel(self)
        self.setModel(self._table_model)

        self.clicked.connect(self.temp)
        self.doubleClicked.connect(lambda index: self.group_double_clicked.emit(
            TracksRepository().get_tracks_by(self.group_key, self.groups[index.row()].title)))

    def temp(self, index):
        tracks = TracksRepository().get_tracks_by(self.group_key, self.groups[index.row()].title)
        # print(tracks)
        # TEST_TRACKS = tracks
        self.group_clicked.emit(tracks)

    def set_group_key(self, key: str) -> None:
        self.group_key = key

    def set_groups(self, groups: List[NavigationGroup]) -> None:
        self.groups = groups
        self._table_model.set_groups(groups)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(SELECTION_STYLESHEET)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(LOST_FOCUS_STYLESHEET)
        super().focusOutEvent(event)