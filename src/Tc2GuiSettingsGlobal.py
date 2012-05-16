
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

	settingSingleApplicationScope = Tc2Config.settings2.ChooseString(
			'Gui/SingleApplication/Scope',
			defaultValue=Tc2Config.SingleApplicationScopeDefault,
			choices=Tc2Win32.SingleApplication.Scopes,
			)
	settingGuiStyle = Tc2Config.settings2.ChooseString(
			'Gui/Style',
			defaultValue=None,	# not known at compile time, set later
			choices=[unicode(i.toUtf8(), 'utf-8') for i in QtGui.QStyleFactory().keys()],
			)
	settingGuiFont = Tc2Config.settings2.Font(
			'Gui/Font',
			defaultValue=None,	# not known at compile time, set later
			)
	settingFixedFont = Tc2Config.settings2.Font(
			'Gui/FontFixed',
			defaultValue=None,	# not known at compile time, set later
			)
	settingTabPosition = Tc2Config.settings2.ChooseString(
			'Gui/Tab/Position',
			defaultValue=Tc2Config.TabPositionDefault,
			choices=Tc2Config.TabPositions,
			)
	settingToolBarPosition = Tc2Config.settings2.ChooseString(
			'Gui/ToolBar/Position',
			defaultValue=Tc2Config.ToolBarPositionDefault,
			choices=Tc2Config.ToolBarPositions,
			)
	settingSideBarPosition = Tc2Config.settings2.ChooseString(
			'Gui/SideBar/Position',
			defaultValue=Tc2Config.SideBarPositionDefault,
			choices=Tc2Config.SideBarPositions
			)
	settingAlternatingRowColors = Tc2Config.settings2.Bool(
			'Gui/AlternatingRowColors',
			defaultValue=True
			)
	settingChildItemIndicators = Tc2Config.settings2.Bool(
			'Gui/ChildItemIndicators',
			defaultValue=True
			)
	settingsWebViewZoomSteps = Tc2Config.settings2.Int(
			'Gui/Browser/ZoomSteps',
			defaultValue=Tc2Config.WebViewZoomStepsDefault,
			minValue=Tc2Config.WebViewZoomStepsMin,
			maxValue=Tc2Config.WebViewZoomStepsMax,
			)
	settingsDialogBackupState = Tc2Config.settings2.ByteArray(
			'Gui/DialogSaveApplicationSettings/State',
			defaultValue=QtCore.QByteArray(),
			)
	settingRestoreMousePosition = Tc2Config.settings2.Bool(
			'Sites/RestoreMousePosition',
			defaultValue=False
			)
	settingRoundBets = Tc2Config.settings2.ChooseString(
			'Sites/RoundBets',
			defaultValue=Tc2Config.RoundBetsDefault,
			choices=Tc2Config.RoundBets
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

		self.comboSideBarPosition = QtGui.QComboBox(self)
		self.labelSideBarPosition = QtGui.QLabel('&Side bar position:', self)
		self.labelSideBarPosition.setBuddy(self.comboSideBarPosition)

		self.comboRoundBets = QtGui.QComboBox(self)
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

		Tc2Config.globalObject.guiInit.connect(self.onInitGui)


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
		grid.col(self.labelSideBarPosition).col(self.comboSideBarPosition)
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
		self.settingSideBarPosition.setComboBox(self.comboSideBarPosition)
		self.settingAlternatingRowColors.setCheckBox(self.checkAlternatingRowColors)
		self.settingChildItemIndicators.setCheckBox(self.checkChildItemIndicators)
		self.settingsWebViewZoomSteps.setSpinBox(self.spinWebViewZoomSteps)

		self.settingSingleApplicationScope.setComboBox(self.comboSingleApplicationScope)
		self.settingRoundBets.setComboBox(self.comboRoundBets)
		self.settingRestoreMousePosition.setCheckBox(self.checkRestoreMousePosition)

		self.layout()


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



