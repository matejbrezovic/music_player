import io
import sys

from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QBuffer
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtWidgets import *

from utils import get_artwork_pixmap


class TestImageLabel(QLabel):
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

        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
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


class BlurWindowPixmapUi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.central_widget_layout = QHBoxLayout()
        self.setCentralWidget(self.central_widget)

        names = ["05 Frozen in Time.mp3",
                 "07 Sanctuary.mp3",
                 "06 Below Zero.mp3",
                 "04 Sound of Silence (Subnautica_ Below Zero).mp3",
                 "03 Ice in My Veins.mp3"]

        self.pixmap = get_artwork_pixmap(f"C:/home/matey/Music/{names[4]}").scaled(
                                      200, 200,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)

        self.label = QLabel(self)
        self.label.setFixedSize(300, 300)
        self.label.setPixmap(self.pixmap)

        self.blurred_label = QLabel(self)
        self.blurred_label.setFixedSize(200, 200)

        # blurred_pixmap = self.blur_pixmap(self.pixmap)
        img = self.pixmap.toImage()
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        img.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))

        blur_img = pil_im.filter(ImageFilter.GaussianBlur(80))

        # blur_img.show()

        # blurred_pixmap = QPixmap.fromImage(ImageQt(blur_img))

        im2 = blur_img.convert("RGBA")
        data = im2.tobytes("raw", "BGRA")
        qim = QtGui.QImage(data, blur_img.size[0], blur_img.size[1], QtGui.QImage.Format.Format_ARGB32)
        blurred_pixmap = QtGui.QPixmap.fromImage(qim)

        print(blurred_pixmap)
        self.blurred_label.setPixmap(blurred_pixmap)

        self.central_widget_layout.addWidget(self.label)
        self.central_widget_layout.addWidget(self.blurred_label)
        self.central_widget.setLayout(self.central_widget_layout)


    # def blur_pixmap(self, pix: QPixmap) -> QPixmap:
    #     # image = pix.toImage()
    #
    #     blurred_label = QLabel(self)
    #     blurred_label.setFixedSize(200, 200)
    #
    #     blur_effect = QGraphicsBlurEffect()
    #     blur_effect.setBlurRadius(100)
    #     # blur_effect.so
    #
    #     blurred_label.setPixmap(pix)
    #     blurred_label.setGraphicsEffect(blur_effect)
    #
    #     output = QPixmap(pix.width(), pix.height())
    #     painter = QPainter(output)
    #     blurred_label.render(painter)
    #     return output


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = BlurWindowPixmapUi()
    main_window.setFixedSize(400, 400)
    main_window.show()
    sys.exit(app.exec())