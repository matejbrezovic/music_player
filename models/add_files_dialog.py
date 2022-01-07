from PyQt6.QtWidgets import QFileDialog
from constants import *
from repositories.tracks_repository import TracksRepository


class AddFilesDialog(QFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    def exec(self) -> None:
        file_paths, _ = self.getOpenFileNames(self, "Add Files to Library", "",
                                              f"Music Files ({' '.join([f'*.{extension}' for extension in SUPPORTED_AUDIO_FORMATS])})")
        tracks = TracksRepository.convert_file_paths_to_tracks(file_paths)
        TracksRepository().save_tracks(tracks)
        self.done(0)
