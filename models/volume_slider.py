from constants import (LIGHT_AUDIO_CONTROLLER_HOVER_COLOR, LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND,
                       LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND, DARK_AUDIO_CONTROLLER_HOVER_COLOR,
                       DARK_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND,
                       DARK_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND)
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

    def slider_moved(self, value: int) -> None:
        self.setToolTip(f"{value}%")

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            self.setStyleSheet(self.dark_stylesheet)
        else:
            print("Set light stylesheet")
            self.setStyleSheet(self.light_stylesheet)

