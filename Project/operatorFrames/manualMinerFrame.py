from PyQt5 import QtCore, QtGui, QtWidgets

from operatorFrames.operatorFrame import OperatorFrame

class ManualMinerFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        self.numActLabel = QtWidgets.QLabel(self.operatorFrame)
        self.numActLabel.setFont(self.normalFont)
        
        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)

        self.logSelectcomboBox1.activated.connect(self.initCounter)
        self.logSelectcomboBox2.activated.connect(self.initCounter)
        
        self.logSelectionLabel2 = QtWidgets.QLabel(self.operatorFrame)
        self.logSelectionLabel2.setFont(self.normalFont)

        self.selectActivitiesLabel = QtWidgets.QLabel(self.operatorFrame)
        self.selectActivitiesLabel.setFont(self.normalFont)

        self.numOfActComboBox = QtWidgets.QComboBox(self.operatorFrame)
        self.numOfActComboBox.activated.connect(self.initActivitySelectors)

        self.mergeEventsLabel = QtWidgets.QLabel(self.operatorFrame)
        self.mergeEventsLabel.setFont(self.normalFont)
        self.mergeEventsCheckBox = QtWidgets.QCheckBox(self.operatorFrame)
        self.mergeEventsCheckBox.setChecked(False)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.logSelectionLabel2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.numActLabel, 4, 0)
        self.innerRightLayout.addWidget(self.numOfActComboBox, 4, 1)
        self.innerRightLayout.addWidget(self.mergeEventsLabel, 5, 0)
        self.innerRightLayout.addWidget(self.mergeEventsCheckBox, 5, 1)        
        self.innerRightLayout.addWidget(self.selectActivitiesLabel, 6, 0)

        self.activityComboBoxes = []

        self.logSelectionLabel1.setText("Select first event log:")
        self.logSelectionLabel2.setText("Select second event log:")
        self.numActLabel.setText("Select number of activities to match:")
        self.mergeEventsLabel.setText("Merge all events from 2nd log:")
        self.selectActivitiesLabel.setText("Match activities:")

        # scroll area for activity matching
        self.scrollArea = QtWidgets.QScrollArea(self.operatorFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.innerRightLayout.addWidget(self.scrollArea, 6, 0, 1, 2)
    
        self.refresh()


    def initCounter(self):
        self.numOfActComboBox.clear()

        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()

        # get set of all activities in both logs
        activities1 = set(self.ocel_model.getEventsDf(name1)[("ocel:activity", "ocel:activity")])
        activities2 = set(self.ocel_model.getEventsDf(name2)[("ocel:activity", "ocel:activity")])

        length = len(activities1) * len(activities2)
        for i in range(length):
            self.numOfActComboBox.addItem("")
            self.numOfActComboBox.setItemText(i, str(i+1))

        self.initActivitySelectors()


    def initActivitySelectors(self):

        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()

        # clear all to begin with
        for i in reversed(range(self.scrollGridLayout.count())): 
            self.scrollGridLayout.itemAt(i).widget().setParent(None)

        self.activityComboBoxes = []
        if self.numOfActComboBox.currentText():
            for i in range(int(self.numOfActComboBox.currentText())):
                label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
                label.setText(str(i+1))
                self.scrollGridLayout.addWidget(label, i+6, 0, 1, 1)
                leftActivityComboBox = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                self.scrollGridLayout.addWidget(leftActivityComboBox, i+6, 1, 1, 4)
                rightActivityComboBox = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                self.scrollGridLayout.addWidget(rightActivityComboBox, i+6, 5, 1, 4)
                self.activityComboBoxes.append((leftActivityComboBox, rightActivityComboBox))
        
        # get set of all activities in both logs
        activities1 = set(self.ocel_model.getEventsDf(name1)[("ocel:activity", "ocel:activity")])
        activities2 = set(self.ocel_model.getEventsDf(name2)[("ocel:activity", "ocel:activity")])

        activities1 = list(activities1)
        activities1.sort()
        activities2 = list(activities2)
        activities2.sort()

        for num in range(len(self.activityComboBoxes)):
            tup = self.activityComboBoxes[num]
            for i in range(len(activities1)):
                tup[0].addItem("")
                tup[0].setItemText(i, activities1[i])
            if len(activities1) != 0:
                tup[0].setCurrentIndex(num % len(activities1))

            for i in range(len(activities2)):
                tup[1].addItem("")
                tup[1].setItemText(i, activities2[i])
            if len(activities2) != 0:
                tup[1].setCurrentIndex(num % len(activities2))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)


    def getParameters(self):
        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()

        # get activity relation from comboboxes
        activity_relation = set()
        for tup in self.activityComboBoxes:
            relation = (tup[0].currentText(), tup[1].currentText())
            activity_relation.add(relation)
        activity_relation = list(activity_relation)
        activity_relation.sort()

        mergeEvents = self.mergeEventsCheckBox.isChecked()
        return {"name1" : name1, "name2" : name2, "activity_relation" : activity_relation, "mergeEvents": mergeEvents}


    def getNewLog(self, newName, parameters={}):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        if len(parameters) == 0:
            parameters = self.getParameters()
        
        name1 = parameters["name1"]
        name2 = parameters["name2"]
        activity_relation = parameters["activity_relation"]
        mergeEvents = parameters["mergeEvents"]

        return self.ocel_model.manualMiner(name1, name2, activity_relation, mergeEvents, newName=newName)


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

        self.initCounter()
        self.initActivitySelectors()
