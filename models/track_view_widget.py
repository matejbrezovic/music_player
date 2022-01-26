import typing
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *

from data_models.track import Track
from utils import *
from constants import *
import global_timer


class TrackViewWidget(QFrame):
    track_double_clicked = pyqtSignal(Track)
    track_clicked = pyqtSignal(Track)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks: List[Track] = []
        self.loaded_displays = {}
        # self.selection_color = "rgba(166, 223, 231, 0.8)"
        # self.lost_focus_color = "rgba(0, 0, 0, 0.2)"
        # self.selection_stylesheet = f"selection-background-color: {self.selection_color}; selection-color: black"
        # self.lost_focus_stylesheet = f"selection-background-color: {self.lost_focus_color}; selection-color: black"
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

        for column_name in self.column_names:
            widget = ElidedLabel("" + column_name)
            widget.setMinimumWidth(20)
            self.header_splitter.addWidget(widget)

        self.table_widget = ChangeStylesheetOnClickTableWidget(self)
        self.table_widget.horizontalHeader().setMinimumSectionSize(20)
        self.table_widget.setColumnCount(len(self.column_names))
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.itemClicked.connect(
            lambda item: (self.track_clicked.emit(item.track),
                          self.set_selected_row_index(self.table_widget.row(item))))
        self.table_widget.itemDoubleClicked.connect(self.double_clicked)

        self.table_widget.setStyleSheet(SELECTION_STYLESHEET)

        self._focus_frame = FocusFrame(self.table_widget)
        self._focus_frame.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.header_splitter.setCollapsible(0, False)
        self.header_splitter.setCollapsible(1, False)
        self.header_splitter.widget(0).setFixedWidth(22)
        self.header_splitter.widget(1).setFixedWidth(16)
        self.table_widget.setColumnWidth(0, 22)
        self.table_widget.setColumnWidth(1, 16)

        self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self._focus_frame)

    def double_clicked(self, item: QTableWidgetItem):
        global_timer.timer_init()
        global_timer.start()
        self.track_double_clicked.emit(item.track)
        self.set_selected_row_index(self.table_widget.row(item))

    def update_column_width(self) -> None:
        total_sizes = sum(self.header_splitter.sizes())
        if not total_sizes:
            return
        for i in range(len(self.column_names)):
            self.table_widget.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))

    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_widget.setRowCount(len(tracks))
        self.table_widget.clearSelection()
        self.displayed_tracks = tracks

        for i, track in enumerate(tracks):
            for j in range(len(self.column_names)):
                item = QTableWidgetItem()
                try:
                    item_text = getattr(track, self.column_names[j].lower())
                except AttributeError:
                    item_text = None
                item.setText(str(item_text) if item_text else "")
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.track = track
                self.table_widget.setItem(i, j, item)
                # self.table_widget.setCellWidget(i, j, ElidedLabel(str(item_text))) # TODO for better text eliding

            speaker_label = SpeakerLabel()
            # speaker_label.setFixedSize(22, 16)
            speaker_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label = ImageLabel(track.artwork_pixmap) if track.artwork_pixmap else QLabel("-")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setFixedSize(22, 22)
            self.table_widget.setCellWidget(i, 1, speaker_label)
            self.table_widget.setCellWidget(i, 0, image_label)

            self.table_widget.setRowHeight(i, 22)

    def set_selected_row_index(self, index: int) -> None:
        self.selected_row_index = index

    def select_row_by_index(self, index: int) -> None:
        self.table_widget.selectRow(index)
        self.set_selected_row_index(index)

    def select_row_by_track(self, track: Track) -> None:
        if track not in self.displayed_tracks:
            self.table_widget.clearSelection()
            return
        self.select_row_by_index(self.displayed_tracks.index(track))

    def set_playing_track(self, track: Track) -> None:
        def reset_track_column() -> None:
            for i in range(self.table_widget.rowCount()):
                try:
                    typing.cast(SpeakerLabel, self.table_widget.cellWidget(i, 1)).set_transparent()
                except AttributeError:
                    pass

        reset_track_column()
        if track not in self.displayed_tracks:
            return

        self.playing_track = track
        typing.cast(SpeakerLabel, self.table_widget.cellWidget(self.displayed_tracks.index(track), 1)).set_playing()

    def pause_playing_track(self) -> None:
        typing.cast(SpeakerLabel, self.table_widget.cellWidget(
            self.displayed_tracks.index(self.playing_track), 1)).set_paused()

    def unpause_playing_track(self) -> None:
        typing.cast(SpeakerLabel, self.table_widget.cellWidget(
            self.displayed_tracks.index(self.playing_track), 1)).set_playing()
