from dataclasses import dataclass
from typing import Optional

from PyQt6.QtGui import QPixmap


@dataclass
class TrackGroup:
    title: str
    visual_title: str
    tracks_num: int
    pixmap: Optional[QPixmap] = None
