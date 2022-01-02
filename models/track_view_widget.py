from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import *

from data_models.track import Track
from utils import ElidedLabel, delete_items


class TrackViewWidget(QFrame):
    track_double_clicked = pyqtSignal(Track)
    track_clicked = pyqtSignal(Track)
    # tracks_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks: List[Track] = []
        self.selected_color = "rgba(175, 193, 244, 0.5)"
        self.selected_row_index = 0
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("border: none")
        self.scroll_area_widget = QWidget()
        self.scroll_area_widget_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.header_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.header_splitter.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.header_splitter.setHandleWidth(0)

        self.track_info_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.track_info_splitter.setHandleWidth(0)
        self.header_splitter.splitterMoved.connect(lambda: self.track_info_splitter.setSizes(
                                                   self.header_splitter.sizes()))

        self.column_names = ["Artist", "Title", "Album", "Year", "Genre"]

        for column_name in self.column_names:
            widget = ElidedLabel("   " + column_name)
            widget.setMinimumWidth(20)
            # widget.setStyleSheet(f"background-color: rgb({randint(50, 200)},{randint(50, 200)},{randint(50, 200)})")
            self.header_splitter.addWidget(widget)
        self.header_splitter.setSizes([1, 1, 1, 1, 1])

        for i in range(len(self.column_names)):
            self.column_widget = QWidget()
            self.column_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.column_widget_layout = QVBoxLayout()
            self.column_widget_layout.setContentsMargins(0, 0, 0, 0)
            self.column_widget_layout.setSpacing(0)
            self.column_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.column_widget.setLayout(self.column_widget_layout)
            # self.column_widget.setStyleSheet(
            #     f"background-color: rgb({randint(50, 200)},{randint(50, 200)},{randint(50, 200)})")
            self.track_info_splitter.addWidget(self.column_widget)

        for child in [widget for widget in self.track_info_splitter.children() if isinstance(widget, QSplitterHandle)]:
            child.setEnabled(False)

        self.track_info_splitter.setSizes(self.header_splitter.sizes())

        self.main_layout.addWidget(self.scroll_area)
        self.scroll_area_widget_layout.addWidget(self.header_splitter)
        self.scroll_area_widget_layout.addWidget(self.track_info_splitter)

    def set_tracks(self, tracks: List[Track]):
        self.reset()
        self.displayed_tracks = tracks
        # self.tracks_changed.emit(tracks)
        for i, track in enumerate(tracks):
            for j, column_widget in enumerate([widget for widget in reversed(self.track_info_splitter.children()) if
                                               not isinstance(widget, QSplitterHandle)]):
                label = ElidedLabel(getattr(track, self.column_names[j].lower()))
                label.index = i
                label.track = track
                label.default_stylesheet = label.styleSheet()
                # label.setStyleSheet("background-color: red")
                label.setContentsMargins(5, 5, 5, 0)
                label.clicked.connect(self.row_clicked)
                label.double_clicked.connect(self.row_double_clicked)
                label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
                column_widget.layout().addWidget(label)

    def reset(self):
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            delete_items(column_widget.layout())

    def row_clicked(self, clicked_label):
        try:
            self.deselect_row_by_index(self.selected_row_index)
        except AttributeError:
            pass
        self.select_row_by_index(clicked_label.index)
        self.track_clicked.emit(clicked_label.track)

    def row_double_clicked(self, clicked_label):
        self.track_double_clicked.emit(clicked_label.track)

    def select_row_by_index(self, index: int):
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            column_widget.layout().itemAt(index).widget().setStyleSheet(f"background-color: {self.selected_color}")
        self.selected_row_index = index

    def deselect_row_by_index(self, index: int):
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            row_label = column_widget.layout().itemAt(index).widget()
            row_label.setStyleSheet(f"background-color: {row_label.default_stylesheet}")

    def select_row_by_track(self, track: Track):
        if track not in self.displayed_tracks:
            return
        self.deselect_row_by_index(self.selected_row_index)
        self.select_row_by_index(self.displayed_tracks.index(track))

    # def deselect_row_by_track(self, track: Track):
    #     if track not in self.displayed_tracks:
    #         return
    #     self.deselect_row_by_index(self.displayed_tracks.index(track))
