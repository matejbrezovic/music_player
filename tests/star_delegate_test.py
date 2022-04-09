import math
import typing
from typing import Any, List, Union

from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QPointF, QSize, Qt, QModelIndex, QEvent
from PyQt6.QtGui import QPainter, QPolygonF, QMoveEvent, QPalette, QColor
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QStyle, QStyledItemDelegate, QWidget, QTableView,
                             QMainWindow, QHBoxLayout)


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
        return self.star_polygon_size * QSize(int(self._max_star_count), 1) * 2

    def paint(self, painter, rect, palette, edit_mode, color = None):
        painter.save()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)

        if color:
            painter.setBrush(color)
        elif edit_mode == StarRating.Editable:
            painter.setBrush(Qt.GlobalColor.red)
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


def combine_colors(color_a: Union[QColor, Qt.GlobalColor], color_b: Union[QColor, Qt.GlobalColor], part_a: float) -> QColor:
    if part_a > 1 or part_a < 0:
        raise BaseException
    rgb_a = part_a * QColor(color_a).rgb()
    rgb_b = (1 - part_a) * QColor(color_b).rgb()

    return QColor(int(rgb_a + rgb_b))


class StarEditor(QWidget):
    def __init__(self, parent: QWidget, palette: QPalette):
        super().__init__(parent)
        self.setPalette(palette)
        self._star_rating = StarRating()

        self.selected_star_count = self._star_rating.star_count()

        self.setMouseTracking(True)
        self.setAutoFillBackground(True)

    def __repr__(self):
        return f"Editor {self._star_rating.star_count()}"

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
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().highlight())
        painter.drawRect(self.rect())
        background_stars_color = combine_colors(self.palette().highlight(), self.palette().base(), 0.8)
        StarRating(5).paint(QPainter(self), self.rect(), self.palette(), StarRating.ReadOnly, background_stars_color)
        self._star_rating.paint(QPainter(self), self.rect(), self.palette(), StarRating.Editable, self.palette().base())

    def repaint_on_changed_selection(self) -> None:
        painter = QPainter(self)
        self._star_rating.paint(painter, self.rect(), self.palette(), False)

    def mouseMoveEvent(self, event: QMoveEvent):
        star = self.star_at_position(event.pos().x())

        if star != self._star_rating.star_count() and star != -1:
            self._star_rating.set_star_count(star)
            self.update()

    def mouseReleaseEvent(self, event):
        self.set_selected_star_count(self._star_rating.star_count())

    def leaveEvent(self, e: QtCore.QEvent) -> None:
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


class StarDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self.active_editors = []

    def paint(self, painter, option, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                star_rating.paint(painter, option.rect, option.palette, StarRating, option.palette.base())
            else:
                star_rating.paint(painter, option.rect, option.palette, StarRating)
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
            editor = StarEditor(parent, option.palette)
            editor.set_selected_star_count(star_rating.star_count())
        else:
            editor = super().createEditor(parent, option, index)
        self.active_editors.append(editor)
        return editor

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

    def commit_and_close_editors(self):
        """Closes all editors except the last one (if there's more than one editor), otherwise it closes all of them
        (no new editor was opened)"""

        print("Commit and close editors:", self.active_editors)

        editors_to_close = self.active_editors[:-1] if len(self.active_editors) > 1 else self.active_editors
        for editor in editors_to_close:
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)
            editor.deleteLater()
        self.active_editors = [self.active_editors[-1]] if len(self.active_editors) > 1 else []

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

        self.general_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 3:
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
        if index.column() == 3:
            return self.general_flags | Qt.ItemFlag.ItemIsEditable
        return self.general_flags

    def setData(self, index, value, role = Qt.ItemDataRole.EditRole):
        if isinstance(value, StarRating):
            self.static_data[index.row()][3] = value.star_count()

        return super().setData(index, value, role)


class DefaultItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)


class MouseTrackingTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # palette = self.palette()
        # palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.Highlight, Qt.GlobalColor.darkBlue)
        # self.setPalette(palette)

        self.setModel(Model())
        self.setItemDelegate(DefaultItemDelegate())
        self.setItemDelegateForColumn(3, StarDelegate())
        self.prev_index = QModelIndex()
        self.setShowGrid(False)
        self.setMouseTracking(True)

    def selectionChanged(self, selected, deselected) -> None:
        for index in deselected.indexes():
            if index.column() == 3:
                typing.cast(StarDelegate, self.itemDelegateForColumn(3)).commit_and_close_editors()
                # self.repaint()
                self.edit(index, QAbstractItemView.EditTrigger.CurrentChanged)
        super().selectionChanged(selected, deselected)


    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        index = self.indexAt(e.pos())
        if index != self.prev_index:
            if index.column() == 3 and index in self.selectedIndexes():
                self.openPersistentEditor(index)
            self.prev_index = index
        super().mouseMoveEvent(e)


    def currentChanged(self, current: QtCore.QModelIndex, previous: QtCore.QModelIndex) -> None:
        if current.column() == 3 and current not in self.selectedIndexes():
            self.openPersistentEditor(current)
            self.edit(current, QAbstractItemView.EditTrigger.CurrentChanged)

        super().currentChanged(current, previous)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        index = self.indexAt(e.pos())
        if index.column() == 3 and index not in self.selectedIndexes():
            self.openPersistentEditor(index)
        self.prev_index = index
        super().mousePressEvent(e)

    def edit(self, index: QModelIndex, trigger=QAbstractItemView.EditTrigger.NoEditTriggers, event: QEvent = QEvent(0)):
        if trigger == QAbstractItemView.EditTrigger.NoEditTriggers:
            return False
        return super().edit(index, trigger, event)


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
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
