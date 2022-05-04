from PyQt5.QtWidgets import QApplication, QLineEdit, QDialogButtonBox, QFormLayout, QDialog, QComboBox, QLabel
from PyQt5 import QtCore, QtGui, QtWidgets

from pycelonis import get_celonis
import ocel

class ExportDialog(QDialog):
    def __init__(self, filePath, url, api, parent=None):
        super().__init__(parent)
        try:
            self.celonis = get_celonis(url, api)
        except:
            print("Invalid login info. Try again")
            return

        self.ocelPath = filePath
        self.api = api
        self.url = url

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.dataPool = QComboBox()
        self.dataModel = QLineEdit()
        self.selectObjLabel = QLabel()
        self.objects = QLineEdit()
        self.transitionLabel = QLabel()
        self.transitions = QLineEdit()

        label = QLabel(self)
        label.setText("Select Empty Data Pool")
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.dataPool, 0, 1)

        label = QLabel(self)
        label.setText("New Data Model Name")
        layout.addWidget(label, 1, 0)
        layout.addWidget(self.dataModel, 1, 1)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        # fetch all data pools and set them as options
        for i in range(len(self.celonis.pools)):
            self.dataPool.addItem("")
            self.dataPool.setItemText(i, self.celonis.pools[i].name)


        ######## Objects selection

        # object types label
        label = QLabel(self)
        label.setText("Select which object types you want to export:")
        layout.addWidget(label, 2, 0, 1, 2, QtCore.Qt.AlignHCenter)

        # scroll area for object selection
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollGridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        layout.addWidget(self.scrollArea, 3, 0, 1, 2)

        log = ocel.import_log(self.ocelPath)
        object_types = set()
        for ev_id, ev in log["ocel:events"].items():
            for obj_id in ev["ocel:omap"]:
                object_types.add(log["ocel:objects"][obj_id]["ocel:type"])
        
        object_types = sorted(list(object_types))

        # add object types to scrollarea for selection
        self.objectWidgets = []
        for i in range(len(object_types)):
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            label.setText(object_types[i])
            self.scrollGridLayout.addWidget(label, i, 0, QtCore.Qt.AlignCenter)
            checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setChecked(True)
            self.scrollGridLayout.addWidget(checkbox, i, 1, QtCore.Qt.AlignCenter)
            self.objectWidgets.append((label, checkbox))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)


        ###### Transitions selection

        # only need to select transitions if there are more than 1 object
        if len(object_types) > 1:
            # transition selection label
            label = QLabel(self)
            label.setText("Select which transitions to consider (IMPORTANT: avoid any cycle):")
            layout.addWidget(label, 4, 0, 1, 2, QtCore.Qt.AlignHCenter)

            # scroll area for object selection
            self.scrollAreaTransitions = QtWidgets.QScrollArea()
            self.scrollAreaTransitions.setWidgetResizable(True)
            self.scrollAreaWidgetContentsTransitions = QtWidgets.QWidget()
            self.scrollGridLayoutTransitions = QtWidgets.QGridLayout(self.scrollAreaWidgetContentsTransitions)
            layout.addWidget(self.scrollAreaTransitions, 5, 0, 1, 2)

            possibleTransitions = []
            for i in range(len(object_types)):
                for obj2 in object_types[i:]:
                    obj1 = object_types[i]
                    if obj1 != obj2:
                        possibleTransitions.append((obj1, obj2))

            # add transitions to scrollarea for selection
            self.transitionWidgets = []
            for i in range(len(possibleTransitions)):
                obj1 = possibleTransitions[i][0]
                obj2 = possibleTransitions[i][1]

                label1 = QtWidgets.QLabel(self.scrollAreaWidgetContentsTransitions)
                label1.setText(obj1)
                self.scrollGridLayoutTransitions.addWidget(label1, i, 0, QtCore.Qt.AlignCenter)
                label2 = QtWidgets.QLabel(self.scrollAreaWidgetContentsTransitions)
                label2.setText(obj2)
                self.scrollGridLayoutTransitions.addWidget(label2, i, 1, QtCore.Qt.AlignCenter)

                checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContentsTransitions)
                checkbox.setChecked(True)
                self.scrollGridLayoutTransitions.addWidget(checkbox, i, 2, QtCore.Qt.AlignCenter)
                self.transitionWidgets.append((label1, label2, checkbox))

            self.scrollAreaTransitions.setWidget(self.scrollAreaWidgetContentsTransitions)


        layout.addWidget(buttonBox, 6, 0, 1, 2, QtCore.Qt.AlignCenter)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)



    def getInputs(self):
        objects = []
        for label, checkbox in self.objectWidgets:
            if checkbox.isChecked:
                objects.append(label.text())
        transitions = []
        if len(objects) > 1:
            for label1, label2, checkbox in self.transitionWidgets:
                if checkbox.isChecked:
                    obj1 = label1.text()
                    obj2 = label2.text()
                    if obj1 in objects and obj2 in objects:
                        transitions.append((obj1, obj2))
        return (self.dataPool.currentText(), self.dataModel.text(), objects, "") # self.transitions.text())


def get_transitions(log, allowed_object_types=None):
    transitions = set()
    for event in log["ocel:events"].values():
        for objid in event["ocel:omap"]:
            obj = log["ocel:objects"][objid]
            objtype = obj["ocel:type"]
            if allowed_object_types is None or objtype in allowed_object_types:
                for objid2 in event["ocel:omap"]:
                    if objid != objid2:
                        obj2 = log["ocel:objects"][objid2]
                        objtype2 = obj2["ocel:type"]
                        if allowed_object_types is None or objtype2 in allowed_object_types:
                            if objtype < objtype2:
                                transitions.add((objtype, objtype2))
    transitions = ";".join(sorted(list(",".join(list(x)) for x in transitions)))
    return transitions

if __name__ == '__main__':

    url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
    api = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

    import sys
    app = QApplication(sys.argv)
    dialog = ExportDialog("ocel_test", url, api)
    if dialog.exec():
        print(dialog.getInputs())
    exit(0)