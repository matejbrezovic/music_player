import math

import music_tag
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *

from data_models import Track
from utils import (ElidedLabel, get_embedded_artwork_pixmap, get_default_artwork_pixmap, SquareImageLabel,
                   TransparentComboBox, format_seconds)


class TrackInfoWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet("border: none")
        self.setContentsMargins(0, 0, 0, 0)
        self.track_info_widget_layout = QVBoxLayout(self)
        self.track_info_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area = QScrollArea(self)
        self.track_info_scroll_area.setWidgetResizable(True)
        self.track_info_scroll_area.verticalScrollBar().setSingleStep(8)
        self.track_info_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area_widget = QWidget(self)
        self.track_info_scroll_area_widget_layout = QVBoxLayout(self.track_info_scroll_area_widget)
        self.track_info_scroll_area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.track_info_scroll_area.setWidget(self.track_info_scroll_area_widget)

        self.playing_track_title_label = ElidedLabel("No Track")
        font = self.playing_track_title_label.font()
        font.setBold(True)
        self.playing_track_title_label.setFont(font)
        self.playing_track_title_label.setContentsMargins(4, 0, 4, 0)
        self.currently_playing_track_info = ElidedLabel("No Info")
        self.currently_playing_track_info.setContentsMargins(4, 0, 4, 0)

        artwork_pixmap = get_embedded_artwork_pixmap("")
        if not artwork_pixmap:
            artwork_pixmap = get_default_artwork_pixmap("album")
        self.playing_track_image_label = SquareImageLabel(artwork_pixmap)
        self.playing_track_image_label.setUpdatesEnabled(True)
        self.playing_track_image_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.track_information_header = QWidget(self)
        self.track_information_header.setFixedHeight(24)
        self.track_information_header.setStyleSheet("background-color: rgba(0, 0, 0, 0.2);")
        self.track_information_header_layout = QHBoxLayout(self.track_information_header)
        self.track_information_header_layout.setContentsMargins(0, 0, 0, 0)
        self.track_information_header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.track_information_combo_box = TransparentComboBox(self.track_information_header)
        self.track_information_combo_box.addItem("Track Information")
        self.track_information_header_layout.addWidget(self.track_information_combo_box)

        self.track_info_scroll_area_widget_layout.addWidget(self.playing_track_title_label)
        self.track_info_scroll_area_widget_layout.addWidget(self.currently_playing_track_info)
        self.track_info_scroll_area_widget_layout.addSpacerItem(QSpacerItem(20, 40))
        self.track_info_scroll_area_widget_layout.addWidget(self.playing_track_image_label)

        self.track_info_widget_layout.addWidget(self.track_information_header)
        self.track_info_widget_layout.addWidget(self.track_info_scroll_area)

        self.artwork_pixmap = get_default_artwork_pixmap("album")

    def set_track(self, track: Track) -> None:
        self.playing_track_title_label.setText(str(track.title))
        self.currently_playing_track_info.setText(self._get_track_info(track))
        artwork_pixmap = get_embedded_artwork_pixmap(track.file_path)
        if not artwork_pixmap:
            artwork_pixmap = self.artwork_pixmap
        self.playing_track_image_label.pixmap = artwork_pixmap
        self.playing_track_image_label.setPixmap(artwork_pixmap)

    def set_track_pixmap(self, pixmap: QPixmap) -> None:
        self.playing_track_image_label.pixmap = pixmap
        self.playing_track_image_label.setPixmap(pixmap)

    @staticmethod
    def _get_track_info(t: Track) -> str:
        f = music_tag.load_file(t.file_path)
        extension = t.file_path.split(".")[-1].upper()
        sample_rate = f'{str(round(f["#samplerate"].first / 1000, 1))} kHz'
        bitrate = f'{str(math.floor(f["#bitrate"].first / 1000))}k'
        channels = "Stereo" if f["#channels"].first == 2 else "Mono"
        return f"{extension} {bitrate}, {sample_rate}, {channels}, {format_seconds(t.length)}"
