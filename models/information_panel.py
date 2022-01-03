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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("information_panel")
        self.setStyleSheet("QFrame#information_panel {background-color: rgba(255, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH * 1.8)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.playing_tracks_widget = QFrame()
        self.playing_tracks_widget_layout = QVBoxLayout(self.playing_tracks_widget)
        self.playing_tracks_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.playing_tracks_table_widget = QTableWidget()
        self.playing_tracks_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.playing_tracks_table_widget.setColumnCount(1)
        self.playing_tracks_table_widget.verticalHeader().setVisible(False)
        self.playing_tracks_table_widget.horizontalHeader().setVisible(False)
        self.playing_tracks_table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playing_tracks_table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playing_tracks_table_widget.setShowGrid(False)
        self.playing_tracks_table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.playing_tracks_scroll_area_widget = QWidget()
        self.playing_tracks_layout = QVBoxLayout(self.playing_tracks_scroll_area_widget)

        self.playing_tracks_widget_layout.addWidget(QLabel("Playing Tracks"))
        self.playing_tracks_widget_layout.addWidget(self.playing_tracks_table_widget)

        self.track_info_widget = QFrame()
        self.track_info_widget_layout = QVBoxLayout(self.track_info_widget)
        self.track_info_scroll_area = QScrollArea()
        # self.track_info_scroll_area.setFixedSize(400, 500)
        self.track_info_scroll_area.setWidgetResizable(True)
        self.track_info_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area_widget = QWidget()
        self.track_info_scroll_area_widget.setStyleSheet("background-color: green")
        self.track_info_scroll_area_widget_layout = QVBoxLayout(self.track_info_scroll_area_widget)
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
        # self.vertical_splitter.setSizes([1, 1])
        self.main_layout.addWidget(self.vertical_splitter)
        self.set_playing_tracks(TracksRepository().get_tracks())

    def set_playing_tracks(self, tracks: List[Track]):
        self.reset_playing_tracks()
        self.playing_tracks_table_widget.setRowCount(len(tracks))
        for i, track in enumerate(tracks):
            track_group_widget = TrackGroupWidget(track)
            self.playing_tracks_table_widget.setCellWidget(i, 0, track_group_widget)
            self.playing_tracks_table_widget.setRowHeight(i, track_group_widget.height())

    def update_currently_playing_track(self, track: Track):
        ...

    def reset_playing_tracks(self):
        delete_items(self.playing_tracks_layout)

    # def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
    #     print(self.size())
    #     super().resizeEvent(a0)


class TrackGroupWidget(QFrame):
    clicked = pyqtSignal(Track)
    double_clicked = pyqtSignal(Track)

    def __init__(self, track: Track):
        super().__init__()
        self.title = track.title
        self.subtitle = track.artist
        self.track = track
        self.tag_manager = TagManager()

        self.default_stylesheet = "TrackGroupWidget {background-color: rgba(18, 178, 255, 0.3)}"
        self.selected_stylesheet = "TrackGroupWidget {background-color: rgba(0, 0, 0, 0.3)}"
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

    # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    #     # for group_widget in self.group_widgets:
    #     #     group_widget.setStyleSheet(self.default_stylesheet)
    #     self.setStyleSheet(self.selected_stylesheet)
    #     self.clicked.emit(self.track)
    #
    # def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
    #     # for group_widget in self.group_widgets:
    #     #     group_widget.setStyleSheet(self.default_stylesheet)
    #     self.setStyleSheet(self.selected_stylesheet)
    #     self.double_clicked.emit(self.track)
