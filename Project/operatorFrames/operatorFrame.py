from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model


class OperatorFrame(QtWidgets.QFrame):
 
    def __init__(self, parent, ocel_model, title, description):
        super().__init__()
        self.parent = parent
        self.ocel_model = ocel_model
        self.title = title
        self.description = description

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
        
        self.operatorDescriptionLabel = QtWidgets.QLabel(self.operatorFrame)
        self.operatorDescriptionLabel.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorDescriptionLabel.setFont(font)

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorTitleLabel, 0, 0, 1, 0, QtCore.Qt.AlignCenter)
        self.innerRightLayout.addWidget(self.operatorDescriptionLabel, 1, 0, 1, 0, QtCore.Qt.AlignCenter)
        self.innerRightLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.innerRightLayout.setSpacing(30)

        self.layout.addWidget(self.operatorFrame)

        self.operatorTitleLabel.setText(self.title)

        self.operatorDescriptionLabel.setText(self.description)
 

    def getNewLog(self, newName):
        # returns new log that is created by applying given operator with selected parameters
        # this is used for the "add to logs" and "export" button in the main window
        pass

    def refresh(self):
        # used to refresh comboboxes for selection of operator parameters
        pass