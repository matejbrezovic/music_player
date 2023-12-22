import random
import string
import sys

from PyQt6.QtWidgets import *

from utils import MarqueeLabel


class MarqueeWindowTest(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.central_widget_layout = QVBoxLayout(self.central_widget)


        self.marquee_widget = MarqueeLabel(self.central_widget)
        self.marquee_widget.setText("   ---   ")
        self.marquee_widget.setFixedHeight(20)
        self.marquee_widget.setStyleSheet("background-color: red;")

        self.button = QPushButton("Change Text")
        self.button.clicked.connect(self.set_random_text)

        self.central_widget_layout.addWidget(self.marquee_widget)
        self.central_widget_layout.addWidget(self.button)

        self.setCentralWidget(self.central_widget)

    def set_random_text(self):
        text = ''.join(random.choice(string.ascii_letters) for i in range(random.randint(10, 40)))
        self.marquee_widget.setText(text)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MarqueeWindowTest()
    mw.show()
    sys.exit(app.exec())