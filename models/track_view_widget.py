from typing import List

from PyQt6.QtCore import QVariant, QPoint
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import *

from data_models.track import Track
from utils import *


class TrackViewWidget(QFrame):
    track_double_clicked = pyqtSignal(Track)
    track_clicked = pyqtSignal(Track)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks: List[Track] = []
        self.loaded_displays = {}
        self.selection_color = "rgba(166, 223, 231, 0.8)"
        self.lost_focus_color = "rgba(0, 0, 0, 0.2)"
        self.selection_stylesheet = f"selection-background-color: {self.selection_color}; selection-color: black"
        self.lost_focus_stylesheet = f"selection-background-color: {self.lost_focus_color}; selection-color: black"
        self.default_stylesheet = ""
        self.selected_row_index = 0
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.header_splitter = HeaderSplitter()
        self.header_splitter.setOrientation(Qt.Orientation.Horizontal)
        self.header_splitter.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.header_splitter.setHandleWidth(0)
        self.header_splitter.resized.connect(self.update_column_width)
        self.track_info_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.header_splitter.splitterMoved.connect(self.update_column_width)

        self.column_names = ["Artist", "Title", "Album", "Year", "Genre"]

        for column_name in self.column_names:
            widget = ElidedLabel("   " + column_name)
            widget.setMinimumWidth(20)
            self.header_splitter.addWidget(widget)

        self.table_widget = TableWidget()
        self.table_widget.setColumnCount(len(self.column_names))
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setShowGrid(False)
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.itemClicked.connect(lambda item: (self.track_clicked.emit(item.track),
                                                            print("B"),
                                                            self.set_row_background_color(self.selected_row_index, QColor(0, 0, 0, 0)),
                                                            self.set_selected_row_index(self.table_widget.row(item))))
        self.table_widget.itemDoubleClicked.connect(lambda item: (self.track_double_clicked.emit(item.track),

                                                                  self.set_selected_row_index(self.table_widget.row(item
                                                                                                                    ))))
        self.table_widget.setStyleSheet(self.selection_stylesheet)

        self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self.table_widget)

    def update_column_width(self) -> None:
        total_sizes = sum(self.header_splitter.sizes())
        try:
            for i in range(len(self.column_names)):
                self.table_widget.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))
        except ZeroDivisionError:
            pass

    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_widget.setRowCount(len(tracks))
        self.table_widget.clearSelection()
        self.displayed_tracks = tracks

        for i, track in enumerate(tracks):
            for j in range(len(self.column_names)):
                item = QTableWidgetItem()
                item_text = getattr(track, self.column_names[j].lower())
                item.setText(str(item_text) if item_text else "")
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                item.track = track
                self.table_widget.setItem(i, j, item)
            self.table_widget.setRowHeight(i, 22)

    def set_selected_row_index(self, index: int) -> None:
        self.selected_row_index = index

    def select_row_by_index(self, index: int) -> None:
        # self.set_row_background_color(self.selected_row_index, self.selection_color)
        # self.table_widget.setStyleSheet(self.selection_stylesheet)
        self.table_widget.selectRow(index)
        self.set_selected_row_index(index)

    def select_row_by_track(self, track: Track) -> None:
        if track not in self.displayed_tracks:
            self.table_widget.clearSelection()
            return
        self.select_row_by_index(self.displayed_tracks.index(track))

    def lose_focus(self) -> None:
        self.table_widget.clearSelection()
        # self.table_widget.clearSelection()
        # self.table_widget.setStyleSheet(self.lost_focus_stylesheet)
        self.set_row_background_color(self.selected_row_index, QColor(100, 20, 30))

    def set_row_background_color(self, row: int, color) -> None:
        # color.setRgb(100, 100, 20)
        # print(color.getRgb())
        # print(row, color)
        for i in range(len(self.column_names)):  # TODO should be improved in the future
            # self.table_widget.item(row, i).setSelected(False)
            self.table_widget.item(row, i).setBackground(color)
            # self.table_widget.item(row, i).setData(Qt.ItemDataRole.BackgroundRole, Qt.GlobalColor.gray)
            # self.table_widget.repaint()


class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selection_stylesheet = f"selection-background-color: rgba(166, 223, 231, 0.8); selection-color: black"

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        print("A")
        self.setStyleSheet(self.selection_stylesheet)
        super().mousePressEvent(event)


