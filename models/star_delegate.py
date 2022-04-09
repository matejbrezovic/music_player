from PyQt6.QtWidgets import QStyle, QStyledItemDelegate, QTableView

from constants import SELECTION_QCOLOR
from models.star_editor import StarEditor
from models.star_rating import StarRating


class StarDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTableView = None):
        super().__init__(parent)
        self.active_editors = []

    def paint(self, painter, option, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, SELECTION_QCOLOR)
                star_rating.paint(painter, option.rect, option.palette, StarRating, option.palette.base())
            else:
                star_rating.paint(painter, option.rect, option.palette, StarRating)
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            return star_rating.size_hint()
        else:
            return super().sizeHint(option, index)

    def createEditor(self, parent, option, index):
        print("Created editor:", index.row(), index.column())
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            editor = StarEditor(parent, option.palette)
            editor.set_selected_star_count(star_rating.star_count())
        else:
            editor = super().createEditor(parent, option, index)
        self.active_editors.append(editor)
        return editor

    def setEditorData(self, editor: StarEditor, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            editor.set_selected_star_count(star_rating.star_count())
            editor.set_star_rating(star_rating)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: StarEditor, model, index):
        star_rating = index.data()
        if isinstance(star_rating, StarRating):
            print(f"Set model data: {index.row(), index.column()}, rating: {editor.star_rating().star_count()}")
            model.setData(index, editor.star_rating())
        else:
            super().setModelData(editor, model, index)

    def commit_and_close_editors(self):
        """Closes all editors except the last one (if there's more than one editor), otherwise it closes all of them
        (no new editor was opened)"""

        print("Commit and close editors:", self.active_editors)

        editors_to_close = self.active_editors[:-1] if len(self.active_editors) > 1 else self.active_editors
        for editor in editors_to_close:
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)
            editor.deleteLater()
        self.active_editors = [self.active_editors[-1]] if len(self.active_editors) > 1 else []