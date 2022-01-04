from typing import List

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
        self.selected_color = "rgba(175, 193, 244, 0.5)"
        self.selected_row_index = 0
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        class HeaderSplitter(QSplitter):
            resized = pyqtSignal()
            def __init__(self, parent=None):
                super().__init__(parent)

            def resizeEvent(self, event):
                self.resized.emit()
                super().resizeEvent(event)

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

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.column_names))
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setShowGrid(False)
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.itemClicked.connect(lambda item: (self.track_clicked.emit(item.track)))
        self.table_widget.itemDoubleClicked.connect(lambda item: self.track_double_clicked.emit(item.track))
        self.table_widget.setStyleSheet("selection-background-color: rgba(166, 223, 231, 0.8); selection-color: black")

        self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self.table_widget)

    def update_column_width(self):
        total_sizes = sum(self.header_splitter.sizes())
        try:
            for i in range(len(self.column_names)):
                self.table_widget.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))
        except ZeroDivisionError:
            pass

    def set_tracks(self, tracks: List[Track]):
        self.table_widget.setRowCount(len(tracks))
        self.table_widget.clearSelection()
        self.displayed_tracks = tracks

        for i, track in enumerate(tracks):
            for j in range(len(self.column_names)):
                item = QTableWidgetItem()
                item_text = getattr(track, self.column_names[j].lower())
                item.setText(str(item_text) if item_text else "")
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.track = track
                self.table_widget.setItem(i, j, item)
            self.table_widget.setRowHeight(i, 22)

    def select_row_by_index(self, index: int):
        self.table_widget.selectRow(index)
        self.selected_row_index = index

    def select_row_by_track(self, track: Track):
        if track not in self.displayed_tracks:
            self.table_widget.clearSelection()
            return
        self.select_row_by_index(self.displayed_tracks.index(track))
