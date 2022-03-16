from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QFrame

from data_models.track import Track
from models.audio_controller import AudioController
from utils import ClickableLabel, format_seconds


class QueueInfoPanel(QFrame):
    # right_label_clicked = pyqtSignal()

    def __init__(self, audio_controller: AudioController, parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)

        self.audio_controller = audio_controller
        self.queue_length = 0
        self.current_queue = []

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.horizontal_layout.setContentsMargins(0, 0, 4, 0)
        # self.setStyleSheet("background-color: red")

        self.left_label = ClickableLabel(self)
        self.left_label.clicked.connect(self.left_label_clicked)
        self.left_label.setFixedWidth(220)
        self.left_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.is_left_label_in_detail_mode = True

        self.right_label = ClickableLabel(self)
        self.right_label.clicked.connect(self.right_label_clicked)
        self.right_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.right_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.is_right_label_in_countdown_mode = False  # TODO deprecated for now

        self.horizontal_layout.addWidget(self.left_label)
        self.horizontal_layout.addWidget(self.right_label)

        self.setStyleSheet("QueueInfoPanel {border-top: 1px solid rgba(0, 0, 0, 0.2);}")

    def left_label_clicked(self):
        if not self.left_label.text():
            return

        self.is_left_label_in_detail_mode = not self.is_left_label_in_detail_mode
        if self.is_left_label_in_detail_mode:
            length_text = format_seconds(self.queue_length)
        else:
            length_text = self.get_length_text(self.queue_length)
        self.left_label.setText(self.left_label.text().rsplit(",", 1)[0] + f", {length_text}" + "/")

    def right_label_clicked(self):
        if not self.right_label.text():
            return
        if not self.is_right_label_in_countdown_mode:
            self.right_label.setText(f"queued: {format_seconds(self.queue_length)}")
        else:
            self.right_label.setText(f"queued: -{format_seconds(self.audio_controller.get_remaining_time_in_secs())}")
        # self.is_right_label_in_countdown_mode = not self.is_right_label_in_countdown_mode

    def update_remaining_queue_time(self, time_in_secs: int) -> None:
        if self.is_right_label_in_countdown_mode:
            self.right_label.setText(f"queued: -{format_seconds(time_in_secs)}")
        else:
            self.right_label.setText(f"queued: {format_seconds(self.queue_length)}")

    def update_info(self, tracks: List[Track]) -> None:
        def get_size_text(size_in_bytes: int) -> str:
            size = size_in_bytes
            units = ("B", "KB", "MB", "GB", "TB")
            unit_index = 0
            while size > 1024:
                size /= 1024
                unit_index += 1

            return f"{size:.1f} {units[unit_index]}"

        if self.current_queue == tracks:
            return

        self.current_queue = tracks.copy()

        self.queue_length = sum(track.length for track in tracks)

        file_text = f"{len(tracks)} {'file' if len(tracks) == 1 else 'files'}"
        size_text = get_size_text(sum(track.size for track in tracks))
        length_text = format_seconds(self.queue_length) if self.is_left_label_in_detail_mode \
            else self.get_length_text(self.queue_length)

        self.left_label.setText(", ".join((file_text, size_text, length_text)) + "/")

        if not self.is_right_label_in_countdown_mode:
            self.right_label.setText(f"queued: {format_seconds(self.queue_length)}")

    @staticmethod
    def get_length_text(length: int) -> str:
        if length < 60:
            return f"{length} secs"
        if length < 3600:
            return f"{length / 60:.1f} mins"
        return f"{length / 3600:.1f} hours"
