from typing import List

from PyQt6 import QtWidgets

# from auto_resizing_header_view_test import HeaderView
from PyQt6.QtCore import pyqtSlot

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

        # noinspection PyTypeChecker
        self.table_view = TrackTableView(self)
        self.table_view.horizontalHeader().setMinimumSectionSize(4)
        self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.table_view.verticalHeader().setVisible(False)
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

        first_col_width = 26
        second_col_width = 20
        rating_col_width = 82

        self.table_view.horizontalHeader().resizeSection(0, first_col_width)
        self.table_view.horizontalHeader().resizeSection(1, second_col_width)
        self.table_view.horizontalHeader().resizeSection(7, rating_col_width)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        self.main_layout.addWidget(self.table_view)

    @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_view.set_tracks(tracks)
        self.displayed_tracks = tracks
        index = self.displayed_tracks.index(self.playing_track) if self.playing_track in self.displayed_tracks else None
        self.table_view.set_playing_track_index(index)
        self.table_view.selectionModel().clearSelection()
        self.table_view.scrollToTop()

    @pyqtSlot(Track)
    def set_playing_track(self, track: Track) -> None:
        self.playing_track = track
        if track not in self.displayed_tracks:
            print("Track not in displayed tracks!")
            self.table_view.set_playing_track_index(None)
            return
        self.table_view.set_playing_track_index(self.displayed_tracks.index(track))
        self.table_view.set_unpaused()

    @pyqtSlot()
    def pause_playing_track(self) -> None:
        self.table_view.set_paused()

    @pyqtSlot()
    def unpause_playing_track(self) -> None:
        self.table_view.set_unpaused()

    @pyqtSlot(list)
    def added_tracks(self, tracks: List[Track]) -> None:
        self.table_view.added_tracks(tracks)
