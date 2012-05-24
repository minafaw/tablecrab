
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

		self.listWidget = QtGui.QListWidget(self)
		self.listWidget.itemSelectionChanged.connect(self.onToolSelected)

		self.stack = QtGui.QStackedWidget(self)

		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.listWidget)
		self.splitter.addWidget(self.stack)

		for toolClass in self.ToolClasses:
			self.addTool(toolClass(parent=self.stack) )

		#
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.splitter)

	def addTool(self, tool):
		item = QtGui.QListWidgetItem(tool.displayName(), self.listWidget)
		item.setToolTip(tool.toolTip())
		self.listWidget.addItem(item)
		self.stack.addWidget(tool)
		item.setData(QtCore.Qt.UserRole, QtCore.QVariant(self.stack.count() -1) )
		return tool

	def onToolSelected(self):
		row = self.listWidget.currentRow()
		if row < 0:
			row = 0
		item = self.listWidget.item(row)
		index, ok = item.data(QtCore.Qt.UserRole).toInt()
		if ok:
			self.stack.setCurrentIndex(row)
			tool = self.stack.currentWidget()
			tool.handleSetCurrent()

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState())
		Tc2Config.settingsSetValue(self.SettingsKeyCurrentToolIndex, self.stack.currentIndex())

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		self.listWidget.setCurrentRow( Tc2Config.settingsValue(self.SettingsKeyCurrentToolIndex, 0).toInt()[0] )
		self.listWidget.setAlternatingRowColors(globalObject.settingsGlobal.alternatingRowColors())
		globalObject.settingsGlobal.alternatingRowColorsChanged.connect(self.listWidget.setAlternatingRowColors)

