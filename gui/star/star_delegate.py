from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Tuple

from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel, QSize, pyqtSignal
from PyQt6.QtGui import QPen, QColor, QPainter
from PyQt6.QtWidgets import QStyle, QStyledItemDelegate, QWidget, QStyleOptionViewItem

from constants import SELECTION_QCOLOR, LOST_FOCUS_QCOLOR
from gui.star import StarEditor, StarRating
from utils import combine_colors, index_pos

if TYPE_CHECKING:
    from gui.views import TrackTableView


class StarDelegate(QStyledItemDelegate):
    track_rating_updated = pyqtSignal(int, float)  # track index, rating

    def __init__(self, parent: TrackTableView = None):
        super().__init__(parent)
        self.active_editors: Dict[Tuple[int, int], StarEditor] = {}
        self._table_view: TrackTableView = parent

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            if option.state & QStyle.StateFlag.State_Selected:
                if self._table_view.hasFocus():
                    fill_color = SELECTION_QCOLOR
                else:
                    fill_color = LOST_FOCUS_QCOLOR
                painter.setBrush(fill_color)
                painter.drawRect(option.rect)
            if option.state & QStyle.StateFlag.State_Selected:
                if self._table_view.hasFocus():
                    background_stars_color = combine_colors(SELECTION_QCOLOR, option.palette.base(), 0.8)
                    StarRating(5).paint(painter, option.rect, option.palette, StarRating.ReadOnly,
                                        background_stars_color)
                else:
                    background_stars_color = QColor(172, 184, 197)
                    StarRating(5).paint(painter, option.rect, option.palette, StarRating.ReadOnly,
                                        background_stars_color)
                    star_rating.paint(painter, option.rect, option.palette, StarRating, option.palette.text())
            else:
                star_rating.paint(painter, option.rect, option.palette, StarRating)
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            return star_rating.size_hint()
        else:
            return super().sizeHint(option, index)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> StarEditor:
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            editor = StarEditor(parent, option.palette)
            editor.set_star_color(self._table_view.palette().highlightedText().color())
            editor.set_selected_star_count(star_rating.star_count())
            editor.rating_changed.connect(lambda rating: self.track_rating_updated.emit(index.row(), rating))
        else:
            editor = super().createEditor(parent, option, index)
        self.active_editors[index_pos(index)] = editor
        return editor

    def setEditorData(self, editor: StarEditor, index: QModelIndex) -> None:
        star_rating = index.data()
        if isinstance(star_rating, StarRating) and isinstance(editor, StarEditor):
            editor.set_selected_star_count(star_rating.star_count())
            editor.set_star_rating(star_rating)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: StarEditor, model: QAbstractTableModel, index: QModelIndex) -> None:
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            model.setData(index, editor.star_rating())
        else:
            super().setModelData(editor, model, index)

    def commit_and_close_editor(self, index: QModelIndex) -> None:
        if index_pos(index) not in self.active_editors:
            return

        editor = self.active_editors[index_pos(index)]
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)
        editor.deleteLater()
        self.active_editors.pop(index_pos(index))
