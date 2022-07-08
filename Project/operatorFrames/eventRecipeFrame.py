from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrames.operatorFrame import OperatorFrame
from datetime import timedelta

class EventRecipeFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        self.outerScrollArea = QtWidgets.QScrollArea(self.operatorFrame)
        self.outerScrollArea.setWidgetResizable(True)
        self.outerScrollAreaWidgetContents = QtWidgets.QWidget()
        self.outerScrollGridLayout = QtWidgets.QGridLayout(self.outerScrollAreaWidgetContents)
        self.outerScrollArea.setWidget(self.outerScrollAreaWidgetContents)
        self.innerRightLayout.addWidget(self.outerScrollArea, 6, 0, 1, 2)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_1 = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.operatorSelectorLabel_1.setEnabled(True)
        self.operatorSelectorLabel_1.setFont(font)
        self.operatorSelectorLabel_1.setObjectName("operatorSelectorLabel_1")
        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.operatorSelectorLabel_2.setEnabled(True)
        self.operatorSelectorLabel_2.setFont(font)
        self.operatorSelectorLabel_2.setObjectName("operatorSelectorLabel_2")

        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.outerScrollAreaWidgetContents)
        self.logSelectcomboBox1.setObjectName("logSelectcomboBox1")

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.outerScrollAreaWidgetContents)
        self.logSelectcomboBox2.setObjectName("logSelectcomboBox2")

        self.parameterLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.parameterLabel.setFont(font)

        self.logSelectcomboBox1.activated.connect(self.initSequenceSelection)
        self.logSelectcomboBox2.activated.connect(self.initSequenceSelection)

        self.directlyFollowsCheckbox = QtWidgets.QCheckBox(self.outerScrollAreaWidgetContents)
        self.directlyFollowsCheckbox.setChecked(True)
        self.directlyFollowsLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.directlyFollowsLabel.setFont(font)
        self.directlyFollowsLabel.setText("Events in directly follows relation")

        self.newActivityNameLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.newActivityNameLabel.setFont(font)
        self.newActivityNameLabel.setText("Enter name for new activity")
        self.newActivityNameText = QtWidgets.QLineEdit(self.outerScrollAreaWidgetContents)

        self.timedeltaCheckbox = QtWidgets.QCheckBox(self.outerScrollAreaWidgetContents)
        self.timedeltaCheckbox.setChecked(False)
        self.timedeltaCheckLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.timedeltaCheckLabel.setFont(font)
        self.timedeltaCheckLabel.setText("Max time between 1st and last event (in hours)")
        self.timedeltaCheckText = QtWidgets.QLineEdit(self.outerScrollAreaWidgetContents)

        self.matchObjectTypesCheckbox = QtWidgets.QCheckBox(self.outerScrollAreaWidgetContents)
        self.matchObjectTypesCheckbox.setChecked(False)
        self.matchObjectTypesCheckbox.stateChanged.connect(self.initObjectTypeSelection)
        self.matchObjectTypesLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.matchObjectTypesLabel.setFont(font)
        self.matchObjectTypesLabel.setText("Match on object types")
        self.objectTypeFrame = QtWidgets.QFrame(self.outerScrollAreaWidgetContents)
        self.objectTypeFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.objectTypeFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.objectTypeFrameLayout = QtWidgets.QGridLayout(self.objectTypeFrame)

        self.matchAttributesCheckbox = QtWidgets.QCheckBox(self.outerScrollAreaWidgetContents)
        self.matchAttributesCheckbox.setChecked(False)
        self.matchAttributesCheckbox.stateChanged.connect(self.initAttributeSelection)
        self.matchAttributesLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.matchAttributesLabel.setFont(font)
        self.matchAttributesLabel.setText("Match on attributes")
        self.attributeFrame = QtWidgets.QFrame(self.outerScrollAreaWidgetContents)
        self.attributeFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.attributeFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.attributeFrameLayout = QtWidgets.QGridLayout(self.attributeFrame)

        self.findAllCheckbox = QtWidgets.QCheckBox(self.outerScrollAreaWidgetContents)
        self.findAllCheckbox.setChecked(False)
        self.findAllLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.findAllLabel.setFont(font)
        self.findAllLabel.setText("Find all occurences of seq (reusing events allowed))")

        # add all labels, buttons etc to right layout
        self.outerScrollGridLayout.addWidget(self.operatorSelectorLabel_1, 2, 0)
        self.outerScrollGridLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.outerScrollGridLayout.addWidget(self.directlyFollowsLabel, 4, 0)
        self.outerScrollGridLayout.addWidget(self.directlyFollowsCheckbox, 4, 1)
        self.outerScrollGridLayout.addWidget(self.newActivityNameLabel, 5, 0)
        self.outerScrollGridLayout.addWidget(self.newActivityNameText, 5, 1)
        self.outerScrollGridLayout.addWidget(self.timedeltaCheckLabel, 6, 0)
        self.outerScrollGridLayout.addWidget(self.timedeltaCheckText, 6, 1)
        self.outerScrollGridLayout.addWidget(self.timedeltaCheckbox, 6, 2)
        self.outerScrollGridLayout.addWidget(self.matchObjectTypesLabel, 7, 0)
        self.outerScrollGridLayout.addWidget(self.matchObjectTypesCheckbox, 7, 1)
        self.outerScrollGridLayout.addWidget(self.objectTypeFrame, 8, 0)
        
        self.outerScrollGridLayout.addWidget(self.matchAttributesLabel, 9, 0)
        self.outerScrollGridLayout.addWidget(self.matchAttributesCheckbox, 9, 1)
        self.outerScrollGridLayout.addWidget(self.attributeFrame, 10, 0)

        self.outerScrollGridLayout.addWidget(self.findAllLabel, 11, 0)
        self.outerScrollGridLayout.addWidget(self.findAllCheckbox, 11, 1)

        self.outerScrollGridLayout.addWidget(self.operatorSelectorLabel_2, 12, 0)
        self.outerScrollGridLayout.addWidget(self.logSelectcomboBox2, 12, 1)

        self.outerScrollGridLayout.addWidget(self.parameterLabel, 13, 0)


        self.operatorSelectorLabel_1.setText("Select event log:")
        self.operatorSelectorLabel_2.setText("Select number of events in desired sequence:")
        self.parameterLabel.setText("Specify event filters for each event in sequence")

        # scroll area for sequence selection
        self.scrollArea = QtWidgets.QScrollArea(self.outerScrollAreaWidgetContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumHeight(200)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.outerScrollGridLayout.addWidget(self.scrollArea, 15, 0, 1, 2)
        
        self.refresh()

    def initAttributeSelection(self):
        self.attrCheckboxLabels = []
        if self.matchAttributesCheckbox.isChecked():
            logName = self.logSelectcomboBox1.currentText()
            attributes = list(self.ocel_model.getEventAttributes(logName))
            attributes.sort()    
            for i in range(len(attributes)):
                attr = attributes[i]
                checkbox = QtWidgets.QCheckBox(self.attributeFrame)
                checkbox.setChecked(False)
                label = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
                label.setText(attr)
                self.attrCheckboxLabels.append((checkbox, label))
                self.attributeFrameLayout.addWidget(checkbox, i, 0)
                self.attributeFrameLayout.addWidget(label, i, 1)    
        else:
            self.reset(self.attributeFrameLayout)


    def initObjectTypeSelection(self):
        self.objTypeCheckboxLabels = []
        if self.matchObjectTypesCheckbox.isChecked():
            logName = self.logSelectcomboBox1.currentText()
            objectTypes = list(self.ocel_model.getObjectTypes(logName))
            objectTypes.sort()    
            for i in range(len(objectTypes)):
                objType = objectTypes[i]
                checkbox = QtWidgets.QCheckBox(self.objectTypeFrame)
                checkbox.setChecked(False)
                
                label = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
                label.setText(objType)
                self.objTypeCheckboxLabels.append((checkbox, label))
                self.objectTypeFrameLayout.addWidget(checkbox, i, 0)
                self.objectTypeFrameLayout.addWidget(label, i, 1)    
        else:
            self.reset(self.objectTypeFrameLayout)


    def initSequenceSelection(self):
        self.reset(self.scrollGridLayout)

        # uncheck other filters
        self.matchAttributesCheckbox.setChecked(False)
        self.matchObjectTypesCheckbox.setChecked(False)

        self.seqBoxes = []
        seqLength = int(self.logSelectcomboBox2.currentText())     

        logName = self.logSelectcomboBox1.currentText()
        activities = list(set(self.ocel_model.getEventsDf(logName)[("ocel:activity", "ocel:activity")]))
        activities.sort()
        objectTypes = list(self.ocel_model.getObjectTypes(logName))
        objectTypes.sort()

        for i in range(seqLength):

            seqFrame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
            seqFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
            seqFrame.setFrameShadow(QtWidgets.QFrame.Raised)
            seqFrameLayout = QtWidgets.QGridLayout(seqFrame)
            seqFrameLayout.setSpacing(20)
            self.scrollGridLayout.addWidget(seqFrame, i, 1)

            label = QtWidgets.QLabel(seqFrame)
            label.setText(str(i+1))
            seqFrameLayout.addWidget(label, 0, 0)
            
            leftActivityComboBox = QtWidgets.QComboBox(seqFrame)
            seqFrameLayout.addWidget(leftActivityComboBox, 0, 1)
            for j in range(len(activities)):
                leftActivityComboBox.addItem("")
                leftActivityComboBox.setItemText(j, activities[j])
            leftActivityComboBox.setCurrentIndex(i)

            objectBoxes = []
            for j in range(len(objectTypes)):
                label = QtWidgets.QLabel(seqFrame)
                label.setText(objectTypes[j])
                checkbox = QtWidgets.QCheckBox(seqFrame)
                checkbox.setChecked(False)
                seqFrameLayout.addWidget(label, j, 2, QtCore.Qt.AlignCenter)
                seqFrameLayout.addWidget(checkbox, j, 3, QtCore.Qt.AlignCenter)
                # save activity and checkbox so we can check state later
                objectBoxes.append((label, checkbox))

            self.seqBoxes.append((leftActivityComboBox, objectBoxes))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

    
    def reset(self, layout):
        # add frame/layout/scrollArea for parameter selections and just clear this...
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().deleteLater()
        


    def getNewLog(self, newName):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        # name of log
        name = self.logSelectcomboBox1.currentText()

        # new activity name
        newActivityName = self.newActivityNameText.text()
        if not newActivityName:
            newActivityName = "newActivity"

        # sequence of event filters
        sequence = []
        for leftActivityComboBox, objectBoxes in self.seqBoxes:
            objectTypes = set()
            for label, checkbox in objectBoxes:
                if checkbox.isChecked():
                    objectTypes.add(label.text())
            event = {"activity" : leftActivityComboBox.currentText()}
            if objectTypes != set():
                event["objectTypes"] = objectTypes
            sequence.append(event)
        
        # time
        time = timedelta.max
        if self.timedeltaCheckbox.isChecked():
            time = timedelta(hours=(float(self.timedeltaCheckText.text())))

        # matchOnObjectTypes set
        matchOnObjectTypes = set()
        if self.matchObjectTypesCheckbox.isChecked():
            for checkbox, label in self.objTypeCheckboxLabels:
                if checkbox.isChecked():
                    matchOnObjectTypes.add(label.text())
        
        # matchOnAttributes set
        matchOnAttributes = set()
        if self.matchAttributesCheckbox.isChecked():
            for checkbox, label in self.attrCheckboxLabels:
                if checkbox.isChecked():
                    matchOnAttributes.add(label.text())

        # findAll parameter
        findAll = self.findAllCheckbox.isChecked()

        # directly parameter
        directly = self.directlyFollowsCheckbox.isChecked()

        return self.ocel_model.eventRecipe(name, newActivityName, sequence, time, matchOnObjectTypes, matchOnAttributes, findAll, directly, newName)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])

        for i in range(5):
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox2.setItemText(i, str(i+1))
        
        self.initSequenceSelection()