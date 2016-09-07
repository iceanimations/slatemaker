from . import slateMakerAction
reload(slateMakerAction)

from slateMakerAction import ActionHandler
sm = ActionHandler()
sm.register()

# import slateProcessor, slateProcessorUI

# reload(slateProcessor)
# reload(slateProcessorUI)

# slateProcessor.register()
# slateProcessorUI.registerUI()

