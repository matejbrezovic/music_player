from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from tag_manager import TagManager
from collections import defaultdict

from constants import *
from utils import *


class NavigationPanel(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet("NavigationPanel {background-color: rgba(0, 212, 88, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)
        # self.setContentsMargins(0, 0, 0, 0)

        self.tag_manager = TagManager()
        self.group_options = {
            0: "Album",
            1: "Artist"
        }
        self.group_container_widget = QtWidgets.QFrame()
        self.group_container_layout = QtWidgets.QVBoxLayout(self.group_container_widget)
        self.group_container_layout.setContentsMargins(0, 0, 0, 0)
        self.group_combo_box = QtWidgets.QComboBox()
        self.group_combo_box_index = 0
        self.group_combo_box.currentIndexChanged.connect(self.group_key_changed)
        self.group_combo_box.addItems(self.group_options.values())

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.group_combo_box)
        self.vertical_layout.addWidget(self.group_container_widget)

    def _load_groups(self, key: int = 0):
        self.groups = defaultdict(lambda: [])

        for track in TRACKS:
            track_file = self.tag_manager.load_file(track)
            self.groups[track_file[self.group_options[key]].value].append(track)

        for group in self.groups:
            title = group
            subtitle = str(len(self.groups[group])) + " " + ("Tracks" if self.group_combo_box_index == 0 else "Albums")[0]
            group_widget = GroupWidget(title, subtitle)
            self.group_container_layout.addWidget(group_widget)
        self.group_container_layout.update()

    def group_key_changed(self, new_key: int):
        self.group_combo_box_index = new_key
        delete_items(self.group_container_layout)
        self._load_groups(new_key)


class GroupWidget(QtWidgets.QFrame):
    def __init__(self, title: str, subtitle: str):
        super().__init__()
        self.setStyleSheet("background-color: rgba(18, 178, 255, 0.3)")
        self.setContentsMargins(0, 0, 0, 0)
        self.title = title
        self.subtitle = subtitle

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(QLabel(self.title))
        self.vertical_layout.addWidget(QLabel(self.subtitle))

