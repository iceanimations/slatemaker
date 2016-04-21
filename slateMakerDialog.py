import hiero.ui as hui
import PySide.QtGui as gui

class SlateMakerDialog(gui.QDialog):
    def __init__(self, slateMaker, parent=hui.mainWindow()):
        super(SlateMakerDialog, self).__init__(parent=parent)
        self.slateMaker = slateMaker

