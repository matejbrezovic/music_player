import time
from typing import Union, List, Tuple

from constants import *
from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import Singleton


cached_track_groups = {}
cached_counts = {}


class CachedTracksRepository(TracksRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

        # self.cached_track_groups = {}
        # self.cached_counts = {}

    def get_tracks_by(self, key: str, value: Union[str, int]) -> List[Track]:
        # print(len(cached_track_groups))
        tuple_key = (key.lower(), value)
        # print(tuple_key)
        if tuple_key not in cached_track_groups:
            # start = time.time()
            # print(tuple_key)
            print("cached tracks")
            cached_track_groups[tuple_key] = super().get_tracks_by(key, value)
            # print("Tracks loaded in: ", time.time() - start)

        return cached_track_groups[tuple_key]

    def get_track_counts_grouped_by(self, group_key: str) -> List[Tuple[str, int]]:
        if group_key not in cached_counts:
            # print("Cached!")
            cached_counts[group_key] = super().get_track_counts_grouped_by(group_key)

        return cached_counts[group_key]

    def cache_tracks(self):
        start = time.time()
        for group_key in GROUP_OPTIONS:
            for group_name, _ in self.get_track_counts_grouped_by(group_key):
                self.get_tracks_by(group_key, group_name)
            self.get_tracks_by(group_key, None)
        print(f"Tracks preloaded in: {time.time() - start:.6f} s")

    def delete_cache(self):
        cached_track_groups = {}
        cached_counts = {}
