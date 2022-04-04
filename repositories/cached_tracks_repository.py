from typing import Union, List, Tuple

from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import Singleton


class CachedTracksRepository(TracksRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

        self.cached_track_groups = {}
        self.cached_counts = {}

    def get_tracks_by(self, key: str, value: Union[str, int]) -> List[Track]:
        tuple_key = (key.lower(), value)
        if tuple_key not in self.cached_track_groups:
            self.cached_track_groups[tuple_key] = super().get_tracks_by(key, value)

        return self.cached_track_groups[tuple_key]

    def get_track_counts_grouped_by(self, group_key: str) -> List[Tuple[str, int]]:
        if group_key not in self.cached_counts:
            self.cached_counts[group_key] = super().get_track_counts_grouped_by(group_key)

        return self.cached_counts[group_key]

    def cache_tracks(self):
        for group_key in GROUP_OPTIONS:
            for group_name, _ in self.get_track_counts_grouped_by(group_key):
                self.get_tracks_by(group_key, group_name)
            self.get_tracks_by(group_key, None)

    def delete_cache(self):
        self.cached_track_groups = {}
        self.cached_counts = {}


if __name__ == "__main__":
    ...
