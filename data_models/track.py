from dataclasses import dataclass
from typing import Optional

from PyQt6.QtGui import QPixmap


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
    artwork_path: str
    artwork_pixmap: QPixmap = None

