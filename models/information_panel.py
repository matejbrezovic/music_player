import datetime
import math
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from constants import *
from PyQt6.QtWidgets import *

from data_models.track import Track
from repositories.tracks_repository import TracksRepository
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

        # policy = QSizePolicy()
        # policy.setHorizontalStretch(0)
        # policy.setVerticalStretch(0)
        # self.setSizePolicy(policy)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.playing_tracks_widget = QFrame()
        self.playing_tracks_widget_layout = QVBoxLayout(self.playing_tracks_widget)
        self.playing_tracks_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.playing_tracks_table_widget = QTableWidget()
        # self.playing_tracks_table_widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.playing_tracks_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.playing_tracks_table_widget.setColumnCount(1)
        self.playing_tracks_table_widget.verticalHeader().setVisible(False)
        self.playing_tracks_table_widget.horizontalHeader().setVisible(False)
        self.playing_tracks_table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playing_tracks_table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playing_tracks_table_widget.setShowGrid(False)
        self.playing_tracks_table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.playing_tracks_table_widget.setStyleSheet(
            "selection-background-color: rgba(166, 223, 231, 0.8); selection-color: black")
        self.playing_tracks_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.playing_tracks_widget_layout.addWidget(QLabel("Playing Tracks"))
        self.playing_tracks_widget_layout.addWidget(self.playing_tracks_table_widget)

        self.track_info_widget = QFrame()
        self.track_info_widget_layout = QVBoxLayout(self.track_info_widget)
        self.track_info_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area = QScrollArea()
        # self.track_info_scroll_area.setFixedSize(400, 500)
        self.track_info_scroll_area.setWidgetResizable(True)
        self.track_info_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area_widget = QWidget()
        self.track_info_scroll_area_widget_layout = QVBoxLayout(self.track_info_scroll_area_widget)
        self.track_info_scroll_area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.track_info_scroll_area.setWidget(self.track_info_scroll_area_widget)

        self.currently_playing_track_title = ElidedLabel("No Track")
        self.currently_playing_track_info = ElidedLabel("No info")
        self.currently_playing_track_image_label = ImageLabel(get_artwork_pixmap("", "album"))

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
        self.set_playing_tracks(TracksRepository().get_tracks())
        # self.set_currently_playing_track(TracksRepository().get_tracks()[0])

    def row_clicked(self, row_index: int):
        self.playing_tracks_table_widget.setCurrentCell(row_index, 0)
        self.track_clicked.emit(self.playing_tracks_table_widget.cellWidget(row_index, 0).track)

    def row_double_clicked(self, row_index: int):
        self.playing_tracks_table_widget.setCurrentCell(row_index, 0)
        self.track_double_clicked.emit(self.playing_tracks_table_widget.cellWidget(row_index, 0).track)

    def set_playing_tracks(self, tracks: List[Track]):
        self.playing_tracks_table_widget.clearSelection()
        self.playing_tracks_table_widget.setRowCount(len(tracks))
        for i, track in enumerate(tracks):
            track_group_widget = TrackGroupWidget(track, i)
            track_group_widget.clicked.connect(self.row_clicked)
            track_group_widget.double_clicked.connect(self.row_double_clicked)
            self.playing_tracks_table_widget.setCellWidget(i, 0, track_group_widget)
            self.playing_tracks_table_widget.setRowHeight(i, track_group_widget.height())

    def set_currently_playing_track(self, track: Track):
        def get_track_info(track: Track) -> str:
            f = TagManager().load_file(track.file_path)
            extension = track.file_path.split(".")[-1].upper()
            samplerate = f'{str(round(f["#samplerate"].first / 1000, 1))} kHz'
            bitrate = f'{str(math.floor(f["#bitrate"].first / 1000))}k'
            channels = "Stereo" if f["#channels"].first == 2 else "Mono"
            print(track.length)
            return f"{extension} {bitrate}, {samplerate}, {channels}, {format_seconds(track.length)}"

        self.currently_playing_track_title.setText(track.title)
        self.currently_playing_track_info.setText(get_track_info(track))
        self.currently_playing_track_image_label.deleteLater()
        self.currently_playing_track_image_label = ImageLabel(get_artwork_pixmap(track.file_path))
        self.track_info_scroll_area_widget_layout.addWidget(self.currently_playing_track_image_label)


class TrackGroupWidget(QFrame):
    clicked = pyqtSignal(int)
    double_clicked = pyqtSignal(int)

    def __init__(self, track: Track, index: int):
        super().__init__()
        self.title = track.title
        self.subtitle = track.artist
        self.track = track
        self.tag_manager = TagManager()
        self.index = index

        self.default_stylesheet = ""  # "TrackGroupWidget {background-color: rgba(18, 178, 255, 0.3)}"
        # self.selected_stylesheet = "TrackGroupWidget {background-color: rgba(0, 0, 0, 0.3)}"
        self.setStyleSheet(self.default_stylesheet)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(60)

        self.title_label = ElidedLabel(self.title)
        self.title_label.clicked.connect(self.mousePressEvent)
        self.title_label.double_clicked.connect(self.mouseDoubleClickEvent)
        self.subtitle_label = ElidedLabel(self.subtitle)
        self.subtitle_label.clicked.connect(self.mousePressEvent)
        self.subtitle_label.double_clicked.connect(self.mouseDoubleClickEvent)
        self.subtitle_label.setStyleSheet("font-size: 10px;")
        self.image_label = QLabel()
        self.image_label.setFixedSize(60, 60)
        self.artwork_pixmap = get_artwork_pixmap(track.file_path, "album")
        self.image_label.setPixmap(self.artwork_pixmap.scaled(self.image_label.width() - 4,
                                                              self.image_label.height() - 4,
                                                              Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation))

        self.text_widget = QWidget()
        self.vertical_layout = QtWidgets.QVBoxLayout(self.text_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setSpacing(0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.title_label)
        self.vertical_layout.addWidget(self.subtitle_label)

        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.addWidget(self.image_label)
        self.horizontal_layout.addWidget(self.text_widget)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.clicked.emit(self.index)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.double_clicked.emit(self.index)
