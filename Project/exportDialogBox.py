from PyQt5.QtWidgets import QApplication, QLineEdit, QDialogButtonBox, QFormLayout, QDialog, QComboBox, QLabel
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

        self.dataPool = QComboBox(self)
        self.dataModel = QLineEdit(self)
        self.selectObjLabel = QLabel(self)
        self.objects = QLineEdit(self)
        self.transitionLabel = QLabel(self)
        self.transitions = QLineEdit(self)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("Select Empty Data Pool", self.dataPool)
        layout.addRow("Data Model Name", self.dataModel)

        for i in range(len(self.celonis.pools)):
            self.dataPool.addItem("")
            self.dataPool.setItemText(i, self.celonis.pools[i].name)

        log = ocel.import_log(self.ocelPath)
        object_types = set()
        for ev_id, ev in log["ocel:events"].items():
            for obj_id in ev["ocel:omap"]:
                object_types.add(log["ocel:objects"][obj_id]["ocel:type"])
        object_types = ",".join(sorted(list(object_types)))
        layout.addRow("Insert the object types to consider separated by a comma without space", self.selectObjLabel)
        selected_object_types = "(default: "+object_types+") ->"
        layout.addRow(selected_object_types, self.objects)

        layout.addRow("Insert the transitions to consider in the model (IMPORTANT: avoid any cycle), where the entities of a transition are split by a , and the entities by ; without any space", self.transitionLabel)
        defaultTransitions = get_transitions(log)
        layout.addRow("(default: " + defaultTransitions + ") ->" , self.transitions)

        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)



    def getInputs(self):
        return (self.dataPool.currentText(), self.dataModel.text(), self.objects.text(), self.transitions.text())


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