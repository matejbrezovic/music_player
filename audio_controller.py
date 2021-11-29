from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QStyle, QHBoxLayout, QSlider, QWidget, QLabel, QVBoxLayout, QSizePolicy, QLayout, \
    QPushButton, QFrame
from PyQt6 import QtCore

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
        self.player.positionChanged.connect(self.player_position_changed)

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

        self.volume_slider = VolumeSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider_position = STARTING_AUDIO_VOLUME
        self.volume_slider_position_backup = STARTING_AUDIO_VOLUME
        self.volume_slider.setSliderPosition(self.volume_slider_position)
        self.volume_slider.valueChanged.connect(self.volume_changed)
        # self.volume_slider.sliderPressedWithValue.connect(self.player.setPosition)  # updates on click
        # self.volume_slider.mousePressEvent.connect(self.player.setPosition)

        self.volume_button = QtWidgets.QPushButton()
        self.volume_button.setIcon(self.volume_on_icon)
        self.volume_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.volume_button.clicked.connect(self.volume_button_clicked)

        self.seek_slider = QSlider()
        self.seek_slider.setMinimum(0)
        self.seek_slider.setMaximum(100)
        self.seek_slider.setOrientation(Qt.Orientation.Horizontal)
        self.seek_slider.setTracking(False)
        self.seek_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.seek_slider.sliderMoved.connect(self.seek_position)

        self.seek_slider_time_label = QLabel("0:00/0:00")
        self.audio_file_name_label = QLabel()
        self.audio_file_name_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        self.audio_file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.audio_file_name_label.setContentsMargins(0, 0, 0, 0)

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
        self.middle_layout.addWidget(self.audio_file_name_label)
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
        # self.main_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

    def play(self):
        print("Play")
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.audio_file_name_label.setText(self.current_playlist[self.playlist_index].rsplit("/", 1)[-1])
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
        print(volume_value)
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

    def seek_position(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            if self.player.isSeekable():
                self.player.setPosition(position)

    def player_position_changed(self, position, sender_type=False):
        if not sender_type:
            self.seek_slider.setValue(position * 100 / (self.player.duration() if self.player.duration() else 99999999))
        # update the text label
        self.seek_slider_time_label.setText('%d:%02d' % (int(position / 60000), int((position / 1000) % 60)))


class VolumeSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = self.contentsMargins().left()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
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


