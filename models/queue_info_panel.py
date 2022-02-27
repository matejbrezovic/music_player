from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from data_models.track import Track
from utils import ClickableLabel


class QueueInfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(20)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: red")

        self.left_label = ClickableLabel()
        self.left_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.left_label_in_seconds = True

        self.horizontal_layout.addWidget(self.left_label)

    def left_label_clicked(self):
        if self.left_label_in_seconds:
            ...

    def update_info(self, tracks: List[Track]) -> None:
        def get_size_text(size_in_bytes: int) -> str:
            size = size_in_bytes
            units = ("B", "KB", "MB", "GB", "TB")
            unit_index = 0
            while size > 1024:
                size /= 1024
                unit_index += 1

            return f"{size:.1f} {units[unit_index]}"

        def get_length_text(length: int) -> str:
            if length < 60:
                return f"{length} secs"
            if length < 60**2:
                return f"{length/60:.1f} mins"
            return f"{length/3600:.1f} hours"

        file_text = f"{len(tracks)} {'file' if len(tracks) == 1 else 'files'}"
        size_text = get_size_text(sum(track.size for track in tracks))
        length_text = get_length_text(sum(track.length for track in tracks))

        self.left_label.setText(", ".join((file_text, size_text, length_text)) + "/")
