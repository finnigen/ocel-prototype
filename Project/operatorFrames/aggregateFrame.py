from PyQt5 import QtCore, QtGui, QtWidgets

from operatorFrames.operatorFrame import OperatorFrame

class AggregateFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

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
