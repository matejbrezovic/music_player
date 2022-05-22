import sys

from PyQt6 import QtWidgets

from utils import TagManager

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    tm = TagManager()

    f = tm.load_file("/home/matey/Music/04 Sound of Silence (Subnautica_ Below Zero).mp3")
    length = f["#channels"]
    print(length)

    sys.exit(app.exec())
