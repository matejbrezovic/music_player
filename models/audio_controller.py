from typing import List

from PyQt6 import QtGui
from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QBrush, QPixmap, QPainter, QIcon, QFont
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QPushButton, QFrame, QSpacerItem, QWidget)

from constants import *
from data_models.track import Track
from models.audio_player import AudioPlayer
from models.audio_playlist import AudioPlaylist
from models.marquee_label import MarqueeLabel
from models.seek_slider import SeekSlider
from models.star_widget import StarWidget
from models.track_not_found_dialog import TrackNotFoundDialog
from models.volume_slider import VolumeSlider
from utils import (get_formatted_time, format_player_position_to_seconds, TrackNotInPlaylistError,
                   get_artwork_pixmap, get_blurred_pixmap, change_icon_color, HoverButton, format_seconds)


class AudioController(QFrame):
    updated_playing_track = pyqtSignal(Track, int)
    updated_playlist = pyqtSignal(list)
    paused = pyqtSignal(Track)
    unpaused = pyqtSignal(Track)
    remaining_queue_time_changed = pyqtSignal(int)
    playback_error_encountered = pyqtSignal(Track)
    player_stopped = pyqtSignal()

    default_stylesheet = "QFrame#audio_controller {background-color: rgba(0, 0, 0, 0.2)}"

    def __init__(self, *args):
        super().__init__(*args)
        self.setObjectName("audio_controller")
        self.setStyleSheet(self.default_stylesheet)
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._is_dark_mode_enabled = None

        self.playlist = AudioPlaylist()
        self.playlist.updated_playlist.connect(self.updated_playlist)

        self.total_queue_time = 0
        self._rounded_remaining_queue_time = 0  # doesn't update while track is playing
        self.remaining_queue_time = 0
        self.user_action = -1  # 0 - stopped, 1 - playing, 2 - paused
        self.is_playing = False
        self.is_muted = False

        self.player = AudioPlayer(self)
        self.player.positionChanged.connect(self.player_position_changed)
        self.player.durationChanged.connect(self.player_duration_changed)

        self.play_button = HoverButton(self)
        self.prev_button = HoverButton(self)
        self.next_button = HoverButton(self)

        self.play_button.setStyleSheet("background: transparent")
        self.prev_button.setStyleSheet("background: transparent")
        self.next_button.setStyleSheet("background: transparent")

        self.play_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT + 10, CONTROLLER_BUTTON_WIDTH + 10)
        self.prev_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.next_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.play_button.setIconSize(QSize(22, 22))

        self.play_icon = QIcon(QPixmap(ROOT + "/icons/play.png"))
        self.pause_icon = QIcon(QPixmap(ROOT + "/icons/pause.png"))
        self.prev_icon = QIcon(QPixmap(ROOT + "/icons/rewind.png"))
        self.next_icon = QIcon(QPixmap(ROOT + "/icons/fast-forward.png"))
        self.volume_on_icon = QIcon(QPixmap(ROOT + "/icons/volume.png"))
        self.volume_off_icon = QIcon(QPixmap(ROOT + "/icons/mute.png"))

        self.play_button.setIcon(self.play_icon)
        self.prev_button.setIcon(self.prev_icon)
        self.next_button.setIcon(self.next_icon)

        self.play_button.clicked.connect(self.play_pause_button_clicked)
        self.next_button.clicked.connect(self.next_button_clicked)
        self.prev_button.clicked.connect(self.prev_button_clicked)

        self.volume_slider = VolumeSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setMinimumWidth(50)
        self.volume_slider_position = STARTING_AUDIO_VOLUME
        self.volume_slider_position_backup = STARTING_AUDIO_VOLUME
        self.volume_slider.setSliderPosition(self.volume_slider_position)
        self.volume_slider.valueChanged.connect(self.volume_changed)
        # self.volume_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.volume_button = HoverButton()
        self.volume_button.setIcon(self.volume_on_icon)
        self.volume_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.volume_button.clicked.connect(self.volume_button_clicked)
        self.volume_button.setStyleSheet("background-color: transparent;")
        # self.volume_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.seek_slider = SeekSlider(self)
        self.seek_slider.setMinimum(0)
        self.seek_slider.setMaximum(100)
        self.seek_slider.setOrientation(Qt.Orientation.Horizontal)
        self.seek_slider.setTracking(False)
        self.seek_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.seek_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.star_widget = StarWidget(0, self)
        self.star_widget.setFixedWidth(90)
        # self.star_widget.setStyleSheet("background-color: green;")

        """ DEPRECATED
        ########################################################################
        
        def set_amplitudes(amps):
            amps = np.array(amps)
            amps = amps.tolist()
            print(amps)

        self.fft_analyser = FFTAnalyser(self.player)
        self.fft_analyser.calculated_visual.connect(set_amplitudes)
        self.fft_analyser.start()

        self.spectrum_equalizer_widget = SpectrumEqualizerWidget(5, 10)
        self.spectrum_equalizer_widget.setFixedSize(40, 30)
        self.paused.connect(self.spectrum_equalizer_widget.stop)
        self.unpaused.connect(self.spectrum_equalizer_widget.start)
        self.updated_playing_track.connect(self.spectrum_equalizer_widget.start)

        ########################################################################
        """

        self.passed_time_label = QLabel("0:00/ 0:00")
        self.passed_time_label.setFixedWidth(90)
        self.track_title_label = MarqueeLabel(self)
        self.track_title_label.setFont(QFont(self.track_title_label.font().family(), 9))
        self.track_title_label.setText("---")
        self.passed_time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.track_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_time_label_container = QFrame(self)
        self.name_time_label_container.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout = QHBoxLayout(self.name_time_label_container)
        self.name_time_label_container_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.name_time_label_container_layout.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout.addWidget(self.star_widget)
        self.name_time_label_container_layout.addWidget(self.track_title_label)
        self.name_time_label_container_layout.addWidget(self.passed_time_label)
        self.name_time_label_container.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred,
                                                                 QSizePolicy.Policy.Expanding))
        self.name_time_label_container.setFixedHeight(self.track_title_label.sizeHint().height())

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
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.left_layout.addWidget(self.prev_button)
        self.left_layout.addWidget(self.play_button)
        self.left_layout.addWidget(self.next_button)
        self.left_layout.addSpacerItem(QSpacerItem(40, 10))
        self.left_layout.addWidget(self.volume_button)
        self.left_layout.addWidget(self.volume_slider)
        # self.left_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.left_part.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.left_part.setFixedSize(self.left_layout.sizeHint())

        self.middle_layout = QVBoxLayout(self.middle_part)
        self.middle_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.middle_layout.addWidget(self.name_time_label_container)
        self.middle_layout.addWidget(self.seek_slider)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)

        self.right_layout = QHBoxLayout(self.right_part)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.right_layout.addWidget(self.audio_order_button)
        # self.right_layout.addWidget(self.spectrum_equalizer_widget)

        self.right_part.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.right_part.setFixedSize(self.left_layout.sizeHint())

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 6, 4, 4)
        self.main_layout.addWidget(self.left_part)
        self.main_layout.addWidget(self.middle_part)
        self.main_layout.addWidget(self.right_part)

        if not self.playlist:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

        self.background_pixmap = None
        # self.star_widget.setEnabled(False)

        for child in self.findChildren(QWidget):
            if isinstance(child, QWidget):
                child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.set_dark_mode_enabled(True)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if self.background_pixmap:
            painter = QPainter(self)

            painter.drawPixmap(self.rect(), self.background_pixmap)
            brush = QBrush(QColor(0, 0, 0, 170))
            painter.setBrush(brush)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            painter.drawRect(self.rect())

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if self._is_dark_mode_enabled == dark_mode_enabled:
            return

        self._is_dark_mode_enabled = dark_mode_enabled

        color = DARK_AUDIO_CONTROLLER_COLOR if dark_mode_enabled else LIGHT_AUDIO_CONTROLLER_COLOR
        name = color.name()
        self.setStyleSheet(self.default_stylesheet + f"QWidget {{color: {name};}}")
        self.seek_slider.set_dark_mode_enabled(dark_mode_enabled)
        self.volume_slider.set_dark_mode_enabled(dark_mode_enabled)

        self.play_icon = change_icon_color(self.play_icon, color)
        self.pause_icon = change_icon_color(self.pause_icon, color)
        self.prev_icon = change_icon_color(self.prev_icon, color)
        self.next_icon = change_icon_color(self.next_icon, color)
        self.volume_on_icon = change_icon_color(self.volume_on_icon, color)
        self.volume_off_icon = change_icon_color(self.volume_off_icon, color)

        if self.is_playing:
            self.play_button.setIcon(self.pause_icon)
        else:
            self.play_button.setIcon(self.play_icon)

        if self.is_muted:
            self.volume_button.setIcon(self.volume_off_icon)
        else:
            self.volume_button.setIcon(self.volume_on_icon)
        self.prev_button.setIcon(self.prev_icon)
        self.next_button.setIcon(self.next_icon)

        self.play_button.is_in_dark_mode = dark_mode_enabled
        self.volume_button.is_in_dark_mode = dark_mode_enabled
        self.prev_button.is_in_dark_mode = dark_mode_enabled
        self.next_button.is_in_dark_mode = dark_mode_enabled

        self.star_widget.set_star_color(color)

    def update_background_pixmap(self, track: Track, reset_to_default: bool = False) -> None:
        # start = time.time()
        pixmap = get_artwork_pixmap(track.file_path)
        if not pixmap or reset_to_default:
            self.background_pixmap = None
            self.set_dark_mode_enabled(True)
            self.repaint()
            return None
        pixmap = get_blurred_pixmap(pixmap)

        start_y = pixmap.height() // 1.5
        new_height = 60

        pixmap = pixmap.copy(0, start_y, pixmap.width(), new_height)
        self.background_pixmap = pixmap
        self.set_dark_mode_enabled(False)
        self.repaint()
        # print("Audio controller background updated in:", time.time() - start)

    @pyqtSlot(list)
    def queue_next(self, tracks: List[Track]) -> None:
        insert_index = self.playlist.playing_track_index + 1
        new_playlist = self.playlist.playlist[:insert_index] + tracks + self.playlist.playlist[insert_index:]
        self.set_playlist(new_playlist)
        # self.current_playlist.queue_next(tracks)

    @pyqtSlot(list)
    def queue_last(self, tracks: List[Track]) -> None:
        new_playlist = self.playlist.playlist + tracks
        self.set_playlist(new_playlist)

    @pyqtSlot(int)
    def update_total_queue_time(self, time_in_secs: int) -> None:
        self.total_queue_time = time_in_secs
        self._rounded_remaining_queue_time = time_in_secs
        self.remaining_queue_time = time_in_secs
        self.remaining_queue_time_changed.emit(self.remaining_queue_time)

    @pyqtSlot()
    def change_audio_order(self) -> None:
        self.playlist.change_mode()
        self.audio_order_button_mode_index = self.audio_order_button_mode_index + 1 if \
            self.audio_order_button_mode_index <= 1 else 0
        self.audio_order_button.setText(self.audio_order_button_modes[self.audio_order_button_mode_index])

        self.update_total_queue_time(sum(track.length for track in self.playlist.playlist))

    @pyqtSlot(int)
    def set_player_position(self, position: int) -> None:
        self.player.setPosition(position)

    @pyqtSlot(list)
    def set_playlist(self, playlist: List[Track]) -> None:
        # print("New playlist:\n", "\n".join(str(t) for t in playlist))
        self.prev_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.playlist.set_playlist(playlist)
        self.updated_playlist.emit(playlist)
        self.update_total_queue_time(sum(track.length for track in playlist))

    @pyqtSlot(int)
    def set_playlist_index(self, index: int) -> None:
        # print("New index:", index)
        self.playlist.set_playlist_index(index)

    @pyqtSlot()
    def play(self) -> None:
        playing_track = self.get_playing_track()

        # print("Playing track:", playing_track)

        self.passed_time_label.setText(f"0:00/ {format_seconds(playing_track.length)}")

        if playing_track.artist:
            self.track_title_label.setText(f"{playing_track.artist} - {playing_track.title}")
        else:
            self.track_title_label.setText(playing_track.title)
        # print(format_seconds(playing_track.length))

        self.is_playing = playing_track.is_valid()
        # print("Track is valid:", playing_track.is_valid())

        if playing_track.is_valid():
            self.user_action = 1
            self.star_widget.setEnabled(True)
            self.seek_slider.setEnabled(True)
            self.update_background_pixmap(playing_track)
            self.play_button.setIcon(self.pause_icon)
            self.player.setSource(QUrl(playing_track.file_path))
            self.player.play()
            self.updated_playing_track.emit(playing_track, self.playlist.playing_track_index)
        else:
            self.user_action = 0
            self.star_widget.setEnabled(False)
            self.update_background_pixmap(playing_track, reset_to_default=True)
            self.play_button.setIcon(self.play_icon)
            self.player.stop()
            self.seek_slider.setEnabled(False)
            self.player_stopped.emit()
            t = TrackNotFoundDialog(playing_track)
            t.exec()  # must be exec, not show, because on the first 'show' dialog instantly closes

    # @pyqtSlot(int)
    def player_duration_changed(self, duration: int) -> None:
        self.seek_slider.setRange(0, duration - 120)
        # self.passed_time_label.setText(get_formatted_time(self.player.duration()))
        self.seek_slider.set_length_in_seconds(format_player_position_to_seconds(self.player.duration()))
        # print(get_formatted_time(self.player.duration()))

    # @pyqtSlot(int)
    def player_position_changed(self, position: int) -> None:
        if not self.player.duration():
            return

        if position > self.player.duration() - 120:
            self.next_button_clicked()
        else:
            self.seek_slider.setSliderPosition(position)
            old_text = self.passed_time_label.text()
            self.passed_time_label.setText(get_formatted_time(self.player.position()) + "/ " +
                                           format_seconds(self.get_playing_track().length))
            if old_text != self.passed_time_label.text():
                # self.remaining_queue_time -= format_player_position_to_seconds(self.player.position())
                self.remaining_queue_time_changed.emit(self.remaining_queue_time -
                                                       format_player_position_to_seconds(self.player.position()))

    def get_remaining_time_in_secs(self) -> int:
        return self._rounded_remaining_queue_time - format_player_position_to_seconds(self.player.position())

    def pause(self, fade=True) -> None:
        # print("Pause")
        self.play_button.setIcon(self.play_icon)
        self.is_playing = False
        self.user_action = 2
        self.player.pause(fade=fade)
        self.paused.emit(self.get_playing_track())

    def unpause(self, fade=True) -> None:
        # print("Unpause")
        self.play_button.setIcon(self.pause_icon)
        self.is_playing = True
        self.user_action = 1
        self.player.play(fade=fade)
        self.unpaused.emit(self.get_playing_track())

    @pyqtSlot()
    def play_pause_button_clicked(self) -> None:
        if not self.playlist:
            return

        if self.user_action <= 0:
            if self.get_playing_track().is_valid():
                self.playlist.set_playlist_index(0)
            self.play()
        elif self.user_action == 1:
            self.pause()
        elif self.user_action == 2:
            self.unpause()

    @pyqtSlot()
    def next_button_clicked(self) -> None:
        self.playlist.set_next()
        if not self.playlist.has_valid_tracks():
            t = TrackNotFoundDialog(self.get_playing_track())
            self.playlist.set_prev()
            t.show()
        elif not self.get_playing_track().is_valid():
            self.playback_error_encountered.emit(self.get_playing_track())
            self.next_button_clicked()
        else:
            self.play()

    @pyqtSlot()
    def prev_button_clicked(self) -> None:
        self.playlist.set_prev()
        if not self.playlist.has_valid_tracks():
            t = TrackNotFoundDialog(self.get_playing_track())
            self.playlist.set_next()
            t.show()
        elif not self.get_playing_track().is_valid():
            self.playback_error_encountered.emit(self.get_playing_track())
            self.prev_button_clicked()
        else:
            self.play()

    @pyqtSlot(int)
    def volume_changed(self, volume_value: int) -> None:
        # print("volume changed:", volume_value)
        self.player.audio_output.setVolume(volume_value / 100)
        self.player.current_volume = volume_value / 100
        self.volume_slider.setSliderPosition(volume_value)
        self.volume_slider_position = volume_value
        if volume_value == 0:
            self.volume_button.setIcon(self.volume_off_icon)
            self.is_muted = True
        else:
            self.volume_button.setIcon(self.volume_on_icon)
            self.is_muted = False

    @pyqtSlot()
    def volume_button_clicked(self) -> None:
        if self.player.audio_output.volume():
            self.volume_slider_position_backup = self.volume_slider_position
            self.volume_slider.setSliderPosition(0)
            self.player.current_volume = self.player.audio_output.volume()
            self.is_muted = True
        else:
            self.volume_slider_position = self.volume_slider_position_backup
            self.volume_slider.setSliderPosition(self.volume_slider_position)
            self.player.current_volume = self.player.audio_output.volume()
            self.is_muted = False

    def get_playing_track(self) -> Track:
        return self.playlist.playing_track

    @pyqtSlot(Track)
    def set_playing_track(self, track: Track) -> None:
        if track not in self.playlist.playlist:
            raise TrackNotInPlaylistError

        self.set_playlist_index(self.playlist.playlist.index(track))
        self.play()

    @pyqtSlot(str)
    def set_audio_output(self, audio_output: str) -> None:
        self.player.set_audio_output(audio_output)
