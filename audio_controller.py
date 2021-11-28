from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QStyle, QHBoxLayout, QSlider

from audio_player import AudioPlayer
from constants import *


class AudioController(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("QFrame {background-color: rgba(0, 0, 88, 0.3)}")
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)

        self.current_playlist = ['/home/matey/Music/Here We Go!.mp3', '/home/matey/Music/Remembrance.mp3']
        self.playlist_index = -1
        self.user_action = -1  # 0 - stopped, 1 - playing, 2 - paused

        self.player = AudioPlayer()

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
        self.volume_on_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        self.volume_off_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted)
        self.play_button.setIcon(self.play_icon)
        self.prev_button.setIcon(self.prev_icon)
        self.next_button.setIcon(self.next_icon)

        self.play_button.clicked.connect(self.play_pause_button_clicked)
        self.next_button.clicked.connect(self.next_button_clicked)
        self.prev_button.clicked.connect(self.prev_button_clicked)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider_position = STARTING_AUDIO_VOLUME
        self.volume_slider_position_backup = STARTING_AUDIO_VOLUME
        self.volume_slider.setSliderPosition(self.volume_slider_position)
        self.volume_slider.valueChanged.connect(self.volume_changed)

        self.volume_button = QtWidgets.QPushButton()
        self.volume_button.setIcon(self.volume_on_icon)
        self.volume_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.volume_button.clicked.connect(self.volume_button_clicked)

        self.horizontal_layer = QHBoxLayout(self)
        self.horizontal_layer.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.horizontal_layer.addWidget(self.prev_button)
        self.horizontal_layer.addWidget(self.play_button)
        self.horizontal_layer.addWidget(self.next_button)
        self.horizontal_layer.addWidget(self.volume_button)
        self.horizontal_layer.addWidget(self.volume_slider)

    def play(self):
        print("Play")
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.player.setSource(QUrl(self.current_playlist[self.playlist_index]))
        self.player.play()

    def pause(self):
        print("Pause")
        self.play_button.setIcon(self.play_icon)
        self.user_action = 2
        self.player.pause()

    def unpause(self):
        print("Unpause")
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.player.play()

    def play_pause_button_clicked(self):
        if self.user_action <= 0:
            self.playlist_index = 0
            self.play()
        elif self.user_action == 1:
            self.pause()
        elif self.user_action == 2:
            self.unpause()

    def next_button_clicked(self):
        self.playlist_index += 1
        if self.playlist_index == len(self.current_playlist):
            self.playlist_index = 0
        self.play()

    def prev_button_clicked(self):
        self.playlist_index -= 1
        if self.playlist_index <= -1:
            self.playlist_index = len(self.current_playlist) - 1
        self.play()

    def volume_changed(self, volume_value: int):
        self.player.audio_output.setVolume(volume_value / 100)
        self.volume_slider.setSliderPosition(volume_value)
        self.volume_slider_position = volume_value
        if volume_value == 0:
            self.volume_button.setIcon(self.volume_off_icon)
        else:
            self.volume_button.setIcon(self.volume_on_icon)

    def volume_button_clicked(self):
        if self.player.audio_output.volume():
            self.volume_slider_position_backup = self.volume_slider_position
            self.volume_slider.setSliderPosition(0)
        else:
            self.volume_slider_position = self.volume_slider_position_backup
            self.volume_slider.setSliderPosition(self.volume_slider_position)
