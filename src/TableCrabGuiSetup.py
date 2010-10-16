
#TODO: would be nice to have some information on how many templates are left until hitting MaxTemplates
#TODO: i kind of dislike in-place editing of template names. an "Edit" button would be more consistent but a bit of overkill right now. then .again .screenshot
# 			open / save is taking away screenspace already. would have to find shorter names for these actions.
#TODO: restore last selected template on restart?

import TableCrabConfig
import TableCrabGuiHelp
import TableCrabGuiTemplates
import TableCrabGuiScreenshots

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
class FrameSetup(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.templatesWidget = TableCrabGuiTemplates.TemplatesWidget(parent=self)
		self.screenshotWidget = TableCrabGuiScreenshots.ScreenshotWidget(parent=self)

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

		TableCrabConfig.globalObject.init.connect(self.onInit)
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)

		self.layout()

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.splitter)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self):
		TableCrabGuiHelp.dialogHelp('setup', parent=self)

	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Setup/SplitterState', self.splitter.saveState())

	def onInit(self):
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Setup/SplitterState', QtCore.QByteArray()).toByteArray() )

