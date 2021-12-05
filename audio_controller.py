import os
from typing import List

from PyQt6 import QtCore
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QStyle, QHBoxLayout, QSlider, QLabel, QVBoxLayout, QSizePolicy, QLayout, QPushButton, \
    QFrame

from audio_player import AudioPlayer
from audio_playlist import AudioPlaylist
from constants import *


class AudioController(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("QFrame {background-color: rgba(0, 0, 88, 0.3)}")
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)

        self.current_playlist = AudioPlaylist()
        self.current_playlist.set_playlist([DEFAULT_AUDIO_PATH + "/" + name for name in os.listdir(DEFAULT_AUDIO_PATH)])
        # shuffle(self.current_playlist)
        # self.playlist_index = -1
        self.user_action = -1  # 0 - stopped, 1 - playing, 2 - paused

        self.player = AudioPlayer(self)
        self.player.positionChanged.connect(self.player_position_changed)
        self.player.durationChanged.connect(self.player_duration_changed)

        self.play_button = QPushButton()
        self.prev_button = QPushButton()
        self.next_button = QPushButton()

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

        self.volume_slider = ImprovedSlider(Qt.Orientation.Horizontal)
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

        self.seek_slider = SeekSlider(self)
        self.seek_slider.setMinimum(0)
        self.seek_slider.setMaximum(100)
        self.seek_slider.setOrientation(Qt.Orientation.Horizontal)
        self.seek_slider.setTracking(False)
        self.seek_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.seek_slider_time_label = QLabel("0:00/0:00")
        self.seek_slider_time_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        self.offset_label = QLabel(self.seek_slider_time_label.text())
        self.offset_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        self.offset_label.setStyleSheet("QLabel {color: rgba(0, 0, 0, 0); background-color: rgba(0, 0, 0, 0);}")
        self.audio_file_name_label = QLabel("---")
        self.audio_file_name_label.setMaximumWidth(400)
        self.seek_slider_time_label.setStyleSheet("QLabel {background-color: rgba(0, 0, 0, 0)}")
        self.seek_slider_time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.audio_file_name_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        self.audio_file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_time_label_container = QFrame()
        self.name_time_label_container.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout = QHBoxLayout(self.name_time_label_container)
        self.name_time_label_container_layout.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout.addWidget(self.offset_label)
        self.name_time_label_container_layout.addWidget(self.audio_file_name_label)
        self.name_time_label_container_layout.addWidget(self.seek_slider_time_label)
        self.name_time_label_container.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding))

        self.equalizer_button = QPushButton("Eq")
        self.audio_order_button = QPushButton("Au")
        self.equalizer_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.audio_order_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)

        # Layout logic
        self.left_part = QFrame()
        self.middle_part = QFrame()
        self.right_part = QFrame()

        self.left_layout = QHBoxLayout(self.left_part)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.left_layout.addWidget(self.prev_button)
        self.left_layout.addWidget(self.play_button)
        self.left_layout.addWidget(self.next_button)
        self.left_layout.addWidget(self.volume_button)
        self.left_layout.addWidget(self.volume_slider)
        self.left_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.left_part.setStyleSheet("QFrame {background-color: rgba(0, 255, 7, 0.3)}")
        self.left_part.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.left_part.setFixedSize(self.left_layout.sizeHint())

        self.middle_layout = QVBoxLayout(self.middle_part)
        self.middle_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.middle_layout.addWidget(self.name_time_label_container)
        self.middle_layout.addWidget(self.seek_slider)
        self.middle_layout.setContentsMargins(0, 4, 0, 2)

        self.right_layout = QHBoxLayout(self.right_part)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.right_layout.addWidget(self.equalizer_button)
        self.right_layout.addWidget(self.audio_order_button)

        self.right_part.setStyleSheet("QFrame {background-color: rgba(255, 0, 231, 0.3)}")
        self.right_part.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.right_part.setFixedSize(self.left_layout.sizeHint())

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.left_part)
        self.main_layout.addWidget(self.middle_part)
        self.main_layout.addWidget(self.right_part)

    def set_player_position(self, position: int):
        self.player.setPosition(position)

    def set_playlist(self, playlist: List[str]):
        self.current_playlist.set_playlist(playlist)

    def play(self):
        print("Play")
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.audio_file_name_label.setText(os.path.basename(self.current_playlist.get_current()))
        self.player.setSource(QUrl(self.current_playlist.get_current()))
        self.player.play()

    @staticmethod
    def get_formatted_time(time_in_seconds: int):
        hours = int(time_in_seconds / 3600000)
        minutes = int((time_in_seconds / 60000) % 60)
        seconds = int((time_in_seconds / 1000) % 60)

        return f'{str(hours) + ":" if hours else ""}{"0" + str(minutes) if hours else minutes}:' \
               f'{"0" + str(seconds) if seconds < 10 else seconds}'

    def player_duration_changed(self, duration):
        # duration = int(duration)
        self.seek_slider.setRange(0, duration)
        print("Duration: ", duration)
        self.seek_slider_time_label.setText(self.get_formatted_time(self.player.duration()))

    def player_position_changed(self, position, sender_type=False):
        if not sender_type:
            if self.player.duration():
                if position == self.player.duration():
                    self.next_button_clicked()
                self.seek_slider.setSliderPosition(position)
        # update the time text label
        self.seek_slider_time_label.setText(self.get_formatted_time(self.player.position()) + "/" +
                                            self.get_formatted_time(self.player.duration()))

    def pause(self, fade=True):
        print("Pause")
        self.play_button.setIcon(self.play_icon)
        self.user_action = 2
        self.player.pause(fade)

    def unpause(self, fade=True):
        print("Unpause")
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.player.play(fade)

    def play_pause_button_clicked(self):
        if self.user_action <= 0:
            self.current_playlist.set_playlist_index(0)
            self.play()
        elif self.user_action == 1:
            self.pause()
        elif self.user_action == 2:
            self.unpause()

    def next_button_clicked(self):
        self.current_playlist.set_next()
        self.play()

    def prev_button_clicked(self):
        self.current_playlist.set_prev()
        self.play()

    def volume_changed(self, volume_value: int):
        print("Volume: ", volume_value)
        self.player.audio_output.setVolume(volume_value / 100)
        self.player.current_volume = volume_value / 100
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
            self.player.current_volume = self.player.audio_output.volume()
        else:
            self.volume_slider_position = self.volume_slider_position_backup
            self.volume_slider.setSliderPosition(self.volume_slider_position)
            self.player.current_volume = self.player.audio_output.volume()


class ImprovedSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            val = self.pixelPosToRangeValue(event.pos())
            self.setValue(val)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        val = self.pixelPosToRangeValue(event.pos())
        self.setValue(val)

    def pixelPosToRangeValue(self, pos):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QtWidgets.QStyle.ComplexControl.CC_Slider, opt,
                                         QtWidgets.QStyle.SubControl.SC_SliderGroove, self)
        sr = self.style().subControlRect(QtWidgets.QStyle.ComplexControl.CC_Slider, opt,
                                         QtWidgets.QStyle.SubControl.SC_SliderHandle, self)

        slider_length = sr.width()
        slider_min = gr.x()
        slider_max = gr.right() - slider_length + 1

        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == QtCore.Qt.Orientation.Horizontal else pr.y()
        return QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - slider_min,
                                                        slider_max - slider_min, opt.upsideDown)


class SeekSlider(ImprovedSlider):
    def __init__(self, parent: AudioController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.backup_volume = self.parent.player.audio_output.volume()
        self.backup_action = -1

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        super(SeekSlider, self).mousePressEvent(event)
        self.backup_action = self.parent.user_action
        self.parent.player.setPosition(self.pixelPosToRangeValue(event.pos()))
        self.backup_volume = self.parent.player.audio_output.volume()
        self.parent.player.audio_output.setVolume(0)
        self.parent.pause(fade=False)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        val = self.pixelPosToRangeValue(event.pos())
        self.setValue(val)
        self.parent.player.setPosition(val)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        # handles unmuting audio and updating player
        print(self.backup_volume)
        self.parent.player.audio_output.setVolume(self.backup_volume)
        self.parent.set_player_position(self.sliderPosition())

        if self.backup_action == 1:
            self.parent.unpause(fade=False)
