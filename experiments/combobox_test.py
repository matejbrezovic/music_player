import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QWidget, QVBoxLayout


class TestComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_stylesheet = ''' 
        QComboBox {
            color: black;
            background-color: rgba(0, 0, 0, 0);
        }

        QComboBox QAbstractItemView {
            background-color: white;
            min-width: 150px;
        }

        QComboBox:!hover {
        color: rgba(0, 0, 0, 0);
        }
        '''

        self.setStyleSheet(self.default_stylesheet)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.layout = QVBoxLayout(self.widget)

        self.combobox = TestComboBox()
        self.combobox.resize(180, 30)
        self.combobox.addItems(["item 1", "item 2"])
        # self.combobox.insertItem(0, "item 2")
        # self.combobox.insertItem(0, "item 3")
        # self.combobox.insertItem(0, "item 4")
        # self.combobox.insertItem(0, "item 5")
        self.layout.addWidget(self.combobox)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())