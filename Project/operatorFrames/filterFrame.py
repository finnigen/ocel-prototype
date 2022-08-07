from PyQt5 import QtCore, QtGui, QtWidgets

from operatorFrames.operatorFrame import OperatorFrame
import datetime
from pandas.api.types import is_numeric_dtype

class FilterFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_2.setFont(self.normalFont)

        self.modeSelectionComboBox = QtWidgets.QComboBox(self.operatorFrame)

        self.parameterLabel = QtWidgets.QLabel(self.operatorFrame)
        self.parameterLabel.setFont(self.normalFont)

        self.logSelectcomboBox1.activated.connect(self.initFilterParameterSelection)
        self.modeSelectionComboBox.activated.connect(self.initFilterParameterSelection)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_2, 3, 0)
        self.innerRightLayout.addWidget(self.modeSelectionComboBox, 3, 1)
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

        mode = self.modeSelectionComboBox.currentText()
        if mode == "Timestamps":
            self.initTimestamps()
        elif mode == "Activities":
            self.initActivities()
        elif mode == "Objects":
            self.initObjects()
        elif mode == "Object Types":
            self.initObjectTypes()
        elif mode == "Event Attributes" or mode == "Object Attributes":
            self.initAttributes(mode)


    # we only consider attributes with numeric values
    def initAttributes(self, mode):
        logName = self.logSelectcomboBox1.currentText()

        if mode == "Event Attributes":
            df = self.ocel_model.getEventsDf(logName)
            if "ocel:vmap" in df.columns:
                attributesDf = df["ocel:vmap"]
            else:
                return
        else:
            df = self.ocel_model.getObjectsDf(logName)
            if "ocel:ovmap" in df.columns:
                attributesDf = df["ocel:ovmap"]
            else:
                return

        # filter out non numeric attributes
        attributes = list(attributesDf.columns)
        numericAttributes = []
        for attr in attributes:
            if is_numeric_dtype(attributesDf[attr]):
                numericAttributes.append(attr)
                
        numericAttributes.sort()

        self.boxes = []
        for i in range(len(numericAttributes)):
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(numericAttributes[i])
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            textLeft = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
            textRight = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)

            mini = min(attributesDf[numericAttributes[i]])
            maxi = max(attributesDf[numericAttributes[i]])

            textLeft.setText(str(mini))
            textRight.setText(str(maxi))

            label2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label2.setText("Enter min and max values")

            self.scrollGridLayout.addWidget(label, i+6, 0, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(checkbox, i+6, 1, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(textLeft, i+6, 3, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(textRight, i+6, 4, QtCore.Qt.AlignCenter)
            self.scrollGridLayout.addWidget(label2, i+6, 2, QtCore.Qt.AlignCenter)

            # save activity and checkbox so we can check state later
            self.boxes.append((label, checkbox, textLeft, textRight))

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
        # get min and max date from events
        logName = self.logSelectcomboBox1.currentText()
        timestamps = self.ocel_model.getEventsDf(logName)[("ocel:timestamp", "ocel:timestamp")]
        mini = min(timestamps)
        maxi = max(timestamps)
        print(mini)

        self.startDate = QtWidgets.QDateTimeEdit(self.scrollAreaWidgetContents)
        self.endDate = QtWidgets.QDateTimeEdit(self.scrollAreaWidgetContents)
        mini = QtCore.QDateTime.fromString(str(mini), 'yyyy-MM-dd hh:mm:ss')
        maxi = QtCore.QDateTime.fromString(str(maxi), 'yyyy-MM-dd hh:mm:ss')

        self.startDate.setDateTime(mini)
        self.endDate.setDateTime(maxi)
        self.scrollGridLayout.addWidget(self.startDate, 6, 0)
        self.scrollGridLayout.addWidget(self.endDate, 6, 1)


    def resetParameters(self):
        # add frame/layout/scrollArea for parameter selections and just clear this...
        for i in reversed(range(self.scrollGridLayout.count())): 
            self.scrollGridLayout.itemAt(i).widget().deleteLater()
    

    def getParameters(self):
        name = self.logSelectcomboBox1.currentText()
        
        mode = self.modeSelectionComboBox.currentText()

        filterParameters = ""
        if mode == "Activities" or mode == "Objects" or mode == "Object Types":
            filterParameters = set()
            for label, checkbox in self.boxes:
                if checkbox.isChecked():
                    filterParameters.add(label.text())
        elif mode == "Event Attributes" or mode == "Object Attributes":
            filterParameters = {}
            for attribute, checkbox, textLeft, textRight in self.boxes:
                if checkbox.isChecked() and len(textLeft.text()) != 0 and len(textRight.text()) != 0:
                    filterParameters[attribute.text()] = (textLeft.text(), textRight.text())
        elif mode == "Timestamps":
            start = datetime.datetime.strptime(self.startDate.text(), '%m/%d/%y %H:%M %p')
            end = datetime.datetime.strptime(self.endDate.text(), '%m/%d/%y %H:%M %p')
            filterParameters = (start, end)
        
        return {"name" : name, "mode" : mode, "filterParameters" : filterParameters, }
        


    def getNewLog(self, newName, parameters={}):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        if len(parameters) == 0:
            parameters = self.getParameters()
        
        name = parameters["name"]
        filterParameters = parameters["filterParameters"]
        mode = parameters["mode"]

        return self.ocel_model.filterLog(name, filterParameters, mode, newName=newName)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.modeSelectionComboBox.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])

        modes = ["Activities", "Event Attributes", "Object Attributes", "Objects", "Object Types", "Timestamps"]
        for i in range(len(modes)):
            self.modeSelectionComboBox.addItem("")
            self.modeSelectionComboBox.setItemText(i, modes[i])
        
        self.initFilterParameterSelection()
