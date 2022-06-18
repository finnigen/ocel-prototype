from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrames.operatorFrame import OperatorFrame
from operators import flatten

class FlattenFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)


        self.operatorSelectorLabel_1 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_1.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_1.setFont(font)
        self.operatorSelectorLabel_1.setObjectName("operatorSelectorLabel_1")
        
        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox1.setObjectName("logSelectcomboBox1")

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox2.setObjectName("logSelectcomboBox2")

        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_2.setEnabled(True)

        self.operatorSelectorLabel_2.setFont(font)
        self.operatorSelectorLabel_2.setObjectName("operatorSelectorLabel_2")

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)

        self.operatorSelectorLabel_1.setText("Select first event log:")
        self.operatorSelectorLabel_2.setText("Select object type:")

        self.logSelectcomboBox1.activated.connect(self.initObjectTypes)

        self.refresh()
 

    def getNewLog(self, newName):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name = self.logSelectcomboBox1.currentText()
        objectType = self.logSelectcomboBox2.currentText()

        return self.ocel_model.flatten(name, objectType, newName=newName)


    def initObjectTypes(self):
        self.logSelectcomboBox2.clear()
        name = self.logSelectcomboBox1.currentText()
        types = list(self.ocel_model.getObjectTypes(name))
        types.sort()
        for i in range(len(types)):
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox2.setItemText(i, types[i])



    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])

        self.initObjectTypes()