from typing import Union, List

from data_models.track import Track
from repositories.singleton import Singleton
from repositories.tracks_repository import TracksRepository


class CachedTracksRepository(TracksRepository, metaclass=Singleton):
    def __init__(self):
        super().__init__()

        self.cached_groups = {}

    def get_tracks_by(self, key: str, value: Union[str, int]) -> List[Track]:
        tuple_key = (key, value)

        if tuple_key in self.cached_groups:
            # print(self.cached_groups)
            return self.cached_groups[tuple_key]
        else:
            tracks = super().get_tracks_by(key, value)
            self.cached_groups[tuple_key] = tracks
            # print(tuple_key)
            return tracks
