from typing import Union, List, Tuple, Optional, Dict

from constants import GROUP_OPTIONS
from data_models import Track
from repositories import TracksRepository
from utils import Singleton


class CachedTracksRepository(TracksRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

        self.cached_track_groups: Dict[Tuple[str, Optional[Union[str, int]]], List[Track]] = {}
        self.cached_counts: Dict[str, List[Tuple[str, int]]] = {}

    def get_tracks_by(self, key: str, value: Optional[Union[str, int]]) -> List[Track]:
        tuple_key = (key.lower(), value)
        if tuple_key not in self.cached_track_groups:
            self.cached_track_groups[tuple_key] = super().get_tracks_by(key, value)

        return self.cached_track_groups[tuple_key]

    def get_track_counts_grouped_by_key(self, group_key: str) -> List[Tuple[str, int]]:
        group_key = group_key.lower()
        if group_key not in self.cached_counts:
            self.cached_counts[group_key] = super().get_track_counts_grouped_by_key(group_key)
        return self.cached_counts[group_key]

    def update_track(self, track: Track, column: str, value: Union[int, float, str]) -> None:
        super().update_track(track, column, value)

        for group in self.cached_track_groups.values():
            if track in group:
                setattr(group[group.index(track)], column, value)

    # def delete_track_by(self, key: str, value: Union[int, float, str]) -> None:  # todo fix with cache
    #     super().delete_track_by(key, value)

    def delete_tracks(self, tracks: List[Track]) -> None:
        for track in tracks:
            self.delete_track_by("file_path", track.file_path)

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
            self.get_track_counts_grouped_by_key(group_key)

    def load_cache(self):
        for group_key in GROUP_OPTIONS:
            for group_name, _ in self.get_track_counts_grouped_by_key(group_key):
                self.get_tracks_by(group_key, group_name)
            self.get_tracks_by(group_key, None)
            self.get_tracks_by(group_key, 'all')

    def delete_cache(self):
        self.cached_track_groups = {}
        self.cached_counts = {}
