
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
import Tc2GuiSettingsICMTaxStyleSheet
import Tc2GuiSettingsClock
import Tc2GuiSettingsCardProtector

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	settingSplitterState = Tc2Config.settings2.ByteArray(
			'Gui/Settings/SplitterState',
			defaultValue=QtCore.QByteArray(),
			)
	settingCurrentIndex = Tc2Config.settings2.Index(
			'Gui/Settings/CurrentIndex',
			defaultValue=0,
			)

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self._listWidget = QtGui.QListWidget(self)
		self._listWidget.itemSelectionChanged.connect(self.onSettingSelected)

		self._stack = QtGui.QStackedWidget(self)

		self._splitter = QtGui.QSplitter(self)
		self._splitter.addWidget(self._listWidget)
		self._splitter.addWidget(self._stack)

		#
		self.settingsGlobal = self.addSetting('Global', Tc2GuiSettingsGlobal.FrameSettings(parent=self._stack), 'Shift+G', 'Global (Shift+G)')
		self.settingsNetwork = self.addSetting('Network', Tc2GuiSettingsNetwork.FrameSettings(parent=self._stack), 'Shift+G', 'Global (Shift+N)')
		self.settingsPokerStars = self.addSetting('PokerStars', Tc2GuiSettingsPokerStars.FrameSettings(parent=self._stack), 'Shift+P', 'PokerStars (Shift+P)')
		self.settingsHand = self.addSetting('HandViewer', Tc2GuiSettingsHandViewer.FrameSettings(parent=self._stack), 'Shift+H', 'Hand viewer (Shift+H)')
		self.settingsHandStyleSheet = self.addSetting('HandViewerStyleSheet', Tc2GuiSettingsHandViewerStyleSheet.FrameSettings(parent=self._stack), 'Shift+S', 'Hand viewer style sheet (Shift+S)')
		self.settingsNashCalculationsStyleSheet = self.addSetting('NashCalculationsStyleSheet', Tc2GuiSettingsNashCalculationsStyleSheet.FrameSettings(parent=self._stack), 'Shift+S', 'Nash calculations style sheet (Shift+C)')
		self.settingsICMTaxStyleSheet = self.addSetting('NashICMTaxStyleSheet', Tc2GuiSettingsICMTaxStyleSheet.FrameSettings(parent=self._stack), 'Shift+S', 'Nash calculations style sheet (Shift+C)')
		self.settingsCardProtector = self.addSetting('CardProtector', Tc2GuiSettingsCardProtector.FrameSettings(parent=self._stack), 'Shift+A', 'Card Protector (Shift+A)')
		self.settingsClock = self.addSetting('Clock', Tc2GuiSettingsClock.FrameSettings(parent=self._stack), 'Shift+C', 'Clock (Shift+C)')

		Tc2Config.globalObject.initGui.connect(self.onInitGui)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		Tc2Config.settings2['Gui/AlternatingRowColors'].changed.connect(
				lambda setting:self._listWidget.setAlternatingRowColors(setting.value())
				)


	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self._splitter)

	def addSetting(self, name, widget, shortcut, toolTip):
		item = QtGui.QListWidgetItem(name, self._listWidget)
		item.setToolTip(toolTip)
		self._listWidget.addItem(item)
		self._stack.addWidget(widget)
		action = QtGui.QAction(self)
		action.setData(QtCore.QVariant(self._listWidget.count() -1) )
		action.setShortcut(shortcut)
		action.triggered.connect(self.onSettingsShortcut)
		self.addAction(action)
		return widget

	def onSettingsShortcut(self):
		index = self.sender().data().toInt()[0]
		self._listWidget.setCurrentRow(index)
		self.onSettingSelected()

	def onSettingSelected(self):
		row = self._listWidget.currentRow()
		if row < 0:
			row = 0
		self._stack.setCurrentIndex(row)

	def onCloseEvent(self, event):
		self.settingSplitterState.setValue(self._splitter.saveState())

	def onInitGui(self):
		self.settingSplitterState.changed.connect(
				lambda setting: self._splitter.restoreState(setting.value())
				)
		self.settingCurrentIndex.setListWidget(self._listWidget)
		self.layout()

