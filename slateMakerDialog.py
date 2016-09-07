import hiero.ui as hui
import PySide.QtGui as gui

from . import slateMakerSettings
reload(slateMakerSettings)
from . import slateMaker
reload(slateMaker)

from .slateMaker import SlateMaker
from .slateMakerSettings import SlateMakerSettings

class SlateMakerDialog(gui.QDialog):
    ''' The SlateMaker Options Dialog '''
    settings = SlateMakerSettings()

    def __init__(self, vtrackItems=None, parent=hui.mainWindow()):
        super(SlateMakerDialog, self).__init__(parent=parent)

        if vtrackItems is not None:
            self.vtrackItems = vtrackItems

        self.layout = gui.QVBoxLayout(self)
        self.setWindowTitle('Slate Maker Options')

        self.doMoveOutCheck = self.addCheckBox('Move Slate to New Sequence',
                checked=self.settings.doMoveOut)
        self.doMoveUpCheck = self.addCheckBox('Move Slate to New Track',
                checked=self.settings.doMoveUp)
        self.doExpandHandlesCheck = self.addCheckBox('Expand Handles',
                checked=self.settings.doExpandHandles)

        self.maxExpandLayout = gui.QHBoxLayout()
        self.layout.addLayout(self.maxExpandLayout)
        self.maxExpandSpinBox = gui.QSpinBox()
        self.maxExpandSpinBox.setMinimum(0)
        self.maxExpandSpinBox.stepBy(1)
        self.maxExpandSpinBox.setValue(self.settings.maxExpandHandles)
        self.maxExpandLayout.addWidget(self.maxExpandSpinBox)
        self.maxExpandLayout.addWidget(gui.QLabel('Expand Max'))

        self.slateTextFrame = gui.QFrame()
        self.slateLayout = gui.QVBoxLayout()
        self.slateTextFrame.setLayout(self.slateLayout)
        self.layout.addWidget(self.slateTextFrame)
        self.slateLayout.addWidget(gui.QLabel('Slate Texts Display:'))
        self.slateChecks = []

        for slateText in SlateMaker.defaultSlateTexts:
            name = slateText[0]
            on = self.settings.displaySlateTexts.get(name, True)
            newCheck = self.addCheckBox(name, checked=on, layout=self.slateLayout)
            self.slateChecks.append(newCheck)

        self.overlayTextFrame = gui.QFrame()
        self.overlayLayout = gui.QVBoxLayout()
        self.overlayTextFrame.setLayout(self.overlayLayout)
        self.layout.addWidget(self.overlayTextFrame)
        self.overlayLayout.addWidget(gui.QLabel('Overlay Texts Display:'))
        self.overlayChecks = []

        for overlay in SlateMaker.defaultOverlayTexts:
            name = overlay[0]
            on = self.settings.displayOverlayTexts.get(name, True)
            newCheck = self.addCheckBox(name, checked=on, layout=self.overlayLayout)
            self.overlayChecks.append(newCheck)

        self.buttonLayout = gui.QHBoxLayout()
        self.saveButton = gui.QPushButton('Save')
        self.saveButton.clicked.connect(self.save)
        self.applyButton = gui.QPushButton('Apply')
        self.cancelButton = gui.QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)

        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.saveButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(self.buttonLayout)

    def save(self, *args):
        self.settings.doMoveOut = self.doMoveOutCheck.isChecked()
        self.settings.doMoveUp = self.doMoveUpCheck.isChecked()
        self.settings.doExpandHandles = self.doExpandHandlesCheck.isChecked()
        self.settings.maxExpandHandles = self.maxExpandSpinBox.value()
        self.settings.displaySlateTexts = {check.text(): check.isChecked() for
                check in self.slateChecks}
        self.settings.displayOverlayTexts = {check.text(): check.isChecked() for
                check in self.overlayChecks}

    def apply(self, *args):
        self.save()
        SlateMaker.makeSlates(self.vtrackItems)

    def addCheckBox(self, label, checked=True, layout=None):
        if layout is None:
            layout = self.layout
        newcb = gui.QCheckBox()
        newcb.setText(label)
        newcb.setChecked(checked)
        layout.addWidget(newcb)
        return newcb

