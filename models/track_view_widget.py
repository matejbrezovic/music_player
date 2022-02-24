from typing import List

from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize, QEvent, QModelIndex
from PyQt6.QtWidgets import *

from data_models.track import Track
from models.track_table_view import TrackTableView
from utils import *


# class MyHeaderView(QtWidgets.QHeaderView):
#     def __init__(self,parent):
#         QtWidgets.QHeaderView.__init__(self, Qt.Orientation.Horizontal, parent)
#         self.sectionResized.connect(self.myresize)
#
#     def myresize(self, *args):
#         '''Resize while keep total width constant'''
#
#         # keep a copy of column widths
#         ws = []
#         for c in range(self.count()):
#             wii = self.sectionSize(c)
#             ws.append(wii)
#
#         if args[0]>0 or args[0]<self.count():
#             for ii in range(args[0],self.count()):
#                 if ii==args[0]:
#                     # resize present column
#                     self.resizeSection(ii,args[2])
#                 elif ii==args[0]+1:
#                     # if present column expands, shrink the one to the right
#                     self.resizeSection(ii,ws[ii]-(args[2]-args[1]))
#                 else:
#                     # keep all others as they were
#                     self.resizeSection(ii,ws[ii])
#
#     def resizeEvent(self, event):
#         """Resize table as a whole, need this to enable resizing"""
#
#         super(QtWidgets.QHeaderView, self).resizeEvent(event)
#         self.setSectionResizeMode(1,QtWidgets.QHeaderView.ResizeMode.Stretch)
#         for column in range(self.count()):
#             self.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.Stretch)
#             width = self.sectionSize(column)
#             self.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.Interactive)
#             self.resizeSection(column, width)
#
#         return

class TestHeaderView(QHeaderView):
    def __init__(self, *args):
        super().__init__(*args)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setStretchLastSection(True)
        self.setCascadingSectionResizes(True)
        self.sectionResized.connect(self.section_resized)
        self.old_width = self.width()

    def section_resized(self, logical_index, old_size, new_size):
        print(logical_index, old_size, new_size)
        count = 7  # self.model().columnCount()
        length = self.width()
        sum = self.length()
        # print(length, sum)

        # if sum != length:
        #     self.resizeSection(logical_index, old_size)
        #     if logical_index < count:
        #         next_header_size = self.sectionSize(logical_index + 1)
        #         if next_header_size > (sum - length):
        #             self.resizeSection(logical_index + 1, next_header_size - (sum - length))
        #         else:
        #             self.resizeSection(logical_index, old_size)

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        # old_width = self.width()
        super().resizeEvent(e)
        for i in range(7):
            self.resizeSection(i, self.sectionSize(i) * self.width() // self.old_width)
        self.old_width = self.width()

    def get_section_sizes(self):
        return [self.sectionSize(i) for i in range(7)]

class TrackViewWidget(QFrame):
    track_double_clicked = pyqtSignal(Track)
    track_clicked = pyqtSignal(Track)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayed_tracks: List[Track] = []
        self.loaded_displays = {}
        self.default_stylesheet = ""
        self.selected_row_index = 0
        self.playing_track = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.header_splitter = HeaderSplitter()
        self.header_splitter.setOrientation(Qt.Orientation.Horizontal)
        self.header_splitter.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.header_splitter.setHandleWidth(2)
        # self.header_splitter.resized.connect(self.update_column_width)
        # self.header_splitter.splitterMoved.connect(self.update_column_width)
        self.header_splitter.setStyleSheet("QSplitter::handle{background: red;}")

        self.column_names = ["", "", "Artist", "Title", "Album", "Year", "Genre"]

        for column_name in self.column_names:
            widget = ElidedLabel("" + column_name)
            widget.setMinimumWidth(20)
            self.header_splitter.addWidget(widget)

        self.table_view = TrackTableView(self)
        test_header = TestHeaderView(Qt.Orientation.Horizontal)
        # test_header.setSize
        self.table_view.setHorizontalHeader(test_header)
        # self.table_view.installEventFilter(self)
        # header_view = MyHeaderView(self.table_vie x
        # ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0w)
        # header_view.setMaximumWidth(self.width())
        # self.table_view.setHorizontalHeader(header_view)
        # self.table_view.horizontalHeader().setMaximumWidth(600)
        # self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # self.table_view.horizontalHeader().setCascadingSectionResizes(True)
        # self.table_view.horizontalHeader().setSectionResizeMode(len(self.column_names) - 1, QHeaderView.ResizeMode.Stretch)
        # self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        # self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        # self.table_view.horizontalHeader().setStretchLastSection(True)
        # self.table_view.horizontalHeader().setMaximumWidth(500)
        # self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # self.table_view.horizontalHeader().setMinimumSectionSize(20)
        self.table_view.verticalHeader().setVisible(False)
        # self.table_view.horizontalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        # self.table_view.horizontalHeader().setStretchLastSection(True)
        # self.res
        self.table_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_view.setIconSize(QSize(22, 22))
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.set_new_tracks.connect(self.update_column_width)

        self.table_view.clicked.connect(lambda model_index: self.track_clicked.emit(
                                                            self.displayed_tracks[model_index.row()]))
        self.table_view.doubleClicked.connect(lambda model_index: self.track_double_clicked.emit(
                                                                  self.displayed_tracks[model_index.row()]))

        self.table_view.setStyleSheet(SELECTION_STYLESHEET)

        self._focus_frame = FocusFrame(self.table_view)
        self._focus_frame.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        first_col_width = 26
        second_col_width = 16
        self.header_splitter.setCollapsible(0, False)
        self.header_splitter.setCollapsible(1, False)
        self.header_splitter.widget(0).setFixedWidth(first_col_width)
        self.header_splitter.widget(1).setFixedWidth(second_col_width)
        # self.table_view.setColumnWidth(0, first_col_width)
        self.table_view.horizontalHeader().resizeSection(0, first_col_width)
        self.table_view.horizontalHeader().resizeSection(1, second_col_width)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)

        self.main_layout.addWidget(self.header_splitter)
        self.main_layout.addWidget(self._focus_frame)

    # def double_clicked(self, new_index: int) -> None:
    #     # global_timer.timer_init()
    #     # global_timer.start()
    #     self.track_double_clicked.emit(self.displayed_tracks[new_index])
    #     # self.set_selected_row_index(self.table_widget.row(item))

    # def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
    #     super().resizeEvent(a0)
    #     # self.table_view.viewport().setMaximumWidth(200)
    #     self.table_view.setMaximumWidth(self.width())
    #     self.table_view.horizontalHeader().setMaximumWidth(200)
        # self.table_view.horizontalHeader().setMax

    # def eventFilter(self, obj, event):
    #     self.last_baseColumnSize = self.table_view.columnWidth(6)
    #     if obj is self.table_view and event.type() == QEvent.Type.Resize:
    #         hub = self.table_view.horizontalHeader()
    #         fixedSizes = self.table_view.verticalHeader().width()
    #         fixedSizes += len(self.column_names) + 1  # Borders
    #         if (self.table_view.verticalScrollBar().isVisible()):
    #             fixedSizes += self.table_view.verticalScrollBar().width()
    #         tmp = [x for x in range(len(self.column_names)) if hub.sectionResizeMode(x) != QHeaderView.ResizeMode.Fixed]
    #
    #         for i in range(len(self.column_names) - 1):
    #             if hub.sectionResizeMode(i) == QHeaderView.ResizeMode.Fixed:
    #                 fixedSizes += self.table_view.columnWidth(i)
    #         if hub.sectionResizeMode(len(self.column_names) - 1) == QHeaderView.ResizeMode.Fixed:
    #             fixedSizes += self.last_baseColumnSize
    #
    #         newsize = max(20, (event.size().width() - fixedSizes) / len(tmp))
    #         for i in tmp:
    #             self.table_view.setColumnWidth(i, newsize)
    #     return False

    def update_column_width(self) -> None:
        total_sizes = sum(self.header_splitter.sizes())
        if not total_sizes:
            return
        for i in range(len(self.column_names)):
            self.table_view.setColumnWidth(i, int(self.header_splitter.sizes()[i] / total_sizes * self.width()))

    def set_tracks(self, tracks: List[Track]) -> None:
        self.table_view.set_tracks(tracks)
        self.displayed_tracks = tracks
        index = self.displayed_tracks.index(self.playing_track) if self.playing_track in self.displayed_tracks else None
        self.table_view.set_playing_track_index(index)

    def set_selected_row_index(self, index: int) -> None:
        self.selected_row_index = index

    def select_row_by_index(self, index: int) -> None:
        self.table_view.selectRow(index)
        self.set_selected_row_index(index)

    def select_row_by_track(self, track: Track) -> None:
        if track not in self.displayed_tracks:
            self.table_view.clearSelection()
            return
        self.select_row_by_index(self.displayed_tracks.index(track))

    def set_playing_track(self, track: Track) -> None:
        if track not in self.displayed_tracks:
            return
        self.playing_track = track
        self.table_view.set_playing_track_index(self.displayed_tracks.index(track))
        self.table_view.set_unpaused()

    def pause_playing_track(self) -> None:
        self.table_view.set_paused()

    def unpause_playing_track(self) -> None:
        self.table_view.set_unpaused()
