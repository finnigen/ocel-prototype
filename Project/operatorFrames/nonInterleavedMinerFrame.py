from PyQt5 import QtCore, QtGui, QtWidgets

from operatorFrames.operatorFrame import OperatorFrame

class NonInterleavedMinerFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectionLabel2 = QtWidgets.QLabel(self.operatorFrame)
        self.logSelectionLabel2.setFont(self.normalFont)

        self.mergeEventsLabel = QtWidgets.QLabel(self.operatorFrame)
        self.mergeEventsLabel.setFont(self.normalFont)
        self.mergeEventsCheckBox = QtWidgets.QCheckBox(self.operatorFrame)
        self.mergeEventsCheckBox.setChecked(False)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.logSelectionLabel2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.mergeEventsLabel, 5, 0)
        self.innerRightLayout.addWidget(self.mergeEventsCheckBox, 5, 1) 

        self.logSelectionLabel1.setText("Select 1st event log:")
        self.logSelectionLabel2.setText("Select 2nd event log:")
        self.mergeEventsLabel.setText("Merge all events from 2nd log:")

        self.refresh()
 
    def getParameters(self):
        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()
        mergeEvents = self.mergeEventsCheckBox.isChecked()

        return {"name1" : name1, "name2" : name2, "mergeEvents" : mergeEvents}

    def getNewLog(self, newName, parameters={}):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        if len(parameters) == 0:
            parameters = self.getParameters()
        
        name1 = parameters["name1"]
        name2 = parameters["name2"]
        mergeEvents = parameters["mergeEvents"]

        return self.ocel_model.nonInterleavedMiner(name1, name2, mergeEvents, newName=newName)

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