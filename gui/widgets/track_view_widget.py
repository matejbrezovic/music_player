from copy import deepcopy
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QAbstractItemView, QFrame, QHeaderView

from data_models import Track
from gui.views import TrackTableView


class TrackViewWidget(QWidget):
    track_double_clicked = pyqtSignal(Track)
    track_clicked = pyqtSignal(Track)
    play_now_triggered = pyqtSignal(list)
    output_to_triggered = pyqtSignal(str)
    queue_next_triggered = pyqtSignal(list)
    queue_last_triggered = pyqtSignal(list)
    tracks_deleted = pyqtSignal(list)

    def __init__(self, *args):
        super().__init__(*args)
        self._displayed_tracks: List[Track] = []
        self.loaded_displays = {}
        self.default_stylesheet = ""
        self.selected_row_index = 0
        self.playing_track = None

        self._setup_ui()
        self._setup_signals()

    def _setup_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.track_table_view = TrackTableView(self)
        self.track_table_view.horizontalHeader().setMinimumSectionSize(4)
        self.track_table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.track_table_view.verticalHeader().setVisible(False)
        self.track_table_view.setShowGrid(False)
        self.track_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.track_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.track_table_view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.track_table_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.track_table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.track_table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.track_table_view.setIconSize(QSize(22, 22))
        self.track_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.track_table_view.setFrameShape(QFrame.Shape.NoFrame)
        self.track_table_view.setAlternatingRowColors(True)
        self.track_table_view.setCornerButtonEnabled(False)
        self.track_table_view.verticalScrollBar().setStyleSheet(
            f'''
            QScrollBar {{
                border: 1px solid white;
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::add-page {{
                border: 1px solid white;
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::sub-page {{
                border: 1px solid white;
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle {{
                background: rgb(230, 230, 230);
                min-height: 25px;
            }}
            QScrollBar::handle:hover {{
                background: rgb(220, 220, 220);
                min-height: 25px;
            }}
            QScrollBar::add-line {{
                background: white;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line {{
                padding-top: {self.track_table_view.horizontalHeader().height() - 1.5}px;
                background: rgba(0, 0, 0, 0);
                border-bottom: 1px solid gray;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
            QScrollBar::vertical {{
                margin-top: {self.track_table_view.horizontalHeader().height()}px;
            }}
            '''
        )

        self.track_table_view.horizontalScrollBar().setStyleSheet(
            f'''
            QScrollBar {{
                border: 1px solid white;
                background: white;
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::add-page {{
                border: 1px solid white;
                background: white;
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::sub-page {{
                border: 1px solid white;
                background: white;
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle {{
                background: rgb(230, 230, 230);
                min-width: 25px;
            }}
            QScrollBar::handle:hover {{
                background: rgb(220, 220, 220);
                min-width: 25px;
            }}
            QScrollBar::add-line {{
                background: white;
                width: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line {{
                background: rgba(0, 0, 0, 0);
                border-bottom: 1px solid gray;
                width: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
            '''
        )

        first_col_width = 26
        second_col_width = 20
        rating_col_width = 82

        self.track_table_view.horizontalHeader().resizeSection(0, first_col_width)
        self.track_table_view.horizontalHeader().resizeSection(1, second_col_width)
        self.track_table_view.horizontalHeader().resizeSection(7, rating_col_width)
        self.track_table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.track_table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.track_table_view.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        self.main_layout.addWidget(self.track_table_view)

    def _setup_signals(self) -> None:
        self.track_table_view.track_clicked.connect(self.track_clicked.emit)
        self.track_table_view.track_double_clicked.connect(self.track_double_clicked.emit)

        self.track_table_view.play_now_triggered.connect(self.play_now_triggered.emit)
        self.track_table_view.queue_next_triggered.connect(self.queue_next_triggered.emit)
        self.track_table_view.queue_last_triggered.connect(self.queue_last_triggered.emit)
        self.track_table_view.output_to_triggered.connect(self.output_to_triggered.emit)
        self.track_table_view.tracks_deleted.connect(self.tracks_deleted.emit)

    @property
    def displayed_tracks(self) -> List[Track]:
        return self.track_table_view.displayed_tracks()

    @pyqtSlot(list)
    def set_tracks(self, tracks: List[Track]) -> None:
        self.track_table_view.set_tracks(tracks)
        self._displayed_tracks = tracks
        index = self.displayed_tracks.index(self.playing_track) if self.playing_track in self.displayed_tracks else None
        self.track_table_view.set_playing_track_index(index)
        self.track_table_view.selectionModel().clearSelection()
        self.track_table_view.scrollToTop()

    @pyqtSlot(Track)
    def set_playing_track(self, track: Track) -> None:
        self.playing_track = deepcopy(track)
        self.playing_track.queue_id = 0
        self.track_table_view.playing_track = self.playing_track
        if self.playing_track not in self.displayed_tracks:
            self.track_table_view.set_playing_track_index(None)
            return

        self.track_table_view.set_playing_track_index(self.displayed_tracks.index(self.playing_track))
        self.track_table_view.set_unpaused()

    @pyqtSlot()
    def pause_playing_track(self) -> None:
        self.track_table_view.set_paused()

    @pyqtSlot()
    def unpause_playing_track(self) -> None:
        self.track_table_view.set_unpaused()

    @pyqtSlot(list)
    def added_tracks(self, tracks: List[Track]) -> None:
        self.track_table_view.added_tracks(tracks)

    @pyqtSlot()
    def stop_playing(self):
        self.track_table_view.set_stopped()
