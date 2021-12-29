import io
import sys

from PIL import Image
from PyQt6 import QtWidgets
from PyQt6.QtCore import QBuffer
from PyQt6.QtGui import QPixmap
from mutagen.id3 import ID3

from tag_manager import TagManager

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # mainWindow = MainWindowUi()
    # mainWindow.show()
    pixmap = QPixmap()

    tm = TagManager()

    file_id3 = ID3("/home/matey/Music/03 Ice in My Veins.mp3")
    artwork = file_id3.getall("APIC")[0]
    print(type(artwork.data))
    pixmap.loadFromData(artwork.data)
    print("AAA")
    buffer = QBuffer()
    buffer.readData(pixmap)
    pixmap.save(buffer, "PNG")
    image = Image.open(io.BytesIO(buffer.data()))
    image.show()
    sys.exit(app.exec())
