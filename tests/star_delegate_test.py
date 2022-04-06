import math

from PyQt6.QtCore import pyqtSignal, QPointF, QSize, Qt
from PyQt6.QtGui import QPainter, QPolygonF, QMoveEvent
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QStyle,
                             QStyledItemDelegate, QTableWidget, QTableWidgetItem, QWidget)
from PyQt6.QtGui import QColor


class StarRating:
    # enum EditMode
    Editable, ReadOnly = False, True
    PaintingScaleFactor = 20

    def __init__(self, star_count=1, max_star_count=5):
        self._star_count = star_count
        self._max_star_count = max_star_count

        self.star_polygon = QPolygonF([QPointF(1.0, 0.5)])
        for i in range(5):
            self.star_polygon << QPointF(0.5 + 0.5 * math.cos(0.8 * i * math.pi),
                                        0.5 + 0.5 * math.sin(0.8 * i * math.pi))

        self.diamond_polygon = QPolygonF()
        self.diamond_polygon << QPointF(0.4, 0.5) \
                             << QPointF(0.5, 0.4) \
                             << QPointF(0.6, 0.5) \
                             << QPointF(0.5, 0.6) \
                             << QPointF(0.4, 0.5)

    def star_count(self):
        return self._star_count

    def max_star_count(self):
        return self._max_star_count

    def set_star_count(self, star_count):
        self._star_count = star_count

    def set_max_star_count(self, max_star_count):
        self._max_star_count = max_star_count

    def size_hint(self):
        return self.PaintingScaleFactor * QSize(self._max_star_count, 1)

    def paint(self, painter, rect, palette, edit_mode):
        painter.save()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)

        if edit_mode == StarRating.Editable:
            painter.setBrush(palette.highlight())
        else:
            painter.setBrush(palette.windowText())

        y_offset = (rect.height() - self.PaintingScaleFactor) / 2
        painter.translate(rect.x(), rect.y() + y_offset)
        painter.scale(self.PaintingScaleFactor, self.PaintingScaleFactor)

        for i in range(self._max_star_count):
            if i < self._star_count:
                painter.drawPolygon(self.star_polygon, Qt.FillRule.WindingFill)
            elif edit_mode == StarRating.Editable:
                painter.setBrush(QColor("red"))
                painter.drawPolygon(self.diamond_polygon, Qt.FillRule.WindingFill)

            painter.translate(1.0, 0.0)

        painter.restore()


class StarEditor(QWidget):
    editing_finished = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self._starRating = StarRating()

        self.setMouseTracking(True)
        self.setAutoFillBackground(True)

    def set_star_rating(self, star_rating):
        self._starRating = star_rating

    def star_rating(self):
        return self._starRating

    def sizeHint(self):
        return self._starRating.size_hint()

    def paintEvent(self, event):
        painter = QPainter(self)
        self._starRating.paint(painter, self.rect(), self.palette(),
                StarRating.Editable)

    def mouseMoveEvent(self, event: QMoveEvent):
        star = self.star_at_position(event.pos().x())

        if star != self._starRating.star_count() and star != -1:
            self._starRating.set_star_count(star)
            self.update()

    def mouseReleaseEvent(self, event):
        self.editing_finished.emit()

    def star_at_position(self, x):
        # Enable a star, if pointer crosses the center horizontally.
        star_width = self._starRating.size_hint().width() // self._starRating.max_star_count()
        star = (x + star_width / 2) // star_width
        if 0 <= star <= self._starRating.max_star_count():
            return star

        return -1


class StarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())

            star_rating.paint(painter, option.rect, option.palette,
                    StarRating.ReadOnly)
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
