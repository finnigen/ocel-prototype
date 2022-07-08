from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrames.operatorFrame import OperatorFrame
from operators import aggregate

class AggregateFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        self.logSelectionLabel1 = QtWidgets.QLabel(self.operatorFrame)
        self.logSelectionLabel1.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.logSelectionLabel1.setFont(font)
        
        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)


        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.logSelectionLabel1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)

        self.logSelectionLabel1.setText("Select event log:")

        self.refresh()
 

    def getNewLog(self, newName):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name = self.logSelectcomboBox1.currentText()

        return self.ocel_model.aggregate(name, newName=newName)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])
