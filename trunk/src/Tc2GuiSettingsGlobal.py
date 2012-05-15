
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
	#TODO: site specific. move to /Sites
	SettingsKeyRestoreMousePosition = 'RestoreMousePosition'
	#TODO: site specific. move to /Sites
	SettingsKeyRoundBets = 'Settings/RoundBets'

	restoreMousePositionChanged = QtCore.pyqtSignal(bool)
	roundBetsChanged = QtCore.pyqtSignal(QtCore.QString)

	# #########################################
	settingSingleApplicationScope = Tc2Config.settings2.chooseString(
			'Gui/SingleApplication/Scope',
			defaultValue=Tc2Config.SingleApplicationScopeDefault,
			choices=Tc2Win32.SingleApplication.Scopes,
			)
	settingGuiStyle = Tc2Config.settings2.chooseString(
			'Gui/Style',
			defaultValue=None,	# not known at compile time, set later
			choices=[unicode(i.toUtf8(), 'utf-8') for i in QtGui.QStyleFactory().keys()],
			)
	settingGuiFont = Tc2Config.settings2.font(
			'Gui/Font',
			defaultValue=None,	# not known at compile time, set later
			)
	settingFixedFont = Tc2Config.settings2.font(
			'Gui/FontFixed',
			defaultValue=None,	# not known at compile time, set later
			)
	settingTabPosition = Tc2Config.settings2.chooseString(
			'Gui/Tab/Position',
			defaultValue=Tc2Config.TabPositionDefault,
			choices=Tc2Config.TabPositions,
			)
	settingToolBarPosition = Tc2Config.settings2.chooseString(
			'Gui/ToolBar/Position',
			defaultValue=Tc2Config.ToolBarPositionDefault,
			choices=Tc2Config.ToolBarPositions,
			)
	settingAlternatingRowColors = Tc2Config.settings2.bool(
			'Gui/AlternatingRowColors',
			defaultValue=True
			)
	settingChildItemIndicators = Tc2Config.settings2.bool(
			'Gui/ChildItemIndicators',
			defaultValue=True
			)
	settingsWebViewZoomSteps = Tc2Config.settings2.int(
			'Gui/Browser/ZoomSteps',
			defaultValue=Tc2Config.WebViewZoomStepsDefault,
			minValue=Tc2Config.WebViewZoomStepsMin,
			maxValue=Tc2Config.WebViewZoomStepsMax,
			)
	settingsDialogBackupState = Tc2Config.settings2.byteArray(
			'Gui/Dialogs/SaveApplicationSettings/State',
			defaultValue=QtCore.QByteArray(),
			)


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.buttonBackup = QtGui.QPushButton('..', self)
		self.buttonBackup.clicked.connect(self.onButtonBackupClicked)
		self.labelBackup = QtGui.QLabel('&Backup TableCrab:', self)
		self.labelBackup.setBuddy(self.buttonBackup)

		self.comboGuiStyle = QtGui.QComboBox(self)
		self.labelGuiStyle = QtGui.QLabel('Global &Style:', self)
		self.labelGuiStyle.setBuddy(self.comboGuiStyle)

		self.groupGuiFont = FontButton.GroupFontButton(
				parent=self,
				text='Global &Font:',
				toolTip='Select gui font'
				)

		self.groupFixedFont = FontButton.GroupFontButton(
				parent=self,
				text='Fi&xed Font:',
				toolTip='Select fixed font'
				)

		self.comboSingleApplicationScope = QtGui.QComboBox(self)
		self.labelSingleApplicationScope = QtGui.QLabel('Single a&pplication scope:', self)
		self.labelSingleApplicationScope.setBuddy(self.comboSingleApplicationScope)

		self.spinWebViewZoomSteps = QtGui.QSpinBox(self)
		self.labelWebViewZoomSteps = QtGui.QLabel('&Zoom Steps (%s max):' % Tc2Config.WebViewZoomStepsMax, self)
		self.labelWebViewZoomSteps.setBuddy(self.spinWebViewZoomSteps)

		self.checkAlternatingRowColors = QtGui.QCheckBox('Alternating &Row Colors', self)
		self.checkChildItemIndicators = QtGui.QCheckBox('&Child Item Indicators', self)
		self.checkRestoreMousePosition = QtGui.QCheckBox('Restore Mouse &Position', self)

		self.comboToolBarPosition = QtGui.QComboBox(self)
		self.labelToolBarPosition = QtGui.QLabel('T&ool bar position:', self)
		self.labelToolBarPosition.setBuddy(self.comboToolBarPosition)

		self.comboTabPosition = QtGui.QComboBox(self)
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
		Tc2Config.globalObject.initGui.connect(self.onInitGui)


	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=2)
		grid.row()
		grid.col(self.labelBackup).col(self.buttonBackup)
		grid.row()
		grid.col(self.labelGuiStyle).col(self.comboGuiStyle)
		grid.row()
		grid.col(self.groupGuiFont.label() ).col(self.groupGuiFont.fontButton()).col(self.groupGuiFont.resetButton())
		grid.row()
		grid.col(self.groupFixedFont.label()).col(self.groupFixedFont.fontButton()).col(self.groupFixedFont.resetButton())
		grid.row()
		grid.col(self.labelSingleApplicationScope).col(self.comboSingleApplicationScope)
		grid.row()
		grid.col(self.labelTabPosition).col(self.comboTabPosition)
		grid.row()
		grid.col(self.labelToolBarPosition).col(self.comboToolBarPosition)
		grid.row()
		grid.col(self.labelWebViewZoomSteps).col(self.spinWebViewZoomSteps)
		grid.row()
		grid.col(self.checkAlternatingRowColors)
		grid.row()
		grid.col(self.checkChildItemIndicators)
		grid.row()
		grid.col(self.checkRestoreMousePosition)
		grid.row()
		grid.col(self.labelRoundBets).col(self.comboRoundBets)
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=2)
		grid.row()
		grid.col(self.buttonBox, colspan=2)

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
		dlg.restoreState(self.settingsDialogBackupState.value())
		result = dlg.exec_()
		self.settingsDialogBackupState.setValue(dlg.saveState())
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

	def restoreMousePosition(self):
		return self.checkRestoreMousePosition.checkState() == QtCore.Qt.Checked

	def setRestoreMousePosition(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyRestoreMousePosition, value)
		self.restoreMousePositionChanged.emit(value)

	def roundBets(self):
		return self.comboRoundBets.currentText()

	def setRoundBets(self,value):
		Tc2Config.settingsSetValue(self.SettingsKeyRoundBets, value)
		self.roundBetsChanged.emit(value)

	def onInitGui(self):
		#NOTE: try to find current gui style
		# - gui style is not known at compile time
		# - QtGui.qApp.style().objectName() returns style but is undocumented
		# - returned string is lowercase for some reason
		# - while QStyleFactory.keys() are camel case
		tmpStyle = unicode(QtGui.qApp.style().objectName().toUtf8(), 'utf-8')
		for style in self.settingGuiStyle.choices():
			if style.lower() == tmpStyle:
				self.settingGuiStyle.setDefaultValue(style)
				break
		else:
			self.settingGuiStyle.setDefaultValue(self.settingGuiStyle.choices()[0])
		self.settingGuiStyle.setComboBox(self.comboGuiStyle)
		self.settingGuiStyle.changed.connect(self.onSettingGuiStyleChanged)

		self.settingGuiFont.setDefaultValue(QtGui.qApp.font())
		self.settingGuiFont.setFontButton(self.groupGuiFont.fontButton())
		self.settingGuiFont.changed.connect(self.onSettingGuiFontChanged)

		settings = QtWebKit.QWebSettings.globalSettings()
		font = QtGui.QFont(settings.fontFamily(settings.FixedFont), settings.fontSize(settings.DefaultFixedFontSize))
		self.settingFixedFont.setDefaultValue(font)
		self.settingFixedFont.setFontButton(self.groupFixedFont.fontButton())
		self.settingFixedFont.changed.connect(self.onSettingFixedFontChanged)

		self.settingToolBarPosition.setComboBox(self.comboToolBarPosition)
		self.settingTabPosition.setComboBox(self.comboTabPosition)
		self.settingAlternatingRowColors.setCheckBox(self.checkAlternatingRowColors)
		self.settingChildItemIndicators.setCheckBox(self.checkChildItemIndicators)
		self.settingsWebViewZoomSteps.setSpinBox(self.spinWebViewZoomSteps)

		self.settingSingleApplicationScope.setComboBox(self.comboSingleApplicationScope)

	def onSettingGuiStyleChanged(self, setting):
		tmpStyle = unicode(QtGui.qApp.style().objectName().toUtf8(), 'utf-8')
		#NOTE: font changes trigger style changes and vice versa, so we check here
		if tmpStyle != setting.value().lower():
			style = QtGui.QStyleFactory.create(setting.value())
			QtGui.qApp.setStyle(style)

	def onSettingGuiFontChanged(self, setting):
		font = setting.value()
		QtGui.qApp.setFont(font)
		#NOTE: have to re-set style to make font changes work as expected
		QtGui.qApp.setStyle(self.settingGuiStyle.value())
		# take QWebKit StandardFont from application font
		settings = QtWebKit.QWebSettings.globalSettings()
		settings.setFontFamily(settings.StandardFont,font.family() )
		settings.setFontSize(settings.DefaultFontSize, font.pointSize() )

	def onSettingFixedFontChanged(self, setting):
		# adjust WeKit fixed font
		font = setting.value()
		settings = QtWebKit.QWebSettings.globalSettings()
		settings.setFontFamily(settings.FixedFont, font.family() )
		settings.setFontSize(settings.DefaultFixedFontSize, font.pointSize() )

	def onInitSettings(self):
		self.layout()

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyRestoreMousePosition, False).toBool() else QtCore.Qt.Unchecked
		self.checkRestoreMousePosition.setCheckState(value)
		self.checkRestoreMousePosition.stateChanged.connect(
				lambda value, self=self: self.setRestoreMousePosition(self.checkRestoreMousePosition.checkState() == QtCore.Qt.Checked)
				)

		value = Tc2Config.settingsValue(self.SettingsKeyRoundBets, '').toString()
		if value not in Tc2Config.RoundBets:
			value = Tc2Config.RoundBetsDefault
		self.comboRoundBets.setCurrentIndex( self.comboRoundBets.findText(value, QtCore.Qt.MatchExactly) )
		#NOTE: pySlot decorator does not work as expected so we have to connect slot the old fashioned way
		self.connect(self.comboRoundBets, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setRoundBets)


		Tc2Config.globalObject.objectCreatedSettingsGlobal.emit(self)



