
import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.buttonBackup = QtGui.QPushButton('..', self)
		self.buttonBackup.clicked.connect(self.onButtonBackupClicked)
		self.labelBackup = QtGui.QLabel('&Backup TableCrab:', self)
		self.labelBackup.setBuddy(self.buttonBackup)

		self.comboGuiStyle = TableCrabConfig.ComboBox(
				[style for style in QtGui.QStyleFactory().keys()] ,
				settingsKey='Gui/Style',
				default=QtGui.qApp.style().objectName(),	#HACK:  not documented for getting style name but the lights are on. so i assume it works
				failsave=True,
				parent=self,
				)
		self.comboGuiStyle.currentIndexChanged.connect(self.onComboGuiStyleCurrentIndexChanged)
		self.labelGuiStyle = QtGui.QLabel('Global &Style:', self)
		self.labelGuiStyle.setBuddy(self.comboGuiStyle)

		self.buttonFont = QtGui.QPushButton('..', self)
		self.buttonFont.clicked.connect(self.onButtonFontClicked)
		self.labelFont = QtGui.QLabel('Global &Font:', self)
		self.labelFont.setBuddy(self.buttonFont)

		self.buttonFixedFont = QtGui.QPushButton('..', self)
		self.buttonFixedFont.clicked.connect(self.onButtonFixedFontClicked)
		self.labelFixedFont = QtGui.QLabel('Fi&xed Font:', self)
		self.labelFixedFont.setBuddy(self.buttonFixedFont)

		self.comboSingleApplication = TableCrabConfig.ComboBox(
				TableCrabWin32.SingleApplication.Scopes,
				settingsKey='Gui/SingleApplication/Scope',
				default=TableCrabConfig.SingleApplicationScopeDefault,
				failsave=True,
				parent=self,
				)
		self.labelSingleApplication = QtGui.QLabel('Single a&pplication scope:', self)
		self.labelSingleApplication.setBuddy(self.comboSingleApplication)

		self.spinZoomSteps = TableCrabConfig.SpinBox(
			settingsKey='Gui/WebView/ZoomSteps',
			default=TableCrabConfig.WebViewToolBar.ZoomSteps,
			minimum=1,
			maximum=TableCrabConfig. WebViewToolBar.ZoomStepsMax,
			parent=self,
			)
		self.labelZoomSteps = QtGui.QLabel('&Zoom Steps (%s max):' % TableCrabConfig.WebViewToolBar.ZoomStepsMax, self)
		self.labelZoomSteps.setBuddy(self.spinZoomSteps)

		self.checkAlternatingRowColors = TableCrabConfig.CheckBox('Alternating &Row Colors', default=False, settingsKey='Gui/AlternatingRowColors', parent=self)
		self.checkAlternatingRowColors.stateChanged.connect(self.onAlternatingRowColorsChanged)
		self.checkChildItemIndicators = TableCrabConfig.CheckBox('&Child Item Indicators', default=True, settingsKey='Gui/ChildItemIndicators', parent=self)
		self.checkChildItemIndicators.stateChanged.connect(self.onChildItemIndicatorsChanged)
		self.checkRestoreMousePosition = TableCrabConfig.CheckBox('Restore Mouse &Position', default=False, settingsKey='RestoreMousePosition', parent=self)

		self.comboRoundBets = TableCrabConfig.ComboBox(
				[
					TableCrabConfig.RoundBetsNoRounding,
					TableCrabConfig.RoundBetsBigBlind,
					TableCrabConfig.RoundBetsSmallBlind
				],
				default= TableCrabConfig.RoundBetsNoRounding,
				failsave=True,
				settingsKey='Settings/RoundBets',
				parent=self,
				)
		self.labelRoundBets = QtGui.QLabel('Round &bets to:', self)
		self.labelRoundBets.setBuddy(self.comboRoundBets)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='F1',
				slot=self.onHelp,
				)
		self.addAction(action)

		TableCrabConfig.globalObject.init.connect(self.onInit)

		self.layout()

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelBackup).col(self.buttonBackup).col(TableCrabConfig.HStretch())
		grid.row()
		grid.col(self.labelGuiStyle).col(self.comboGuiStyle).col(TableCrabConfig.HStretch())
		grid.row()
		grid.col(self.labelFont).col(self.buttonFont).col(TableCrabConfig.HStretch())
		grid.row()
		grid.col(self.labelFixedFont).col(self.buttonFixedFont).col(TableCrabConfig.HStretch())
		grid.row()
		grid.col(self.labelSingleApplication).col(self.comboSingleApplication).col(TableCrabConfig.HStretch())
		grid.row()
		grid.col(self.labelZoomSteps).col(self.spinZoomSteps).col(TableCrabConfig.HStretch())
		grid.row()
		grid.col(self.checkAlternatingRowColors)
		grid.row()
		grid.col(self.checkChildItemIndicators)
		grid.row()
		grid.col(self.checkRestoreMousePosition)
		grid.row()
		grid.col(self.labelRoundBets).col(self.comboRoundBets).col(TableCrabConfig.HStretch())
		grid.row()
		grid.col(TableCrabConfig.VStretch())
		grid.row()
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def setFont(self):
		font = QtGui.QFont()
		# try to read font from config, if not take application font
		if font.fromString( TableCrabConfig.settingsValue('Gui/Font', '').toString() ):
			QtGui.qApp.setFont(font)
		else:
			font = QtGui.qApp.font()
		# we have to reload style on font changes anyways, so global style setting is dome here
		QtGui.qApp.setStyle(QtGui.QStyleFactory.create( TableCrabConfig.settingsValue('Gui/Style', '').toString() ))
		self.comboGuiStyle.onInit()
		self.buttonFont.setText( QtCore.QString('%1 %2').arg(font.family()).arg(font.pointSize()) )
		# take QWebKit StandardFont from application font
		settings = QtWebKit.QWebSettings.globalSettings()
		settings.setFontFamily(settings.StandardFont, font.family() )
		settings.setFontSize(settings.DefaultFontSize, font.pointSize() )

	def setFixedFont(self):
		font = QtGui.QFont()
		settings = QtWebKit.QWebSettings.globalSettings()
		# try to read QWebKit FixedFont from config, if not take it from QWebKit FixedFont
		if font.fromString(TableCrabConfig.settingsValue('Gui/FontFixed', '').toString() ):
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
		dlg.restoreState( TableCrabConfig.settingsValue('Gui/Settings/DialogBackup/State', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Settings/DialogBackup/State', dlg.saveState() )
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
			TableCrabConfig.msgWarning(self, 'Could Not Open Config File\n\n%s' % d)
			return
		finally:
			if fp is not None: fp.close()

		newSettings = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
		if not newSettings.isWritable:
			TableCrabConfig.msgWarning(self, 'Config File Is Not Writable')
			return
		settings = TableCrabConfig.settings()
		for key in settings.allKeys():
			newSettings.setValue(key, settings.value(key) )

	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('settingsGlobal', parent=self)

	def onButtonFontClicked(self, checked):
		font, ok = QtGui.QFontDialog.getFont(QtGui.qApp.font(), self)
		if ok:
			TableCrabConfig.settingsSetValue('Gui/Font', font.toString())
			self.setFont()

	def onButtonFixedFontClicked(self, checked):
		font = QtGui.QFont()
		settings = QtWebKit.QWebSettings.globalSettings()
		font.setFamily( settings.fontFamily(settings.FixedFont) )
		font.setPointSize( settings.fontSize(settings.DefaultFixedFontSize) )
		font, ok = QtGui.QFontDialog.getFont(font, self)
		if ok:
			TableCrabConfig.settingsSetValue('Gui/FontFixed', font.toString())
			self.setFixedFont()

	def onComboGuiStyleCurrentIndexChanged(self, index):
		QtGui.qApp.setStyle(QtGui.QStyleFactory.create(self.comboGuiStyle.itemText(index)) )

	def onAlternatingRowColorsChanged(self, state):
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.emit(state == QtCore.Qt.Checked)

	def onChildItemIndicatorsChanged(self, state):
		TableCrabConfig.globalObject.settingChildItemIndicatorsChanged.emit(state == QtCore.Qt.Checked)

	def onInit(self):
		self.setFont()	#NOTE: sets gui style as well
		self.setFixedFont()
