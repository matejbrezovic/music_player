import sys
import weakref
from typing import Any, Optional

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QHeaderView, QStyledItemDelegate, QStyleOptionViewItem, QFrame


class HeaderView(QtWidgets.QHeaderView):
    def __init__(self,
                 orientation: QtCore.Qt.Orientation = Qt.Orientation.Horizontal,
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(orientation, parent)

        self.padding = 4

        self.setMinimumSectionSize(5)
        self.setStretchLastSection(True)
        self.setCascadingSectionResizes(True)
        self.setSectionsMovable(True)
        self.setFirstSectionMovable(False)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.sectionMoved.connect(self.section_moved)
        self.sectionResized.connect(self.section_resized)
        self.__section_moved_recursions = 0
        self.__section_resized_recursions = 0

        self.fixed_section_indexes = (0, 1)

        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.setTimerType(Qt.TimerType.PreciseTimer)
        # timer.timeout.connect(self._update_sizes)

        resize_mode_timer = QtCore.QTimer(self)
        resize_mode_timer.setTimerType(Qt.TimerType.PreciseTimer)
        resize_mode_timer.setSingleShot(True)
        # resize_mode_timer.timeout.connect(lambda: self.setSectionResizeMode(QHeaderView.ResizeMode.Interactive))

        self._resize_mode_timer = weakref.proxy(resize_mode_timer)
        self._timer = weakref.proxy(timer)
        # self.sectionResized.connect(self._handle_resize)

        # self.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        self.proportions = []

        self.mouse_pressed = False

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        self.mouse_pressed = False
        super().mouseReleaseEvent(e)
        self.proportions = [self.sectionSize(i) / self.width() for i in range(self.count())]
        # print(self.mouse_pressed)

    def init_sizes(self):
        each = self.width() // self.count()
        for i in range(self.count()):
            self.resizeSection(self.logicalIndex(i), each)

    @pyqtSlot(int, int, int)
    def _handle_resize(self, logicalIndex: int, oldSize: int, newSize: int):
        # return
        self._timer.start(1)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        width = self.width()
        # sizes = [self.sectionSize(self.logicalIndex(i)) for i in range(self.count())]
        width_without_fixed = width - sum([self.sectionSize(i) for i in self.fixed_section_indexes])

        for i in range(self.count()):
            if not self.proportions:
                break

            if i not in self.fixed_section_indexes:
                self.resizeSection(i, int(self.proportions[i] * width_without_fixed))

        self._timer.start(1)

    @pyqtSlot()
    def _update_sizes(self):
        print("updated sizes")
        width = self.width()
        sizes = [self.sectionSize(self.logicalIndex(i)) for i in range(self.count())]
        # width_without_fixed = width - sum([self.sectionSize(i) for i in self.fixed_section_indexes])
        index = len(sizes) - 1
        i = 0
        while index >= 0 and sum(sizes) > width:
            i += 1
            if i > 100:
                break
            if sizes[index] > 5 and index not in self.fixed_section_indexes:  # minimum width (5)
                new_width = width - (sum(sizes) - sizes[index])
                if new_width < 5:
                    new_width = 5
                sizes[index] = new_width
            index -= 1
        for j, value in enumerate(sizes):
            self.resizeSection(self.logicalIndex(j), value)
        if not self.proportions:
            self.proportions = [self.sectionSize(i) / width for i in range(self.count())]

    def text(self, section):
        if isinstance(self.model(), QtCore.QAbstractItemModel):
            return self.model().headerData(section, self.orientation())

    def paintSection(self, painter: QtGui.QPainter, rect: QtCore.QRect, logicalIndex: int) -> None:
        elided_text: str = QFontMetrics(self.font()).elidedText(self.text(logicalIndex),
                                                                Qt.TextElideMode.ElideRight,
                                                                self.sectionSize(logicalIndex))

        top = rect.topLeft()
        top.setY(top.y() + 1)
        bottom = rect.bottomLeft()
        bottom.setY(bottom.y() - 2)

        painter.setPen(Qt.GlobalColor.gray)
        painter.drawLine(top, bottom)

        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        painter.setPen(Qt.GlobalColor.black)
        rect.setLeft(rect.left() + self.padding)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft, elided_text)

    def section_moved(self, logicalIndex: int, oldVisualIndex: int, newVisualIndex: int) -> None:
        """Prevents section 1 from moving."""
        if self.__section_moved_recursions:
            self. __section_moved_recursions = 0
            return

        if 1 in [oldVisualIndex, newVisualIndex]:
            self.__section_moved_recursions += 1
            self.moveSection(newVisualIndex, oldVisualIndex)

    def section_resized(self, logical_index: int, old_size: int, new_size: int) -> None:
        if self.__section_resized_recursions:
            self.__section_resized_recursions = 0
            return

        # if logical_index == 6:
        #
        #     print(logical_index, old_size, new_size)
        self.__section_resized_recursions += 1
        count = self.model().columnCount()
        width = self.width()
        sum = self.length()

        if sum != width:
            if logical_index < count:
                next_header_size = self.sectionSize(logical_index + 1)
                if next_header_size > sum - width:
                    self.resizeSection(logical_index + 1, next_header_size - (sum - width))
                else:
                    self.resizeSection(logical_index, old_size)


class Model(QtCore.QAbstractTableModel):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super(Model, self).__init__(parent)
        self.__headers = ["Column A", "Column B", "Column C", "Column D", "Column E", "Column F", "Column G"]
        self.__data = []
        for i in range(10):
            row = [0, 1, 2, 3, 42222222222, 5, 6, 74444444]
            self.__data.append(row)

    def rowCount(self, index: Optional[QtCore.QModelIndex] = None) -> int:
        return len(self.__data)

    def columnCount(self, index: Optional[QtCore.QModelIndex] = None) -> int:
        return len(self.__headers)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: QtCore.Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.__headers[section]
            return f"{section}"
        return None

    def data(self, index: QtCore.QModelIndex,
             role: QtCore.Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            return self.__data[index.row()][index.column()]
        return None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    view = QtWidgets.QTableView()
    view.resize(600, 600)
    header = HeaderView()
    # view.setFixedSize(600, 600)
    # header.setFixedWidth(600)
    view.setHorizontalHeader(header)
    view.setFrameShape(QFrame.Shape.NoFrame)
    model = Model()
    view.setModel(model)
    header.init_sizes()
    header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
    # header.setStyleSheet("background-color: red;")
    view.horizontalHeader().resizeSection(0, 30)
    view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
    view.horizontalHeader().resizeSection(1, 30)
    view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
    view.show()
    app.exec()
