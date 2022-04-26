import typing

from PyQt6.QtCore import Qt, QEvent, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QMoveEvent, QKeyEvent, QWheelEvent
from PyQt6.QtWidgets import QToolTip

from utils import format_seconds, ImprovedSlider


class SeekSlider(ImprovedSlider):
    light_stylesheet = f"""
        QSlider::groove:horizontal {{
            border: none;
            background: transparent;
            height: 3px;
        }}

        QSlider::handle:horizontal {{
            background: white;
            width: 10px;
        }}

        QSlider::add-page:horizontal {{
            background: rgba(255, 255, 255, .3);
        }}

        QSlider::sub-page:horizontal {{
            background: rgb(200, 200, 200);
        }}
        """

    dark_stylesheet = f"""
        QSlider::groove:horizontal {{
            border: none;
            background: white;
            height: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: black;
            width: 10px;
        }}

        QSlider::add-page:horizontal {{
            background: lightGray;
        }}

        QSlider::sub-page:horizontal {{
            background: darkGray;
        }}
        """

    slider_pressed = pyqtSignal(int)
    slider_released = pyqtSignal(int)
    slider_moved = pyqtSignal(int)

    def __init__(self, *args):
        super().__init__(*args)
        self.setFixedHeight(14)
        self.setStyleSheet(self.dark_stylesheet)
        self.length_in_seconds = 0
        self.formatted_length_in_seconds = format_seconds(self.length_in_seconds)

        #     self.__can_update_tooltip = True
        #     self._tooltip_timer = QTimer()
        #     self._tooltip_timer.setTimerType(Qt.TimerType.PreciseTimer)
        #     self._tooltip_timer.setSingleShot(True)
        #     self._tooltip_timer.timeout.connect(self._tooltip_timer_timeout)
        #
        # def _tooltip_timer_timeout(self):
        #     self.__can_update_tooltip = True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        self.slider_pressed.emit(event.pos().x() if self.orientation() == Qt.Orientation.Horizontal
                                 else event.pos().y())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        self.slider_moved.emit(event.pos().x() if self.orientation() == Qt.Orientation.Horizontal
                               else event.pos().y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        self.slider_released.emit(event.pos().x() if self.orientation() == Qt.Orientation.Horizontal
                                  else event.pos().y())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.parent().wheelEvent(event)

    def event(self, event: QEvent):  # TODO fix fast refreshing when hovering near widget edge
        if event.type() == QEvent.Type.HoverMove:
            if not self.length_in_seconds or not self.isEnabled():
                return True
            event = typing.cast(QMoveEvent, event)
            seconds = int((event.oldPos().x() / self.width()) * self.length_in_seconds)
            seconds = max(0, min(seconds, self.length_in_seconds))
            formatted_seconds = format_seconds(seconds)
            tool_tip_str = f"{formatted_seconds}/{self.formatted_length_in_seconds}"
            QToolTip.showText(self.mapToGlobal(QPoint(event.oldPos().x(), self.y() - self.height())),
                              tool_tip_str, self)
            # self.__can_update_tooltip = False

            # self._tooltip_timer.start(30)
            return True
        return super().event(event)

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            self.setStyleSheet(self.dark_stylesheet)
        else:
            self.setStyleSheet(self.light_stylesheet)

    def set_length_in_seconds(self, length_in_seconds: int) -> None:
        self.length_in_seconds = length_in_seconds
        self.formatted_length_in_seconds = format_seconds(length_in_seconds)

