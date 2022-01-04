import datetime

import mutagen
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFontMetrics, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QFrame, QGridLayout
from mutagen import MutagenError
from mutagen.id3 import ID3
from mutagen.mp4 import MP4
from PIL.ImageQt import ImageQt


def classify(module):
    return type(module.__name__, (),
                {key: staticmethod(value) if callable(value) else value
                 for key, value in ((name, getattr(module, name))
                                    for name in dir(module))})


def delete_items(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                delete_items(item.layout())


def unparent_items(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                delete_items(item.layout())


class ElidedLabel(QLabel):
    clicked = pyqtSignal(QLabel)
    double_clicked = pyqtSignal(QLabel)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    def paintEvent(self, event):
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        QPainter(self).drawText(self.rect(), self.alignment(), elided)

    def mousePressEvent(self, ev):
        self.clicked.emit(self)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.double_clicked.emit(self)


class ImageLabel(QLabel):
    def __init__(self, pixmap: QPixmap):
        super().__init__()
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

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self.pixmap is not None:
            if self.pixmap.width() != 0 and self.width() != 0:
                if self.pixmap.height() / self.pixmap.width() > self.height() / self.width():
                    displayed_image = self.pixmap.scaledToHeight(self.height(),
                                                                 Qt.TransformationMode.SmoothTransformation)
                else:
                    displayed_image = self.pixmap.scaledToWidth(self.width(),
                                                                Qt.TransformationMode.SmoothTransformation)

                self.setPixmap(displayed_image)

    def heightForWidth(self, width):
        return width


def get_artwork_pixmap(file_path: str, default: str = "album"):
    class NoArtworkError(Exception):
        pass

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
    except (AttributeError, NoArtworkError, MutagenError):
        if default.lower() in ['album', 'artist', 'composer', 'folder']:
            pixmap = QPixmap(f"icons/{default.lower()}.png")
        else:
            pixmap = QPixmap("icons/misc.png")
    return pixmap


def get_formatted_time(track_duration: int):
    hours = int(track_duration / 3600000)
    minutes = int((track_duration / 60000) % 60)
    seconds = int((track_duration / 1000) % 60)

    return f'{str(hours) + ":" if hours else ""}{"0" + str(minutes) if hours else minutes}:' \
           f'{"0" + str(seconds) if seconds < 10 else seconds}'


def format_seconds(time_in_seconds: int):
    return str(datetime.timedelta(seconds=time_in_seconds)).replace("0:", "")


def delete_grid_layout_items(layout: QGridLayout):
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


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
