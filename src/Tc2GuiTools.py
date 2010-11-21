
import Tc2Config
import Tc2GuiHelp

import Tc2GuiToolsFPPCalculator
import Tc2GuiToolsHandHistoryViewer

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameTools(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'
	SettingsKeyCurrentToolIndex = SettingsKeyBase + '/CurrentIndex'


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.listWidget = QtGui.QListWidget(self)
		self.listWidget.itemSelectionChanged.connect(self.onToolSelected)

		self.stack = QtGui.QStackedWidget(self)

		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.listWidget)
		self.splitter.addWidget(self.stack)

		self.addTool(Tc2GuiToolsFPPCalculator.FrameTool(parent=self.stack), self.listWidget)
		self.addTool(Tc2GuiToolsHandHistoryViewer.FrameTool(parent=self.stack), self.listWidget)


		#
		Tc2Config.globalObject.init.connect(self.onInit)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		Tc2Config.globalObject.settingAlternatingRowColorsChanged.connect(self.onSettingAlternatingRowColorsChanged)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.splitter)

	def addTool(self, widget, parent):
		item = QtGui.QListWidgetItem(widget.toolName(), parent)
		item.setToolTip(widget.toolTip())
		self.listWidget.addItem(item)
		self.stack.addWidget(widget)
		item.setData(QtCore.Qt.UserRole, QtCore.QVariant(self.stack.count() -1) )
		return widget

	def onToolSelected(self):
		row = self.listWidget.currentRow()
		if row < 0:
			row = 0
		item = self.listWidget.item(row)
		index, ok = item.data(QtCore.Qt.UserRole).toInt()
		if ok:
			self.stack.setCurrentIndex(row)

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState())
		Tc2Config.settingsSetValue(self.SettingsKeyCurrentToolIndex, self.stack.currentIndex())

	def onInit(self):
		self.layout()
		self.listWidget.setAlternatingRowColors( Tc2Config.settingsValue(Tc2Config.SettingsKeyAlternatingRowColors, False).toBool() )
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		self.listWidget.setCurrentRow( Tc2Config.settingsValue(self.SettingsKeyCurrentToolIndex, 0).toInt()[0] )

	def onSettingAlternatingRowColorsChanged(self, flag):
		self.listWidget.setAlternatingRowColors(flag)

