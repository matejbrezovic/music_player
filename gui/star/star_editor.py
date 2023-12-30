from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QPainter, QMoveEvent, QPalette, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import QWidget

from gui.star import StarRating


class StarEditor(QWidget):
    rating_changed = pyqtSignal(float)

    def __init__(self, parent: QWidget, palette: QPalette):
        super().__init__(parent)
        self._star_rating = StarRating()
        self.selected_star_count = self._star_rating.star_count()
        self.setMouseTracking(True)
        self.setPalette(palette)

        self.color = None

    def __repr__(self):
        return f"Editor {self._star_rating.star_count()}"

    def set_star_rating(self, star_rating: StarRating) -> None:
        self._star_rating = star_rating
        if self.color:
            self._star_rating.set_color(self.color)

    def set_selected_star_count(self, star_count: float) -> None:
        if star_count == self.selected_star_count:
            return

        self.selected_star_count = star_count
        self._star_rating.set_star_count(self.selected_star_count)
        self.rating_changed.emit(self.selected_star_count)

    def star_rating(self) -> StarRating:
        return self._star_rating

    def sizeHint(self) -> int:
        return self._star_rating.size_hint()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)

        self._star_rating.paint(painter, self.rect(), self.palette(), StarRating.Editable)

    def mouseMoveEvent(self, event: QMoveEvent) -> None:
        star = self.star_at_position(event.pos().x())

        if star != self._star_rating.star_count() and star != -1:
            self._star_rating.set_star_count(star)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.set_selected_star_count(self._star_rating.star_count())

    def leaveEvent(self, e: QEvent) -> None:
        self._star_rating.set_star_count(self.selected_star_count)
        self.repaint()
        super().leaveEvent(e)

    def star_at_position(self, x: int) -> int:
        if x <= 2:
            return 0

        # Enable a star, if pointer crosses the center horizontally.
        star_width = self._star_rating.size_hint().width() // self._star_rating.max_star_count()
        num_of_stars = (x + star_width / 2) / star_width // 0.5 / 2
        if 0 <= num_of_stars <= self._star_rating.max_star_count():
            return num_of_stars

        return -1

    def set_star_color(self, color) -> None:
        self.color = color
        self._star_rating.set_color(color)
