
import pickle
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from pycelonis import get_celonis
from transformationCenter import TransformationCenter
from ocel_converter import convertToOcelModel
from ocel_model import OCEL_Model

from PyQt5.QtCore import QObject, QThread, pyqtSignal

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):

        ################## define global fonts
        # big font
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.bigFont = font
        # middle font
        font = QtGui.QFont()
        font.setPointSize(16)
        self.middleFont = font
        
        # size and central widget
        LoginWindow.resize(900, 400)
        self.centralwidget = QtWidgets.QWidget(LoginWindow)
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)

        # celonis url text and label
        self.celonisURLText = QtWidgets.QLineEdit(self.centralwidget)
        self.celonisURLText.setFont(self.middleFont)
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.celonisURLText)

        self.celonisURLLabel = QtWidgets.QLabel(self.centralwidget)
        self.celonisURLLabel.setFont(self.middleFont)
        self.celonisURLLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.celonisURLLabel)
        
        # celonis token text and label
        self.celonisTokenText = QtWidgets.QLineEdit(self.centralwidget)
        self.celonisTokenText.setFont(self.middleFont)
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.celonisTokenText)
        
        self.celonisTokenLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.celonisTokenLabel.sizePolicy().hasHeightForWidth())
        self.celonisTokenLabel.setSizePolicy(sizePolicy)
        self.celonisTokenLabel.setFont(self.middleFont)
        self.celonisTokenLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.celonisTokenLabel)
        # login button and label
        self.loginButton = QtWidgets.QPushButton(self.centralwidget)
        self.loginButton.setFont(self.middleFont)
        self.formLayout.setWidget(16, QtWidgets.QFormLayout.FieldRole, self.loginButton)
        
        self.loginLabel = QtWidgets.QLabel(self.centralwidget)
        self.loginLabel.setFont(self.bigFont)
        self.loginLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loginLabel.setScaledContents(False)
        self.loginLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.loginLabel)

        # error label
        self.errorLabel = QtWidgets.QLabel(self.centralwidget)
        self.errorLabel.setFont(self.middleFont)
        self.errorLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.errorLabel.setScaledContents(False)
        self.errorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(18, QtWidgets.QFormLayout.FieldRole, self.errorLabel)

        # separator line
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.formLayout.setWidget(19, QtWidgets.QFormLayout.FieldRole, self.line)
        # data pool label and combobox
        self.dataPoolLabel = QtWidgets.QLabel(self.centralwidget)
        self.dataPoolLabel.setEnabled(False)
        self.dataPoolLabel.setFont(self.middleFont)
        self.dataPoolLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(20, QtWidgets.QFormLayout.FieldRole, self.dataPoolLabel)
        
        self.dataPoolComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.dataPoolComboBox.setEnabled(False)
        self.dataPoolComboBox.setFont(self.middleFont)
        self.formLayout.setWidget(21, QtWidgets.QFormLayout.FieldRole, self.dataPoolComboBox)
        # data model label and combobox
        self.dataModelLabel = QtWidgets.QLabel(self.centralwidget)
        self.dataModelLabel.setEnabled(False)
        self.dataModelLabel.setFont(self.middleFont)
        self.dataModelLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(22, QtWidgets.QFormLayout.FieldRole, self.dataModelLabel)
        
        self.dataModelComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.dataModelComboBox.setEnabled(False)
        self.dataModelComboBox.setFont(self.middleFont)
        self.formLayout.setWidget(23, QtWidgets.QFormLayout.FieldRole, self.dataModelComboBox)
        # set conversion button
        self.conversionButton = QtWidgets.QPushButton(self.centralwidget)
        self.conversionButton.setEnabled(False)
        self.conversionButton.setSizePolicy(sizePolicy)
        self.conversionButton.setFont(self.middleFont)
        self.formLayout.setWidget(25, QtWidgets.QFormLayout.FieldRole, self.conversionButton)
        # set spacer
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(24, QtWidgets.QFormLayout.FieldRole, spacerItem)
        
        # set central widget of window
        LoginWindow.setCentralWidget(self.centralwidget)

        # connect buttons to functions
        self.loginButton.clicked.connect(self.login)
        self.dataPoolComboBox.activated.connect(self.initModelBox)
        self.conversionButton.clicked.connect(self.startConversion)

        # wait label
        self.waitLabel = QtWidgets.QLabel(self.centralwidget)
        self.waitLabel.setFont(self.middleFont)
        self.waitLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(27, QtWidgets.QFormLayout.FieldRole, self.waitLabel)  

        # conversion error label
        self.conversionErrorLabel = QtWidgets.QLabel(self.centralwidget)
        self.conversionErrorLabel.setFont(self.middleFont)
        self.conversionErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(28, QtWidgets.QFormLayout.FieldRole, self.conversionErrorLabel)  

        # loading symbol for conversion
        self.spinnerLabel = QtWidgets.QLabel(self.centralwidget)
        self.spinnerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setWidget(29, QtWidgets.QFormLayout.FieldRole, self.spinnerLabel)  
        self.spinner = QtGui.QMovie("loading2.gif")
        self.spinnerLabel.setMovie(self.spinner)

        self.newWindow = None

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle("LoginWindow")
        self.celonisURLLabel.setText("Enter your Celonis URL:")
        self.celonisTokenLabel.setText("Enter your Celonis API token:")
        self.loginButton.setText("Login")
        self.loginLabel.setText("Login to Celonis")
        self.errorLabel.setText("Connection failed: no data pools found. Please double check internet connection / login info")
        self.dataPoolLabel.setText("Select a data pool:")
        self.dataModelLabel.setText("Select a data model:")
        self.conversionButton.setText("Start Conversion")
        self.waitLabel.setText("Please be patient. This can take some time...")
        self.conversionErrorLabel.setText("Conversion failed: Is the data pool loaded and non-empty?")
        self.waitLabel.hide()
        self.errorLabel.hide()
        self.conversionErrorLabel.hide()

    def login(self):
        self.url = self.celonisURLText.text()
        self.token = self.celonisTokenText.text()

        try:
            self.celonis = get_celonis(self.url, self.token, key_type="USER_KEY")
        except:
            print("Failed to connect")
            self.errorLabel.show()
            return

        if len(self.celonis.pools) == 0:
            print("Connection failed: no data pools found. Please double check internet connection / login info")
            self.errorLabel.show()
            return

        self.errorLabel.hide()
        self.initRest()
    

    def initRest(self):
        self.dataPoolComboBox.clear()
        self.dataPoolLabel.setEnabled(True)
        self.dataPoolComboBox.setEnabled(True)
        self.dataModelLabel.setEnabled(True)
        self.dataModelComboBox.setEnabled(True)
        self.conversionButton.setEnabled(True)

        # list all data pools in combobox
        for i in range(len(self.celonis.pools)):
            self.dataPoolComboBox.addItem("")
            self.dataPoolComboBox.setItemText(i, self.celonis.pools[i].name)
        self.initModelBox()

    def initModelBox(self):
        self.conversionButton.setEnabled(False)
        self.dataModelComboBox.clear()
        pool_name = self.dataPoolComboBox.currentText()
        pool = self.celonis.pools.find(pool_name)

        # list all data models in combobox
        for i in range(len(pool.datamodels)):
            self.dataModelComboBox.addItem("")
            self.dataModelComboBox.setItemText(i, pool.datamodels[i].name) 

        self.conversionButton.setEnabled(True)

    def startConversion(self):
        print("Opening Transformation Center...")
        self.conversionErrorLabel.hide()
  
        if self.newWindow is not None:
            try:
                self.newWindow.deleteLater()
            except:
                pass
        self.newWindow = None

        self.waitLabel.show()
        self.conversionButton.setEnabled(False)
        self.dataPoolComboBox.setEnabled(False)
        self.dataModelComboBox.setEnabled(False)
        self.celonisTokenText.setEnabled(False)
        self.celonisURLText.setEnabled(False)
        self.loginButton.setEnabled(False)

        # find data model
        pool_name = self.dataPoolComboBox.currentText()
        pool = self.celonis.pools.find(pool_name)
        model_name = self.dataModelComboBox.currentText()
        data_model = pool.datamodels.find(model_name)

        # start loading gif
        self.spinner.start()
        self.spinnerLabel.show()

        # create thread so that GUI stays responsive
        self.worker = WorkerThread(pool, data_model)
        self.worker.updateOCEL.connect(self.conversionComplete)
        self.worker.finished.connect(self.worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def conversionComplete(self, ocel_model):
        if ocel_model is not None:
            # open new window of transformation center
            self.newWindow = QtWidgets.QMainWindow()
            ui = TransformationCenter(ocel_model, self.url, self.token)
            ui.setupUi(self.newWindow)
            self.newWindow.show()
        else:
            self.conversionErrorLabel.show()

        # reset visuals
        self.conversionButton.setEnabled(True)
        self.dataPoolComboBox.setEnabled(True)
        self.dataModelComboBox.setEnabled(True)
        self.celonisTokenText.setEnabled(True)
        self.celonisURLText.setEnabled(True)
        self.loginButton.setEnabled(True)
        self.spinnerLabel.hide()
        self.spinner.stop()
        self.waitLabel.hide()


class WorkerThread(QThread):
    updateOCEL = pyqtSignal(object)
    def __init__(self, pool, data_model):
        super().__init__()
        self.data_model = data_model
        self.data_pool = pool

    def run(self):
        try:
            ocel_model = convertToOcelModel("", "", self.data_pool, self.data_model, skipConnection=True)
        except Exception as e:
            print(e)
            ocel_model = None

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
