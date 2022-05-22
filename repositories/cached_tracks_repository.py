from typing import Union, List, Tuple, Optional

from constants import GROUP_OPTIONS
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import Singleton


class CachedTracksRepository(TracksRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

        self.cached_track_groups = {}
        self.cached_counts = {}

    def get_tracks_by(self, key: str, value: Optional[Union[str, int]]) -> List[Track]:
        tuple_key = (key.lower(), value)
        if tuple_key not in self.cached_track_groups:
            self.cached_track_groups[tuple_key] = super().get_tracks_by(key, value)

        return self.cached_track_groups[tuple_key]

    def get_track_counts_grouped_by(self, group_key: str) -> List[Tuple[str, int]]:
        group_key = group_key.lower()
        if group_key not in self.cached_counts:
            self.cached_counts[group_key] = super().get_track_counts_grouped_by(group_key)
        return self.cached_counts[group_key]

    def drop_track_by(self, key: str, value: Union[int, float, str]) -> None:
        super().drop_track_by(key, value)

    def drop_tracks(self, tracks: List[Track]) -> None:
        for track in tracks:
            self.drop_track_by("file_path", track.file_path)

        new = {}
        for key, value in self.cached_track_groups.items():
            for track in tracks:
                if track in value:
                    value.remove(track)
            if value:
                new[key] = value
        self.cached_track_groups = new

        self.cached_counts = {}
        for group_key in GROUP_OPTIONS:
            self.get_track_counts_grouped_by(group_key)

    def cache_tracks(self):
        for group_key in GROUP_OPTIONS:
            for group_name, _ in self.get_track_counts_grouped_by(group_key):
                self.get_tracks_by(group_key, group_name)
            self.get_tracks_by(group_key, None)

    def delete_cache(self):
        self.cached_track_groups = {}
        self.cached_counts = {}
