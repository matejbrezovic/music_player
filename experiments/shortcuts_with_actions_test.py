import sys

from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QApplication


def test_func():
    print("Hello action!")

class Test(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(200, 200)


        my_action = QAction("test", self)
        my_action.triggered.connect(test_func)
        my_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        self.shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        self.shortcut.activated.connect(test_func)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Test()
    main_window.show()
    sys.exit(app.exec())