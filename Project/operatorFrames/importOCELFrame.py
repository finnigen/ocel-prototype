from PyQt5 import QtCore, QtGui, QtWidgets
from helpWindow import HelpWindow

from ocel_converter import convertToOcelModel, OCEL_Model


class ImportOCELFrame(QtWidgets.QFrame):
 
    def __init__(self, parent, ocel_model, title, description, tutorialPic="overviewTutorial.png"):
        super().__init__()
        self.parent = parent
        self.ocel_model = ocel_model
        self.title = title
        self.description = description
        self.tutorialPic = tutorialPic

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.operatorFrame = QtWidgets.QFrame(self.parent)
        self.operatorFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.operatorFrame.setFrameShadow(QtWidgets.QFrame.Raised)

        # set inner layout of right area
        self.innerRightLayout = QtWidgets.QGridLayout(self.operatorFrame)

        self.operatorTitleLabel = QtWidgets.QLabel(self.operatorFrame)
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.operatorTitleLabel.setFont(font)

        # help button for operator
        helpButton = QtWidgets.QPushButton(self.operatorFrame)
        helpButton.setText("Help")
        helpButton.clicked.connect(lambda : self.helpWindow(self.tutorialPic))
        
        self.operatorDescriptionLabel = QtWidgets.QLabel(self.operatorFrame)
        self.operatorDescriptionLabel.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.normalFont = font
        self.operatorDescriptionLabel.setFont(self.normalFont)
    #    self.operatorDescriptionLabel.setMinimumWidth(750)
        self.operatorDescriptionLabel.setWordWrap(True)

        self.extractObjRelCheckbox = QtWidgets.QCheckBox(self.operatorFrame)
        self.extractObjRelLabel = QtWidgets.QLabel(self.operatorFrame)
        self.extractObjRelLabel.setText("Extract object relationships from events of new log and add to list of object relationships (can be useful in case future operator application is desired)")
        self.extractObjRelLabel.setWordWrap(True)
        self.extractObjRelLabel.setFont(self.normalFont)
        self.extractObjRelLabel.setToolTip("If unchecked, we only add reflexive relation. If checked, we consider all objects named in same events in relation with each other.")
        self.extractObjRelCheckbox.setToolTip("If unchecked, we only add reflexive relation. If checked, we consider all objects named in same events in relation with each other.")


        self.ocelPathText = QtWidgets.QLineEdit(self.operatorFrame)
        self.ocelPathText.setReadOnly(True)
        self.ocelPathButton = QtWidgets.QPushButton(self.operatorFrame)
        self.ocelPathButton.setText("Choose OCEL file")
        self.ocelPathButton.clicked.connect(self.openFileNameDialog)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorTitleLabel, 0, 0, 1, 0, QtCore.Qt.AlignCenter)
        self.innerRightLayout.addWidget(helpButton, 0, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.innerRightLayout.addWidget(self.operatorDescriptionLabel, 1, 0, 1, 0)
        self.innerRightLayout.addWidget(self.extractObjRelLabel, 2, 0)
        self.innerRightLayout.addWidget(self.extractObjRelCheckbox, 2, 1)

        self.innerRightLayout.addWidget(self.ocelPathText, 3, 0) 
        self.innerRightLayout.addWidget(self.ocelPathButton, 3, 1)

        self.innerRightLayout.setAlignment(QtCore.Qt.AlignVCenter)
        self.innerRightLayout.setSpacing(30)

        self.layout.addWidget(self.operatorFrame)

        self.operatorTitleLabel.setText(self.title)

        self.operatorDescriptionLabel.setText(self.description)

        self.openedWindows = {}
    
    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Choose OCEL File", "","JSON Files (*.json);;JSONOCEL Files (*.jsonocel)", options=options)
        if fileName:
            self.ocelPathText.setText(fileName)

    def helpWindow(self, tutorialPic):
        if "helpWindow" not in self.openedWindows:
            newWindow = HelpWindow("tutorialPics/" + tutorialPic)
            self.openedWindows["helpWindow"] = newWindow
        self.openedWindows["helpWindow"].show()

    def getParameters(self):
        return {"addObjectRelations" : self.extractObjRelCheckbox.isChecked(), "path" : self.ocelPathText.text()}

    def getNewLog(self, newName, parameters = {}):

        if len(parameters) == 0:
            parameters = self.getParameters()
        
        path = parameters["path"]
        addObjectRelations = parameters["addObjectRelations"]

        return self.ocel_model.importOCEL(path, addObjectRelations=addObjectRelations, newName=newName)

    def refresh(self):
        self.ocelPathText.setText("")