from typing import List, Union

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtWidgets import QStyle, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QLayout, QPushButton, \
    QFrame, QToolTip

from constants import *
from data_models.track import Track
from models.audio_player import AudioPlayer
from models.audio_playlist import AudioPlaylist
from utils import get_formatted_time, format_player_position_to_seconds, TrackNotInPlaylistError, \
    ImprovedSlider


class AudioController(QtWidgets.QFrame):
    updated_playing_track = pyqtSignal(Track)
    updated_playlist = pyqtSignal(list)
    paused = pyqtSignal(Track)
    unpaused = pyqtSignal(Track)
    remaining_queue_time_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("audio_controller")
        self.setStyleSheet("QFrame#audio_controller {background-color: rgba(0, 0, 88, 0.3)}")
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.current_playlist = AudioPlaylist()
        self.total_queue_time = 0
        self._rounded_remaining_queue_time = 0  # doesn't update while track is playing
        self.remaining_queue_time = 0
        self.user_action = -1  # 0 - stopped, 1 - playing, 2 - paused

        self.player = AudioPlayer(self)
        self.player.positionChanged.connect(self.player_position_changed)
        self.player.durationChanged.connect(self.player_duration_changed)

        self.play_button = QPushButton(self)
        self.prev_button = QPushButton(self)
        self.next_button = QPushButton(self)

        # self.play_button.setStyleSheet("background: transparent")
        # self.prev_button.setStyleSheet("background: transparent")
        # self.next_button.setStyleSheet("background: transparent")

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
        self.volume_slider.setMinimumWidth(50)
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
        self.seek_slider_time_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred,
                                                              QSizePolicy.Policy.Preferred))
        self.offset_label = QLabel(self.seek_slider_time_label.text())
        self.offset_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        self.offset_label.setStyleSheet("QLabel {color: rgba(0, 0, 0, 0); background-color: rgba(0, 0, 0, 0);}")
        self.audio_file_name_label = QLabel("---")
        self.audio_file_name_label.setMaximumWidth(400)
        self.seek_slider_time_label.setStyleSheet("QLabel {background-color: rgba(0, 0, 0, 0)}")
        self.seek_slider_time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.audio_file_name_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred,
                                                             QSizePolicy.Policy.Preferred))
        self.audio_file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_time_label_container = QFrame(self)
        self.name_time_label_container.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout = QHBoxLayout(self.name_time_label_container)
        self.name_time_label_container_layout.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout.addWidget(self.offset_label)
        self.name_time_label_container_layout.addWidget(self.audio_file_name_label)
        self.name_time_label_container_layout.addWidget(self.seek_slider_time_label)
        self.name_time_label_container.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred,
                                                                 QSizePolicy.Policy.Expanding))

        self.equalizer_button = QPushButton("Eq")
        self.equalizer_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)

        self.audio_order_button_modes = ("O", "S", "R")  # order, shuffle, repeat single
        self.audio_order_button_mode_index = 0
        self.audio_order_button = QPushButton("O")
        self.audio_order_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.audio_order_button.clicked.connect(self.change_audio_order)

        # Layout logic
        self.left_part = QFrame(self)
        self.middle_part = QFrame(self)
        self.right_part = QFrame(self)

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

        # for child in self.children():
        #     if isinstance(child, QWidget):
        #         child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        if not self.current_playlist:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

    def update_total_queue_time(self, time_in_secs: int) -> None:
        self.total_queue_time = time_in_secs
        self._rounded_remaining_queue_time = time_in_secs
        self.remaining_queue_time = time_in_secs
        self.remaining_queue_time_changed.emit(self.remaining_queue_time)

    def change_audio_order(self) -> None:
        self.current_playlist.change_mode()
        self.audio_order_button_mode_index = self.audio_order_button_mode_index + 1 if \
            self.audio_order_button_mode_index <= 1 else 0
        self.audio_order_button.setText(self.audio_order_button_modes[self.audio_order_button_mode_index])

        self.update_total_queue_time(sum(track.length for track in self.current_playlist.playlist))

    def set_player_position(self, position: int) -> None:
        self.player.setPosition(position)

    def set_playlist(self, playlist: List[Union[Track]]) -> None:
        self.prev_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.current_playlist.set_playlist(playlist)
        self.updated_playlist.emit(playlist)
        self.update_total_queue_time(sum(track.length for track in playlist))

    def set_playlist_index(self, index: int) -> None:
        self.current_playlist.set_playlist_index(index)

    def play(self) -> None:
        self.updated_playing_track.emit(self.current_playlist.currently_playing)
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        # self.audio_file_name_label.setText(os.path.basename(self.current_playlist.currently_playing.file_path))
        # artist = self.current_playlist.currently_playing.artist
        title = self.current_playlist.currently_playing.title.rsplit(".", 1)[0]
        # if not artist:
        #     self.audio_file_name_label.setText(title)
        # else:
        #     self.audio_file_name_label.setText(" - ".join([artist, title]))
        self.audio_file_name_label.setText(title)
        self.player.setSource(QUrl(self.current_playlist.currently_playing.file_path))
        self.player.play()

    def player_duration_changed(self, duration: int) -> None:
        self.seek_slider.setRange(0, duration - 120)
        self.seek_slider_time_label.setText(get_formatted_time(self.player.duration()))

    def player_position_changed(self, position: int, sender_type=False) -> None:  # TODO why sender_type?
        if not sender_type:
            if self.player.duration():
                if position > self.player.duration() - 120:
                    self.next_button_clicked()
                else:
                    self.seek_slider.setSliderPosition(position)
                    old_text = self.seek_slider_time_label.text()
                    self.seek_slider_time_label.setText(get_formatted_time(self.player.position()) + "/" +
                                                        get_formatted_time(self.player.duration()))
                    if old_text != self.seek_slider_time_label.text():
                        # self.remaining_queue_time -= format_player_position_to_seconds(self.player.position())
                        self.remaining_queue_time_changed.emit(self.remaining_queue_time -
                                                               format_player_position_to_seconds(self.player.position()))

    def get_remaining_time_in_secs(self) -> int:
        return self._rounded_remaining_queue_time - format_player_position_to_seconds(self.player.position())

    def pause(self, fade=True) -> None:
        self.play_button.setIcon(self.play_icon)
        self.user_action = 2
        self.player.pause(fade=fade)
        self.paused.emit(self.get_playing_track())

    def unpause(self, fade=True) -> None:
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.player.play(fade=fade)
        self.unpaused.emit(self.get_playing_track())

    def play_pause_button_clicked(self) -> None:
        if not self.current_playlist:
            return

        if self.user_action <= 0:
            self.current_playlist.set_playlist_index(0)
            self.play()
        elif self.user_action == 1:
            self.pause()
        elif self.user_action == 2:
            self.unpause()

    def next_button_clicked(self) -> None:
        self.current_playlist.set_next()
        self.play()

    def prev_button_clicked(self) -> None:
        self.current_playlist.set_prev()
        self.play()

    def volume_changed(self, volume_value: int) -> None:
        self.player.audio_output.setVolume(volume_value / 100)
        self.player.current_volume = volume_value / 100
        self.volume_slider.setSliderPosition(volume_value)
        self.volume_slider_position = volume_value
        if volume_value == 0:
            self.volume_button.setIcon(self.volume_off_icon)
        else:
            self.volume_button.setIcon(self.volume_on_icon)

    def volume_button_clicked(self) -> None:
        if self.player.audio_output.volume():
            self.volume_slider_position_backup = self.volume_slider_position
            self.volume_slider.setSliderPosition(0)
            self.player.current_volume = self.player.audio_output.volume()
        else:
            self.volume_slider_position = self.volume_slider_position_backup
            self.volume_slider.setSliderPosition(self.volume_slider_position)
            self.player.current_volume = self.player.audio_output.volume()

    def get_playing_track(self) -> Track:
        return self.current_playlist.currently_playing

    def set_playing_track(self, track: Track) -> None:
        if track not in self.current_playlist.playlist:
            raise TrackNotInPlaylistError

        self.set_playlist_index(self.current_playlist.playlist.index(track))
        self.play()


class VolumeSlider(ImprovedSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.value_changed.connect(self.slider_moved)

    def slider_moved(self, value: int) -> None:
        self.setToolTip(f"{value}%")


class SeekSlider(ImprovedSlider):
    def __init__(self, parent: AudioController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent  # TODO remove self.parent
        self.backup_volume = self.parent.player.audio_output.volume()
        self.backup_action = -1

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super(SeekSlider, self).mousePressEvent(event)
        self.backup_action = self.parent.user_action
        self.parent.player.setPosition(self.pixel_pos_to_range_value(event.pos()))
        self.backup_volume = self.parent.player.audio_output.volume()
        self.parent.pause(fade=False)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        val = self.pixel_pos_to_range_value(event.pos())
        self.setValue(val)
        self.parent.player.setPosition(val)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        # handles unmuting audio and updating player
        self.parent.player.audio_output.setVolume(self.backup_volume)
        self.parent.set_player_position(self.sliderPosition())

        if self.backup_action == 1:
            self.parent.unpause(fade=False)
