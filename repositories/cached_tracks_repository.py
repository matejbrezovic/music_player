import time
from typing import Union, List, Tuple

from data_models.track import Track
from repositories.singleton import Singleton
from repositories.tracks_repository import TracksRepository


class CachedTracksRepository(TracksRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

        self.cached_track_groups = {}
        self.cached_counts = {}

    def get_tracks_by(self, key: str, value: Union[str, int]) -> List[Track]:
        tuple_key = (key, value)
        # print(tuple_key)
        if tuple_key not in self.cached_track_groups:
            start = time.time()
            self.cached_track_groups[tuple_key] = super().get_tracks_by(key, value)
            print("Tracks loaded in: ", time.time() - start)

        return self.cached_track_groups[tuple_key]

    def get_track_counts_grouped_by(self, group_key: str) -> List[Tuple[str, int]]:
        if group_key not in self.cached_counts:
            # print("Cached!")
            self.cached_counts[group_key] = super().get_track_counts_grouped_by(group_key)

        return self.cached_counts[group_key]

