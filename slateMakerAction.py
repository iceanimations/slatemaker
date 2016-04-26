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
        self.vtrackItems = []

    def onClick(self):

        items = sorted(self.vtrackItems, key=lambda t:t.timelineIn(),
                reverse=True)

        if items:
            items = items[1:] + [ items[0] ]

        for vtrackItem in items:
            if slateMaker.Slate.isSlate(vtrackItem):
                continue
            sm = SlateMaker(vtrackItem)
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
            self.vtrackItems = vtrackItems
            event.menu.addAction(self)

    def unregister(self):
        hcore.events.unregisterInterest("kShowContextMenu/kTimeline",
                self.eventHandler)

