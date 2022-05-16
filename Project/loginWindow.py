# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loginWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import pickle
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from pycelonis import get_celonis
from transformationCenter import TransformationCenter
from ocel_converter import OCEL_Model, convertToOcelModel

from PyQt5.QtCore import QObject, QThread, pyqtSignal

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(775, 503)
        self.centralwidget = QtWidgets.QWidget(LoginWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setObjectName("formLayout")
        self.celonisTokenText = QtWidgets.QLineEdit(self.centralwidget)
        self.celonisTokenText.setObjectName("celonisTokenText")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.celonisTokenText)
        self.celonisURLText = QtWidgets.QLineEdit(self.centralwidget)
        self.celonisURLText.setObjectName("celonisURLText")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.celonisURLText)
        self.celonisURLLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.celonisURLLabel.setFont(font)
        self.celonisURLLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.celonisURLLabel.setObjectName("celonisURLLabel")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.celonisURLLabel)
        self.celonisTokenLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.celonisTokenLabel.sizePolicy().hasHeightForWidth())
        self.celonisTokenLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.celonisTokenLabel.setFont(font)
        self.celonisTokenLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.celonisTokenLabel.setObjectName("celonisTokenLabel")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.celonisTokenLabel)
        self.loginButton = QtWidgets.QPushButton(self.centralwidget)
        self.loginButton.setObjectName("loginButton")
        self.formLayout.setWidget(16, QtWidgets.QFormLayout.FieldRole, self.loginButton)
        self.loginLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.loginLabel.setFont(font)
        self.loginLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loginLabel.setScaledContents(False)
        self.loginLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.loginLabel.setObjectName("loginLabel")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.loginLabel)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout.setWidget(19, QtWidgets.QFormLayout.FieldRole, self.line)
        self.dataPoolLabel = QtWidgets.QLabel(self.centralwidget)
        self.dataPoolLabel.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.dataPoolLabel.setFont(font)
        self.dataPoolLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.dataPoolLabel.setObjectName("dataPoolLabel")
        self.formLayout.setWidget(20, QtWidgets.QFormLayout.FieldRole, self.dataPoolLabel)
        self.dataPoolComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.dataPoolComboBox.setObjectName("dataPoolComboBox")
        self.dataPoolComboBox.setEnabled(False)
        self.formLayout.setWidget(21, QtWidgets.QFormLayout.FieldRole, self.dataPoolComboBox)
        self.dataModelLabel = QtWidgets.QLabel(self.centralwidget)
        self.dataModelLabel.setEnabled(False)
        self.dataModelLabel.setFont(font)
        self.dataModelLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.dataModelLabel.setObjectName("dataModelLabel")
        self.formLayout.setWidget(22, QtWidgets.QFormLayout.FieldRole, self.dataModelLabel)
        self.dataModelComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.dataModelComboBox.setEnabled(False)
        self.dataModelComboBox.setObjectName("dataModelComboBox")
        self.formLayout.setWidget(23, QtWidgets.QFormLayout.FieldRole, self.dataModelComboBox)
        self.conversionButton = QtWidgets.QPushButton(self.centralwidget)
        self.conversionButton.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.conversionButton.sizePolicy().hasHeightForWidth())
        self.conversionButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.conversionButton.setFont(font)
        self.conversionButton.setObjectName("conversionButton")
        self.formLayout.setWidget(25, QtWidgets.QFormLayout.FieldRole, self.conversionButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(24, QtWidgets.QFormLayout.FieldRole, spacerItem)
        LoginWindow.setCentralWidget(self.centralwidget)

        self.loginButton.clicked.connect(self.login)
        self.dataPoolComboBox.activated.connect(self.initModelBox)
        self.conversionButton.clicked.connect(self.startConversion)

        self.waitLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.waitLabel.setFont(font)
        self.waitLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.waitLabel.setObjectName("waitLabel")
        self.formLayout.setWidget(27, QtWidgets.QFormLayout.FieldRole, self.waitLabel)  

        # loading symbol for conversion
        self.spinnerLabel = QtWidgets.QLabel(self.centralwidget)
        self.spinnerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(28, QtWidgets.QFormLayout.FieldRole, self.spinnerLabel)  
        self.spinner = QtGui.QMovie("loading2.gif")
        self.spinnerLabel.setMovie(self.spinner)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle("LoginWindow")
        self.celonisURLLabel.setText("Enter your Celonis URL:")
        self.celonisTokenLabel.setText("Enter your Celonis API token:")
        self.loginButton.setText("Login")
        self.loginLabel.setText("Login to Celonis")
        self.dataPoolLabel.setText("Select a data pool:")
        self.dataModelLabel.setText("Select a data model:")
        self.conversionButton.setText("Start Conversion")
        self.waitLabel.setText("Pease be patient. This can take up to a few minutes...")
        self.waitLabel.hide()

    def login(self):
        self.url = self.celonisURLText.text()
        self.token = self.celonisTokenText.text()

        # for development
        self.url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
        self.token = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

        try:
            self.celonis = get_celonis(self.url, self.token, key_type="USER_KEY")
        except:
            print("Invalid login info. Try again")
            return
        self.initRest()
    
    def initRest(self):
        self.dataPoolComboBox.clear()
        self.dataPoolLabel.setEnabled(True)
        self.dataPoolComboBox.setEnabled(True)
        self.dataModelLabel.setEnabled(True)
        self.dataModelComboBox.setEnabled(True)
        self.conversionButton.setEnabled(True)
        for i in range(len(self.celonis.pools)):
            self.dataPoolComboBox.addItem("")
            self.dataPoolComboBox.setItemText(i, self.celonis.pools[i].name)
        self.initModelBox()

    def initModelBox(self):
        self.dataModelComboBox.clear()
        pool_name = self.dataPoolComboBox.currentText()
        pool = self.celonis.pools.find(pool_name)
        for i in range(len(pool.datamodels)):
            self.dataModelComboBox.addItem("")
            self.dataModelComboBox.setItemText(i, pool.datamodels[i].name) 


    def startConversion(self):
        print("Opening Transformation Center...")
  
        self.waitLabel.show()
        self.conversionButton.setEnabled(False)
        self.dataPoolComboBox.setEnabled(False)
        self.dataModelComboBox.setEnabled(False)
        self.loginButton.setEnabled(False)

        # find data model
        pool_name = self.dataPoolComboBox.currentText()
        pool = self.celonis.pools.find(pool_name)
        model_name = self.dataModelComboBox.currentText()
        data_model = pool.datamodels.find(model_name)

        self.spinner.start()
        self.spinnerLabel.show()

        # create thread so that GUI stays responsive
        self.worker = WorkerThread(pool, data_model)
        self.worker.updateOCEL.connect(self.conversionComplete)
        self.worker.finished.connect(self.worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def conversionComplete(self, ocel_model):
        # open new window
        self.newWindow = QtWidgets.QMainWindow()
        ui = TransformationCenter(ocel_model, self.url, self.token)
        ui.setupUi(self.newWindow)
        self.newWindow.show()

        self.conversionButton.setEnabled(True)
        self.dataPoolComboBox.setEnabled(True)
        self.dataModelComboBox.setEnabled(True)
        self.loginButton.setEnabled(True)
        self.waitLabel.hide()
        self.spinnerLabel.hide()
        self.spinner.stop()


class WorkerThread(QThread):
    updateOCEL = pyqtSignal(OCEL_Model)
    def __init__(self, pool, data_model):
        super().__init__()
        self.data_model = data_model
        self.data_pool = pool

    def run(self):
        ocel_model = convertToOcelModel("", "", self.data_pool, self.data_model, skipConnection=True)

        # for presentation...
#        time.sleep(10)
#        with open('filePresentation.pkl', 'rb') as file:
            # Call load method to deserialze
#            ocel_model = pickle.load(file)
        self.updateOCEL.emit(ocel_model)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LoginWindow = QtWidgets.QMainWindow()
    ui = Ui_LoginWindow()
    ui.setupUi(LoginWindow)
    LoginWindow.show()
    sys.exit(app.exec_())
