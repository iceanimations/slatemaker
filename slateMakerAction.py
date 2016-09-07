import PySide.QtGui as gui
import hiero.core as hcore

from . import slateMaker
reload(slateMaker)
from . import slateMakerDialog
reload(slateMakerDialog)

from .slateMaker import SlateMaker
from .slateMakerDialog import SlateMakerDialog

class ActionHandler(object):

    def event(self, event):
        if not hasattr(event.sender, "selection"):
            return

        selection = event.sender.selection()
        if selection is None:
            selection = []

        vtrackItems = [item for item in selection if isinstance(item,
            hcore.TrackItem) and item.mediaType() == item.MediaType.kVideo]

        self.project = hcore.projects()[-1]
        slateClips = SlateMaker.detectSlateClips()

        if vtrackItems and slateClips:
            self.vtrackItems = vtrackItems
            self.actions = [SlateMakerAction(self.vtrackItems), SlateMakerDialogAction(self.vtrackItems)]
            for action in self.actions:
                event.menu.addAction(action)

    def register(self):
        hcore.events.registerInterest("kShowContextMenu/kTimeline",
                self.event)

    def unregister(self):
        hcore.events.unregisterInterest("kShowContextMenu/kTimeline",
                self.event)


class SlateMakerAction(gui.QAction):
    '''Action to initial slate maker'''

    def __init__(self, vtrackItems=None):
        ''' initialize Slate Maker Action'''
        super(SlateMakerAction, self).__init__("Slate Maker", None)
        self.triggered.connect(self.onClick)
        if vtrackItems is not None:
            self.vtrackItems = vtrackItems

    def onClick(self):
        SlateMaker.makeSlates(self.vtrackItems)

class SlateMakerDialogAction(gui.QAction):
    ''' Action to show Dialog Window '''

    def __init__(self, vtrackItems=None):
        ''' initialize Slate Maker Action'''
        super(SlateMakerDialogAction, self).__init__("Slate Maker Options", None)
        self.triggered.connect(self.onClick)
        if vtrackItems is not None:
            self.vtrackItems = vtrackItems

    def onClick(self):
        diag = SlateMakerDialog(self.vtrackItems)
        diag.exec_()

