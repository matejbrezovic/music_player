from copy import deepcopy
from typing import List

from PyQt6.QtCore import pyqtSlot, Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QSplitter, QWidget, QHeaderView, QAbstractItemView)

from constants import PANEL_MIN_WIDTH
from data_models.track import Track
from gui.audio.audio_queue import AudioQueue
from gui.views.queue_table_view import QueueTableView
from gui.widgets.track_info_widget import TrackInfoWidget


class QueuePanel(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        # self.setStyleSheet("InformationPanel {background-color: rgba(0, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

        self.audio_queue = AudioQueue()
        self.audio_queue.queue_updated.connect(self.update_queue)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.vertical_splitter.setHandleWidth(0)
        self.playing_tracks_widget = QWidget(self)
        # self.playing_tracks_widget.setStyleSheet("QWidget {border: none;}")
        self.playing_tracks_widget.setContentsMargins(0, 0, 0, 0)
        self.playing_tracks_widget_layout = QVBoxLayout(self.playing_tracks_widget)
        self.playing_tracks_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.playing_tracks_widget_layout.setSpacing(0)

        default_row_height = 44
        self.queue_table_view = QueueTableView(self)
        self.queue_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.queue_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.queue_table_view.setShowGrid(False)
        self.queue_table_view.setFrameShape(QFrame.Shape.NoFrame)
        self.queue_table_view.verticalHeader().setDefaultSectionSize(default_row_height + 2)
        self.queue_table_view.horizontalHeader().setDefaultSectionSize(default_row_height + 2)
        self.queue_table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.queue_table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.queue_table_view.setIconSize(QSize(default_row_height - 6, default_row_height - 6))
        self.queue_table_view.setWordWrap(False)
        self.queue_table_view.verticalHeader().setVisible(False)
        self.queue_table_view.horizontalHeader().setVisible(False)
        self.queue_table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.queue_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.queue_table_view.track_double_clicked.connect(self.audio_queue.set_playing_track)

        # self.playing_tracks_widget_layout.addWidget(self.information_panel_combo_box)
        self.playing_tracks_widget_layout.addWidget(self.queue_table_view)

        self.track_info_widget = TrackInfoWidget(self)
        self.vertical_splitter.addWidget(self.playing_tracks_widget)
        self.vertical_splitter.addWidget(self.track_info_widget)
        self.vertical_splitter.setSizes([1, 1])
        self.main_layout.addWidget(self.vertical_splitter)

    def view_key_changed(self, key: int) -> None:
        ...

    def update_queue(self, tracks: List[Track]) -> None:
        self.queue_table_view.clearSelection()
        self.queue_table_view.set_tracks(tracks)

    @pyqtSlot(Track, int)
    def set_playing_track(self, track: Track) -> None:
        track = deepcopy(track)
        self.queue_table_view.set_playing_track(track)

        self.track_info_widget.set_track(track)

    def set_track_pixmap(self, pixmap: QPixmap) -> None:
        self.track_info_widget.set_track_pixmap(pixmap)

    def pause_playing_track(self) -> None:
        self.queue_table_view.set_paused()

    def unpause_playing_track(self) -> None:
        self.queue_table_view.set_unpaused()

    def stop_playing(self) -> None:
        self.queue_table_view.stop_playing()
