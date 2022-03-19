import sys

from PyQt6.QtCore import Qt, QTimer, QSize, QPointF
from PyQt6.QtGui import QPainter, QStaticText, QTransform, QImage, qRgba, QColor, QLinearGradient
from PyQt6.QtWidgets import *


class MarqueeLabel(QLabel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.staticText = QStaticText()
        self.staticText.setTextFormat(Qt.TextFormat.PlainText)
        self._string = ''
        self.timer = QTimer()
        self.timer.setInterval(16)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.timerTimeout)
        self.waitTimer = QTimer()
        self.waitTimer.setInterval(10)
        self.waitTimer.timeout.connect(self.timerTimeout)
        self.leftMargin = int(self.height() / 3)
        self.scrollPos = 0
        self.buffer = QImage()
        self.alphaChannel = QImage()
        self.scrollEnabled = False
        self.waiting = True
        self.seperator = '   :::   '
        self.update_text()

        self.wholeTextSize = QSize(0, 0)
        self.flag = True

    def text(self):
        return self._string

    def setText(self, string):
        self._string = string
        self.update_text()
        self.update()
        self.updateGeometry()

    def sizeHint(self):
        return QSize(min(self.wholeTextSize.width() + self.leftMargin, self.maximumWidth()),
                     self.fontMetrics().height())

    def update_text(self):
        self.timer.stop()

        self.singleTextWidth = self.fontMetrics().horizontalAdvance(self._string)
        self.scrollEnabled = self.singleTextWidth > self.width() - self.leftMargin

        if self.scrollEnabled:

            self.staticText.setText(self._string + self.seperator)
            if not self.window().windowState() & Qt.WindowState.WindowMinimized:
                self.scrollPos = 0
                self.waitTimer.start()
                self.waiting = True
        else:
            self.staticText.setText(self._string)

        self.staticText.prepare(QTransform(), self.font())
        # self.wholeTextSize = QSize(self.fontMetrics().width(self.staticText.text()),
        #                            self.fontMetrics().height())

    # self.setFixedWidth()

    def hideEvent(self, event):
        if self.scrollEnabled:
            self.scrollPos = 0
            self.timer.stop()
            self.waitTimer.stop()

    def showEvent(self, event):
        if self.scrollEnabled:
            self.waitTimer.start()
            self.waiting = True

    def paintEvent(self, paint_event):
        painter = QPainter(self)
        if self.flag:
            self.r = painter.boundingRect(0, 0, 0, 0, 0, self.staticText.text())
            self.wholeTextSize = QSize(self.r.width(), self.r.height())
            self.flag = False
        if self.scrollEnabled:
            self.buffer.fill(qRgba(0, 0, 0, 0))
            pb = QPainter(self.buffer)
            pb.setPen(painter.pen())
            pb.setFont(painter.font())
            x = min(-self.scrollPos, 0) + self.leftMargin
            while x < self.width():
                pb.drawStaticText(QPointF(x, (self.height() - self.wholeTextSize.height()) / 2), self.staticText)
                x += self.wholeTextSize.width()
            # apply Alpha channel
            pb.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            pb.setClipRect(self.width() - 15, 0, 15, self.height())
            pb.drawImage(0, 0, self.alphaChannel)
            pb.setClipRect(0, 0, 15, self.height())
            pb.drawImage(0, 0, self.alphaChannel)
            painter.drawImage(0, 0, self.buffer)
        else:
            painter.drawStaticText(QPointF(self.leftMargin, (self.height() - self.wholeTextSize.height()) / 2),
                                   self.staticText)

    def resizeEvent(self, resizeEvent):
        # When the widget is resized, we need to update the alpha channel.
        self.alphaChannel = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.buffer = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.alphaChannel.fill(qRgba(0, 0, 0, 0))
        self.buffer.fill(qRgba(0, 0, 0, 0))
        if self.width() > 64:
            grad = QLinearGradient(QPointF(0, 0), QPointF(16, 0))
            grad.setColorAt(0, QColor(0, 0, 0, 0))
            grad.setColorAt(1, QColor(0, 0, 0, 255))
            painter = QPainter(self.alphaChannel)
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, 16, self.height())
            grad = QLinearGradient(QPointF(self.alphaChannel.width() - 16, 0),
                                   QPointF(self.alphaChannel.width(), 0))
            grad.setColorAt(0, QColor(0, 0, 0, 255))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(grad)
            painter.drawRect(self.alphaChannel.width() - 16, 0, self.alphaChannel.width(), self.height())
            # filename = 'alphaChannel'+str(randrange(0, 100000))+'.png'
            # print('writing '+filename)
            # self.alphaChannel.save(filename, 'PNG')
        else:
            self.alphaChannel.fill(QColor(0, 0, 0))

        newScrollEnabled = (self.singleTextWidth > self.width() - self.leftMargin)
        if not newScrollEnabled == self.scrollEnabled:
            self.update_text()

    def timerTimeout(self):
        if self.wholeTextSize.width():
            self.scrollPos = (self.scrollPos + 1) % \
                             self.wholeTextSize.width()
        if self.waiting == True:
            self.waiting = False
            self.timer.start()
            self.waitTimer.stop()
        if self.scrollPos == 0:
            self.waiting = True
            self.timer.stop()
            self.waitTimer.start()

        self.update()


class MarqueeWindowTest(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.central_widget_layout = QHBoxLayout(self.central_widget)


        self.marquee_widget = MarqueeLabel(self)
        self.marquee_widget.setText("Test 1 2 3 4 AAAAAAAAAAAAAAAAAAAAAAAAAAA")
        self.marquee_widget.setFixedHeight(20)
        self.marquee_widget.setStyleSheet("background-color: red;")

        self.central_widget_layout.addWidget(self.marquee_widget)

        self.setCentralWidget(self.central_widget)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MarqueeWindowTest()
    mw.show()
    sys.exit(app.exec())