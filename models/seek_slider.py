from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QRectF, QEvent
from PyQt6.QtGui import QPainter, QMouseEvent
from PyQt6.QtWidgets import QProxyStyle, QToolTip, QStyleOptionComplex

from audio_player_test import ImprovedSlider
from utils import format_player_position_to_seconds, format_seconds

if TYPE_CHECKING:
    pass


class Style(QProxyStyle):
    def drawComplexControl(self, control, opt: QStyleOptionComplex, qp: QPainter, widget=None):
        print("DRAWN", control)

        if control == self.ComplexControl.CC_Slider:
            # get the default rectangle of the groove
            groove = self.subControlRect(control, opt, self.SubControl.SC_SliderGroove, widget)
            print(groove, opt.orientation)
            # create a small one
            if opt.orientation == Qt.Orientation.Horizontal:
                rect = QRectF(
                    groove.x(), groove.center().y() - .5,
                    groove.width(), 2)
            else:
                rect = QRectF(
                    groove.center().x() - .5, groove.y(),
                    2, groove.height())
            qp.save()
            qp.setBrush(opt.palette.base())
            qp.setPen(opt.palette.dark().color())
            qp.setRenderHints(qp.RenderHint.Antialiasing)
            qp.drawRoundedRect(rect, 1, 1)
            qp.restore()

            # remove the groove flag from the subcontrol list

            print(opt.subControls)
            opt.subControls &= ~self.SubControl.SC_SliderGroove

        super().drawComplexControl(control, opt, qp, widget)


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

    def __init__(self, audio_controller, *args):
        super().__init__(*args)
        self.audio_controller = audio_controller  # TODO remove self.audio_controller
        self.backup_volume = self.audio_controller.player.audio_output.volume()
        self.backup_action = -1
        self.setFixedHeight(14)
        self.setStyleSheet(self.dark_stylesheet)
        self.length_in_seconds = format_player_position_to_seconds(self.audio_controller.player.duration())
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
        super().mousePressEvent(event)
        self.backup_action = self.audio_controller.user_action
        self.audio_controller.player.setPosition(self.pixel_pos_to_range_value(event.pos()))
        self.audio_controller.pause(fade=False)
        self.audio_controller.player.current_volume = self.audio_controller.volume_slider.value() / 100

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        super().mouseMoveEvent(event)

    def event(self, event: QEvent):  # TODO fix fast refreshing when hovering near widget edge
        if event.type() == QEvent.Type.HoverMove:
            if not self.length_in_seconds or not self.isEnabled():
                return True
            # print(self.height(), self.y(), event.oldPos().y())

            seconds = int((event.oldPos().x() / self.width()) * self.length_in_seconds)
            seconds = max(0, min(seconds, self.length_in_seconds))
            formatted_seconds = format_seconds(seconds)
            tool_tip_str = f"{formatted_seconds}/{self.formatted_length_in_seconds}"
            QToolTip.showText(self.mapToGlobal(event.oldPos()), tool_tip_str, self)
            # self.__can_update_tooltip = False

            # self._tooltip_timer.start(30)
            return True
        return super().event(event)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        if not self.length_in_seconds:
            return
        # handles unmuting audio and updating player

        self.audio_controller.set_player_position(self.sliderPosition())

        if self.backup_action == 1:
            # self.audio_controller.player.audio_output.current_volume = self.backup_volume
            self.audio_controller.unpause(fade=False)

    def set_dark_mode_enabled(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            self.setStyleSheet(self.dark_stylesheet)
        else:
            self.setStyleSheet(self.light_stylesheet)

    # def hide_handle(self) -> None:
    #     self.setStyleSheet(self.styleSheet() + "\nQSlider::handle:horizontal {background: transparent;}")
    #
    # def show_handle(self) -> None:
    #     self.

    def set_length_in_seconds(self, length_in_seconds: int) -> None:
        self.length_in_seconds = length_in_seconds
        self.formatted_length_in_seconds = format_seconds(length_in_seconds)
