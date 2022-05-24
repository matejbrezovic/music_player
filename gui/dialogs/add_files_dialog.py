from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog

from constants import SUPPORTED_AUDIO_FORMATS
from repositories.cached_tracks_repository import CachedTracksRepository
from repositories.tracks_repository import TracksRepository


class AddFilesDialog(QFileDialog):
    added_tracks = pyqtSignal(list)

    def __init__(self, *args):
        super().__init__(*args)

        self.cached_tracks_repository = CachedTracksRepository()

    def exec(self) -> None:
        extension_string = ' '.join([f'*{extension}' for extension in SUPPORTED_AUDIO_FORMATS])
        file_paths, _ = self.getOpenFileNames(self, "Add Files to Library", "", f"Music Files ({extension_string})")
        tracks = TracksRepository.convert_file_paths_to_tracks(file_paths)
        CachedTracksRepository().add_new_tracks(tracks)
        self.cached_tracks_repository.delete_cache()
        self.cached_tracks_repository.cache_tracks()
        self.added_tracks.emit(tracks)
        self.done(0)
