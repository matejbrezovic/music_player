import os
from dataclasses import dataclass, field
from typing import Any


@dataclass(eq=False)
class Track:
    track_id: int
    file_path: str = field(repr=False)
    title: str
    album: str
    artist: str
    composer: str = field(repr=False)
    genre: str = field(repr=False)
    year: int = field(repr=False)
    length: int = field(repr=False)
    size: int = field(repr=False)
    rating: int = field(repr=False, default=0)
    # artwork_path: str = field(repr=False)

    artwork_pixmap: Any = field(repr=False, default=None)
    # size: int = field(repr=False, default=0)

    # def __post_init__(self):
    #     self.size = os.path.getsize(self.file_path)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        if not isinstance(other, Track):
            return False

        return self.file_path == other.file_path

    # @property
    # def size(self):
    #     return os.path.getsize(self.file_path)

    @property
    def format(self):
        return os.path.splitext(self.file_path)[-1]

