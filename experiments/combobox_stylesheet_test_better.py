import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QStyleFactory
from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QApplication


class TestComboBox(QComboBox):
    default_stylesheet = ''' 
        TestComboBox {
            color: black;
            background-color: rgba(255, 255, 255, 0);
            selection-background-color: rgba(255, 255, 255, 0);
            selection-color: black;
            border: none;
        }

        TestComboBox QAbstractItemView {
            background-color: white;
            min-width: 150px;
        }
        '''

    non_hover_stylesheet = '''
        TestComboBox::drop-down {
            border: none;
            background-color: rgba(255, 255, 255, 0);
        }
        '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHoverState(False)

    def setHoverState(self, state):
        qss = self.default_stylesheet
        if not state:
            qss += self.non_hover_stylesheet
        self.setStyleSheet(qss)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setHoverState(True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setHoverState(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget(self)
        self.widget.setStyleSheet("background-color: red")
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
    app.setStyle(QStyleFactory.create("windowsvista"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())