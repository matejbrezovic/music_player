import sys

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QMainWindow, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(200, 200)


        my_color = QColor(100, 100, 0, 100)

        string = repr(my_color.rgba())
        print(type(my_color.rgba()))

        self.setStyleSheet(f"background-color: {string};")
        print(self.styleSheet())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())