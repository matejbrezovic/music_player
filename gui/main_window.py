from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenuBar, QWidget, QMenu, QMainWindow, QVBoxLayout

from constants import (APPLICATION_NAME, MAIN_WINDOW_Y, MAIN_PANEL_MIN_WIDTH, PANEL_MIN_WIDTH, MAIN_WINDOW_X,
                       MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
from data_models.track import Track
from gui.audio.audio_controller import AudioController
from gui.audio.audio_queue import AudioQueue
from gui.dialogs.add_files_dialog import AddFilesDialog
from gui.dialogs.scan_folders_dialog import ScanFoldersDialog
from gui.panels.queue_panel import QueuePanel
from gui.panels.main_panel import MainPanel
from gui.panels.group_panel import GroupPanel
from gui.widgets.header_menu_widget import HeaderMenuWidget
from gui.widgets.status_bar import StatusBar
from repositories.cached_tracks_repository import CachedTracksRepository
from utils import FixedHorizontalSplitter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scan_folders_dialog = ScanFoldersDialog()
        self.add_files_dialog = AddFilesDialog()

        self.cached_tracks_repository = CachedTracksRepository()
        self.cached_tracks_repository.load_cache()

        self._setup_ui()

        self.audio_queue = AudioQueue()

        self.setWindowTitle(APPLICATION_NAME)
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

    def show(self):
        super().show()
        self._setup_signals()
        self.group_panel.refresh_groups()

    def _setup_ui(self) -> None:
        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout()
        self.central_widget_layout.setContentsMargins(1, 1, 1, 1)
        self.central_widget_layout.setSpacing(0)
        self.central_widget.setLayout(self.central_widget_layout)
        self.setCentralWidget(self.central_widget)

        self._setup_panels()
        self._setup_menu_bar()

    def _setup_menu_bar(self) -> None:
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu("&File", self)
        add_files_action = QAction("&Add Files to Library", self)
        add_files_action.triggered.connect(lambda: self.add_files_dialog.exec())
        scan_folders_action = QAction("&Scan Folders for New Files", self)
        scan_folders_action.triggered.connect(lambda: self.scan_folders_dialog.exec())

        file_menu.addAction(add_files_action)
        file_menu.addAction(scan_folders_action)

        self.menu_bar.addMenu(file_menu)

    def _setup_panels(self) -> None:
        self.group_panel = GroupPanel(self)
        self.main_panel = MainPanel(self)
        self.queue_panel = QueuePanel(self)
        self.audio_controller = AudioController(self)
        self.status_bar = StatusBar(self.audio_controller, self)
        self.header_menu = HeaderMenuWidget(self)
        self.horizontal_splitter = FixedHorizontalSplitter(self)
        self.horizontal_splitter.sizes_changed.connect(self.header_menu.set_sizes)

        self.horizontal_splitter.addWidget(self.group_panel)
        self.horizontal_splitter.addWidget(self.main_panel)
        self.horizontal_splitter.addWidget(self.queue_panel)
        self.horizontal_splitter.setSizes([int(PANEL_MIN_WIDTH), MAIN_PANEL_MIN_WIDTH * 2, int(PANEL_MIN_WIDTH)])
        self.horizontal_splitter.setStretchFactor(0, 0)
        self.horizontal_splitter.setStretchFactor(1, 1)
        self.horizontal_splitter.setStretchFactor(2, 0)
        self.horizontal_splitter.setHandleWidth(1)
        self.horizontal_splitter.setStyleSheet("""
        QSplitter::handle {background-color: rgba(0, 0, 0, 0.2);}
        """)
        self.horizontal_splitter.setChildrenCollapsible(False)
        # self.horizontal_splitter.setOpaqueResize(False)

        self.central_widget_layout.addWidget(self.header_menu)
        self.central_widget_layout.addWidget(self.horizontal_splitter)
        self.central_widget_layout.addWidget(self.status_bar)
        self.central_widget_layout.addWidget(self.audio_controller)

        self.audio_controller.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _setup_signals(self) -> None:
        def play_now_triggered(tracks: List[Track]) -> None:
            if len(tracks) == 1:
                if self.main_panel.displayed_tracks != self.audio_queue.get_queue():
                    self.audio_controller.set_queue(self.main_panel.displayed_tracks)
                self.audio_controller.set_playing_track(tracks[0])
            else:
                self.audio_controller.set_queue(tracks)
                self.audio_controller.set_playing_track(tracks[0])

        self.scan_folders_dialog.finished.connect(self.group_panel.refresh_groups)
        self.add_files_dialog.finished.connect(self.group_panel.refresh_groups)

        self.header_menu.navigation_panel_group_key_changed.connect(self.group_panel.group_key_changed)
        self.header_menu.main_panel_view_key_changed.connect(self.main_panel.view_key_changed)
        self.header_menu.information_panel_view_key_changed.connect(self.queue_panel.view_key_changed)

        self.main_panel.track_double_clicked.connect(
            lambda track, _: (self.status_bar.update_info(self.main_panel.displayed_tracks),
                              self.audio_queue.set_queue(self.main_panel.displayed_tracks),
                              self.audio_queue.set_playing_track(track),
                              self.audio_controller.play()))
        self.main_panel.play_now_triggered.connect(play_now_triggered)
        self.main_panel.queue_next_triggered.connect(self.queue_next)
        self.main_panel.queue_last_triggered.connect(self.queue_last)
        self.main_panel.output_to_triggered.connect(self.audio_controller.set_audio_output)
        self.main_panel.tracks_deleted.connect(self.tracks_deleted)

        self.group_panel.group_clicked.connect(
            lambda tracks, key_value_tuple: (self.main_panel.display_tracks(tracks, key_value_tuple)))

        self.group_panel.group_double_clicked.connect(
            lambda tracks, key_value_tuple: (self.main_panel.display_tracks(tracks, key_value_tuple),
                                             self.status_bar.update_info(self.main_panel.displayed_tracks),
                                             self.audio_controller.set_queue(self.main_panel.displayed_tracks),
                                             self.audio_queue.set_playing_track(self.main_panel.displayed_tracks[0]),
                                             self.audio_controller.play()))

        self.audio_queue.playing_track_updated.connect(
            lambda track: (
                self.main_panel.set_playing_track(track),
                self.queue_panel.set_playing_track(track),
                self.audio_controller.play()
            )
        )

        self.audio_controller.paused.connect(lambda: (self.main_panel.pause_playing_track(),
                                             self.queue_panel.pause_playing_track()))
        self.audio_controller.unpaused.connect(lambda: (self.main_panel.unpause_playing_track(),
                                               self.queue_panel.unpause_playing_track()))
        self.audio_controller.remaining_queue_time_changed.connect(self.status_bar.update_remaining_queue_time)
        self.audio_controller.player_stopped.connect(self._player_stopped)

        self.scan_folders_dialog.added_tracks.connect(self._added_tracks_to_database)
        self.scan_folders_dialog.removed_tracks.connect(self._removed_tracks_from_database)

        self.add_files_dialog.added_tracks.connect(self._added_tracks_to_database)

        self.audio_controller.background_pixmap_updated.connect(self.queue_panel.set_track_pixmap)

    def queue_next(self, tracks_to_queue: List[Track]) -> None:
        self.audio_controller.enqueue_next(tracks_to_queue)
        self.status_bar.update_info(self.audio_controller.get_tracks())

    def queue_last(self, tracks_to_queue: List[Track]) -> None:
        self.audio_controller.enqueue_last(tracks_to_queue)
        self.status_bar.update_info(self.audio_controller.get_tracks())

    def _added_tracks_to_database(self, _: List[Track] = None) -> None:
        tracks_from_last_selected_group = self.group_panel.get_last_selected_tracks()
        self.main_panel.display_tracks(tracks_from_last_selected_group)
        self.main_panel.set_playing_track(self.audio_controller.get_playing_track())

    def tracks_deleted(self, deleted_tracks: List[Track]) -> None:
        self.cached_tracks_repository.drop_tracks(deleted_tracks)
        self.group_panel.refresh_groups()

    def _removed_tracks_from_database(self, tracks: List[Track]) -> None:
        ...

    def _player_stopped(self) -> None:
        self.main_panel.stop_playing()
        self.queue_panel.stop_playing()
