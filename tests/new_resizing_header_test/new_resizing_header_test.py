import sys
from typing import Any, Optional

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QTableView
from PyQt6 import QtGui


class Model(QtCore.QAbstractTableModel):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(Model, self).__init__(parent)
        self.__data = []
        for i in range(10):
            row = [0, 1, 2, 3, 4, 5, 6, 7]
            self.__data.append(row)

    def rowCount(self, index: Optional[QtCore.QModelIndex] = None) -> int:
        return len(self.__data)

    def columnCount(self, index: Optional[QtCore.QModelIndex] = None) -> int:
        return len(self.__data[0])

    def data(self, index: QtCore.QModelIndex,
             role: QtCore.Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            return self.__data[index.row()][index.column()]
        return None


class MyView(QTableView):
    def __init__(self):
        super().__init__()

    # def paintEvent(self, e: QtGui.QPaintEvent) -> None:

    # def updateGeometry(self) -> None:
    #     print("uuu")
    #     # super().updateGeometries()

    # def paintEvent(self, e: QtGui.QPaintEvent) -> None:
    #     super().paintEvent(e)
    #     self.verticalHeader().setOffset(-40)

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        super().resizeEvent(e)
        self.verticalHeader().setOffset(-40)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(700, 700)

        self.central_widget = QWidget()
        self.central_widget_layout = QHBoxLayout(self.central_widget)

        self.view = QTableView()
        self.model = Model()
        self.view.setModel(self.model)
        self.view.verticalHeader().setOffset(-40)

        self.central_widget_layout.addWidget(self.view)
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    # mw.view.verticalHeader().setOffset(-40)
    sys.exit(app.exec())
