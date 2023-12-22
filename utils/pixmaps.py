import io
import os
from typing import Optional

import mutagen
import mutagen.id3
import mutagen.mp4
from PIL import UnidentifiedImageError, Image, ImageFilter
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import QBuffer, QThread
from PyQt6.QtGui import QPixmap, QImage

from utils import get_project_root


def get_embedded_artwork_pixmap(file_path: str) -> Optional[QPixmap]:
    class NoArtworkError(Exception):
        pass
    pixmap = QPixmap()
    try:
        try:
            file_id3 = mutagen.id3.ID3(file_path)
            artwork = file_id3.getall("APIC")[0]
            pixmap.loadFromData(artwork.data)
        except (mutagen.id3.ID3NoHeaderError, IndexError):
            try:
                file_xmp = mutagen.mp4.MP4(file_path)
                artwork = file_xmp.tags["covr"]
                pixmap = QPixmap.fromImage(ImageQt(artwork))
            except (mutagen.mp4.MP4StreamInfoError, KeyError):
                raise NoArtworkError
    except (AttributeError, NoArtworkError, mutagen.MutagenError, TypeError):
        return None
    return pixmap


def get_default_artwork_pixmap(default_type: str) -> QPixmap:
    root = get_project_root(__file__)
    default_type = default_type.lower()
    if default_type in ('album', 'artist', 'composer', 'folder'):
        return QPixmap(os.path.join(root, f"icons/{default_type}.png"))
    return QPixmap(os.path.join(root, "icons/misc.png"))


def get_blurred_pixmap(pixmap: QPixmap) -> QPixmap:
    img = pixmap.toImage()
    buffer = QBuffer()
    buffer.open(QBuffer.OpenModeFlag.ReadWrite)

    img.save(buffer, "JPG")
    pil_im = Image.open(io.BytesIO(buffer.data()))

    blur_img = pil_im.filter(ImageFilter.GaussianBlur(80))

    im2 = blur_img.convert("RGBA")
    data = im2.tobytes("raw", "BGRA")
    qim = QImage(data, blur_img.size[0], blur_img.size[1], QImage.Format.Format_ARGB32)

    return QPixmap.fromImage(qim)
