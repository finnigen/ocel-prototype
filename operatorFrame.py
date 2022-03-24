from PyQt5 import QtCore, QtGui, QtWidgets

from ocel_converter import convertToOcelModel, OCEL_Model


class OperatorFrame(QtWidgets.QWidget):
    def __init__(self, parent, ocel, mainWindow):
        super().__init__()
        self.matchMinerPage = parent
        self.ocel_model = ocel
        self.mainWindow = mainWindow

        # code for right area
        self.operatorFrame = QtWidgets.QFrame(self.matchMinerPage)

        self.operatorFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.operatorFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.operatorFrame.setObjectName("operatorFrame")

        # set inner layout of right area
        self.innerRightLayout = QtWidgets.QGridLayout(self.operatorFrame)
        self.innerRightLayout.setObjectName("innerRightLayout")

        self.operatorTitleLabel = QtWidgets.QLabel(self.operatorFrame)
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.operatorTitleLabel.setFont(font)
        self.operatorTitleLabel.setObjectName("operatorTitleLabel")

        self.operatorDescriptionLabel = QtWidgets.QLabel(self.operatorFrame)
        self.operatorDescriptionLabel.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorDescriptionLabel.setFont(font)
        self.operatorDescriptionLabel.setObjectName("operatorDescriptionLabel")
        self.operatorSelectorLabel_1 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_1.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_1.setFont(font)
        self.operatorSelectorLabel_1.setObjectName("operatorSelectorLabel_1")
        self.operatorSelectorLabel_3 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_3.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_3.setFont(font)
        self.operatorSelectorLabel_3.setObjectName("operatorSelectorLabel_3")
        
        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox1.setObjectName("logSelectcomboBox1")

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
        self.logSelectcomboBox2.setObjectName("logSelectcomboBox2")

        self.logSelectcomboBox1.activated.connect(self.initAttributes1)
        self.logSelectcomboBox2.activated.connect(self.initAttributes2)

        self.attrSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
        self.attrSelectcomboBox1.setObjectName("attrSelectcomboBox1")

        self.attrSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
        self.attrSelectcomboBox2.setObjectName("attrSelectcomboBox2")

        self.operatorAddButton = QtWidgets.QPushButton(self.operatorFrame)
        self.operatorAddButton.setObjectName("operatorAddButton")
        self.operatorAddButton.clicked.connect(self.mainWindow.addToLogs)

        self.operatorExportButton = QtWidgets.QPushButton(self.operatorFrame)
        self.operatorExportButton.setObjectName("operatorExportButton")
        self.operatorExportButton.clicked.connect(lambda checked, x="PlaceHolder": self.mainWindow.export(x))

        
        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_2.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_2.setFont(font)
        self.operatorSelectorLabel_2.setObjectName("operatorSelectorLabel_2")

        # add all labels, buttons etc to right layout
        self.innerRightLayout.addWidget(self.operatorTitleLabel, 0, 0, QtCore.Qt.AlignHCenter)
        self.innerRightLayout.addWidget(self.operatorDescriptionLabel, 1, 0)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_1, 2, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox1, 2, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_2, 3, 0)
        self.innerRightLayout.addWidget(self.logSelectcomboBox2, 3, 1)
        self.innerRightLayout.addWidget(self.operatorSelectorLabel_3, 4, 0)
        self.innerRightLayout.addWidget(self.attrSelectcomboBox1, 4, 1)
        self.innerRightLayout.addWidget(self.attrSelectcomboBox2, 5, 1)
        self.innerRightLayout.addWidget(self.operatorAddButton, 6, 0)
        self.innerRightLayout.addWidget(self.operatorExportButton, 6, 1)


    def initAttributes1(self):
        _translate = QtCore.QCoreApplication.translate
        attributes = self.ocel_model.ocels[self.logSelectcomboBox1.currentText()]["ocel:global-log"]["ocel:attribute-names"]
        self.attrSelectcomboBox1.clear()
        for i in range(len(attributes)):
            self.attrSelectcomboBox1.addItem("")
            self.attrSelectcomboBox1.setItemText(i, _translate("MainWindow", attributes[i]))

    def initAttributes2(self):
        _translate = QtCore.QCoreApplication.translate
        attributes = self.ocel_model.ocels[self.logSelectcomboBox2.currentText()]["ocel:global-log"]["ocel:attribute-names"]
        self.attrSelectcomboBox2.clear()
        for i in range(len(attributes)):
            self.attrSelectcomboBox2.addItem("")
            self.attrSelectcomboBox2.setItemText(i, _translate("MainWindow", attributes[i]))

