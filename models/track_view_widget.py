from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor
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

        self.column_names = ["", "Artist", "Title", "Album", "Year", "Genre"]

        for column_name in self.column_names:
            widget = ElidedLabel("   " + column_name)
            widget.setMinimumWidth(20)
            self.header_splitter.addWidget(widget)

        self.header_splitter.widget(0).setStyleSheet("background-color: blue")
        self.header_splitter.widget(0).setMaximumWidth(60)

        self.table_widget = CustomHeaderTableWidget()
        self.table_widget.setColumnCount(len(self.column_names))
        self.table_widget.verticalHeader().setVisible(False)
        # self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # self.table_widget.horizontalHeader()
        # self.table_widget.horizontalHeader().
        # self.table_widget.horizontalHeader().setMaximumWidth(200)
        # self.table_widget.horizontalHeader().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        # self.table_widget.horizontalHeader().setCascadingSectionResizes(True)
        # self.table_widget.horizontalHeader().setSectionsMovable(True)
        # self.table_widget.horizontalHeader().setVisible(False)
        # self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.table_widget.setShowGrid(False)
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # self.table_widget
        # self.table_widget.horizontalHeader().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        # self.table_widget.resized.connect(lambda: self.table_widget.horizontalHeader().setMaximumWidth(self.table_widget.width()))
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.itemClicked.connect(lambda item: (self.track_clicked.emit(item.track),
                                                            self.set_selected_row_index(self.table_widget.row(item))))
        self.table_widget.itemDoubleClicked.connect(lambda item: (self.track_double_clicked.emit(item.track),
                                                                  self.set_selected_row_index(self.table_widget.row(item
                                                                                                                    ))))
        self.table_widget.setStyleSheet(self.selection_stylesheet)

        # for i in range(len(self.column_names)):
        #     self.table_widget.horizontalHeader().add

        self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self.table_widget)

    def update_column_width(self) -> None:
        total_sizes = sum(self.header_splitter.sizes())
        if not total_sizes:
            return
        print(self.header_splitter.sizes())
        for i in range(len(self.column_names)):
            # self.table_widget.horizontalHeader().setH
            print(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))
            # self.table_widget.horizontalHeader().resizeSection(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))
            # self.table_widget.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # self.table_widget.horizontalHeader().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        super().resizeEvent(a0)

    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_widget.setRowCount(len(tracks))
        self.table_widget.clearSelection()
        self.displayed_tracks = tracks

        for i, track in enumerate(tracks):
            for j in range(len(self.column_names)):
                item = QTableWidgetItem()
                # item.setSizeHint(QSize(20, 20))
                try:
                    item_text = getattr(track, self.column_names[j].lower())
                except AttributeError:
                    item_text = ""
                    item.setBackground(QColor(100, 20, 30))
                item.setText(str(item_text) if item_text else "")
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                item.track = track
                self.table_widget.setItem(i, j, item)
            self.table_widget.setRowHeight(i, 22)

    def set_selected_row_index(self, index: int) -> None:
        self.selected_row_index = index

    def select_row_by_index(self, index: int) -> None:
        self.table_widget.selectRow(index)
        self.set_selected_row_index(index)

    def select_row_by_track(self, track: Track) -> None:
        if track not in self.displayed_tracks:
            self.table_widget.clearSelection()
            return
        self.select_row_by_index(self.displayed_tracks.index(track))

    def lose_focus(self) -> None:
        self.table_widget.setStyleSheet(self.lost_focus_stylesheet)



