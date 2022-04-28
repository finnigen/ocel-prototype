from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrame import OperatorFrame
from operators import filterLog
import datetime

class FilterFrame(OperatorFrame):
 
    def __init__(self, parent, ocel, title, description):
        miner = filterLog
        super().__init__(parent, ocel, title, description, miner)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_1 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_1.setEnabled(True)
        self.operatorSelectorLabel_1.setFont(font)
        self.operatorSelectorLabel_1.setObjectName("operatorSelectorLabel_1")
        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_2.setEnabled(True)
        self.operatorSelectorLabel_2.setFont(font)
        self.operatorSelectorLabel_2.setObjectName("operatorSelectorLabel_2")

        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox1.setObjectName("logSelectcomboBox1")

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox2.setObjectName("logSelectcomboBox2")

        self.parameterLabel = QtWidgets.QLabel(self.operatorFrame)
        self.parameterLabel.setFont(font)
        self.parameterInput = QtWidgets.QLineEdit(self.operatorFrame)


        self.logSelectcomboBox1.activated.connect(self.initFilterParameterSelection)
        self.logSelectcomboBox2.activated.connect(self.initFilterParameterSelection)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.parameterLabel, 4, 0)
        self.innerRightLayout.addWidget(self.parameterInput, 5, 0)


        self.operatorSelectorLabel_1.setText("Select first event log:")
        self.operatorSelectorLabel_2.setText("Select based on what you want to filter:")
        self.parameterLabel.setText("Enter parameters (activity: set, attribute: dict, object: set, timestamp: tuple):")

        self.refresh()

 
    def initFilterParameterSelection(self):
        # clear other things added for other parameters?
        mode = self.logSelectcomboBox2.currentText()
        if mode == "timestamp":
            self.initTimestamps()


    def initTimestamps(self):

        self.startDate = QtWidgets.QDateTimeEdit(self.operatorFrame)
        self.endDate = QtWidgets.QDateTimeEdit(self.operatorFrame)

        self.innerRightLayout.addWidget(self.startDate, 6, 0)
        self.innerRightLayout.addWidget(self.endDate, 6, 1)


    def getNewLog(self):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name1 = self.logSelectcomboBox1.currentText()
        log1 = self.ocel_model.ocels[name1]
        
        parameters = self.parameterInput.text()
        mode = self.logSelectcomboBox2.currentText()
        if mode == "activity" or mode == "object":
            parameters = set(parameters.split(","))
        elif mode == "timestamp":
            start = datetime.datetime.strptime(self.startDate.text(), '%m/%d/%y %H:%M %p')
            end = datetime.datetime.strptime(self.endDate.text(), '%m/%d/%y %H:%M %p')
            parameters = (start, end)
        else:
            print("not working yet")
            return

        name = "FILTER (" + name1 + ")"
#        if name in self.ocel_model.ocels:
#            return
        newLog = self.miner(log1, parameters, mode)

        return (name, newLog)
       

    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        for i in range(len(self.ocel_model.ocels.keys())):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, list(self.ocel_model.ocels.keys())[i])

        modes = ["activity", "attribute", "object", "timestamp"]
        for i in range(len(modes)):
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox2.setItemText(i, modes[i])
        
        self.parameterInput.clear()
