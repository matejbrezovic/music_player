import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QDialog, QApplication, QFrame, QHBoxLayout, QWidget, QLabel, QPushButton, QVBoxLayout,
                             QSpacerItem, QSizePolicy, QStyle)

from data_models import Track


class TrackNotFoundDialog(QDialog):
    def __init__(self, track: Track, *args):
        super().__init__(*args)

        self.setWindowFlag(Qt.WindowType.CustomizeWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowTitleHint, True)
        self.setWindowFlag(Qt.WindowType.WindowSystemMenuHint, False)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setWindowTitle("Error")
        self.setFixedSize(450, 150)

        self.dialog_layout = QVBoxLayout(self)
        self.dialog_layout.setContentsMargins(3, 3, 3, 3)

        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet(".QFrame {border: 1px solid black;}")
        self.main_frame_layout = QVBoxLayout(self.main_frame)

        self.top_widget = QWidget(self.main_frame)
        self.top_widget_layout = QHBoxLayout(self.top_widget)
        self.top_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.warning_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        self.warning_pixmap = self.warning_icon.pixmap(QSize(40, 40))

        self.warning_icon_label = QLabel(self.main_frame)
        self.warning_icon_label.setFixedWidth(50)
        self.warning_icon_label.setPixmap(self.warning_pixmap)

        self.text_label = QLabel(f"The source file for track '{track.title}' could not be found")
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.text_label.setWordWrap(True)
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedWidth(100)
        self.ok_button.setAutoDefault(False)
        self.ok_button.clicked.connect(lambda: self.done(0))

        self.top_widget_layout.addWidget(self.warning_icon_label)
        self.top_widget_layout.addWidget(self.text_label)
        self.top_widget_layout.addSpacerItem(QSpacerItem(50, 10))
        self.top_widget_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_frame_layout.addWidget(self.top_widget)
        self.main_frame_layout.addWidget(self.ok_button)
        self.main_frame_layout.setAlignment(self.ok_button, Qt.AlignmentFlag.AlignCenter)

        self.dialog_layout.addWidget(self.main_frame)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    t = TrackNotFoundDialog(...)
    t.show()
    sys.exit(app.exec())
