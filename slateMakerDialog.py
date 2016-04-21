import heiro.ui as hui
import PySide.QtGui as gui

from . import slateMaker
reload(slateMaker)

from .slateMaker import SlateMaker

class SlateMakerDialog(gui.QDialog):
    def __init__(self, parent=hui.mainWindow()):
        super(SlateMakerDialog, self).__init__(parent=parent)
        self.slateMaker = SlateMaker

