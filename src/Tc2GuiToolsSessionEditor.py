
import Tc2Config
import Tc2GuiHelp
from Tc2Lib import GuiSessionEditor

from PyQt4 import QtCore, QtGui
#***********************************************************************************
#
#***********************************************************************************
class FrameTool(GuiSessionEditor.FrameSessionEditor):

	SettingsKeyBase = 'Gui/Tools/SessionEditor'
	SettingsKeyCurrency = SettingsKeyBase + '/Curreny'
	SettingsKeyDlgOpenFileNameState = SettingsKeyBase + '/DlgOpenFileNameState'
	SettingsKeyDlgHelpGeometry = SettingsKeyBase + '/DlgHelpGeometry'
	SettingsKeyFileName = SettingsKeyBase + '/FileName'
	SettingsKeySessionStates = SettingsKeyBase + '/SessionStates'
	SettingsKeySessionTypesHeaderState = SettingsKeyBase + '/SessionTypesHeaderState'
	SettingsKeySplitterVState = SettingsKeyBase + '/SplitterVState'
	SettingsKeySplitterHState = SettingsKeyBase + '/SplitterHState'

	def __init__(self, parent=None):
		GuiSessionEditor.FrameSessionEditor.__init__(self, parent=parent, backupSessionsFile=False)

		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		self.restoreSettings(Tc2Config.settings())
		self.handleFontChanged(globalObject.settingsGlobal.guiFont())
		globalObject.settingsGlobal.guiFontChanged.connect(self.handleFontChanged)

	def onCloseEvent(self, event):
		self.saveSettings()

	def onHelp(self):
		Tc2GuiHelp.dialogHelp('toolsSessionEditor', parent=self)

	def toolTip(self):
		return 'Session editor'

	def displayName(self):
		return 'Session editor'

	def handleSetCurrent(self):
		pass


