
import pickle
from tableWindow import TableWindow
from operatorFrames.matchMinerFrame import MatchMinerFrame
from operatorFrames.interleavedMinerFrame import InterleavedMinerFrame
from operatorFrames.nonInterleavedMinerFrame import NonInterleavedMinerFrame
from objRelationWindow import ObjectWindow
from operatorFrames.manualMinerFrame import ManualMinerFrame
from operatorFrames.filterFrame import FilterFrame
from operatorFrames.flattenFrame import FlattenFrame
from operatorFrames.concatFrame import ConcatFrame
from operatorFrames.aggregateFrame import AggregateFrame
from operatorFrames.eventRecipeFrame import EventRecipeFrame

from ocel_model import *

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
        MainWindow.resize(1250, 700)
        MainWindow.setMinimumWidth(1250)


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        # define rightFrame and layout for operator area
        self.rightFrame = QtWidgets.QFrame(self.centralwidget)
        self.rightFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rightGridLayout = QtWidgets.QGridLayout(self.rightFrame)
        # add rightFrame to most outer layout
        self.gridLayout.addWidget(self.rightFrame, 0, 1, 2, 2)

        ################## define global fonts
        # title font
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(18)
        self.titleFont = font
        # middle font
        font = QtGui.QFont()
        font.setPointSize(15)
        self.middleFont = font
        # standard font
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(13)
        self.standardFont = font

        ################## start of code for sidebar
        
        # define scroll area for list of OCELs + associated layout
        OCEL_list_scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        OCEL_list_scrollArea.setMinimumWidth(360)
        OCEL_list_scrollArea.setMaximumWidth(460)
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
        sidebarTitlelabel.setFont(self.titleFont)
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

        # keep track of opened openedWindows to view tables or object relationships so that we don't have to re-apply transformation from data to PyQt Table
        self.openedWindows = {}

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
        operatorSelectorTitle.setFont(self.titleFont)
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
        description = "Merge objects across logs based on matching attribute values."
        self.initOperatorPage("Match Miner", description, MatchMinerFrame)
        description = "Merge objects across logs based on manual matchings of activities of the logs."
        self.initOperatorPage("Manual Miner", description, ManualMinerFrame)
        description = "Merge objects across logs based on interleaving timestamps of events in the logs."
        self.initOperatorPage("Interleaved Miner", description, InterleavedMinerFrame)
        description = "Merge objects across logs based on interleaving timestamps of events in the logs (non-interleaved)."
        self.initOperatorPage("Non-Interleaved Miner", description, NonInterleavedMinerFrame)
        description = "Filter event log based on activities, attributes, objects, object types, or timestamps."
        self.initOperatorPage("Filter Event Log", description, FilterFrame)
        description = "Map all events to objects of one object type based on object relationships."
        self.initOperatorPage("Flatten Event Log", description, FlattenFrame)
        description = "Merge all events of two logs into one without merging any objects or events."
        self.initOperatorPage("Concatenate Event Log", description, ConcatFrame)
        description = "Aggregate events with matching activity names and timestamps. Objects of the matching events are merged into first occurence."
        self.initOperatorPage("Aggregate Event Log", description, AggregateFrame)
        description = "Specify sequence of low-level events and turn them into one high-level event. Besides sequence of activity, specify sequence based on objects, types, attribute values, object relations, and more"
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

        # initialize collection of sidebar elements
        self.ocelSideBarFrames = {}
        self.ocelSideBarExportButtons = {}
        self.ocelSideBarDeleteButtons = {}
        self.ocelSideBarViewButtons = {}

        ocel_names = list(self.ocel_model.getOcelNames())
        ocel_names.sort()

        # for every OCEL: add frame to sidebar with export, delete, and view buttons
        for name in ocel_names:
            self.addOcelFrameToSidebar(name)

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
        if len(self.ocel_model.getOcelNames()) == 1:
            print("Can't delete last log")
            return
        self.ocel_model.removeOCEL(name)
        self.ocelSideBarFrames[name].setParent(None)
        del self.ocelSideBarFrames[name]
        if name in self.openedWindows:
            del self.openedWindows[name]
        self.refreshSelection(returnToOperatorSelectorPage=False)

    def addOcelFrameToSidebar(self, name):
        # add frame and delete/view/export button for an OCEL to the sidebar

        self.ocelSideBarFrames[name] = QtWidgets.QFrame(self.OCEL_list_frame)
        self.sidebarScrollVerticalLayout.addWidget(self.ocelSideBarFrames[name])
    
        self.ocelSideBarFrames[name].setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ocelSideBarFrames[name].setFrameShadow(QtWidgets.QFrame.Raised)

        sidebarOCELTitle = QtWidgets.QLabel(self.ocelSideBarFrames[name])
        sidebarOCELTitle.setFont(self.standardFont)
        sidebarOCELTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.ocelSideBarViewButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])
        self.ocelSideBarExportButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])
        self.ocelSideBarDeleteButtons[name] = QtWidgets.QPushButton(self.ocelSideBarFrames[name])

        self.ocelSideBarDeleteButtons[name].clicked.connect(lambda checked, x=name: self.removeFromLogs(x))
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


    def refreshSelection(self, name="", returnToOperatorSelectorPage=True):
        # is called after applying an operator
        # adds new OCEL to sidebar and refreshes parameters / standard view

        # refresh selection of all operators to account for new log
        for i in self.operatorFrames:
            i.refresh()
        
        # go back to operator overview page (after applying operator)
        if returnToOperatorSelectorPage:
            self.operatorSectionStackedWidget.setCurrentIndex(0)

        # only add new log to sidebar if we just applied some operator (e.g. in case we delete, we don't want to add anything)
        if name == "":
            return

        self.addOcelFrameToSidebar(name)


    def show_table_window(self, name):
        if name not in self.openedWindows:
            newWindow = QtWidgets.QMainWindow()
            ui = TableWindow(self.ocel_model, name)
            ui.setupUi(newWindow)
            self.openedWindows[name] = newWindow
        self.openedWindows[name].show()


    def viewObjectRelations(self):
        if "objRelationshipWindow" not in self.openedWindows:
            newWindow = QtWidgets.QMainWindow()
            ui = ObjectWindow(self.ocel_model.getRelation())
            ui.setupUi(newWindow)
            self.openedWindows["objRelationshipWindow"] = newWindow
        self.openedWindows["objRelationshipWindow"].show()


    def export(self, name):
        print("exporting " + name)
        fileName = 'ocel_' + name + '.json'
        filePath = "exportedOCELs/" + fileName

        ocelDict = self.ocel_model.transformEventDfObjectDfToOcel(name)

        ocel_lib.export_log(ocelDict, filePath)
        dialog = ExportDialog(filePath, self.url, self.api)
        if dialog.exec():
            parameters = dialog.getInputs()
            # parameters of shape (datapool, datamode, objectTypes, transitions)
            
            # if no objects selected, don't export
            if len(parameters[2]) == 0:
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
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        minerFrame.setSizePolicy(sizePolicy)
        minerFrame.setMaximumWidth(1000)

        minerFrameLayout = QtWidgets.QGridLayout(minerFrame)
        minerFrameLayout.setSpacing(20)
        # miner title on overview page
        minerTitleLabel = QtWidgets.QLabel(minerFrame)
        minerTitleLabel.setFont(self.titleFont)
        minerTitleLabel.setText(minerTitle)
        # miner description on overview page
        minerDescriptionLabel = QtWidgets.QLabel(minerFrame)
        minerDescriptionLabel.setFont(self.middleFont)
        minerDescriptionLabel.setText(minerDescription)
        minerDescriptionLabel.setWordWrap(True)

        # miner button on overview page
        minerButton = QtWidgets.QPushButton(minerFrame)
        minerButton.clicked.connect(lambda checked, x=pageNum: self.switchPage(x))
        minerButton.setText("Apply Operator")

        # layout
        minerFrameLayout.addWidget(minerTitleLabel)
        minerFrameLayout.addWidget(minerDescriptionLabel)
        minerFrameLayout.addWidget(minerButton)

        self.operatorSelectorScrollGridLayout.addWidget(minerFrame)

        # export and add-to-logs buttons on operator page
        operatorAddButton = QtWidgets.QPushButton(operatorPage)
        operatorAddButton.clicked.connect(lambda checked, x=pageNum: self.addToLogs(x))
        innerStackedLayout.addWidget(operatorAddButton)
        operatorAddButton.setText("Add to event logs")
        operatorAddButton.setToolTip("Apply " + minerTitle + " with specified parameters and add output to list of logs")  


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
    with open('fileBig.pkl', 'rb') as file:
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