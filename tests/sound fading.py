import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStyle

from audio_player import AudioPlayer


class MainWindowUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._setup_ui()

        self.setWindowTitle('sound fading')
        self.setGeometry(100, 100, 100, 100)

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.player = AudioPlayer()
        self.user_action = -1  # 0 - stopped, 1 - playing, 2 - paused
        self.play_button = QPushButton()
        self.play_button.clicked.connect(self.play_pause_button_clicked)

        self.play_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.pause_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        self.play_button.setIcon(self.play_icon)

        self.central_widget_layout.addWidget(self.play_button)

    def play(self):
        print("Play")
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.player.setSource(QUrl("/home/matey/Music/Remembrance.ogg"))
        self.player.play()

    def pause(self):
        print("Pause")
        self.play_button.setIcon(self.play_icon)
        self.user_action = 2
        self.player.pause()

    def unpause(self):
        print("Unpause")
        self.play_button.setIcon(self.pause_icon)
        self.user_action = 1
        self.player.play()

    def play_pause_button_clicked(self):
        if self.user_action <= 0:
            self.play()
        elif self.user_action == 1:
            self.pause()
        elif self.user_action == 2:
            self.unpause()


# class AudioPlayer(QMediaPlayer):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.audio_output = QAudioOutput()
#         self.setAudioOutput(self.audio_output)
#         self.audioOutput().setVolume(0.3)
#         self.current_volume = self.audio_output.volume()
#
#     def play(self):
#         super().play()
#
#     def pause(self):
#         super().pause()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindowUi()
    mainWindow.show()

    sys.exit(app.exec())
