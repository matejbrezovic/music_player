import os
import sys
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QApplication, QVBoxLayout, QFrame, QLabel, QSizePolicy, QRadioButton, QWidget,
                             QPushButton, QHBoxLayout)

from data_models import Track
from repositories import CachedTracksRepository


class DeleteTracksDialog(QDialog):
    def __init__(self, tracks: List[Track], *args):
        super().__init__(*args)

        self._tracks = tracks
        self.cached_tracks_repository = CachedTracksRepository()

        self.setWindowFlag(Qt.WindowType.CustomizeWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowTitleHint, True)
        self.setWindowFlag(Qt.WindowType.WindowSystemMenuHint, False)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setWindowTitle("Confirmation")
        self.setFixedSize(420, 180)

        self.dialog_layout = QVBoxLayout(self)
        self.dialog_layout.setContentsMargins(3, 3, 3, 3)

        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet(".QFrame {border: 1px solid black;}")
        self.main_frame_layout = QVBoxLayout(self.main_frame)

        self.text_label = QLabel(self)
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.text_label.setWordWrap(True)
        if len(tracks) == 1:
            self.text_label.setText(f"Delete '{tracks[0].display_name}'  [{tracks[0].format}]")
        else:
            self.text_label.setText(f"Delete the {len(tracks)} selected files")

        self.delete_from_library_button = QRadioButton('Delete from Library only', self.main_frame)
        self.delete_from_library_button.setChecked(True)
        self.delete_from_computer_button = QRadioButton('Delete from Library and Computer', self.main_frame)
        self.radio_buttons_frame = QFrame(self)
        self.radio_buttons_frame.setStyleSheet(".QFrame {border: 1px solid gray;}")
        self.radio_buttons_frame_layout = QVBoxLayout(self.radio_buttons_frame)

        self.radio_buttons_frame_layout.addWidget(self.delete_from_library_button)
        self.radio_buttons_frame_layout.addWidget(self.delete_from_computer_button)

        self.bottom_button_container = QWidget(self)
        self.bottom_button_layout = QHBoxLayout(self.bottom_button_container)
        self.bottom_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.yes_button = QPushButton('Yes', self)
        self.yes_button.setMaximumWidth(80)
        self.yes_button.setAutoDefault(False)
        self.yes_button.clicked.connect(self.delete_tracks)

        self.no_button = QPushButton('No', self)
        self.no_button.setMaximumWidth(80)
        self.no_button.setAutoDefault(False)
        self.no_button.clicked.connect(lambda: self.reject())

        self.bottom_button_layout.addWidget(self.yes_button)
        self.bottom_button_layout.addWidget(self.no_button)

        self.main_frame_layout.addWidget(self.text_label)
        self.main_frame_layout.addWidget(self.radio_buttons_frame)
        self.main_frame_layout.addWidget(self.bottom_button_container)

        self.dialog_layout.addWidget(self.main_frame)

    def delete_tracks(self) -> None:
        for track in self._tracks:
            if self.delete_from_library_button.isChecked():
                self.cached_tracks_repository.delete_track_by("file_path", track.file_path)

            elif self.delete_from_computer_button.isChecked():
                self.cached_tracks_repository.delete_track_by("file_path", track.file_path)
                if os.path.isfile(track.file_path):
                    os.remove(track.file_path)

        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    d = DeleteTracksDialog(CachedTracksRepository().get_tracks()[:10])
    d.show()
    sys.exit(app.exec())
