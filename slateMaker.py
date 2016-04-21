import hiero.core as hcore
import json

__slateClipKeyword__ = 'Slate'
__tagName__ = 'SlateMaker'

class Slate(object):

    def __init__(self, vtrackItem=None, slateItem=None, overlayTexts=None,
            slateTexts=None):
        self.vtrackItem = vtrackItem
        self.slateItem = slateItem
        self.tag = None
        self.overlayTexts = overlayTexts if overlayTexts else []
        self.slateTexts = slateTexts if slateTexts else []


class SlateMaker(object):
    ''' make slate on the timeline '''
    doExpandHandles = True
    defaultOverlayTexts = (
            ('ForReview', 'For Review', 50, 0.2, 816, 1060, 362, 74),
            ('FrameNumber', 'Frame [metadata input/frame]', 50, 0.2, 1653, 27, 362, 72),
            ('ShotName', '[metadata hiero/clip]', 50, 0.2, 15, 20, 971, 72),
            )
    overlayTexts = None
    defaultSlateTexts = (
            ( 'StartHandle', lambda self: str(self.trimIn*-1)
                , 50, 1.0, 1100, 90 , 800, 60 ),
            ( 'EndHandle'  , lambda self: str(self.trimOut*-1)
                , 50, 1.0, 1100, 222, 800, 60 ),
            ( 'Duration', lambda self: str(self.timelineOut-self.timelineIn+1)
                , 50, 1.0, 1100, 354, 800, 60 ),
            ( 'Date'       , "[clock format [clock seconds] -format %d-%m-%y]"
                , 50, 1.0, 1100, 486, 800, 60 ),
            ( 'Version'    , lambda self: self.vtrackItem.source().name()
                , 50, 1.0, 1100, 618, 800, 60 ),
            ( 'Shot'       , lambda self: self.vtrackItem.name()
                , 50, 1.0, 1100, 750, 800, 60 )
            )
    slateTexts = None
    standardResolution = (2048, 1152)
    maxExpandHandle = 6
    slate = None

    def __init__(self, vtrackItem, slateClip=None):
        ''' initialize Slate Maker Action'''
        self.setSlateClip(slateClip)
        self.setItem(vtrackItem)

    def updateSlate(self):

        if self.slate:
            print 'updating'
        else:
            print 'creating new'
            if self.doExpandHandles:
                self.expandHandles()
            self.createOverlayTexts()
            self.createSlate()

    def removeSlate(self):
        if self.slate:
            print 'remove slate'

    def setItem(self, item):
        self.vtrackItem = item
        self.updateItemTimes()

    def setSlateClip(self, slateClip=None):
        if slateClip is None:
            slateClip = self.findSlateItem()
        if slateClip is None:
            slateClip = SlateMaker.detectSlateClips()[0]
        self.slateClip = slateClip

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
        item = self.vtrackItem
        self.trimIn = -1 * min(self.handleInLength, self.maxExpandHandle)
        self.trimOut = -1 * min(self.handleOutLength, self.maxExpandHandle)
        item.trimIn(self.trimIn)
        item.trimOut(self.trimOut)

    def getOverlayTexts(self, recalc=False):
        if self.overlayTexts is None or recalc:
            self.overlayTexts = self.calcTexts(self.defaultOverlayTexts)
        return self.overlayTexts

    def calcTexts(self, defaults):
        texts = []
        for overlay in defaults:
            overlay = list(overlay)
            tmp = overlay[1]
            overlay[1] = tmp(self) if hasattr(tmp, '__call__') else tmp
            texts.append(overlay)
        return texts

    def createOverlayTexts(self):
        textEffects = []
        vtrack = self.vtrackItem.parentTrack()
        for idx, data in enumerate( self.getOverlayTexts() ):
            text2 = vtrack.createEffect(trackItem=self.vtrackItem,
                    effectType='Text2', subTrackIndex=idx)
            SlateMaker.modifyTextEffect(text2, data)
            textEffects.append(text2)
        self.overlayTextEffects = textEffects
        return textEffects

    def getSlateTexts(self, recalc=False):
        if self.slateTexts is None or recalc:
            self.slateTexts = self.calcTexts(self.defaultSlateTexts)
        return self.slateTexts

    def createSlate(self):
        vtrack = self.vtrackItem.parentTrack()
        slateItem = vtrack.createTrackItem(
                '_'.join([self.vtrackItem.name(), __slateClipKeyword__]))
        self.slateItem = slateItem
        slateItem.setSource(self.slateClip)
        slateTimelineIn = self.vtrackItem.timelineIn() - 1
        slateItem.setTimelineIn(slateTimelineIn)
        slateItem.setTimelineOut(slateTimelineIn)
        vtrack.addTrackItem(slateItem)
        self.createTag()
        self.createSlateTexts()
        return slateItem

    def createSlateTexts(self):
        vtrack = self.vtrackItem.parentTrack()
        textEffects = []
        for idx, data in enumerate( self.getSlateTexts() ):
            slateText = vtrack.createEffect(trackItem=self.slateItem,
                    effectType='Text2', subTrackIndex=idx)
            SlateMaker.modifyTextEffect( slateText, data )
            textEffects.append(slateText)
        return textEffects

    def createTransition(self):
        slateItem, vtrackItem = self.slateItem, self.vtrackItem
        transition = hcore.Transition()
        transition = transition.createDissolveTransition(slateItem, vtrackItem, 1, 1)
        self.vtrackItem.parentTrack().addTransition(transition)
        return transition

    def createTag(self):
        tag = hcore.Tag('SlateMaker')
        data = {
                'keyword': __slateClipKeyword__,
                'trimIn': self.trimIn,
                'trimOut': self.trimOut
        }
        tag.setNote(json.dumps(data))
        tag.setIcon('icons:TagNote.png')
        tag.setVisible(False)
        self.tag = tag
        self.vtrackItem.addTag(tag)
        return tag

    def _slateName(self):
        keyword = __slateClipKeyword__
        tagdata = self._getTagData()
        if tagdata.has_key('keyword'):
            keyword = tagdata.get('keyword')
        return '_'.join([self.vtrackItem.name(), keyword])

    def _getTagData(self):
        data = {}
        for tag in self.vtrackItem.tags():
            if tag.name().beginswith(__tagName__):
                data = json.loads(tag.note())
        return data

    def findSlateItem(self):
        slateTime = self.timelineIn() - 1
        slateName = self._slateName()
        for item in self.vtrackItem.parentTrack().items():
            if item.name() == slateName and item.timelineIn() == slateTime:
                self.slateItem = item
        return self.slateItem

    @staticmethod
    def modifyTextEffect(text2, data):
        text2.setName(data[0])
        format = text2.sequence().format()
        xRes = format.width()
        yRes = format.height()

        node = text2.node()
        node.knob('message').setValue(data[1])
        node.knob('font_size').setValue(data[2])
        node.knob('opacity').setValue(data[3])

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

    @staticmethod
    def detectSlateClips():
        project = hcore.projects()[-1]
        return project.clips(__slateClipKeyword__)

    @staticmethod
    def makeNew(vtrackItem, slateClip=None):
        sm = SlateMaker(vtrackItem, slateClip)
        sm.updateSlate()

    def printItemTimes(self):
        item = self.vtrackItem
        print item.sourceIn(), item.sourceOut(), item.sourceDuration()
        print item.timelineIn(), item.timelineOut(), item.duration()
        print item.handleInLength(), item.handleOutLength()
        print item.handleInTime(), item.handleOutTime()
        print item.source().duration(), item.playbackSpeed()

