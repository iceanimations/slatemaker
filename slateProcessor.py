import hiero.core


class SlateProcessor(hiero.core.ProcessorBase):

    def __init__(self, preset, submission=None, synchronous=False):
        hiero.core.ProcessorBase.__init__(self, preset, submission,
                synchronous)
        hiero.core.log.info(str(preset))
        hiero.core.log.info(str(submission))
        hiero.core.log.info(str(synchronous))

    def startProcessing(self, exportItems):
        hiero.core.log.info(str(exportItems))


class SlateProcessorPreset(hiero.core.ProcessorPreset):

    def __init__(self, name, properties):
        hiero.core.ProcessorPreset.__init__(self, SlateProcessor, name)

        hiero.core.log.info(str(properties))
        hiero.core.log.info(str(name))

        # setup defaults
        self.properties().update(properties)

        # This remaps the project root if os path remapping has been set up in the preferences
        self.properties()["exportRoot"] = hiero.core.remapPath (self.properties()["exportRoot"])

    def addCustomResolveEntries(self, resolver):
        hiero.core.log.info(str(resolver))
        pass


def register():
    hiero.core.taskRegistry.registerProcessor( SlateProcessorPreset,
            SlateProcessor)
