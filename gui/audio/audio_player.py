from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSlot, QAbstractAnimation
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices

from constants import *


class AudioPlayer(QMediaPlayer):
    fade_in_anim_key_value = 0.04
    fade_in_anim_start_value = 0.05
    fade_out_anim_key_value = fade_in_anim_key_value
    fade_out_anim_end_value = 0

    def __init__(self, *args):
        super().__init__(*args)
        self._audio_output = QAudioOutput(self)

        # print([d.description() for d in self.audio_outputs])

        # self.audio_output.volumeChanged.connect(lambda: print("Changed volume:", self.audio_output.volume()))
        self.setAudioOutput(self._audio_output)
        self.audioOutput().setVolume(STARTING_AUDIO_VOLUME / 100)
        self.current_volume = STARTING_AUDIO_VOLUME / 100

        self.fade_in_anim = QPropertyAnimation(self._audio_output, b"volume")
        self.fade_in_anim.setDuration(800)

        self.fade_in_anim.setEndValue(self.current_volume)
        self.fade_in_anim.setStartValue(0.05)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.Linear)

        self.fade_out_anim = QPropertyAnimation(self._audio_output, b"volume")
        self.fade_out_anim.setDuration(600)
        self.fade_out_anim.setEndValue(self.fade_out_anim_end_value)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.fade_out_anim.finished.connect(super().pause)

    def play(self, fade: bool = True) -> None:
        if self.position() and fade:
            self.fade_in_anim.setStartValue(0 if self.current_volume < self.fade_in_anim_start_value
                                            else self.fade_in_anim_start_value)
            self.fade_in_anim.setKeyValueAt(self.fade_in_anim_key_value, 0 if
                                            self.current_volume < self.fade_in_anim_start_value
                                            else self.fade_in_anim_start_value)
            self.fade_in_anim.setEndValue(self.current_volume)
            self.fade_in_anim.start()
        else:
            self.audioOutput().setVolume(self.current_volume)
        super().play()

    def pause(self, fade: bool = True) -> None:
        if self.fade_in_anim.state() != QAbstractAnimation.State.Running:
            self.current_volume = self._audio_output.volume()
        if self.position() and fade:
            self.fade_out_anim.setStartValue(self._audio_output.volume())
            self.fade_out_anim.setKeyValueAt(self.fade_out_anim_key_value, self.current_volume)
            self.fade_out_anim.start()
        else:
            self._audio_output.setVolume(0)  # important to avoid noises when dragging seek slider
            super().pause()

    @pyqtSlot(str)
    def set_audio_output(self, audio_output_name: str) -> None:
        audio_output_devices = QMediaDevices.audioOutputs()
        if audio_output_name == "Primary Sound Driver":
            index = 0
        else:
            index = [d.description() for d in audio_output_devices].index(audio_output_name)
        self._audio_output.setDevice(audio_output_devices[index])
        self.setAudioOutput(self._audio_output)
