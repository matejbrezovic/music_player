import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QSlider, QHBoxLayout,
                             QLabel, QApplication)


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        hbox = QHBoxLayout()

        sld = QSlider(Qt.Horizontal, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.valueChanged.connect(self.changeValue)

        self.label = QLabel(self)
        self.label.setPixmap(QPixmap('mute.png'))

        hbox.addWidget(sld)
        hbox.addSpacing(15)
        hbox.addWidget(self.label)

        self.setLayout(hbox)

        self.move(300, 300)
        self.setWindowTitle('Volume control')
        self.show()

    def changeValue(self, value):

        if value == 0:
            self.setStyleSheet("background-color: red")
        elif 0 < value <= 30:
            self.setStyleSheet("background-color: blue")
        elif 30 < value < 80:
            self.setStyleSheet("background-color: yellow")
        else:
            self.setStyleSheet("background-color: green")


def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()