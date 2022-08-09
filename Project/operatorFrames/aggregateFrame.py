from PyQt5 import QtCore, QtGui, QtWidgets

from operatorFrames.operatorFrame import OperatorFrame

class AggregateFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        self.logSelectionLabel1.setText("Select event log:")
        self.logSelectcomboBox1.activated.connect(self.initCounter)

        self.numOfMatchesLabel = QtWidgets.QLabel(self.operatorFrame)
        self.numOfMatchesLabel.setFont(self.normalFont)

        self.numOfMatchesComboBox = QtWidgets.QComboBox(self.operatorFrame)
        self.numOfMatchesComboBox.activated.connect(self.initPropertiesSelectors)

        self.innerRightLayout.addWidget(self.numOfMatchesLabel, 3, 0)
        self.innerRightLayout.addWidget(self.numOfMatchesComboBox, 3, 1)

        # scroll area for matching columns
        self.scrollArea = QtWidgets.QScrollArea(self.operatorFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.innerRightLayout.addWidget(self.scrollArea, 4, 0, 1, 2)

        self.numOfMatchesLabel.setText("Select number of properties to aggregate on:")
        self.scrollAreaWidgetContents.setToolTip("Objects related to events where all these specified attributes match will be merged into first occurence of event.")

        self.propertyComboBoxes = []

        self.refresh()
 


    def initCounter(self):
        self.numOfMatchesComboBox.clear()

        name1 = self.logSelectcomboBox1.currentText()

        # get number of columns in both logs (minus omap)
        properties1 = len(self.ocel_model.getEventsDf(name1).columns) - 1

        for i in range(properties1):
            self.numOfMatchesComboBox.addItem("")
            self.numOfMatchesComboBox.setItemText(i, str(i+1))

        self.initPropertiesSelectors()


    def initPropertiesSelectors(self):

        name1 = self.logSelectcomboBox1.currentText()

        # clear all to begin with
        for i in reversed(range(self.scrollGridLayout.count())): 
            self.scrollGridLayout.itemAt(i).widget().setParent(None)

        df1 = self.ocel_model.getEventsDf(name1)

        properties1 = list(set(df1.columns).difference([("ocel:omap", "ocel:omap")]))
        properties1 = [c[1] for c in properties1]
        properties1.sort()

        self.propertyComboBoxes = []
        if self.numOfMatchesComboBox.currentText():
            for i in range(int(self.numOfMatchesComboBox.currentText())):
                label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
                label.setText(str(i+1))
                self.scrollGridLayout.addWidget(label, i+6, 0, 1, 1)
                leftPropertyComboBox = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                self.scrollGridLayout.addWidget(leftPropertyComboBox, i+6, 1, 1, 4)
                self.propertyComboBoxes.append((leftPropertyComboBox))

        for num in range(len(self.propertyComboBoxes)):
            box = self.propertyComboBoxes[num]
            for i in range(len(properties1)):
                box.addItem("")
                box.setItemText(i, properties1[i])
            if len(properties1) != 0:
                box.setCurrentIndex(num % len(properties1[i]))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)


    def getParameters(self):
        name = self.logSelectcomboBox1.currentText()

        aggregateBy = []
        for box in self.propertyComboBoxes:
            left = box.currentText()
            if left == "ocel:activity":
                left = ("ocel:activity", "ocel:activity")
            elif left == "ocel:timestamp":
                left = ("ocel:timestamp", "ocel:timestamp")
            else:
                left = ("ocel:vmap", left)

            aggregateBy.append(left)

        return {"name" : name, "aggregateBy" : aggregateBy}


    def getNewLog(self, newName, parameters={}):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        if len(parameters) == 0:
            parameters = self.getParameters()

        name = parameters["name"]
        aggregateBy = parameters["aggregateBy"]

        return self.ocel_model.aggregate(name, aggregateBy=aggregateBy, newName=newName)


    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters

        self.logSelectcomboBox1.clear()

        names = list(self.ocel_model.getOcelNames())
        names.sort()

        for i in range(len(names)):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox1.setItemText(i, names[i])

        self.initCounter()
        self.initPropertiesSelectors()