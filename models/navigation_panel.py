from collections import defaultdict
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QScrollArea

from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from tag_manager import TagManager
from utils import *


class NavigationPanel(QtWidgets.QFrame):
    group_clicked = pyqtSignal(list)
    group_double_clicked = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.selected_group_index = 0
        self.setStyleSheet("NavigationPanel {background-color: rgba(0, 212, 88, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

        self.tag_manager = TagManager()
        self.group_options = {
            0: "Album",
            1: "Artist",
            2: "Composer",
            3: "Folder",
            4: "Genre",
            5: "Year"
        }
        self.group_container_scroll_area = QScrollArea()
        self.group_container_widget = QFrame()
        self.group_container_scroll_area.setWidget(self.group_container_widget)
        self.group_container_scroll_area.setWidgetResizable(True)
        self.group_container_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.group_container_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.group_container_layout = QtWidgets.QVBoxLayout(self.group_container_widget)
        self.group_container_layout.setContentsMargins(0, 0, 0, 0)
        self.group_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.group_combo_box = QtWidgets.QComboBox()
        self.group_combo_box.currentIndexChanged.connect(self.group_key_changed)
        self.group_combo_box.addItems(self.group_options.values())

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.group_combo_box)
        self.vertical_layout.addWidget(self.group_container_scroll_area)

    def _load_groups(self, key: int = 0):
        self.groups = defaultdict(lambda: [])
        self.group_widgets = []

        for track in TracksRepository().get_tracks():
            if self.group_options[key].lower() != "folder":
                group_key = str(getattr(track, self.group_options[key].lower()))
                self.groups["[Unknown]" if group_key == "None" else (group_key if len(group_key) > 0
                            else ("[Empty]" if key == 0 else "[Unknown]"))].append(track)
            else:
                group_key = track.file_path.split("/" if "/" in track.file_path else "\\")[-2]
                self.groups[group_key].append(track)

        self.groups = {x: self.groups[x] for x in sorted(self.groups)}
        for group in self.groups:
            title = group
            subtitle = str(str(len(self.groups[group])) + " " + ("Tracks" if self.group_combo_box.currentIndex() == 0
                                                                 else "Tracks"))[:(-1 if len(self.groups[group])
                                                                                   == 1 else 10)]
            group_widget = GroupWidget(title, subtitle, self.group_options[key], self.groups[group])
            self.group_widgets.append(group_widget)
            self.group_container_layout.addWidget(group_widget)

        for i, group_widget in enumerate(self.group_widgets):
            group_widget.group_clicked.connect(lambda clicked_group_widget: (self.update_selected_group_index(self.group_widgets.index(clicked_group_widget)),
                                                                    self.group_clicked.emit(clicked_group_widget.tracks)))
            group_widget.group_double_clicked.connect(lambda clicked_group_widget: (self.update_selected_group_index(i),
                                                      self.group_double_clicked.emit(clicked_group_widget.tracks)))
            group_widget.group_widgets = self.group_widgets

    def group_key_changed(self, new_key: int):
        delete_items(self.group_container_layout)
        self._load_groups(new_key)

    def refresh_groups(self):
        delete_items(self.group_container_layout)
        self._load_groups(self.group_combo_box.currentIndex())

    def update_selected_group_index(self, index: int):
        self.selected_group_index = index

    # def get_display_key(self):
    #     # print(self.selected_group_index)
    #     return self.group_combo_box.currentIndex(), self.selected_group_index


class GroupWidget(QFrame):
    group_clicked = pyqtSignal(QFrame)
    group_double_clicked = pyqtSignal(QFrame)

    def __init__(self, title: str, subtitle: str, group_type: str, tracks: List[Track]):
        super().__init__()
        self.default_stylesheet = "GroupWidget {background-color: rgba(18, 178, 255, 0.3)}"
        self.selected_stylesheet = "GroupWidget {background-color: rgba(0, 0, 0, 0.3)}"
        self.setStyleSheet(self.default_stylesheet)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(60)
        self.title = title
        self.subtitle = subtitle
        self.tracks = tracks
        self.tag_manager = TagManager()
        self.group_widgets = []

        self.title_label = ElidedLabel(self.title)
        self.title_label.clicked.connect(self.mousePressEvent)
        self.title_label.double_clicked.connect(self.mouseDoubleClickEvent)
        self.subtitle_label = ElidedLabel(self.subtitle)
        self.subtitle_label.clicked.connect(self.mousePressEvent)
        self.subtitle_label.double_clicked.connect(self.mouseDoubleClickEvent)
        self.subtitle_label.setStyleSheet("font-size: 10px;")
        self.image_label = QLabel()
        self.image_label.setFixedSize(60, 60)
        self.artwork_pixmap = get_artwork_pixmap(self.tracks[0].file_path, group_type)
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
        for group_widget in self.group_widgets:
            group_widget.setStyleSheet(self.default_stylesheet)
        self.setStyleSheet(self.selected_stylesheet)
        self.group_clicked.emit(self)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        for group_widget in self.group_widgets:
            group_widget.setStyleSheet(self.default_stylesheet)
        self.setStyleSheet(self.selected_stylesheet)
        self.group_double_clicked.emit(self)
