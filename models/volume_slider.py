from constants import (LIGHT_AUDIO_CONTROLLER_HOVER_COLOR, LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND,
                       LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND, DARK_AUDIO_CONTROLLER_HOVER_COLOR,
                       DARK_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND,
                       DARK_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND)
from utils import ImprovedSlider


class VolumeSlider(ImprovedSlider):
    light_stylesheet = f"""
    QSlider::handle {{
        height: 4px;
        background: {LIGHT_AUDIO_CONTROLLER_HOVER_COLOR};
    }}

    QSlider::add-page {{
        background: {LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND};
    }}

    QSlider::sub-page {{
        background: {LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND};
    }}
    """

    dark_stylesheet = f"""
    QSlider::handle {{
        height: 4px;
        background: {DARK_AUDIO_CONTROLLER_HOVER_COLOR};
    }}

    QSlider::add-page {{
        background: {DARK_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND};
    }}

    QSlider::sub-page {{
        background: {DARK_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND};
    }}
    """

    def __init__(self, *args):
        super().__init__(*args)

        self.value_changed.connect(self.slider_moved)

    def slider_moved(self, value: int) -> None:
        self.setToolTip(f"{value}%")

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            self.setStyleSheet(self.dark_stylesheet)
        else:
            self.setStyleSheet(self.light_stylesheet)

