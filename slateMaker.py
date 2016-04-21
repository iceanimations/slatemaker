import hiero.core as hcore
import json

__slateClipKeyword__ = 'Slate'

class Slate(object):
    ''' Slate info object'''

    def __init__(self, vtrackItem=None, slateItem=None, tag=None):
        self.vtrackItem = vtrackItem
        self.slateItem = slateItem
        self._tag = tag

    @property
    def getTag(self):
        if not self._tag:
            self._tag = SlateTag.find(self.vtrackItem)
        return self._tag
    tag = property(fget=getTag)

    @property
    def overlayTexts(self):
        texts = {}
        for txt in SlateMaker.defaultOverlayTexts:
            defaultName = txt[0]
            for effect in self.vtrackItem.linkedItems():
                if effect.name().startswith(defaultName):
                    texts[defaultName]=effect
        return texts

    @property
    def slateTexts(self):
        texts = {}
        for txt in SlateMaker.defaultSlateTexts:
            defaultName = txt[0]
            for effect in self.slateItem.linkedItems():
                if effect.name().startswith(defaultName):
                    texts[defaultName]=effect
        return texts

    @classmethod
    def _slateName(cls, vtrackItem, tag=None):
        keyword = __slateClipKeyword__
        tagData = {}
        if not tag:
            tag = SlateTag.find(vtrackItem)
        if tag:
            tagData = tag.getData()
        if tagData.has_key('keyword'):
            keyword = tagData.get('keyword')
        return '_'.join([vtrackItem.name(), keyword])

    @classmethod
    def detectSlate(cls, vtrackItem):
        slateTime = vtrackItem.timelineIn()-1
        slateName = cls._slateName(vtrackItem)
        slateItem = None
        for item in vtrackItem.parentTrack().items():
            if item.name() == slateName and item.timelineIn() == slateTime:
                slateItem = item
        if slateItem:
            return Slate(vtrackItem, slateItem)

class SlateTag(object):
    '''class wrapping tags with some utility functions'''
    __tagName__ = 'SlateMaker'
    tag = None
    vtrackItem = None

    def __init__(self, tag, vtrackItem=None):
        if not isinstance(tag, hcore.Tag):
            raise TypeError, 'tag must of type hiero.core.Tag not %s'%type(tag)
        self.tag = tag
        if not isinstance(vtrackItem, hcore.TrackItem):
            raise TypeError, 'tag must of type hiero.core.VideoTrack not %s'%type(vtrackItem)
        self.vtrackItem = vtrackItem

    def getData(self):
        return json.loads(self.tag.note())
    def setData(self, data):
        self.tag.setNote(json.dumps(data))
    data = property(fget=getData)

    @classmethod
    def find(cls, vtrackItem):
        for tag in vtrackItem.tags():
            if tag.name().startswith(cls.__tagName__):
                return SlateTag(tag, vtrackItem)

    @classmethod
    def create(cls, vtrackItem, data=None, trimIn=0, trimOut=0,
            handlesCollapsed=False):
        tag = hcore.Tag(cls.__tagName__)

        if not data:
            data = {
                    'keyword': __slateClipKeyword__,
                    'trimIn': trimIn,
                    'trimOut': trimOut,
                    'handlesCollapsed': handlesCollapsed
            }

        tag.setNote(json.dumps(data))
        tag.setIcon('icons:TagNote.png')
        tag.setVisible(False)
        vtrackItem.addTag(tag)
        return SlateTag(tag, vtrackItem)

class SlateMaker(object):
    ''' make slate on the timeline '''
    _doExpandHandles = True
    _maxExpandHandle = 6

    # defaults
    standardResolution = (2048, 1152)
    defaultOverlayTexts = (
            ('ForReview', 'For Review', 50, 0.2, 816, 1060, 362, 74),
            ('FrameNumber', 'Frame [metadata input/frame]', 50, 0.2, 1653, 27, 362, 72),
            ('ShotName', '[metadata hiero/clip]', 50, 0.2, 15, 20, 971, 72),
            )
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

    overlayTexts = None
    slateTexts = None
    slate = None

    def __init__(self, vtrackItem, slateClip=None):
        ''' initialize Slate Maker Action'''
        self.setSlateClip(slateClip)
        self.setItem(vtrackItem)

    def setSlateClip(self, slateClip=None):
        if slateClip is None:
            slateClip = SlateMaker.detectSlateClips()[0]
        self.slateClip = slateClip

    def updateItemTimes(self):
        item = self.vtrackItem
        self.handleInLength = item.handleInLength()
        self.handleOutLength = item.handleOutLength()
        self.sourceIn = item.sourceIn()
        self.sourceOut = item.sourceOut()
        self.timelineIn = item.timelineIn()
        self.timelineOut = item.timelineOut()
        if self.handlesCollapsed and self.doExpandHandles:
            self.trimInVal = -1 * min(self.handleInLength, self.maxExpandHandle)
            self.trimOutVal = -1 * min(self.handleOutLength, self.maxExpandHandles)

    def setItem(self, item):
        self.vtrackItem = item
        self.slate = Slate.detectSlate(item)
        self.tag = SlateTag.find(self.vtrackItem)
        self.updateItemTimes()

    def update(self):
        self.updateHandles()
        self.updateSlate()
        self.updateOverlayTexts()
        self.updateSlateTexts()

    def removeSlate(self):
        if self.slate:
            vtrack = self.slate.vtrackItem.parentTrack()
            for item in self.slate.slateTexts.values():
                vtrack.removeSubTrackItem(item)
            for item in self.slate.overlayTexts.values():
                vtrack.removeSubTrackItem(item)
            vtrack.removeItem(self.slate.slateItem)
            if self.tag:
                self.slate.vtrackItem.removeTag(self.tag)
            self.slate = None
            self.tag = None

    def setDoExpandHandles(self, value):
        self._doExpandHandles = value
        self.updateItemTimes()
    def getDoExpandHandles(self):
        return self._doExpandHandles
    doExpandHandles = property(fget=getDoExpandHandles,
            fset=setDoExpandHandles)

    def setMaxExpandHandles(self, maxHandle):
        self._maxExpandHandles = maxHandle
        self.updateItemTimes()
    def getMaxExpandHandles(self):
        return self._maxExpandHandles
    maxExpandHandles = property(fset=setMaxExpandHandles,
            fget=getMaxExpandHandles)

    def getHandlesCollapsed(self):
        if self.tag:
            return self.tag.data.get( 'handlesCollapsed', False )
        return False
    def setHandlesCollpsed(self, value):
        if self.tag:
            data = self.tag.data
            data['handlesCollapsed'] = value
            self.tag.data = data
        else:
            self.tag = SlateTag.create(self.vtrackItem, handlesCollapsed=value)
    handlesCollapsed = property(fget=getHandlesCollapsed,
            fset=setHandlesCollpsed)

    def getTrimIn(self):
        if self.tag:
            return self.tag.data.get( 'trimIn', 0 )
        return 0
    def setTrimIn(self, value):
        if self.tag:
            data = self.tag.data
            data['trimIn'] = value
            self.tag.data = data
        else:
            self.tag = SlateTag.create(self.vtrackItem, handlesCollapsed=value)
    trimIn = property(fget=getTrimIn, fset=setTrimIn)

    def getTrimOut(self):
        if self.tag:
            return self.tag.data.get( 'trimOut', 0 )
        return 0
    def setTrimOut(self, value):
        if self.tag:
            data = self.tag.data
            data['trimOut'] = value
            self.tag.data = data
        else:
            self.tag = SlateTag.create(self.vtrackItem, handlesCollapsed=value)
    trimOut = property(fget=getTrimOut, fset=setTrimOut)

    def collapseHandles(self):
        item = self.vtrackItem
        if not self.handlesCollapsed:
            item.trimIn(self.trimIn * -1)
            item.trimOut(self.trimOut * -1)
            self.trimIn = 0
            self.trimOut = 0
            self.handlesCollapsed = True
            if self.slate:
                self.updateSlate()

    def expandHandles(self):
        item = self.vtrackItem
        if not self.handlesCollapsed:
            if self.slate:
                self.slate.slateItem.setTimelineIn(
                        item.timelineIn+self.trimInVal-1)
            item.trimIn(self.trimInVal)
            item.trimOut(self.trimOutVal)
            self.trimIn = self.trimInVal
            self.trimOut = self.trimOutVal
            self.handlesCollapsed = False

    def updateHandles(self):
        if self.handlesCollapsed and self.doExpandHandles:
            self.expandHandles()
        elif not (self.handlesCollapsed or self.doExpandHandles):
            self.collapseHandles()

    def calcTexts(self, defaults):
        texts = []
        for overlay in defaults:
            overlay = list(overlay)
            tmp = overlay[1]
            overlay[1] = tmp(self) if hasattr(tmp, '__call__') else tmp
            texts.append(overlay)
        return texts

    def getSlateTexts(self, recalc=False):
        if self.slateTexts is None or recalc:
            self.slateTexts = self.calcTexts(self.defaultSlateTexts)
        return self.slateTexts

    def getOverlayTexts(self, recalc=False):
        if self.overlayTexts is None or recalc:
            self.overlayTexts = self.calcTexts(self.defaultOverlayTexts)
        return self.overlayTexts

    def updateSlate(self):
        vtrack = self.vtrackItem.parentTrack()
        if self.slate:
            slateItem = self.slate.slateItem
        else:
            slateItem = vtrack.createTrackItem(
                    '_'.join([self.vtrackItem.name(), __slateClipKeyword__]))

        slateItem.setSource(self.slateClip)
        slateTimelineIn = self.vtrackItem.timelineIn() - 1
        slateItem.setTimelineIn(slateTimelineIn)
        slateItem.setTimelineOut(slateTimelineIn)
        if not self.slate:
            vtrack.addTrackItem(slateItem)
        self.slate = Slate(self.vtrackItem, slateItem)
        return self.slate

    def updateOverlayTexts(self):
        textEffects = []
        vtrack = self.vtrackItem.parentTrack()
        existingTexts = self.slate.overlayTexts
        for idx, data in enumerate( self.getOverlayTexts() ):
            if existingTexts.has_key(data[0]):
                text2 = existingTexts[data[0]]
            else:
                text2 = vtrack.createEffect(trackItem=self.vtrackItem,
                    effectType='Text2', subTrackIndex=idx)
            SlateMaker.modifyTextEffect(text2, data)
            textEffects.append(text2)
        self.overlayTextEffects = textEffects
        return textEffects

    def updateSlateTexts(self):
        vtrack = self.vtrackItem.parentTrack()
        textEffects = []
        existingTexts = self.slate.slateTexts
        for idx, data in enumerate( self.getSlateTexts() ):
            if existingTexts.has_key(data[0]):
                slateText = existingTexts[data[0]]
            else:
                slateText = vtrack.createEffect(trackItem=self.slate.slateItem,
                    effectType='Text2', subTrackIndex=idx)
            SlateMaker.modifyTextEffect( slateText, data )
            textEffects.append(slateText)
        return textEffects

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
        sm.update()

    def printItemTimes(self):
        item = self.vtrackItem
        print item.sourceIn(), item.sourceOut(), item.sourceDuration()
        print item.timelineIn(), item.timelineOut(), item.duration()
        print item.handleInLength(), item.handleOutLength()
        print item.handleInTime(), item.handleOutTime()
        print item.source().duration(), item.playbackSpeed()

