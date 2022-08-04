from asyncio import events
from PyQt5 import QtCore, QtGui, QtWidgets
import pickle
import pandas as pd
from tableWindow import PandasTableModel

class HelpWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(HelpWindow, self).__init__()
        self.title = "Image Viewer"
        self.setWindowTitle(self.title)

        label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap('overviewTutorial.png')
        label.setPixmap(pixmap)
        self.setCentralWidget(label)
    #    self.resize(pixmap.width(), pixmap.height())

    #    QtCore.QMetaObject.connectSlotsByName(MainWindow)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    window = HelpWindow()
#    ui.setupUi(MainWindow)
    window.show()
    sys.exit(app.exec_())
