import sys

from PyQt6 import QtWidgets

from tag_manager import TagManager

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    tm = TagManager()

    f = tm.load_file("/home/matey/Music/06 Below Zero.mp3")
    length = int(f["#length"])
    print(length)

    sys.exit(app.exec())
