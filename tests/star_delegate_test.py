import math

from PyQt6.QtCore import pyqtSignal, QPointF, QSize, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainter, QPolygonF, QMoveEvent
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QStyle,
                             QStyledItemDelegate, QTableWidget, QTableWidgetItem, QWidget)


class StarPolygon(QPolygonF):
    def __init__(self, size: float):
        super().__init__()

        # offset_x = -0
        # offset_y = 100

        for i in range(5):
            x = math.cos(0.8 * i * math.pi - math.pi / 2)
            y = math.sin(0.8 * i * math.pi - math.pi / 2)
            self << QPointF(size * x, size *  y)


class HalfStarPolygon(QPolygonF):
    def __init__(self, size: float):
        super().__init__()

        # star_polygon_size = 40
        half_star_polygon_size = size / 2
        star_angle_step = 2 * math.pi / 5
        star_angle_start = - math.pi / 2
        half_star_angle_start = star_angle_start - star_angle_step / 2

        x = math.cos(star_angle_start)
        y = math.sin(star_angle_start)
        self << QPointF(size * x, size * y)

        x = math.cos(half_star_angle_start)
        y = math.sin(half_star_angle_start)
        self << QPointF(half_star_polygon_size * x, half_star_polygon_size * y)

        star_angle_start -= star_angle_step
        x = math.cos(star_angle_start)
        y = math.sin(star_angle_start)
        self << QPointF(size * x, size * y)

        half_star_angle_start -= star_angle_step
        x = math.cos(half_star_angle_start)
        y = math.sin(half_star_angle_start)
        self << QPointF(half_star_polygon_size * x, half_star_polygon_size * y)

        star_angle_start -= star_angle_step
        x = math.cos(star_angle_start)
        y = math.sin(star_angle_start)
        self << QPointF(size * x, size * y)

        half_star_angle_start -= star_angle_step
        x = math.cos(half_star_angle_start)
        y = math.sin(half_star_angle_start)
        self << QPointF(half_star_polygon_size * x, half_star_polygon_size * y)


def get_star_polygon():
    star_polygon = QPolygonF()

    for i in range(5):
        star_polygon_size = 0.5
        default_x = math.cos(0.8 * i * math.pi - math.pi / 2)
        default_y = math.sin(0.8 * i * math.pi - math.pi / 2)
        star_polygon << QPointF(1 + star_polygon_size * default_x,
                                1 + star_polygon_size * default_y)
    return star_polygon


class StarRating:
    # enum EditMode
    Editable, ReadOnly = False, True
    # PaintingScaleFactor = 10

    def __init__(self, star_count: float = 0, max_star_count: float = 5):
        self._star_count = float(star_count)
        self._max_star_count = float(max_star_count)

        self.star_polygon_size = 10
        half_star_polygon_size = 0.3
        star_angle_step = 2 * math.pi / 5
        star_angle_start = - math.pi / 2
        half_star_angle_start = star_angle_start + star_angle_step / 2

        self.star_polygon = StarPolygon(self.star_polygon_size)
        self.half_star_polygon = HalfStarPolygon(self.star_polygon_size)

    def star_count(self):
        return self._star_count

    def max_star_count(self):
        return self._max_star_count

    def set_star_count(self, star_count: float):
        # print(star_count)
        self._star_count = star_count

    def set_max_star_count(self, max_star_count: float):
        self._max_star_count = max_star_count

    def size_hint(self):
        return self.star_polygon_size * QSize(self._max_star_count, 1) * 2

    def paint(self, painter, rect, palette, edit_mode):
        painter.save()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)

        if edit_mode == StarRating.Editable:
            painter.setBrush(palette.highlight())
        else:
            painter.setBrush(palette.windowText())

        y_offset = (rect.height() - self.star_polygon_size) / 2
        painter.translate(rect.x() + self.star_polygon_size, rect.y() + y_offset)

        for i in range(int(self._star_count * 2)):
            if not i % 2:
                painter.drawPolygon(self.half_star_polygon, Qt.FillRule.WindingFill)
            else:
                painter.drawPolygon(self.star_polygon, Qt.FillRule.WindingFill)
                painter.translate(self.star_polygon_size * 2, 0.0)

        painter.restore()


class StarEditor(QWidget):
    editing_finished = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self._star_rating = StarRating()

        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        # self.setStyleSheet("background-color: red")

    def set_star_rating(self, star_rating: float):
        self._star_rating = star_rating

    def star_rating(self):
        return self._star_rating

    def sizeHint(self):
        return self._star_rating.size_hint()

    def paintEvent(self, event):
        painter = QPainter(self)
        self._star_rating.paint(painter, self.rect(), self.palette(),
                StarRating.Editable)

    def mouseMoveEvent(self, event: QMoveEvent):
        print(event.pos().x())
        star = self.star_at_position(event.pos().x())

        if star != self._star_rating.star_count() and star != -1:
            self._star_rating.set_star_count(star)
            self.update()

    def mouseReleaseEvent(self, event):
        self.editing_finished.emit()

    def star_at_position(self, x):
        if not x:
            return 0

        # Enable a star, if pointer crosses the center horizontally.
        star_width = self._star_rating.size_hint().width() // self._star_rating.max_star_count()
        num_of_stars = (x + star_width / 2) / star_width // 0.5 / 2
        if 0 <= num_of_stars <= self._star_rating.max_star_count():
            return num_of_stars

        return -1


class StarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())

            star_rating.paint(painter, option.rect, option.palette, StarRating.ReadOnly)
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            return star_rating.size_hint()
        else:
            return super().sizeHint(option, index)

    def createEditor(self, parent, option, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            editor = StarEditor(parent)
            editor.editing_finished.connect(self.commit_and_close_editor)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor: StarEditor, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            editor.set_star_rating(star_rating)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: StarEditor, model, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            model.setData(index, editor.star_rating())
        else:
            super().setModelData(editor, model, index)

    def commit_and_close_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)


def populate_table_widget(table_widget):
    static_data = (
        ("Mass in B-Minor", "Baroque", "J.S. Bach", 5),
        ("Three More Foxes", "Jazz", "Maynard Ferguson", 4),
        ("Sex Bomb", "Pop", "Tom Jones", 3),
        ("Barbie Girl", "Pop", "Aqua", 5),
    )

    for row, (title, genre, artist, rating) in enumerate(static_data):
        item0 = QTableWidgetItem(title)
        item1 = QTableWidgetItem(genre)
        item2 = QTableWidgetItem(artist)
        item3 = QTableWidgetItem()
        item3.setData(0, StarRating(rating))
        table_widget.setItem(row, 0, item0)
        table_widget.setItem(row, 1, item1)
        table_widget.setItem(row, 2, item2)
        table_widget.setItem(row, 3, item3)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    tableWidget = QTableWidget(4, 4)
    tableWidget.setItemDelegate(StarDelegate())
    tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
    tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    headerLabels = ("Title", "Genre", "Artist", "Rating")
    tableWidget.setHorizontalHeaderLabels(headerLabels)

    populate_table_widget(tableWidget)

    tableWidget.resizeColumnsToContents()
    tableWidget.resize(500, 300)
    tableWidget.show()

    sys.exit(app.exec())
