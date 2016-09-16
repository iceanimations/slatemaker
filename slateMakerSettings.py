import PySide.QtCore as core
import json

class Setting(object):
    def __init__(self, keystring, default):
        self.keystring = keystring
        self.default = json.dumps(default)

    def __get__(self, instance, owner):
        return json.loads(instance.value(self.keystring, self.default))

    def __set__(self, instance, value):
        instance.setValue(self.keystring, json.dumps(value))

class SlateMakerSettings(core.QSettings):
    ''' Class for accessing all Settings of the slateMaker'''

    doMoveOut = Setting('doMoveOut', True)
    doMoveUp = Setting('doMoveUp', False)
    displayOverlayTexts = Setting('displayOverlayTexts', {})
    displaySlateTexts = Setting('displaySlateTexts', {})
    doExpandHandles = Setting('doExpandHandles', True)
    maxExpandHandles = Setting('maxExpandHandles', 6)
    overlayTexts = Setting('overlayTexts', ())
    slateTexts = Setting('slateTexts', ())
    doMakeLabels = Setting('doMakeLabels', True)

    def __init__(self, organization='ICE Animations', product='SlateMaker'):
        super(SlateMakerSettings, self).__init__(organization, product)

