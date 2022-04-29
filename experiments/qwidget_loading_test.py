import random
import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.colors = ["black", "red", "blue", "green", "yellow", "magenta"]
        self.loaded_labels = {}
        self.button = QPushButton()
        self.button.clicked.connect(self.load_label)
        self.label = QLabel()
        self.label.setStyleSheet("background-color: black")
        self.loaded_labels["black"] = self.label

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.label)

        self.setWindowTitle('TEST')
        self.setGeometry(200, 200, 200, 200)
        self.setCentralWidget(self.main_widget)

    def load_label(self):
        key = random.choice(self.colors)
        print(key, self.loaded_labels)
        if key not in self.loaded_labels:
            new_label = QLabel()
            new_label.setFixedHeight(20)
            new_label.setStyleSheet(f"background-color: {key}")
            self.label = new_label
            self.loaded_labels[key] = new_label
            print("Created label")
        else:
            self.label = self.loaded_labels[key]
            print("Loaded label")
        # print(self.label.styleSheet())
        self.main_layout.addWidget(self.label)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowUi()
    mainWindow.show()
    sys.exit(app.exec())