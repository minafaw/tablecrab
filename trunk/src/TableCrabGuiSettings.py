
#TODO: accelerators for settings "Hand Style Sheet"
#TODO: tooltips flapping out on settings selector pane are ugly. no way to set tooltip delay in Qt4
#			so we may have to reimplement tool tips
#TODO: have to find a better way to present prefix | postfix in settings hand
#TODO: would be nice to have line numbers in HandCss editor

import TableCrabConfig
import PokerStarsHandGrabber
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui, QtWebKit

#**********************************************************************************************
#
#**********************************************************************************************

class FrameSettingsGlobal(QtGui.QFrame):
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
		grid.addWidget(TableCrabConfig.HLine(self), 0, 0, 1, 3)

		grid.addWidget(self.labelBackup, 1, 0)
		grid.addWidget(self.buttonBackup, 1, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 1, 2)

		grid.addWidget(self.labelGuiStyle, 2, 0)
		grid.addWidget(self.comboGuiStyle, 2, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 2, 2)

		grid.addWidget(self.labelFont, 3, 0)
		grid.addWidget(self.buttonFont, 3, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 3, 2)

		grid.addWidget(self.labelFixedFont, 4, 0)
		grid.addWidget(self.buttonFixedFont, 4, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 4, 2)

		grid.addWidget(self.labelZoomSteps, 5, 0)
		grid.addWidget(self.spinZoomSteps, 5, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 5, 2)

		grid.addWidget(self.checkAlternatingRowColors, 6, 0)
		grid.addWidget(self.checkChildItemIndicators, 7, 0)
		grid.addWidget(self.checkRestoreMousePosition, 8, 0)

		grid.addWidget(self.labelRoundBets, 9, 0)
		grid.addWidget(self.comboRoundBets, 9, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 9, 2)


		grid.addLayout(TableCrabConfig.VStretch(), 10, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 11, 0, 1, 3)

		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 12, 0, 1, 3)
		grid2.addWidget(self.buttonBox, 0, 0)

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


class FrameSettingsPokerStars(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.checkAutoClosePopupNews = TableCrabConfig.CheckBox(
				'Close Popup &News',
				settingsKey='PokerStars/AutoClosePopupNews',
				default=False
				)
		self.checkAutoCloseTourneyRegistrationBoxes = TableCrabConfig.CheckBox(
				'Close T&ourney Registration Boxes',
				settingsKey='PokerStars/AutoCloseTourneyRegistrationBoxes',
				default=False
				)
		self.checkAutoCloseTableMessageBoxes = TableCrabConfig.CheckBox(
				'Close Ta&ble Message Boxes',
				settingsKey='PokerStars/AutoCloseTableMessageBoxes',
				default=False
				)
		self.checkAutoLogIn = TableCrabConfig.CheckBox(
				'Close &Log In Box',
				settingsKey='PokerStars/AutoCloseLogin',
				default=False
				)
		self.checkMoveMouseToActiveTable = TableCrabConfig.CheckBox(
				'Move &Mouse To Active table',
				settingsKey='PokerStars/MoveMouseToActiveTable',
				default=False
				)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='F1',
				slot=self.onHelp,
				)
		self.addAction(action)


		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(TableCrabConfig.HLine(self), 0, 0, 1, 3)

		grid.addWidget(self.checkAutoClosePopupNews, 1, 0)
		grid.addWidget(self.checkAutoCloseTourneyRegistrationBoxes, 2, 0)
		grid.addWidget(self.checkAutoCloseTableMessageBoxes, 3, 0)
		grid.addWidget(self.checkAutoLogIn, 4, 0)
		grid.addWidget(self.checkMoveMouseToActiveTable, 5, 0)

		grid.addLayout(TableCrabConfig.VStretch(), 6, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 7, 0, 1, 3)

		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 8, 0, 1, 3)
		grid2.addWidget(self.buttonBox, 0, 0)

	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('settingsPokerStars', parent=self)


class FrameSettingsHand(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.labelPrefix = QtGui.QLabel('<i>Prefix</i>', self)
		self.labelAction = QtGui.QLabel('<i>Action</i>', self)
		self.labelPostfix = QtGui.QLabel('<i>Postfix</i>', self)

		actionSettings = (
			('PrefixBet', '&Bet', 'PostfixBet'),
			('PrefixCall', '&Call', 'PostfixCall'),
			('PrefixCheck', 'Ch&eck', None),
			('PrefixFold', '&Fold', None),
			('PrefixRaise', '&Raise', 'PostfixRaise'),
			('PrefixAnte', 'A&nte', 'PostfixAnte'),
			('PrefixBigBlind', 'B&igBlind', 'PostfixBigBlind'),
			('PrefixSmallBlind', '&SmallBlind', 'PostfixSmallBlind'),
			)
		self.actionWidgets = []
		for actionPrefix, actionName, actionPostfix in actionSettings:
			editPrefix = TableCrabConfig.LineEdit(
					settingsKey='PokerStarsHandGrabber/handFornmatterHtmlTabular/%s' % actionPrefix,
					default=getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPrefix),
					maxLength=TableCrabConfig.MaxHandGrabberPrefix,
					parent=self,
					)
			labelAction = QtGui.QLabel('<i>' + actionName + '</i>', self)
			labelAction.setBuddy(editPrefix)
			if actionPostfix is not None:
				editPostfix = TableCrabConfig.LineEdit(
						settingsKey='PokerStarsHandGrabber/handFornmatterHtmlTabular/%s' % actionPostfix,
						default=getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPostfix),
						maxLength=TableCrabConfig.MaxHandGrabberPrefix,
						parent=self,
						)
			else:
				editPostfix = None
			self.actionWidgets.append( (editPrefix, labelAction, editPostfix, actionPrefix, actionPostfix) )

		self.spinMaxPlayerName = TableCrabConfig.SpinBox(
				settingsKey='PokerStarsHandGrabber/HandFornmatterHtmlTabular/MaxPlayerName',
				default=PokerStarsHandGrabber.HandFormatterHtmlTabular.MaxPlayerName,
				minimum=-1,
				maximum=999,
				parent=self
				)
		self.labelMaxPlayerName = QtGui.QLabel('Ma&x Player Name:', self)
		self.labelMaxPlayerName.setBuddy(self.spinMaxPlayerName)

		self.checkNoFloatingPoint = TableCrabConfig.CheckBox(
				'Floating &Point To Integer',
				settingsKey='PokerStarsHandGrabber/HandFornmatterHtmlTabular/NoFloatingPoint',
					default=False,
				parent=self
				)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		self.buttonRestoreDefault.setToolTip('Restore Default (Ctrl+R)')
		self.buttonRestoreDefault.clicked.connect(self.onRestoreDefault)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='Ctrl+R',
				slot=self.onRestoreDefault,
				)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='F1',
				slot=self.onHelp,
				)
		self.addAction(action)

		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)

		grid.addWidget(TableCrabConfig.HLine(self),0, 0, 1, 3)

		grid.addWidget(self.labelMaxPlayerName, 1, 0)
		grid.addWidget(self.spinMaxPlayerName, 1, 1)
		grid.addWidget(self.checkNoFloatingPoint, 2, 0, 1, 3)

		grid.addWidget(TableCrabConfig.HLine(self), 3, 0, 1, 3)

		grid.addWidget(self.labelPrefix, 4, 0)
		grid.addWidget(self.labelAction, 4, 1)
		grid.addWidget(self.labelPostfix, 4, 2)
		for i, (editPrefix, labelAction, editPostfix, _, _) in enumerate(self.actionWidgets):
			grid.addWidget(editPrefix, i+5, 0)
			grid.addWidget(labelAction, i+5, 1)
			if editPostfix is not None:
				grid.addWidget(editPostfix, i+5, 2)

		grid.addLayout(TableCrabConfig.VStretch(), i+6, 0)

		grid.addWidget(TableCrabConfig.HLine(self), i+7, 0, 1, 3)
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, i+8, 0, 1, 3)
		grid2.addWidget(self.buttonBox, 0, 0)

	def onRestoreDefault(self, *args):
		for editPrefix, _, editPostfix, actionPrefix, actionPostfix in self.actionWidgets:
			default = getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPrefix)
			editPrefix.setText(default)
			editPrefix.editingFinished.emit()
			if actionPostfix is not None:
				default = getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPostfix)
				editPostfix.setText(default)
				editPostfix.editingFinished.emit()

	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('settingsHand', parent=self)


class FrameSettingsHandSyleSheet(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.edit = TableCrabConfig.PlainTextEdit(
				settingsKey='PokerStarsHandGrabber/handFornmatterHtmlTabular/StyleSheet',
				default=PokerStarsHandGrabber.HandFormatterHtmlTabular.StyleSheet,
				maxChars=TableCrabConfig.MaxHandStyleSheet,
				)
		self.edit.maxCharsExceeded.connect(self.onMaxCharsExceeded)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		self.buttonRestoreDefault.setToolTip('Restore Default (Ctrl+R)')
		self.buttonRestoreDefault.clicked.connect(self.onRestoreDefault)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='Ctrl+R',
				slot=self.onRestoreDefault,
				)
		self.addAction(action)

		self.buttonOpen = QtGui.QPushButton('Open..', self)
		self.buttonOpen.setToolTip('Open style sheet (Ctrl+O)')
		self.buttonOpen.clicked.connect(self.onOpen)
		self.buttonBox.addButton(self.buttonOpen, self.buttonBox.ActionRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='Ctrl+O',
				slot=self.onOpen,
				)
		self.addAction(action)

		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonSave.setToolTip('Save style sheet (Ctrl+S)')
		self.buttonSave.clicked.connect(self.onSave)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ActionRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='Ctrl+S',
				slot=self.onSave,
				)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='F1',
				slot=self.onHelp,
				)
		self.addAction(action)

		self.layout()

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(TableCrabConfig.HLine(self), 0, 0)

		grid.addWidget(self.edit, 1, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 2, 0)
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 3, 0)
		grid2.addWidget(self.buttonBox, 0, 0)

	def onOpen(self, checked):
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Style Sheet..',
				fileFilters=('Style sheets (*.css)', 'All Files (*)'),
				settingsKey='Gui/Settings/HandStyleSheet/DialogOpen/State',
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = open(fileName, 'r')
			self.edit.setPlainText(fp.read() )
		except Exception, d:
			TableCrabConfig.msgWarning(self, 'Could Not Open Style sheet\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onSave(self, checked):
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Style Sheet..',
				fileFilters=('Stylesheets (*.css)', 'All Files (*)'),
				settingsKey='Gui/Settings/HandStyleSheet/DialogSave/State',
				)
		if fileName is None:
			return
		# default to '.css'
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not format:
			fileName = fileName + '.css'
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.edit.toPlainText() )
		except Exception, d:
			TableCrabConfig.msgWarning(self, 'Could Not Save Style sheet\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('settingsHandStyleSheet', parent=self)

	#TODO: resetting document jumps to top of widget. store/restore position would be nice
	def onRestoreDefault(self):
		self.edit.setPlainText(PokerStarsHandGrabber.HandFormatterHtmlTabular.StyleSheet)

	def onMaxCharsExceeded(self, flag):
		TableCrabConfig.globalObject.feedback.emit(self, ('Style sheet too big -- maximum Is %s chars' % TableCrabConfig.MaxHandStyleSheet) if flag else '')


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
		self.settingsGlobal = self.addSetting('Global', FrameSettingsGlobal(parent=self.stack), 'Shift+G', 'Global (Shift+G)')
		self.settingsPokerStars = self.addSetting('PokerStars', FrameSettingsPokerStars(parent=self.stack), 'Shift+P', 'PokerStars (Shift+P)')
		self.settingsHand = self.addSetting('Hand', FrameSettingsHand(parent=self.stack), 'Shift+H', 'Hand (Shift+H)')
		self.settingsHandStyleSheet = self.addSetting('Hand Style Sheet', FrameSettingsHandSyleSheet(parent=self.stack), 'Shift+S', 'Hand Style Sheet (Shift+S)')

		TableCrabConfig.globalObject.init.connect(self.onInit)
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSettingAlternatingRowColorsChanged)

		self.layout()

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.splitter, 0, 0)

	def addSetting(self, name, widget, shortcut, toolTip):
		item = QtGui.QListWidgetItem(name, self.listWidget)
		item.setToolTip(toolTip)
		self.listWidget.addItem(item)
		self.stack.addWidget(widget)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut=shortcut,
				slot=self.onSettingsShortcut,
				userData=item,
				)
		self.addAction(action)
		return widget

	def onSettingsShortcut(self):
		item = self.sender().userData
		self.listWidget.setCurrentItem(item)
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



