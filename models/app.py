from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QStyleFactory


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
        # noinspection PyArgumentList
        self.setStyle(QStyleFactory.create("windowsvista"))
