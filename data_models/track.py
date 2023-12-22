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
    playlist_id: int = field(repr=False, default=0)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        if not isinstance(other, Track):
            return False

        return self.file_path == other.file_path

    def __hash__(self):
        return hash((self.track_id, self.file_path, self.title, self.album,
                    self.artist, self.composer, self.size, self.playlist_id))

    @property
    def format(self) -> str:
        return os.path.splitext(self.file_path)[-1]

    @property
    def display_name(self) -> str:
        if self.artist and self.title:
            return f"{self.artist} - {self.title}"
        elif self.artist:
            return f"{self.artist} - Unknown Title"
        elif self.title:
            return self.title
        else:
            return os.path.splitext(self.file_path)[0].rsplit("/", 1)[-1]

    def is_valid(self) -> bool:
        return os.path.exists(self.file_path)

