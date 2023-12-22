import sys
import time
from dataclasses import dataclass
from random import randint, choice
from string import ascii_letters
from typing import List, Optional

from PyQt6 import QtCore, QtWidgets
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QFontMetrics, QColor
from PyQt6.QtWidgets import (QApplication, QTableView, QAbstractItemView, QHeaderView, QStyleOptionViewItem, QStyle,
                             QStyledItemDelegate, QVBoxLayout, QPushButton, QWidget)

SELECTION_QCOLOR = QColor(156, 206, 233)
SELECTION_QCOLOR_BORDER = QColor(110, 189, 232)
LOST_FOCUS_QCOLOR = QColor(0, 0, 0, 50)
LOST_FOCUS_QCOLOR_BORDER = QColor(0, 0, 0, 60)


@dataclass
class Track:
    track_id: int
    file_path: str
    title: str
    album: str
    artist: str
    composer: str
    genre: str
    year: int
    length: int

    # def __post_init__(self): # won't work bcz file_path is some random gibberish
    #     self.size = os.path.getsize(self.file_path)

def random_string():
    return ''.join(choice(ascii_letters) for i in range(10))

def generate_random_track():
    return Track(
        track_id=696969,
        file_path=random_string(),
        title=random_string(),
        album=random_string(),
        artist=random_string(),
        composer=random_string(),
        genre=random_string(),
        year=randint(1, 2000),
        length=randint(1, 10000)
    )


class TrackTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        self._tracks: List[Track] = []
        self.is_playing = False
        self.playing_track_index: Optional[int] = None

    def set_tracks(self, tracks: List[Track]) -> None:
        self.layoutAboutToBeChanged.emit()
        self._tracks = tracks
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not self._tracks:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole and not index.column():
            return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.DisplayRole and not index.data(Qt.ItemDataRole.DecorationRole):
            if not index.column():
                return "-"

            value = self.column_names[index.column()].lower()
            return getattr(self._tracks[index.row()], value) if value else None

    def rowCount(self, index: QModelIndex = QModelIndex):
        return len(self._tracks)

    def columnCount(self, index: QModelIndex = QModelIndex):
        return len(self.column_names)

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
        if self.playing_track_index is not None:
            self.dataChanged.emit(self.index(0, 1),
                                  self.index(self.rowCount(), 1))


class TrackTableItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self.last_index = -1

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        if option.state & QStyle.StateFlag.State_Selected:
            if self._table_view.hasFocus():
                fill_color = SELECTION_QCOLOR
                border_color = SELECTION_QCOLOR_BORDER
                if index.row() != self.last_index:
                    self.last_index = index.row()
                    print(f"{self.last_index} Blue")

            else:
                fill_color = LOST_FOCUS_QCOLOR
                border_color = LOST_FOCUS_QCOLOR_BORDER
                if index.row() != self.last_index:
                    self.last_index = index.row()
                    print(f"{self.last_index} Grey")

            painter.setBrush(fill_color)
            painter.drawRect(option.rect)
            painter.setPen(QPen(QBrush(border_color), 1))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            # painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            if index.row() != self.last_index:
                self.last_index = index.row()
                print(f"{self.last_index} White")

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
        # time.sleep(0.02)


class TrackTableView(QTableView):
    set_new_tracks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks: List[Track] = []
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]
        self._table_model = TrackTableModel(self)
        self._table_delegate = TrackTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)

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
        if QtWidgets.QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton:
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
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        start = time.time()
        self.table_view.set_tracks([generate_random_track() for i in range(10)])
        print(f"Test loaded in: {time.time() - start:.6f} s")

        self.vbox.addWidget(self.table_view)
        self.vbox.addWidget(QPushButton())

        self.setCentralWidget(self.widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = TestMainWindow()
    mainWindow.show()
    sys.exit(app.exec())
