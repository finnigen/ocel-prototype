from asyncio import events
from operator import is_
from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd


class TableWindow(QtWidgets.QMainWindow):

    def __init__(self, ocel_model, name):
        super().__init__()
        self.ocel_model = ocel_model
        self.name = name
        self.eventsDf = ocel_model.getEventsDf(name)
        self.objectsDf = ocel_model.getObjectsDf(name)

        # reset index, add name for index, and flatten column from multicolumns 
        self.eventsDf.reset_index(inplace=True)
        self.eventsDf.columns = [("EVENT ID", "EVENT ID")] + list(self.eventsDf.columns[1:])
        self.eventsDf.columns = self.eventsDf.columns.map(lambda x : x[1])

        self.objectsDf.reset_index(inplace=True)
        self.objectsDf.columns = [("OBJECT", "OBJECT")] + list(self.objectsDf.columns[1:])
        self.objectsDf.columns = self.objectsDf.columns.map(lambda x : x[1])


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle(self.name)
        MainWindow.resize(960, 540)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.outerLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.outerLayout.setObjectName("outerLayout")

        # objects table
        self.objectsLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.objectsLabel.setFont(font)
        self.objectsLabel.setObjectName("objectsLabel")

        self.outerLayout.addWidget(self.objectsLabel, 3, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.objectTable = QtWidgets.QTableView(self.centralwidget)
        self.objectTable.setObjectName("objectTable")

        self.objectsModel = PandasTableModel(self.objectsDf)
        self.objectTable.setModel(self.objectsModel)

        self.outerLayout.addWidget(self.objectTable, 4, 0, 1, 1)

        # event table
        self.eventsLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.eventsLabel.setFont(font)
        self.eventsLabel.setObjectName("eventsLabel")
        self.outerLayout.addWidget(self.eventsLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.eventTable = QtWidgets.QTableView(self.centralwidget)
        self.eventTable.setDragEnabled(False)
        self.eventTable.setObjectName("eventTable")
        self.outerLayout.addWidget(self.eventTable, 1, 0, 1, 1)

        self.eventsModel = PandasTableModel(self.eventsDf)
        self.eventTable.setModel(self.eventsModel)

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

        # sort on timestamp
        self.eventTable.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.eventTable.sortByColumn(3, QtCore.Qt.SortOrder.AscendingOrder)
        self.objectTable.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)



class PandasTableModel(QtGui.QStandardItemModel):
    def __init__(self, data, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self._data = data
        for col in data.columns:
            data_col = [QtGui.QStandardItem("{}".format(x)) for x in data[col].values]
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
    ocel = {'ocel:global-event': {'ocel:activity': ['place order', 'send package']}, 'ocel:global-object': {'ocel:type': '__INVALID__'}, 'ocel:global-log': {'ocel:attribute-names': ['ATT_package_attr1', 'EVID_general', 'EVID_package', 'ATT_EVENT_attr1'], 'ocel:object-types': ['CASE_package'], 'ocel:version': '1.0', 'ocel:ordering': 'timestamp'}, 'ocel:events': {'0': {'ocel:activity': 'place order', 'ocel:timestamp': '2020-07-09 08:20:00', 'ocel:omap': ['package1'], 'ocel:vmap': {'ATT_EVENT_attr1': 'attValue', 'EVID_general': '1.0', 'EVID_package': '1.0:package1'}}, '1': {'ocel:activity': 'send package', 'ocel:timestamp': '2020-07-09 08:31:00', 'ocel:omap': ['package1'], 'ocel:vmap': {'ATT_EVENT_attr1': 'attValue', 'EVID_general': '7.0', 'EVID_package': '7.0:package1'}}}, 'ocel:objects': {'package1': {'ocel:type': 'CASE_package', 'ocel:ovmap': {'ATT_package_attr1': 'attValue'}}}}
    objdf = {('ocel:type', 'ocel:type'): {'o1': 'CASE_ORDERS', 'o2': 'CASE_ORDERS'}}
    evdf = {('ocel:omap', 'ocel:omap'): {0: ['o1'],   1: ['o1'],   2: ['o1'],   3: ['o2'],   4: ['o2'],   5: ['o1'],   6: ['o2'],   7: ['o2'],   8: ['o2'],   9: ['o2']},  ('ocel:activity', 'ocel:activity'): {0: 'place order',   1: 'confirm order',   2: 'pay order',   3: 'place order',   4: 'confirm order',   5: 'order dispatched',   6: 'order delayed',   7: 'order updated',   8: 'pay order',   9: 'order dispatched'},  ('ocel:timestamp', 'ocel:timestamp'): {0: '2020-07-15 13:00:00',   1: '2020-07-15 14:00:00',   2: '2020-07-15 14:30:00',   3: '2020-07-16 09:21:00',   4: '2020-07-16 09:22:00',   5: '2020-07-16 10:00:00',   6: '2020-07-19 18:00:00',   7: '2020-07-20 10:31:00',   8: '2020-07-20 12:44:20',   9: '2020-07-21 10:00:00'},  ('ocel:vmap', 'WEIGHT'): {0: 550,   1: 550,   2: 550,   3: 2480,   4: 2480,   5: 550,   6: 2480,   7: 2480,   8: 2480,   9: 2480},  ('ocel:vmap', 'PRICE'): {0: 30,   1: 30,   2: 30,   3: 316,   4: 316,   5: 30,   6: 316,   7: 316,   8: 316,   9: 316}}
    ui = TableWindow(ocel, "package_EVENTS", objdf, evdf)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
