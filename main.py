# stop python from using internet
# import socket
# def guard(*args, **kwargs):
#     raise Exception("I told you not to use the Internet!")
# socket.socket = guard

import sys
import time

from PyQt6 import QtWidgets
from PyQt6.QtGui import QAction
from data_models.track import Track
from models.add_files_dialog import AddFilesDialog
from models.app import App
from models.audio_controller import AudioController
from models.header_menu_widget import HeaderMenuWidget
from models.information_panel import InformationPanel
from models.main_panel import MainPanel
from models.navigation_panel import NavigationPanel
from models.queue_info_panel import QueueInfoPanel
from models.scan_folders_dialog import *
from repositories.cached_tracks_repository import CachedTracksRepository


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.scan_folders_dialog = ScanFoldersDialog()
        self.add_files_dialog = AddFilesDialog()

        # TracksRepository().create_groups()
        self._setup_ui()

        self.setWindowTitle(APPLICATION_NAME)
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        # self.setMinimumSize(MAIN_PANEL_MIN_WIDTH + 2 * PANEL_MIN_WIDTH + 550, 600)

        # self.setWindowOpacity(0.8)
        # self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        CachedTracksRepository().cache_tracks()

    def __post__(self):
        self._setup_signals()
        self.navigation_panel.refresh_groups()

        # self.main_panel.track_view_widget.update_column_width()

    def show(self):
        super().show()
        self.__post__()

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
        self.menu_bar = QtWidgets.QMenuBar(self)
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
        self.navigation_panel = NavigationPanel(self)
        self.main_panel = MainPanel(self)
        self.information_panel = InformationPanel(self)
        self.audio_controller = AudioController(self)
        self.queue_info_panel = QueueInfoPanel(self.audio_controller, self)
        self.header_menu = HeaderMenuWidget(self)
        self.horizontal_splitter = FixedHorizontalSplitter(self)
        self.horizontal_splitter.sizes_changed.connect(self.header_menu.set_sizes)

        self.horizontal_splitter.addWidget(self.navigation_panel)
        self.horizontal_splitter.addWidget(self.main_panel)
        self.horizontal_splitter.addWidget(self.information_panel)
        self.horizontal_splitter.setSizes([int(PANEL_MIN_WIDTH * 1.5), MAIN_PANEL_MIN_WIDTH * 2,
                                           int(PANEL_MIN_WIDTH * 1.5)])
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
        self.central_widget_layout.addWidget(self.queue_info_panel)
        self.central_widget_layout.addWidget(self.audio_controller)

    def _setup_signals(self) -> None:
        def play_now_triggered(tracks: List[Track]) -> None:
            if len(tracks) == 1:
                if self.main_panel.displayed_tracks != self.information_panel.playing_tracks:
                    self.audio_controller.set_playlist(self.main_panel.displayed_tracks)
                self.audio_controller.set_playing_track(tracks[0])
            else:
                self.audio_controller.set_playlist(tracks)
                self.audio_controller.set_playing_track(tracks[0])

        self.scan_folders_dialog.finished.connect(self.navigation_panel.refresh_groups)
        self.add_files_dialog.finished.connect(self.navigation_panel.refresh_groups)

        # self.main_panel.track_clicked.connect(lambda: ...)  # TODO

        self.header_menu.navigation_panel_group_key_changed.connect(self.navigation_panel.group_key_changed)
        self.header_menu.main_panel_view_key_changed.connect(self.main_panel.view_key_changed)
        self.header_menu.information_panel_view_key_changed.connect(self.information_panel.view_key_changed)

        self.main_panel.track_double_clicked.connect(
            lambda track, index: (self.queue_info_panel.update_info(self.main_panel.displayed_tracks),
                                  self.audio_controller.set_playlist(self.main_panel.displayed_tracks),
                                  self.audio_controller.set_playlist_index(index),
                                  self.audio_controller.play(),
                                  ))
        self.main_panel.play_now_triggered.connect(play_now_triggered)
        self.main_panel.queue_next_triggered.connect(self.audio_controller.queue_next)  # TODO update queue info panel
        self.main_panel.queue_last_triggered.connect(self.audio_controller.queue_last)
        self.main_panel.output_to_triggered.connect(self.audio_controller.set_audio_output)

        self.navigation_panel.group_clicked.connect(
            lambda tracks: (self.main_panel.display_tracks(tracks)))

        self.navigation_panel.group_double_clicked.connect(
            lambda tracks: (self.main_panel.display_tracks(tracks),
                            self.queue_info_panel.update_info(tracks),
                            self.audio_controller.set_playlist(tracks),
                            self.audio_controller.play()))

        # self.information_panel.track_clicked.connect(lambda: ...)

        self.information_panel.track_double_clicked.connect(
            lambda track, index: (self.audio_controller.set_playlist_index(index),
                                  self.audio_controller.play()))

        self.audio_controller.updated_playing_track.connect(
            lambda track, index: (self.main_panel.set_playing_track(track),
                                  self.information_panel.set_playing_track(track, index)))

        self.audio_controller.paused.connect(lambda: (self.main_panel.pause_playing_track(),
                                             self.information_panel.pause_playing_track()))
        self.audio_controller.unpaused.connect(lambda: (self.main_panel.unpause_playing_track(),
                                               self.information_panel.unpause_playing_track()))
        self.audio_controller.updated_playlist.connect(lambda tracks: self.information_panel.set_playing_tracks(tracks))

        self.audio_controller.remaining_queue_time_changed.connect(self.queue_info_panel.update_remaining_queue_time)
        # self.queue_info_panel.right_label_clicked.connect(...)


if __name__ == '__main__':
    start = time.time()
    app = App(sys.argv)
    main_window = MainWindowUi()
    main_window.show()
    print(f"Window shown in: {time.time() - start:.6f}")
    sys.exit(app.exec())
