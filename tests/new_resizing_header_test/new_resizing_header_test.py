import sys

from PyQt6.QtCore import QAbstractTableModel
from PyQt6.QtWidgets import QWidget, QHeaderView, QTableView, QPushButton, QVBoxLayout, QApplication


# class MyModel(QAbstractTableModel):
#     def __init__(self, *args):
#         super().__init__(*args)
#
#     def data(self):


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.tableModel = QAbstractTableModel(self) #Set the model as part of your class to access it in the event handler

        self.view = QTableView(self)
        self.view.setModel(self.tableModel) #Modified here too
        self.view.horizontalHeader().setResizeMode(QHeaderView.ResizeMode.Interactive) #Mode set to Interactive to allow resizing

        hideButton=QPushButton('Hide Column')
        hideButton.clicked.connect(self.hideColumn)

        unhideButton=QPushButton('Unhide Column')
        unhideButton.clicked.connect(self.unhideColumn)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(hideButton)
        layout.addWidget(unhideButton)
        self.setLayout(layout)

    def hideColumn(self):
        self.view.model().setColumnCount(1)

    def unhideColumn(self):
        self.view.model().setColumnCount(10)

    #Added a reimplementation of the resize event
    def resizeEvent(self, event):
        tableSize = self.view.width() #Retrieves your QTableView width
        sideHeaderWidth = self.view.verticalHeader().width() #Retrieves the left header width
        tableSize -= sideHeaderWidth #Perform a substraction to only keep all the columns width
        numberOfColumns = self.tableModel.columnCount() #Retrieves the number of columns

        for columnNum in range( self.tableModel.columnCount()): #For each column
            self.view.setColumnWidth(columnNum, int(tableSize/numberOfColumns) ) #Set the width = tableSize / nbColumns
        super().resizeEvent(event) #Restores the original behaviour of the resize event


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MyWindow()
    main_window.show()
    sys.exit(app.exec())
