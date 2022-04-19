from PyQt6.QtCore import QTimer, Qt, QSize, QPointF
from PyQt6.QtGui import QStaticText, QImage, QTransform, QPainter, qRgba, QLinearGradient, QColor
from PyQt6.QtWidgets import QLabel


class MarqueeLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*args)
        self.static_text = QStaticText()
        self.static_text.setTextFormat(Qt.TextFormat.PlainText)
        self._text = ''
        self.timer = QTimer()
        self.timer.setInterval(30)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.timer_timeout)
        self.wait_timer = QTimer()
        self.wait_timer.setInterval(10)
        self.wait_timer.timeout.connect(self.timer_timeout)
        self.left_margin = int(self.height() / 3)
        self.single_text_width = 0
        self.scroll_pos = 0
        self.buffer = QImage()
        self.alpha_channel = QImage()
        self.scroll_enabled = False
        self.waiting = True
        self.seperator = '     :::     '
        self.update_text()

        self.whole_text_size = QSize(0, 0)
        self.update_text_rect_flag = True

    def text(self):
        return self._text

    def setText(self, text: str):
        self._text = text
        self.update_text()
        self.update()
        self.updateGeometry()

    def sizeHint(self):
        return QSize(min(self.whole_text_size.width() + self.left_margin, self.maximumWidth()),
                     self.fontMetrics().height())

    def update_text(self):
        self.timer.stop()
        self.update_text_rect_flag = True

        self.single_text_width = self.fontMetrics().horizontalAdvance(self._text)
        self.scroll_enabled = self.single_text_width > self.width() - self.left_margin

        if self.scroll_enabled:
            self.static_text.setText(self._text + self.seperator)
            if not self.window().windowState() & Qt.WindowState.WindowMinimized:
                self.scroll_pos = 0
                self.wait_timer.start()
                self.waiting = True
        else:
            self.static_text.setText(self._text)

        self.static_text.prepare(QTransform(), self.font())

    def hideEvent(self, event):
        if self.scroll_enabled:
            self.scroll_pos = 0
            self.timer.stop()
            self.wait_timer.stop()

    def showEvent(self, event):
        if self.scroll_enabled:
            self.wait_timer.start()
            self.waiting = True

    def paintEvent(self, paint_event):
        painter = QPainter(self)
        if self.update_text_rect_flag:
            r = painter.boundingRect(0, 0, 0, 0, 0, self.static_text.text())
            self.whole_text_size = QSize(r.width(), r.height())
            self.update_text_rect_flag = False
        if self.scroll_enabled:
            self.buffer.fill(qRgba(0, 0, 0, 0))
            pb = QPainter(self.buffer)
            pb.setPen(painter.pen())
            pb.setFont(painter.font())
            x = min(-self.scroll_pos, 0) + self.left_margin
            while x < self.width():
                pb.drawStaticText(QPointF(x, (self.height() - self.whole_text_size.height()) / 2), self.static_text)
                x += self.whole_text_size.width()
            # apply Alpha channel
            pb.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            pb.setClipRect(self.width() - 15, 0, 15, self.height())
            pb.drawImage(0, 0, self.alpha_channel)
            pb.setClipRect(0, 0, 15, self.height())
            pb.drawImage(0, 0, self.alpha_channel)
            painter.drawImage(0, 0, self.buffer)
        else:
            x = self.left_margin + (self.width() - self.left_margin - self.contentsMargins().right() -
                                    self.fontMetrics().horizontalAdvance(self.text())) / 2
            painter.drawStaticText(QPointF(x, (self.height() - self.whole_text_size.height()) / 2),
                                   self.static_text)

    def resizeEvent(self, resize_event):
        # When the widget is resized, we need to update the alpha channel.
        self.alpha_channel = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.buffer = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.alpha_channel.fill(qRgba(0, 0, 0, 0))
        self.buffer.fill(qRgba(0, 0, 0, 0))
        if self.width() > 64:
            grad = QLinearGradient(QPointF(0, 0), QPointF(16, 0))
            grad.setColorAt(0, QColor(0, 0, 0, 0))
            grad.setColorAt(1, QColor(0, 0, 0, 255))
            painter = QPainter(self.alpha_channel)
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, 16, self.height())
            grad = QLinearGradient(QPointF(self.alpha_channel.width() - 16, 0),
                                   QPointF(self.alpha_channel.width(), 0))
            grad.setColorAt(0, QColor(0, 0, 0, 255))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(grad)
            painter.drawRect(self.alpha_channel.width() - 16, 0, self.alpha_channel.width(), self.height())
        else:
            self.alpha_channel.fill(QColor(0, 0, 0))

        new_scroll_enabled = (self.single_text_width > self.width() - self.left_margin)
        if not new_scroll_enabled == self.scroll_enabled:
            self.update_text()

    def timer_timeout(self):
        if self.whole_text_size.width():
            self.scroll_pos = (self.scroll_pos + 1) % \
                             self.whole_text_size.width()
        if self.waiting:
            self.waiting = False
            self.timer.start()
            self.wait_timer.stop()
        if self.scroll_pos == 0:
            self.waiting = True
            self.timer.stop()
            self.wait_timer.start()

        self.update()
