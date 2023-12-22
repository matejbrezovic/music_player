import sys

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolTip

from audio_player_test import ImprovedSlider
from utils import format_seconds


class TestSlider(ImprovedSlider):  # TODO add transparent background
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFixedHeight(10)
        # self.setMouseTracking(True)
        self.length_in_seconds = 200
        self.formatted_length_in_seconds = format_seconds(self.length_in_seconds)

    def event(self, event):
        if event.type() == QEvent.Type.HoverMove:
            # event = typing.cast(event, QHoverEvent)
            # print(event)
            seconds = int((event.oldPos().x() / self.width()) * self.length_in_seconds)
            formatted_seconds = format_seconds(seconds)
            tool_tip_str = f"{formatted_seconds}/{self.formatted_length_in_seconds}"
            QToolTip.showText(self.mapToGlobal(event.globalPosition().toPoint()), tool_tip_str, self)

            return True
        return super().event(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)
        # print("press")

    # def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
    #     seconds = int((event.pos().x() / self.width()) * self.length_in_seconds)
    #     formatted_seconds = format_seconds(seconds)
    #     tool_tip_str = f"{formatted_seconds}/{self.formatted_length_in_seconds}"
    #
    #     QToolTip.showText(event.globalPosition().toPoint(), tool_tip_str, self)
    #
    #     # if self.mouse
    #     # super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        ...
        # print("release")
        # handles unmuting audio and updating player

    def set_length_in_seconds(self, length_in_seconds: int) -> None:
        self.length_in_seconds = length_in_seconds
        self.formatted_length_in_seconds = format_seconds(length_in_seconds)



class TestSliderWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet("QWidget#central_widget {background-color: black;}")
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.central_widget_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = TestSlider(Qt.Orientation.Horizontal)
        # self.slider.setFixedWidth(600)
        self.central_widget_layout.addWidget(self.slider)

        self.setCentralWidget(self.central_widget)






if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestSliderWindow()
    window.show()
    sys.exit(app.exec())