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

        self.logSelectcomboBox1.activated.connect(self.initFilterParameterSelection)
        self.logSelectcomboBox2.activated.connect(self.initFilterParameterSelection)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.parameterLabel, 4, 0)

        self.operatorSelectorLabel_1.setText("Select first event log:")
        self.operatorSelectorLabel_2.setText("Select based on what you want to filter:")
        self.parameterLabel.setText("Specify filter criteria")

        # scroll area for activity matching
        self.scrollArea = QtWidgets.QScrollArea(self.operatorFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.innerRightLayout.addWidget(self.scrollArea, 6, 0, 1, 2)

        self.refresh()

 
    def initFilterParameterSelection(self):
        # clear other things added for other parameters
        self.resetParameters()

        mode = self.logSelectcomboBox2.currentText()
        if mode == "timestamp":
            self.initTimestamps()
        elif mode == "activity":
            self.initActivities()
        elif mode == "object":
            self.initObjects()
        elif mode == "attribute":
            self.initAttributes()

    def initAttributes(self):
        logName = self.logSelectcomboBox1.currentText()
        attributes = list(set(self.ocel_model.ocels[logName]["ocel:global-log"]["ocel:attribute-names"]))

        self.boxes = []
        for i in range(len(attributes)):
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(attributes[i])
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            text = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
            
            # get all attribute values and save them in input box comma separated
            allAttributeValues = set()
            for ev_id, event in self.ocel_model.ocels[logName]["ocel:events"].items():
                if attributes[i] in event["ocel:vmap"].keys():
                    allAttributeValues.add(event["ocel:vmap"][attributes[i]])
            attributeValueStr = ""
            for value in allAttributeValues:
                attributeValueStr += str(value) + ";"
            if attributeValueStr != "" and attributeValueStr[-1] == ";":
                attributeValueStr = attributeValueStr[:-1]
            text.setText(attributeValueStr)

            label2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label2.setText("Allowed values separated by ; (no space)")

            self.scrollGridLayout.addWidget(label, i+6, 0, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(checkbox, i+6, 1, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(text, i+6, 2, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(label2, i+6, 3, QtCore.Qt.AlignCenter)

            # save activity and checkbox so we can check state later
            self.boxes.append((label, checkbox, text))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)


    def initActivities(self):
        logName = self.logSelectcomboBox1.currentText()
        activities = list(set(self.ocel_model.ocels[logName]["ocel:global-event"]["ocel:activity"]))

        self.boxes = []
        for i in range(len(activities)):
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(activities[i])
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            self.scrollGridLayout.addWidget(label, i+6, 0, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(checkbox, i+6, 1, QtCore.Qt.AlignCenter)
            # save activity and checkbox so we can check state later
            self.boxes.append((label, checkbox))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

    def initObjects(self):
        logName = self.logSelectcomboBox1.currentText()
        objects = list(set(self.ocel_model.ocels[logName]["ocel:objects"].keys()))

        self.boxes = []
        for i in range(len(objects)):
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(objects[i])
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            self.scrollGridLayout.addWidget(label, i+6, 0, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(checkbox, i+6, 1, QtCore.Qt.AlignCenter)
            # save activity and checkbox so we can check state later
            self.boxes.append((label, checkbox))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

    def initTimestamps(self):
        self.startDate = QtWidgets.QDateTimeEdit(self.scrollAreaWidgetContents)
        self.endDate = QtWidgets.QDateTimeEdit(self.scrollAreaWidgetContents)
        defaultDate = QtCore.QDateTime(2020, 1, 1, 12, 30)
        self.startDate.setDateTime(defaultDate)
        self.endDate.setDateTime(defaultDate)
        self.scrollGridLayout.addWidget(self.startDate, 6, 0)
        self.scrollGridLayout.addWidget(self.endDate, 6, 1)


    def resetParameters(self):
        # add frame/layout/scrollArea for parameter selections and just clear this...
        for i in reversed(range(self.scrollGridLayout.count())): 
            self.scrollGridLayout.itemAt(i).widget().deleteLater()
    

    def getNewLog(self):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name1 = self.logSelectcomboBox1.currentText()
        log1 = self.ocel_model.ocels[name1]
        
        mode = self.logSelectcomboBox2.currentText()

        parameters = ""
        if mode == "activity" or mode == "object":
            parameters = set()
            for label, checkbox in self.boxes:
                if checkbox.isChecked():
                    parameters.add(label.text())
        elif mode == "attribute":
            parameters = {}
            for attribute, checkbox, text in self.boxes:
                if checkbox.isChecked() and len(text.text()) != 0:
                    values = set(text.text().split(";"))
                    parameters[attribute.text()] = values
        elif mode == "timestamp":
            start = datetime.datetime.strptime(self.startDate.text(), '%m/%d/%y %H:%M %p')
            end = datetime.datetime.strptime(self.endDate.text(), '%m/%d/%y %H:%M %p')
            parameters = (start, end)

        name = "FILTER (" + name1 + ")"
#        if name in self.ocel_model.ocels:
#            return
        newLog = self.miner(log1, parameters, mode)

        return (name, newLog)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.initFilterParameterSelection()

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        for i in range(len(self.ocel_model.ocels.keys())):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, list(self.ocel_model.ocels.keys())[i])

        modes = ["activity", "attribute", "object", "timestamp"]
        for i in range(len(modes)):
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox2.setItemText(i, modes[i])
        