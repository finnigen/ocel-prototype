# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'firstDraft.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from ast import Name
from ctypes import alignment
from re import S
from ocel_converter import convertToOcelModel, OCEL_Model
from operators import manualMiner, matchMiner
import pickle
from tableWindow import TableWindow
from objRelationWindow import ObjectWindow

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):


        # url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
        # api = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

        # data_pool = "OCEL_Pool1"
        # data_model = "OCEL_Model1"

        # self.ocel_model = convertToOcelModel(url, api, data_pool, data_model)

        # for development purposes
        with open('file.pkl', 'rb') as file:
            # Call load method to deserialze
            self.ocel_model = pickle.load(file)


        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1300, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # most outer layout (grid layouts for left side)
        self.rightFrame = QtWidgets.QFrame(self.centralwidget)
        self.rightFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rightFrame.setObjectName("rightFrame")

        self.rightGridLayout = QtWidgets.QGridLayout(self.rightFrame)
        self.rightGridLayout.setObjectName("rightGridLayout")
        self.gridLayout.addWidget(self.rightFrame, 0, 1, 2, 2)

        # start of code for side scroll area
        self.OCEL_list_scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.leftGridLayout = QtWidgets.QGridLayout(self.OCEL_list_scrollArea)
        self.leftGridLayout.setObjectName("leftGridLayout")
        self.gridLayout.addWidget(self.OCEL_list_scrollArea, 0, 0, 1, 1)
    #    self.OCEL_list_scrollArea.setGeometry(QtCore.QRect(30, 20, 391, 581))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.OCEL_list_scrollArea.sizePolicy().hasHeightForWidth())
        self.OCEL_list_scrollArea.setSizePolicy(sizePolicy)
        self.OCEL_list_scrollArea.setWidgetResizable(True)
        self.OCEL_list_scrollArea.setObjectName("OCEL_list_scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
    #    self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 375, 1018))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")

        self.OCEL_list_frame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        # set height of scroll frame to multiple of length of OCELs collection
    #    self.OCEL_list_frame.setMinimumSize(QtCore.QSize(0, 150 * len(self.ocel_model.ocels)))
        self.OCEL_list_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.OCEL_list_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.OCEL_list_frame.setObjectName("OCEL_list_frame")
        self.sidebarTitlelabel = QtWidgets.QLabel(self.OCEL_list_frame)
    #    self.sidebarTitlelabel.setGeometry(QtCore.QRect(30, 10, 321, 31))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.sidebarTitlelabel.setFont(font)
        self.sidebarTitlelabel.setObjectName("sidebarTitlelabel")

        self.verticalLayout.addWidget(self.OCEL_list_frame)

        self.OCEL_list_scrollArea.setWidget(self.scrollAreaWidgetContents)

        # set inner layout of left sidebar
        self.innerVerticalLayout = QtWidgets.QVBoxLayout(self.OCEL_list_frame)
        self.innerVerticalLayout.setObjectName("innerVerticalLayout")
        self.innerVerticalLayout.addWidget(self.sidebarTitlelabel, 0, QtCore.Qt.AlignHCenter)
        # end of code for side scroll area



        # stacked widget for multiple different views
        self.stackedWidget = QtWidgets.QStackedWidget(self.rightFrame)
        self.stackedWidget.setObjectName("stackedWidget")
        self.rightGridLayout.addWidget(self.stackedWidget, 0, 0, 1, 2)

        self.operatorSelectorPage = QtWidgets.QWidget()
        self.operatorSelectorPage.setObjectName("operatorSelectorPage")

        innerStackedLayout = QtWidgets.QGridLayout(self.operatorSelectorPage)
        innerStackedLayout.setObjectName("innerStackedLayout")

        self.stackedWidget.addWidget(self.operatorSelectorPage)

        self.matchMinerButton = QtWidgets.QPushButton(self.operatorSelectorPage)
        self.matchMinerButton.setObjectName("matchMinerButton")
        self.matchMinerButton.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(1))
        self.matchMinerButton.setText("Match Miner")

        innerStackedLayout.addWidget(self.matchMinerButton)



        self.matchMinerPage = QtWidgets.QWidget()
        self.matchMinerPage.setObjectName("matchMinerPage")
        innerStackedLayout = QtWidgets.QGridLayout(self.matchMinerPage)
        innerStackedLayout.setObjectName("innerStackedLayout")
        self.stackedWidget.addWidget(self.matchMinerPage)


        # code for right area
        self.operatorFrame = QtWidgets.QFrame(self.matchMinerPage)
    #    self.rightGridLayout.addWidget(self.operatorFrame, 0, 0, 1, 2)

    #    self.operatorFrame.setGeometry(QtCore.QRect(20, 20, 751, 511))
        self.operatorFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.operatorFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.operatorFrame.setObjectName("operatorFrame")

        # set inner layout of right area
        self.innerRightLayout = QtWidgets.QGridLayout(self.operatorFrame)
        self.innerRightLayout.setObjectName("innerRightLayout")

        self.operatorTitleLabel = QtWidgets.QLabel(self.operatorFrame)
    #    self.operatorTitleLabel.setGeometry(QtCore.QRect(280, 20, 231, 41))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.operatorTitleLabel.setFont(font)
        self.operatorTitleLabel.setObjectName("operatorTitleLabel")

        self.operatorDescriptionLabel = QtWidgets.QLabel(self.operatorFrame)
        self.operatorDescriptionLabel.setEnabled(True)
    #    self.operatorDescriptionLabel.setGeometry(QtCore.QRect(60, 70, 611, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorDescriptionLabel.setFont(font)
        self.operatorDescriptionLabel.setObjectName("operatorDescriptionLabel")
        self.operatorSelectorLabel_1 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_1.setEnabled(True)
    #    self.operatorSelectorLabel_1.setGeometry(QtCore.QRect(60, 160, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_1.setFont(font)
        self.operatorSelectorLabel_1.setObjectName("operatorSelectorLabel_1")
        self.operatorSelectorLabel_3 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_3.setEnabled(True)
    #    self.operatorSelectorLabel_3.setGeometry(QtCore.QRect(60, 280, 311, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.operatorSelectorLabel_3.setFont(font)
        self.operatorSelectorLabel_3.setObjectName("operatorSelectorLabel_3")
        
        self.logSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
    #    self.logSelectcomboBox1.setGeometry(QtCore.QRect(420, 160, 221, 31))
        self.logSelectcomboBox1.setObjectName("logSelectcomboBox1")

        self.logSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
    #    self.logSelectcomboBox2.setGeometry(QtCore.QRect(420, 210, 221, 31))
        self.logSelectcomboBox2.setObjectName("logSelectcomboBox2")

        self.logSelectcomboBox1.activated.connect(self.initAttributes1)
        self.logSelectcomboBox2.activated.connect(self.initAttributes2)

        self.attrSelectcomboBox1 = QtWidgets.QComboBox(self.operatorFrame)
    #    self.attrSelectcomboBox1.setGeometry(QtCore.QRect(420, 280, 221, 31))
        self.attrSelectcomboBox1.setObjectName("attrSelectcomboBox1")

        self.attrSelectcomboBox2 = QtWidgets.QComboBox(self.operatorFrame)
    #    self.attrSelectcomboBox2.setGeometry(QtCore.QRect(420, 320, 221, 31))
        self.attrSelectcomboBox2.setObjectName("attrSelectcomboBox2")

        self.operatorAddButton = QtWidgets.QPushButton(self.operatorFrame)
    #    self.operatorAddButton.setGeometry(QtCore.QRect(80, 430, 231, 41))
        self.operatorAddButton.setObjectName("operatorAddButton")
        self.operatorAddButton.clicked.connect(self.addToLogs)

        self.operatorExportButton = QtWidgets.QPushButton(self.operatorFrame)
    #    self.operatorExportButton.setGeometry(QtCore.QRect(410, 430, 231, 41))
        self.operatorExportButton.setObjectName("operatorExportButton")
        self.operatorExportButton.clicked.connect(lambda checked, x="PlaceHolder": self.export(x))

        
        self.operatorSelectorLabel_2 = QtWidgets.QLabel(self.operatorFrame)
        self.operatorSelectorLabel_2.setEnabled(True)
    #    self.operatorSelectorLabel_2.setGeometry(QtCore.QRect(60, 210, 271, 31))
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


        innerStackedLayout.addWidget(self.operatorFrame)


        # button for viewing object relationships
        self.viewObjectRelationsButton = QtWidgets.QPushButton(self.centralwidget)
        self.viewObjectRelationsButton.setObjectName("viewObjectRelationsButton")
        self.gridLayout.addWidget(self.viewObjectRelationsButton, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1052, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        # set current page for stacked widget
        self.stackedWidget.setCurrentIndex(0)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Transformation Center"))

        # right hand side operator view
        self.operatorTitleLabel.setText(_translate("MainWindow", "Match Miner"))

        self.refreshSelection()

        self.operatorDescriptionLabel.setText(_translate("MainWindow", "Merge events across logs based on matching attribute(s)."))
        self.operatorSelectorLabel_1.setText(_translate("MainWindow", "Select first event log:"))
        self.operatorSelectorLabel_3.setText(_translate("MainWindow", "Select attribute(s) to match on:"))

        self.operatorAddButton.setText(_translate("MainWindow", "Add to event logs"))
        self.operatorExportButton.setText(_translate("MainWindow", "Export"))
        self.operatorSelectorLabel_2.setText(_translate("MainWindow", "Select second event log:"))


        # start for side scroll area
        self.ocelSideBarFrames = {}
        
        self.ocelSideBarExportButtons = {}
        self.ocelSideBarDeleteButtons = {}
        self.ocelSideBarViewButtons = {}

        for i in range(len(self.ocel_model.ocels.keys())):
            currName = list(self.ocel_model.ocels.keys())[i]
            self.ocelSideBarFrames[currName] = QtWidgets.QFrame(self.OCEL_list_frame)
            self.innerVerticalLayout.addWidget(self.ocelSideBarFrames[currName])
        
        #    height = i*120+60
        #    self.ocelSideBarFrames[currName].setGeometry(QtCore.QRect(40, height, 280, 100))
            self.ocelSideBarFrames[currName].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.ocelSideBarFrames[currName].setFrameShadow(QtWidgets.QFrame.Raised)
            self.ocelSideBarFrames[currName].setObjectName("OcelNameFrame_" + str(currName))

            sidebarOCELTitle = QtWidgets.QLabel(self.ocelSideBarFrames[currName])
        #    sidebarOCELTitle.setGeometry(QtCore.QRect(60, 10, 181, 21))
            font = QtGui.QFont()
            font.setPointSize(13)
            font.setBold(True)
            font.setWeight(75)
            sidebarOCELTitle.setFont(font)
            sidebarOCELTitle.setObjectName("sidebarTitlelabel")
            sidebarOCELTitle.setAlignment(QtCore.Qt.AlignCenter)
            self.ocelSideBarViewButtons[currName] = QtWidgets.QPushButton(self.ocelSideBarFrames[currName])
        #    self.ocelSideBarViewButtons[currName].setGeometry(QtCore.QRect(10, 50, 81, 25))
            self.ocelSideBarViewButtons[currName].setObjectName("sidebarPushButtonView")
            self.ocelSideBarExportButtons[currName] = QtWidgets.QPushButton(self.ocelSideBarFrames[currName])
        #    self.ocelSideBarExportButtons[currName].setGeometry(QtCore.QRect(100, 50, 81, 25))
            self.ocelSideBarExportButtons[currName].setObjectName("sidebarPushButtonExport")
            self.ocelSideBarDeleteButtons[currName] = QtWidgets.QPushButton(self.ocelSideBarFrames[currName])
        #    self.ocelSideBarDeleteButtons[currName].setGeometry(QtCore.QRect(190, 50, 81, 25))
            self.ocelSideBarDeleteButtons[currName].setObjectName("sidebarPushButtonDelete")

            self.ocelSideBarDeleteButtons[currName].clicked.connect(lambda checked, x=currName: self.removeFromLogs(x))
            self.ocelSideBarExportButtons[currName].clicked.connect(lambda checked, x=currName: self.export(x))
            self.ocelSideBarViewButtons[currName].clicked.connect(lambda checked, x=currName: self.show_table_window(x))


            self.ocelSideBarViewButtons[currName].setText(_translate("MainWindow", "View"))
            self.ocelSideBarExportButtons[currName].setText(_translate("MainWindow", "Export"))
            self.ocelSideBarDeleteButtons[currName].setText(_translate("MainWindow", "Delete"))
            sidebarOCELTitle.setText(_translate("MainWindow", currName))
            sidebarOCELTitle.setMaximumWidth(350)
            sidebarOCELTitle.setWordWrap(True)

            innerLayout = QtWidgets.QGridLayout(self.ocelSideBarFrames[currName])
            innerLayout.setObjectName("innerLayout")
            innerLayout.addWidget(sidebarOCELTitle)
            innerLayout.addWidget(self.ocelSideBarViewButtons[currName])
            innerLayout.addWidget(self.ocelSideBarExportButtons[currName])
            innerLayout.addWidget(self.ocelSideBarDeleteButtons[currName])

        self.innerVerticalLayout.setSpacing(20)

        self.sidebarTitlelabel.setText(_translate("MainWindow", "Object-centric event logs"))
        self.sidebarTitlelabel.setAlignment(QtCore.Qt.AlignTop)
        # end for side scroll area

        # button for viewing object relationships
        self.viewObjectRelationsButton.setText(_translate("MainWindow", "View Object Relationships"))
        self.viewObjectRelationsButton.clicked.connect(self.viewObjectRelations)


    def addToLogs(self):
        name1 = self.logSelectcomboBox1.currentText()
        name2 = self.logSelectcomboBox2.currentText()
        log1 = self.ocel_model.ocels[name1]
        log2 = self.ocel_model.ocels[name2]
        attr1 = self.attrSelectcomboBox1.currentText()
        attr2 = self.attrSelectcomboBox2.currentText()
        name = "MATCH_MINER (" + name1 + ", " + name2 + ")" + " on " + "(" + attr1 + ", " + attr2 + ")"
        if name in self.ocel_model.ocels:
            return
        newLog = matchMiner(log1, log2, self.ocel_model.obj_relation, attr1, attr2)
        self.ocel_model.addOCEL(name, newLog)

        self.refreshSelection(name)

    def removeFromLogs(self, name):
        self.ocel_model.removeOCEL(name)
        self.ocelSideBarFrames[name].setParent(None)
        del self.ocelSideBarFrames[name]
        self.refreshSelection()


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

    def refreshSelection(self, name=""):
        _translate = QtCore.QCoreApplication.translate

        self.logSelectcomboBox1.clear()
        self.logSelectcomboBox2.clear()

        for i in range(len(self.ocel_model.ocels.keys())):
            self.logSelectcomboBox1.addItem("")
            self.logSelectcomboBox2.addItem("")
            self.logSelectcomboBox1.setItemText(i, _translate("MainWindow", list(self.ocel_model.ocels.keys())[i]))
            self.logSelectcomboBox2.setItemText(i, _translate("MainWindow", list(self.ocel_model.ocels.keys())[i]))

        self.initAttributes1()
        self.initAttributes2()
        
        # only add new log to sidebar if we just applied some operator
        if name == "":
            return

        # start for side scroll area
        i = len(self.ocel_model.ocels) - 1
        self.ocelSideBarFrames[name] = QtWidgets.QFrame(self.OCEL_list_frame)
        self.innerVerticalLayout.addWidget(self.ocelSideBarFrames[name])

    #    height = i*120+60
    #    self.ocelSideBarFrames[name].setGeometry(QtCore.QRect(40, height, 280, 100))
        self.ocelSideBarFrames[name].setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ocelSideBarFrames[name].setFrameShadow(QtWidgets.QFrame.Raised)
        self.ocelSideBarFrames[name].setObjectName("OcelNameFrame_" + str(name))

        sidebarOCELTitle = QtWidgets.QLabel(self.ocelSideBarFrames[name])
    #    sidebarOCELTitle.setGeometry(QtCore.QRect(60, 10, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        sidebarOCELTitle.setFont(font)
        sidebarOCELTitle.setObjectName("sidebarTitlelabel")
        sidebarOCELTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.ocelSideBarViewButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])
    #    self.ocelSideBarViewButtons[name].setGeometry(QtCore.QRect(10, 50, 81, 25))
        self.ocelSideBarViewButtons[name].setObjectName("sidebarPushButtonView")
        self.ocelSideBarExportButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])
    #    self.ocelSideBarExportButtons[name].setGeometry(QtCore.QRect(100, 50, 81, 25))
        self.ocelSideBarExportButtons[name].setObjectName("sidebarPushButtonExport")
        self.ocelSideBarDeleteButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])
    #    self.ocelSideBarDeleteButtons[name].setGeometry(QtCore.QRect(190, 50, 81, 25))
        self.ocelSideBarDeleteButtons[name].setObjectName("sidebarPushButtonDelete")

        self.ocelSideBarDeleteButtons[name].clicked.connect(lambda: self.removeFromLogs(name))
        self.ocelSideBarExportButtons[name].clicked.connect(lambda checked, x=name: self.export(x))
        self.ocelSideBarViewButtons[name].clicked.connect(lambda checked, x=name: self.show_table_window(x))


        self.ocelSideBarViewButtons[name].setText(_translate("MainWindow", "View"))
        self.ocelSideBarExportButtons[name].setText(_translate("MainWindow", "Export"))
        self.ocelSideBarDeleteButtons[name].setText(_translate("MainWindow", "Delete"))
        sidebarOCELTitle.setText(_translate("MainWindow", name))
        sidebarOCELTitle.setMaximumWidth(350)
        sidebarOCELTitle.setWordWrap(True)

        innerLayout = QtWidgets.QGridLayout(self.ocelSideBarFrames[name])
        innerLayout.setObjectName("innerLayout")
        innerLayout.addWidget(sidebarOCELTitle)
        innerLayout.addWidget(self.ocelSideBarViewButtons[name])
        innerLayout.addWidget(self.ocelSideBarExportButtons[name])
        innerLayout.addWidget(self.ocelSideBarDeleteButtons[name])

        self.ocelSideBarFrames[name].show()

        # update height of scroll area
        self.OCEL_list_frame.setMinimumSize(QtCore.QSize(0, 150 * len(self.ocel_model.ocels)))

        # end for side scroll area

    def show_table_window(self, name):
        self.newWindow = QtWidgets.QMainWindow()
        ui = TableWindow(self.ocel_model.ocels[name], name)
        ui.setupUi(self.newWindow)
        self.newWindow.show()


    def viewObjectRelations(self):
        self.newWindow = QtWidgets.QMainWindow()
        ui = ObjectWindow(self.ocel_model.obj_relation)
        ui.setupUi(self.newWindow)
        self.newWindow.show()


    def export(self, name):
        print("export " + name)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


