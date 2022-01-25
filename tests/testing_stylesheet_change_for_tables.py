import sys

from PyQt6.QtWidgets import *


class TestWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = TestWindow()
    sys.exit(app.exec())
