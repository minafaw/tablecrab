
#TODO: accelerators for settings "Hand Style Sheet"
#TODO: tooltips flapping out on settings selector pane are ugly. no way to set tooltip delay in Qt4
#			so we may have to reimplement tool tips
#TODO: would be nice to have line numbers in HandCss editor

import TableCrabConfig
import TableCrabGuiSettingsGlobal
import TableCrabGuiSettingsPokerStars
import TableCrabGuiSettingsHandViewer
import TableCrabGuiSettingsHandViewerStyleSheet

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.listWidget = QtGui.QListWidget(self)
		self.listWidget.itemSelectionChanged.connect(self.onSettingSelected)

		self.stack = QtGui.QStackedWidget(self)

		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.listWidget)
		self.splitter.addWidget(self.stack)

		#
		self.settingsGlobal = self.addSetting('Global', TableCrabGuiSettingsGlobal.FrameSettings(parent=self.stack), 'Shift+G', 'Global (Shift+G)')
		self.settingsPokerStars = self.addSetting('PokerStars', TableCrabGuiSettingsPokerStars.FrameSettings(parent=self.stack), 'Shift+P', 'PokerStars (Shift+P)')
		self.settingsHand = self.addSetting('Hand Viewer', TableCrabGuiSettingsHandViewer.FrameSettings(parent=self.stack), 'Shift+H', 'Hand Viewer (Shift+H)')
		self.settingsHandStyleSheet = self.addSetting('Hand Viewer Style Sheet', TableCrabGuiSettingsHandViewerStyleSheet.FrameSettings(parent=self.stack), 'Shift+S', 'Hand Viewer Style Sheet (Shift+S)')

		TableCrabConfig.globalObject.init.connect(self.onInit)
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSettingAlternatingRowColorsChanged)

		self.layout()

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.splitter)

	def addSetting(self, name, widget, shortcut, toolTip):
		item = QtGui.QListWidgetItem(name, self.listWidget)
		item.setToolTip(toolTip)
		self.listWidget.addItem(item)
		self.stack.addWidget(widget)
		action = QtGui.QAction(self)
		action.setData(QtCore.QVariant(self.listWidget.count() -1) )
		action.setShortcut(shortcut)
		action.triggered.connect(self.onSettingsShortcut)
		self.addAction(action)
		return widget

	def onSettingsShortcut(self):
		index = self.sender().data().toInt()[0]
		self.listWidget.setCurrentRow(index)
		self.onSettingSelected()

	def onSettingSelected(self):
		row = self.listWidget.currentRow()
		if row < 0:
			row = 0
		self.stack.setCurrentIndex(row)

	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Settings/SplitterState', self.splitter.saveState())
		TableCrabConfig.settingsSetValue('Gui/Settings/CurrentIndex', self.stack.currentIndex())

	def onInit(self):
		self.listWidget.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Settings/SplitterState', QtCore.QByteArray()).toByteArray() )
		self.listWidget.setCurrentRow( TableCrabConfig.settingsValue('Gui/Settings/CurrentIndex', 0).toInt()[0] )

	def onSettingAlternatingRowColorsChanged(self, flag):
		self.listWidget.setAlternatingRowColors(flag)



