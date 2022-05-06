# -*- coding: utf-8 -*-

from ast import Name
from ctypes import alignment
from os import supports_bytes_environ
from re import S

from numpy import inner
from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrame import OperatorFrame
from matchMinerFrame import MatchMinerFrame
from interleavedMinerFrame import InterleavedMinerFrame
from nonInterleavedMinerFrame import NonInterleavedMinerFrame
from operators import manualMiner, matchMiner
import pickle
from tableWindow import TableWindow
from objRelationWindow import ObjectWindow
from manualMinerFrame import ManualMinerFrame
from filterFrame import FilterFrame

import json
import ocel as ocel_lib
from exportDialogBox import ExportDialog
from toCelonis import cli

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal

# import qdarkstyle

class TransformationCenter(QtWidgets.QWidget):

    def __init__(self, ocel_model, url, api):
        super().__init__()
        self.ocel_model = ocel_model
        self.url = url
        self.api = api

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1300, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # most outer layout
        self.rightFrame = QtWidgets.QFrame(self.centralwidget)
        self.rightFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rightFrame.setObjectName("rightFrame")

        self.rightGridLayout = QtWidgets.QGridLayout(self.rightFrame)
        self.rightGridLayout.setObjectName("rightGridLayout")
        self.gridLayout.addWidget(self.rightFrame, 0, 1, 2, 2)

        # start of code for side scroll area
        self.OCEL_list_scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.OCEL_list_scrollArea.setMinimumWidth(360)
        self.leftGridLayout = QtWidgets.QGridLayout(self.OCEL_list_scrollArea)
        self.leftGridLayout.setObjectName("leftGridLayout")
        self.gridLayout.addWidget(self.OCEL_list_scrollArea, 0, 0, 1, 1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.OCEL_list_scrollArea.sizePolicy().hasHeightForWidth())
        self.OCEL_list_scrollArea.setSizePolicy(sizePolicy)
        self.OCEL_list_scrollArea.setWidgetResizable(True)
        self.OCEL_list_scrollArea.setObjectName("OCEL_list_scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")

        self.OCEL_list_frame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.OCEL_list_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.OCEL_list_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.OCEL_list_frame.setObjectName("OCEL_list_frame")
        self.sidebarTitlelabel = QtWidgets.QLabel(self.OCEL_list_frame)
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
        self.innerVerticalLayout.addWidget(self.sidebarTitlelabel)
        # end of code for side scroll area
        self.innerVerticalLayout.setAlignment(QtCore.Qt.AlignVCenter)
        self.sidebarTitlelabel.setAlignment(QtCore.Qt.AlignCenter)

        # stacked widget for multiple different views
        self.stackedWidget = QtWidgets.QStackedWidget(self.rightFrame)
        self.stackedWidget.setObjectName("stackedWidget")
        self.rightGridLayout.addWidget(self.stackedWidget, 0, 0, 1, 2)

        self.operatorSelectorPage = QtWidgets.QWidget()
        self.operatorSelectorPage.setObjectName("operatorSelectorPage")

        self.operatorOverviewStackedLayout = QtWidgets.QGridLayout(self.operatorSelectorPage)
        self.operatorOverviewStackedLayout.setObjectName("operatorOverviewStackedLayout")

        self.stackedWidget.addWidget(self.operatorSelectorPage)

        self.operatorSelectorTitle = QtWidgets.QLabel(self.operatorSelectorPage)
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.operatorSelectorTitle.setFont(font)
        self.operatorSelectorTitle.setObjectName("operatorSelectorTitle")
        self.operatorSelectorTitle.setText("Select an Operator")
        self.operatorOverviewStackedLayout.addWidget(self.operatorSelectorTitle, 0, 0, 1, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.operatorOverviewStackedLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.operatorOverviewStackedLayout.setSpacing(40)

        # scrollarea for operators on overview page
        self.scrollArea = QtWidgets.QScrollArea(self.operatorSelectorPage)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.scrollGridLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.scrollGridLayout.setSpacing(40)
        self.operatorOverviewStackedLayout.addWidget(self.scrollArea)
        self.operatorFrames = []
        # we need to initialize a page for every supported operator
        description = "Merge events across logs based on matching attribute(s)."
        self.initOperatorPage("Match Miner", description, MatchMinerFrame)
        description = "Merge events across logs based on manual matching of activities of logs."
        self.initOperatorPage("Manual Miner", description, ManualMinerFrame)
        description = "Merge events across logs based on interleaved interactions between events."
        self.initOperatorPage("Interleaved Miner", description, InterleavedMinerFrame)
        description = "Merge events across logs based on non-interleaved interactions between events."
        self.initOperatorPage("Non-Interleaved Miner", description, NonInterleavedMinerFrame)
        description = "Filter event log based on activities, attributes, objects or timestamps."
        self.initOperatorPage("Filter Event Log", description, FilterFrame)


        # button for viewing object relationships
        self.viewObjectRelationsButton = QtWidgets.QPushButton(self.centralwidget)
        self.viewObjectRelationsButton.setObjectName("viewObjectRelationsButton")
        self.gridLayout.addWidget(self.viewObjectRelationsButton, 1, 0, 1, 1)

        # general properties
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
        # keep track of windows to view tables, and object relationships
        self.windows = {}


        self.viewObjectRelationsButton.setText("Calculating Object Relationships...")
        self.viewObjectRelationsButton.setEnabled(False)
        self.formattedObjRows = {}
        # create thread to reformat rows for object relationship view
        self.worker = WorkerThread(self.ocel_model)
        self.worker.reformatObjRelation.connect(self.reformattingComplete)
        self.worker.finished.connect(self.worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()


        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Transformation Center")

        # right hand side operator view

        self.refreshSelection()

        # start for side scroll area
        self.ocelSideBarFrames = {}
        
        self.ocelSideBarExportButtons = {}
        self.ocelSideBarDeleteButtons = {}
        self.ocelSideBarViewButtons = {}

        for i in range(len(self.ocel_model.getOcelNames())):
            currName = list(self.ocel_model.getOcelNames())[i]
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


            self.ocelSideBarViewButtons[currName].setText("View")
            self.ocelSideBarExportButtons[currName].setText("Export")
            self.ocelSideBarDeleteButtons[currName].setText("Delete")
            sidebarOCELTitle.setText(currName)
            sidebarOCELTitle.setMaximumWidth(350)
            sidebarOCELTitle.setWordWrap(True)

            innerLayout = QtWidgets.QGridLayout(self.ocelSideBarFrames[currName])
            innerLayout.setObjectName("innerLayout")
            innerLayout.addWidget(sidebarOCELTitle)
            innerLayout.addWidget(self.ocelSideBarViewButtons[currName])
            innerLayout.addWidget(self.ocelSideBarExportButtons[currName])
            innerLayout.addWidget(self.ocelSideBarDeleteButtons[currName])

        self.innerVerticalLayout.setSpacing(20)

        self.sidebarTitlelabel.setText("Object-centric event logs")
    #    self.sidebarTitlelabel.setAlignment(QtCore.Qt.AlignTop)
        # end for side scroll area

        # button for viewing object relationships
        self.viewObjectRelationsButton.setText("View Object Relationships")
        self.viewObjectRelationsButton.clicked.connect(self.viewObjectRelations)


    def addToLogs(self, pageNum):
        # get name for new log as input from user
        text = ""
        duplicate = False
        while (text == ""):
            if not duplicate:
                text, ok = QtWidgets.QInputDialog.getText(self, 'Applying Operator', 'Enter name for new log:')
            else:
                text, ok = QtWidgets.QInputDialog.getText(self, 'Applying Operator', 'Enter name for new log (name already exists):')
            if not ok:
                return
            # avoid duplicate names
            duplicate = False
            if text in self.ocel_model.getOcelNames():
                text = ""
                duplicate = True

        name_newLog = self.operatorFrames[pageNum].getNewLog()
        if not name_newLog:
            return
        name = text # name_newLog[0]
        newLog = name_newLog[1]
        self.ocel_model.addOCEL(name, ocelFileName=name+".json", ocel=newLog)
        self.refreshSelection(name)

    def removeFromLogs(self, name):
        if len(self.ocel_model.ocels) == 1:
            print("Can't delete last log")
            return
        self.ocel_model.removeOCEL(name)
        self.ocelSideBarFrames[name].setParent(None)
        del self.ocelSideBarFrames[name]
        if name in self.windows:
            del self.windows[name]
        self.refreshSelection(returnToOperatorOverviewPage=False)


    def refreshSelection(self, name="", returnToOperatorOverviewPage=True):

        for i in self.operatorFrames:
            i.refresh()
        
        # go back to operator overview page
        if returnToOperatorOverviewPage:
            self.stackedWidget.setCurrentIndex(0)

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


        self.ocelSideBarViewButtons[name].setText("View")
        self.ocelSideBarExportButtons[name].setText("Export")
        self.ocelSideBarDeleteButtons[name].setText("Delete")
        sidebarOCELTitle.setText(name)
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
     #   self.OCEL_list_frame.setMinimumSize(QtCore.QSize(0, 150 * len(self.ocel_model.ocels)))

        # end for side scroll area

    def show_table_window(self, name):
        if name not in self.windows:
            newWindow = QtWidgets.QMainWindow()
            ui = TableWindow(self.ocel_model.getOCEL(name), name)
            ui.setupUi(newWindow)
            self.windows[name] = newWindow
        self.windows[name].show()


    def viewObjectRelations(self):
        if "objRelationshipWindow" not in self.windows:
            newWindow = QtWidgets.QMainWindow()
            ui = ObjectWindow(self.formattedObjRows)
            ui.setupUi(newWindow)
            self.windows["objRelationshipWindow"] = newWindow
        self.windows["objRelationshipWindow"].show()


    def export(self, name):
        print("exporting " + name)
        fileName = 'ocel_' + name + '.json'
        filePath = "exportedOCELs/" + fileName
        ocel_lib.export_log(self.ocel_model.getOCEL(name), filePath)
        dialog = ExportDialog(filePath, self.url, self.api)
        if dialog.exec():
            parameters = dialog.getInputs()
            self.ocelSideBarDeleteButtons[name].setEnabled(False)
            self.ocelSideBarExportButtons[name].setEnabled(False)
            self.ocelSideBarExportButtons[name].setText("Exporting...")
            self.ocelSideBarExportButtons[name].setStyleSheet("background-color: red")

            # create thread so that GUI stays responsive while exporting
            self.worker = ExportWorkerThread(name, filePath, self.url, self.api, parameters[0], parameters[1], parameters[2], parameters[3])
            self.worker.exportDone.connect(self.exportDone)
            self.worker.finished.connect(self.worker.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.start()


    def exportDone(self, name, success):
        if not success:
            QtWidgets.QMessageBox.question(self, 'Export Failed', 'Export of ' + name + ' failed', QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.question(self, 'Export Complete', 'Export of ' + name + ' completed', QtWidgets.QMessageBox.Ok)
        self.ocelSideBarExportButtons[name].setEnabled(True)
        self.ocelSideBarExportButtons[name].setText("Export")
        self.ocelSideBarExportButtons[name].setStyleSheet("")
        self.ocelSideBarDeleteButtons[name].setEnabled(True)



    def switchPage(self, pageNum, toOverview=False):
        if toOverview:
            self.stackedWidget.setCurrentIndex(0)
            return
        self.operatorFrames[pageNum].refresh()  
        self.stackedWidget.setCurrentIndex(pageNum+1) # +1 since the 0th page is the operator overview page


    def initOperatorPage(self, minerTitle, minerDescription, minerFrameClass):
        operatorPage = QtWidgets.QWidget()
        operatorPage.setObjectName("operatorPage")
        innerStackedLayout = QtWidgets.QGridLayout(operatorPage)
        innerStackedLayout.setObjectName("innerStackedLayout")

        # button to go back t overview page
        goBackButton = QtWidgets.QPushButton(operatorPage)
        goBackButton.setObjectName("goBackButton")
        goBackButton.clicked.connect(lambda: self.switchPage(0, toOverview=True ))
        innerStackedLayout.addWidget(goBackButton)
        goBackButton.setText("Go back to overview of operators")

        operatorFrame = minerFrameClass(operatorPage, self.ocel_model, minerTitle, minerDescription)
        innerStackedLayout.addWidget(operatorFrame)

        # page number of stacked widget
        pageNum = len(self.operatorFrames)

        # create frame on overview page for miner as well
        # frame on over view page
        minerFrame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        minerFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        minerFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        minerFrameLayout = QtWidgets.QGridLayout(minerFrame)
        minerFrameLayout.setSpacing(20)
        # miner title on overview page
        minerTitleLabel = QtWidgets.QLabel(minerFrame)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        minerTitleLabel.setFont(font)
        minerTitleLabel.setText(minerTitle)
        # miner description on overview page
        minerDescriptionLabel = QtWidgets.QLabel(minerFrame)
        font = QtGui.QFont()
        font.setPointSize(15)
        minerDescriptionLabel.setFont(font)
        minerDescriptionLabel.setText(minerDescription)
        # miner button on overview page
        minerButton = QtWidgets.QPushButton(minerFrame)
        minerButton.clicked.connect(lambda checked, x=pageNum: self.switchPage(x))
        minerButton.setText("Apply Operator")
        # layout
        minerFrameLayout.addWidget(minerTitleLabel)
        minerFrameLayout.addWidget(minerDescriptionLabel)
        minerFrameLayout.addWidget(minerButton)

        self.scrollGridLayout.addWidget(minerFrame)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
       # self.operatorOverviewStackedLayout.addWidget(minerFrame)

        # export and add-to-logs buttons on operator page
        operatorAddButton = QtWidgets.QPushButton(operatorPage)
        operatorAddButton.setObjectName("operatorAddButton")
        operatorAddButton.clicked.connect(lambda checked, x=pageNum: self.addToLogs(x))
        innerStackedLayout.addWidget(operatorAddButton)
        operatorAddButton.setText("Add to event logs")

    #    operatorExportButton = QtWidgets.QPushButton(operatorPage)
    #    operatorExportButton.setObjectName("operatorExportButton")
    #    operatorExportButton.clicked.connect(lambda checked, x=pageNum: self.export("Placeholder_" + str(x) ))
    #    innerStackedLayout.addWidget(operatorExportButton)
    #    operatorExportButton.setText("Export")

        self.stackedWidget.addWidget(operatorPage)
        self.operatorFrames.append(operatorFrame)


    def reformattingComplete(self, rows):
        self.formattedObjRows = rows
        self.viewObjectRelationsButton.setText("View Object Relationships")
        self.viewObjectRelationsButton.setEnabled(True)

class WorkerThread(QThread):
    reformatObjRelation = pyqtSignal(dict)
    def __init__(self, ocel_model):
        super().__init__()
        self.ocel_model = ocel_model

    def run(self):
        obj_relations = self.ocel_model.getRelation()
        all_objects = set()
        for ocelName in self.ocel_model.getOcelNames():
            all_objects = all_objects.union(self.ocel_model.getOCEL(ocelName)["ocel:objects"].keys())
        all_objects = list(all_objects)
        rows = {}
        for obj in all_objects:
            rows[obj] = set([b for (a,b) in obj_relations if a == obj])
        self.reformatObjRelation.emit(rows)


class ExportWorkerThread(QThread):
    exportDone = pyqtSignal(str, bool)
    def __init__(self, name, filePath, url, api, dataPool, dataModel, objects, transitions):
        super().__init__()
        self.name = name
        self.filePath = filePath
        self.url = url
        self.api = api
        self.dataPool = dataPool
        self.dataModel = dataModel
        self.objects = objects
        self.transitions = transitions

    def run(self):
        try:
            print(self.filePath)
            print(self.url)
            print(self.api)
            print(self.dataPool)
            print(self.dataModel)
            print(self.objects)
            print(self.transitions)
            cli(self.filePath, self.url, self.api, self.dataPool, self.dataModel, self.objects, self.transitions)
            self.exportDone.emit(self.name, True)
        except:
            self.exportDone.emit(self.name, False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)


    # set style using stylesheet, templates from: https://qss-stock.devsecstudio.com/templates.php
#    File = open("../StyleSheets/Darkeum/Darkeum.qss",'r')
#    with File:
#        qss = File.read()
#        app.setStyleSheet(qss)

    # set style using setStyle, limited on linux
#    app.setStyle('Fusion')

    # need to import qdarkstyle first
#    app.setStyleSheet(qdarkstyle.load_stylesheet())

    MainWindow = QtWidgets.QMainWindow()

    with open('fileBig1.pkl', 'rb') as file:
        # Call load method to deserialze
        ocel_model = pickle.load(file)

    url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
    token = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

    ui = TransformationCenter(ocel_model, url, token)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())