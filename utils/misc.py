import os
from typing import Union

from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGridLayout, QLayout, QFrame, QCheckBox


def classify(module):
    return type(module.__name__, (),
                {key: staticmethod(value) if callable(value) else value
                 for key, value in ((name, getattr(module, name))
                                    for name in dir(module))})


def get_project_root(file_path: str) -> str:
    anchor_files = ("main.py", "Qt6Widgets.dll")
    dir_path = os.path.dirname(file_path)
    while dir_path != '/' and not any([os.path.exists(os.path.join(dir_path, a)) for a in anchor_files]):
        dir_path = os.path.dirname(dir_path)

    if dir_path == '/':
        dir_path = os.path.dirname(file_path)
    return dir_path


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def delete_items(layout: QLayout) -> None:
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                delete_items(item.layout())


def delete_grid_layout_items(layout: QGridLayout) -> None:
    if layout is None:
        return
    for r in range(layout.rowCount()):
        for c in range(layout.columnCount()):
            item = layout.itemAtPosition(r, c)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
    for i in range(layout.count()):
        layout.takeAt(i)


def index_pos(index: QModelIndex):
    return index.row(), index.column()


class TrackNotInPlaylistError(Exception):
    pass


class QHLine(QFrame):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


def combine_colors(color_a: Union[QColor, Qt.GlobalColor], color_b: Union[QColor, Qt.GlobalColor],
                   part_a: float) -> QColor:
    if part_a > 1 or part_a < 0:
        raise BaseException
    rgb_a = part_a * QColor(color_a).rgb()
    rgb_b = (1 - part_a) * QColor(color_b).rgb()

    return QColor(int(rgb_a + rgb_b))


class PathCheckbox(QCheckBox):
    state_changed = pyqtSignal(bool, str)

    def __init__(self, *args):
        super().__init__(*args)
        self.path = None
        self.stateChanged.connect(lambda: self.state_changed.emit(self.checkState() == Qt.CheckState.Checked,
                                                                  self.path))

    def set_path(self, p: str) -> None:
        self.path = p
