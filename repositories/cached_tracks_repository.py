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
        if tuple_key not in self.cached_groups:
            self.cached_groups[tuple_key] = super().get_tracks_by(key, value)

        return self.cached_groups[tuple_key]

