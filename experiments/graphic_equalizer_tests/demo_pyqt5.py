import random
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from equalizer_bar import SpectrumEqualizer


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        steps = ['#0C0786', '#40039C', '#6A00A7', '#8F0DA3', '#B02A8F', '#CA4678', '#E06461',
                 '#F1824C', '#FCA635', '#FCCC25', '#EFF821']

        self.equalizer = SpectrumEqualizer(5, 10)

        self.equalizer.setFixedSize(40, 30)

        self.central_widget = QWidget()
        self.central_widget_layout = QHBoxLayout(self.central_widget)
        self.central_widget_layout.addWidget(self.equalizer)

        self.setCentralWidget(self.central_widget)

        self._timer = QTimer()
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.update_values)
        self._timer.start()

    def update_values(self):
        self.equalizer.setValues([
            min(100, v+random.randint(0, 50) if random.randint(0, 5) > 2 else v)
            for v in self.equalizer.values()
        ])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()





