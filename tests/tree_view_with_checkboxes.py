import os
import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QTreeWidgetItem, QDialog, QTreeWidget


class TestSelectFoldersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Folders...")
        self.setFixedSize(500, 900)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_frame")
        self.main_frame.setStyleSheet("QFrame#main_frame {border: 1px solid rgba(0, 0, 0, 0.3)}")

        self.main_layout.addWidget(self.main_frame)
        self.vertical_layout = QVBoxLayout(self.main_frame)

        self.dir_tree_widget = QTreeWidget()
        self.dir_tree_widget.itemClicked.connect(self.tree_item_clicked)
        self.dir_tree_widget.itemExpanded.connect(self.tree_item_clicked)
        self.load_immediate_directory_dir_tree_widget("/", self.dir_tree_widget)

        self.dir_tree_widget.setAnimated(False)
        
        self.dir_tree_widget.setIndentation(20)
        self.dir_tree_widget.setSortingEnabled(True)
        self.dir_tree_widget.setSortingEnabled(False)
        self.dir_tree_widget.setHeaderHidden(True)
        self.dir_tree_widget.resize(640, 480)

        self.vertical_layout.addWidget(self.dir_tree_widget)

    def load_immediate_directory_dir_tree_widget(self, path, tree):
        try:
            for element in [x for x in os.listdir(path) if os.path.isdir(path + ("/" if path != "/" else "") + x)]:

                path_info = path + ("/" if path != "/" else "") + element
                new_item = self.SpecialItem(tree, [os.path.basename(element)], full_path=path_info)
                new_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                new_item.setCheckState(0, Qt.CheckState.Unchecked)
                placeholder_item = self.SpecialItem(new_item, ["/"])
        except PermissionError:
            pass

    def tree_item_clicked(self, item):
        print("clicked on", item.text(0))
        item.takeChild(0)
        self.load_immediate_directory_dir_tree_widget(item.full_path, item)

    class SpecialItem(QTreeWidgetItem):
        def __init__(self, *args, full_path=None):
            super().__init__(*args)
            self.full_path = full_path


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    TestSelectFoldersDialog().exec()
    sys.exit(app.exec())
