from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QPainter, QMoveEvent, QPalette, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import QWidget

from models.star_rating import StarRating


class StarEditor(QWidget):
    def __init__(self, parent: QWidget, palette: QPalette):
        super().__init__(parent)
        self._star_rating = StarRating()
        self.selected_star_count = self._star_rating.star_count()
        self.setMouseTracking(True)
        self.setPalette(palette)

    def __repr__(self):
        return f"Editor {self._star_rating.star_count()}"

    def set_star_rating(self, star_rating: StarRating):
        self._star_rating = star_rating

    def set_selected_star_count(self, star_count: float) -> None:
        self.selected_star_count = star_count
        self._star_rating.set_star_count(self.selected_star_count)

    def star_rating(self):
        return self._star_rating

    def sizeHint(self):
        return self._star_rating.size_hint()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)

        # painter.save()
        # painter.setBrush(Qt.GlobalColor.red)
        # painter.drawRect(event.rect())
        # painter.restore()

        self._star_rating.paint(painter, self.rect(), self.palette(), StarRating.Editable,
                                self.palette().highlightedText())

    def mouseMoveEvent(self, event: QMoveEvent):
        star = self.star_at_position(event.pos().x())

        if star != self._star_rating.star_count() and star != -1:
            self._star_rating.set_star_count(star)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.set_selected_star_count(self._star_rating.star_count())

    def leaveEvent(self, e: QEvent) -> None:
        self._star_rating.set_star_count(self.selected_star_count)
        self.repaint()
        super().leaveEvent(e)

    def star_at_position(self, x):
        if x <= 2:
            return 0

        # Enable a star, if pointer crosses the center horizontally.
        star_width = self._star_rating.size_hint().width() // self._star_rating.max_star_count()
        num_of_stars = (x + star_width / 2) / star_width // 0.5 / 2
        if 0 <= num_of_stars <= self._star_rating.max_star_count():
            return num_of_stars

        return -1
