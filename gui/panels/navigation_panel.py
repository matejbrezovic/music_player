from typing import List, Optional

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHeaderView, QAbstractItemView

from constants import PANEL_MIN_WIDTH, GROUP_OPTIONS
from data_models.navigation_group import NavigationGroup
from data_models.track import Track
from gui.views.navigation_table_view import NavigationTableView
from repositories.cached_tracks_repository import CachedTracksRepository
from utils import get_embedded_artwork_pixmap, get_default_artwork_pixmap


class NavigationPanel(QFrame):
    group_clicked = pyqtSignal(list, tuple)
    group_double_clicked = pyqtSignal(list, tuple)

    def __init__(self, *args):
        super().__init__(*args)
        self.setStyleSheet("NavigationPanel {background-color: rgba(0, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

        self.cached_tracks_repository = CachedTracksRepository()

        self._last_group_key = None
        self._last_group_title = None

        default_row_height = 56
        self.navigation_table_view = NavigationTableView()
        self.navigation_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
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
        self.navigation_table_view.setFrameShape(QFrame.Shape.NoFrame)

        self.navigation_table_view.group_clicked.connect(self.group_clicked.emit)
        self.navigation_table_view.group_double_clicked.connect(self.group_double_clicked.emit)

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setSpacing(0)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.navigation_table_view)
        self.setLayout(self.vertical_layout)

        self.view_key = 0
        self.group_key_changed(0)

    def _load_groups(self, key: int = 0) -> None:
        def get_group_pixmap(group_key: str, group_title: str) -> Optional[QPixmap]:
            tracks = self.cached_tracks_repository.get_tracks_by(group_key, group_title)  # TODO should be optimized
            artwork_pixmap = get_embedded_artwork_pixmap(tracks[0].file_path)

            if not artwork_pixmap:
                if group_key in ("artist", "composer"):
                    return QPixmap("icons/artist.png")
                elif group_key == "album":
                    return QPixmap("icons/album.png")
                elif group_key == "folder":
                    return QPixmap("icons/folder.png")
                else:
                    return QPixmap("icons/misc.png")
            return artwork_pixmap

        group_key: str = GROUP_OPTIONS[key].lower()
        self.groups: List[NavigationGroup] = [NavigationGroup("all",
                                                              f"All {group_key.capitalize()}s",
                                                              self.cached_tracks_repository.get_track_count(),
                                                              get_default_artwork_pixmap(group_key)
                                                              )]

        for title, count in self.cached_tracks_repository.get_track_counts_grouped_by(group_key):
            pixmap = get_group_pixmap(group_key, title)

            if title is None and group_key == "album":
                visual_title = "[Empty]"
            elif title is None:
                visual_title = "[Unknown]"
            elif title == "all":
                visual_title = f"All {group_key.capitalize()}s"
            else:
                visual_title = title

            self.groups.append(NavigationGroup(title, visual_title, count, pixmap))

        self.navigation_table_view.set_groups(self.groups)

    @pyqtSlot(int)
    def group_key_changed(self, new_key: int) -> None:
        self.navigation_table_view.selectionModel().clearSelection()
        self.navigation_table_view.scrollToTop()
        self.navigation_table_view.set_group_key(GROUP_OPTIONS[new_key])
        self.view_key = new_key
        self._load_groups(new_key)

    @pyqtSlot()
    def refresh_groups(self) -> None:
        self._load_groups(self.view_key)

    @pyqtSlot(list)
    def added_tracks(self) -> None:
        return

    @pyqtSlot(list)
    def removed_tracks(self) -> None:
        ...

    def get_last_selected_tracks(self) -> List[Track]:
        if not self.navigation_table_view.last_group_key or not self.navigation_table_view.last_group_title:
            return []

        tracks = self.cached_tracks_repository.get_tracks_by(self.navigation_table_view.last_group_key,
                                                             self.navigation_table_view.last_group_title)
        return tracks
