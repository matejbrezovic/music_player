import os
from dataclasses import dataclass
from typing import Any


@dataclass
class Track:
    track_id: int
    file_path: str
    title: str
    album: str
    artist: str
    composer: str
    genre: str
    year: int
    length: int
    # artwork_path: str
    artwork_pixmap: Any = None

    def __post_init__(self):
        self.size = os.path.getsize(self.file_path)

    # @property
    # def size(self):
    #     return os.path.getsize(self.file_path)

