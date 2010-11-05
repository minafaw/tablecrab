
#TODO: i kind of dislike in-place editing of template names. an "Edit" button would be more consistent but a bit of overkill right now. then .again .screenshot
# 			open / save is taking away screenspace already. would have to find shorter names for these actions.

import Tc2Config
import Tc2GuiHelp
import Tc2GuiTemplates
import Tc2GuiScreenshots

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSetup(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Setup'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.grid = Tc2Config.GridBox(self)

		self.templatesWidget = Tc2GuiTemplates.TemplatesWidget(parent=self)
		self.screenshotWidget = Tc2GuiScreenshots.ScreenshotWidget(parent=self)

		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self.splitter.addWidget(self.templatesWidget)
		self.splitter.addWidget(self.screenshotWidget)

		self.toolBar = QtGui.QToolBar(self)
		for action in self.templatesWidget.actions():
			self.toolBar.addAction(action)
		self.toolBar.addSeparator()
		self.toolBar.addSeparator()
		for action in self.screenshotWidget.actions():
			self.toolBar.addAction(action)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self.toolBar.addAction(self.actionHelp)

		Tc2Config.globalObject.init.connect(self.onInit)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		Tc2Config.globalObject.settingToolBarPositionChanged.connect(self.onSettingToolBarPositionChanged)

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def layout(self):
		toolBarPositionBottom = Tc2Config.settingsValue(Tc2Config.SettingsKeyToolBarPosition, Tc2Config.ToolBarPositionTop).toString() == Tc2Config.ToolBarPositionBottom
		grid = self.grid
		if not toolBarPositionBottom:
			grid.col(self.toolBar)
			grid.row()
		grid.col(self.splitter)
		if toolBarPositionBottom:
			grid.row()
			grid.col(self.toolBar)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self):
		Tc2GuiHelp.dialogHelp('setup', parent=self)

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState())

	def onInit(self):
		self.layout()
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )

	def onSettingToolBarPositionChanged(self, position):
		self.grid.clear()
		self.layout()

