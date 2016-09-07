import hiero.core
import hiero.ui

from PySide import QtCore

from .slateProcessor import SlateProcessorPreset


class SlateProcessorUI(hiero.ui.ProcessorUIBase, QtCore.QObject):

    def __init__( self, preset ):
        QtCore.QObject.__init__(self)
        hiero.ui.ProcessorUIBase.__init__(self, preset,
                itemTypes=hiero.core.TaskPresetBase.kSequence)
        hiero.core.log.info(str(preset))

    def createProcessorSettingsWidget( self, exportItems ):
        hiero.core.log.info(str(exportItems))


def registerUI():
    hiero.ui.taskUIRegistry.registerProcessorUI(SlateProcessorPreset,
            SlateProcessorUI)
