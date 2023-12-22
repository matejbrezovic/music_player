import math

from PyQt6.QtCore import QPointF, QSize, Qt
from PyQt6.QtGui import QPainter, QPolygonF


class StarPolygon(QPolygonF):
    def __init__(self, size: float):
        super().__init__()

        for i in range(5):
            x = math.cos(0.8 * i * math.pi - math.pi / 2)
            y = math.sin(0.8 * i * math.pi - math.pi / 2)
            self << QPointF(size * x, size * y)


class HalfStarPolygon(QPolygonF):
    def __init__(self, size: float):
        super().__init__()

        half_star_polygon_size = size / 2
        star_angle_step = 2 * math.pi / 5
        star_angle_start = - math.pi / 2
        half_star_angle_start = star_angle_start - star_angle_step / 2

        for _ in range(3):
            x = math.cos(star_angle_start)
            y = math.sin(star_angle_start)
            self << QPointF(size * x, size * y)

            x = math.cos(half_star_angle_start)
            y = math.sin(half_star_angle_start)
            self << QPointF(half_star_polygon_size * x, half_star_polygon_size * y)

            star_angle_start -= star_angle_step
            half_star_angle_start -= star_angle_step


class StarRating:
    # enum EditMode
    Editable, ReadOnly = False, True

    def __init__(self, star_count: float = 0, max_star_count: float = 5):
        self._star_count = float(star_count)
        self._max_star_count = float(max_star_count)

        self.star_polygon_size = 8

        self.star_polygon = StarPolygon(self.star_polygon_size)
        self.half_star_polygon = HalfStarPolygon(self.star_polygon_size)

        self.color = None

    def star_count(self):
        return self._star_count

    def max_star_count(self):
        return self._max_star_count

    def set_star_count(self, star_count: float):
        self._star_count = star_count

    def set_max_star_count(self, max_star_count: float):
        self._max_star_count = max_star_count

    def size_hint(self):
        return self.star_polygon_size * QSize(int(self._max_star_count), 1) * 2

    def paint(self, painter, rect, palette, edit_mode, forced_color=None) -> None:
        painter.save()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)

        if forced_color:
            painter.setBrush(forced_color)
        elif self.color:
            painter.setBrush(self.color)
        elif edit_mode == StarRating.Editable:
            painter.setBrush(Qt.GlobalColor.red)
        else:
            painter.setBrush(palette.windowText())

        y_offset = rect.height() / 2
        painter.translate(rect.x() + self.star_polygon_size, rect.y() + y_offset)

        for i in range(int(self._star_count * 2)):
            if not i % 2 and i == int(self._star_count * 2) - 1:
                painter.drawPolygon(self.half_star_polygon, Qt.FillRule.WindingFill)
            elif i % 2:
                painter.drawPolygon(self.star_polygon, Qt.FillRule.WindingFill)
                painter.translate(self.star_polygon_size * 2, 0.0)

        painter.restore()

    def set_color(self, color) -> None:
        self.color = color
