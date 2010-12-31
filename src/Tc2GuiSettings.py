
#TODO: accelerators for settings "Hand Style Sheet"
#TODO: tooltips flapping out on settings selector pane are ugly. no way to set tooltip delay in Qt4
#			so we may have to reimplement tool tips
#TODO: would be nice to have line numbers in HandCss editor

import Tc2Config
import Tc2GuiSettingsGlobal
import Tc2GuiSettingsNetwork
import Tc2GuiSettingsPokerStars
import Tc2GuiSettingsHandViewer
import Tc2GuiSettingsHandViewerStyleSheet
import Tc2GuiSettingsNashCalculationsStyleSheet
import Tc2GuiSettingsClock
import Tc2GuiSettingsCardProtector

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Settings'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'
	SettingsKeyCurrentSettingIndex = SettingsKeyBase + '/CurrentIndex'


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.listWidget = QtGui.QListWidget(self)
		self.listWidget.itemSelectionChanged.connect(self.onSettingSelected)

		self.stack = QtGui.QStackedWidget(self)

		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.listWidget)
		self.splitter.addWidget(self.stack)

		#
		self.settingsGlobal = self.addSetting('Global', Tc2GuiSettingsGlobal.FrameSettings(parent=self.stack), 'Shift+G', 'Global (Shift+G)')
		self.settingsNetwork = self.addSetting('Network', Tc2GuiSettingsNetwork.FrameSettings(parent=self.stack), 'Shift+G', 'Global (Shift+N)')
		self.settingsPokerStars = self.addSetting('PokerStars', Tc2GuiSettingsPokerStars.FrameSettings(parent=self.stack), 'Shift+P', 'PokerStars (Shift+P)')
		self.settingsHand = self.addSetting('HandViewer', Tc2GuiSettingsHandViewer.FrameSettings(parent=self.stack), 'Shift+H', 'Hand viewer (Shift+H)')
		self.settingsHandStyleSheet = self.addSetting('HandViewerStyleSheet', Tc2GuiSettingsHandViewerStyleSheet.FrameSettings(parent=self.stack), 'Shift+S', 'Hand viewer style sheet (Shift+S)')
		self.settingsNashCalculationsStyleSheet = self.addSetting('NashCalculationsStyleSheet', Tc2GuiSettingsNashCalculationsStyleSheet.FrameSettings(parent=self.stack), 'Shift+S', 'Nash calculations style sheet (Shift+C)')
		self.settingsCardProtector = self.addSetting('CardProtector', Tc2GuiSettingsCardProtector.FrameSettings(parent=self.stack), 'Shift+A', 'Card Protector (Shift+A)')
		self.settingsClock = self.addSetting('Clock', Tc2GuiSettingsClock.FrameSettings(parent=self.stack), 'Shift+C', 'Clock (Shift+C)')

		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)

	def layout(self):
		grid = Tc2Config.GridBox(self)
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
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState())
		Tc2Config.settingsSetValue(self.SettingsKeyCurrentSettingIndex, self.stack.currentIndex())

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		self.listWidget.setCurrentRow( Tc2Config.settingsValue(self.SettingsKeyCurrentSettingIndex, 0).toInt()[0] )

		self.listWidget.setAlternatingRowColors(globalObject.settingsGlobal.alternatingRowColors())
		globalObject.settingsGlobal.alternatingRowColorsChanged.connect(self.listWidget.setAlternatingRowColors)



