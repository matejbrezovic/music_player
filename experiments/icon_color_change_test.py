import sys

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import *

from constants import *
from utils import get_icon_with_updated_states


class IconChangeMainWindowUi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self.central_widget = QWidget()
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.central_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.button = QPushButton(self.central_widget)
        self.button.setFixedSize(100, 100)


        self.test_pixmap = QPixmap(ROOT + "/icons/album.png").scaled(100,
                                                                     100,
                                                                     Qt.AspectRatioMode.KeepAspectRatio,
                                                                     Qt.TransformationMode.SmoothTransformation)


        icon = QIcon(self.test_pixmap)

        icon = get_icon_with_updated_states(icon)

        self.button.setIcon(icon)
        self.button.setIconSize(QSize(self.width(), self.height()))

        self.central_widget_layout.addWidget(self.button)

        self.setCentralWidget(self.central_widget)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = IconChangeMainWindowUi()
    main_window.show()
    sys.exit(app.exec())
