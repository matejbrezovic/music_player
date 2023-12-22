from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QComboBox


class TransparentComboBox(QComboBox):
    default_stylesheet = ''' 
                       QComboBox {
                           color: black;
                           selection-color: black;
                           selection-background-color: rgba(255, 255, 255, 0);
                           background-color: rgba(255, 255, 255, 0);
                       }
                       QComboBox QAbstractItemView {
                           background-color: white;
                           min-width: 150px;
                       }
                       QComboBox:open {
                           color: black;
                       }
                       QComboBox:drop-down:open {
                           color: black;
                           background-color: rgba(255, 255, 255, 0);
                       }
                       QComboBox:down-arrow:open {
                           color: black;
                           background-color: rgba(255, 255, 255, 0);
                       }
                       '''
    hide_combobox = '''QComboBox::drop-down:!hover {
                            background-color: rgba(255, 255, 255, 0);
                        }'''

    def __init__(self, *args):
        super().__init__(*args)

        self.setStyleSheet(self.hide_combobox + self.default_stylesheet)
        self.setUpdatesEnabled(True)
        self.currentIndexChanged.connect(lambda: self.adjustSize())

    def sizeHint(self):
        text = self.currentText()
        width = self.fontMetrics().boundingRect(text).width() + 28
        self.setFixedWidth(width)
        return QSize(width, self.height())

    def enterEvent(self, *args, **kwargs):
        super().enterEvent(*args, **kwargs)
        self.setStyleSheet(self.default_stylesheet)

    def leaveEvent(self, *args, **kwargs):
        super().leaveEvent(*args, **kwargs)
        self.setStyleSheet(self.hide_combobox + self.default_stylesheet)
