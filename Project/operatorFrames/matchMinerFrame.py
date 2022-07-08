from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrames.operatorFrame import OperatorFrame
from operators import matchMiner

class MatchMinerFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)


        self.logSelectionLabel1 = QtWidgets.QLabel(self.operatorFrame)
        self.logSelectionLabel1.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.logSelectionLabel1.setFont(font)
        self.operatorSelectorLabel_3 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_3.setEnabled(True)
        self.operatorSelectorLabel_3.setFont(font)
        
        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)

        self.logSelectcomboBox1.activated.connect(self.initAttributes1)
        self.logSelectcomboBox2.activated.connect(self.initAttributes2)

        self.attrSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)

        self.attrSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
        
        self.logSelectionLabel2 = QtWidgets.QLabel(self.operatorFrame)
        self.logSelectionLabel2.setEnabled(True)

        self.logSelectionLabel2.setFont(font)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.logSelectionLabel1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.innerRightLayout.addWidget(self.logSelectionLabel2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_3, 4, 0)
        self.innerRightLayout.addWidget(self.attrSelectcomboBox1, 4, 1)
        self.innerRightLayout.addWidget(self.attrSelectcomboBox2, 5, 1)

        self.logSelectionLabel1.setText("Select first event log:")
        self.logSelectionLabel2.setText("Select second event log:")
        self.operatorSelectorLabel_3.setText("Select attribute(s) to match on:")

        self.refresh()


    def initAttributes1(self):
        name = self.logSelectcomboBox1.currentText()
        attributes = self.ocel_model.getEventsDf(name)["ocel:vmap"].columns
        self.attrSelectcomboBox1.clear()
        for i in range(len(attributes)):
            self.attrSelectcomboBox1.addItem("")
            self.attrSelectcomboBox1.setItemText(i, attributes[i])

    def initAttributes2(self):
        name = self.logSelectcomboBox2.currentText()
        attributes = self.ocel_model.getEventsDf(name)["ocel:vmap"].columns        
        self.attrSelectcomboBox2.clear()
        for i in range(len(attributes)):
            self.attrSelectcomboBox2.addItem("")
            self.attrSelectcomboBox2.setItemText(i, attributes[i])
 

    def getNewLog(self, newName):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()
        attr1 = self.attrSelectcomboBox1.currentText()
        attr2 = self.attrSelectcomboBox2.currentText()

        return self.ocel_model.matchMiner(name1, name2, attr1, attr2, newName=newName)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])
            self.logSelectcomboBox2.setItemText(i, names[i])

        self.initAttributes1()
        self.initAttributes2()