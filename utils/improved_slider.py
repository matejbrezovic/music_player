from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QSlider, QStyleOptionSlider, QStyle


class ImprovedSlider(QSlider):
    value_changed = pyqtSignal(int)

    def __init__(self, *args):
        super().__init__(*args)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.pixel_pos_to_range_value(event.pos())
            self.setValue(val)
            self.value_changed.emit(val)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        val = self.pixel_pos_to_range_value(event.pos())
        self.setValue(val)
        self.value_changed.emit(val)

    def pixel_pos_to_range_value(self, pos: QPoint) -> int:
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt,
                                         QStyle.SubControl.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt,
                                         QStyle.SubControl.SC_SliderHandle, self)

        slider_length = sr.width()
        slider_min = gr.x()
        slider_max = gr.right() - slider_length + 2

        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Orientation.Horizontal else pr.y()
        val = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - slider_min,
                                             slider_max - slider_min, opt.upsideDown)
        if val == 99:  # it wasn't able to be 100
            val = 100
        return val
