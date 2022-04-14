import time
from typing import List

from PyQt6 import QtGui
from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot, QEvent, QSize
from PyQt6.QtGui import QBrush, QPixmap, QPainter, QIcon, QPaintEvent, QMouseEvent
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QPushButton,
                             QFrame, QToolTip, QSpacerItem, QStyleOptionSlider, QStyle, QSlider)

from constants import *
from data_models.track import Track
from models.audio_player import AudioPlayer
from models.audio_playlist import AudioPlaylist
from models.star_widget import StarWidget
from utils import (get_formatted_time, format_player_position_to_seconds, TrackNotInPlaylistError,
                   ImprovedSlider, get_artwork_pixmap, get_blurred_pixmap, change_icon_color, HoverButton,
                   format_seconds, MarqueeLabel)


class AudioController(QFrame):
    updated_playing_track = pyqtSignal(Track, int)
    updated_playlist = pyqtSignal(list)
    paused = pyqtSignal(Track)
    unpaused = pyqtSignal(Track)
    remaining_queue_time_changed = pyqtSignal(int)

    default_stylesheet = "QFrame#audio_controller {background-color: rgba(0, 0, 0, 0.2)}"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("audio_controller")
        self.setStyleSheet(self.default_stylesheet)
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.current_playlist = AudioPlaylist()
        self.current_playlist.updated_playlist.connect(self.updated_playlist)

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
        self.volume_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setMinimumWidth(50)
        self.volume_slider_position = STARTING_AUDIO_VOLUME
        self.volume_slider_position_backup = STARTING_AUDIO_VOLUME
        self.volume_slider.setSliderPosition(self.volume_slider_position)
        self.volume_slider.valueChanged.connect(self.volume_changed)

        self.volume_button = HoverButton()
        self.volume_button.setIcon(self.volume_on_icon)
        self.volume_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.volume_button.clicked.connect(self.volume_button_clicked)
        self.volume_button.setStyleSheet("background-color: transparent;")

        self.seek_slider = SeekSlider(self)
        self.seek_slider.setMinimum(0)
        self.seek_slider.setMaximum(100)
        self.seek_slider.setOrientation(Qt.Orientation.Horizontal)
        self.seek_slider.setTracking(False)
        self.seek_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.star_widget = StarWidget()
        self.star_widget.setMaximumWidth(100)
        # self.star_widget.setStyleSheet("background-color: green;")

        self.seek_slider_time_label = QLabel("0:00/0:00")
        self.seek_slider_time_label.setMaximumWidth(100)
        # self.offset_label = QLabel(self.seek_slider_time_label.text())
        # self.offset_label.setMaximumWidth(100)
        # self.offset_label.setStyleSheet("QLabel {color: rgba(0, 0, 0, 0); background-color: rgba(0, 0, 0, 0);}")
        self.audio_file_name_label = MarqueeLabel(self)
        # self.audio_file_name_label.setStyleSheet("background-color: blue;")
        self.audio_file_name_label.setText("---")
        # self.audio_file_name_label.setStyleSheet("background-color: blue;")
        self.seek_slider_time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.audio_file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # self.offset_label.setStyleSheet("background-color: red;")

        self.name_time_label_container = QFrame(self)
        self.name_time_label_container.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout = QHBoxLayout(self.name_time_label_container)
        self.name_time_label_container_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.name_time_label_container_layout.setContentsMargins(0, 0, 0, 0)
        self.name_time_label_container_layout.addWidget(self.star_widget)
        self.name_time_label_container_layout.addWidget(self.audio_file_name_label)
        self.name_time_label_container_layout.addWidget(self.seek_slider_time_label)
        self.name_time_label_container.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred,
                                                                 QSizePolicy.Policy.Expanding))

        self.audio_order_button_modes = ("O", "S", "R")  # order, shuffle, repeat single
        self.audio_order_button_mode_index = 0
        self.audio_order_button = QPushButton("O")
        self.audio_order_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.audio_order_button.clicked.connect(self.change_audio_order)

        # Layout logic
        self.left_part = QFrame(self)
        # self.left_part.setStyleSheet("background: green;")
        self.middle_part = QFrame(self)
        # self.middle_part.setStyleSheet("background-color: green;")
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

        self.right_part.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.right_part.setFixedSize(self.left_layout.sizeHint())

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 6, 4, 4)
        self.main_layout.addWidget(self.left_part)
        self.main_layout.addWidget(self.middle_part)
        self.main_layout.addWidget(self.right_part)

        if not self.current_playlist:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

        self.background_pixmap = None

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if self.background_pixmap:
            painter = QPainter(self)

            painter.drawPixmap(self.rect(), self.background_pixmap)
            brush = QBrush(QColor(0, 0, 0, 170))
            painter.setBrush(brush)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            painter.drawRect(self.rect())

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        color = DARK_AUDIO_CONTROLLER_COLOR if dark_mode_enabled else LIGHT_AUDIO_CONTROLLER_COLOR
        name = color.name()
        self.setStyleSheet(self.default_stylesheet + f"QWidget {{color: {name};}}")
        self.seek_slider.set_dark_mode_enabled(dark_mode_enabled)

        self.play_icon = change_icon_color(self.play_icon, color)
        self.pause_icon = change_icon_color(self.pause_icon, color)
        self.prev_icon = change_icon_color(self.prev_icon, color)
        self.next_icon = change_icon_color(self.next_icon, color)
        self.volume_on_icon = change_icon_color(self.volume_on_icon, color)
        self.volume_off_icon = change_icon_color(self.volume_off_icon, color)

        if self.is_playing:
            self.play_button.setIcon(self.play_icon)
        else:
            self.play_button.setIcon(self.pause_icon)

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

        palette = self.palette()
        palette.setColor(QPalette.ColorGroup.Normal, QPalette.ColorRole.HighlightedText, color)
        self.star_widget.setPalette(palette)

    def update_background_pixmap(self, track: Track) -> None:
        start = time.time()
        pixmap = get_artwork_pixmap(track.file_path)
        if not pixmap:
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
        print("Audio controller background updated in:", time.time() - start)

    @pyqtSlot(list)
    def queue_next(self, tracks: List[Track]) -> None:
        insert_index = self.current_playlist.playing_track_index + 1
        new_playlist = self.current_playlist.playlist[:insert_index] + tracks + \
            self.current_playlist.playlist[insert_index:]
        self.set_playlist(new_playlist)
        # self.current_playlist.queue_next(tracks)

    @pyqtSlot(list)
    def queue_last(self, tracks: List[Track]) -> None:
        new_playlist = self.current_playlist.playlist + tracks
        self.set_playlist(new_playlist)

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

    def set_playlist(self, playlist: List[Track]) -> None:
        # print("New playlist:\n", "\n".join(str(t) for t in playlist))
        self.prev_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.current_playlist.set_playlist(playlist)
        self.updated_playlist.emit(playlist)
        self.update_total_queue_time(sum(track.length for track in playlist))

    def set_playlist_index(self, index: int) -> None:
        # print("New index:", index)
        self.current_playlist.set_playlist_index(index)

    def play(self) -> None:
        self.seek_slider_time_label.setText("0:00/0:00")
        self.updated_playing_track.emit(self.current_playlist.playing_track, self.current_playlist.playing_track_index)
        self.update_background_pixmap(self.current_playlist.playing_track)
        self.play_button.setIcon(self.pause_icon)
        self.is_playing = True
        self.user_action = 1
        # self.audio_file_name_label.setText(os.path.basename(self.current_playlist.currently_playing.file_path))
        # artist = self.current_playlist.currently_playing.artist
        title = self.current_playlist.playing_track.title
        self.audio_file_name_label.setText(title)
        self.player.setSource(QUrl(self.current_playlist.playing_track.file_path))
        self.player.play()

    def player_duration_changed(self, duration: int) -> None:
        self.seek_slider.setRange(0, duration - 120)
        self.seek_slider_time_label.setText(get_formatted_time(self.player.duration()))
        self.seek_slider.set_length_in_seconds(format_player_position_to_seconds(self.player.duration()))

    def player_position_changed(self, position: int) -> None:
        if not self.player.duration():
            return

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
        self.is_playing = False
        self.user_action = 2
        self.player.pause(fade=fade)
        self.paused.emit(self.get_playing_track())

    def unpause(self, fade=True) -> None:
        self.play_button.setIcon(self.pause_icon)
        self.is_playing = True
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
        return self.current_playlist.playing_track

    def set_playing_track(self, track: Track) -> None:
        if track not in self.current_playlist.playlist:
            raise TrackNotInPlaylistError

        self.set_playlist_index(self.current_playlist.playlist.index(track))
        self.play()

    @pyqtSlot(str)
    def set_audio_output(self, audio_output: str) -> None:
        self.player.set_audio_output(audio_output)


class VolumeSlider(ImprovedSlider):
    light_stylesheet = f"""
    QSlider::handle {{
        height: 4px;
        background: {LIGHT_AUDIO_CONTROLLER_HOVER_COLOR};
    }}

    QSlider::add-page {{
        background: {LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND};
    }}

    QSlider::sub-page {{
        background: {LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND};
    }}
    """

    dark_stylesheet = f"""
    QSlider::handle {{
        height: 4px;
        background: {DARK_AUDIO_CONTROLLER_HOVER_COLOR};
    }}

    QSlider::add-page {{
        background: {DARK_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND};
    }}

    QSlider::sub-page {{
        background: {DARK_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND};
    }}
    """

    def __init__(self, *args):
        super().__init__(*args)

        self.value_changed.connect(self.slider_moved)

    def slider_moved(self, value: int) -> None:
        self.setToolTip(f"{value}%")

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            self.setStyleSheet(self.dark_stylesheet)
        else:
            self.setStyleSheet(self.light_stylesheet)


class SeekSlider(ImprovedSlider):  # TODO add transparent background
    light_stylesheet = f"""
    QSplitter::groove {{
        height: 2px;
    
    }}
    
    QSlider::handle {{
        height: 2px;
        background: {LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_HANDLE_BACKGROUND.name()};
    }}
    
    QSlider::add-page {{
        background: {LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND.name()};
    }}
    
    QSlider::sub-page {{
        background: {LIGHT_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND.name()};
    }}
    """

    dark_stylesheet = f"""
    QSplitter::groove {{
        height: 2px;
        width: 2px;
    
    }}
     
    QSlider::handle {{
        height: 2px;
        width: 2px;
        background: {DARK_AUDIO_CONTROLLER_SEEK_SLIDER_HANDLE_BACKGROUND.name()};
    }}
    
    QSlider::add-page {{
        background: {DARK_AUDIO_CONTROLLER_SEEK_SLIDER_BACKGROUND.name()};
    }}
    
    QSlider::sub-page {{
        background: {DARK_AUDIO_CONTROLLER_SEEK_SLIDER_PASSED_BACKGROUND.name()};
    }}
    """

    def __init__(self, audio_controller: AudioController, *args):
        super().__init__(*args)
        self.audio_controller = audio_controller  # TODO remove self.parent
        self.backup_volume = self.audio_controller.player.audio_output.volume()
        self.backup_action = -1
        self.setFixedHeight(3)
        # self.setContentsMargins(0, 0, 0, 10)
        self.setStyleSheet(self.dark_stylesheet)
        self.length_in_seconds = format_player_position_to_seconds(self.audio_controller.player.duration())
        self.formatted_length_in_seconds = format_seconds(self.length_in_seconds)

    def paintEvent(self, ev: QPaintEvent) -> None:
        # print("Paint called")

        new_rect = ev.rect()
        new_rect.setHeight(2)

        paint_event = QPaintEvent(new_rect)
        # print(paint_event.rect().height())

        super().paintEvent(paint_event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        super().mousePressEvent(event)
        # print("press")
        self.backup_action = self.audio_controller.user_action
        self.audio_controller.player.setPosition(self.pixel_pos_to_range_value(event.pos()))
        # self.backup_volume = self.audio_controller.volume_slider.value() / 100
        # print(self.backup_volume)
        self.audio_controller.pause(fade=False)
        self.audio_controller.player.current_volume = self.audio_controller.volume_slider.value() / 100

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        super().mouseMoveEvent(event)

    def event(self, event):
        if event.type() == QEvent.Type.HoverMove:
            if not self.length_in_seconds:
                return True
            # event = typing.cast(event, QHoverEvent)
            seconds = int((event.oldPos().x() / self.width()) * self.length_in_seconds)
            seconds = max(0, min(seconds, self.length_in_seconds))
            formatted_seconds = format_seconds(seconds)
            tool_tip_str = f"{formatted_seconds}/{self.formatted_length_in_seconds}"
            QToolTip.showText(self.mapToGlobal(event.globalPosition().toPoint()), tool_tip_str, self)

            return True
        return super().event(event)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        # print("release")
        # handles unmuting audio and updating player

        self.audio_controller.set_player_position(self.sliderPosition())

        if self.backup_action == 1:
            # self.audio_controller.player.audio_output.current_volume = self.backup_volume
            self.audio_controller.unpause(fade=False)

        # print(self.backup_volume)

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            self.setStyleSheet(self.dark_stylesheet)
        else:
            self.setStyleSheet(self.light_stylesheet)
        # print(self.styleSheet())

    def set_length_in_seconds(self, length_in_seconds: int) -> None:
        self.length_in_seconds = length_in_seconds
        self.formatted_length_in_seconds = format_seconds(length_in_seconds)

