import sys

import music_tag
from PyQt6 import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)


    f = music_tag.load_file("/home/matey/Music/04 Sound of Silence (Subnautica_ Below Zero).mp3")
    length = f["#channels"]
    print(length)

    sys.exit(app.exec())
