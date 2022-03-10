from dataclasses import dataclass

from PyQt6.QtGui import QPixmap


@dataclass
class NavigationGroup:
    title: str
    visual_title: str
    tracks_num: int
    pixmap: QPixmap = None
