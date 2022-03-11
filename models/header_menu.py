from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout

from utils import TransparentComboBox
from constants import *


class HeaderMenu(QWidget):
    main_panel_view_key_changed = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.main_splitter.setContentsMargins(0, 0, 0, 0)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(0)
        # self.main_splitter.setRe

        self.main_panel_view_options_combo_box = TransparentComboBox(self)
        self.main_panel_view_options_combo_box.setFixedSize(150, 24)
        self.main_panel_view_options_combo_box.currentIndexChanged.connect(self.main_panel_view_key_changed.emit)
        self.main_panel_view_options_combo_box.addItems(MAIN_PANAL_VIEW_OPTIONS)



        self.main_splitter.addWidget(self.main_panel_view_options_combo_box)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.main_splitter)