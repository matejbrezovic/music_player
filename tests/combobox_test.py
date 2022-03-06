import sys

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QEnterEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QWidget


class TestComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_stylesheet = ''' 
        QComboBox {
            background-color: rgba(0, 0, 0, 0);
        }
        QComboBox QAbstractItemView {
            background-color: white;
            min-width: 150px;
        }'''

        self.hide_down_arrow_stylesheet = '''QComboBox::down-arrow { \
                                             background-color: rgba(0, 0, 0, 0);}'''

        self.setStyleSheet(self.default_stylesheet + self.hide_down_arrow_stylesheet)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.setStyleSheet(self.default_stylesheet)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.setStyleSheet(self.default_stylesheet + self.hide_down_arrow_stylesheet)
        super().leaveEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.combobox = TestComboBox(self.widget)
        self.combobox.resize(180, 30)
        self.combobox.insertItem(0, "item 1")
        self.combobox.insertItem(0, "item 2")

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
    window = MainWindow()
    sys.exit(app.exec())