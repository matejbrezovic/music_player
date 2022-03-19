import sys
from typing import Any, Optional

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QMainWindow, QWidget, \
    QHBoxLayout


class Model(QtCore.QAbstractTableModel):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super(Model, self).__init__(parent)
        self.__data = []
        for i in range(10):
            row = [0, 1, 2, 3, 42222222222, 5, 6, 74444444]
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(700, 700)

        self.central_widget = QWidget()
        self.central_widget_layout = QHBoxLayout(self.central_widget)

        view = QtWidgets.QTableView()
        view.resize(600, 600)
        view.setFrameShape(QFrame.Shape.NoFrame)
        model = Model()
        view.setModel(model)
        view.verticalHeader().setOffset(-40)

        self.central_widget_layout.addWidget(view)

        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
