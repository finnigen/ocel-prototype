from asyncio import events
from PyQt5 import QtCore, QtGui, QtWidgets
import pickle
from ocel_converter import OCEL_Model


class ObjectWindow(QtWidgets.QMainWindow):

    def __init__(self, formattedRows):
        super().__init__()
        self.formattedRows = formattedRows

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(960, 540)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.outerLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.outerLayout.setObjectName("outerLayout")

        # objects table
        self.objectTable = QtWidgets.QTableWidget(self.centralwidget)
        self.objectTable.setObjectName("objectTable")

        # one row for every object
        numRows = len(self.formattedRows) 
        numColumns = 2

        self.objectTable.setColumnCount(numColumns)
        self.objectTable.setRowCount(numRows)

        for i in range(numColumns):
            item = QtWidgets.QTableWidgetItem()
            self.objectTable.setHorizontalHeaderItem(i, item)

        for i in range(numRows):
            for j in range(numColumns):
                item = QtWidgets.QTableWidgetItem()
                self.objectTable.setItem(i, j, item)

        self.outerLayout.addWidget(self.objectTable, 0, 0, 1, 1)

        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # fit table to size of window
        self.objectTable.horizontalHeader().setStretchLastSection(True)
        self.objectTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.objectTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.objectTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Object Relations")

        # set column headers
        item = self.objectTable.horizontalHeaderItem(0)
        item.setText("Object")
        item = self.objectTable.horizontalHeaderItem(1)
        item.setText("Objects")

        # reformat object relation
        rows = self.formattedRows

        for row in range(len(rows)):
            item = self.objectTable.item(row, 0)
            item.setText(list(rows.keys())[row])
            item = self.objectTable.item(row, 1)
            data = rows[list(rows.keys())[row]]
            if data == set():
                data = {}
            item.setText(str(data))

        # sort objects ascending
        self.objectTable.setSortingEnabled(True)
        self.objectTable.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
#    obj_relations = {('package1', 'order1'), ('item2', 'order1'), ('item1', 'package1'), ('order1', 'item2'), ('package1', 'item1'), ('item1', 'order1'), ('order1', 'item1'), ('item2', 'package1'), ('order1', 'package1'), ('package1', 'item2')}
#    with open('file.pkl', 'rb') as file:
        # Call load method to deserialze
#        ocel_model = pickle.load(file)
    formattedRows = {'order2': set(), 'package1': {'item1', 'order1', 'item2'}, 'item2': {'order1', 'package1'}, 'order1': {'item1', 'item2', 'package1'}, 'item1': {'order1', 'package1'}}
    ui = ObjectWindow(formattedRows)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
