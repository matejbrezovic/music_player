from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QIcon, QEnterEvent, QMouseEvent, QColor
from PyQt6.QtWidgets import QPushButton

import constants


class HoverButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)
        self.normal_icon = None
        self.hover_icon = None
        self.is_in_dark_mode = True

    def enterEvent(self, _: QEnterEvent) -> None:
        if self.isEnabled() and self.hover_icon:
            super().setIcon(self.hover_icon)

    def leaveEvent(self, _: QEvent) -> None:
        if self.isEnabled() and self.normal_icon:
            super().setIcon(self.normal_icon)

    def mousePressEvent(self, _: QMouseEvent) -> None:
        self.clicked.emit()
        if self.isEnabled() and self.hover_icon:
            super().setIcon(self.hover_icon)

    def setIcon(self, icon: QIcon) -> None:
        # print("set icon")
        self.normal_icon = icon
        self.hover_icon = get_hover_icon(icon, self.is_in_dark_mode)
        super().setIcon(icon)

    def set_is_in_dark_mode(self, is_in_dark_mode: bool) -> None:
        self.is_in_dark_mode = is_in_dark_mode
        if self.normal_icon:
            self.hover_icon = get_hover_icon(self.normal_icon, is_in_dark_mode)


def change_icon_color(icon: QIcon, color: QColor) -> QIcon:
    pixmap = icon.pixmap(60, 60, QIcon.Mode.Normal)
    mask = pixmap.createMaskFromColor(QColor('transparent'), Qt.MaskMode.MaskInColor)
    pixmap.fill(color)
    pixmap.setMask(mask)
    icon = QIcon(pixmap)
    return icon


def get_hover_icon(icon: QIcon, is_in_dark_mode: bool) -> QIcon:
    pixmap = icon.pixmap(60, 60, QIcon.Mode.Normal)
    mask = pixmap.createMaskFromColor(QColor('transparent'), Qt.MaskMode.MaskInColor)

    color = constants.DARK_AUDIO_CONTROLLER_HOVER_COLOR if is_in_dark_mode \
        else constants.LIGHT_AUDIO_CONTROLLER_HOVER_COLOR

    pixmap.fill(color)
    pixmap.setMask(mask)
    icon = QIcon(pixmap)
    return icon
