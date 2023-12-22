from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QToolTip

from constants import STARTING_AUDIO_VOLUME
from utils import ImprovedSlider


class VolumeSlider(ImprovedSlider):
    light_stylesheet = f"""
            QSlider::groove:horizontal {{
                border: none;
                background: rgba(255, 255, 255, 0.3);
                margin: 12px 6px;
            }}

            QSlider::handle:horizontal {{
                background: white;
                margin: -8px -6px;
                width: 6px;
            }}
            """

    dark_stylesheet = f"""
            QSlider::groove:horizontal {{
                border: none;
                background: white;
                margin: 12px 6px;
            }}

            QSlider::handle:horizontal {{
                background: black;
                margin: -8px -6px;
                width: 6px;
            }}
            """

    def __init__(self, *args):
        super().__init__(*args)

        self.setStyleSheet(self.dark_stylesheet)
        self.value_changed.connect(self.slider_moved)
        self.sliderMoved.connect(self.slider_moved)
        self.setToolTip(f"{STARTING_AUDIO_VOLUME}%")

    def slider_moved(self, value: int) -> None:
        self.setToolTip(f"{value}%")

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            self.setStyleSheet(self.dark_stylesheet)
        else:
            self.setStyleSheet(self.light_stylesheet)

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        self.value_changed.emit(self.value())

        x = self.value() / self.maximum() * self.width()
        QToolTip.showText(self.mapToGlobal(QPoint(x, self.y())), self.toolTip())

    # def mouseMoveEvent(self, event: QMouseEvent) -> None:
    #     super().mouseMoveEvent(event)
    #
    #     x = self.value() / self.maximum() * self.width()
    #     QToolTip.showText(self.mapToGlobal(QPoint(x, self.y())), self.toolTip())
