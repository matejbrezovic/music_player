import random
import string
import sys
from typing import List

from data_models.track import Track
from repositories.tracks_repository import TracksRepository
from utils import *


class TrackViewWidgetWithTable(QFrame):
    track_double_clicked = pyqtSignal(Track)
    track_clicked = pyqtSignal(Track)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks: List[Track] = []
        self.loaded_displays = {}
        self.selected_color = "rgba(175, 193, 244, 0.5)"
        self.selected_row_index = 0
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.header_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.header_splitter.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.header_splitter.setHandleWidth(0)
        self.track_info_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.header_splitter.splitterMoved.connect(self.update_column_width)

        self.column_names = ["Artist", "Title", "Album", "Year", "Genre"]

        for column_name in self.column_names:
            widget = ElidedLabel("   " + column_name)
            widget.setMinimumWidth(20)
            widget.setStyleSheet(f"background-color: rgb({random.randint(50, 200)},{random.randint(50, 200)},{random.randint(50, 200)})")
            self.header_splitter.addWidget(widget)
        print(self.header_splitter.sizes())

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.column_names))
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setShowGrid(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.itemClicked.connect(lambda item: self.track_clicked.emit(item.track))
        self.table_widget.itemDoubleClicked.connect(lambda item: self.track_double_clicked.emit(item.track))

        self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self.table_widget)
        # self.set_tracks(TracksRepository().get_tracks()[:40])

    def update_column_width(self):
        total_sizes = sum(self.header_splitter.sizes())
        for i in range(len(self.column_names)):
            self.table_widget.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))

    def set_tracks(self, tracks: List[Track]):
        self.table_widget.setRowCount(len(tracks))
        self.displayed_tracks = tracks

        for i, track in enumerate(tracks):
            for j in range(len(self.column_names)):
                label_name = getattr(track, self.column_names[j].lower())
                item = QTableWidgetItem()
                item.setText(label_name)
                item.track = track
                self.table_widget.setItem(i, j, item)

    def select_row_by_index(self, index: int):
        self.table_widget.selectRow(index)
        self.selected_row_index = index

    def select_row_by_track(self, track: Track):
        if track not in self.displayed_tracks:
            return
        self.select_row_by_index(self.displayed_tracks.index(track))


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Testing widget'

        self.setWindowTitle(self.title)
        self.resize(1000, 600)

        self.track_view_widget = TrackViewWidgetWithTable()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.button_clicked)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.track_view_widget)
        self.layout.addWidget(self.refresh_button)
        self.setLayout(self.layout)
        # self.track_view_widget.update_column_width()
        self.show()

    def button_clicked(self):
        self.track_view_widget.set_tracks(TracksRepository().get_tracks())

    def generate_tracks(self, num):
        tracks = []
        for i in range(num):
            tracks.append(Track(i,
                                *[(''.join(random.choice(string.ascii_lowercase) for _ in range(10))) for _ in
                                  range(8)]
                                ))
        return tracks


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.track_view_widget.update_column_width()
    sys.exit(app.exec())
