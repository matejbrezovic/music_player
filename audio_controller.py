import PySide6
import pygame
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon, Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import QStyle, QHBoxLayout
from pygame import mixer

from constants import *


class AudioController(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        pygame.init()
        pygame.mixer.init()
        self.setStyleSheet("background-color: rgba(0, 0, 88, 0.3)")
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)

        # self.player = AudioPlayer()
        self.current_playlist = ['/home/matey/Music/Remembrance.ogg']
        self.playlist_index = -1
        self.user_action_index = -1  # 0 - stopped, 1 - playing 2 - paused

        self.play_button = QtWidgets.QPushButton()
        self.prev_button = QtWidgets.QPushButton()
        self.next_button = QtWidgets.QPushButton()

        self.play_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.prev_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.next_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)

        style = self.style()
        play_icon = QIcon.fromTheme("media-playback-start.png", style.standardIcon(QStyle.SP_MediaPlay))
        pause_icon = QIcon.fromTheme("media-playback-start.png", style.standardIcon(QStyle.SP_MediaPause))
        prev_icon = QIcon.fromTheme("media-playback-start.png", style.standardIcon(QStyle.SP_MediaSkipBackward))
        next_icon = QIcon.fromTheme("media-playback-start.png", style.standardIcon(QStyle.SP_MediaSkipForward))
        self.play_button.setIcon(play_icon)
        self.prev_button.setIcon(prev_icon)
        self.next_button.setIcon(next_icon)

        self.play_button.clicked.connect(self.play_pause_button_clicked)

        self.horizontal_layer = QHBoxLayout(self)
        self.horizontal_layer.setAlignment(Qt.AlignLeft)
        self.horizontal_layer.addWidget(self.prev_button)
        self.horizontal_layer.addWidget(self.play_button)
        self.horizontal_layer.addWidget(self.next_button)

    def play_pause_button_clicked(self):
        if self.user_action_index <= 1:
            print(self.current_playlist[0], "mp3")
            mixer.music.load(self.current_playlist[0])
            mixer.music.play(-1)
