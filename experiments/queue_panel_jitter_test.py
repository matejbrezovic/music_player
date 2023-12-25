from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QAbstractItemView, QHeaderView, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QModelIndex


class MusicPlayer(QMainWindow):
    track_changed_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Music Player")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.table_view = MusicTable(self)
        self.layout.addWidget(self.table_view)

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.start_playing)
        self.layout.addWidget(self.play_button)

        self.model = self.create_table_model()
        self.table_view.setModel(self.model)

        # Simulate music track changes with a timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_timeout)
        self.timer.start(2000)  # Change track every 5 seconds

        # Store the currently playing row
        self.current_playing_row = -1

    def create_table_model(self):
        model = QStandardItemModel(5, 3, self)

        for row in range(100):
            for column in range(3):
                item = QStandardItem(f"Track {row + 1}-{column + 1}")
                model.setItem(row, column, item)

        return model

    def start_playing(self):
        # Simulate the start of a new track
        new_playing_row = (self.current_playing_row + 1) % self.model.rowCount()

        # Emit a signal indicating the start of a new track
        self.track_changed_signal.emit(new_playing_row)

        self.current_playing_row = new_playing_row

    def on_timer_timeout(self):
        self.start_playing()


class MusicTable(QTableView):
    def __init__(self, parent):
        super().__init__(parent)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Connect the signal from the MusicPlayer to the slot for track changes
        parent.track_changed_signal.connect(self.handle_track_changed)

    def handle_track_changed(self, new_playing_row):
        print(new_playing_row)
        # Scroll to a position 2 rows below the top
        index = self.model().index(new_playing_row, 0)
        if new_playing_row > 2:
            index = self.model().index(new_playing_row - 2, 0)
        self.scrollTo(index,
                      QAbstractItemView.ScrollHint.PositionAtTop)
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtTop)

        # Add "PLAYING" beside the playing track
        for row in range(self.model().rowCount()):
            item = self.model().item(row, 0)
            if item is not None:
                item.setText(f"Track {row + 1}")

        playing_item = self.model().item(new_playing_row, 0)
        if playing_item is not None:
            playing_item.setText(f"Track {new_playing_row + 1} - PLAYING")

        # Redraw the viewport to update the speaker indicator
        self.viewport().update()


if __name__ == '__main__':
    app = QApplication([])
    window = MusicPlayer()
    window.show()
    app.exec()