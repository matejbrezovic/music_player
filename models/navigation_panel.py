from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot

from constants import *
from data_models.navigation_group import NavigationGroup
from data_models.track import Track
from models.navigation_table_view import NavigationTableView
from repositories.cached_tracks_repository import CachedTracksRepository
from tag_manager import TagManager
from utils import *


class NavigationPanel(QFrame):
    group_clicked = pyqtSignal(list)
    group_double_clicked = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("NavigationPanel {background-color: rgba(0, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

        # self.tag_manager = TagManager()

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

        self.navigation_table_view.group_clicked.connect(self._group_clicked)
        self.navigation_table_view.group_double_clicked.connect(self.group_double_clicked.emit)

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setSpacing(0)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.navigation_table_view)

        self.view_key = 0
        self.group_key_changed(0)

    def _group_clicked(self, group_tracks: List[Track]):
        # self._last_selected_tracks = group_tracks
        self.group_clicked.emit(group_tracks)

    def _load_groups(self, key: int = 0) -> None:
        def get_group_pixmap(group_key: str, group_title: str) -> Optional[QPixmap]:
            tracks = CachedTracksRepository().get_tracks_by(group_key, group_title)  # TODO should be optimized
            artwork_pixmap = get_artwork_pixmap(tracks[0].file_path)

            if not artwork_pixmap:
                if group_key in ["artist", "composer"]:
                    return QPixmap("icons/artist.png")
                elif group_key == "album":
                    return QPixmap("icons/album.png")
                elif group_key == "folder":
                    return QPixmap("icons/folder.png")
                else:
                    return QPixmap("icons/misc.png")
            return artwork_pixmap

        self.groups: List[NavigationGroup] = []

        group_key = GROUP_OPTIONS[key].lower()
        for title, count in CachedTracksRepository().get_track_counts_grouped_by(group_key):
            pixmap = get_group_pixmap(group_key, title)

            if title is None and group_key == "album":
                visual_title = "[Empty]"
            elif title is None and group_key == "artist":
                visual_title = "[Unknown]"
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
        # self._last_selected_tracks = self.navigation_table_view.get_tracks_from_selected_group()

    @pyqtSlot(list)
    def removed_tracks(self) -> None:
        ...

    # def get_tracks_from_selected_group(self) -> List[Track]:
    #     return self.navigation_table_view.get_tracks_from_selected_group()

    def get_last_selected_tracks(self) -> List[Track]:
        if not self.navigation_table_view.last_group_key or not self.navigation_table_view.last_group_title:
            return []

        tracks = CachedTracksRepository().get_tracks_by(self.navigation_table_view.last_group_key,
                                                        self.navigation_table_view.last_group_title)
        return tracks


