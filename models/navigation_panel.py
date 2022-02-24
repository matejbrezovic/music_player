import time
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import *

from data_models.navigation_group import NavigationGroup
from models.navigation_table_view import NavigationTableView
from repositories.cached_tracks_repository import CachedTracksRepository
from tag_manager import TagManager
from utils import *


class NavigationPanel(QFrame):
    group_clicked = pyqtSignal(list)
    group_double_clicked = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
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

        default_row_height = 56
        self.navigation_table_view = NavigationTableView()
        self.navigation_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navigation_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navigation_table_view.setShowGrid(False)
        self.navigation_table_view.verticalHeader().setDefaultSectionSize(default_row_height + 4)
        self.navigation_table_view.horizontalHeader().setDefaultSectionSize(default_row_height + 4)
        self.navigation_table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.navigation_table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.navigation_table_view.setIconSize(QSize(default_row_height - 6, default_row_height - 6))
        self.navigation_table_view.setWordWrap(False)
        self.navigation_table_view.verticalHeader().setVisible(False)
        self.navigation_table_view.horizontalHeader().setVisible(False)
        self.navigation_table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.navigation_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.navigation_table_view.group_clicked.connect(self.group_clicked.emit)
        self.navigation_table_view.group_double_clicked.connect(self.group_double_clicked.emit)
        self.group_combo_box = QtWidgets.QComboBox()
        self.group_combo_box.currentIndexChanged.connect(self.group_key_changed)
        self.group_combo_box.addItems(self.group_options.values())

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.group_combo_box)
        self.vertical_layout.addWidget(self.navigation_table_view)

    def _load_groups(self, key: int = 0) -> None:
        def get_group_pixmap(group_key: str, group_title: str) -> Optional[QPixmap]:
            # tracks = CachedTracksRepository().get_tracks_by(group_key, group_title)  # TODO should be optimized
            pixmap = None  # get_artwork_pixmap(tracks[0].file_path)

            # group_key = group_key.lower()
            if not pixmap:
                if group_key in ["artist", "composer"]:
                    pixmap = QPixmap("icons/artist.png")
                elif group_key == "album":
                    pixmap = QPixmap("icons/album.png")
                elif group_key == "folder":
                    pixmap = QPixmap("icons/folder.png")
                else:
                    pixmap = QPixmap("icons/misc.png")
            return pixmap

        start = time.time()
        self.groups: List[NavigationGroup] = []

        group_key = self.group_options[key].lower()
        for title, count in CachedTracksRepository().get_track_counts_grouped_by(group_key):
            pixmap = get_group_pixmap(group_key, title)
            self.groups.append(NavigationGroup(title, count, pixmap))

        print("Groups created in:", time.time() - start)
        self.navigation_table_view.set_groups(self.groups)
        print("Groups fully displayed in:", time.time() - start)

    def group_key_changed(self, new_key: int) -> None:
        self.navigation_table_view.set_group_key(self.group_options[new_key])
        self._load_groups(new_key)

    def refresh_groups(self) -> None:
        self._load_groups(self.group_combo_box.currentIndex())
