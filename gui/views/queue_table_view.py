from typing import List, Any, Optional, Union

from PyQt6.QtCore import QModelIndex, pyqtSignal, QRect, QPoint, QTimer, QAbstractTableModel, Qt
from PyQt6.QtGui import QPixmap, QBrush, QPen, QPainter, QFocusEvent, QPalette, QColor
from PyQt6.QtWidgets import (QTableView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QStyledItemDelegate,
                             QStyle, QStyleOptionViewItem, QApplication, QAbstractItemView)

from constants import SELECTION_QCOLOR, LOST_FOCUS_QCOLOR, ROOT
from data_models.track import Track
from utils import ElidedLabel, get_embedded_artwork_pixmap, get_formatted_time_in_mins, get_default_artwork_pixmap


class QueueTableView(QTableView):
    track_double_clicked = pyqtSignal(Track)

    def __init__(self, *args):
        super().__init__(*args)
        self._table_model = QueueTableModel(self)
        self._table_delegate = QueueTableItemDelegate(self)
        self.setModel(self._table_model)
        self.setItemDelegate(self._table_delegate)
        self._playing_track_index = -1

        palette = self.palette()
        palette.setColor(QPalette.ColorGroup.All, QPalette.ColorRole.BrightText, QColor(79, 180, 242))
        self.setPalette(palette)

        self.doubleClicked.connect(lambda index: self.track_double_clicked.emit(self._table_model.tracks[index.row()]))

        self._viewport_fix_timer = QTimer(self)
        self._viewport_fix_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._viewport_fix_timer.setSingleShot(True)
        self._viewport_fix_timer.timeout.connect(self.on_viewport_fix_timeout)

    def set_tracks(self, tracks: List[Track]) -> None:
        self._table_model.set_tracks(tracks)
        self._table_delegate.set_tracks(tracks)

    def on_viewport_fix_timeout(self):
        visible_index_range = range(self.rowAt(4), self.rowAt(self.rect().height()))
        if self._playing_track_index is None:
            self.scrollToTop()
        elif self._playing_track_index not in visible_index_range:
            self.scrollTo(self._table_model.index(self._playing_track_index, 0),
                          QAbstractItemView.ScrollHint.PositionAtTop)
        elif self._playing_track_index in visible_index_range[2:]:
            self.scrollTo(self._table_model.index(self._playing_track_index - 2, 0),
                          QAbstractItemView.ScrollHint.PositionAtTop)
        self.viewport().repaint()

    def set_playing_track(self, track: Optional[Track]) -> None:
        self._table_delegate.is_paused = True if track is None else False

        index = self._table_model.tracks.index(track) if track in self._table_model.tracks else None

        self._playing_track_index = index
        self._table_model.set_playing_track_index(index)
        self._table_delegate.set_playing_track_index(index)
        self._viewport_fix_timer.start(0)

    def set_paused(self) -> None:
        self._table_delegate.is_stopped = False
        self._table_delegate.is_paused = True
        self.viewport().repaint()

    def set_unpaused(self) -> None:
        self._table_delegate.is_stopped = False
        self._table_delegate.is_paused = False
        self.viewport().repaint()

    def stop_playing(self):
        self._table_delegate.is_stopped = True
        self.viewport().repaint()

    def focusInEvent(self, event: QFocusEvent) -> None:
        if QApplication.mouseButtons() & Qt.MouseButton.LeftButton:
            self.clearSelection()
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        return super().focusOutEvent(event)


class QueueTableModel(QAbstractTableModel):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        # self.table_view = parent
        self.tracks: List[Track] = []
        self._playing_track_index = None

        self.loaded_tracks_num = 0
        self.loaded_pixmap_mapping = {}

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if not self.tracks:
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignTop

        if role == Qt.ItemDataRole.DecorationRole:
            if not index.column():
                if index.row() not in self.loaded_pixmap_mapping:
                    artwork_pixmap = get_embedded_artwork_pixmap(self.tracks[index.row()].file_path)
                    if not artwork_pixmap or artwork_pixmap.isNull():
                        artwork_pixmap = get_default_artwork_pixmap("album")
                    self.loaded_pixmap_mapping[index.row()] = artwork_pixmap
                else:
                    artwork_pixmap = self.loaded_pixmap_mapping[index.row()]
                return artwork_pixmap

    def rowCount(self, index: QModelIndex = QModelIndex) -> int:
        return len(self.tracks)

    def columnCount(self, index: QModelIndex = QModelIndex) -> int:
        return 2

    def set_tracks(self, tracks: List[Track]) -> None:
        self.loaded_pixmap_mapping = {}
        self.layoutAboutToBeChanged.emit()
        self.tracks = tracks
        self.layoutChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(),
                                               self.columnCount()))

    def set_playing_track_index(self, index: Optional[int]) -> None:
        self._playing_track_index = index


class QueueTableItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QueueTableView = None):
        super().__init__(parent)
        self._table_view = parent
        self._tracks: List[Track] = []
        self._playing_track_index = None
        self.is_paused = True
        self.is_stopped = True
        self.track_info_widgets_mapping = {}

        self.pixmap_width = 16
        self.pixmap_height = 16

        self.playing_pixmap = QPixmap(f"{ROOT}/icons/speaker-playing.png").scaled(
            self.pixmap_width, self.pixmap_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.paused_pixmap = QPixmap(f"{ROOT}/icons/speaker-not-playing.png").scaled(
            self.pixmap_width, self.pixmap_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        if option.state & QStyle.StateFlag.State_Selected:
            if self._table_view.hasFocus():
                fill_color = SELECTION_QCOLOR
            else:
                fill_color = LOST_FOCUS_QCOLOR
            painter.setBrush(fill_color)
            painter.drawRect(option.rect)

        else:
            painter.setBrush(QBrush(Qt.GlobalColor.white))

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
                track_info_widget = QueueItemWidget(track.title,
                                                    track.artist,
                                                    get_formatted_time_in_mins(track.length))
                self.track_info_widgets_mapping[index.row()] = track_info_widget
            else:
                track_info_widget = self.track_info_widgets_mapping[index.row()]

            if index.row() == self._playing_track_index and not self.is_stopped:
                vertical_offset = 4
                bottom_right = QPoint(main_part_rect.left() + self.pixmap_width, main_part_rect.top() +
                                      self.pixmap_height + vertical_offset)
                top_left = QPoint(main_part_rect.left(), main_part_rect.top() + vertical_offset)
                pixmap_rect = QRect(top_left, bottom_right)
                main_part_rect.setLeft(main_part_rect.left() + self.pixmap_width)
                if not self.is_paused:
                    painter.drawPixmap(pixmap_rect, self.playing_pixmap)
                else:
                    painter.drawPixmap(pixmap_rect, self.paused_pixmap)
                # self._table_view.on_viewport_fix_timeout()

            track_info_widget.setGeometry(main_part_rect)

            painter.save()
            painter.translate(main_part_rect.x(), main_part_rect.y())
            if option.state & QStyle.StateFlag.State_Selected and self._table_view.hasFocus():
                track_info_widget.set_text_colors(option.palette.highlightedText(), option.palette.brightText())
            else:
                track_info_widget.set_text_colors(Qt.GlobalColor.black, Qt.GlobalColor.darkGray)
            track_info_widget.render(painter)
            painter.restore()

    def set_tracks(self, tracks: List[Track]) -> None:
        self.track_info_widgets_mapping = {}
        self._tracks = tracks

    def set_playing_track_index(self, index: Optional[int]) -> None:
        self._playing_track_index = index


class QueueItemWidget(QWidget):
    def __init__(self, title: str, artist: str, duration: str, *args):
        super().__init__(*args)
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 0, 4, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.v_layout.setSpacing(0)
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        self.id = f"{title}{artist}{duration}"

        self.title_label = ElidedLabel(title)
        self.title_label.setContentsMargins(0, 0, 0, 0)

        self.dur_label = QLabel(duration)
        self.dur_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.dur_label.setContentsMargins(0, 0, 0, 0)
        self.dur_label.setMinimumHeight(20)
        self.dur_label.setFixedWidth(40)

        self.h_layout.addWidget(self.title_label, Qt.AlignmentFlag.AlignLeft)
        self.h_layout.addWidget(self.dur_label)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.upper_widget = QWidget()
        self.upper_widget.setContentsMargins(0, 0, 0, 0)
        self.upper_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        self.upper_widget.setLayout(self.h_layout)

        self.artist_label = ElidedLabel(artist or "")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.v_layout.addWidget(self.upper_widget)
        self.v_layout.addWidget(self.artist_label)

        self.main_widget_part = QWidget()
        self.main_widget_part.setLayout(self.v_layout)

        self.main_horizontal_layout = QHBoxLayout(self)
        self.main_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.main_horizontal_layout.addWidget(self.main_widget_part)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_text_colors(self, top: Union[QColor, Qt.GlobalColor, int, str],
                        bottom: Union[QColor, Qt.GlobalColor, int, str]) -> None:
        top = QColor(top)
        bottom = QColor(bottom)

        self.title_label.setStyleSheet(f"color: {top.name()}")
        self.dur_label.setStyleSheet(f"color: {top.name()}")
        self.artist_label.setStyleSheet(f"color: {bottom.name()}")
