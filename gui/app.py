from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QStyleFactory

from constants import APPLICATION_NAME, APPLICATION_VERSION


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setApplicationName(APPLICATION_NAME)
        self.setApplicationVersion(APPLICATION_VERSION)

        self.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
        self.setStyle(QStyleFactory.create("windowsvista"))
