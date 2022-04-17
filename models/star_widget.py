import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPaintEvent, QPainter, QPalette, QColor
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton, QFrame

from models.star_editor import StarEditor
from models.star_rating import StarRating


class StarWidget(QWidget):
    def __init__(self, star_count: float = 0, parent: QWidget = None):
        super().__init__(parent)
        self.background_stars = StarRating(5)
        self.setContentsMargins(0, 0, 0, 0)

        self.star_count = star_count

        self.editor = StarEditor(self, self.palette())
        self.editor.set_selected_star_count(star_count)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        self.background_stars.paint(painter, self.editor.rect(), self.palette(), StarRating.ReadOnly,
                                    QColor(255, 255, 255, 70))

    def sizeHint(self):
        return self.background_stars.size_hint()

    def setPalette(self, palette: QPalette) -> None:
        super().setPalette(palette)
        self.editor.setPalette(palette)


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet("QWidget#central_widget {background-color: green;}")
        self.central_widget_layout = QVBoxLayout()
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        sw = StarWidget()
        # sw.setFixedSize(40, 40)
        # test_widget = QFrame(self)
        # test_widget.setStyleSheet("background-color: yellow;")
        # test_widget.setFixedSize(40, 40)

        self.central_widget_layout.addWidget(sw)
        self.central_widget_layout.addWidget(QPushButton("TEST"))

        self.central_widget.setLayout(self.central_widget_layout)

        self.setCentralWidget(self.central_widget)

        self.resize(500, 500)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())