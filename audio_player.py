from PyQt6.QtCore import QThread
from PyQt6.QtMultimedia import QMediaPlayer
from time import sleep


class AudioPlayer(QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)

    def _fade_in(self, fade_time):
        self.current_volume = self.audioOutput().volume()
        self.audioOutput().setVolume(self.current_volume)

        iterations = 100
        fade_interval = fade_time / iterations
        for i in range(1, iterations + 1):
            self.audioOutput().setVolume(i / iterations * self.current_volume)
            print(self.audioOutput().volume())
            sleep(fade_interval)

    def _start_fade_in(self, fade_time=2):
        self.thread = QThread(self)
        self.thread.setTerminationEnabled(True)
        self.thread.started.connect(lambda: self._fade_in(fade_time))
        self.thread.start()

    def play(self):
        _play = super().play
        _play
