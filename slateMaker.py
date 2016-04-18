import hiero.core as hcore
import hiero.ui as hui

import datetime
import PySide.QtGui as gui


class SlateDialog(gui.QDialog):
    pass

class SlateMaker(gui.QAction):
    ''' make slate on the timeline '''
    deleteExistingEffects = False
    doExpandHandles = True
    overlayTexts = [
            ('ForReview', 'For Review', 50, 0.2, 816, 1060, 362, 74),
            ('FrameNumber', 'Frame [metadata input/frame]', 50, 0.2, 1653, 27, 362, 72),
            ('ShotName', '[metadata hiero/clip]', 50, 0.2, 15, 20, 971, 72), ]
    slateTexts = [
            ( 'StartHandle', '', 50, 1.0, 1100, 90 , 800, 60 ),
            ( 'EndHandle'  , '', 50, 1.0, 1100, 222, 800, 60 ),
            ( 'Duration'   , '', 50, 1.0, 1100, 354, 800, 60 ),
            ( 'Date'       , '', 50, 1.0, 1100, 486, 800, 60 ),
            ( 'Version'    , '', 50, 1.0, 1100, 618, 800, 60 ),
            ( 'Shot'       , '', 50, 1.0, 1100, 750, 800, 60 ),
            ]
    standardResolution = (2048, 1152)
    maxExpandHandle = 6

    def __init__(self):
        ''' initialize Slate Maker Action'''
        gui.QAction.__init__(self, "Slate Maker", None)
        self.triggered.connect(self.doit)
        hcore.events.registerInterest("kShowContextMenu/kTimeline",
                self.eventHandler)
        self.vtrackItem = None

    def doit(self):

        if self.doExpandHandles:
            self.expandHandles()
        self.createOverlayTexts()
        self.createSlate()

    def setItem(self, item):
        self.vtrackItem = item
        self.updateItemTimes()


    def setMaxExpandHandle(self, maxHandle):
        self.maxExpandHandle = maxHandle

    def updateItemTimes(self):
        item = self.vtrackItem
        self.handleInLength = item.handleInLength()
        self.handleOutLength = item.handleOutLength()
        self.sourceIn= item.sourceIn()
        self.sourceOut= item.sourceOut()
        self.timelineIn = item.timelineIn()
        self.timelineOut = item.timelineOut()
        self.playbackSpeed = item.playbackSpeed()

    def expandHandles(self):
        ''' Remove Handles  '''
        duration = self.timelineOut - self.timelineIn + 1
        # totalDuration = duration + self.handleInLength + self.handleOutLength
        # totalSourceDuration = totalDuration * self.playbackSpeed

        item = self.vtrackItem

        self.expandHandleIn = min(self.handleInLength, self.maxExpandHandle)
        self.expandHandleOut = min(self.handleOutLength, self.maxExpandHandle)
        self.totalDuration = duration + self.expandHandleIn + self.expandHandleOut
        self.totalSourceDuration = self.totalDuration * self.playbackSpeed

        item.setTimelineIn(self.timelineIn - self.expandHandleIn)
        item.setSourceIn(self.handleInLength - self.expandHandleIn)
        item.setTimelineOut(self.timelineOut + self.expandHandleOut)
        item.setSourceOut(self.totalSourceDuration)
        item.setPlaybackSpeed(self.playbackSpeed)

    def createOverlayTexts(self):
        vtrack = self.vtrackItem.parentTrack()

        #if self.deleteExistingEffects:
            #linkedSubTrackItems = [x for x in self.vtrackItem.linkedItems() if
                    #isinstance(x, hcore.SubTrackItem)]
            #self.vtrackItem.unlinkAll()
            #for subitem in linkedSubTrackItems:
                #vtrack.removeItem(subitem)

        for data in self.overlayTexts:
            text2 = vtrack.createEffect(trackItem=self.vtrackItem, effectType='Text2')
            SlateMaker.modifyTextEffect(text2, data)


    def createSlate(self):
        vtrack = self.vtrackItem.parentTrack()
        slateItem = vtrack.createTrackItem('Slate')
        self.slateItem = slateItem
        slateItem.setSource(self.slateClip)
        slateTimelineIn = self.vtrackItem.timelineIn() - 1
        slateItem.setTimelineIn(slateTimelineIn)
        slateItem.setTimelineOut(slateTimelineIn)
        vtrack.addTrackItem(slateItem)

        for idx, data in enumerate( self.slateTexts ):
            slateText = vtrack.createEffect(trackItem=slateItem,
                    effectType='Text2', subTrackIndex=idx)
            data = list(data)
            if   idx == 0: data[1] = str(self.handleInLength)
            elif idx == 1: data[1] = str(self.handleOutLength)
            elif idx == 2: data[1] = str(self.timelineOut-self.timelineIn+1)
            elif idx == 3: data[1] = "[clock format [clock seconds] -format %d-%m-%y]"
            elif idx == 4: data[1] = self.vtrackItem.source().name()
            elif idx == 5: data[1] = self.vtrackItem.name()
            SlateMaker.modifyTextEffect( slateText, data )

    @staticmethod
    def modifyTextEffect(text2, data):
        text2.setName(data[0])
        format = text2.sequence().format()
        xRes = format.width()
        yRes = format.height()

        node = text2.node()
        node.knob('opacity').setValue(data[3])
        node.knob('font_size').setValue(data[2])
        node.knob('message').setValue(data[1])

        scale = xRes / float(SlateMaker.standardResolution[0])
        xPos  = round( data[4] * scale )
        yDiff = round( scale * ( data[5] - SlateMaker.standardResolution[1]/2 ) )
        yPos  = yRes/2 + yDiff
        font_size = round(data[2] * scale)

        box = node.knob('box')
        box.setX(xPos)
        box.setY(yPos)
        box.setR(xPos+data[6]*scale)
        box.setT(yPos+data[7]*scale)

        font_size = reduce( lambda l,n:l+list(n),
                zip(range(256),[font_size]*256), [])
        node.knob('font_size_values').resize(len(font_size), 1)
        node.knob('font_size_values').setValue(font_size)


    def printItemTimes(self):
        item = self.vtrackItem
        print item.sourceIn(), item.sourceOut(), item.sourceDuration()
        print item.timelineIn(), item.timelineOut(), item.duration()
        print item.handleInLength(), item.handleOutLength()
        print item.handleInTime(), item.handleOutTime()
        print item.source().duration(), item.playbackSpeed()

    def eventHandler(self, event):
        if not hasattr(event.sender, "selection"):
            return

        selection = event.sender.selection()
        if selection is None:
            selection = []

        vtrackItems = [item for item in selection if isinstance(item,
            hcore.TrackItem) and item.mediaType() == item.MediaType.kVideo]

        self.project = hcore.projects()[-1]
        slateClips = self.project.clips('Slate')

        if vtrackItems and slateClips:
            self.setItem(vtrackItems[0])
            self.slateClip = slateClips[0]
            event.menu.addAction(self)

    def unregister(self):
        hcore.events.unregisterInterest("kShowContextMenu/kTimeline",
                self.eventHandler)

