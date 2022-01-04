from collections import defaultdict
from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *

from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from tag_manager import TagManager
from utils import *


class NavigationPanel(QFrame):
    group_clicked = pyqtSignal(list)
    group_double_clicked = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
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
        self.group_table_widget = QTableWidget()
        self.group_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.group_table_widget.setColumnCount(1)
        self.group_table_widget.verticalHeader().setVisible(False)
        self.group_table_widget.horizontalHeader().setVisible(False)
        self.group_table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.group_table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.group_table_widget.setShowGrid(False)
        self.group_table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.group_table_widget.cellClicked.connect(lambda row_index, _: self.row_clicked(row_index))
        self.group_table_widget.cellDoubleClicked.connect(lambda row_index, _: self.row_double_clicked(row_index))

        self.group_combo_box = QtWidgets.QComboBox()
        self.group_combo_box.currentIndexChanged.connect(self.group_key_changed)
        self.group_combo_box.addItems(self.group_options.values())

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vertical_layout.addWidget(self.group_combo_box)
        self.vertical_layout.addWidget(self.group_table_widget)

    def row_clicked(self, row_index: int):
        self.group_table_widget.setCurrentCell(row_index, 0)
        self.group_clicked.emit(self.group_table_widget.cellWidget(row_index, 0).tracks)

    def row_double_clicked(self, row_index: int):
        self.group_table_widget.setCurrentCell(row_index, 0)
        self.group_double_clicked.emit(self.group_table_widget.cellWidget(row_index, 0).tracks)

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
        self.group_table_widget.setRowCount(len(self.groups))
        for i, group in enumerate(self.groups):
            title = group
            subtitle = str(str(len(self.groups[group])) + " " + ("Tracks" if self.group_combo_box.currentIndex() == 0
                                                                 else "Tracks"))[:(-1 if len(self.groups[group])
                                                                                   == 1 else 10)]
            group_widget = GroupWidget(title, subtitle, self.group_options[key], self.groups[group], i)
            group_widget.clicked.connect(self.row_clicked)
            group_widget.double_clicked.connect(self.row_double_clicked)
            self.group_table_widget.setCellWidget(i, 0, group_widget)
            self.group_table_widget.setRowHeight(i, group_widget.height())

    def group_key_changed(self, new_key: int):
        self._load_groups(new_key)

    def refresh_groups(self):
        self._load_groups(self.group_combo_box.currentIndex())


class GroupWidget(QFrame):
    clicked = pyqtSignal(int)
    double_clicked = pyqtSignal(int)

    def __init__(self, title: str, subtitle: str, group_type: str, tracks: List[Track], index: int):
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
        self.index = index

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
        self.clicked.emit(self.index)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.double_clicked.emit(self.index)
