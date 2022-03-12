import datetime
import typing
from typing import Optional

import mutagen
from PIL.ImageQt import ImageQt
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFontMetrics, QPainter, QPixmap, QPalette, QPaintEvent
from PyQt6.QtWidgets import QLabel, QSizePolicy, QFrame, QGridLayout, QSplitter, QLayout, QCheckBox, QTableWidget, \
    QVBoxLayout, QWidget, QComboBox, QStyle, QStyleOptionFocusRect, QStyleOption, QStyleOptionComplex, QProxyStyle
from mutagen import MutagenError
from mutagen.id3 import ID3
from mutagen.mp4 import MP4

from constants import *


def classify(module):
    return type(module.__name__, (),
                {key: staticmethod(value) if callable(value) else value
                 for key, value in ((name, getattr(module, name))
                                    for name in dir(module))})


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


class ElidedLabel(QLabel):
    # clicked = pyqtSignal(QLabel)
    # double_clicked = pyqtSignal(QLabel)

    def __init__(self, *args, **kwargs):
        super().__init__(*tuple(map(str, args)) if args else "", **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    def paintEvent(self, event) -> None:
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        QPainter(self).drawText(self.rect(), self.alignment(), elided)

    # def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
    #     self.clicked.emit(self)
    #
    # def mouseDoubleClickEvent(self, ev: QtGui.QMouseEvent) -> None:
    #     self.double_clicked.emit(self)


class ImageLabel(QLabel):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap

        size_policy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)  # Very important!
        size_policy.setHeightForWidth(True)
        size_policy.setWidthForHeight(True)
        self.setSizePolicy(size_policy)

        if self.pixmap.width() != 0:
            if self.pixmap.height() / self.pixmap.width() > self.height() / self.width():
                self.pixmap = self.pixmap.scaledToHeight(self.height(), Qt.TransformationMode.SmoothTransformation)
            else:
                self.pixmap = self.pixmap.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation)

        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        if self.pixmap is None:
            return
        if self.pixmap.width() != 0 and self.width() != 0:
            if self.pixmap.height() / self.pixmap.width() > self.height() / self.width():
                displayed_pixmap = self.pixmap.scaledToHeight(self.height(),
                                                              Qt.TransformationMode.SmoothTransformation)
            else:
                displayed_pixmap = self.pixmap.scaledToWidth(self.width(),
                                                             Qt.TransformationMode.SmoothTransformation)

            self.setPixmap(displayed_pixmap)

    def heightForWidth(self, width: int) -> int:
        return width

    def setPixmap(self, new_pixmap: QPixmap) -> None:
        super().setPixmap(new_pixmap.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation))


class SpecificImageLabel(QLabel):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap
        # self.setStyleSheet("background-color: red;")
        # self.setMinimumWidth(super().minimumWidth())

        size_policy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)  # Very important!
        size_policy.setHeightForWidth(True)
        size_policy.setWidthForHeight(True)
        self.setSizePolicy(size_policy)

        if self.pixmap.width() != 0:
            self.pixmap = self.pixmap.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation)

        self.resize_counter = 0
        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        self.resize_counter += 1
        if self.resize_counter > 100:
            self.resize_counter = 0
            return
        print(self.width())
        if self.pixmap is None:
            return
        if self.pixmap.width() != 0 and self.width() != 0:
            displayed_pixmap = self.pixmap.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(displayed_pixmap)

    def heightForWidth(self, width: int) -> int:
        return width

    def setPixmap(self, new_pixmap: QPixmap) -> None:
        super().setPixmap(new_pixmap.scaled(self.width(),
                                            self.width(),
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))


class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)


class FixedHorizontalSplitter(QSplitter):
    sizes_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOrientation(Qt.Orientation.Horizontal)
        self.last_sizes = self.sizes()
        self.splitterMoved.connect(self.splitter_moved)

        palette = QPalette()
        # for color in QPalette.ColorRole:
        #     print(color)
        #     palette.setColor(color, Qt.GlobalColor.red)

        # palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.AlternateBase, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Button, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.PlaceholderText, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.NoRole, Qt.GlobalColor.red)

        # palette.setColor(QPalette.ColorRole.Light, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Midlight, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Dark, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Mid, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Shadow, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Highlight, 244)
        # palette.setColor(QPalette.ColorRole.Midlight, QColor(200, 200, 200, 255))
        # palette.setColor(QPalette.ColorRole.Dark)
        # palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.Link, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.LinkVisited, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.NoRole, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.NoRole, Qt.GlobalColor.red)
        # palette.setColor(QPalette.ColorRole.NoRole, Qt.GlobalColor.red)

        # self.setStyle(TestProxyStyle())

        # palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.red)
        # style = self.style()
        # style.setProperty(QStyle.P)

        # self.setPalette(palette)

    # def paintEvent(self, pe: QPaintEvent) -> None:
    #     painter = QPainter(self)
    #     option = QStyleOption()
    #     option.initFrom(self)
    #     option.backgroundColor = QColor(100)
    #     # for p in QStyle.PrimitiveElement:
    #     #     self.style().drawPrimitive(p, option, painter)
    #     # for c in QStyle.ComplexControl:
    #     #     option = QStyleOptionComplex()
    #     #     option.initFrom(self)
    #     #     option.backgroundColor = QColor(100)
    #     #     self.style().drawComplexControl(c, option, painter)
    #     # for k in QStyle.ControlElement:
    #     #     option = QStyleOption()
    #     #     option.initFrom(self)
    #     #     option.backgroundColor = QColor(100)
    #     #     self.style().drawControl(k, option, painter)
    #     self.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorDockWidgetResizeHandle, option, painter, self)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        try:
            if self.sizes()[0] > self.last_sizes[0] or self.sizes()[2] > self.last_sizes[2]:
                first = self.last_sizes[0]
                third = self.last_sizes[2]
                second = self.width() - first - third
                self.setSizes([first, second, third])
        except IndexError:
            self.last_sizes = self.sizes()
        self.last_sizes = self.sizes()

        self.sizes_changed.emit(self.sizes())

    def splitter_moved(self) -> None:
        self.last_sizes = self.sizes()
        self.sizes_changed.emit(self.sizes())


class TestProxyStyle(QProxyStyle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def drawControl(self, element: QStyle.ControlElement, option: 'QStyleOption', painter: QtGui.QPainter, widget: Optional[QWidget] = ...) -> None:
        print("draw control", element)
        if element == QStyle.ControlElement.CE_ShapedFrame:
            print("Resize Handle")
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Highlight, 244)
            option.palette = palette
            painter.setOpacity(255)
            painter.setBrush(Qt.GlobalColor.red)
            painter.setPen(Qt.GlobalColor.green)
        # super().drawPrimitive(element, option, painter, widget)
        super().drawControl(element, option, painter, widget)

    def drawComplexControl(self, control: QStyle.ComplexControl, option: 'QStyleOptionComplex', painter: QtGui.QPainter, widget: typing.Optional[QWidget] = ...) -> None:
        print("draw complex control")
        super().drawComplexControl(control, option, painter, widget)


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class HeaderSplitter(QSplitter):
    resized = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.resized.emit()
        super().resizeEvent(event)


class PathCheckbox(QCheckBox):
    state_changed = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = None
        self.stateChanged.connect(lambda: self.state_changed.emit(True if self.checkState() == Qt.CheckState.Checked
                                                                  else False, self.path))

    def set_path(self, path: str) -> None:
        self.path = path


# class FocusFrame(QFrame): # TODO remove, better fix found
#     def __init__(self, focus_receiver: QWidget, parent=None):
#         super().__init__(parent)
#         self.focus_receiver = focus_receiver
#         self.layout = QVBoxLayout(self)
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.setContentsMargins(0, 0, 0, 0)
#         self.layout.addWidget(focus_receiver)
#         self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
#
#     def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
#         # global_timer.timer_init()
#         # global_timer.start()
#         # print("GOT FOCUS")
#         self.focus_receiver.focusInEvent(event)
#         # global_timer.stop()
#
#     def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
#         # print("LOST FOCUS")
#         self.focus_receiver.focusOutEvent(event)


# class ChangeStylesheetOnClickTableWidget(QTableWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#     def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
#         self.setStyleSheet(SELECTION_STYLESHEET)
#         super().focusInEvent(event)
#
#     def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
#         self.setStyleSheet(LOST_FOCUS_STYLESHEET)
#         super().focusOutEvent(event)


class TransparentComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_stylesheet = ''' 
                QComboBox {
                    color: black;
                    selection-color: black;
                    selection-background-color: rgba(255, 255, 255, 0);
                    background-color: rgba(255, 255, 255, 0);
                }

                QComboBox QAbstractItemView {
                    background-color: white;
                    min-width: 150px;
                }
                QComboBox:open {
                    color: black;
                }
                QComboBox:drop-down:open {
                    color: black;
                    background-color: rgba(255, 255, 255, 0);
                }
                QComboBox:down-arrow:open {
                    color: black;
                    background-color: rgba(255, 255, 255, 0);
                }

                '''
        self.hide_combobox = '''QComboBox::drop-down:!hover {
                                    background-color: rgba(255, 255, 255, 0);
                                }'''

        self.setStyleSheet(self.hide_combobox + self.default_stylesheet)
        self.setUpdatesEnabled(True)
        self.currentIndexChanged.connect(self.adjustSize)

    def sizeHint(self):
        text = self.currentText()
        width = self.fontMetrics().boundingRect(text).width() + 28
        self.setFixedWidth(width)
        return QSize(width, self.height())

    def enterEvent(self, *args, **kwargs):
        super().enterEvent(*args, **kwargs)
        self.setStyleSheet(self.default_stylesheet)

    def leaveEvent(self, *args, **kwargs):
        super().leaveEvent(*args, **kwargs)
        self.setStyleSheet(self.hide_combobox + self.default_stylesheet)



class TrackNotInPlaylistError(Exception):
    pass


def get_artwork_pixmap(file_path: str) -> Optional[QPixmap]:
    class NoArtworkError(Exception):
        pass
    # return None
    # print("CREATED PIXMAP")
    pixmap = QPixmap()
    try:
        try:
            file_id3 = ID3(file_path)
            artwork = file_id3.getall("APIC")[0]
            pixmap.loadFromData(artwork.data)
        except (mutagen.id3.ID3NoHeaderError, IndexError):
            try:
                file_xmp = MP4(file_path)
                artwork = file_xmp.tags["covr"]
                pixmap = QPixmap.fromImage(ImageQt(artwork))
            except (mutagen.mp4.MP4StreamInfoError, KeyError):
                raise NoArtworkError
    except (AttributeError, NoArtworkError, MutagenError, TypeError):
        return None
    return pixmap


def get_default_artwork_pixmap(default_type: str) -> QPixmap:
    if default_type.lower() in ['album', 'artist', 'composer', 'folder']:
        return QPixmap(f"icons/{default_type.lower()}.png")
    return QPixmap("icons/misc.png")


def get_formatted_time(track_duration: int) -> str:
    hours = int(track_duration / 3600000)
    minutes = int((track_duration / 60000) % 60)
    seconds = int((track_duration / 1000) % 60)

    return f'{str(hours) + ":" if hours else ""}{"0" + str(minutes) if hours else minutes}:' \
           f'{"0" + str(seconds) if seconds < 10 else seconds}'


def format_seconds(time_in_seconds: int) -> str:
    # print(time_in_seconds)
    if not time_in_seconds:
        return "0:00"

    if time_in_seconds < 60:
        return f"0:{time_in_seconds}"
    # print("0:".join(str(datetime.timedelta(seconds=time_in_seconds)).split("00:")[-2:]))
    return "".join(str(datetime.timedelta(seconds=time_in_seconds)).split("0:")[-1:]).split()[-1]


def format_player_position_to_seconds(position: int) -> int:
    return int((position / 1000) % 60)
