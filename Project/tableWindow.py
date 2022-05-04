from asyncio import events
from operator import is_
from PyQt5 import QtCore, QtGui, QtWidgets



#def is_float(element):
#    try:
#        float(element)
#        return True
#    except ValueError:
#        return False



class TableWindow(QtWidgets.QMainWindow):

    def __init__(self, ocel, name):
        super().__init__()
        self.ocel = ocel
        self.name = name

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
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
        self.objectTable = QtWidgets.QTableWidget(self.centralwidget)
        self.objectTable.setObjectName("objectTable")

        numRows = len(self.ocel["ocel:objects"])
        obj_attributes = set()
        # find attributes
        for obj in self.ocel["ocel:objects"]:
            obj_attributes = obj_attributes.union(self.ocel["ocel:objects"][obj]["ocel:ovmap"])
        numColumns = len(obj_attributes) + 2 # 2 for object name and type

        self.objectTable.setColumnCount(numColumns)
        self.objectTable.setRowCount(numRows)

        for i in range(numColumns):
            item = QtWidgets.QTableWidgetItem()
            self.objectTable.setHorizontalHeaderItem(i, item)
        
    #    for i in range(numRows):
    #        item = QtWidgets.QTableWidgetItem()
    #        self.objectTable.setVerticalHeaderItem(i, item)

        for i in range(numRows):
            for j in range(numColumns):
                item = QtWidgets.QTableWidgetItem()
                self.objectTable.setItem(i, j, item)

        self.outerLayout.addWidget(self.objectTable, 4, 0, 1, 1)

        
        
        # event table
        self.eventsLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.eventsLabel.setFont(font)
        self.eventsLabel.setObjectName("eventsLabel")
        self.outerLayout.addWidget(self.eventsLabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.eventTable = QtWidgets.QTableWidget(self.centralwidget)
        self.eventTable.setDragEnabled(False)
        self.eventTable.setObjectName("eventTable")
        self.outerLayout.addWidget(self.eventTable, 1, 0, 1, 1)

        numColumns = len(self.ocel['ocel:global-log']['ocel:attribute-names']) + 4 # 4 for id, timestamp, case, column
        numRows = len(self.ocel['ocel:events'])

        self.eventTable.setColumnCount(numColumns)
        self.eventTable.setRowCount(numRows)

        for i in range(numColumns):
            item = QtWidgets.QTableWidgetItem()
            self.eventTable.setHorizontalHeaderItem(i, item)
        
    #    for i in range(numRows):
    #        item = QtWidgets.QTableWidgetItem()
    #        self.eventTable.setVerticalHeaderItem(i, item)

        for i in range(numRows):
            for j in range(numColumns):
                item = QtWidgets.QTableWidgetItem()
                self.eventTable.setItem(i, j, item)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # fit table to size of window
        self.eventTable.horizontalHeader().setStretchLastSection(True)
        self.eventTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.eventTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.eventTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.objectTable.horizontalHeader().setStretchLastSection(True)
        self.objectTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.objectTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.objectTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Data Viewer: " + self.name)
        
        # objects table
        self.objectsLabel.setText("Objects")

        rowKeys = list(self.ocel["ocel:objects"].keys())
        obj_attributes = set()
        # find attributes
        for obj in self.ocel["ocel:objects"]:
            obj_attributes = obj_attributes.union(self.ocel["ocel:objects"][obj]["ocel:ovmap"])
        columns = ["object", "type"] + list(obj_attributes)

        # set column headers
        for i in range(len(columns)):
            item = self.objectTable.horizontalHeaderItem(i)
            item.setText(columns[i])

        for row in range(len(rowKeys)):
            for column in range(len(columns)):
                item = self.objectTable.item(row, column)
                data = ""
                if column == 0: # object
                    data = rowKeys[row]
                elif column == 1: # type
                    data = self.ocel["ocel:objects"][rowKeys[row]]["ocel:type"]
                elif column >= 2: # for attributes, we need to access ovmap
                    attributes = self.ocel["ocel:objects"][rowKeys[row]]["ocel:ovmap"]
                    if columns[column] in attributes.keys():
                        data = attributes[columns[column]]
                item.setText(str(data))

        self.objectTable.setSortingEnabled(True)

        # events table
        self.eventsLabel.setText("Events")
        
        columns = ["id", "omap", "activity", "timestamp"]
        for i in self.ocel['ocel:global-log']['ocel:attribute-names']:
            columns.append(i)

        # set column headers
        for i in range(len(columns)):
            item = self.eventTable.horizontalHeaderItem(i)
            item.setText(columns[i])
        
        # set row header
        rowKeys = list(self.ocel['ocel:events'].keys())
    #    for i in range(len(rowKeys)):
    #        item = self.eventTable.verticalHeaderItem(i)
    #        item.setText(rowKeys[i])

        # set data
        for row in range(len(rowKeys)):
            for column in range(len(columns)):
                item = self.eventTable.item(row, column)
                data = ""
                if column == 0:
                    data = rowKeys[row]
                elif column > 3: # for attributes, we need to access vmap
                    attributes = self.ocel["ocel:events"][rowKeys[row]]["ocel:vmap"]
                    if columns[column] in attributes.keys():
                        data = attributes[columns[column]]
                else:
                    data = self.ocel["ocel:events"][rowKeys[row]]["ocel:" + columns[column]]
                data = str(data)
                item.setText(str(data))

        self.eventTable.setSortingEnabled(True)
        # sort on timestamp
        self.eventTable.sortByColumn(3, QtCore.Qt.SortOrder.AscendingOrder)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ocel = {'ocel:global-event': {'ocel:activity': ['place order', 'send package']}, 'ocel:global-object': {'ocel:type': '__INVALID__'}, 'ocel:global-log': {'ocel:attribute-names': ['ATT_package_attr1', 'EVID_general', 'EVID_package', 'ATT_EVENT_attr1'], 'ocel:object-types': ['CASE_package'], 'ocel:version': '1.0', 'ocel:ordering': 'timestamp'}, 'ocel:events': {'0': {'ocel:activity': 'place order', 'ocel:timestamp': '2020-07-09 08:20:00', 'ocel:omap': ['package1'], 'ocel:vmap': {'ATT_EVENT_attr1': 'attValue', 'EVID_general': '1.0', 'EVID_package': '1.0:package1'}}, '1': {'ocel:activity': 'send package', 'ocel:timestamp': '2020-07-09 08:31:00', 'ocel:omap': ['package1'], 'ocel:vmap': {'ATT_EVENT_attr1': 'attValue', 'EVID_general': '7.0', 'EVID_package': '7.0:package1'}}}, 'ocel:objects': {'package1': {'ocel:type': 'CASE_package', 'ocel:ovmap': {'ATT_package_attr1': 'attValue'}}}}
    ui = TableWindow(ocel, "package_EVENTS")
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
