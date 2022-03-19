from typing import List, Any

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QPixmap, QBrush, QPen, QPainter
from PyQt6.QtWidgets import QTableView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QStyledItemDelegate, \
    QStyle, QStyleOptionViewItem, QApplication, QAbstractItemView

from constants import *
from data_models.track import Track
from utils import ElidedLabel, format_seconds, get_artwork_pixmap


class InformationTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self.table_view = parent
        self._tracks: List[Track] = []
        self._playing_track_index = None

        self.loaded_tracks_num = 0
        self.loaded_pixmap_mapping = {}

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self._tracks:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignTop

        if role == Qt.ItemDataRole.DecorationRole:
            # return None
            if not index.column():
                if index.row() not in self.loaded_pixmap_mapping:
                    artwork_pixmap = get_artwork_pixmap(self._tracks[index.row()].file_path)
                    if not artwork_pixmap:
                        artwork_pixmap = QPixmap(f"icons/album.png")
                    self.loaded_pixmap_mapping[index.row()] = artwork_pixmap
                else:
                    artwork_pixmap = self.loaded_pixmap_mapping[index.row()]
                    # artwork_pixmap = artwork_pixmap if artwork_pixmap else QPixmap(f"icons/album.png")
                # icon = QIcon(artwork_pixmap)
                # icon.addPixmap(artwork_pixmap, QtGui.QIcon.Mode.Selected)
                return artwork_pixmap

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self._tracks)

    def columnCount(self, index: QModelIndex = QModelIndex) -> int:
        return 2

    def set_tracks(self, tracks: List[Track]) -> None:
        self.loaded_pixmap_mapping = {}
        self.layoutAboutToBeChanged.emit()
        self._tracks = tracks
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))

    def set_currently_playing_track_index(self, index: int) -> None:
        self._playing_track_index = index


class InformationTableItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self._table_view: QTableView = parent
        self._tracks: List[Track] = []
        self._playing_track_index = None
        self.is_playing = False
        # self.loaded_pixmap_indexes = []
        self.track_info_widgets_mapping = {}

        self.pixmap_width = 16
        self.pixmap_height = 16

        self.playing_pixmap = QPixmap("icons/speaker_playing.png").scaled(self.pixmap_width, self.pixmap_height,
                                                                          Qt.AspectRatioMode.IgnoreAspectRatio,
                                                                          Qt.TransformationMode.SmoothTransformation)
        self.paused_pixmap = QPixmap("icons/speaker_muted.png").scaled(self.pixmap_width, self.pixmap_height,
                                                                       Qt.AspectRatioMode.IgnoreAspectRatio,
                                                                       Qt.TransformationMode.SmoothTransformation)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        if option.state & QStyle.StateFlag.State_Selected:
            if self._table_view.hasFocus():
                fill_color = SELECTION_QCOLOR
                border_color = SELECTION_QCOLOR_BORDER
            else:
                fill_color = LOST_FOCUS_QCOLOR
                border_color = fill_color
            painter.setBrush(fill_color)
            painter.drawRect(option.rect)
            painter.setPen(QPen(QBrush(border_color), 1))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            # if index.row() == self._table_view.selectedIndexes()[-1].row():  # might be ruining performance
            #     painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))
        # painter.drawRect(option.rect)

        if index.data(Qt.ItemDataRole.DecorationRole):
            decoration_value = index.data(Qt.ItemDataRole.DecorationRole)
            rect = option.rect
            rect.setRect(rect.left() + 2, rect.top() + 2,
                         rect.width() - 4, rect.height() - 4)

            pixmap = decoration_value.scaled(rect.width(), rect.width(),
                                             Qt.AspectRatioMode.IgnoreAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)

            painter.drawPixmap(rect, pixmap)

        if index.column() == 1:
            main_part_rect = option.rect

            if index.row() not in self.track_info_widgets_mapping:
                track = self._tracks[index.row()]
                track_info_widget = TrackInfoWidget(track.title,
                                                    track.artist,
                                                    format_seconds(track.length))
                self.track_info_widgets_mapping[index.row()] = track_info_widget
            else:
                track_info_widget = self.track_info_widgets_mapping[index.row()]

            if index.row() == self._playing_track_index:
                vertical_offset = 4
                bottom_right = QPoint(main_part_rect.left() + self.pixmap_width, main_part_rect.top() +
                                      self.pixmap_height + vertical_offset)
                top_left = QPoint(main_part_rect.left(), main_part_rect.top() + vertical_offset)
                pixmap_rect = QRect(top_left, bottom_right)
                main_part_rect.setLeft(main_part_rect.left() + self.pixmap_width)
                if self.is_playing:
                    painter.drawPixmap(pixmap_rect, self.playing_pixmap)
                else:
                    painter.drawPixmap(pixmap_rect, self.paused_pixmap)

            track_info_widget.setGeometry(main_part_rect)

            painter.save()
            painter.translate(main_part_rect.x(), main_part_rect.y())
            track_info_widget.render(painter)
            painter.restore()

    def set_tracks(self, tracks: List[Track]) -> None:
        self.track_info_widgets_mapping = {}
        self._tracks = tracks

    def set_currently_playing_track_index(self, index: int) -> None:
        self._playing_track_index = index


class InformationTableView(QTableView):
    set_new_tracks = pyqtSignal()
    track_clicked = pyqtSignal(Track, int)
    track_double_clicked = pyqtSignal(Track, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_model = InformationTableModel(self)
        self._table_delegate = InformationTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)
        self._tracks: List[Track] = []

        self.clicked.connect(lambda index: self.track_clicked.emit(self._tracks[index.row()], index.row()))
        self.doubleClicked.connect(lambda index: self.track_double_clicked.emit(self._tracks[index.row()], index.row()))

    def set_tracks(self, tracks: List[Track]) -> None:
        self._table_model.set_tracks(tracks)
        self._table_delegate.set_tracks(tracks)
        self._tracks = tracks
        self.set_new_tracks.emit()

    def set_currently_playing_track_index(self, index: int) -> None:
        self._table_delegate.is_playing = True
        self._table_model.set_currently_playing_track_index(index)
        self._table_delegate.set_currently_playing_track_index(index)
        # print("Currently playing:", index)
        # print("Bottom index:", self.rowAt(self.height()))
        if self.rowAt(self.rect().height()) == index:
            self.scrollTo(self._table_model.index(index - 2, 0), QAbstractItemView.ScrollHint.PositionAtTop)

        self.viewport().repaint()

    def set_paused(self) -> None:
        self._table_delegate.is_playing = False
        self.viewport().repaint()

    def set_unpaused(self) -> None:
        self._table_delegate.is_playing = True
        self.viewport().repaint()

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        if QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton:
            self.clearSelection()
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        return super().focusOutEvent(event)


class TrackInfoWidget(QWidget):
    def __init__(self, title: str, artist: str, duration: str, parent=None):
        super().__init__(parent)
        print("CREATED")
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 0, 4, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.v_layout.setSpacing(0)
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        self.id = f"{title}{artist}{duration}"

        title_label = ElidedLabel(title)
        title_label.setContentsMargins(0, 0, 0, 0)
        # title_label.setStyleSheet("background-color: red")
        # title_label.setFixedHeight(20)

        dur_label = QLabel(duration)
        # dur_label.setStyleSheet("background-color: green")
        dur_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        dur_label.setContentsMargins(0, 0, 0, 0)
        dur_label.setMinimumHeight(20)
        dur_label.setFixedWidth(30)

        self.h_layout.addWidget(title_label, Qt.AlignmentFlag.AlignLeft)
        self.h_layout.addWidget(dur_label)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.upper_widget = QWidget()
        self.upper_widget.setContentsMargins(0, 0, 0, 0)
        self.upper_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        self.upper_widget.setLayout(self.h_layout)

        artist_label = ElidedLabel(artist if artist else "")
        # artist_label.setStyleSheet("background-color: blue")
        artist_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.v_layout.addWidget(self.upper_widget)
        self.v_layout.addWidget(artist_label)

        self.main_widget_part = QWidget()
        self.main_widget_part.setLayout(self.v_layout)

        self.image_label = QLabel()
        self.image_label.setFixedWidth(20)
        self.image_label.resize(0, 20)

        self.main_horizontal_layout = QHBoxLayout(self)
        self.main_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        # self.main_horizontal_layout.addWidget(self.image_label)
        self.main_horizontal_layout.addWidget(self.main_widget_part)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setStyleSheet("background:transparent;")
