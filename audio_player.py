from time import sleep

from PyQt6.QtCore import QObject, QTimer, QElapsedTimer
from PyQt6.QtCore import QThread
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from constants import *



class AudioPlayer(QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_output = QAudioOutput()
        self.setAudioOutput(self.audio_output)
        self.audioOutput().setVolume(STARTING_AUDIO_VOLUME / 100)
        self.timer = QElapsedTimer()
        self.current_volume = self.audio_output.volume()

        self.audio_output.setProperty("volume", self.current_volume - self.timer.elapsed() / 0.6 * self.current_volume)
        # print(self.audioOutput().volume()

        # self.fade_in_thread = QThread(self)
        # # self.fade_in_thread.started.connect(lambda: self._fade_in())
        # self.fade_out_thread = QThread(self)
        # # self.fade_out_thread.started.connect(lambda: self._fade_out())
        #
        # self.in_worker = WorkerIn(self)
        # self.out_worker = WorkerOut(self)
        # self.in_worker.moveToThread(self.fade_in_thread)
        # self.out_worker.moveToThread(self.fade_out_thread)
        # self.fade_in_thread.started.connect(self.in_worker.run)
        # self.fade_out_thread.started.connect(self.out_worker.run)

    def play(self):
        # self.audio_output.setVolume(0)
        self.timer.start()
        super().play()
        # self.fade_in_thread.start()

    def pause(self):
        # self.fade_out_thread.start()

        super().pause()

    def super_pause(self):
        super().pause()


class WorkerIn(QObject):
    def __init__(self, parent: AudioPlayer):
        super().__init__()
        self.parent = parent

    def _fade_in(self, fade_time=.4):
        iterations = 10
        fade_interval = fade_time / iterations
        for i in range(1, iterations + 1):
            # print("crr", self.current_volume)
            # print("factor", i / iterations)
            self.parent.audioOutput().setVolume(i / iterations * self.parent.current_volume)
            print("Fade in vol: ", self.parent.audioOutput().volume())
            sleep(fade_interval)

    def run(self, fade_time=1):
        self._fade_in()


class WorkerOut(QObject):
    def __init__(self, parent: AudioPlayer):
        super().__init__()
        self.parent = parent

    def _fade_out(self, fade_time=.4):
        self.parent.current_volume = self.parent.audioOutput().volume()
        self.parent.audioOutput().setVolume(0)

        iterations = 10
        fade_interval = fade_time / iterations
        for i in range(1, iterations + 1):
            self.parent.audioOutput().setVolume(self.parent.current_volume - i / iterations * self.parent.current_volume)
            print("Fade out vol: ", self.parent.audioOutput().volume())
            sleep(fade_interval)
        self.parent.super_pause()

    def run(self, fade_time=2):
        # self.parent.fade_in_thread.quit()
        # self.parent.fade_out_thread.start()
        self._fade_out()


# class AudioPlayerThread(QThread):
#
