from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget


class ScanFoldersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Folders for New Files")
        self.setMinimumSize(700, 400)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_frame")
        self.main_frame.setStyleSheet("QFrame#main_frame {border: 1px solid rgba(0, 0, 0, 0.3)}")

        self.label = QLabel("Scan for new files in the following folders:")
        self.choose_folders_button = QPushButton("Choose Folders")
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

        self.top_horizontal_layout.addWidget(self.label)
        self.top_horizontal_layout.addStretch()
        self.top_horizontal_layout.addWidget(self.choose_folders_button)

        self.vertical_layout.addWidget(self.top_horizontal_widget)
        self.vertical_layout.addWidget(self.selected_folders_scroll_area)
