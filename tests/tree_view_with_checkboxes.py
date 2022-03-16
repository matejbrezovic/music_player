import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTreeWidget, QScrollArea, \
    QPushButton

from utils import *


class TestSelectFoldersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Folders...")
        self.setFixedSize(500, 800)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_frame")
        self.main_frame.setStyleSheet("QFrame#main_frame {border: 1px solid rgba(0, 0, 0, 0.3)}")

        self.dir_tree_widget = QTreeWidget()
        self.dir_tree_widget.itemClicked.connect(self.tree_item_clicked)
        self.dir_tree_widget.itemExpanded.connect(self.tree_item_clicked)
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

    def load_immediate_directory_dir_tree_widget(self, path, tree):
        try:
            for element in [x for x in os.listdir(path) if os.path.isdir(path + ("/" if path != "/" else "") + x)]:

                path_info = path + ("/" if path != "/" else "") + element
                new_item = self.DirectoryItem(tree, [os.path.basename(element)], full_path=path_info)
                new_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                new_item.setCheckState(0, Qt.CheckState.Unchecked)
                self.DirectoryItem(new_item, ["/"])
        except PermissionError:
            pass

    def tree_item_clicked(self, item):
        print("clicked on", item.text(0))
        item.takeChild(0)
        self.load_immediate_directory_dir_tree_widget(item.full_path, item)

    class DirectoryItem(QTreeWidgetItem):
        def __init__(self, *args, full_path=None):
            super().__init__(*args)
            self.full_path = full_path




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    TestSelectFoldersDialog().exec()
    sys.exit(app.exec())
