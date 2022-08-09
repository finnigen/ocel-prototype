import pickle
from turtle import right
from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd


class TableWindow(QtWidgets.QMainWindow):

    def __init__(self, ocel_model, name):
        super().__init__()
        self.ocel_model = ocel_model
        self.name = name
        self.eventsDf = ocel_model.getEventsDf(name)
        self.objectsDf = ocel_model.getObjectsDf(name)
        self.eventsDf.fillna('-', inplace=True)
        self.objectsDf.fillna('-', inplace=True)

        # reset index, add name for index, and flatten column from multicolumns 
        self.eventsDf.reset_index(inplace=True)
        self.eventsDf.columns = [("ID", "ID"), ("Object", "Object") , ("Activity", "Activity"), ("Timestamp", "Timestamp")] + list(self.eventsDf.columns[4:])
        self.eventsDf.columns = self.eventsDf.columns.map(lambda x : x[1])

        self.objectsDf.reset_index(inplace=True)
        self.objectsDf.columns = [("OBJECT", "OBJECT")] + list(self.objectsDf.columns[1:])
        # add index to objects table so that we can see number of objects
        self.objectsDf.reset_index(inplace=True)
        self.objectsDf.columns = [("", "")] + list(self.objectsDf.columns[1:])

        self.objectsDf.columns = self.objectsDf.columns.map(lambda x : x[1])

        # transform format of objectsDf so that we have a column for each object type
        columns = [""]
        objTypes = set(self.objectsDf["ocel:type"])
        for ot in objTypes:
            columns.append(ot + " objects")
            self.objectsDf[ot + " objects"] = self.objectsDf["OBJECT"].apply(lambda x : x if x.split(":")[0] == ot else "-")
        self.objectsDf.drop(["OBJECT", "ocel:type"], axis=1, inplace=True)
        # re-order columns
        columns = columns + list(set(self.objectsDf.columns).difference(columns))
        self.objectsDf = self.objectsDf[columns]

        # transform format of eventsDf so that we have a column for each object type
        columns = ["ID"]
        for ot in objTypes:
            columns.append(ot + " objects")
            self.eventsDf[ot + " objects"] = self.eventsDf["Object"].apply(lambda x : [o for o in x if o.split(":")[0] == ot])
        self.eventsDf.drop(["Object"], axis=1, inplace=True)
        # re-order columns
        columns += ["Activity", "Timestamp"]
        columns = columns + list(set(self.eventsDf.columns).difference(columns))
        self.eventsDf = self.eventsDf[columns]


    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle(self.name)
        MainWindow.resize(960, 540)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.outerLayout = QtWidgets.QGridLayout(self.centralwidget)

        # objects table
        self.objectsLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.objectsLabel.setFont(font)

        self.outerLayout.addWidget(self.objectsLabel, 3, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.objectTable = QtWidgets.QTableView(self.centralwidget)

        _model = PandasTableModel(self.objectsDf)
        # enable custom numerical sorting
        filter_model = SortFilterProxyModel()
        filter_model.setSourceModel(_model)
        self.objectTable.setModel(filter_model)

        self.objectTable.setModel(filter_model)

        self.outerLayout.addWidget(self.objectTable, 4, 0, 1, 1)

        # event table
        self.eventsLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.eventsLabel.setFont(font)
        self.outerLayout.addWidget(self.eventsLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.eventTable = QtWidgets.QTableView(self.centralwidget)
        self.eventTable.setDragEnabled(False)
        self.outerLayout.addWidget(self.eventTable, 1, 0, 1, 1)

        _model = PandasTableModel(self.eventsDf)
        # enable custom numerical sorting
        filter_model = SortFilterProxyModel()
        filter_model.setSourceModel(_model)
        self.eventTable.setModel(filter_model)

        self.eventTable.setModel(filter_model)

        # remove index since it is same as event id columns
        self.eventTable.verticalHeader().setVisible(False)
        self.objectTable.verticalHeader().setVisible(False)

        self.objectsLabel.setText("Objects")
        self.objectTable.setSortingEnabled(True)

        self.eventsLabel.setText("Events")
        self.eventTable.setSortingEnabled(True)

        # fit table to size of window
        self.eventTable.horizontalHeader().setStretchLastSection(True)
        self.eventTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.eventTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.eventTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.objectTable.horizontalHeader().setStretchLastSection(True)
        self.objectTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.objectTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.objectTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # adjust width of ID columns to content so that they aren't unnecessarily wide
        header = self.eventTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header = self.objectTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        # sort on timestamp
        self.eventTable.sortByColumn(3, QtCore.Qt.SortOrder.AscendingOrder)
        self.eventTable.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.objectTable.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    

# we need this class for correct numerical sorting
class SortFilterProxyModel(QtCore.QSortFilterProxyModel):

    def lessThan(self, left_index, right_index):

        left_var = left_index.data(QtCore.Qt.EditRole)
        right_var = right_index.data(QtCore.Qt.EditRole)
        
        try:
            return float(left_var) < float(right_var)
        except (ValueError, TypeError):
            pass
        return left_var < right_var


class PandasTableModel(QtGui.QStandardItemModel):
    def __init__(self, data, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self._data = data
        for col in data.columns:
            data_col = []
            for x in data[col].values:
                item = QtGui.QStandardItem("{}".format(x))
                # align item text to center
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                data_col.append(item)
            self.appendColumn(data_col)
        return

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[x]
        return None



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    with open('fileBig.pkl', 'rb') as file:
        # Call load method to deserialze
        ocel_model = pickle.load(file)

    ui = TableWindow(ocel_model, "items_EVENTS")
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
