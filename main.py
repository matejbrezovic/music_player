# stop python from using internet
# import socket
# def guard(*args, **kwargs):
#     raise Exception("I told you not to use the Internet!")
# socket.socket = guard

import sys

from PyQt6 import QtCore
from PyQt6 import QtWidgets
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import *

from models.add_files_dialog import AddFilesDialog
from models.audio_controller import AudioController
from models.information_panel import InformationPanel
from models.main_panel import MainPanel
from models.navigation_panel import NavigationPanel
from models.queue_info_panel import QueueInfoPanel
from models.scan_folders_dialog import *


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.scan_folders_dialog = ScanFoldersDialog()
        self.add_files_dialog = AddFilesDialog()

        # TracksRepository().create_groups()
        self._setup_ui()

        self.setWindowTitle('music player v0.0.9')
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        # self.setMinimumSize(MAIN_PANEL_MIN_WIDTH + 2 * PANEL_MIN_WIDTH + 550, 600)

        # self.setWindowOpacity(0.8)
        # self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.show()

        self.__post__()

    def __post__(self):
        self._setup_signals()

        # self.main_panel.track_view_widget.update_column_width()

    def _setup_ui(self) -> None:
        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout()
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget_layout.setSpacing(0)
        self.central_widget.setLayout(self.central_widget_layout)
        self.setCentralWidget(self.central_widget)

        self._setup_panels()
        # print("SSSS")
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
        self.horizontal_splitter = FixedHorizontalSplitter()
        self.queue_info_panel = QueueInfoPanel(self.audio_controller, self)

        self.horizontal_splitter.addWidget(self.navigation_panel)
        self.horizontal_splitter.addWidget(self.main_panel)
        self.horizontal_splitter.addWidget(self.information_panel)
        self.horizontal_splitter.setSizes([int(PANEL_MIN_WIDTH * 1.5), MAIN_PANEL_MIN_WIDTH * 2,
                                           int(PANEL_MIN_WIDTH * 1.5)])
        self.horizontal_splitter.setStretchFactor(0, 0)
        self.horizontal_splitter.setStretchFactor(1, 1)
        self.horizontal_splitter.setStretchFactor(2, 0)
        self.horizontal_splitter.setChildrenCollapsible(False)

        self.central_widget_layout.addWidget(self.horizontal_splitter)
        self.central_widget_layout.addWidget(self.queue_info_panel)
        self.central_widget_layout.addWidget(self.audio_controller)

    def _setup_signals(self) -> None:
        self.scan_folders_dialog.finished.connect(self.navigation_panel.refresh_groups)
        self.add_files_dialog.finished.connect(self.navigation_panel.refresh_groups)

        # self.main_panel.track_clicked.connect(lambda: ...)  # TODO

        self.main_panel.track_double_clicked.connect(
            lambda track: (self.queue_info_panel.update_info(self.main_panel.displayed_tracks),
                           self.audio_controller.set_playlist(self.main_panel.displayed_tracks),
                           self.audio_controller.set_playlist_index(
                               self.audio_controller.current_playlist.index(track)),
                           self.audio_controller.play(),
                           ))

        self.navigation_panel.group_clicked.connect(
            lambda tracks: (self.main_panel.display_tracks(tracks)))

        self.navigation_panel.group_double_clicked.connect(
            lambda tracks: (self.main_panel.display_tracks(tracks),
                            self.queue_info_panel.update_info(tracks),
                            self.audio_controller.set_playlist(tracks),
                            self.audio_controller.play()))

        # self.information_panel.track_clicked.connect(lambda: ...)

        self.information_panel.track_double_clicked.connect(
            lambda track: (self.audio_controller.set_playlist_index(
                            self.audio_controller.current_playlist.index(track)),
                           self.audio_controller.play()))

        self.audio_controller.updated_playing_track.connect(
            lambda track: (self.main_panel.set_playing_track(track),
                           self.information_panel.set_currently_playing_track(track)))

        self.audio_controller.paused.connect(lambda: (self.main_panel.pause_playing_track(),
                                             self.information_panel.pause_playing_track()))
        self.audio_controller.unpaused.connect(lambda: (self.main_panel.unpause_playing_track(),
                                               self.information_panel.unpause_playing_track()))
        self.audio_controller.updated_playlist.connect(lambda tracks: self.information_panel.set_playing_tracks(tracks))

        self.audio_controller.remaining_queue_time_changed.connect(self.queue_info_panel.update_remaining_queue_time)
        # self.queue_info_panel.right_label_clicked.connect()


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
        # noinspection PyArgumentList
        self.setStyle(QStyleFactory.create("windowsvista"))


if __name__ == '__main__':
    app = App(sys.argv)
    mainWindow = MainWindowUi()
    sys.exit(app.exec())
