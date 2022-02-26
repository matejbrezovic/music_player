import math
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import *

from data_models.track import Track
from models.information_table_view import InformationTableView
from tag_manager import TagManager
from utils import *


class InformationPanel(QtWidgets.QFrame):
    track_clicked = pyqtSignal(Track)
    track_double_clicked = pyqtSignal(Track)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("information_panel")
        self.setStyleSheet("QFrame#information_panel {background-color: rgba(255, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH * 1.8)

        self.playing_tracks: List[Track] = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.playing_tracks_widget = QFrame()
        self.playing_tracks_widget_layout = QVBoxLayout(self.playing_tracks_widget)
        self.playing_tracks_widget_layout.setContentsMargins(0, 0, 0, 0)

        default_row_height = 56
        self.information_table_view = InformationTableView(self)
        self.information_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.information_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.information_table_view.setShowGrid(False)
        self.information_table_view.verticalHeader().setDefaultSectionSize(default_row_height + 4)
        self.information_table_view.horizontalHeader().setDefaultSectionSize(default_row_height + 4)
        self.information_table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.information_table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.information_table_view.setIconSize(QSize(default_row_height - 6, default_row_height - 6))
        self.information_table_view.setWordWrap(False)
        self.information_table_view.verticalHeader().setVisible(False)
        self.information_table_view.horizontalHeader().setVisible(False)
        self.information_table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.information_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.information_table_view.track_clicked.connect(self.track_clicked.emit)
        self.information_table_view.track_double_clicked.connect(self.track_double_clicked.emit)

        self.playing_tracks_widget_layout.addWidget(QLabel("Playing Tracks"))
        self.playing_tracks_widget_layout.addWidget(self.information_table_view)

        self.track_info_widget = QFrame()
        self.track_info_widget_layout = QVBoxLayout(self.track_info_widget)
        self.track_info_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area = QScrollArea()
        self.track_info_scroll_area.setWidgetResizable(True)
        self.track_info_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area_widget = QWidget()
        self.track_info_scroll_area_widget_layout = QVBoxLayout(self.track_info_scroll_area_widget)
        self.track_info_scroll_area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.track_info_scroll_area.setWidget(self.track_info_scroll_area_widget)

        self.currently_playing_track_title = ElidedLabel("No Track")
        self.currently_playing_track_info = ElidedLabel("No Info")

        artwork_pixmap = get_artwork_pixmap("")
        if not artwork_pixmap:
            artwork_pixmap = get_default_artwork_pixmap("album")
        self.currently_playing_track_image_label = ImageLabel(artwork_pixmap)

        self.track_info_scroll_area_widget_layout.addWidget(self.currently_playing_track_title)
        self.track_info_scroll_area_widget_layout.addWidget(self.currently_playing_track_info)
        self.track_info_scroll_area_widget_layout.addSpacerItem(QSpacerItem(20, 50))
        self.track_info_scroll_area_widget_layout.addWidget(self.currently_playing_track_image_label)

        self.track_info_widget_layout.addWidget(QLabel("Track Information"))
        self.track_info_widget_layout.addWidget(self.track_info_scroll_area)

        self.vertical_splitter.addWidget(self.playing_tracks_widget)
        self.vertical_splitter.addWidget(self.track_info_widget)
        self.vertical_splitter.setSizes([1, 1])
        self.main_layout.addWidget(self.vertical_splitter)
        self.artwork_pixmap = QPixmap(f"icons/album.png")
        # self.set_currently_playing_track(TracksRepository().get_tracks())

    def set_playing_tracks(self, tracks: List[Track]) -> None:
        # global_timer.timer_init()
        # global_timer.start()
        self.playing_tracks = tracks
        self.information_table_view.clearSelection()
        self.information_table_view.set_tracks(tracks)
        # global_timer.stop()

    def set_currently_playing_track(self, track: Track) -> None:
        def get_track_info(track: Track) -> str:
            f = TagManager().load_file(track.file_path)
            extension = track.file_path.split(".")[-1].upper()
            samplerate = f'{str(round(f["#samplerate"].first / 1000, 1))} kHz'
            bitrate = f'{str(math.floor(f["#bitrate"].first / 1000))}k'
            channels = "Stereo" if f["#channels"].first == 2 else "Mono"
            # print(track.length)
            return f"{extension} {bitrate}, {samplerate}, {channels}, {format_seconds(track.length)}"

        self.currently_playing_track_title.setText(track.title)
        self.currently_playing_track_info.setText(get_track_info(track))
        self.currently_playing_track_image_label.deleteLater()
        artwork_pixmap = get_artwork_pixmap(track.file_path)
        if not artwork_pixmap:
            artwork_pixmap = self.artwork_pixmap
        self.currently_playing_track_image_label = ImageLabel(artwork_pixmap)
        self.track_info_scroll_area_widget_layout.addWidget(self.currently_playing_track_image_label)

        self.information_table_view.set_currently_playing_track_index(self.playing_tracks.index(track))

    def pause_playing_track(self) -> None:
        self.information_table_view.set_paused()

    def unpause_playing_track(self) -> None:
        self.information_table_view.set_unpaused()
