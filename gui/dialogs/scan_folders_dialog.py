from __future__ import annotations

import os
import sys
from collections import defaultdict
from typing import List, Tuple, Union

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (QPushButton, QScrollArea, QTreeWidgetItem, QTreeWidget, QSpacerItem, QHBoxLayout,
                             QVBoxLayout, QDialog, QFrame, QGridLayout, QWidget, QLabel, QSizePolicy, QApplication)

from constants import DEFAULT_CONFIG_PATH, SUPPORTED_AUDIO_FORMATS
from repositories.cached_tracks_repository import CachedTracksRepository
from utils import delete_grid_layout_items, PathCheckbox, QHLine, Config


class ScanFoldersDialog(QDialog):
    added_tracks = pyqtSignal(list)
    removed_tracks = pyqtSignal(list)

    # noinspection PyTypeChecker
    def __init__(self, *args):
        super().__init__(*args)

        self.setWindowFlag(Qt.WindowType.CustomizeWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowTitleHint, True)
        self.setWindowFlag(Qt.WindowType.WindowSystemMenuHint, False)

        self.setWindowTitle("Scan Folders for New Files")
        self.setFixedSize(700, 400)
        self.selected_folders: List[str] = []
        self.checked_folders: List[str] = []
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.cached_tracks_repository = CachedTracksRepository()

        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_frame")
        self.main_frame.setStyleSheet("QFrame#main_frame {border: 1px solid rgba(0, 0, 0, 0.3)}")

        self.select_folders_dialog = SelectFoldersDialog(tuple(self.checked_folders))
        self.select_folders_dialog.folders_selected.connect(self.update_selected_folders)

        self.choose_folders_button = QPushButton("Choose Folders")

        self.choose_folders_button.clicked.connect(lambda: (self.select_folders_dialog.set_preselected_folders(
                                                            self.checked_folders), self.select_folders_dialog.exec()))
        self.selected_folders_scroll_area = QScrollArea()
        self.selected_folders_widget = QWidget()
        self.selected_folders_widget_grid_layout = QGridLayout(self.selected_folders_widget)
        self.selected_folders_widget_grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.selected_folders_scroll_area.setWidget(self.selected_folders_widget)
        self.selected_folders_scroll_area.setWidgetResizable(True)
        self.selected_folders_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.selected_folders_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.proceed_button = QPushButton("Proceed")
        self.proceed_button.clicked.connect(self.proceed_button_clicked)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(lambda: self.done(0))

        self.choose_folders_button.setAutoDefault(False)
        self.proceed_button.setAutoDefault(False)
        self.close_button.setAutoDefault(False)

        self.main_layout.addWidget(self.main_frame)
        self.vertical_layout = QVBoxLayout(self.main_frame)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.top_horizontal_widget = QWidget()
        self.top_horizontal_layout = QHBoxLayout(self.top_horizontal_widget)
        self.top_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.top_horizontal_layout.addWidget(QLabel("Scan for new files in the following folders:"))
        self.top_horizontal_layout.addStretch()
        self.top_horizontal_layout.addWidget(self.choose_folders_button)

        self.bottom_horizontal_widget = QWidget()
        self.bottom_horizontal_layout = QHBoxLayout(self.bottom_horizontal_widget)
        self.bottom_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bottom_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_horizontal_layout.addWidget(self.proceed_button)
        self.bottom_horizontal_layout.addWidget(self.close_button)

        self.vertical_layout.addWidget(self.top_horizontal_widget)
        self.vertical_layout.addWidget(self.selected_folders_scroll_area)
        self.vertical_layout.addWidget(self.bottom_horizontal_widget)

        config = Config()
        config.load(DEFAULT_CONFIG_PATH)
        self.update_selected_folders(config.get_setting("preselected_folders"))

    def exec(self) -> None:
        # must return None, not int
        super().exec()

    def proceed_button_clicked(self) -> None:
        config = Config()
        config.load(DEFAULT_CONFIG_PATH)
        config.set_setting("preselected_folders", self.checked_folders)
        config.save(DEFAULT_CONFIG_PATH)

        found_file_paths = defaultdict(list)
        for folder in self.checked_folders:
            for root, _, files in os.walk("C:" + folder):
                for file in files:
                    if os.path.splitext(file)[-1] in SUPPORTED_AUDIO_FORMATS:
                        found_file_paths[root.replace("\\", "/")].append(
                            f"{root}/{file}".replace("\\", "/").replace("//", "/"))

        tracks_added, tracks_removed = [], []

        for dir_root, file_paths in found_file_paths.items():
            added, removed = self.cached_tracks_repository.update_tracks_by_folder(dir_root, file_paths)
            tracks_added += added
            tracks_removed += removed

        self.cached_tracks_repository.delete_cache()
        self.cached_tracks_repository.load_cache()

        self.added_tracks.emit(tracks_added)
        self.removed_tracks.emit(tracks_removed)

        config = Config()
        config.load(DEFAULT_CONFIG_PATH)
        self.update_selected_folders(config.get_setting("preselected_folders"))

        self.done(0)

    def checkbox_state_changed(self, is_checked: bool, checkbox_path: str) -> None:
        if is_checked:
            self.checked_folders.append(checkbox_path)
        else:
            self.checked_folders.remove(checkbox_path)
        if not self.checked_folders:
            self.proceed_button.setEnabled(False)
        else:
            self.proceed_button.setEnabled(True)

    def update_selected_folders(self, paths: List[str]) -> None:
        delete_grid_layout_items(self.selected_folders_widget_grid_layout)
        self.selected_folders = []
        self.checked_folders = []
        if not paths:
            self.proceed_button.setEnabled(False)
            return
        self.proceed_button.setEnabled(True)
        for i, folder_path in enumerate(paths):
            checkbox = PathCheckbox()
            checkbox.setCheckState(Qt.CheckState.Checked)
            checkbox.set_path(folder_path)
            checkbox.state_changed.connect(self.checkbox_state_changed)

            self.selected_folders_widget_grid_layout.addWidget(checkbox, i, 0)
            self.selected_folders_widget_grid_layout.addWidget(QLabel(folder_path), i, 1)
            if folder_path not in self.selected_folders:
                self.selected_folders.append(folder_path)
                self.checked_folders.append(folder_path)
        self.selected_folders_widget_grid_layout.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum,
                                                                     QSizePolicy.Policy.Expanding))


class SelectFoldersDialog(QDialog):
    folders_selected = pyqtSignal(list)

    def __init__(self, preselected_folders: Tuple[str] = ()):
        super().__init__()

        self.setWindowFlag(Qt.WindowType.CustomizeWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowTitleHint, True)
        self.setWindowFlag(Qt.WindowType.WindowSystemMenuHint, False)

        self.setWindowTitle("Choose Folders...")
        self.setFixedSize(500, 600)
        self.preselected_folders = preselected_folders
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_frame")
        self.main_frame.setStyleSheet("QFrame#main_frame {border: 1px solid rgba(0, 0, 0, 0.3)}")

        self._is_user_action = True
        self.dir_tree_widget = QTreeWidget()
        self.dir_tree_widget.itemClicked.connect(self.tree_item_clicked)
        self.dir_tree_widget.itemExpanded.connect(self.tree_item_clicked)
        self.dir_tree_widget.itemChanged.connect(self.tree_item_changed)
        self.dir_tree_widget.setAnimated(False)
        self.dir_tree_widget.setSortingEnabled(True)
        self.dir_tree_widget.setSortingEnabled(False)
        self.dir_tree_widget.setHeaderHidden(True)
        self.dir_tree_widget.setIndentation(20)
        self.dir_tree_widget.setContentsMargins(0, 0, 0, 0)
        self.dir_tree_widget.setStyleSheet("border: none")
        self.dir_tree_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dir_tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.load_immediate_directory_dir_tree_widget("/", self.dir_tree_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.dir_tree_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFixedHeight(500)
        self.scroll_area.setStyleSheet("border: none")

        self.info_label = QLabel("Select folders containing music to add to the library")
        self.info_label.setContentsMargins(5, 4, 4, 5)
        self.info_label.setStyleSheet("color: rgba(0, 0, 0, 0.4)")
        self.info_label.setFixedHeight(26)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: self.done(0))

        self.main_layout.addWidget(self.main_frame)
        self.vertical_layout = QVBoxLayout(self.main_frame)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bottom_horizontal_layout = QHBoxLayout()

        self.bottom_horizontal_layout.addWidget(self.ok_button)
        self.bottom_horizontal_layout.addWidget(self.cancel_button)
        self.bottom_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bottom_widget = QWidget(self)
        self.bottom_widget.setLayout(self.bottom_horizontal_layout)

        self.vertical_layout.addWidget(self.info_label)
        self.vertical_layout.addWidget(self.scroll_area)
        self.vertical_layout.addWidget(QHLine())
        self.vertical_layout.addWidget(self.bottom_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

    def exec(self) -> None:
        self.select_preselected_folders()
        super().exec()

    def set_preselected_folders(self, preselected_folders: Tuple[str]) -> None:
        valid_folders = []

        for folder in preselected_folders:
            if os.path.isdir(folder):
                valid_folders.append(folder)

        self.preselected_folders = valid_folders

    def select_preselected_folders(self) -> None:
        def get_child_by_text(_item: QTreeWidgetItem, text: str) -> QTreeWidgetItem:
            for child in [_item.child(c) for c in range(_item.childCount())]:
                if child.text(0) == text:
                    return child

        for i in range(self.dir_tree_widget.invisibleRootItem().childCount()):
            item = self.dir_tree_widget.invisibleRootItem().child(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            # noinspection PyTypeChecker
            self.tree_item_changed(item)

        for folder_path in self.preselected_folders:
            path_parts = folder_path.split("/")
            item = self.dir_tree_widget.invisibleRootItem()
            for path_part in path_parts[1:-1]:
                self.load_immediate_directory_dir_tree_widget(item.full_path if isinstance(item, DirectoryItem)
                                                              else "/", item)
                item = get_child_by_text(item, path_part)
                item.setExpanded(True)
            self.load_immediate_directory_dir_tree_widget(item.full_path if isinstance(item, DirectoryItem)
                                                          else "/", item)
            get_child_by_text(item, path_parts[-1]).setCheckState(0, Qt.CheckState.Checked)

    def load_immediate_directory_dir_tree_widget(self, path: str, tree: Union[QTreeWidget, QTreeWidgetItem]) -> None:
        if isinstance(tree, QTreeWidgetItem) \
                and (not tree.child(0) or not isinstance(tree.child(0), PlaceholderItem)):
            return
        try:
            self._is_user_action = False
            if isinstance(tree, DirectoryItem):
                tree.takeChild(0)
            for element in [x for x in os.listdir(path) if os.path.isdir(path + ("/" if path != "/" else "") + x)]:
                path_info = path + ("/" if path != "/" else "") + element
                new_item = DirectoryItem(tree, [os.path.basename(element)], full_path=path_info)
                new_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                new_item.setCheckState(0, Qt.CheckState.Unchecked if isinstance(tree, QTreeWidget) else
                                       (Qt.CheckState.Checked if tree.checkState(0) == Qt.CheckState.Checked else
                                        Qt.CheckState.Unchecked))
                PlaceholderItem(new_item)
        except PermissionError:
            pass
        self._is_user_action = True

    def tree_item_clicked(self, item: QTreeWidgetItem) -> None:
        self.load_immediate_directory_dir_tree_widget(item.full_path, item)

    def tree_item_changed(self, item: DirectoryItem) -> None:
        def change_parents_checked_state(_item: DirectoryItem) -> None:
            for parent in _item.get_parents():
                children_check_state = parent.get_all_children_state()
                parent.setCheckState(0, Qt.CheckState.PartiallyChecked if
                                     children_check_state != Qt.CheckState.Unchecked else Qt.CheckState.Unchecked)

        def change_children_checked_state(_item: DirectoryItem) -> None:
            for child in _item.get_children():
                child.setCheckState(0, item.checkState(0))

        if not self._is_user_action:
            return

        self._is_user_action = False
        change_children_checked_state(item)
        change_parents_checked_state(item)
        self._is_user_action = True

    def ok_button_clicked(self) -> None:
        def get_main_checked_items(parent_item=self.dir_tree_widget.invisibleRootItem()):
            checked_items = []
            for item in [parent_item.child(i) for i in range(parent_item.childCount())]:
                if item.checkState(0) == Qt.CheckState.Checked:
                    checked_items.append(item)
                elif item.checkState(0) == Qt.CheckState.PartiallyChecked:
                    checked_items.extend(get_main_checked_items(item))
            return checked_items

        self.folders_selected.emit([item.full_path for item in get_main_checked_items()])
        self.done(0)


class DirectoryItem(QTreeWidgetItem):
    def __init__(self, *args, full_path=None):
        super().__init__(*args)
        self.full_path = full_path

    def get_children(self):
        children = []
        for i in range(self.childCount()):
            children.append(self.child(i)) if not self.child(i).childCount() \
                else children.extend([self.child(i)] + self.child(i).get_children())
        return children

    def get_parents(self) -> List[DirectoryItem]:
        parents = []
        item = self
        while True:
            try:
                item = item.parent()
                parents.append(item)
            except AttributeError:
                break
        return parents[:-1]

    def get_all_children_state(self) -> Qt.CheckState:
        state = self.child(0).checkState(0)
        for child in self.get_children():
            if child.checkState(0) != state:
                return Qt.CheckState.PartiallyChecked
        return state


class PlaceholderItem(DirectoryItem):
    def __init__(self, parent):
        super().__init__(parent, ["/"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ScanFoldersDialog()
    dialog.show()
    sys.exit(app.exec())
