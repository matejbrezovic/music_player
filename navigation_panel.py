from PyQt6 import QtWidgets
from constants import *


class NavigationPanel(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet("background-color: rgba(0, 212, 88, 0.3)")
        self.setMinimumWidth(PANEL_MIN_WIDTH)

    # def load_groups(self):
    #
