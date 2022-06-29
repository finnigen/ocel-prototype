from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrames.operatorFrame import OperatorFrame
from operators import manualMiner

class ManualMinerFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)


        self.operatorSelectorLabel_1 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_1.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_1.setFont(font)
        self.operatorSelectorLabel_1.setObjectName("operatorSelectorLabel_1")
        self.operatorSelectorLabel_3 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_3.setEnabled(True)
        self.operatorSelectorLabel_3.setFont(font)
        self.operatorSelectorLabel_3.setObjectName("operatorSelectorLabel_3")
        
        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox1.setObjectName("logSelectcomboBox1")

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox2.setObjectName("logSelectcomboBox2")

        self.logSelectcomboBox1.activated.connect(self.initCounter)
        self.logSelectcomboBox2.activated.connect(self.initCounter)
        
        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_2.setEnabled(True)

        self.operatorSelectorLabel_2.setFont(font)
        self.operatorSelectorLabel_2.setObjectName("operatorSelectorLabel_2")

        self.selectActivitiesLabel = QtWidgets.QLabel(self.operatorFrame)
        self.selectActivitiesLabel.setFont(font)
        self.selectActivitiesLabel.setObjectName("selectActivitiesLabel")

        self.numOfActComboBox = QtWidgets.QComboBox(self.operatorFrame)
        self.numOfActComboBox.setObjectName("numOfActComboBox")
        self.numOfActComboBox.activated.connect(self.initActivitySelectors)


        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_3, 4, 0)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_3, 4, 0)
        self.innerRightLayout.addWidget(self.numOfActComboBox)
        self.innerRightLayout.addWidget(self.selectActivitiesLabel)

        self.activityComboBoxes = []

        self.operatorSelectorLabel_1.setText("Select first event log:")
        self.operatorSelectorLabel_2.setText("Select second event log:")
        self.operatorSelectorLabel_3.setText("Select number of activities to match:")
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
        for tup in self.activityComboBoxes:
            for i in tup:
                i.setParent(None)

        self.activityComboBoxes = []
        for i in range(int(self.numOfActComboBox.currentText())):
            leftActivityComboBox = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
            self.scrollGridLayout.addWidget(leftActivityComboBox, i+6, 0)
            rightActivityComboBox = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
            self.scrollGridLayout.addWidget(rightActivityComboBox, i+6, 1)
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
            tup[0].setCurrentIndex(num)

            for i in range(len(activities2)):
                tup[1].addItem("")
                tup[1].setItemText(i, activities2[i])
            tup[1].setCurrentIndex(num)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)



    def getNewLog(self, newName):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()

        # get activity relation from comboboxes
        activity_relation = set()
        for tup in self.activityComboBoxes:
            relation = (tup[0].currentText(), tup[1].currentText())
            activity_relation.add(relation)
        activity_relation = list(activity_relation)
        activity_relation.sort()

        return self.ocel_model.manualMiner(name1, name2, activity_relation, newName=newName)


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
