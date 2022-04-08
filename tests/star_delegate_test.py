import math
import typing
from typing import Any, Dict, List, Union

from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import pyqtSignal, QPointF, QSize, Qt, QModelIndex, QEvent
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainter, QPolygonF, QMoveEvent
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QStyle,
                             QStyledItemDelegate, QTableWidget, QTableWidgetItem, QWidget, QTableView, QMainWindow,
                             QHBoxLayout)


class StarPolygon(QPolygonF):
    def __init__(self, size: float):
        super().__init__()

        for i in range(5):
            x = math.cos(0.8 * i * math.pi - math.pi / 2)
            y = math.sin(0.8 * i * math.pi - math.pi / 2)
            self << QPointF(size * x, size *  y)


class HalfStarPolygon(QPolygonF):
    def __init__(self, size: float):
        super().__init__()

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


class StarRating:
    # enum EditMode
    Editable, ReadOnly = False, True
    # PaintingScaleFactor = 10

    def __init__(self, star_count: float = 0, max_star_count: float = 5):
        self._star_count = float(star_count)
        self._max_star_count = float(max_star_count)

        self.star_polygon_size = 10

        self.star_polygon = StarPolygon(self.star_polygon_size)
        self.half_star_polygon = HalfStarPolygon(self.star_polygon_size)

    def star_count(self):
        return self._star_count

    def max_star_count(self):
        return self._max_star_count

    def set_star_count(self, star_count: float):
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

        self.selected_star_count = self._star_rating.star_count()

        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_star_rating(self, star_rating: StarRating):
        self._star_rating = star_rating

    def set_selected_star_count(self, star_count: float) -> None:
        self.selected_star_count = star_count

    def star_rating(self):
        return self._star_rating

    def sizeHint(self):
        return self._star_rating.size_hint()

    def paintEvent(self, event):
        painter = QPainter(self)
        self._star_rating.paint(painter, self.rect(), self.palette(),
                StarRating.Editable)

    def mouseMoveEvent(self, event: QMoveEvent):
        # print("Editor mouse move:", event.pos().x())
        star = self.star_at_position(event.pos().x())

        if star != self._star_rating.star_count() and star != -1:
            self._star_rating.set_star_count(star)
            self.update()

    def mouseReleaseEvent(self, event):
        self.set_selected_star_count(self._star_rating.star_count())
        self.editing_finished.emit()

    def leaveEvent(self, e: QtCore.QEvent) -> None:
        print("Editor leave event")
        self._star_rating.set_star_count(self.selected_star_count)
        self.update()
        self.editing_finished.emit()
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
        print("Created editor:", index.row(), index.column())
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            editor = StarEditor(parent)
            editor.set_selected_star_count(star_rating.star_count())
            editor.editing_finished.connect(self.commit_and_close_editor)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor: StarEditor, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            editor.set_selected_star_count(star_rating.star_count())
            editor.set_star_rating(star_rating)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: StarEditor, model, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            print(f"Set model data: {index.row(), index.column()}, rating: {editor.star_rating().star_count()}")
            model.setData(index, editor.star_rating())
        else:
            super().setModelData(editor, model, index)

    def commit_and_close_editor(self):
        print("Commit and close editor")
        editor: StarEditor = self.sender()
        # editor.repaint()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)


class Model(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self.header_sections_text = ("Title", "Genre", "Artist", "Rating")

        self.static_data: List[List[Union[str, int]]] = [
            ["Mass in B-Minor", "Baroque", "J.S. Bach", 5],
            ["Three More Foxes", "Jazz", "Maynard Ferguson", 4],
            ["Sex Bomb", "Pop", "Tom Jones", 3],
            ["Barbie Girl", "Pop", "Aqua", 5],
        ]

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        # print(index.row())
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 3:
                # return
                return StarRating(self.static_data[index.row()][index.column()])

            return self.static_data[index.row()][index.column()]

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return 4

    def columnCount(self, index: QModelIndex = QModelIndex) -> int:
        return 4

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: QtCore.Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.header_sections_text[section]
            return f"{section}"
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role = Qt.ItemDataRole.EditRole):
        if isinstance(value, StarRating):
            self.static_data[index.row()][3] = value.star_count()
        super().setData(index, value, role)

        print("Set item data:", index.row(), index.column(), value)


class MouseTrackingTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setModel(Model())
        self.setItemDelegate(StarDelegate())
        self.prev_index = QModelIndex()

        # self.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)

        # self.setIndexWidget(self.model().index(0, 3), StarEditor())
        self.setMouseTracking(True)


    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        index = self.indexAt(e.pos())
        if index != self.prev_index:
            self.itemDelegate().commit_and_close_editor()
            if index.column() == 3 and index in self.selectedIndexes():
                print("Opened editor")
                self.openPersistentEditor(index)
            self.prev_index = index
        super().mouseMoveEvent(e)

    # def leaveEvent(self, e: QtCore.QEvent) -> None:
    #     self.closePersistentEditor(self.prev_index)
    #     self.prev_index = QModelIndex()
    #     super().leaveEvent(e)

    def edit(self, index: QModelIndex, trigger=QAbstractItemView.EditTrigger.NoEditTriggers, event: QEvent = QEvent(0)):
        if trigger == QAbstractItemView.EditTrigger.NoEditTriggers:
            return False
        print(f"Item editing: ({index.row()}, {index.column()})")

        return super().edit(index, trigger, event)





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
        item0.setFlags(item0.flags() & Qt.ItemFlag.ItemIsEditable)
        item1.setFlags(item1.flags() & Qt.ItemFlag.ItemIsEditable)
        item2.setFlags(item2.flags() & Qt.ItemFlag.ItemIsEditable)

        item3 = QTableWidgetItem()
        item3.setData(0, StarRating(rating))
        table_widget.setItem(row, 0, item0)
        table_widget.setItem(row, 1, item1)
        table_widget.setItem(row, 2, item2)
        table_widget.setItem(row, 3, item3)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(700, 700)

        self.central_widget = QWidget()
        self.central_widget_layout = QHBoxLayout(self.central_widget)

        self.table_view = MouseTrackingTableView()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.resize(500, 500)

        self.central_widget_layout.addWidget(self.table_view)
        self.setCentralWidget(self.central_widget)



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    tableWidget = QTableWidget(4, 4)
    tableWidget.setItemDelegateForColumn(3, StarDelegate())
    tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
    tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    populate_table_widget(tableWidget)

    tableWidget.resizeColumnsToContents()
    tableWidget.resize(500, 300)
    # tableWidget.show()

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
