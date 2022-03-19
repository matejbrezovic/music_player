from typing import List

from PyQt6 import QtWidgets

from constants import *
# from auto_resizing_header_view_test import HeaderView
from data_models.track import Track
from models.track_table_view import TrackTableView
from utils import *


class TrackViewWidget(QWidget):
    track_double_clicked = pyqtSignal(Track, int)
    track_clicked = pyqtSignal(Track, int)
    play_now_triggered = pyqtSignal(list)
    output_to_triggered = pyqtSignal(str)
    queue_next_triggered = pyqtSignal(list)
    queue_last_triggered = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks: List[Track] = []
        self.loaded_displays = {}
        self.default_stylesheet = ""
        self.selected_row_index = 0
        self.playing_track = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.header_splitter = HeaderSplitter()
        self.header_splitter.setOrientation(Qt.Orientation.Horizontal)
        self.header_splitter.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.header_splitter.setHandleWidth(2)
        self.header_splitter.resized.connect(self.update_column_width)
        self.header_splitter.splitterMoved.connect(self.update_column_width)
        self.header_splitter.setStyleSheet("QSplitter {background-color: white;}"
                                           "QSplitter::handle{background: black;}")

        for i, column_name in enumerate(MAIN_PANEL_COLUMN_NAMES):
            widget = ElidedLabel(column_name)
            widget.setMinimumWidth(4)
            self.header_splitter.addWidget(widget)
            self.header_splitter.setCollapsible(i, False)

        # noinspection PyTypeChecker
        self.table_view = TrackTableView(self)
        # self.table_view.setStyleSheet("""
        # QTableView::item{padding: 10px;}
        # """)
        # self.table_view.horizontalHeader().pa
        self.table_view.horizontalHeader().setMinimumSectionSize(4)
        self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.table_view.verticalHeader().setOffset(-20)
        # print(self.table_view.verticalOffset())
        self.table_view.verticalHeader().setVisible(False)
        # self.table_view.horizontalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table_view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table_view.setIconSize(QSize(22, 22))
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setFrameShape(QFrame.Shape.NoFrame)
        self.table_view.set_new_tracks.connect(self.update_column_width)

        self.table_view.clicked.connect(lambda model_index: self.track_clicked.emit(
                                                            self.displayed_tracks[model_index.row()],
                                                            model_index.row()))
        self.table_view.doubleClicked.connect(lambda model_index: self.track_double_clicked.emit(
                                                                  self.displayed_tracks[model_index.row()],
                                                                  model_index.row()))
        self.table_view.play_now_triggered.connect(self.play_now_triggered.emit)
        self.table_view.queue_next_triggered.connect(self.queue_next_triggered.emit)
        self.table_view.queue_last_triggered.connect(self.queue_last_triggered.emit)
        self.table_view.output_to_triggered.connect(self.output_to_triggered.emit)

        # self.table_view.setStyleSheet(SELECTION_STYLESHEET)

        first_col_width = 26
        second_col_width = 20
        rating_col_width = 50

        self.header_splitter.setCollapsible(0, False)
        self.header_splitter.setCollapsible(1, False)
        self.header_splitter.setCollapsible(7, False)
        self.header_splitter.widget(0).setFixedWidth(first_col_width)
        self.header_splitter.widget(1).setFixedWidth(second_col_width)
        self.header_splitter.widget(7).setFixedWidth(rating_col_width)
        self.table_view.setColumnWidth(0, first_col_width)
        self.table_view.setColumnWidth(1, second_col_width)
        self.table_view.setColumnWidth(7, rating_col_width)
        self.table_view.horizontalHeader().resizeSection(0, first_col_width)
        self.table_view.horizontalHeader().resizeSection(1, second_col_width)
        self.table_view.horizontalHeader().resizeSection(7, rating_col_width)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        # self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self.table_view)

        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    def update_column_width(self) -> None:
        total_sizes = sum(self.header_splitter.sizes())
        if not total_sizes:
            return
        for i in range(2, len(MAIN_PANEL_COLUMN_NAMES)):
            self.table_view.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))

    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_view.set_tracks(tracks)
        self.displayed_tracks = tracks
        index = self.displayed_tracks.index(self.playing_track) if self.playing_track in self.displayed_tracks else None
        self.table_view.set_playing_track_index(index)
        self.table_view.selectionModel().clearSelection()
        self.table_view.scrollToTop()

    # def set_selected_row_index(self, index: int) -> None: # TODO remove, unneeded
    #     self.selected_row_index = index
    #
    # def select_row_by_index(self, index: int) -> None:
    #     self.table_view.selectRow(index)
    #     self.set_selected_row_index(index)
    #
    # def select_row_by_track(self, track: Track) -> None:
    #     if track not in self.displayed_tracks:
    #         self.table_view.clearSelection()
    #         return
    #     self.select_row_by_index(self.displayed_tracks.index(track))

    def set_playing_track(self, track: Track) -> None:
        self.playing_track = track
        if track not in self.displayed_tracks:
            self.table_view.set_playing_track_index(None)
            return
        self.table_view.set_playing_track_index(self.displayed_tracks.index(track))
        self.table_view.set_unpaused()

    def pause_playing_track(self) -> None:
        self.table_view.set_paused()

    def unpause_playing_track(self) -> None:
        self.table_view.set_unpaused()
