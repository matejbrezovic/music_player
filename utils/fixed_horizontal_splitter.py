from typing import Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QResizeEvent, QPainter, QColor
from PyQt6.QtWidgets import QSplitter, QProxyStyle, QStyle, QStyleOption, QWidget


class FixedHorizontalSplitter(QSplitter):
    sizes_changed = pyqtSignal(list)

    def __init__(self, *args):
        super().__init__(*args)
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setStyle(FixedHorizontalSplitterProxyStyle())
        self.last_sizes = self.sizes()
        self.splitterMoved.connect(self.splitter_moved)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        try:
            if self.sizes()[0] > self.last_sizes[0] or self.sizes()[2] > self.last_sizes[2]:
                first = self.last_sizes[0]
                third = self.last_sizes[2]
                second = self.width() - first - third
                self.setSizes([first, second, third])
        except IndexError:
            self.last_sizes = self.sizes()
        self.last_sizes = self.sizes()

        self.sizes_changed.emit(self.sizes())

    def splitter_moved(self) -> None:
        self.last_sizes = self.sizes()
        self.sizes_changed.emit(self.sizes())


class FixedHorizontalSplitterProxyStyle(QProxyStyle):
    def __init__(self, *args):
        super().__init__(*args)

    def drawControl(self,
                    element: QStyle.ControlElement,
                    option: QStyleOption,
                    painter: QPainter,
                    widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.ControlElement.CE_RubberBand:
            painter.save()
            option.rect.setWidth(10)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("grey"))
            painter.drawRect(option.rect)
            painter.restore()
        else:
            return super().drawControl(element, option, painter, widget)
