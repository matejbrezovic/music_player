from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QUrl, QThread
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QStyle, QHBoxLayout
from time import sleep

from constants import *


class AudioController(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("QFrame {background-color: rgba(0, 0, 88, 0.3)}")
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)

        self.current_playlist = ['/home/matey/Music/Remembrance.ogg']
        self.playlist_index = -1
        self.user_action = -1  # 0 - stopped, 1 - playing, 2 - paused
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.play_button = QtWidgets.QPushButton()
        self.prev_button = QtWidgets.QPushButton()
        self.next_button = QtWidgets.QPushButton()

        self.play_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.prev_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.next_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)

        self.play_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.pause_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        self.prev_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward)
        self.next_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward)
        self.play_button.setIcon(self.play_icon)
        self.prev_button.setIcon(self.prev_icon)
        self.next_button.setIcon(self.next_icon)

        self.play_button.clicked.connect(self.play_pause_button_clicked)

        self.horizontal_layer = QHBoxLayout(self)
        self.horizontal_layer.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.horizontal_layer.addWidget(self.prev_button)
        self.horizontal_layer.addWidget(self.play_button)
        self.horizontal_layer.addWidget(self.next_button)



    def _fade_out(self, fade_time=2):
        self.current_volume = self.audio_output.volume()
        self.audio_output.setVolume(0)

        iterations = 100
        fade_interval = fade_time / iterations
        for i in range(1, iterations + 1):
            self.audio_output.setVolume(self.current_volume - i / iterations * self.current_volume)
            print(self.audio_output.volume())
            sleep(fade_interval)

    def _start_fade_out(self, fade_time=2):
        self.thread = QThread(self)
        self.thread.started.connect(lambda: self._fade_out(fade_time))
        self.thread.start()

    def play_pause_button_clicked(self):
        if self.user_action <= 0:
            print("Play")
            self.play_button.setIcon(self.pause_icon)
            self.user_action = 1
            self.player.setSource(QUrl(self.current_playlist[0]))
            self.player.play()
            self._start_fade_in()

        elif self.user_action == 1:
            print("Pause")
            self.user_action = 2
            self.play_button.setIcon(self.play_icon)
            self._start_fade_out()
            self.player.pause()

        elif self.user_action == 2:
            print("Play")
            self.play_button.setIcon(self.pause_icon)
            self.user_action = 1
            self.player.play()
            self._start_fade_in()
