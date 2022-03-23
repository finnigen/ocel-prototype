from asyncio import events
from PyQt5 import QtCore, QtGui, QtWidgets



class ObjectWindow(QtWidgets.QMainWindow):

    def __init__(self, obj_relations):
        super().__init__()
        self.obj_relations = obj_relations

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
        all_objects = set([a for (a,b) in self.obj_relations])

        numRows = len(all_objects) 
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
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Object Relations"))
        

        # set column headers
        item = self.objectTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Object"))
        item = self.objectTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Objects"))

        # reformat object relation
        all_objects = set([a for (a,b) in self.obj_relations])
        rows = {}
        for obj in all_objects:
            rows[obj] = set([b for (a,b) in self.obj_relations if a == obj])

        for row in range(len(rows)):
                item = self.objectTable.item(row, 0)
                item.setText(_translate("MainWindow", list(rows.keys())[row]))
                item = self.objectTable.item(row, 1)
                item.setText(_translate("MainWindow", str(rows[list(rows.keys())[row]])))


        self.objectTable.setSortingEnabled(True)
        self.objectTable.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    obj_relations = {('package1', 'order1'), ('item2', 'order1'), ('item1', 'package1'), ('order1', 'item2'), ('package1', 'item1'), ('item1', 'order1'), ('order1', 'item1'), ('item2', 'package1'), ('order1', 'package1'), ('package1', 'item2')}
    ui = ObjectWindow(obj_relations)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
