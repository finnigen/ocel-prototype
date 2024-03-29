from PyQt5 import QtCore, QtGui, QtWidgets
from helpWindow import HelpWindow

from ocel_converter import convertToOcelModel, OCEL_Model


class OperatorFrame(QtWidgets.QFrame):
 
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


        # combobox and label to select (1st) log that we want to apply operator too
        self.logSelectionLabel1 = QtWidgets.QLabel(self.operatorFrame)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.logSelectionLabel1.setFont(self.normalFont)
        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
        self.innerRightLayout.addWidget(self.logSelectionLabel1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorTitleLabel, 0, 0, 1, 0, QtCore.Qt.AlignCenter)
        self.innerRightLayout.addWidget(helpButton, 0, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.innerRightLayout.addWidget(self.operatorDescriptionLabel, 1, 0, 1, 0) #, QtCore.Qt.AlignHCenter)
        self.innerRightLayout.setAlignment(QtCore.Qt.AlignVCenter)
        self.innerRightLayout.setSpacing(30)

        self.layout.addWidget(self.operatorFrame)

        self.operatorTitleLabel.setText(self.title)

        self.operatorDescriptionLabel.setText(self.description)

        self.openedWindows = {}
    
    def helpWindow(self, tutorialPic):
        if "helpWindow" not in self.openedWindows:
            newWindow = HelpWindow("tutorialPics/" + tutorialPic)
            self.openedWindows["helpWindow"] = newWindow
        self.openedWindows["helpWindow"].show()

    def getParameters(self):
        return {}

    def getNewLog(self, newName, parameters = {}):
        # returns new log that is created by applying given operator with selected parameters
        # this is used for the "add to logs" and "export" button in the main window
        pass

    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters
        pass