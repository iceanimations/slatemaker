import hiero.core as hcore
import json
from collections import namedtuple
import re

from .slateMakerSettings import SlateMakerSettings

__slateClipKeyword__ = 'Slate'

class Slate(object):
    ''' Slate info object '''

    def __init__(self, vtrackItem=None, slateItem=None, tag=None):
        self.vtrackItem = vtrackItem
        self.slateItem = slateItem
        self._tag = tag

    def getTag(self):
        if not self._tag:
            self._tag = SlateTag.find(self.vtrackItem)
        return self._tag
    tag = property(fget=getTag)

    @property
    def overlayTexts(self):
        texts = {}
        for txt in SlateMaker.defaultOverlayTexts:
            defaultName = txt.name
            for effect in self.vtrackItem.linkedItems():
                if effect.name().startswith(defaultName):
                    texts[defaultName]=effect
        return texts

    @property
    def slateTexts(self):
        texts = {}
        for txt in SlateMaker.defaultSlateTexts:
            defaultName = txt.name
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

    @classmethod
    def isSlate(cls, vtrackItem):
        return vtrackItem.name().endswith(__slateClipKeyword__)

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
        SlateTag.removeSlateTags(self.vtrackItem)
        self.tag.setNote(json.dumps(data))
        self.vtrackItem.addTag(self.tag)
    data = property(fget=getData, fset=setData)

    @classmethod
    def removeSlateTags(cls, vtrackItem):
        for tag in vtrackItem.tags():
            if cls.isSlateTag(tag):
                vtrackItem.removeTag(tag)

    @classmethod
    def isSlateTag(cls, tag):
        return tag.name().startswith(cls.__tagName__)

    @classmethod
    def find(cls, vtrackItem):
        for tag in vtrackItem.tags():
            if SlateTag.isSlateTag(tag):
                return SlateTag(tag, vtrackItem)

    @classmethod
    def create( cls, vtrackItem, data=None, trimIn=0, trimOut=0,
            handlesCollapsed=True, move=0, push=0 ):
        tag = hcore.Tag( cls.__tagName__ )

        if not data:
            data = {
                    'keyword': __slateClipKeyword__,
                    'trimIn': trimIn,
                    'trimOut': trimOut,
                    'handlesCollapsed': handlesCollapsed,
                    'move': move,
                    'push': push
            }

        tag.setNote( json.dumps(data) )
        tag.setIcon( 'icons:TagNote.png' )
        tag.setVisible( True )
        vtrackItem.addTag( tag )
        return SlateTag( tag, vtrackItem )

class TagData(object):
    def __init__(self, keyword, default):
        self.keyword = keyword
        self.default = default

    def __get__(self, instance, owner):
        tag = instance.tag
        if tag:
            return tag.data.get(self.keyword, self.default)
        return self.default

    def __set__(self, instance, value):
        if not instance.tag:
            instance.tag = SlateTag.create(instance.vtrackItem)
        data = instance.tag.data
        data[self.keyword]=value
        instance.tag.data = data

class TextEffectData(namedtuple('_TextEffectData', [
        'name',
        'message',
        'font_size',
        'opacity',
        'x',
        'y',
        'w',
        'h',
        'display',
        'label' ]
    )):

    def eval_(self, instance):
        msg = self.message
        data = list(self)
        if msg.startswith('lambda'):
            data[1] = eval(msg, locals(), globals())(instance)
        return TextEffectData(*data)

    def setDisplay(self, display=True):
        data = list(self)
        data[8] = display
        return TextEffectData(*data)

class SlateMakerOption(object):
    '''SlateMakerOption as a descriptor, cuz they are awesome'''

    def __init__(self, name, default):
        self.name = re.sub('\s', '', name)
        self.default = default

    def __get__(self, instance, owner):
        if hasattr(instance, '_' + self.name):
            return getattr(instance, '_' + self.name)
        else:
            return self.default

    def __set__(self, instance, value ):
        setattr(instance, '_' + self.name, value)

Resolution = namedtuple('Resolution', ['x', 'y'])

class SlateMaker(object):
    ''' make slate on the timeline '''
    doExpandHandles = SlateMakerOption('doExpandHandles', True)
    maxExpandHandles = SlateMakerOption('maxExpandHandles', 6)
    doMoveUp = SlateMakerOption('doMoveUp', False)
    doMoveOut = SlateMakerOption('doMoveOut', True)
    doMakeLabels = SlateMakerOption('doMakeLabels', True)

    # defaults
    standardResolution = Resolution(2048, 1152)
    defaultOverlayTexts = (
            TextEffectData('ForReview', 'For Review', 50, 0.2, 816, 1060, 362,
                74, True, ''),
            TextEffectData('FrameNumber', 'Frame [metadata input/frame]', 50, 0.2, 1653, 27,
                362, 72, True, ''),
            TextEffectData('ShotName', '[metadata hiero/clip]', 50, 0.2, 15, 20, 971, 72,
                True, ''), )
    defaultSlateTexts = (
            TextEffectData( 'StartHandle',
                'lambda inst: str(inst.trimIn*-1)' , 50, 1.0, 1100,
                90 , 800, 60, True, 'Start Handle:' ),
            TextEffectData( 'EndHandle'  , 'lambda inst: str(inst.trimOut*-1)' , 50, 1.0, 1100,
                222, 800, 60, True, 'End Handle:' ),
            TextEffectData( 'Duration', 
                    'lambda inst: str( inst.vtrackItem.timelineOut()'
                    ' - inst.vtrackItem.timelineIn() + 1)' ,
                    50, 1.0, 1100, 354, 800, 60, True, 'Duration:' ),
            TextEffectData( 'Date'       ,
                "[clock format [clock seconds] -format %d-%m-%y]"
                , 50, 1.0, 1100, 486, 800, 60, True, 'Date:' ),
            TextEffectData( 'Version'    ,
                'lambda inst: inst.vtrackItem.source().name()' , 50,
                1.0, 1100, 618, 800, 60, True, 'Version:' ),
            TextEffectData( 'Shot'       ,
                'lambda inst: inst.vtrackItem.name()' , 50, 1.0,
                1100, 750, 800, 60, True, 'Shot:' ))

    overlayTexts = None
    slateTexts = None
    slate = None

    trimOut = TagData('trimOut', 0)
    trimIn = TagData('trimIn', 0)
    handlesCollapsed = TagData('handlesCollapsed', True)
    move = TagData('move', 0)
    push = TagData('push', 0)

    def __init__(self, vtrackItem, slateClip=None):
        ''' initialize Slate Maker Action'''
        self.setSlateClip(slateClip)
        self.setItem(vtrackItem)

    def setSlateClip(self, slateClip=None):
        if slateClip is None:
            slateClip = SlateMaker.detectSlateClips()[0]
        self.slateClip = slateClip

    def setItem(self, item):
        self.vtrackItem = item
        self.slate = Slate.detectSlate( item )
        self.tag = SlateTag.find( self.vtrackItem )
        self.updateItemTimes()

    def update(self):
        self.moveOut()
        self.moveUp()
        self.updateHandles()
        self.updateSlate()
        self.updateOverlayTexts()
        self.updateSlateTexts()

    def removeSlate(self):
        if self.slate:
            vtrack = self.slate.vtrackItem.parentTrack()
            SlateMaker.removeSubTrackItems(self.slate.vtrackItem)
            SlateMaker.removeSubTrackItems(self.slate.slateItem)
            vtrack.removeItem(self.slate.slateItem)
            self.collapseHandles()
            SlateTag.removeSlateTags(self.slate.vtrackItem)
            self.slate = None
            self.tag = None


    def getRightItems(self, getLinkedItems=False):
        vtrack = self.vtrackItem.parentTrack()
        timelineOut = self.vtrackItem.timelineOut()
        rightItems = [item for item in vtrack.items() if item.timelineIn() >
                timelineOut]
        if getLinkedItems:
            linkedItems = reduce(lambda a, b: a+list(b.linkedItems()),
                    rightItems, [])
            rightItems.extend(linkedItems)
        return rightItems

    def getLeftItems(self, getLinkedItems=False):
        vtrack = self.vtrackItem.parentTrack()
        timelineIn = self.vtrackItem.timelineIn()
        leftItems = [item for item in vtrack.items() if item.timelineOut() <
                timelineIn]
        if getLinkedItems:
            linkedItems = reduce(lambda a, b: a+list(b.linkedItems()),
                    leftItems, [])
            leftItems.extend(linkedItems)
        return leftItems

    def getItemToTheLeft(self):
        nearest = None
        leftItems = self.getLeftItems()
        for item in leftItems:
            if ((not nearest) or nearest.timelineOut() < item.timelineOut):
                nearest = item
        return nearest

    def getItemToTheRight(self):
        nearest = None
        rightItems = self.getRightItems()
        for item in rightItems:
            if ((not nearest) or nearest.timelineIn() > item.timelineIn):
                nearest = item
        return nearest

    def updateItemTimes(self):
        item = self.vtrackItem
        handleInLength = item.handleInLength()
        handleOutLength = item.handleOutLength()
        timelineIn = item.timelineIn()
        timelineOut = item.timelineOut()

        self._push = self._move = 0
        self._moveUp = False

        if self.handlesCollapsed and self.doExpandHandles:

            self._trimIn = -1 * min(handleInLength, self.maxExpandHandles)
            self._trimOut = -1 * min(handleOutLength, self.maxExpandHandles)

            self._move = 0
            slateIn = timelineIn + self._trimIn - 1
            negativeSlate = False
            if slateIn < 0:
                negativeSlate = True
            left = self.getItemToTheLeft()
            if ( left and left.timelineOut() > slateIn ):
                self._move = left.timelineOut() - slateIn + 1
            if negativeSlate:
                self._move += -1 * slateIn

            self._push = 0
            out = timelineOut - self._trimOut
            right = self.getItemToTheRight()
            if ( right and right.timelineIn() < out ):
                self._push = self._move + ( out - right.timelineIn()) + 1

            self._moveOut = False
            self._moveUp = False

            if self.doMoveUp and (left or self._move or self._push):
                self._moveUp = True
                self._move = 0
                if negativeSlate:
                    self._move = -1 * slateIn
                self._push = 0

            if self.doMoveOut:
                self._moveUp = False
                self._moveOut = True
                self._move = 0
                if negativeSlate:
                    self._move = -1 * slateIn
                self._push = 0

    def moveItem(self, push):
        for item in self.vtrackItem.linkedItems():
            item.move(push)
        self.vtrackItem.move(push)

    def trimItem(self, trimIn, trimOut):
        for item in self.vtrackItem.linkedItems():
            item.trimIn(trimIn)
            item.trimOut(trimOut)
        self.vtrackItem.trimIn(trimIn)
        self.vtrackItem.trimOut(trimOut)

    def moveRightItems(self, move):
        rightItems = self.getRightItems(True)
        self.vtrackItem.moveTrackItems(rightItems, move)

    def setSlateItemTime(self, time, slateItem = None):
        '''Set Slate Item Time'''

        if ( not slateItem ) and self.slate:
            slateItem = self.slate.slateItem

        if slateItem:
            moveForward = slateItem.timelineIn() < time
            for item in slateItem.linkedItems():
                if moveForward:
                    item.setTimelineOut(time)
                    item.setTimelineIn(time)
                else:
                    item.setTimelineIn(time)
                    item.setTimelineOut(time)

            if moveForward:
                slateItem.setTimelineOut(time)
                slateItem.setTimelineIn(time)
            else:
                slateItem.setTimelineIn(time)
                slateItem.setTimelineOut(time)

    def expandHandles(self):
        item = self.vtrackItem
        if self.handlesCollapsed:

            self.moveRightItems(self._push)
            self.push = self._push
            self._push = 0

            self.moveItem(self._move)
            self.move = self._move
            self._move = 0

            if self.slate:
                time = item.timelineIn+self._trimIn-1
                self.setSlateItemTime(time)

            self.trimItem(self._trimIn, self._trimOut)
            self.trimIn, self.trimOut = self._trimIn, self._trimOut
            self._trimIn, self._trimOut = 0, 0

            self.handlesCollapsed = False

    def collapseHandles(self):
        '''assume for now slate has already been removed'''
        if not self.handlesCollapsed:

            self.trimItem(self.trimIn*-1, self.trimOut*-1)
            self.trimIn, self.trimOut = 0, 0

            self.moveItem(self.move*-1)
            self.move = 0

            self.moveRightItems(self.push*-1)
            self.push = 0

            self.handlesCollapsed = True
            if self.slate:
                self.updateSlate()

    def moveUp(self):
        if self._moveUp:
            vtrack = self.vtrackItem.parentTrack()
            sequence = vtrack.parent()
            new_track = hcore.VideoTrack(self.vtrackItem.name())
            vtrack.removeItem(self.vtrackItem)
            new_track.addItem(self.vtrackItem)
            self.moveItem(self._move)
            self._move = 0
            sequence.addTrack(new_track)
            self._moveUp = False

    def moveOut(self):
        if self._moveOut:
            self.vtrackItem = self.createTrackItemInNewSequence()

    def createTrackItemInNewSequence(self):
        clip = self.vtrackItem.source()
        position = self.vtrackItem.timelineIn()+self._move

        project = hcore.projects()[-1]
        newSeq = hcore.Sequence(self.vtrackItem.currentVersion().name())
        project.clipsBin().addItem(hcore.BinItem(newSeq))
        newVideoTrack = hcore.VideoTrack(self.vtrackItem.name())
        newSeq.addTrack(newVideoTrack)

        newTrackItem = newVideoTrack.addTrackItem(clip, position)
        newTrackItem.setTimelineIn(self.vtrackItem.timelineIn()+self._move)
        newTrackItem.setSourceIn(self.vtrackItem.sourceIn())
        newTrackItem.setSourceOut(self.vtrackItem.sourceOut())
        newTrackItem.setTimelineOut(self.vtrackItem.timelineOut()+self._move)

        newSeq.setInTime(newTrackItem.timelineIn()+self._trimIn-1)
        newSeq.setOutTime(newTrackItem.timelineOut()-self._trimOut)

        self._move = 0
        return newTrackItem

    def updateHandles(self):
        if self.handlesCollapsed and self.doExpandHandles:
            self.expandHandles()
        elif not (self.handlesCollapsed or self.doExpandHandles):
            self.collapseHandles()

    def evalTexts(self, defaults):
        return [text.eval_(self) for text in defaults if text.display]

    def getSlateTexts(self, reeval=False):
        if self.slateTexts is None or reeval:
            self.slateTexts = self.evalTexts(self.defaultSlateTexts)
        return self.slateTexts

    def getOverlayTexts(self, reeval=False):
        if self.overlayTexts is None or reeval:
            self.overlayTexts = self.evalTexts(self.defaultOverlayTexts)
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
        self.setSlateItemTime(slateTimelineIn, slateItem)
        if not self.slate:
            vtrack.addTrackItem(slateItem)
        self.slate = Slate(self.vtrackItem, slateItem)
        return self.slate

    def updateTexts(self, typ='overlay'):
        textEffects = []
        vtrack = self.vtrackItem.parentTrack()

        overlay = True if typ == 'overlay' else False
        existing = ( self.slate.overlayTexts if overlay else
                self.slate.slateTexts )
        incoming = ( self.getOverlayTexts() if overlay else
                self.getSlateTexts())
        item = self.slate.vtrackItem if overlay else self.slate.slateItem

        idx = 0
        for data in incoming:
            label = None
            if existing.has_key(data.name):
                slateText = existing[data.name]
            else:
                slateText = vtrack.createEffect(trackItem=item,
                    effectType='Text2', subTrackIndex=idx)
                idx += 1
                if data.label.strip() and self.doMakeLabels:
                    label = vtrack.createEffect(trackItem=item,
                            effectType='Text2', subTrackIndex=idx)
                    idx += 1
            SlateMaker.modifyTextEffect( slateText, data, label )
            textEffects.append(slateText)

        return textEffects

    def updateOverlayTexts(self):
        self.updateTexts('overlay')

    def updateSlateTexts(self):
        self.updateTexts('slate')

    @staticmethod
    def modifyTextEffect(text2, data, label=None):
        ''':type data: TextEffectData'''
        text2.setName(data.name)

        seq = text2.sequence()
        format_ = seq.format()
        xRes = format_.width()
        yRes = format_.height()

        node = text2.node()

        scaleX = xRes / float(SlateMaker.standardResolution.x)
        scaleY = yRes / float(SlateMaker.standardResolution.y)
        xPos  = round( data.x * scaleX )
        yDiff = round( scaleY * ( data.y - SlateMaker.standardResolution.y/2 ) )
        yPos  = yRes/2 + yDiff
        font_size = round(data.font_size * scaleX)
        font_size_values = reduce( lambda l,n:l+list(n),
                zip(range(256),[font_size]*256), [])

        node.knob('box').setX(xPos)
        node.knob('box').setY(yPos)
        node.knob('box').setR(xPos+data.w*scaleX)
        node.knob('box').setT(yPos+data.h*scaleY)
        node.knob('message').setValue(data.message)
        node.knob('font_size').setValue(font_size)
        node.knob('opacity').setValue(data.opacity)
        node.knob('font_size_values').resize(len(font_size_values), 1)
        node.knob('font_size_values').setValue(font_size_values)
        node.knob('xjustify').setValue('left')
        node.knob('yjustify').setValue('center')

        if label:
            label.node().knob('message').setValue(data.label)
            label.node().knob('font_size').setValue(font_size)
            label.node().knob('opacity').setValue(data.opacity)
            label.node().knob('font_size_values').resize(len(font_size_values), 1)
            label.node().knob('font_size_values').setValue(font_size_values)
            label.node().knob('xjustify').setValue('right')
            label.node().knob('yjustify').setValue('center')
            label.node().knob('box').setX(xPos - 650 * scaleX)
            label.node().knob('box').setY(yPos)
            label.node().knob('box').setR(xPos - 50  * scaleX)
            label.node().knob('box').setT(yPos + data.h * scaleY)

    @staticmethod
    def detectSlateClips():
        project = hcore.projects()[-1]
        return project.clips(__slateClipKeyword__)

    @staticmethod
    def makeNew(vtrackItem, slateClip=None):
        sm = SlateMaker(vtrackItem, slateClip)
        sm.update()

    @staticmethod
    def removeSubTrackItems(vtrackItem):
        vtrack = vtrackItem.parent()
        for item in vtrackItem.linkedItems():
            vtrack.removeSubTrackItem(item)
        vtrack.addItem(vtrackItem)


    @staticmethod
    def makeSlates(vtrackItems):
        ''' Make Slates using video trackItems '''

        items = sorted(vtrackItems, key=lambda t:t.timelineIn(),
                reverse=True)

        if items:
            items = items[1:] + [ items[0] ]

        for vtrackItem in items:
            if Slate.isSlate(vtrackItem):
                continue

            sm = SlateMaker(vtrackItem)
            sm.readSettings()

            if sm.slate:
                sm.removeSlate()
            else:
                sm.update()

    def readSettings(self):
        settings = SlateMakerSettings()

        self.doMoveOut = settings.doMoveOut
        self.doMoveUp = settings.doMoveUp
        self.doExpandHandles = settings.doExpandHandles
        self.maxExpandHandles = settings.maxExpandHandles
        self.doMakeLabels = settings.doMakeLabels

        self.defaultOverlayTexts = [
                text.setDisplay(settings.displayOverlayTexts.get(text.name,
                    True)) for text in self.defaultOverlayTexts]
        self.defaultSlateTexts = [
                text.setDisplay(settings.displaySlateTexts.get(text.name,
                    True)) for text in self.defaultSlateTexts]

        self.setItem(self.vtrackItem)


    def printItemTimes(self):
        item = self.vtrackItem
        print item.sourceIn(), item.sourceOut(), item.sourceDuration()
        print item.timelineIn(), item.timelineOut(), item.duration()
        print item.handleInLength(), item.handleOutLength()
        print item.handleInTime(), item.handleOutTime()
        print item.source().duration(), item.playbackSpeed()

