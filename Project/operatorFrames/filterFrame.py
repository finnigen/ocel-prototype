from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrames.operatorFrame import OperatorFrame
from operators import filterLog
import datetime

class FilterFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.logSelectionLabel1 = QtWidgets.QLabel(self.operatorFrame)
        self.logSelectionLabel1.setEnabled(True)
        self.logSelectionLabel1.setFont(font)
        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_2.setEnabled(True)
        self.operatorSelectorLabel_2.setFont(font)

        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)

        self.parameterLabel = QtWidgets.QLabel(self.operatorFrame)
        self.parameterLabel.setFont(font)

        self.logSelectcomboBox1.activated.connect(self.initFilterParameterSelection)
        self.logSelectcomboBox2.activated.connect(self.initFilterParameterSelection)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.logSelectionLabel1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.parameterLabel, 4, 0)

        self.logSelectionLabel1.setText("Select event log:")
        self.operatorSelectorLabel_2.setText("Select based on what you want to filter:")
        self.parameterLabel.setText("Specify filter criteria")

        # scroll area for parameter selection
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
        elif mode == "objectType":
            self.initObjectTypes()
        elif mode == "eventAttribute" or mode == "objectAttribute":
            self.initAttributes(mode)

    def initAttributes(self, mode):
        logName = self.logSelectcomboBox1.currentText()

        if mode == "eventAttribute":
            if "ocel:vmap" in self.ocel_model.getEventsDf(logName).columns:
                attributesDf = self.ocel_model.getEventsDf(logName)["ocel:vmap"]
            else:
                return
        else:
            if "ocel:ovmap" in self.ocel_model.getObjectsDf(logName).columns:
                attributesDf = self.ocel_model.getObjectsDf(logName)["ocel:ovmap"]
            else:
                return

        attributes = list(attributesDf.columns)
        attributes.sort()

        self.boxes = []
        for i in range(len(attributes)):
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(attributes[i])
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            text = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
            
            typ = attributesDf[attributes[i]].dtype
            if typ == "int64" or typ == "float64" or typ == "datetime64[ns]":
                mini = min(attributesDf[attributes[i]])
                maxi = max(attributesDf[attributes[i]])
                attributeValueStr = str(mini) + ";" + str(maxi)
            else:
                # get all attribute values and save them in input box comma separated
                allAttributeValues = set(attributesDf[attributes[i]].dropna())

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
        activities = list(set(self.ocel_model.getEventsDf(logName)[("ocel:activity", "ocel:activity")]))
        activities.sort()

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
        objectsDf = self.ocel_model.getObjectsDf(logName)
        objects = list(set(objectsDf.index))
        objects.sort()

        myFont=QtGui.QFont()
        myFont.setBold(True)

        self.boxes = []
        for i in range(len(objects)):
            # object type
            labelType = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            labelType.setText(objectsDf.loc[objects[i]][("ocel:type", "ocel:type")] + ":")
            labelType.setFont(myFont)

            # object
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(objects[i])
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            self.scrollGridLayout.addWidget(labelType, i, 0, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(label, i, 1, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(checkbox, i, 2, QtCore.Qt.AlignCenter)
            # save activity and checkbox so we can check state later
            self.boxes.append((label, checkbox))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)


    def initObjectTypes(self):
        logName = self.logSelectcomboBox1.currentText()
        objectsDf = self.ocel_model.getObjectsDf(logName)
        objectTypes = list(set(objectsDf[("ocel:type", "ocel:type")]))
        objectTypes.sort()

        myFont=QtGui.QFont()
        myFont.setBold(True)

        self.boxes = []
        for i in range(len(objectTypes)):
            # objectType
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(objectTypes[i])
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            self.scrollGridLayout.addWidget(label, i, 1, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(checkbox, i, 2, QtCore.Qt.AlignCenter)
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
    

    def getNewLog(self, newName):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name = self.logSelectcomboBox1.currentText()
        
        mode = self.logSelectcomboBox2.currentText()

        parameters = ""
        if mode == "activity" or mode == "object" or mode == "objectType":
            parameters = set()
            for label, checkbox in self.boxes:
                if checkbox.isChecked():
                    parameters.add(label.text())
        elif mode == "eventAttribute" or "objectAttribute":
            parameters = {}
            for attribute, checkbox, text in self.boxes:
                if checkbox.isChecked() and len(text.text()) != 0:
                    values = text.text().split(";")
                    parameters[attribute.text()] = values
        elif mode == "timestamp":
            start = datetime.datetime.strptime(self.startDate.text(), '%m/%d/%y %H:%M %p')
            end = datetime.datetime.strptime(self.endDate.text(), '%m/%d/%y %H:%M %p')
            parameters = (start, end)

        return self.ocel_model.filterLog(name, parameters, mode, newName=newName)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])

        modes = ["activity", "eventAttribute", "objectAttribute", "object", "objectType", "timestamp"]
        for i in range(len(modes)):
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox2.setItemText(i, modes[i])
        
        self.initFilterParameterSelection()
