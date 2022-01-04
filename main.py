import sys

from PyQt6 import QtWidgets
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import *

from models.audio_controller import AudioController
from models.dialogs import *
from models.information_panel import InformationPanel
from models.main_panel import MainPanel
from models.navigation_panel import NavigationPanel


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.scan_folders_dialog = ScanFoldersDialog()

        self._setup_ui()
        self._setup_signals()

        self.scan_folders_dialog.finished.connect(self.navigation_panel.refresh_groups)

        self.setWindowTitle('music player v0.0.6')
        self.setGeometry(MAIN_WINDOW_X, MAIN_WINDOW_Y, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setMinimumSize(MAIN_PANEL_MIN_WIDTH + 2 * PANEL_MIN_WIDTH + 550, 600)

        self.show()
        self.main_panel.track_view_widget.update_column_width()

    def _setup_ui(self) -> None:
        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget_layout)
        self.setCentralWidget(self.central_widget)

        self._setup_panels()
        self._setup_menu_bar()

    # noinspection PyTypeChecker
    def _setup_menu_bar(self) -> None:
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu("&File", self)
        add_files_action = QAction("&Add Files to Library", self)
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

        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.horizontal_splitter.addWidget(self.navigation_panel)
        self.horizontal_splitter.addWidget(self.main_panel)
        self.horizontal_splitter.addWidget(self.information_panel)
        self.horizontal_splitter.setSizes([int(PANEL_MIN_WIDTH * 1.5), MAIN_PANEL_MIN_WIDTH * 2,
                                           int(PANEL_MIN_WIDTH * 1.5)])

        self.central_widget_layout.addWidget(self.horizontal_splitter)
        self.central_widget_layout.addWidget(self.audio_controller)

    def _setup_signals(self):
        self.main_panel.track_double_clicked.connect(lambda track: (self.audio_controller.set_playlist(
                                                                    self.main_panel.displayed_tracks),
                                                                    self.audio_controller.set_playlist_index(
                                                                    self.audio_controller.current_playlist.index(
                                                                        track)),
                                                                    self.audio_controller.play()))
        self.navigation_panel.group_clicked.connect(lambda tracks: (self.main_panel.display_tracks(tracks),
                                                                    self.main_panel.select_track(
                                                                        self.audio_controller.get_current_track())))
        self.navigation_panel.group_double_clicked.connect(lambda tracks: (self.main_panel.display_tracks(tracks),
                                                                           self.audio_controller.set_playlist(tracks),
                                                                           self.audio_controller.play()))
        self.audio_controller.updated_playing_track.connect(lambda track: (self.main_panel.select_track(track),
                                                                           self.information_panel.
                                                                           set_currently_playing_track(track)))
        self.audio_controller.updated_playlist.connect(lambda tracks: self.information_panel.set_playing_tracks(tracks))
        self.information_panel.track_double_clicked.connect(lambda track: (self.audio_controller.set_playlist_index(
                                                                    self.audio_controller.current_playlist.index(
                                                                        track)),
                                                                    self.audio_controller.play()))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowUi()
    sys.exit(app.exec())
