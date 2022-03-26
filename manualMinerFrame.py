from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrame import OperatorFrame
from operators import manualMiner

class ManualMinerFrame(OperatorFrame):
 
    def __init__(self, parent, ocel, title):
        description = "Merge events across logs based on manual matching of activities of logs."
        miner = manualMiner
        super().__init__(parent, ocel, title, description, miner)


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

        self.refresh()

    def initCounter(self):
        self.numOfActComboBox.clear()

        # get set of all activities in both logs
        activities1 = set()
        for k, v in self.ocel_model.ocels[self.logSelectcomboBox1.currentText()]["ocel:events"].items():
            activities1.add(v["ocel:activity"])

        activities2 = set()
        for k, v in self.ocel_model.ocels[self.logSelectcomboBox2.currentText()]["ocel:events"].items():
            activities2.add(v["ocel:activity"])

        for i in range(len(activities1) * len(activities2)):
            self.numOfActComboBox.addItem("")
            self.numOfActComboBox.setItemText(i, str(i+1))


    def initActivitySelectors(self):

        # clear all to begin with
        for tup in self.activityComboBoxes:
            for i in tup:
                i.setParent(None)

        self.activityComboBoxes = []
        for i in range(int(self.numOfActComboBox.currentText())):
            leftActivityComboBox = QtWidgets.QComboBox(self.operatorFrame)
            self.innerRightLayout.addWidget(leftActivityComboBox, i+6, 0)
            rightActivityComboBox = QtWidgets.QComboBox(self.operatorFrame)
            self.innerRightLayout.addWidget(rightActivityComboBox, i+6, 1)
            self.activityComboBoxes.append((leftActivityComboBox, rightActivityComboBox))
        
        # get set of all activities in both logs
        activities1 = set()
        for k, v in self.ocel_model.ocels[self.logSelectcomboBox1.currentText()]["ocel:events"].items():
            activities1.add(v["ocel:activity"])

        activities2 = set()
        for k, v in self.ocel_model.ocels[self.logSelectcomboBox2.currentText()]["ocel:events"].items():
            activities2.add(v["ocel:activity"])

        for tup in self.activityComboBoxes:
            for i in range(len(activities1)):
                tup[0].addItem("")
                tup[0].setItemText(i, list(activities1)[i])

            for i in range(len(activities2)):
                tup[1].addItem("")
                tup[1].setItemText(i, list(activities2)[i])


    def getNewLog(self):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()
        log1 = self.ocel_model.ocels[name1]
        log2 = self.ocel_model.ocels[name2]

        # get activity relation from comboboxes
        activity_relation = set()
        for tup in self.activityComboBoxes:
            relation = (tup[0].currentText(), tup[1].currentText())
            activity_relation.add(relation)
        activity_relation = list(activity_relation)

        name = "MANUAL_MINER (" + name1 + ", " + name2 + ")" + " on " + "(" + str(activity_relation) + ")"
        if name in self.ocel_model.ocels:
            return
        newLog = self.miner(log1, log2, self.ocel_model.obj_relation, activity_relation)

        return (name, newLog)

    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        for i in range(len(self.ocel_model.ocels.keys())):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox1.setItemText(i, list(self.ocel_model.ocels.keys())[i])
            self.logSelectcomboBox2.setItemText(i, list(self.ocel_model.ocels.keys())[i])

        self.initCounter()
        self.initActivitySelectors()
