from typing import List

from PIL import UnidentifiedImageError
from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot, QSize, QPoint, Qt, QThread, QTimer
from PyQt6.QtGui import QBrush, QPixmap, QPainter, QIcon, QFont, QPaintEvent, QWheelEvent, QColor, QImage
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QFrame, QSpacerItem, QWidget

from constants import (AUDIO_CONTROLLER_HEIGHT, ROOT, CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH,
                       STARTING_AUDIO_VOLUME, DARK_AUDIO_CONTROLLER_COLOR, LIGHT_AUDIO_CONTROLLER_COLOR)
from data_models.track import Track
from gui.audio.audio_player import AudioPlayer
from gui.audio.audio_playlist import AudioPlaylist
from gui.audio.enums import UserAction, RepeatMode
from gui.dialogs.track_not_found_dialog import TrackNotFoundDialog
from gui.star.star_widget import StarWidget
from gui.widgets.marquee_label import MarqueeLabel
from gui.widgets.seek_slider import SeekSlider
from gui.widgets.volume_slider import VolumeSlider
from utils import (get_formatted_time, format_player_position_to_seconds, TrackNotInPlaylistError,
                   get_embedded_artwork_pixmap, get_blurred_pixmap, change_icon_color, HoverButton, format_seconds,
                   get_default_artwork_pixmap, ImageDownloader)


class AudioController(QFrame):
    playing_track_updated = pyqtSignal(Track, int)
    playlist_updated = pyqtSignal(list)
    paused = pyqtSignal(Track)
    unpaused = pyqtSignal(Track)
    remaining_queue_time_changed = pyqtSignal(int)
    playback_error_encountered = pyqtSignal(Track)
    player_stopped = pyqtSignal()
    background_pixmap_updated = pyqtSignal(QPixmap)

    default_stylesheet = "QFrame#audio_controller {background-color: rgba(0, 0, 0, 0.2)}"

    def __init__(self, *args):
        super().__init__(*args)
        self.setObjectName("audio_controller")
        self.setStyleSheet(self.default_stylesheet)
        self.setFixedHeight(AUDIO_CONTROLLER_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._is_dark_mode_enabled = None
        self._image_downloader_thread = QThread()
        self.image_downloader = ImageDownloader()
        self.image_downloader.image_downloaded.connect(self._image_downloaded)
        self.image_downloader.image_downloaded.connect(self._image_downloader_thread.quit)
        self.image_downloader.moveToThread(self._image_downloader_thread)
        self._image_downloader_thread.started.connect(self.image_downloader.get_image)
        self._background_pixmap_update_timer = QTimer()
        self._background_pixmap_update_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._background_pixmap_update_timer.setSingleShot(True)

        self.playlist = AudioPlaylist()
        self.playlist.updated_playlist.connect(self.playlist_updated)
        self._playing_track = None

        self.total_queue_time = 0
        self._rounded_remaining_queue_time = 0  # shouldn't update while track is playing
        self.remaining_queue_time = 0
        self._user_action = UserAction.Stopped
        self._repeat_mode = RepeatMode.RepeatOff
        self._backup_action = self._user_action
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
        self.prev_icon = QIcon(QPixmap(ROOT + "/icons/prev.png"))
        self.next_icon = QIcon(QPixmap(ROOT + "/icons/next.png"))
        self.volume_on_icon = QIcon(QPixmap(ROOT + "/icons/speaker-playing.png"))
        self.volume_off_icon = QIcon(QPixmap(ROOT + "/icons/speaker-muted.png"))

        self.repeat_off_icon = QIcon(QPixmap(ROOT + "/icons/repeat-off.png"))
        self.repeat_on_icon = QIcon(QPixmap(ROOT + "/icons/repeat-on.png"))
        self.repeat_one_icon = QIcon(QPixmap(ROOT + "/icons/repeat-one.png"))

        self.play_button.setIcon(self.play_icon)
        self.prev_button.setIcon(self.prev_icon)
        self.next_button.setIcon(self.next_icon)

        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

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

        self.volume_button = HoverButton()
        self.volume_button.setIcon(self.volume_on_icon)
        self.volume_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT, CONTROLLER_BUTTON_WIDTH)
        self.volume_button.clicked.connect(self.volume_button_clicked)
        self.volume_button.setStyleSheet("background-color: transparent;")

        self.seek_slider = SeekSlider(self)
        self.seek_slider.setOrientation(Qt.Orientation.Horizontal)
        self.seek_slider.setTracking(False)
        self.seek_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.seek_slider.slider_pressed.connect(self.seek_slider_pressed)
        self.seek_slider.slider_released.connect(self.seek_slider_released)
        self.seek_slider.slider_moved.connect(self.seek_slider_moved)

        self.star_widget = StarWidget(0, self)
        self.star_widget.setFixedWidth(90)

        self.passed_time_label = QLabel("0:00/ 0:00")
        self.passed_time_label.setFixedWidth(90)
        self.track_title_label = MarqueeLabel(self)
        self.track_title_label.setFont(QFont(self.track_title_label.font().family(), 9))
        self.track_title_label.setText("~~~")
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

        self.is_audio_order_shuffled = False
        self.audio_order_button = HoverButton(self)
        self.audio_order_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT + 10, CONTROLLER_BUTTON_WIDTH + 10)
        self.audio_order_button.setIconSize(QSize(CONTROLLER_BUTTON_HEIGHT + 10, CONTROLLER_BUTTON_WIDTH + 10))
        self.audio_order_button.clicked.connect(self.change_audio_order)

        self.ordered_icon = QIcon(QPixmap(ROOT + "/icons/ordered.png"))
        self.shuffled_icon = QIcon(QPixmap(ROOT + "/icons/shuffled.png"))

        self.audio_order_button.setStyleSheet("background: transparent;")
        self.audio_order_button.setIcon(self.ordered_icon)

        self.repeat_mode_button = HoverButton(self)
        self.repeat_mode_button.setFixedSize(CONTROLLER_BUTTON_HEIGHT + 10, CONTROLLER_BUTTON_WIDTH + 10)
        self.repeat_mode_button.setIconSize(QSize(CONTROLLER_BUTTON_HEIGHT + 10, CONTROLLER_BUTTON_WIDTH + 10))
        self.repeat_mode_button.setIcon(self.repeat_off_icon)
        self.repeat_mode_button.clicked.connect(self.change_repeat_mode)
        self.repeat_mode_button.setStyleSheet("background: transparent;")

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

        self.left_part.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.left_part.setFixedSize(self.left_layout.sizeHint())

        self.middle_layout = QVBoxLayout(self.middle_part)
        self.middle_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.middle_layout.addWidget(self.name_time_label_container)
        self.middle_layout.addWidget(self.seek_slider)
        self.middle_layout.setContentsMargins(0, 6, 0, 4)

        self.right_layout = QHBoxLayout(self.right_part)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.right_layout.addWidget(self.repeat_mode_button)
        self.right_layout.addWidget(self.audio_order_button)
        # self.right_layout.addWidget(self.spectrum_equalizer_widget)

        self.right_part.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.right_part.setFixedSize(self.left_layout.sizeHint())

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 0, 10, 0)
        self.main_layout.addWidget(self.left_part)
        self.main_layout.addWidget(self.middle_part)
        self.main_layout.addWidget(self.right_part)

        if not self.playlist:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

        self.background_pixmap = None
        self.star_widget.setEnabled(False)

        for child in self.findChildren(QWidget):
            if isinstance(child, QWidget):
                child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.set_dark_mode_enabled(True)

    def paintEvent(self, event: QPaintEvent) -> None:
        if self.background_pixmap:
            painter = QPainter(self)

            painter.drawPixmap(self.rect(), self.background_pixmap)
            brush = QBrush(QColor(0, 0, 0, 170))
            painter.setBrush(brush)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            painter.drawRect(self.rect())

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.volume_slider.wheelEvent(event)
        super().wheelEvent(event)

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

        self.ordered_icon = change_icon_color(self.ordered_icon, color)
        self.shuffled_icon = change_icon_color(self.shuffled_icon, color)

        self.repeat_off_icon = change_icon_color(self.repeat_off_icon, color)
        self.repeat_on_icon = change_icon_color(self.repeat_on_icon, color)
        self.repeat_one_icon = change_icon_color(self.repeat_one_icon, color)

        if self.is_playing:
            self.play_button.setIcon(self.pause_icon)
        else:
            self.play_button.setIcon(self.play_icon)

        if self.is_muted:
            self.volume_button.setIcon(self.volume_off_icon)
        else:
            self.volume_button.setIcon(self.volume_on_icon)

        if self.is_audio_order_shuffled:
            self.audio_order_button.setIcon(self.shuffled_icon)
        else:
            self.audio_order_button.setIcon(self.ordered_icon)

        if self._repeat_mode == RepeatMode.RepeatOff:
            self.repeat_mode_button.setIcon(self.repeat_off_icon)
        elif self._repeat_mode == RepeatMode.RepeatOn:
            self.repeat_mode_button.setIcon(self.repeat_on_icon)
        else:
            self.repeat_mode_button.setIcon(self.repeat_one_icon)

        self.prev_button.setIcon(self.prev_icon)
        self.next_button.setIcon(self.next_icon)

        self.play_button.set_is_in_dark_mode(dark_mode_enabled)
        self.volume_button.set_is_in_dark_mode(dark_mode_enabled)
        self.prev_button.set_is_in_dark_mode(dark_mode_enabled)
        self.next_button.set_is_in_dark_mode(dark_mode_enabled)

        self.audio_order_button.set_is_in_dark_mode(dark_mode_enabled)
        self.repeat_mode_button.set_is_in_dark_mode(dark_mode_enabled)

        self.star_widget.set_star_color(color)

    def _set_to_default(self) -> None:
        self.background_pixmap = None
        self.set_dark_mode_enabled(True)
        self.background_pixmap_updated.emit(get_default_artwork_pixmap("album"))
        self.repaint()

    def _set_custom_background_pixmap(self, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            self._set_to_default()

        self.background_pixmap_updated.emit(pixmap)

        pixmap = get_blurred_pixmap(pixmap)
        start_y = int(pixmap.height() // 1.5)
        new_height = 60
        pixmap = pixmap.copy(0, start_y, pixmap.width(), new_height)

        self.background_pixmap = pixmap
        self.set_dark_mode_enabled(False)
        self.repaint()

    def _image_downloaded(self, qimage: QImage, track: Track = None) -> None:
        if track == self.get_playing_track():
            pixmap = QPixmap.fromImage(qimage)
            try:
                self._set_custom_background_pixmap(pixmap)
            except UnidentifiedImageError:
                self.update_background_pixmap(track)

    def update_background_pixmap(self, track: Track, reset_to_default: bool = False) -> None:
        if reset_to_default or not (track.artist and track.title):
            self._set_to_default()
            return

        pixmap = get_embedded_artwork_pixmap(track.file_path)
        if not pixmap:
            self._set_to_default()
            self._background_pixmap_update_timer.stop()
            self.image_downloader.deleteLater()
            self._image_downloader_thread.quit()

            self.image_downloader = ImageDownloader()
            self.image_downloader.image_downloaded.connect(self._image_downloaded)
            self.image_downloader.image_downloaded.connect(self._image_downloader_thread.quit)
            self.image_downloader.set_track(track)
            self.image_downloader.moveToThread(self._image_downloader_thread)
            self._image_downloader_thread.started.connect(self.image_downloader.get_image)
            self._background_pixmap_update_timer.timeout.connect(
                lambda: self._image_downloader_thread.start())
            self._background_pixmap_update_timer.start(2000)

        else:
            self._set_custom_background_pixmap(pixmap)

    @pyqtSlot()
    def playlist_ended(self):
        self.player.stop()
        self.play_button.setIcon(self.play_icon)
        self._user_action = UserAction.Stopped
        self.seek_slider.setEnabled(False)
        self.player_stopped.emit()

    @pyqtSlot(list)
    def queue_next(self, tracks: List[Track]) -> None:
        self.playlist.queue_next(tracks)
        self.playlist_updated.emit(self.playlist.playlist)
        self.next_button.setEnabled(True)
        self.update_total_queue_time(sum(track.length for track in self.playlist.playlist))

    @pyqtSlot(list)
    def queue_last(self, tracks: List[Track]) -> None:
        self.playlist.queue_last(tracks)
        self.next_button.setEnabled(True)
        self.playlist_updated.emit(self.playlist.playlist)
        self.update_total_queue_time(sum(track.length for track in self.playlist.playlist))

    @pyqtSlot(int)
    def update_total_queue_time(self, time_in_secs: int) -> None:
        self.total_queue_time = time_in_secs
        self._rounded_remaining_queue_time = time_in_secs
        self.remaining_queue_time = time_in_secs
        self.remaining_queue_time_changed.emit(self.remaining_queue_time)

    @pyqtSlot()
    def change_audio_order(self) -> None:
        self.playlist.change_audio_order()
        self.is_audio_order_shuffled = not self.is_audio_order_shuffled
        if self.is_audio_order_shuffled:
            self.audio_order_button.setIcon(self.shuffled_icon)
        else:
            self.audio_order_button.setIcon(self.ordered_icon)

        self.update_total_queue_time(sum(track.length for track in self.playlist.playlist))

    @pyqtSlot()
    def change_repeat_mode(self) -> None:
        # repeat_off -> repeat_on -> repeat_one -> repeat_off ...
        if self._repeat_mode == RepeatMode.RepeatOff:
            self._repeat_mode = RepeatMode.RepeatOn
            self.repeat_mode_button.setIcon(self.repeat_on_icon)
            self.playlist.set_repeat_on()
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)
        elif self._repeat_mode == RepeatMode.RepeatOn:
            self._repeat_mode = RepeatMode.RepeatOne
            self.repeat_mode_button.setIcon(self.repeat_one_icon)
            self.playlist.set_repeat_one()
        elif self._repeat_mode == RepeatMode.RepeatOne:
            self._repeat_mode = RepeatMode.RepeatOff
            self.repeat_mode_button.setIcon(self.repeat_off_icon)
            self.playlist.set_repeat_off()

            if self.get_playing_track() and self.playlist.index(self.get_playing_track()) == len(self.playlist) - 1:
                self.next_button.setEnabled(False)
            else:
                self.next_button.setEnabled(True)

    @pyqtSlot(int)
    def set_player_position(self, position: int) -> None:
        self.player.setPosition(position)

    @pyqtSlot(list)
    def set_playlist(self, playlist: List[Track]) -> None:
        self.prev_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.playlist.set_playlist(playlist)
        self.playlist.set_playlist_index(0)
        self.playlist_updated.emit(playlist)
        self.update_total_queue_time(sum(track.length for track in playlist))
        self.playlist.update_currently_playing()

    @pyqtSlot(int)
    def set_playlist_index(self, index: int) -> None:
        self.playlist.set_playlist_index(index)

    @pyqtSlot()
    def play(self) -> None:
        self._background_pixmap_update_timer.stop()
        if not self.get_playing_track():
            return

        new_playing_track = self.get_playing_track()

        self.passed_time_label.setText(f"0:00/ {format_seconds(new_playing_track.length)}")

        self.track_title_label.setText(new_playing_track.display_name)

        if not self.playlist.index(new_playing_track) and self._repeat_mode == RepeatMode.RepeatOff:
            self.prev_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(True)

        if self.playlist.index(new_playing_track) == len(self.playlist) - 1 and \
                self._repeat_mode == RepeatMode.RepeatOff:
            self.next_button.setEnabled(False)
        else:
            self.next_button.setEnabled(True)

        self.is_playing = new_playing_track.is_valid()

        if new_playing_track.is_valid():
            self._user_action = UserAction.Playing
            self.star_widget.setEnabled(True)
            self.seek_slider.setEnabled(True)

            self.play_button.setIcon(self.pause_icon)
            self.player.setSource(QUrl(new_playing_track.file_path))
            self.player.play()
            self.playing_track_updated.emit(new_playing_track, self.playlist.get_ordered_playing_track_index())
            if self._playing_track != new_playing_track:
                self._playing_track = new_playing_track
                self.update_background_pixmap(new_playing_track)

        else:
            self._user_action = UserAction.Stopped
            self.star_widget.setEnabled(False)
            self.update_background_pixmap(new_playing_track, reset_to_default=True)
            self.play_button.setIcon(self.play_icon)
            self.player.stop()
            self.seek_slider.setEnabled(False)
            self.player_stopped.emit()
            t = TrackNotFoundDialog(new_playing_track)
            t.exec()  # must be 'exec', not show, because on the first 'show' dialog instantly closes

    @pyqtSlot('qint64')
    def player_duration_changed(self, duration: int) -> None:
        self.seek_slider.setRange(0, duration - 120)
        self.seek_slider.set_length_in_seconds(format_player_position_to_seconds(self.player.duration()))

    @pyqtSlot('qint64')
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

    @pyqtSlot(int)
    def seek_slider_pressed(self, pos: int) -> None:
        self._backup_action = self._user_action
        self.set_player_position(self.seek_slider.pixel_pos_to_range_value(QPoint(pos, 0)))
        self.pause(fade=False)

    @pyqtSlot(int)
    def seek_slider_moved(self, pos: int) -> None:
        self.player.setPosition(self.seek_slider.pixel_pos_to_range_value(QPoint(pos, 0)))

    @pyqtSlot(int)
    def seek_slider_released(self) -> None:
        if self._backup_action == UserAction.Playing:
            self.unpause(fade=False)

    def get_remaining_time_in_secs(self) -> int:  # TODO fully implement, not currently used
        return self._rounded_remaining_queue_time - format_player_position_to_seconds(self.player.position())

    def pause(self, fade=True) -> None:
        self.play_button.setIcon(self.play_icon)
        self.is_playing = False
        self._user_action = UserAction.Paused
        self.player.pause(fade=fade)
        self.paused.emit(self.get_playing_track())

    def unpause(self, fade=True) -> None:
        self.play_button.setIcon(self.pause_icon)
        self.is_playing = True
        self._user_action = UserAction.Playing
        self.player.play(fade=fade)
        self.unpaused.emit(self.get_playing_track())

    @pyqtSlot()
    def play_pause_button_clicked(self) -> None:
        if not self.playlist:
            return

        if self._user_action == UserAction.Stopped:
            if self.get_playing_track().is_valid():
                if not self.playlist.has_ended():
                    self.playlist.set_playlist_index(0)
            self.play()
        elif self._user_action == UserAction.Playing:
            self.pause()
        elif self._user_action == UserAction.Paused:
            self.unpause()

    @pyqtSlot()
    def next_button_clicked(self) -> None:
        self.playlist.set_next()

        if self.playlist.has_ended():
            self.playlist_ended()
            self.next_button.setEnabled(False)
            return
        self.next_button.setEnabled(True)
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

        if self.playlist.has_ended():
            self.playlist_ended()
            self.prev_button.setEnabled(False)
            return

        self.prev_button.setEnabled(True)
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
        self.player.audioOutput().setVolume(volume_value / 100)
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
        if self.player.audioOutput().volume():
            self.volume_slider_position_backup = self.volume_slider_position
            self.volume_slider.setSliderPosition(0)
            self.player.current_volume = self.player.audioOutput().volume()
            self.is_muted = True
        else:
            self.volume_slider_position = self.volume_slider_position_backup
            self.volume_slider.setSliderPosition(self.volume_slider_position)
            self.player.current_volume = self.player.audioOutput().volume()
            self.is_muted = False

    def get_playing_track(self) -> Track:
        return self.playlist.playing_track

    def get_tracks(self) -> List[Track]:
        return self.playlist.playlist

    @pyqtSlot(Track, int)
    def set_playing_track(self, track: Track, index: int) -> None:
        if track not in self.playlist.playlist:
            raise TrackNotInPlaylistError

        self.set_playlist_index(index)
        self.play()

    @pyqtSlot(str)
    def set_audio_output(self, audio_output: str) -> None:
        self.player.set_audio_output(audio_output)
