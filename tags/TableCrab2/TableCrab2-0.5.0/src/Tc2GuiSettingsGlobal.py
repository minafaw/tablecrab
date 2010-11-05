
import Tc2Config
import Tc2Win32
import Tc2GuiHelp
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Settings'
	SettingsKeyDialogBackupState = SettingsKeyBase + '/DialogBackup/State'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.buttonBackup = QtGui.QPushButton('..', self)
		self.buttonBackup.clicked.connect(self.onButtonBackupClicked)
		self.labelBackup = QtGui.QLabel('&Backup TableCrab:', self)
		self.labelBackup.setBuddy(self.buttonBackup)

		self.comboGuiStyle = QtGui.QComboBox(self)
		self.comboGuiStyle.addItems( QtGui.QStyleFactory().keys() )
		self.labelGuiStyle = QtGui.QLabel('Global &Style:', self)
		self.labelGuiStyle.setBuddy(self.comboGuiStyle)

		self.buttonFont = QtGui.QPushButton('..', self)
		self.labelFont = QtGui.QLabel('Global &Font:', self)
		self.labelFont.setBuddy(self.buttonFont)

		self.buttonFixedFont = QtGui.QPushButton('..', self)
		self.labelFixedFont = QtGui.QLabel('Fi&xed Font:', self)
		self.labelFixedFont.setBuddy(self.buttonFixedFont)

		self.comboSingleApplication = QtGui.QComboBox(self)
		self.comboSingleApplication.addItems(Tc2Win32.SingleApplication.Scopes)
		self.labelSingleApplication = QtGui.QLabel('Single a&pplication scope:', self)
		self.labelSingleApplication.setBuddy(self.comboSingleApplication)

		self.spinZoomSteps = QtGui.QSpinBox(self)
		self.spinZoomSteps.setRange(Tc2Config.WebViewToolBar.ZoomStepsMin, Tc2Config.WebViewToolBar.ZoomStepsMax)
		self.labelZoomSteps = QtGui.QLabel('&Zoom Steps (%s max):' % Tc2Config.WebViewToolBar.ZoomStepsMax, self)
		self.labelZoomSteps.setBuddy(self.spinZoomSteps)

		self.checkAlternatingRowColors = QtGui.QCheckBox('Alternating &Row Colors', self)
		self.checkChildItemIndicators = QtGui.QCheckBox('&Child Item Indicators', self)
		self.checkRestoreMousePosition = QtGui.QCheckBox('Restore Mouse &Position', self)

		self.comboToolBarPosition = QtGui.QComboBox(self)
		self.comboToolBarPosition.addItems(Tc2Config.ToolBarPositions)
		self.labelToolBarPosition = QtGui.QLabel('T&oolBar position:', self)
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

		Tc2Config.globalObject.init.connect(self.onInit)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelBackup).col(self.buttonBackup).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelGuiStyle).col(self.comboGuiStyle).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelFont).col(self.buttonFont).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelFixedFont).col(self.buttonFixedFont).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelSingleApplication).col(self.comboSingleApplication).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelTabPosition).col(self.comboTabPosition).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelToolBarPosition).col(self.comboToolBarPosition).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelZoomSteps).col(self.spinZoomSteps).col(Tc2Config.HStretch())
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

	def setFont(self):
		font = QtGui.QFont()
		# try to read font from config, if not take application font
		if font.fromString( Tc2Config.settingsValue(Tc2Config.SettingsKeyFont, '').toString() ):
			QtGui.qApp.setFont(font)
		else:
			font = QtGui.qApp.font()

		# we have to reload style on font changes anyways, so global style setting is dome here
		styleName = Tc2Config.settingsValue(Tc2Config.SettingsKeyStyle, '').toString()
		styleNames = QtGui.QStyleFactory().keys()
		if styleName in styleNames:
			pass
		else:
			#HACK:  not documented for getting style name but the lights are on. so i assume it works
			styleName =QtGui.qApp.style().objectName()
		style = QtGui.QStyleFactory.create(styleName)
		#TODO: we currently set no palette. QStyle docs say palette should not be set
		# for styles that use system defaults, but there seems to be no way to find out
		# so ..and where to find some kind of default palette.
		##QtGui.qApp.setPalette(style.standardPalette())
		QtGui.qApp.setStyle(style)

		self.comboGuiStyle.setCurrentIndex( self.comboGuiStyle.findText(styleName, QtCore.Qt.MatchExactly) )
		self.buttonFont.setText( QtCore.QString('%1 %2').arg(font.family()).arg(font.pointSize()) )
		# take QWebKit StandardFont from application font
		settings = QtWebKit.QWebSettings.globalSettings()
		settings.setFontFamily(settings.StandardFont, font.family() )
		settings.setFontSize(settings.DefaultFontSize, font.pointSize() )

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

	def onButtonFontClicked(self, checked):
		font, ok = QtGui.QFontDialog.getFont(QtGui.qApp.font(), self)
		if ok:
			Tc2Config.settingsSetValue(Tc2Config.SettingsKeyFont, font.toString())
			self.setFont()

	def onButtonFixedFontClicked(self, checked):
		font = QtGui.QFont()
		settings = QtWebKit.QWebSettings.globalSettings()
		font.setFamily( settings.fontFamily(settings.FixedFont) )
		font.setPointSize( settings.fontSize(settings.DefaultFixedFontSize) )
		font, ok = QtGui.QFontDialog.getFont(font, self)
		if ok:
			Tc2Config.settingsSetValue(Tc2Config.SettingsKeyFontFixed, font.toString())
			self.setFixedFont()

	def onComboGuiStyleCurrentIndexChanged(self, index):
		style = self.comboGuiStyle.itemText(index)
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyStyle, style)
		self.setFont()

	def onComboRoundBetsCurrentIndexChanged(self, index):
		roundBets = self.comboRoundBets.itemText(index)
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyRoundBets, roundBets)

	def onComboSingleApplicationCurrentIndexChanged(self, index):
		scope = self.comboSingleApplication.itemText(index)
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeySingleApplicationScope, scope)

	def onAlternatingRowColorsChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyAlternatingRowColors, flag)
		Tc2Config.globalObject.settingAlternatingRowColorsChanged.emit(flag)

	def onChildItemIndicatorsChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyChildItemIndicators, flag)
		Tc2Config.globalObject.settingChildItemIndicatorsChanged.emit(state == QtCore.Qt.Checked)

	def onRestoreMousePositionChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyRestoreMousePosition, flag)

	def onSpinZoomValueChanged(self, value):
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyWebViewZoomSteps, value)

	def onComboToolBarPositionCurrentIndexChanged(self, index):
		value = self.comboToolBarPosition.itemText(index)
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyToolBarPosition, value)
		Tc2Config.globalObject.settingToolBarPositionChanged.emit(value)

	def onComboTabPositionCurrentIndexChanged(self, index):
		value = self.comboTabPosition.itemText(index)
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyTabPosition, value)
		Tc2Config.globalObject.settingTabPositionChanged.emit(value)

	def onInit(self):
		self.layout()

		self.setFont()	#NOTE: sets gui style as well
		self.comboGuiStyle.currentIndexChanged.connect(self.onComboGuiStyleCurrentIndexChanged)
		self.buttonFont.clicked.connect(self.onButtonFontClicked)
		self.setFixedFont()
		self.buttonFixedFont.clicked.connect(self.onButtonFixedFontClicked)

		scope= Tc2Config.settingsValue(Tc2Config.SettingsKeySingleApplicationScope, '').toString()
		if scope not in Tc2Win32.SingleApplication.Scopes:
			scope = Tc2Config.SingleApplicationScopeDefault
		self.comboSingleApplication.setCurrentIndex( self.comboSingleApplication.findText(scope, QtCore.Qt.MatchExactly) )
		self.comboSingleApplication.currentIndexChanged.connect(self.onComboSingleApplicationCurrentIndexChanged)

		zoomSteps = Tc2Config.settingsValue(Tc2Config.SettingsKeyWebViewZoomSteps, Tc2Config.WebViewToolBar.ZoomStepsDefault).toInt()[0]
		self.spinZoomSteps.setValue(zoomSteps)
		self.spinZoomSteps.valueChanged.connect(self.onSpinZoomValueChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2Config.SettingsKeyAlternatingRowColors, False).toBool() else QtCore.Qt.Unchecked
		self.checkAlternatingRowColors.setCheckState(state)
		self.checkAlternatingRowColors.stateChanged.connect(self.onAlternatingRowColorsChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2Config.SettingsKeyChildItemIndicators, False).toBool() else QtCore.Qt.Unchecked
		self.checkChildItemIndicators.setCheckState(state)
		self.checkChildItemIndicators.stateChanged.connect(self.onChildItemIndicatorsChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2Config.SettingsKeyRestoreMousePosition, False).toBool() else QtCore.Qt.Unchecked
		self.checkRestoreMousePosition.setCheckState(state)
		self.checkRestoreMousePosition.stateChanged.connect(self.onRestoreMousePositionChanged)

		value= Tc2Config.settingsValue(Tc2Config.SettingsKeyToolBarPosition, '').toString()
		if value not in Tc2Config.ToolBarPositions:
			value = Tc2Config.ToolBarPositionDefault
		self.comboToolBarPosition.setCurrentIndex( self.comboToolBarPosition.findText(value, QtCore.Qt.MatchExactly) )
		self.comboToolBarPosition.currentIndexChanged.connect(self.onComboToolBarPositionCurrentIndexChanged)

		value= Tc2Config.settingsValue(Tc2Config.SettingsKeyTabPosition, '').toString()
		if value not in Tc2Config.TabPositions:
			value = Tc2Config.TabPositionDefault
		self.comboTabPosition.setCurrentIndex( self.comboTabPosition.findText(value, QtCore.Qt.MatchExactly) )
		self.comboTabPosition.currentIndexChanged.connect(self.onComboTabPositionCurrentIndexChanged)

		roundBets = Tc2Config.settingsValue(Tc2Config.SettingsKeyRoundBets, '').toString()
		if roundBets not in Tc2Config.RoundBets:
			roundBets = Tc2Config.RoundBetsDefault
		self.comboRoundBets.setCurrentIndex( self.comboRoundBets.findText(roundBets, QtCore.Qt.MatchExactly) )
		self.comboRoundBets.currentIndexChanged.connect(self.onComboRoundBetsCurrentIndexChanged)
