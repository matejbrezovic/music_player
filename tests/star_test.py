import math
import sys

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPolygonF, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)
        self.show()

    @staticmethod
    def get_star_polygon():
        star_polygon = QPolygonF()
        star_polygon_size = 10

        for i in range(5):
            default_x = math.cos(0.8 * i * math.pi - math.pi / 2)
            default_y = math.sin(0.8 * i * math.pi - math.pi / 2)
            star_polygon << QPointF(100 + star_polygon_size * default_x,
                                    100 + star_polygon_size * default_y)
        return star_polygon

    @staticmethod
    def get_quarter_polygon():
        offset_x = 100
        offset_y = 100
        star_polygon_size = 40

        star_polygon = QPolygonF()
        star_polygon << QPointF(offset_x, offset_y)
        for i in range(10):
            default_x = math.cos(math.radians(i))
            default_y = math.sin(math.radians(i))
            star_polygon << QPointF(offset_x + star_polygon_size * default_x,
                                    offset_y + star_polygon_size * default_y)
        return star_polygon

    @staticmethod
    def get_x_axis():
        offset_x = 100
        offset_y = 100

        star_polygon = QPolygonF()
        star_polygon << QPointF(0, offset_y) <<  QPointF(600, offset_y)

        return star_polygon

    @staticmethod
    def get_y_axis():
        offset_x = 100
        offset_y = 100

        star_polygon = QPolygonF()
        star_polygon << QPointF(offset_x, 0) << QPointF(offset_x, 600)

        return star_polygon

    def get_half_star_polygon(self):
        star_polygon_size = 40
        half_star_polygon_size = 20
        star_angle_step = 2 * math.pi / 5
        star_angle_start = - math.pi / 2
        half_star_angle_start = star_angle_start - star_angle_step / 2

        offset_x = 100
        offset_y = 100

        self.star_polygon = QPolygonF()

        x = math.cos(star_angle_start)
        y = math.sin(star_angle_start)
        self.star_polygon << QPointF(offset_x + star_polygon_size * x, offset_y + star_polygon_size * y)

        x = math.cos(half_star_angle_start)
        y = math.sin(half_star_angle_start)
        self.star_polygon << QPointF(offset_x + half_star_polygon_size * x, offset_y + half_star_polygon_size * y)

        star_angle_start -= star_angle_step
        x = math.cos(star_angle_start)
        y = math.sin(star_angle_start)
        self.star_polygon << QPointF(offset_x + star_polygon_size * x, offset_y + star_polygon_size * y)

        half_star_angle_start -= star_angle_step
        x = math.cos(half_star_angle_start)
        y = math.sin(half_star_angle_start)
        self.star_polygon << QPointF(offset_x + half_star_polygon_size * x, offset_y + half_star_polygon_size * y)

        star_angle_start -= star_angle_step
        x = math.cos(star_angle_start)
        y = math.sin(star_angle_start)
        self.star_polygon << QPointF(offset_x + star_polygon_size * x, offset_y + star_polygon_size * y)

        half_star_angle_start -= star_angle_step
        x = math.cos(half_star_angle_start)
        y = math.sin(half_star_angle_start)
        self.star_polygon << QPointF(offset_x + half_star_polygon_size * x, offset_y + half_star_polygon_size * y)

        return self.star_polygon

    def draw_polygon(self, polygon, line_color):
        painter = QPainter(self)
        painter.setPen(QPen(line_color, 1, Qt.PenStyle.SolidLine))
        painter.drawPolygon(polygon)

    def paintEvent(self, event):
        self.draw_polygon(self.get_x_axis(), Qt.GlobalColor.red)
        self.draw_polygon(self.get_y_axis(), Qt.GlobalColor.red)
        self.draw_polygon(self.get_star_polygon(), Qt.GlobalColor.black)


        # painter = QPainter(self)
        # painter.setPen(QPen(Qt.GlobalColor.black, 5, Qt.PenStyle.SolidLine))
        # painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        # painter.setBrush(QBrush(Qt.GlobalColor.black, Qt.BrushStyle.SolidPattern))

        # polygon = self.get_half_star_polygon()
        # # polygon = self.get_quarter_polygon()
        #
        # painter.drawPolygon(polygon)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())