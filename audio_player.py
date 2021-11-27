from PyQt6.QtCore import QThread
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from time import sleep
from constants import *


class AudioPlayer(QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_output = QAudioOutput()
        self.setAudioOutput(self.audio_output)
        self.audioOutput().setVolume(STARTING_AUDIO_VOLUME / 100)
        self.current_volume = self.audioOutput().volume()
        print(self.audioOutput().volume())

        self.fade_in_thread = QThread(self)
        self.fade_in_thread.started.connect(lambda: self._fade_in())
        self.fade_out_thread = QThread(self)
        self.fade_out_thread.started.connect(lambda: self._fade_out())

    def _fade_in(self, fade_time=1):
        iterations = 10
        fade_interval = fade_time / iterations
        for i in range(1, iterations + 1):
            self.audioOutput().setVolume(i / iterations * self.current_volume)
            print(self.audioOutput().volume())
            sleep(fade_interval)

    def _start_fade_in(self, fade_time=1):
        self.fade_out_thread.quit()
        self.fade_in_thread.start()

    def _fade_out(self, fade_time=2):
        self.current_volume = self.audioOutput().volume()
        self.audioOutput().setVolume(0)

        iterations = 10
        fade_interval = fade_time / iterations
        for i in range(1, iterations + 1):
            self.audioOutput().setVolume(self.current_volume - i / iterations * self.current_volume)
            print(self.audioOutput().volume())
            sleep(fade_interval)
        super().pause()

    def _start_fade_out(self, fade_time=2):
        self.fade_in_thread.quit()
        self.fade_out_thread.start()

    def play(self):
        super().play()
        # self._start_fade_in()

    def pause(self):
        # self._start_fade_out()
        super().pause()
