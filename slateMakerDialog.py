import hiero.ui as hui
import PySide.QtGui as gui

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

        self.moveFrame = gui.QFrame()
        self.layout.addWidget(self.moveFrame)
        self.moveLayout = gui.QVBoxLayout()
        self.moveFrame.setLayout(self.moveLayout)
        self.moveLayout.addWidget(gui.QLabel('Move / Copy:'))
        self.moveGroupBox = gui.QGroupBox('Move / Copy')
        # self.moveLayout.addWidget(self.moveGroupBox)
        self.doMoveOutCheck = self.addCheckBox(
                'Copy Slate to New Sequence',
                checked=self.settings.doMoveOut, radio=True,
                layout=self.moveLayout)
        self.doMoveUpCheck = self.addCheckBox(
                'Move Colliding Slate to New Track',
                checked=self.settings.doMoveUp, radio=True,
                layout=self.moveLayout)
        self.doPushCheck = self.addCheckBox(
                'Push Colliding Slates towards Right',
                checked=not (self.settings.doMoveOut or
                    self.settings.doMoveUp), radio=True,
                layout=self.moveLayout)

        self.showLabelsFrame = gui.QFrame()
        self.showLabelsLayout = gui.QVBoxLayout()
        self.showLabelsFrame.setLayout(self.showLabelsLayout)
        self.showLabelsLayout.addWidget(gui.QLabel('Labels:'))
        self.doMakeLabelsCheck = self.addCheckBox('Make Labels',
                checked=self.settings.doMakeLabels,
                layout=self.showLabelsLayout)
        self.showLabelsLayout.addWidget(self.doMakeLabelsCheck)
        self.layout.addWidget(self.showLabelsFrame)

        self.expandFrame = gui.QFrame()
        self.expandLayout = gui.QVBoxLayout()
        self.expandLayout.addWidget(gui.QLabel('Handle Expansion:'))
        self.layout.addWidget(self.expandFrame)
        self.expandFrame.setLayout(self.expandLayout)
        self.doExpandHandlesCheck = self.addCheckBox('Expand Handles',
                checked=self.settings.doExpandHandles,
                layout=self.expandLayout)
        self.maxExpandLayout = gui.QHBoxLayout()
        self.expandLayout.addLayout(self.maxExpandLayout)
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
        self.applyButton = gui.QPushButton('Save + Apply')
        self.applyButton.clicked.connect(self.apply)
        self.cancelButton = gui.QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)

        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.saveButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(self.buttonLayout)

        self.layout.addStretch(1)

    def save(self, *args):
        self.settings.doMoveOut = self.doMoveOutCheck.isChecked()
        self.settings.doMoveUp = self.doMoveUpCheck.isChecked()
        self.settings.doExpandHandles = self.doExpandHandlesCheck.isChecked()
        self.settings.maxExpandHandles = self.maxExpandSpinBox.value()
        self.settings.displaySlateTexts = {check.text(): check.isChecked() for
                check in self.slateChecks}
        self.settings.displayOverlayTexts = {check.text(): check.isChecked() for
                check in self.overlayChecks}
        self.settings.doMakeLabels = self.doMakeLabelsCheck.isChecked()
        self.accept()

    def apply(self, *args):
        self.save()
        SlateMaker.makeSlates(self.vtrackItems)
        self.accept()

    def addCheckBox(self, label, checked=True, layout=None, radio=False):
        if layout is None:
            layout = self.layout
        if radio:
            newcb = gui.QRadioButton()
        else:
            newcb = gui.QCheckBox()
        newcb.setText(label)
        newcb.setChecked(checked)
        layout.addWidget(newcb)
        return newcb

