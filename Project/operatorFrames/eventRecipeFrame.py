from PyQt5 import QtCore, QtGui, QtWidgets

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
        font.setPointSize(15)
        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.operatorSelectorLabel_2.setFont(font)

        self.seqLengthComboBox = QtWidgets.QComboBox(self.outerScrollAreaWidgetContents)

        self.parameterLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.parameterLabel.setFont(font)

        self.logSelectcomboBox1.activated.connect(self.initSequenceSelection)
        self.seqLengthComboBox.activated.connect(self.initSequenceSelection)

        self.directlyFollowsCheckbox = QtWidgets.QCheckBox(self.outerScrollAreaWidgetContents)
        self.directlyFollowsCheckbox.setChecked(True)
        self.directlyFollowsLabel = QtWidgets.QLabel(self.outerScrollAreaWidgetContents)
        self.directlyFollowsLabel.setFont(font)
        self.directlyFollowsLabel.setText("Events in directly follows relation (else: eventually)")

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

        self.timedeltaCheckText.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))

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

        self.outerScrollGridLayout.addWidget(self.newActivityNameLabel, 5, 0, 1, 2)
        self.outerScrollGridLayout.addWidget(self.newActivityNameText, 5, 2, 1, 2)
        self.outerScrollGridLayout.addWidget(self.timedeltaCheckLabel, 6, 1, 1, 2)
        self.outerScrollGridLayout.addWidget(self.timedeltaCheckText, 6, 2, 1, 1)
        self.outerScrollGridLayout.addWidget(self.timedeltaCheckbox, 6, 0, 1, 1)

        self.outerScrollGridLayout.addWidget(self.matchObjectTypesLabel, 7, 1)
        self.outerScrollGridLayout.addWidget(self.matchObjectTypesCheckbox, 7, 0)
        self.outerScrollGridLayout.addWidget(self.objectTypeFrame, 7, 2, 1, 2)
        
        self.outerScrollGridLayout.addWidget(self.matchAttributesLabel, 9, 1)
        self.outerScrollGridLayout.addWidget(self.matchAttributesCheckbox, 9, 0)
        self.outerScrollGridLayout.addWidget(self.attributeFrame, 9, 2, 1, 2)

        self.outerScrollGridLayout.addWidget(self.findAllLabel, 10, 1)
        self.outerScrollGridLayout.addWidget(self.findAllCheckbox, 10, 0)

        self.outerScrollGridLayout.addWidget(self.directlyFollowsLabel, 11, 1)
        self.outerScrollGridLayout.addWidget(self.directlyFollowsCheckbox, 11, 0)

        # spacing line
        self.outerScrollGridLayout.addWidget(QtWidgets.QLabel(self.outerScrollAreaWidgetContents), 12, 0)

        self.outerScrollGridLayout.addWidget(self.operatorSelectorLabel_2, 13, 0, 1, 2)
        self.outerScrollGridLayout.addWidget(self.seqLengthComboBox, 13, 2, 1, 2)

        self.outerScrollGridLayout.addWidget(self.parameterLabel, 14, 0, 1, 4)


        self.logSelectionLabel1.setText("Select event log:")
        self.operatorSelectorLabel_2.setText("Select number of events in desired sequence:")
        self.parameterLabel.setText("Specify event filters for each event in sequence")

        # scroll area for sequence selection
        self.scrollArea = QtWidgets.QScrollArea(self.outerScrollAreaWidgetContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumHeight(200)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.outerScrollGridLayout.addWidget(self.scrollArea, 15, 0, 1, 4)
        
        # tool tips
        self.newActivityNameLabel.setToolTip("Events that match specified pattern will be replaced by new event with this activity.")
        self.newActivityNameText.setToolTip("Events that match specified pattern will be replaced by new event with this activity.")
        self.timedeltaCheckLabel.setToolTip("This is the time maximum that is allowed between the 1st and last event in the sequence specified below.")
        self.timedeltaCheckText.setToolTip("This is the maximum time that is allowed between the 1st and last event in the sequence specified below.")
        self.timedeltaCheckbox.setToolTip("Check this to activate the time filter.")
        self.matchObjectTypesLabel.setToolTip("Ell events in sequence must have at least one of the same objects of each specified object type.")
        self.objectTypeFrame.setToolTip("Ell events in sequence must have at least one of the same objects of each specified object type.")
        self.matchObjectTypesCheckbox.setToolTip("Check this to activate object type filter.") 
        self.matchAttributesLabel.setToolTip("All events in sequence must have matching values for the specified attributes.")
        self.attributeFrame.setToolTip("All events in sequence must have matching values for the specified attributes.")
        self.matchAttributesCheckbox.setToolTip("Check this to activate attribute filter.")
        self.findAllLabel.setToolTip("If unchecked, an event may only be used to form a sequence once. If checked, events can be re-used to form multiple sequences. Note that checking this, can lead to long waiting times.")
        self.findAllCheckbox.setToolTip("If unchecked, an event may only be used to form a sequence once. If checked, events can be re-used to form multiple sequences. Note that checking this, can lead to long waiting times.")
        self.directlyFollowsLabel.setToolTip("If checked, events must be directly following each other. If unchecked, other events may occur inbetween.")
        self.directlyFollowsCheckbox.setToolTip("If checked, events must be directly following each other. If unchecked, other events may occur inbetween.")
        self.parameterLabel.setToolTip("Specify sequence of activities used to identify events.")
        self.seqLengthComboBox.setToolTip("Longer sequences can be computationally expensive. Longer waiting times are to be expected.")

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
        seqLength = int(self.seqLengthComboBox.currentText())     

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
            seqFrameLayout.addWidget(label, 0, 0, 1, 1)
            
            leftActivityComboBox = QtWidgets.QComboBox(seqFrame)
            leftActivityComboBox.setToolTip("Specify which activity this event has.")

            seqFrameLayout.addWidget(leftActivityComboBox, 0, 1, 1, 3)
            for j in range(len(activities)):
                leftActivityComboBox.addItem("")
                leftActivityComboBox.setItemText(j, activities[j])
            if len(activities) != 0:
                leftActivityComboBox.setCurrentIndex(i % len(activities))

            objectBoxes = []
            for j in range(len(objectTypes)):
                label = QtWidgets.QLabel(seqFrame)
                label.setText(objectTypes[j])
                checkbox = QtWidgets.QCheckBox(seqFrame)
                checkbox.setChecked(False)
                seqFrameLayout.addWidget(label, j, 4, QtCore.Qt.AlignCenter)
                seqFrameLayout.addWidget(checkbox, j, 5, QtCore.Qt.AlignCenter)

                # set tool tips
                label.setToolTip("Check this to ensure that this event contains at least one object of type " + objectTypes[j])
                checkbox.setToolTip("Check this to ensure that this event contains at least one object of type " + objectTypes[j])

                # save activity and checkbox so we can check state later
                objectBoxes.append((label, checkbox))

            self.seqBoxes.append((leftActivityComboBox, objectBoxes))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

    
    def reset(self, layout):
        # add frame/layout/scrollArea for parameter selections and just clear this...
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().deleteLater()
        

    def getParameters(self):
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

        return {"name" : name, "newActivityName" : newActivityName, "sequence" : sequence, "time" : time, "matchOnObjectTypes" : matchOnObjectTypes, "matchOnAttributes" : matchOnAttributes, "findAll" : findAll, "directly" : directly}
        


    def getNewLog(self, newName, parameters={}):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        if len(parameters) == 0:
            parameters = self.getParameters()

        name = parameters["name"]
        newActivityName = parameters["newActivityName"]
        sequence = parameters["sequence"]
        time = parameters["time"]
        matchOnObjectTypes = parameters["matchOnObjectTypes"]
        matchOnAttributes = parameters["matchOnAttributes"]
        findAll = parameters["findAll"]
        directly = parameters["directly"]

        return self.ocel_model.eventRecipe(name, newActivityName, sequence, time, matchOnObjectTypes, matchOnAttributes, findAll, directly, newName)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.seqLengthComboBox.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])

        for i in range(5):
            self.seqLengthComboBox.addItem("")
            self.seqLengthComboBox.setItemText(i, str(i+1))
        
        self.initSequenceSelection()