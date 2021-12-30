from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from constants import *


class AudioPlayer(QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_output = QAudioOutput()
        # self.audio_output.volumeChanged.connect(lambda: print(self.audio_output.volume()))
        self.setAudioOutput(self.audio_output)
        self.audioOutput().setVolume(STARTING_AUDIO_VOLUME / 100)
        self.current_volume = self.audio_output.volume()

        self.fade_in_anim = QPropertyAnimation(self.audio_output, b"volume")
        self.fade_in_anim.setDuration(1400)

        self.fade_in_anim.setEndValue(self.current_volume)
        self.fade_in_anim.setStartValue(FADE_IN_ANIM_START_VALUE)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.Linear)

        self.fade_out_anim = QPropertyAnimation(self.audio_output, b"volume")
        self.fade_out_anim.setDuration(600)
        self.fade_out_anim.setEndValue(FADE_OUT_ANIM_END_VALUE)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.fade_out_anim.finished.connect(super().pause)

    def play(self, fade=True):
        if fade:
            self.fade_in_anim.setStartValue(0 if self.current_volume < FADE_IN_ANIM_START_VALUE
                                            else FADE_IN_ANIM_START_VALUE)
            self.fade_in_anim.setKeyValueAt(FADE_IN_ANIM_KEY_VALUE, 0 if self.current_volume < FADE_IN_ANIM_START_VALUE
                                            else FADE_IN_ANIM_START_VALUE)
            self.fade_in_anim.setEndValue(self.current_volume)
            # print("fade_in_vol; ", self.current_volume)
            self.fade_in_anim.start()
        super().play()

    def pause(self, fade=True):
        self.current_volume = self.audio_output.volume()
        if fade:
            # print("curr", self.current_volume)
            self.fade_out_anim.setStartValue(self.current_volume)
            self.fade_out_anim.setKeyValueAt(FADE_OUT_ANIM_KEY_VALUE, self.current_volume)
            self.fade_out_anim.start()
        else:
            super().pause()
