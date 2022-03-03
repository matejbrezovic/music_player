from typing import List

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QSize, QEvent, QModelIndex
from PyQt6.QtWidgets import *

from auto_resizing_header_view_test import HeaderView
from data_models.track import Track
from models.track_table_view import TrackTableView
from utils import *


class TrackViewWidget(QWidget):
    track_double_clicked = pyqtSignal(Track, int)
    track_clicked = pyqtSignal(Track, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks: List[Track] = []
        self.loaded_displays = {}
        self.default_stylesheet = ""
        self.selected_row_index = 0
        self.playing_track = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.header_splitter = HeaderSplitter()
        self.header_splitter.setOrientation(Qt.Orientation.Horizontal)
        self.header_splitter.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.header_splitter.setHandleWidth(2)
        self.header_splitter.resized.connect(self.update_column_width)
        self.header_splitter.splitterMoved.connect(self.update_column_width)
        self.header_splitter.setStyleSheet("QSplitter::handle{background: red;}")

        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]

        for i, column_name in enumerate(self.column_names):
            widget = ElidedLabel("" + column_name)
            widget.setMinimumWidth(4)
            self.header_splitter.addWidget(widget)
            self.header_splitter.setCollapsible(i, False)

        self.table_view = TrackTableView(self)
        # self.table_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_view.horizontalHeader().setMinimumSectionSize(4)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table_view.setIconSize(QSize(22, 22))
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.set_new_tracks.connect(self.update_column_width)

        self.table_view.clicked.connect(lambda model_index: self.track_clicked.emit(
                                                            self.displayed_tracks[model_index.row()],
                                                            model_index.row()))
        self.table_view.doubleClicked.connect(lambda model_index: self.track_double_clicked.emit(
                                                                  self.displayed_tracks[model_index.row()],
                                                                  model_index.row()))

        self.table_view.setStyleSheet(SELECTION_STYLESHEET)

        # header = HeaderView()
        # self.table_view.setHorizontalHeader(header)
        # self.table_view.setTextElideMode(Qt.TextElideMode.ElideNone)

        self._focus_frame = FocusFrame(self.table_view)
        self._focus_frame.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        first_col_width = 26
        second_col_width = 20

        self.header_splitter.setCollapsible(0, False)
        self.header_splitter.setCollapsible(1, False)
        self.header_splitter.widget(0).setFixedWidth(first_col_width)
        self.header_splitter.widget(1).setFixedWidth(second_col_width)
        self.table_view.setColumnWidth(0, first_col_width)
        self.table_view.setColumnWidth(1, second_col_width)
        self.table_view.horizontalHeader().resizeSection(0, first_col_width)
        self.table_view.horizontalHeader().resizeSection(1, second_col_width)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)

        self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self.table_view)

        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    def update_column_width(self) -> None:
        total_sizes = sum(self.header_splitter.sizes())
        if not total_sizes:
            return
        for i in range(2, len(self.column_names)):
            self.table_view.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))

    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_view.set_tracks(tracks)
        self.displayed_tracks = tracks
        index = self.displayed_tracks.index(self.playing_track) if self.playing_track in self.displayed_tracks else None
        self.table_view.set_playing_track_index(index)
        self.table_view.selectionModel().clearSelection()
        self.table_view.scrollToTop()

    def set_selected_row_index(self, index: int) -> None:
        self.selected_row_index = index

    def select_row_by_index(self, index: int) -> None:
        self.table_view.selectRow(index)
        self.set_selected_row_index(index)

    def select_row_by_track(self, track: Track) -> None:
        if track not in self.displayed_tracks:
            self.table_view.clearSelection()
            return
        self.select_row_by_index(self.displayed_tracks.index(track))

    def set_playing_track(self, track: Track) -> None:
        if track not in self.displayed_tracks:
            return
        self.playing_track = track
        self.table_view.set_playing_track_index(self.displayed_tracks.index(track))
        self.table_view.set_unpaused()

    def pause_playing_track(self) -> None:
        self.table_view.set_paused()

    def unpause_playing_track(self) -> None:
        self.table_view.set_unpaused()
