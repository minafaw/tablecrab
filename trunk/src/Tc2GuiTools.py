
import Tc2Config
import Tc2GuiHelp

import Tc2GuiToolsFPPCalculator
import Tc2GuiToolsHandHistoryViewer
import Tc2GuiToolsHoldemTrivia
import Tc2GuiToolsFlopEval
import Tc2GuiToolsFlopster
import Tc2GuiToolsPokerStarsIniDecrypter

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameTools(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'
	SettingsKeyCurrentToolIndex = SettingsKeyBase + '/CurrentIndex'

	ToolClasses = (
			Tc2GuiToolsFPPCalculator.FrameTool,
			Tc2GuiToolsHandHistoryViewer.FrameTool,
			Tc2GuiToolsHoldemTrivia.FrameTool,
			Tc2GuiToolsFlopEval.FrameTool,
			Tc2GuiToolsFlopster.FrameTool,
			 Tc2GuiToolsPokerStarsIniDecrypter.FrameTool,
			)


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.toolCombo = QtGui.QComboBox(self)
		self.toolCombo.currentIndexChanged.connect(self.onToolSelected)
		self.stack = QtGui.QStackedWidget(self)
		for toolClass in self.ToolClasses:
			self.addTool(toolClass(parent=self.stack) )

		#
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.toolCombo)
		grid.row()
		grid.col(self.stack)

	def addTool(self, tool):
		self.toolCombo.addItem(tool.displayName())
		self.stack.addWidget(tool)
		return tool

	def onToolSelected(self, i):
		self.stack.setCurrentIndex(i)
		tool = self.stack.currentWidget()
		tool.handleSetCurrent()

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeyCurrentToolIndex, self.stack.currentIndex())

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		self.toolCombo.setCurrentIndex( Tc2Config.settingsValue(self.SettingsKeyCurrentToolIndex, 0).toInt()[0] )


