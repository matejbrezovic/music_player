from typing import List

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout

from utils import TransparentComboBox
from constants import *


class HeaderMenu(QWidget):
    main_panel_view_key_changed = pyqtSignal(int)
    navigation_panel_group_key_changed = pyqtSignal(int)
    information_panel_view_key_changed = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedHeight(24)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        self.setContentsMargins(0, 0, 0, 0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.main_splitter.setContentsMargins(0, 0, 0, 0)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(0)

        self.main_panel_view_options_combo_box = TransparentComboBox(self)
        self.main_panel_view_options_combo_box.setFixedSize(150, 24)
        self.main_panel_view_options_combo_box.currentIndexChanged.connect(self.main_panel_view_key_changed.emit)
        self.main_panel_view_options_combo_box.addItems(MAIN_PANAL_VIEW_OPTIONS)

        self.navigation_panel_group_combo_box = TransparentComboBox(self)
        self.navigation_panel_group_combo_box.currentIndexChanged.connect(self.navigation_panel_group_key_changed.emit)
        self.navigation_panel_group_combo_box.addItems(GROUP_OPTIONS)
        self.navigation_panel_group_combo_box.setFixedHeight(24)

        self.information_panel_view_key_combo_box = TransparentComboBox(self)
        self.information_panel_view_key_combo_box.addItem("Playing Tracks")
        self.information_panel_view_key_combo_box.setFixedHeight(24)
        self.information_panel_view_key_combo_box.currentIndexChanged.connect(self.information_panel_view_key_changed.emit)

        self.navigation_panel_header_widget = QWidget(self)
        # self.navigation_panel_header_widget.setStyleSheet("background-color: red;")
        self.navigation_panel_header_widget_layout = QHBoxLayout(self.navigation_panel_header_widget)
        self.navigation_panel_header_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.navigation_panel_header_widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.navigation_panel_header_widget_layout.addWidget(self.navigation_panel_group_combo_box)

        self.main_panel_header_widget = QWidget(self)
        self.main_panel_header_widget_layout = QHBoxLayout(self.main_panel_header_widget)
        self.main_panel_header_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.main_panel_header_widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_panel_header_widget_layout.addWidget(self.main_panel_view_options_combo_box)

        self.information_panel_header_widget = QWidget(self)
        self.information_panel_header_widget_layout = QHBoxLayout(self.information_panel_header_widget)
        self.information_panel_header_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.information_panel_header_widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.information_panel_header_widget_layout.addWidget(self.information_panel_view_key_combo_box)

        self.main_splitter.addWidget(self.navigation_panel_header_widget)
        self.main_splitter.addWidget(self.main_panel_header_widget)
        self.main_splitter.addWidget(self.information_panel_header_widget)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.main_splitter)

    @pyqtSlot(list)
    def set_sizes(self, sizes: List[int]) -> None:
        self.main_splitter.setSizes(sizes)
