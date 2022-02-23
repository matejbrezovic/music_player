import sys
from typing import List

from PyQt6.QtWidgets import *

import global_timer
from data_models.track import Track


# class MyTableModel(QtCore.QAbstractTableModel):
#     def __init__(self, data=[[]], parent=None):
#         super().__init__(parent)
#         self.data = data
#
#
#     def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole.DisplayRole):
#         if role == QtCore.Qt.ItemDataRole.DisplayRole:
#             if orientation == Qt.Orientation.Horizontal:
#                 return "Column " + str(section)
#             else:
#                 return "Row " + str(section)
#
#     def columnCount(self, parent=None):
#         return len(self.data[0])
#
#     def rowCount(self, parent=None):
#         return len(self.data)
#
#     def data(self, index: QModelIndex, role: int):
#         if role == QtCore.Qt.ItemDataRole.DisplayRole:
#             row = index.row()
#             col = index.column()
#             return str(self.data[row][col])


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()

        self.setWindowTitle('lazy loading test window')
        self.resize(500, 500)

    def _setup_ui(self) -> None:
        self.central_widget = QWidget(self)
        self.central_widget_layout = QVBoxLayout()
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.central_widget_layout)
        self.setCentralWidget(self.central_widget)

        self.list_view = QListView()
        self.list_model = MyTableModel()
        self.list_view.setModel(self.table_model)
        self.list_view.show()


    def set_playing_tracks(self, tracks: List[Track]) -> None:
        global_timer.timer_init()
        global_timer.start()
        # self.playing_tracks = tracks
        # self.table_widget.clearSelection()
        # self.playing_tracks_table_widget.setRowCount(len(tracks))
        # print(len(tracks))
        # for i, track in enumerate(tracks):
        #     track_group_widget = TrackGroupWidget(track, i)
        #     track_group_widget.clicked.connect(lambda row_index: (self.row_clicked(row_index)))
        #     track_group_widget.double_clicked.connect(self.row_double_clicked)
        #     self.playing_tracks_table_widget.setCellWidget(i, 0, track_group_widget)
        #     self.playing_tracks_table_widget.setRowHeight(i, track_group_widget.height())
        # global_timer.stop()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # mainWindow.show()
    sys.exit(app.exec())
