from PyQt5 import QtCore, QtGui, QtWidgets

from operatorFrames.operatorFrame import OperatorFrame

class IntersectionFrame(OperatorFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__(parent, ocel_model, title, description)

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)

        self.logSelectionLabel2 = QtWidgets.QLabel(self.operatorFrame)
        self.logSelectionLabel2.setFont(self.normalFont)

        self.logSelectcomboBox1.activated.connect(self.initCounter)
        self.logSelectcomboBox2.activated.connect(self.initCounter)

        self.numOfMatchesLabel = QtWidgets.QLabel(self.operatorFrame)
        self.numOfMatchesLabel.setFont(self.normalFont)

        self.numOfMatchesComboBox = QtWidgets.QComboBox(self.operatorFrame)
        self.numOfMatchesComboBox.activated.connect(self.initPropertiesSelectors)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.logSelectionLabel2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.numOfMatchesLabel, 4, 0)
        self.innerRightLayout.addWidget(self.numOfMatchesComboBox, 4, 1)

        self.logSelectionLabel1.setText("Select 1st event log:")
        self.logSelectionLabel2.setText("Select 2nd event log:")
        self.numOfMatchesLabel.setText("Select number of properties to match on:")
        self.numOfMatchesLabel.setWordWrap(True)

        # scroll area for matching columns
        self.scrollArea = QtWidgets.QScrollArea(self.operatorFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.innerRightLayout.addWidget(self.scrollArea, 5, 0, 1, 2)

        self.scrollAreaWidgetContents.setToolTip("Select which attributes of 1st log (left) should be matched with attributes of 2nd log (right) (can only match attributes of same type)")

        self.propertyComboBoxes = []

        self.refresh()
 


    def initCounter(self):
        self.numOfMatchesComboBox.clear()

        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()

        # get number of columns in both logs (minus omap)
        properties1 = len(self.ocel_model.getEventsDf(name1).columns) - 1
        properties2 = len(self.ocel_model.getEventsDf(name2).columns) - 1

        for i in range(min([properties1, properties2])):
            self.numOfMatchesComboBox.addItem("")
            self.numOfMatchesComboBox.setItemText(i, str(i+1))

        self.initPropertiesSelectors()


    def initPropertiesSelectors(self):

        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()

        # clear all to begin with
        for i in reversed(range(self.scrollGridLayout.count())): 
            self.scrollGridLayout.itemAt(i).widget().setParent(None)

        df1 = self.ocel_model.getEventsDf(name1)
        df2 = self.ocel_model.getEventsDf(name2)
        df2.drop(("ocel:omap", "ocel:omap"), axis=1, inplace=True)

        properties1 = set(df1.columns).difference([("ocel:omap", "ocel:omap")])

        # find which columns could be matched based on types and flatten multiindex column names
        self.matchingColumns = {}
        for column in properties1:
            self.matchingColumns[column[1]] = [c[1] for c in df2.select_dtypes(df1[column].dtype).columns]
            self.matchingColumns[column[1]].sort()

        self.propertyComboBoxes = []
        if self.numOfMatchesComboBox.currentText():
            for i in range(int(self.numOfMatchesComboBox.currentText())):
                label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
                label.setText(str(i+1))
                self.scrollGridLayout.addWidget(label, i+6, 0, 1, 1)
                leftPropertyComboBox = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                leftPropertyComboBox.activated.connect(lambda checked, x=i : self.adjustRightComboBox(x))
                self.scrollGridLayout.addWidget(leftPropertyComboBox, i+6, 1, 1, 4)
                rightPropertyComboBox = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                self.scrollGridLayout.addWidget(rightPropertyComboBox, i+6, 5, 1, 4)
                self.propertyComboBoxes.append((leftPropertyComboBox, rightPropertyComboBox))
        
        keys = list(self.matchingColumns.keys())
        keys.sort()

        for num in range(len(self.propertyComboBoxes)):
            tup = self.propertyComboBoxes[num]
            for i in range(len(keys)):
                tup[0].addItem("")
                tup[0].setItemText(i, keys[i])
            if len(keys) != 0:
                tup[0].setCurrentIndex(num % len(keys[i]))
                self.adjustRightComboBox(num)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    

    def adjustRightComboBox(self, num):
        currentText = self.propertyComboBoxes[num][0].currentText()
        values = self.matchingColumns[currentText]
        rightComboBox = self.propertyComboBoxes[num][1]
        rightComboBox.clear()
        for i in range(len(values)):
            rightComboBox.addItem("")
            rightComboBox.setItemText(i, values[i])


    def getParameters(self):
        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()
        matchOn = {}
        for tup in self.propertyComboBoxes:
            left = tup[0].currentText()
            right = tup[1].currentText()
            if left == "ocel:activity":
                left = ("ocel:activity", "ocel:activity")
            elif left == "ocel:timestamp":
                left = ("ocel:timestamp", "ocel:timestamp")
            else:
                left = ("ocel:vmap", left)
            if right == "ocel:activity":
                right = ("ocel:activity", "ocel:activity")
            elif right == "ocel:timestamp":
                right = ("ocel:timestamp", "ocel:timestamp")
            else:
                right = ("ocel:vmap", right)

            matchOn[left] = right

        return {"name1" : name1, "name2" : name2, "matchOn" : matchOn}


    def getNewLog(self, newName, parameters={}):
        # returns new log that is created by applying given operator with selected parameters + name
        # this is used for the "add to logs" and "export" button in the main window
        
        if len(parameters) == 0:
            parameters = self.getParameters()
        
        name1 = parameters["name1"]
        name2 = parameters["name2"]
        matchOn = parameters["matchOn"]

        return self.ocel_model.intersection(name1, name2, matchOn=matchOn, newName=newName)

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
        self.initPropertiesSelectors()