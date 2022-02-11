from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtWidgets import QListView

from constants import *


class NavigationListModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._groups = []

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        ...

    def rowCount(self, index: QModelIndex = QModelIndex):
        return len(self._groups)


class NavigationListView(QListView):
    set_new_tracks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._list_model = NavigationListModel()
        self.setModel(self._list_model)

    def set_groups(self):
        ...

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(SELECTION_STYLESHEET)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setStyleSheet(LOST_FOCUS_STYLESHEET)
        super().focusOutEvent(event)