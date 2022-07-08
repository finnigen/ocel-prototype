# -*- coding: utf-8 -*-

from ast import Name
from ctypes import alignment
from os import supports_bytes_environ
from re import S

from numpy import inner
from ocel_converter import convertToOcelModel, OCEL_Model
from operatorFrames.matchMinerFrame import MatchMinerFrame
from operatorFrames.interleavedMinerFrame import InterleavedMinerFrame
from operatorFrames.nonInterleavedMinerFrame import NonInterleavedMinerFrame
from operators import manualMiner, matchMiner
import pickle
from tableWindow import TableWindow
from objRelationWindow import ObjectWindow
from operatorFrames.manualMinerFrame import ManualMinerFrame
from operatorFrames.filterFrame import FilterFrame
from operatorFrames.flattenFrame import FlattenFrame
from operatorFrames.concatFrame import ConcatFrame
from operatorFrames.aggregateFrame import AggregateFrame
from operatorFrames.eventRecipeFrame import EventRecipeFrame

from ocel_model import *

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
        
        # define main widget, most outer layout and saize
        MainWindow.resize(1300, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        # define rightFrame and layout for operator area
        self.rightFrame = QtWidgets.QFrame(self.centralwidget)
        self.rightFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rightGridLayout = QtWidgets.QGridLayout(self.rightFrame)
        # add rightFrame to most outer layout
        self.gridLayout.addWidget(self.rightFrame, 0, 1, 2, 2)

        ################## start of code for sidebar
        # define scroll area for list of OCELs + associated layout
        OCEL_list_scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        OCEL_list_scrollArea.setMinimumWidth(360)
        self.leftGridLayout = QtWidgets.QGridLayout(OCEL_list_scrollArea)

        # set sizePolicy so that resizing works better
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(OCEL_list_scrollArea.sizePolicy().hasHeightForWidth())
        OCEL_list_scrollArea.setSizePolicy(sizePolicy)
        OCEL_list_scrollArea.setWidgetResizable(True)

        # add scroll area to most outer layout
        self.gridLayout.addWidget(OCEL_list_scrollArea, 0, 0, 1, 1)

        # define content widget for scroll area of sidebar and apply vertical layout
        self.OCEL_list_frame = QtWidgets.QWidget()
        self.sidebarScrollVerticalLayout = QtWidgets.QVBoxLayout(self.OCEL_list_frame)

        # add title to sidebar (adjust font first)
        sidebarTitlelabel = QtWidgets.QLabel(self.OCEL_list_frame)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        sidebarTitlelabel.setFont(font)
        sidebarTitlelabel.setText("Object-centric event logs")

        OCEL_list_scrollArea.setWidget(self.OCEL_list_frame)

        # set inner layout of left sidebar
        self.sidebarScrollVerticalLayout.addWidget(sidebarTitlelabel)

        # adjust alignment for scroll area
        self.sidebarScrollVerticalLayout.setAlignment(QtCore.Qt.AlignVCenter)
        sidebarTitlelabel.setAlignment(QtCore.Qt.AlignCenter)

        # button for viewing object relationships (below and not part of scrollArea)
        viewObjectRelationsButton = QtWidgets.QPushButton(self.centralwidget)
        self.gridLayout.addWidget(viewObjectRelationsButton, 1, 0, 1, 1)
        viewObjectRelationsButton.setText("View Object Relationships")
        viewObjectRelationsButton.clicked.connect(self.viewObjectRelations)

        # keep track of opened windows to view tables or object relationships so that we don't have to re-apply transformation from data to PyQt Table
        self.windows = {}

        ################## end of code for sidebar


        ################## start of code for right-hand operator section

        # stacked widget for multiple different views (e.g. operators overview, specific operator page...)
        self.operatorSectionStackedWidget = QtWidgets.QStackedWidget(self.rightFrame)
        self.rightGridLayout.addWidget(self.operatorSectionStackedWidget, 0, 0, 1, 2)

        # define operator overview/selector page and add layout
        self.operatorSelectorPage = QtWidgets.QWidget()
        self.operatorSelectorLayout = QtWidgets.QGridLayout(self.operatorSelectorPage)
        self.operatorSectionStackedWidget.addWidget(self.operatorSelectorPage)
        # add title with right font to operator overview page
        operatorSelectorTitle = QtWidgets.QLabel(self.operatorSelectorPage)
        operatorSelectorTitle.setFont(font)
        operatorSelectorTitle.setText("Select an Operator")
        self.operatorSelectorLayout.addWidget(operatorSelectorTitle, 0, 0, 1, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.operatorSelectorLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.operatorSelectorLayout.setSpacing(40)

        # scrollarea for operators on overview page
        operatorSelectionScrollArea = QtWidgets.QScrollArea(self.operatorSelectorPage)
        operatorSelectionScrollArea.setWidgetResizable(True)
        self.operatorSelectorScrollAreaWidgetContents = QtWidgets.QWidget()
        self.operatorSelectorScrollGridLayout = QtWidgets.QGridLayout(self.operatorSelectorScrollAreaWidgetContents)
        self.operatorSelectorScrollGridLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.operatorSelectorScrollGridLayout.setSpacing(40)
        self.operatorSelectorLayout.addWidget(operatorSelectionScrollArea)
        self.operatorFrames = []
        operatorSelectionScrollArea.setWidget(self.operatorSelectorScrollAreaWidgetContents)

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
        description = "Map all events to one object type based on relationships."
        self.initOperatorPage("Flatten Event Log", description, FlattenFrame)
        description = "Merge all events of two logs into one without merging any objects."
        self.initOperatorPage("Concatenate Event Log", description, ConcatFrame)
        description = "Merge objects of one log from duplicate events into its first occurence."
        self.initOperatorPage("Aggregate Event Log", description, AggregateFrame)
        description = "Specify sequence of low-level events and turn them into one high-level event."
        self.initOperatorPage("Event Recipe", description, EventRecipeFrame)

        # set current page for stacked widget in the beginning to the operator selector page
        self.operatorSectionStackedWidget.setCurrentIndex(0)

        ################## end of code for right-hand operator section

        # general properties
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1052, 22))
        MainWindow.setMenuBar(self.menubar)
        MainWindow.setWindowTitle("Transformation Center")

        # populate widgets with data from ocel_model (list of ocels...)
        self.initSideBar()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def initSideBar(self):

        self.ocelSideBarFrames = {}
        self.ocelSideBarExportButtons = {}
        self.ocelSideBarDeleteButtons = {}
        self.ocelSideBarViewButtons = {}

        ocel_names = list(self.ocel_model.getOcelNames())
        for i in range(len(ocel_names)):
            currName = ocel_names[i]
            self.ocelSideBarFrames[currName] = QtWidgets.QFrame(self.OCEL_list_frame)
            self.sidebarScrollVerticalLayout.addWidget(self.ocelSideBarFrames[currName])
        
            self.ocelSideBarFrames[currName].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.ocelSideBarFrames[currName].setFrameShadow(QtWidgets.QFrame.Raised)

            sidebarOCELTitle = QtWidgets.QLabel(self.ocelSideBarFrames[currName])
            font = QtGui.QFont()
            font.setPointSize(13)
            font.setBold(True)
            font.setWeight(75)
            sidebarOCELTitle.setFont(font)
            sidebarOCELTitle.setAlignment(QtCore.Qt.AlignCenter)
            self.ocelSideBarViewButtons[currName] = QtWidgets.QPushButton(self.ocelSideBarFrames[currName])
            self.ocelSideBarExportButtons[currName] = QtWidgets.QPushButton(self.ocelSideBarFrames[currName])
            self.ocelSideBarDeleteButtons[currName] = QtWidgets.QPushButton(self.ocelSideBarFrames[currName])

            self.ocelSideBarDeleteButtons[currName].clicked.connect(lambda checked, x=currName: self.removeFromLogs(x))
            self.ocelSideBarExportButtons[currName].clicked.connect(lambda checked, x=currName: self.export(x))
            self.ocelSideBarViewButtons[currName].clicked.connect(lambda checked, x=currName: self.show_table_window(x))


            self.ocelSideBarViewButtons[currName].setText("View")
            self.ocelSideBarExportButtons[currName].setText("Export")
            self.ocelSideBarDeleteButtons[currName].setText("Delete")
            self.ocelSideBarDeleteButtons[currName].setToolTip("Delete this log from collection")
            self.ocelSideBarExportButtons[currName].setToolTip("Export this log to ocel file and connect to Celonis")
            self.ocelSideBarViewButtons[currName].setToolTip("View events and objects of this log")
            sidebarOCELTitle.setText(currName)
            sidebarOCELTitle.setMaximumWidth(350)
            sidebarOCELTitle.setWordWrap(True)

            innerLayout = QtWidgets.QGridLayout(self.ocelSideBarFrames[currName])
            innerLayout.addWidget(sidebarOCELTitle)
            innerLayout.addWidget(self.ocelSideBarViewButtons[currName])
            innerLayout.addWidget(self.ocelSideBarExportButtons[currName])
            innerLayout.addWidget(self.ocelSideBarDeleteButtons[currName])

        self.sidebarScrollVerticalLayout.setSpacing(20)


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
        newName=text

        result = self.operatorFrames[pageNum].getNewLog(newName)
        if not result:
            return

        self.refreshSelection(newName)


    def removeFromLogs(self, name):
        if len(self.ocel_model.ocels) == 1:
            print("Can't delete last log")
            return
        self.ocel_model.removeOCEL(name)
        self.ocelSideBarFrames[name].setParent(None)
        del self.ocelSideBarFrames[name]
        if name in self.windows:
            del self.windows[name]
        self.refreshSelection(returnToOperatorSelectorPage=False)


    def refreshSelection(self, name="", returnToOperatorSelectorPage=True):

        for i in self.operatorFrames:
            i.refresh()
        
        # go back to operator overview page
        if returnToOperatorSelectorPage:
            self.operatorSectionStackedWidget.setCurrentIndex(0)

        # only add new log to sidebar if we just applied some operator
        if name == "":
            return

        # start for side scroll area
        i = len(self.ocel_model.ocels) - 1
        self.ocelSideBarFrames[name] = QtWidgets.QFrame(self.OCEL_list_frame)
        self.sidebarScrollVerticalLayout.addWidget(self.ocelSideBarFrames[name])

        self.ocelSideBarFrames[name].setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ocelSideBarFrames[name].setFrameShadow(QtWidgets.QFrame.Raised)

        sidebarOCELTitle = QtWidgets.QLabel(self.ocelSideBarFrames[name])
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        sidebarOCELTitle.setFont(font)
        sidebarOCELTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.ocelSideBarViewButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])
        self.ocelSideBarExportButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])
        self.ocelSideBarDeleteButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])

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
        innerLayout.addWidget(sidebarOCELTitle)
        innerLayout.addWidget(self.ocelSideBarViewButtons[name])
        innerLayout.addWidget(self.ocelSideBarExportButtons[name])
        innerLayout.addWidget(self.ocelSideBarDeleteButtons[name])

        self.ocelSideBarFrames[name].show()

        # end for side scroll area

    def show_table_window(self, name):
        if name not in self.windows:
            newWindow = QtWidgets.QMainWindow()
            ui = TableWindow(self.ocel_model, name)
            ui.setupUi(newWindow)
            self.windows[name] = newWindow
        self.windows[name].show()


    def viewObjectRelations(self):
        if "objRelationshipWindow" not in self.windows:
            newWindow = QtWidgets.QMainWindow()
            ui = ObjectWindow(self.ocel_model.getRelation())
            ui.setupUi(newWindow)
            self.windows["objRelationshipWindow"] = newWindow
        self.windows["objRelationshipWindow"].show()


    def export(self, name):
        print("exporting " + name)
        fileName = 'ocel_' + name + '.json'
        filePath = "exportedOCELs/" + fileName

        ocelDict = self.ocel_model.transformEventDfObjectDfToOcel(name)

        ocel_lib.export_log(ocelDict, filePath)
        dialog = ExportDialog(filePath, self.url, self.api)
        if dialog.exec():
            parameters = dialog.getInputs()
            
            # if no objects selected, don't export
            if len(parameters[2]) == 0:
                print(parameters[2])
                return

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
            self.operatorSectionStackedWidget.setCurrentIndex(0)
            return
        self.operatorFrames[pageNum].refresh()  
        self.operatorSectionStackedWidget.setCurrentIndex(pageNum+1) # +1 since the 0th page is the operator overview page


    def initOperatorPage(self, minerTitle, minerDescription, minerFrameClass):
        operatorPage = QtWidgets.QWidget()
        innerStackedLayout = QtWidgets.QGridLayout(operatorPage)

        # button to go back to overview page
        goBackButton = QtWidgets.QPushButton(operatorPage)
        goBackButton.clicked.connect(lambda: self.switchPage(0, toOverview=True ))
        innerStackedLayout.addWidget(goBackButton)
        goBackButton.setText("Go back to overview of operators")

        operatorFrame = minerFrameClass(operatorPage, self.ocel_model, minerTitle, minerDescription)
        innerStackedLayout.addWidget(operatorFrame)

        # page number of stacked widget
        pageNum = len(self.operatorFrames)

        # create frame on overview page for miner as well
        # frame on over view page
        minerFrame = QtWidgets.QFrame(self.operatorSelectorScrollAreaWidgetContents)
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

        self.operatorSelectorScrollGridLayout.addWidget(minerFrame)
       # self.operatorSelectorLayout.addWidget(minerFrame)

        # export and add-to-logs buttons on operator page
        operatorAddButton = QtWidgets.QPushButton(operatorPage)
        operatorAddButton.clicked.connect(lambda checked, x=pageNum: self.addToLogs(x))
        innerStackedLayout.addWidget(operatorAddButton)
        operatorAddButton.setText("Add to event logs")

        self.operatorSectionStackedWidget.addWidget(operatorPage)
        self.operatorFrames.append(operatorFrame)

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
        #    print(self.filePath)
        #    print(self.url)
        #    print(self.api)
        #    print(self.dataPool)
        #    print(self.dataModel)
        #    print(self.objects)
        #    print(self.transitions)
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

                # 'fileBig.pkl'
    with open('fileDf.pkl', 'rb') as file:
        # Call load method to deserialze
        ocel_model = pickle.load(file)

    url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
    token = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

    url = "https://students-pads.eu-1.celonis.cloud"
    token = "MmRlZTU4M2MtNjg5NS00YTU4LTlhOWEtODQ1ZDAxYTUzNTcxOmNaUjhMUllkSUQ4Y0E2cG9uRERkSWJSY2FtdVp0NkxLTVhuTm92TGk0Q0Fi"

    ui = TransformationCenter(ocel_model, url, token)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())