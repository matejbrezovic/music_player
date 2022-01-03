import random
import string
import sys
from random import randint
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from tests.simplified_track_view_widget_test import TestTrackViewWidget

from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import ElidedLabel, delete_items


class CustomScrollArea(QScrollArea):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.distance_from_top = 0
        self.tracks = []
        # print(self.height())
        self.coef = 1
        self.offset = 1400
        self.load_pack = 3

    def scrollContentsBy(self, dx, dy):
        self.distance_from_top -= dy
        # print(self.distance_from_top)

        if self.distance_from_top > self.offset // 20 + self.coef * 20 * self.load_pack:
            self.display_tracks(self.tracks[self.offset // 20 + ((self.coef-1) * self.load_pack):self.offset // 20 + (self.coef * self.load_pack)])
            print("Displayed", self.coef)
            self.coef += 1
        super().scrollContentsBy(dx, dy)

    def set_tracks(self, tracks: List[Track]):
        self.tracks = tracks
        self.display_tracks(tracks[:self.offset // 20])

    def display_tracks(self, tracks):
        for i, track in enumerate(tracks):
            for j, column_widget in enumerate([widget for widget in reversed(self.parent.track_info_splitter.children()) if
                                               not isinstance(widget, QSplitterHandle)]):
                label = ElidedLabel(getattr(track, self.parent.column_names[j].lower()))
                label.index = self.tracks.index(tracks[i])
                label.default_stylesheet = label.styleSheet()
                label.setContentsMargins(5, 5, 5, 0)
                label.clicked.connect(self.parent.row_clicked)
                label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
                if label.index % 3 == 0:
                    label.setStyleSheet(f"background-color: red")
                # label.resize(100, 100)
                label.setFixedHeight(20)
                column_widget.layout().addWidget(label)
        # print(self.parent.)


class TestTrackViewWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = "red"
        self.selected_row_index = 0
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area = CustomScrollArea(self)
        self.scroll_area.setStyleSheet("border: none")
        self.scroll_area_widget = QWidget()
        self.scroll_area_widget_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.header_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.header_splitter.setHandleWidth(0)

        self.track_info_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.track_info_splitter.setHandleWidth(0)
        self.header_splitter.splitterMoved.connect(lambda: self.track_info_splitter.setSizes(
                                                   self.header_splitter.sizes()))

        self.column_names = ["Artist", "Title", "Album", "Year", "Genre"]

        for column_name in self.column_names:
            widget = ElidedLabel("   " + column_name)
            widget.setMinimumWidth(20)
            widget.setStyleSheet(f"background-color: rgb({randint(50, 200)},{randint(50, 200)},{randint(50, 200)})")
            self.header_splitter.addWidget(widget)
        self.header_splitter.setSizes([1, 1, 1, 1, 1])

        for i in range(len(self.column_names)):
            self.column_widget = QWidget()
            self.column_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.column_widget_layout = QVBoxLayout()
            self.column_widget_layout.setContentsMargins(0, 0, 0, 0)
            self.column_widget_layout.setSpacing(0)
            self.column_widget.setLayout(self.column_widget_layout)
            self.column_widget.setStyleSheet(
                f"background-color: rgb({randint(50, 200)},{randint(50, 200)},{randint(50, 200)})")
            self.track_info_splitter.addWidget(self.column_widget)

        for child in [widget for widget in self.track_info_splitter.children() if isinstance(widget, QSplitterHandle)]:
            child.setEnabled(False)

        self.track_info_splitter.setSizes(self.header_splitter.sizes())

        self.main_layout.addWidget(self.scroll_area)
        self.scroll_area_widget_layout.addWidget(self.header_splitter)
        self.scroll_area_widget_layout.addWidget(self.track_info_splitter)

    def add_tracks(self, tracks: List[Track]):
        self.reset()
        self.scroll_area.set_tracks(tracks)

    def row_clicked(self, clicked_label):
        self.select_row(clicked_label.index)

    def reset(self):
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            delete_items(column_widget.layout())

    def select_row(self, index: int):
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            row_label = column_widget.layout().itemAt(self.selected_row_index).widget()
            row_label.setStyleSheet(f"background-color: {row_label.default_stylesheet}")
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            column_widget.layout().itemAt(index).widget().setStyleSheet(f"background-color: {self.selected_color}")
        self.selected_row_index = index


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Testing widget'

        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 600, 600)

        self.track_view_widget = TestTrackViewWidget()
        self.refresh_button = QPushButton("Refresh")
        print(len(TracksRepository().get_tracks() * 10))
        self.refresh_button.clicked.connect(self.button_clicked)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.track_view_widget)
        self.layout.addWidget(self.refresh_button)
        self.setLayout(self.layout)

        self.show()
        self.counter = 1
    def button_clicked(self):
        if self.counter == 1:
            self.track_view_widget.add_tracks(TracksRepository().get_tracks() * 10)
        else:
            self.track_view_widget.scroll_area.display_tracks(self.generate_tracks(10))

    def generate_tracks(self, num):
        tracks = []
        for i in range(num):
            tracks.append(Track(i,
                                *[(''.join(random.choice(string.ascii_lowercase) for _ in range(10))) for _ in range(8)]
                                ))
        return tracks


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
