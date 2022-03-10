import sys

from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFrame, QScrollArea, QLabel, QSpacerItem, \
    QSizePolicy


class SpecificImageLabel(QLabel):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap
        self.setStyleSheet("background-color: green;")
        size_policy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)  # Very important!
        # size_policy.setHeightForWidth(True)
        size_policy.setWidthForHeight(True)
        self.setSizePolicy(size_policy)

        if self.pixmap.width() != 0:
            self.pixmap = self.pixmap.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation)

        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        if self.pixmap is None:
            return
        if self.pixmap.width() != 0 and self.width() != 0:
            displayed_pixmap = self.pixmap.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(displayed_pixmap)

    # def heightForWidth(self, width: int) -> int:
    #     return width

    def setPixmap(self, new_pixmap: QPixmap) -> None:
        super().setPixmap(new_pixmap.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation))


class TestWindowUi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout(self.central_widget)

        self.track_info_widget = QFrame(self)
        self.track_info_widget_layout = QVBoxLayout(self.track_info_widget)
        self.track_info_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area = QScrollArea(self)
        self.track_info_scroll_area.setWidgetResizable(True)
        self.track_info_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.track_info_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.track_info_scroll_area_widget = QWidget(self)
        self.track_info_scroll_area_widget_layout = QVBoxLayout(self.track_info_scroll_area_widget)
        self.track_info_scroll_area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.track_info_scroll_area_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.track_info_scroll_area.setWidget(self.track_info_scroll_area_widget)

        self.currently_playing_track_image_label = SpecificImageLabel(QPixmap("C:/My Files/My Projects/music_player/icons/album.png"))
        self.currently_playing_track_image_label.setUpdatesEnabled(True)
        self.currently_playing_track_image_label.setAlignment(Qt.AlignmentFlag.AlignTop)


        self.track_info_scroll_area_widget_layout.addWidget(QLabel("Random Title"))
        self.track_info_scroll_area_widget_layout.addWidget(QLabel("Random Info"))
        self.track_info_scroll_area_widget_layout.addSpacerItem(QSpacerItem(20, 40))
        self.track_info_scroll_area_widget_layout.addWidget(self.currently_playing_track_image_label)

        self.track_info_widget_layout.addWidget(QLabel("Track Information"))
        self.track_info_widget_layout.addWidget(self.track_info_scroll_area)

        self.central_widget_layout.addWidget(self.track_info_widget)

        self.setCentralWidget(self.central_widget)

        # self.resize(500, 200)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = TestWindowUi()
    main_window.show()
    sys.exit(app.exec())