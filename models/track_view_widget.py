from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from data_models.track import Track
from utils import ElidedLabel, delete_items


class TrackViewWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = "rgba(175, 193, 244, 0.5)"
        self.selected_row_index = 0
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("border: none")
        self.scroll_area_widget = QWidget()
        self.scroll_area_widget_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_widget_layout.setContentsMargins(0, 0, 0, 0)
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
            # widget.setStyleSheet(f"background-color: rgb({randint(50, 200)},{randint(50, 200)},{randint(50, 200)})")
            self.header_splitter.addWidget(widget)
        self.header_splitter.setSizes([1, 1, 1, 1, 1])

        for i in range(len(self.column_names)):
            self.column_widget = QWidget()
            self.column_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.column_widget_layout = QVBoxLayout()
            self.column_widget_layout.setContentsMargins(0, 0, 0, 0)
            self.column_widget_layout.setSpacing(0)
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
        for i, track in enumerate(tracks):
            for j, column_widget in enumerate([widget for widget in reversed(self.track_info_splitter.children()) if
                                               not isinstance(widget, QSplitterHandle)]):
                label = ElidedLabel(getattr(track, self.column_names[j].lower()))
                label.index = i
                label.default_stylesheet = label.styleSheet()
                label.setContentsMargins(5, 5, 5, 0)
                label.clicked.connect(self.row_clicked)
                label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
                column_widget.layout().addWidget(label)

    def reset(self):
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                                               not isinstance(widget, QSplitterHandle)]:
            delete_items(column_widget.layout())

    def row_clicked(self, clicked_label):
        self.select_row(clicked_label.index)

    def select_row(self, index: int):
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            row_label = column_widget.layout().itemAt(self.selected_row_index).widget()
            row_label.setStyleSheet(f"background-color: {row_label.default_stylesheet}")
        for column_widget in [widget for widget in reversed(self.track_info_splitter.children()) if
                              not isinstance(widget, QSplitterHandle)]:
            column_widget.layout().itemAt(index).widget().setStyleSheet(f"background-color: {self.selected_color}")
        self.selected_row_index = index