
import Tc2Config
import Tc2GuiHelp
from Tc2Lib import FlopEvalWidget
#************************************************************************************
#
#************************************************************************************

class FrameTool(FlopEvalWidget.FlopEvalWidget):
	
	def __init__(self, parent=None):
		FlopEvalWidget.FlopEvalWidget.__init__(self, parent)
		
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
	
	def toolTip(self):
		return 'FlopEvaluator'

	def displayName(self):
		return 'FlopEvaluator'

	def handleSetCurrent(self):
		pass
		
	def onGlobalObjectInitSettingsFinished(self, globalObject):
		#TODO: find better placeto init our widgets?
		self.handleFontChanged()
		globalObject.settingsGlobal.guiFontChanged.connect(self.handleFontChanged)
		
