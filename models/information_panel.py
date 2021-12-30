from PyQt6 import QtWidgets
from constants import *


class InformationPanel(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color: rgba(255, 0, 0, 0.3)")
        self.setMinimumWidth(PANEL_MIN_WIDTH)
