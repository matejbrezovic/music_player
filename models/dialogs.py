import os
from typing import Union

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QWidget, \
    QTreeWidgetItem, QTreeWidget

from utils import *


class ScanFoldersDialog(QDialog):
    # noinspection PyTypeChecker
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Folders for New Files")
        self.setFixedSize(700, 400)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_frame")
        self.main_frame.setStyleSheet("QFrame#main_frame {border: 1px solid rgba(0, 0, 0, 0.3)}")

        self.choose_folders_button = QPushButton("Choose Folders")
        self.choose_folders_button.clicked.connect(lambda: SelectFoldersDialog().exec())
        self.selected_folders_scroll_area = QScrollArea()
        self.selected_folders_widget = QWidget()
        self.selected_folders_scroll_area.setWidget(self.selected_folders_widget)
        self.selected_folders_scroll_area.setWidgetResizable(True)
        self.selected_folders_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.selected_folders_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.proceed_button = QPushButton("Proceed")
        self.close_button = QPushButton("Close")

        self.main_layout.addWidget(self.main_frame)
        self.vertical_layout = QVBoxLayout(self.main_frame)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.top_horizontal_widget = QWidget()
        self.top_horizontal_layout = QHBoxLayout(self.top_horizontal_widget)
        self.top_horizontal_layout.setContentsMargins(0, 0, 0, 0)

        self.top_horizontal_layout.addWidget(QLabel("Scan for new files in the following folders:"))
        self.top_horizontal_layout.addStretch()
        self.top_horizontal_layout.addWidget(self.choose_folders_button)

        self.vertical_layout.addWidget(self.top_horizontal_widget)
        self.vertical_layout.addWidget(self.selected_folders_scroll_area)


class SelectFoldersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Folders...")
        self.setFixedSize(500, 800)
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
        self.scroll_area.setFixedHeight(700)
        self.scroll_area.setStyleSheet("border: none")

        self.info_label = QLabel("Select folders containing music to add to the library")
        self.info_label.setStyleSheet("color: rgba(0, 0, 0, 0.4)")
        self.info_label.setFixedHeight(20)

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        self.main_layout.addWidget(self.main_frame)
        self.vertical_layout = QVBoxLayout(self.main_frame)
        self.vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bottom_horizontal_layout = QHBoxLayout()

        self.bottom_horizontal_layout.addWidget(self.ok_button)
        self.bottom_horizontal_layout.addWidget(self.cancel_button)
        self.bottom_horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(self.bottom_horizontal_layout)

        self.vertical_layout.addWidget(self.info_label)
        self.vertical_layout.addWidget(self.scroll_area)
        self.vertical_layout.addWidget(QHLine())
        self.vertical_layout.addWidget(self.bottom_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

    def load_immediate_directory_dir_tree_widget(self, path, tree: Union[QTreeWidget, QTreeWidgetItem]):
        if isinstance(tree, (self.DirectoryItem, self.PlaceholderItem)) \
                and (not tree.child(0) or not isinstance(tree.child(0), self.PlaceholderItem)):
            return
        try:
            self._is_user_action = False
            if isinstance(tree, self.DirectoryItem):
                tree.takeChild(0)
            for element in [x for x in os.listdir(path) if os.path.isdir(path + ("/" if path != "/" else "") + x)]:
                path_info = path + ("/" if path != "/" else "") + element
                new_item = self.DirectoryItem(tree, [os.path.basename(element)], full_path=path_info)
                new_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                new_item.setCheckState(0, Qt.CheckState.Unchecked if isinstance(tree, QTreeWidget) else
                                       (Qt.CheckState.Checked if tree.checkState(0) == Qt.CheckState.Checked else
                                        Qt.CheckState.Unchecked))
                self.PlaceholderItem(new_item)
        except PermissionError:
            pass
        self._is_user_action = True

    def tree_item_clicked(self, item):
        self.load_immediate_directory_dir_tree_widget(item.full_path, item)

    def tree_item_changed(self, item):
        def change_parents_checked_state(item):
            for parent in item.get_parents():
                parent.setCheckState(0, parent.get_all_children_state())

        def change_children_checked_state(item):
            for child in item.get_children():
                child.setCheckState(0, item.checkState(0))

        if not self._is_user_action:
            return

        # for child in item.get_children():
        #     print(child.text(0))

        self._is_user_action = False
        change_children_checked_state(item)
        change_parents_checked_state(item)
        self._is_user_action = True

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

        def get_parents(self):
            parents = []
            item = self
            while True:
                try:
                    item = item.parent()
                    parents.append(item)
                except AttributeError:
                    break
            return parents[:-1]

        def get_all_children_state(self):
            state = self.child(0).checkState(0)
            for child in self.get_children():
                if child.checkState(0) != state:
                    return Qt.CheckState.PartiallyChecked
            return state

    class PlaceholderItem(DirectoryItem):
        def __init__(self, parent):
            super().__init__(parent, ["/"])
