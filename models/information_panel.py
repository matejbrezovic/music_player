import math
from typing import List

from PyQt6.QtCore import pyqtSlot

from constants import *
from data_models.track import Track
from models.information_table_view import InformationTableView
from tag_manager import TagManager
from utils import *


class InformationPanel(QFrame):
    track_clicked = pyqtSignal(Track, int)
    track_double_clicked = pyqtSignal(Track, int)

    def __init__(self, *args):
        super().__init__(*args)
        # self.setObjectName("information_panel")
        # self.setStyleSheet("InformationPanel {background-color: rgba(0, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

        self.playing_tracks: List[Track] = []

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
        self.information_table_view = InformationTableView(self)
        self.information_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.information_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.information_table_view.setShowGrid(False)
        self.information_table_view.setFrameShape(QFrame.Shape.NoFrame)
        self.information_table_view.verticalHeader().setDefaultSectionSize(default_row_height + 2)
        self.information_table_view.horizontalHeader().setDefaultSectionSize(default_row_height + 2)
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

        # self.playing_tracks_widget_layout.addWidget(self.information_panel_combo_box)
        self.playing_tracks_widget_layout.addWidget(self.information_table_view)

        self.track_info_widget = QWidget(self)
        self.track_info_widget.setStyleSheet("border: none")
        self.track_info_widget.setContentsMargins(0, 0, 0, 0)
        self.track_info_widget_layout = QVBoxLayout(self.track_info_widget)
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
        # self.currently_playing_track_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.currently_playing_track_info = ElidedLabel("No Info")
        self.currently_playing_track_info.setContentsMargins(4, 0, 4, 0)
        # self.currently_playing_track_info.setStyleSheet("background-color: red")

        artwork_pixmap = get_artwork_pixmap("")
        if not artwork_pixmap:
            artwork_pixmap = get_default_artwork_pixmap("album")
        self.playing_track_image_label = SpecificImageLabel(artwork_pixmap)
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

        self.vertical_splitter.addWidget(self.playing_tracks_widget)
        self.vertical_splitter.addWidget(self.track_info_widget)
        self.vertical_splitter.setSizes([1, 1])
        self.main_layout.addWidget(self.vertical_splitter)
        self.artwork_pixmap = QPixmap(f"icons/album.png")
        # self.main_layout.setSpacing(0)
        # self.set_currently_playing_track(TracksRepository().get_tracks())

    def view_key_changed(self, key: int) -> None:
        ...

    def set_playing_tracks(self, tracks: List[Track]) -> None:
        # global_timer.timer_init()
        # global_timer.start()
        self.playing_tracks = tracks
        self.information_table_view.clearSelection()
        self.information_table_view.set_tracks(tracks)
        # global_timer.stop()

    @pyqtSlot(Track, int)
    def set_playing_track(self, track: Track, track_index: int = None) -> None:
        def get_track_info(t: Track) -> str:
            f = TagManager().load_file(t.file_path)
            extension = t.file_path.split(".")[-1].upper()
            samplerate = f'{str(round(f["#samplerate"].first / 1000, 1))} kHz'
            bitrate = f'{str(math.floor(f["#bitrate"].first / 1000))}k'
            channels = "Stereo" if f["#channels"].first == 2 else "Mono"
            return f"{extension} {bitrate}, {samplerate}, {channels}, {format_seconds(t.length)}"

        self.playing_track_title_label.setText(str(track.title))
        self.currently_playing_track_info.setText(get_track_info(track))
        artwork_pixmap = get_artwork_pixmap(track.file_path)
        if not artwork_pixmap:
            artwork_pixmap = self.artwork_pixmap
        self.playing_track_image_label.pixmap = artwork_pixmap
        self.playing_track_image_label.setPixmap(artwork_pixmap)

        # print("Inf index:", track_index)
        if track_index is None:
            self.information_table_view.set_currently_playing_track_index(self.playing_tracks.index(track))
        else:
            self.information_table_view.set_currently_playing_track_index(track_index)

    # def set_playing_track_index(self):

    def pause_playing_track(self) -> None:
        self.information_table_view.set_paused()

    def unpause_playing_track(self) -> None:
        self.information_table_view.set_unpaused()

    def stop_playing(self) -> None:
        self.information_table_view.stop_playing()
