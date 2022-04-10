import datetime
import io
from os import path
from typing import Optional, Union

import mutagen
from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QBuffer, QPointF, QTimer, QModelIndex
from PyQt6.QtGui import (QFontMetrics, QPainter, QPixmap, QColor, QIcon, QEnterEvent, qRgba, QImage, QLinearGradient,
                         QTransform, QStaticText)
from PyQt6.QtWidgets import *
from mutagen import MutagenError
from mutagen.id3 import ID3
from mutagen.mp4 import MP4

import constants


def classify(module):
    return type(module.__name__, (),
                {key: staticmethod(value) if callable(value) else value
                 for key, value in ((name, getattr(module, name))
                                    for name in dir(module))})


def get_project_root(file_path: str) -> str:
    anchor_files = ("main.py", "Qt6Widgets.dll")
    dir_path = path.dirname(file_path)
    while dir_path != '/' and not any([path.exists(path.join(dir_path, a)) for a in anchor_files]):
        dir_path = path.dirname(dir_path)

    if dir_path == '/':
        dir_path = path.dirname(file_path)

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


class ElidedLabel(QLabel):
    def __init__(self, *args):
        super().__init__(*tuple(map(str, args)) if args else "")
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    def paintEvent(self, event) -> None:
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        rect = self.rect()
        rect.setLeft(self.contentsMargins().left() + rect.left())
        QPainter(self).drawText(rect, self.alignment(), elided)


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

        # self.resize_counter = 0
        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        # self.resize_counter += 1
        # if self.resize_counter > 100:
        #     self.resize_counter = 0
        #     return
        # print(self.width())
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
        self.setStyle(FixedHorizontalSplitterProxyStyle())
        self.last_sizes = self.sizes()
        self.splitterMoved.connect(self.splitter_moved)

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


class FixedHorizontalSplitterProxyStyle(QProxyStyle):
    def __init__(self, *args):
        super().__init__(*args)

    def drawControl(self,
                    element: QStyle.ControlElement,
                    option: QStyleOption,
                    painter: QtGui.QPainter,
                    widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.ControlElement.CE_RubberBand:
            painter.save()
            option.rect.setWidth(10)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("grey"))
            painter.drawRect(option.rect)
            painter.restore()
        else:
            return super().drawControl(element, option, painter, widget)


class QHLine(QFrame):
    def __init__(self):
        super().__init__()
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

    def set_path(self, p: str) -> None:
        self.path = p


class TransparentComboBox(QComboBox):
    default_stylesheet = ''' 
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
    hide_combobox = '''QComboBox::drop-down:!hover {
                            background-color: rgba(255, 255, 255, 0);
                        }'''

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(self.hide_combobox + self.default_stylesheet)
        self.setUpdatesEnabled(True)
        self.currentIndexChanged.connect(lambda: self.adjustSize())

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


class ImprovedSlider(QSlider):
    value_changed = pyqtSignal(int)

    def __init__(self, *args):
        super().__init__(*args)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            val = self.pixel_pos_to_range_value(event.pos())
            self.setValue(val)
            self.value_changed.emit(val)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        val = self.pixel_pos_to_range_value(event.pos())
        self.setValue(val)
        self.value_changed.emit(val)

    def pixel_pos_to_range_value(self, pos: QPoint) -> int:
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt,
                                         QStyle.SubControl.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt,
                                         QStyle.SubControl.SC_SliderHandle, self)

        slider_length = sr.width()
        slider_min = gr.x()
        slider_max = gr.right() - slider_length + 2

        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == QtCore.Qt.Orientation.Horizontal else pr.y()
        val = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - slider_min,
                                             slider_max - slider_min, opt.upsideDown)
        if val == 99:  # it wasn't able to be 100
            val = 100
        return val


class MarqueeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.static_text = QStaticText()
        self.static_text.setTextFormat(Qt.TextFormat.PlainText)
        self._text = ''
        self.timer = QTimer()
        self.timer.setInterval(16)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.timer_timeout)
        self.wait_timer = QTimer()
        self.wait_timer.setInterval(10)
        self.wait_timer.timeout.connect(self.timer_timeout)
        self.left_margin = int(self.height() / 3)
        self.single_text_width = 0
        self.scroll_pos = 0
        self.buffer = QImage()
        self.alpha_channel = QImage()
        self.scroll_enabled = False
        self.waiting = True
        self.seperator = '     :::     '
        self.update_text()

        self.whole_text_size = QSize(0, 0)
        self.update_text_rect_flag = True

    def text(self):
        return self._text

    def setText(self, text: str):
        self._text = text
        self.update_text()
        self.update()
        self.updateGeometry()

    def sizeHint(self):
        return QSize(min(self.whole_text_size.width() + self.left_margin, self.maximumWidth()),
                     self.fontMetrics().height())

    def update_text(self):
        self.timer.stop()
        self.update_text_rect_flag = True

        self.single_text_width = self.fontMetrics().horizontalAdvance(self._text)
        self.scroll_enabled = self.single_text_width > self.width() - self.left_margin

        if self.scroll_enabled:
            self.static_text.setText(self._text + self.seperator)
            if not self.window().windowState() & Qt.WindowState.WindowMinimized:
                self.scroll_pos = 0
                self.wait_timer.start()
                self.waiting = True
        else:
            self.static_text.setText(self._text)

        self.static_text.prepare(QTransform(), self.font())

    def hideEvent(self, event):
        if self.scroll_enabled:
            self.scroll_pos = 0
            self.timer.stop()
            self.wait_timer.stop()

    def showEvent(self, event):
        if self.scroll_enabled:
            self.wait_timer.start()
            self.waiting = True

    def paintEvent(self, paint_event):
        painter = QPainter(self)
        if self.update_text_rect_flag:
            r = painter.boundingRect(0, 0, 0, 0, 0, self.static_text.text())
            self.whole_text_size = QSize(r.width(), r.height())
            self.update_text_rect_flag = False
        if self.scroll_enabled:
            self.buffer.fill(qRgba(0, 0, 0, 0))
            pb = QPainter(self.buffer)
            pb.setPen(painter.pen())
            pb.setFont(painter.font())
            x = min(-self.scroll_pos, 0) + self.left_margin
            while x < self.width():
                pb.drawStaticText(QPointF(x, (self.height() - self.whole_text_size.height()) / 2), self.static_text)
                x += self.whole_text_size.width()
            # apply Alpha channel
            pb.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            pb.setClipRect(self.width() - 15, 0, 15, self.height())
            pb.drawImage(0, 0, self.alpha_channel)
            pb.setClipRect(0, 0, 15, self.height())
            pb.drawImage(0, 0, self.alpha_channel)
            painter.drawImage(0, 0, self.buffer)
        else:
            x = self.left_margin + (self.width() - self.left_margin - self.contentsMargins().right() -
                                    self.fontMetrics().horizontalAdvance(self.text())) / 2
            painter.drawStaticText(QPointF(x, (self.height() - self.whole_text_size.height()) / 2),
                                   self.static_text)

    def resizeEvent(self, resize_event):
        # When the widget is resized, we need to update the alpha channel.
        self.alpha_channel = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.buffer = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.alpha_channel.fill(qRgba(0, 0, 0, 0))
        self.buffer.fill(qRgba(0, 0, 0, 0))
        if self.width() > 64:
            grad = QLinearGradient(QPointF(0, 0), QPointF(16, 0))
            grad.setColorAt(0, QColor(0, 0, 0, 0))
            grad.setColorAt(1, QColor(0, 0, 0, 255))
            painter = QPainter(self.alpha_channel)
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, 16, self.height())
            grad = QLinearGradient(QPointF(self.alpha_channel.width() - 16, 0),
                                   QPointF(self.alpha_channel.width(), 0))
            grad.setColorAt(0, QColor(0, 0, 0, 255))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(grad)
            painter.drawRect(self.alpha_channel.width() - 16, 0, self.alpha_channel.width(), self.height())
        else:
            self.alpha_channel.fill(QColor(0, 0, 0))

        new_scroll_enabled = (self.single_text_width > self.width() - self.left_margin)
        if not new_scroll_enabled == self.scroll_enabled:
            self.update_text()

    def timer_timeout(self):
        if self.whole_text_size.width():
            self.scroll_pos = (self.scroll_pos + 1) % \
                             self.whole_text_size.width()
        if self.waiting:
            self.waiting = False
            self.timer.start()
            self.wait_timer.stop()
        if self.scroll_pos == 0:
            self.waiting = True
            self.timer.stop()
            self.wait_timer.start()

        self.update()


class TrackNotInPlaylistError(Exception):
    pass


def get_artwork_pixmap(file_path: str) -> Optional[QPixmap]:
    class NoArtworkError(Exception):
        pass
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
    if default_type.lower() in ('album', 'artist', 'composer', 'folder'):
        return QPixmap(f"icons/{default_type.lower()}.png")
    return QPixmap("icons/misc.png")


def get_blurred_pixmap(pixmap: QPixmap) -> QPixmap:
    img = pixmap.toImage()
    buffer = QBuffer()
    buffer.open(QBuffer.OpenModeFlag.ReadWrite)
    img.save(buffer, "JPG")
    pil_im = Image.open(io.BytesIO(buffer.data()))

    blur_img = pil_im.filter(ImageFilter.GaussianBlur(80))

    im2 = blur_img.convert("RGBA")
    data = im2.tobytes("raw", "BGRA")
    qim = QtGui.QImage(data, blur_img.size[0], blur_img.size[1], QtGui.QImage.Format.Format_ARGB32)

    return QPixmap.fromImage(qim)


class HoverButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)
        self.backup_icon = None
        self.is_in_dark_mode = True

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        if self.isEnabled():
            self.backup_icon = self.icon()
            self.setIcon(get_hover_icon(self.backup_icon, self.is_in_dark_mode))

    def leaveEvent(self, e: QtCore.QEvent) -> None:
        if self.isEnabled():
            self.setIcon(self.backup_icon)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.clicked.emit()
        self.enterEvent(QEnterEvent(QPointF(1, 1), QPointF(1, 1), QPointF(1, 1)))


def change_icon_color(icon: QIcon, color: QColor) -> QIcon:
    pixmap = icon.pixmap(60, 60, QIcon.Mode.Normal)
    mask = pixmap.createMaskFromColor(QColor('transparent'), Qt.MaskMode.MaskInColor)
    pixmap.fill(color)
    pixmap.setMask(mask)
    icon = QIcon(pixmap)
    return icon


def get_hover_icon(icon: QIcon, is_in_dark_mode: bool) -> QIcon:
    pixmap = icon.pixmap(60, 60, QIcon.Mode.Normal)
    mask = pixmap.createMaskFromColor(QColor('transparent'), Qt.MaskMode.MaskInColor)

    color = constants.DARK_AUDIO_CONTROLLER_HOVER_COLOR if is_in_dark_mode \
        else constants.LIGHT_AUDIO_CONTROLLER_HOVER_COLOR

    pixmap.fill(color)
    pixmap.setMask(mask)
    icon = QIcon(pixmap)
    return icon


def combine_colors(color_a: Union[QColor, Qt.GlobalColor], color_b: Union[QColor, Qt.GlobalColor],
                   part_a: float) -> QColor:
    if part_a > 1 or part_a < 0:
        raise BaseException
    rgb_a = part_a * QColor(color_a).rgb()
    rgb_b = (1 - part_a) * QColor(color_b).rgb()

    return QColor(int(rgb_a + rgb_b))


def index_pos(index: QModelIndex):
    return index.row(), index.column()


def get_formatted_time(track_duration: int) -> str:
    hours = int(track_duration / 3600000)
    minutes = int((track_duration / 60000) % 60)
    seconds = int((track_duration / 1000) % 60)

    return f'{str(hours) + ":" if hours else ""}{"0" + str(minutes) if hours else minutes}:' \
           f'{"0" + str(seconds) if seconds < 10 else seconds}'


def format_seconds(time_in_seconds: int) -> str:
    if not time_in_seconds:
        return "0:00"

    if time_in_seconds < 10:
        return f"0:0{time_in_seconds}"

    if time_in_seconds < 60:
        return f"0:{time_in_seconds}"
    time_str = "".join(str(datetime.timedelta(seconds=time_in_seconds))).lstrip("0:")

    return time_str


def get_formatted_time_in_mins(time_in_seconds: int) -> str:
    if not time_in_seconds:
        return "0:00"

    if time_in_seconds < 10:
        return f"0:0{time_in_seconds}"

    if time_in_seconds < 60:
        return f"0:{time_in_seconds}"

    mins = time_in_seconds // 60
    secs = time_in_seconds % 60

    if secs < 10:
        return f"{mins}:0{secs}"
    return f"{mins}:{secs}"


def format_player_position_to_seconds(position: int) -> int:
    return int(position / 1000)


if __name__ == "__main__":
    while True:
        print(format_seconds(int(input())))
