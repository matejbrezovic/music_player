from typing import List, Any, Union

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QModelIndex, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPen, QBrush, QPainter, QFont
from PyQt6.QtWidgets import (QTableView, QWidget, QVBoxLayout, QHBoxLayout, QStyledItemDelegate, QStyle,
                             QStyleOptionViewItem, QApplication, QAbstractItemView)

from constants import *
from data_models.navigation_group import NavigationGroup
from data_models.track import Track
from repositories.cached_tracks_repository import CachedTracksRepository
from utils import ElidedLabel


class NavigationTableModel(QtCore.QAbstractTableModel):
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
                # icon = QIcon(artwork_pixmap)
                # icon.addPixmap(artwork_pixmap, QtGui.QIcon.Mode.Selected)
                return artwork_pixmap

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self._groups)

    def columnCount(self, parent: QModelIndex = QModelIndex) -> int:
        return 2

    @pyqtSlot(list)
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
        # super().paint(painter, option, index)
        # painter.save()
        # set background color
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
            # painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            # if index.row() == self._table_view.selectedIndexes()[-1].row():  # might be ruining performance
            #     painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
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
            navigation_group = self._groups[index.row()]
            navigation_group_widget = NavigationGroupWidget(navigation_group.visual_title, navigation_group.tracks_num)

            navigation_group_widget.setGeometry(option.rect)

            painter.save()
            painter.translate(option.rect.x(), option.rect.y())
            if option.state & QStyle.StateFlag.State_Selected and self._table_view.hasFocus():
                navigation_group_widget.set_text_colors(option.palette.highlightedText(), option.palette.brightText())
            else:
                navigation_group_widget.set_text_colors(Qt.GlobalColor.black, Qt.GlobalColor.darkGray)

            navigation_group_widget.render(painter)
            painter.restore()

    @pyqtSlot(list)
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
        self.last_group_key = self.group_key
        self.last_group_title = None
        self._table_model = NavigationTableModel(self)
        self._table_delegate = NavigationTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        palette = self.palette()
        palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.BrightText, QColor(79, 180, 242))
        self.setPalette(palette)

        self.clicked.connect(self.single_click_action)
        self.doubleClicked.connect(self.double_click_action)

    @pyqtSlot(str)
    def set_group_key(self, key: str) -> None:
        self.group_key = key

    @pyqtSlot(list)
    def set_groups(self, groups: List[NavigationGroup]) -> None:
        self.groups = groups
        self._table_model.set_groups(groups)
        self._table_delegate.set_groups(groups)

    @pyqtSlot(QModelIndex)
    def single_click_action(self, index: QModelIndex) -> None:
        self.last_group_key = self.group_key
        self.last_group_title = self.groups[index.row()].title
        tracks = CachedTracksRepository().get_tracks_by(self.group_key, self.last_group_title)
        self.group_clicked.emit(tracks)

    @pyqtSlot(QModelIndex)
    def double_click_action(self, index: QModelIndex) -> None:
        self.last_group_key = self.group_key
        self.last_group_title = self.groups[index.row()].title
        tracks = CachedTracksRepository().get_tracks_by(self.group_key, self.last_group_title)
        self.group_double_clicked.emit(tracks)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        if QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton:
            self.clearSelection()
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        return super().focusOutEvent(event)


class NavigationGroupWidget(QWidget):
    def __init__(self, title: str, tracks_num: int, parent=None):
        super().__init__(parent)

        self.group_id = f"{title}{tracks_num}"
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 0, 5, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.v_layout.setSpacing(0)

        self.title_label = ElidedLabel(title)
        self.title_label.setContentsMargins(0, 0, 0, 0)

        self.tracks_label = ElidedLabel(f"{tracks_num} {'tracks' if tracks_num > 1 else 'track'}")
        self.tracks_label.setFont(QFont(self.tracks_label.font().family(), 7))
        self.tracks_label.setContentsMargins(0, 0, 0, 0)

        self.v_layout.addWidget(self.title_label)
        self.v_layout.addWidget(self.tracks_label)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_text_colors(self, top: Union[QColor, Qt.GlobalColor, int, str],
                        bottom: Union[QColor, Qt.GlobalColor, int, str]) -> None:
        top = QColor(top)
        bottom = QColor(bottom)

        self.title_label.setStyleSheet(f"color: {top.name()}")
        self.tracks_label.setStyleSheet(f"color: {bottom.name()}")
