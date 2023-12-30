from typing import List, Optional

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHeaderView, QAbstractItemView

from constants import PANEL_MIN_WIDTH, GROUP_OPTIONS
from gui.views import GroupTableView
from repositories import CachedTracksRepository
from utils import get_embedded_artwork_pixmap, get_default_artwork_pixmap
from data_models import Track, TrackGroup


class GroupPanel(QFrame):
    group_clicked = pyqtSignal(list, tuple)
    group_double_clicked = pyqtSignal(list, tuple)

    def __init__(self, *args):
        super().__init__(*args)
        self.setStyleSheet("GroupPanel {background-color: rgba(0, 0, 0, 0.3)}")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

        self.cached_tracks_repository = CachedTracksRepository()

        self._setup_ui()
        self._setup_signals()

        self.view_key = 0
        self.group_key_changed(0)

    def _setup_ui(self) -> None:
        default_row_height = 56
        self.group_table_view = GroupTableView(self)
        self.group_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.group_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.group_table_view.setShowGrid(False)
        self.group_table_view.verticalHeader().setDefaultSectionSize(default_row_height + 4)
        self.group_table_view.horizontalHeader().setDefaultSectionSize(default_row_height + 4)
        self.group_table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.group_table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.group_table_view.setIconSize(QSize(default_row_height - 6, default_row_height - 6))
        self.group_table_view.setWordWrap(False)
        self.group_table_view.verticalHeader().setVisible(False)
        self.group_table_view.horizontalHeader().setVisible(False)
        self.group_table_view.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.group_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.group_table_view.setFrameShape(QFrame.Shape.NoFrame)
        self.group_table_view.verticalScrollBar().setStyleSheet(
            f'''
            QScrollBar {{
                border: 1px solid white;
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::add-page {{
                border: 1px solid white;
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::sub-page {{
                border: 1px solid white;
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgb(230, 230, 230);
                min-height: 25px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgb(220, 220, 220);
                min-height: 25px;
            }}
            QScrollBar::add-line:vertical {{
                background: white;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line:vertical {{
                background: white;
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
            '''
        )

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setSpacing(0)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.group_table_view)
        self.setLayout(self.vertical_layout)

    def _setup_signals(self) -> None:
        self.group_table_view.group_clicked.connect(self.group_clicked.emit)
        self.group_table_view.group_double_clicked.connect(self.group_double_clicked.emit)

    def _load_groups(self, key: int = 0) -> None:
        def get_group_pixmap(group_key: str, group_title: str) -> Optional[QPixmap]:
            tracks = self.cached_tracks_repository.get_tracks_by(group_key, group_title)  # TODO should be optimized
            artwork_pixmap = get_embedded_artwork_pixmap(tracks[0].file_path)

            if not artwork_pixmap or artwork_pixmap.isNull():
                artwork_pixmap = get_default_artwork_pixmap(group_key)
            return artwork_pixmap

        group_key: str = GROUP_OPTIONS[key].lower()
        self.groups: List[TrackGroup] = [TrackGroup("all",
                                                    f"All {group_key.capitalize()}s",
                                                    self.cached_tracks_repository.get_track_count(),
                                                    get_default_artwork_pixmap(group_key)
                                                    )]

        for title, count in self.cached_tracks_repository.get_track_counts_grouped_by_key(group_key):
            pixmap = get_group_pixmap(group_key, title)

            if title is None and group_key == "album":
                visual_title = "[Empty]"
            elif title is None:
                visual_title = "[Unknown]"
            elif title == "all":
                visual_title = f"All {group_key.capitalize()}s"
            else:
                visual_title = title

            self.groups.append(TrackGroup(title, visual_title, count, pixmap))

        self.group_table_view.set_groups(self.groups)

    @pyqtSlot(int)
    def group_key_changed(self, new_key: int) -> None:
        self.group_table_view.scrollToTop()
        self.group_table_view.selectionModel().clearSelection()
        self.group_table_view.set_group_key(GROUP_OPTIONS[new_key])
        self.view_key = new_key
        self._load_groups(new_key)

    @pyqtSlot()
    def refresh_groups(self) -> None:
        self._load_groups(self.view_key)

    def get_last_selected_tracks(self) -> List[Track]:
        if not self.group_table_view.last_group_key or not self.group_table_view.last_group_title:
            return []

        tracks = self.cached_tracks_repository.get_tracks_by(self.group_table_view.last_group_key,
                                                             self.group_table_view.last_group_title)
        return tracks
