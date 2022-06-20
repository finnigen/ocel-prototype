from asyncio import events
from PyQt5 import QtCore, QtGui, QtWidgets
import pickle
from ocel_converter import OCEL_Model
import pandas as pd
from tableWindow import PandasTableModel

class ObjectWindow(QtWidgets.QMainWindow):

    def __init__(self, objRelation):
        super().__init__()

        df = pd.DataFrame(objRelation)
        df[1] = df[1].apply(lambda x : [x])
        df = pd.DataFrame(df.groupby(0)[1].apply(sum))
        df.reset_index(inplace=True)
        df.columns = ["Object", "Related Objects"]
        self.df = df

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("Object Relationships")
        MainWindow.resize(960, 540)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.outerLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.outerLayout.setObjectName("outerLayout")

        self.relationTable = QtWidgets.QTableView(self.centralwidget)
        self.relationTable.setDragEnabled(False)
        self.relationTable.setObjectName("relationTable")

        self.relationModel = PandasTableModel(self.df)
        self.relationTable.setModel(self.relationModel)

        self.relationTable.setSortingEnabled(True)

        # fit table to size of window
        self.relationTable.horizontalHeader().setStretchLastSection(True)
        self.relationTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.relationTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.relationTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.outerLayout.addWidget(self.relationTable, 0, 0, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.relationTable.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
#    obj_relations = {('package1', 'order1'), ('item2', 'order1'), ('item1', 'package1'), ('order1', 'item2'), ('package1', 'item1'), ('item1', 'order1'), ('order1', 'item1'), ('item2', 'package1'), ('order1', 'package1'), ('package1', 'item2')}
#    with open('file.pkl', 'rb') as file:
        # Call load method to deserialze
#        ocel_model = pickle.load(file)
#    formattedRows = {'order2': set(), 'package1': {'item1', 'order1', 'item2'}, 'item2': {'order1', 'package1'}, 'order1': {'item1', 'item2', 'package1'}, 'item1': {'order1', 'package1'}}
    relations = set([(1,2),(2,3)])
    ui = ObjectWindow(relations)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
