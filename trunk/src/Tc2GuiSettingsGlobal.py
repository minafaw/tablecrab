
import Tc2Config
import Tc2Win32
import Tc2GuiHelp
from Tc2Lib import FontButton
from Tc2Lib import ComboBox
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Settings'
	SettingsKeyDialogBackupState = SettingsKeyBase + '/DialogBackup/State'
	SettingsKeyGuiStyle = 'Gui/Style'
	SettingsKeyGuiFont = 'Gui/Font'
	SettingsKeyFontFixed = 'Gui/FontFixed'
	SettingsKeyWebViewZoomSteps = 'Gui/WebView/ZoomSteps'
	SettingsKeyAlternatingRowColors = 'Gui/AlternatingRowColors'
	SettingsKeyChildItemIndicators = 'Gui/ChildItemIndicators'
	SettingsKeyRestoreMousePosition = 'RestoreMousePosition'
	SettingsKeyToolBarPosition = 'Gui/ToolBar/Position'
	SettingsKeyTabPosition = 'Gui/Tab/Position'
	SettingsKeyRoundBets = 'Settings/RoundBets'

	guiStyleChanged = QtCore.pyqtSignal(QtCore.QString)
	guiFontChanged = QtCore.pyqtSignal(QtGui.QFont)
	fixedFontChanged = QtCore.pyqtSignal(QtGui.QFont)
	singleApplicationScopeChanged = QtCore.pyqtSignal(QtCore.QString)
	webViewZoomStepsChanged = QtCore.pyqtSignal(int)
	alternatingRowColorsChanged = QtCore.pyqtSignal(bool)
	childItemIndicatorsChanged = QtCore.pyqtSignal(bool)
	restoreMousePositionChanged = QtCore.pyqtSignal(bool)
	toolBarPositionChanged = QtCore.pyqtSignal(QtCore.QString)
	tabPositionChanged = QtCore.pyqtSignal(QtCore.QString)
	roundBetsChanged = QtCore.pyqtSignal(QtCore.QString)


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.buttonBackup = QtGui.QPushButton('..', self)
		self.buttonBackup.clicked.connect(self.onButtonBackupClicked)
		self.labelBackup = QtGui.QLabel('&Backup TableCrab:', self)
		self.labelBackup.setBuddy(self.buttonBackup)

		self.groupGuiStyle = ComboBox.GroupComboBox(
				parent=self,
				defaultValue=QtGui.qApp.style().objectName(), 	# undocumented but works
				values=QtCore.QStringList(QtGui.QStyleFactory().keys()),
				text='Global &Style:'
				)
		self.groupGuiFont = FontButton.GroupFontButton(
				parent=self,
				defaultFont=QtGui.qApp.font(),
				text='Global &Font:',
				toolTip='Select gui font'
				)

		settings = QtWebKit.QWebSettings.globalSettings()
		font = QtGui.QFont(settings.fontFamily(settings.FixedFont), settings.fontSize(settings.DefaultFixedFontSize))
		self.groupFixedFont = FontButton.GroupFontButton(
				parent=self,
				defaultFont=font,
				text='Fi&xed Font:',
				toolTip='Select fixed font'
				)

		self.groupSingleApplicationScope = ComboBox.GroupComboBox(
				parent=self,
				defaultValue=Tc2Config.SingleApplicationScopeDefault,
				values=QtCore.QStringList(Tc2Win32.SingleApplication.Scopes),
				text='Single a&pplication scope:'
				)

		self.spinWebViewZoomSteps = QtGui.QSpinBox(self)
		self.spinWebViewZoomSteps.setRange(Tc2Config.WebViewZoomStepsMin, Tc2Config.WebViewZoomStepsMax)
		self.labelWebViewZoomSteps = QtGui.QLabel('&Zoom Steps (%s max):' % Tc2Config.WebViewZoomStepsMax, self)
		self.labelWebViewZoomSteps.setBuddy(self.spinWebViewZoomSteps)

		self.checkAlternatingRowColors = QtGui.QCheckBox('Alternating &Row Colors', self)
		self.checkChildItemIndicators = QtGui.QCheckBox('&Child Item Indicators', self)
		self.checkRestoreMousePosition = QtGui.QCheckBox('Restore Mouse &Position', self)

		self.comboToolBarPosition = QtGui.QComboBox(self)
		self.comboToolBarPosition.addItems(Tc2Config.ToolBarPositions)
		self.labelToolBarPosition = QtGui.QLabel('T&ool bar position:', self)
		self.labelToolBarPosition.setBuddy(self.comboToolBarPosition)

		self.comboTabPosition = QtGui.QComboBox(self)
		self.comboTabPosition.addItems(Tc2Config.TabPositions)
		self.labelTabPosition = QtGui.QLabel('&Tab position:', self)
		self.labelTabPosition.setBuddy(self.comboTabPosition)

		self.comboRoundBets = QtGui.QComboBox(self)
		self.comboRoundBets.addItems(Tc2Config.RoundBets)
		self.labelRoundBets = QtGui.QLabel('Round &bets to:', self)
		self.labelRoundBets.setBuddy(self.comboRoundBets)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)
		self.addAction(action)

		Tc2Config.globalObject.initSettings.connect(self.onInitSettings)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelBackup).col(self.buttonBackup).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.groupGuiStyle.label() ).col(self.groupGuiStyle.comboBox() ).col(self.groupGuiStyle.resetButton() )
		grid.row()
		grid.col(self.groupGuiFont.label() ).col(self.groupGuiFont.fontButton() ).col(self.groupGuiFont.resetButton() )
		grid.row()
		grid.col(self.groupFixedFont.label() ).col(self.groupFixedFont.fontButton() ).col(self.groupFixedFont.resetButton() )
		grid.row()
		grid.col(self.groupSingleApplicationScope.label() ).col(self.groupSingleApplicationScope.comboBox() ).col(self.groupSingleApplicationScope.resetButton() )
		grid.row()
		grid.col(self.labelTabPosition).col(self.comboTabPosition).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelToolBarPosition).col(self.comboToolBarPosition).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelWebViewZoomSteps).col(self.spinWebViewZoomSteps).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.checkAlternatingRowColors)
		grid.row()
		grid.col(self.checkChildItemIndicators)
		grid.row()
		grid.col(self.checkRestoreMousePosition)
		grid.row()
		grid.col(self.labelRoundBets).col(self.comboRoundBets).col(Tc2Config.HStretch())
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def setFixedFont(self):
		font = QtGui.QFont()
		settings = QtWebKit.QWebSettings.globalSettings()
		# try to read QWebKit FixedFont from config, if not take it from QWebKit FixedFont
		if font.fromString(Tc2Config.settingsValue(Tc2Config.SettingsKeyFontFixed, '').toString() ):
			settings.setFontFamily(settings.FixedFont, font.family() )
			settings.setFontSize(settings.DefaultFixedFontSize, font.pointSize() )
		else:
			font.setFamily( settings.fontFamily(settings.FixedFont) )
			font.setPointSize( settings.fontSize(settings.DefaultFixedFontSize) )
		self.buttonFixedFont.setText( QtCore.QString('%1 %2').arg(font.family()).arg(font.pointSize()) )

	def onButtonBackupClicked(self, checked):
		dlg = QtGui.QFileDialog(self)
		dlg.setWindowTitle('Backup tableCrab To Config File..')
		dlg.setFileMode(dlg.AnyFile)
		dlg.setAcceptMode(dlg.AcceptSave)
		dlg.setConfirmOverwrite(True)
		filters = QtCore.QStringList()
		filters << 'Config Files (*.ini *.cfg)'
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( Tc2Config.settingsValue(self.SettingsKeyDialogBackupState, QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		Tc2Config.settingsSetValue(self.SettingsKeyDialogBackupState, dlg.saveState() )
		if result != dlg.Accepted:
			return

		fileName = dlg.selectedFiles()[0]
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		# default save format to to ".ini"
		if not format:
			fileName = fileName + '.ini'

		#NOTE: looks like Qt is only checking for write protect anything else may or may not pass ..and we don't get any IO errors
		# 		 so we try in advance. obv there are still loopholes
		fp = None
		try: fp = open(fileName, 'w').close()
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Open Config File\n\n%s' % d)
			return
		finally:
			if fp is not None: fp.close()

		newSettings = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
		if not newSettings.isWritable():
			Tc2Config.msgWarning(self, 'Config File Is Not Writable')
			return
		settings = Tc2Config.settings()
		for key in settings.allKeys():
			newSettings.setValue(key, settings.value(key) )

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsGlobal', parent=self)

	def guiStyle(self):
		return self.groupGuiStyle.style()

	def setGuiStyle(self, value):
		style = QtGui.QStyleFactory.create(value)
		#TODO: we currently set no palette. QStyle docs say palette should not be set
		# for styles that use system defaults, but there seems to be no way to find out
		# so ..and where to find some kind of default palette.
		##QtGui.qApp.setPalette(style.standardPalette())
		QtGui.qApp.setStyle(style)
		Tc2Config.settingsSetValue(self.SettingsKeyGuiStyle, value)
		self.guiStyleChanged.emit(value)

	def guiFont(self):
		return QtGui.qApp.font()

	def setGuiFont(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyGuiFont, value.toString())
		QtGui.qApp.setFont(value)
		#NOTE: have to re-set style to make font changes work as expected
		self.setGuiStyle(self.guiStyle())
		# take QWebKit StandardFont from application font
		settings = QtWebKit.QWebSettings.globalSettings()
		settings.setFontFamily(settings.StandardFont, value.family() )
		settings.setFontSize(settings.DefaultFontSize, value.pointSize() )
		self.guiFontChanged.emit(value)

	def fixedFont(self):
		font = QtGui.QFont()
		# take fixed font from QWebKit
		settings = QtWebKit.QWebSettings.globalSettings()
		family = settings.fontFamily(settings.FixedFont)
		pointSize = settings.fontSize(settings.DefaultFixedFontSize)
		font.setFamily(family)
		font.setPointSize(pointSize)
		return font

	def setFixedFont(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyFontFixed, value.toString())
		# sdjust WeKit fixed font here
		settings = QtWebKit.QWebSettings.globalSettings()
		settings.setFontFamily(settings.FixedFont, value.family() )
		settings.setFontSize(settings.DefaultFixedFontSize, value.pointSize() )
		self.fixedFontChanged.emit(value)

	def singleApplicationScope(self):
		return self.groupSingleApplicationScope.value()

	def setSingleApplicationScope(self, value):
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeySingleApplicationScope, value)
		self.singleApplicationScopeChanged.emit(value)

	def webViewZoomSteps(self):
		return self.spinWebViewZoomSteps.value()

	def setWebViewZoomSteps(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyWebViewZoomSteps, value)
		self.webViewZoomStepsChanged.emit(value)

	def alternatingRowColors(self):
		return self.checkAlternatingRowColors.checkState() == QtCore.Qt.Checked

	def setAlternatingRowColors(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyAlternatingRowColors, value)
		self.alternatingRowColorsChanged.emit(value)

	def childItemIndicators(self):
		return self.checkChildItemIndicators.checkState() == QtCore.Qt.Checked

	def setChildItemIndicators(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyChildItemIndicators, value)
		self.childItemIndicatorsChanged.emit(value)

	def restoreMousePosition(self):
		return self.checkRestoreMousePosition.checkState() == QtCore.Qt.Checked

	def setRestoreMousePosition(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyRestoreMousePosition, value)
		self.restoreMousePositionChanged.emit(value)

	def toolBarPosition(self):
		return self.comboToolBarPosition.currentText()

	def setToolBarPosition(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyToolBarPosition, value)
		self.toolBarPositionChanged.emit(value)

	def tabPosition(self):
		return self.comboTabPosition.currentText()

	def setTabPosition(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyTabPosition, value)
		self.tabPositionChanged.emit(value)

	def roundBets(self):
		return self.comboRoundBets.currentText()

	def setRoundBets(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyRoundBets, value)
		self.roundBetsChanged.emit(value)

	def onInitSettings(self):
		self.layout()

		# have to set font ahead of style to make it work as expected
		value = QtGui.QFont()
		if value.fromString( Tc2Config.settingsValue(self.SettingsKeyGuiFont, '').toString() ):
			QtGui.qApp.setFont(value)
		else:
			value = QtGui.qApp.font()
		self.groupGuiFont.setFont(value)
		self.groupGuiFont.fontChanged.connect(self.setGuiFont)

		value = Tc2Config.settingsValue(self.SettingsKeyGuiStyle, '').toString()
		self.groupGuiStyle.valueChanged.connect(self.setGuiStyle)
		self.groupGuiStyle.setValue(value)

		value = QtGui.QFont()
		if value.fromString(Tc2Config.settingsValue(self.SettingsKeyFontFixed, '').toString() ):
			self.setFixedFont(value)
			self.groupFixedFont.setFont(value)
		self.groupFixedFont.fontChanged.connect(self.setFixedFont)

		value = Tc2Config.settingsValue(Tc2Config.SettingsKeySingleApplicationScope, '').toString()
		self.groupSingleApplicationScope.valueChanged.connect(self.setSingleApplicationScope)
		self.groupSingleApplicationScope.setValue(value)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyWebViewZoomSteps, Tc2Config.WebViewZoomStepsDefault).toInt()
		if not ok or value < Tc2Config.WebViewZoomStepsMin or value > Tc2Config.WebViewZoomStepsMax:
			value = Tc2Config.WebView.ZoomStepsDefault
		self.spinWebViewZoomSteps.setValue(value)
		self.spinWebViewZoomSteps.valueChanged.connect(self.setWebViewZoomSteps)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyAlternatingRowColors, False).toBool() else QtCore.Qt.Unchecked
		self.checkAlternatingRowColors.setCheckState(value)
		self.checkAlternatingRowColors.stateChanged.connect(
				lambda value, self=self: self.setAlternatingRowColors(self.checkAlternatingRowColors.checkState() == QtCore.Qt.Checked)
				)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyChildItemIndicators, False).toBool() else QtCore.Qt.Unchecked
		self.checkChildItemIndicators.setCheckState(value)
		self.checkChildItemIndicators.stateChanged.connect(
				lambda value, self=self: self.setChildItemIndicators(self.checkChildItemIndicators.checkState() == QtCore.Qt.Checked)
				)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyRestoreMousePosition, False).toBool() else QtCore.Qt.Unchecked
		self.checkRestoreMousePosition.setCheckState(value)
		self.checkRestoreMousePosition.stateChanged.connect(
				lambda value, self=self: self.setRestoreMousePosition(self.checkRestoreMousePosition.checkState() == QtCore.Qt.Checked)
				)

		value = Tc2Config.settingsValue(self.SettingsKeyToolBarPosition, '').toString()
		if value not in Tc2Config.ToolBarPositions:
			value = Tc2Config.ToolBarPositionDefault
		self.comboToolBarPosition.setCurrentIndex( self.comboToolBarPosition.findText(value, QtCore.Qt.MatchExactly) )
		#NOTE: pySlot decorator does not work as expected so we have to connect slot the old fashioned way
		self.connect(self.comboToolBarPosition, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setToolBarPosition)

		value = Tc2Config.settingsValue(self.SettingsKeyTabPosition, '').toString()
		if value not in Tc2Config.TabPositions:
			value = Tc2Config.TabPositionDefault
		self.comboTabPosition.setCurrentIndex( self.comboTabPosition.findText(value, QtCore.Qt.MatchExactly) )
		#NOTE: pySlot decorator does not work as expected so we have to connect slot the old fashioned way
		self.connect(self.comboTabPosition, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setTabPosition)

		value = Tc2Config.settingsValue(self.SettingsKeyRoundBets, '').toString()
		if value not in Tc2Config.RoundBets:
			value = Tc2Config.RoundBetsDefault
		self.comboRoundBets.setCurrentIndex( self.comboRoundBets.findText(value, QtCore.Qt.MatchExactly) )
		#NOTE: pySlot decorator does not work as expected so we have to connect slot the old fashioned way
		self.connect(self.comboRoundBets, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setRoundBets)


		Tc2Config.globalObject.objectCreatedSettingsGlobal.emit(self)



