import PySide.QtGui as gui
import hiero.core as hcore

from . import slateMaker
reload(slateMaker)

from .slateMaker import SlateMaker

from . import slateMakerDialog
reload(slateMakerDialog)
from .slateMakerDialog import SlateMakerDialog

class SlateMakerAction(gui.QAction):
    '''Action to initial slate maker'''

    def __init__(self):
        ''' initialize Slate Maker Action'''
        gui.QAction.__init__(self, "Slate Maker", None)
        self.triggered.connect(self.onClick)
        hcore.events.registerInterest("kShowContextMenu/kTimeline",
                self.eventHandler)
        self.vtrackItem = None

    def onClick(self):
        sm = SlateMaker(self.vtrackItem)
        diag = SlateMakerDialog(sm)
        diag.exec_()
        if sm.slate:
            sm.removeSlate()
        else:
            sm.update()

    def eventHandler(self, event):
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
            self.vtrackItem = vtrackItems[0]
            event.menu.addAction(self)

    def unregister(self):
        hcore.events.unregisterInterest("kShowContextMenu/kTimeline",
                self.eventHandler)

