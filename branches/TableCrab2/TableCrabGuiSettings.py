
#TODO: have to find a better waay to present prefix | postfix in settings hand
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

		self.labelBackup = QtGui.QLabel('Backup TableCrab:', self)
		self.buttonBackup = QtGui.QPushButton('..', self)
		self.buttonBackup.clicked.connect(self.onButtonBackupClicked)

		self.labelGuiStyle = QtGui.QLabel('Global Style:', self)
		self.comboGuiStyle = TableCrabConfig.ComboBox(
				[style for style in QtGui.QStyleFactory().keys()] ,
				settingsKey='Gui/Style',
				default=QtGui.qApp.style().objectName(),	#HACK:  not documented for getting style name but the lights are on. so i assume it works
				failsave=True,
				parent=self,
				)
		self.comboGuiStyle.currentIndexChanged.connect(self.onComboGuiStyleCurrentIndexChanged)

		self.labelFont = QtGui.QLabel('Global Font:', self)
		self.buttonFont = QtGui.QPushButton('..', self)
		self.buttonFont.clicked.connect(self.onButtonFontClicked)

		self.labelFixedFont = QtGui.QLabel('Fixed Font:', self)
		self.buttonFixedFont = QtGui.QPushButton('..', self)
		self.buttonFixedFont.clicked.connect(self.onButtonFixedFontClicked)

		self.labelZoomIncrement = QtGui.QLabel('Zoom Increment:', self)
		self.spinZoomIncrement = TableCrabConfig.DoubleSpinBox(
				settingsKey='Gui/WebView/ZoomIncrement',
				default=0.1,
				minimum=0.1,
				maximum=2.99,
				precision=1,
				step=0.1,
				parent=self
				)

		self.checkAlternatingRowColors = TableCrabConfig.CheckBox('Show Alternating Row Colors', default=False, settingsKey='Gui/AlternatingRowColors', parent=self)
		self.checkAlternatingRowColors.stateChanged.connect(self.onAlternatingRowColorsChanged)
		self.checkChildItemIndicators = TableCrabConfig.CheckBox('Show Child Item Indicators', default=True, settingsKey='Gui/ChildItemIndicators', parent=self)
		self.checkChildItemIndicators.stateChanged.connect(self.onChildItemIndicatorsChanged)
		self.checkRestoreMousePosition = TableCrabConfig.CheckBox('Restore Mouse Position', default=False, settingsKey='RestoreMousePosition', parent=self)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.clicked.connect(self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		# set all aplplication fonts
		self.setFont()
		self.setFixedFont()
		self.layout()


	def layout(self):
		grid = TableCrabConfig.GridBox(self)

		grid.addWidget(self.labelBackup, 0, 0)
		grid.addWidget(self.buttonBackup, 0, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 0, 2)

		grid.addWidget(self.labelGuiStyle, 1, 0)
		grid.addWidget(self.comboGuiStyle, 1, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 1, 2)

		grid.addWidget(self.labelFont, 2, 0)
		grid.addWidget(self.buttonFont, 2, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 2, 2)

		grid.addWidget(self.labelFixedFont, 3, 0)
		grid.addWidget(self.buttonFixedFont, 3, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 3, 2)

		grid.addWidget(self.labelZoomIncrement, 4, 0)
		grid.addWidget(self.spinZoomIncrement, 4, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 4, 2)

		grid.addWidget(self.checkAlternatingRowColors, 5, 0)
		grid.addWidget(self.checkChildItemIndicators, 6, 0)
		grid.addWidget(self.checkRestoreMousePosition, 7, 0)

		grid.addLayout(TableCrabConfig.VStretch(), 8, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 9, 0, 1, 3)

		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 10, 0, 1, 3)
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

	def onButtonHelpClicked(self, checked):
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


class FrameSettingsPokerStars(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.checkAutoClosePopupNews = TableCrabConfig.CheckBox(
				'Auto-Close Popup News',
				settingsKey='PokerStars/AutoClosePopupNews',
				default=False
				)
		self.checkAutoCloseTourneyRegistrationBoxes = TableCrabConfig.CheckBox(
				'Auto-Close Tourney Registration Boxes',
				settingsKey='PokerStars/AutoCloseTourneyRegistrationBoxes',
				default=False
				)
		self.checkAutoCloseTableMessageBoxes = TableCrabConfig.CheckBox(
				'Auto-Close Table Message Boxes',
				settingsKey='PokerStars/AutoCloseTableMessageBoxes',
				default=False
				)
		self.checkAutoLogIn = TableCrabConfig.CheckBox(
				'Auto-Close Log In Box',
				settingsKey='PokerStars/AutoCloseLogin',
				default=False
				)
		self.checkMoveMouseToActiveTable = TableCrabConfig.CheckBox(
				'Move Mouse To Active table',
				settingsKey='PokerStars/MoveMouseToActiveTable',
				default=False
				)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.clicked.connect(self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.checkAutoClosePopupNews, 0, 0)
		grid.addWidget(self.checkAutoCloseTourneyRegistrationBoxes, 1, 0)
		grid.addWidget(self.checkAutoCloseTableMessageBoxes, 2, 0)
		grid.addWidget(self.checkAutoLogIn, 3, 0)
		grid.addWidget(self.checkMoveMouseToActiveTable, 4, 0)


		grid.addLayout(TableCrabConfig.VStretch(), 5, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 6, 0)

		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 7, 0)
		grid2.addWidget(self.buttonBox, 0, 0)

	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('settingsPokerStars', parent=self)


class FrameSettingsHand(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.labelPrefix = QtGui.QLabel('Prefix', self)
		self.labelAction = QtGui.QLabel('Action', self)
		self.labelPostfix = QtGui.QLabel('Postfix', self)

		actionSettings = (
			('PrefixBet', 'Bet', 'PostfixBet'),
			('PrefixCall', 'Call', 'PostfixCall'),
			('PrefixCheck', 'Check', None),
			('PrefixFold', 'Fold', None),
			('PrefixRaise', 'Raise', 'PostfixRaise'),
			('PrefixAnte', 'Ante', 'PostfixAnte'),
			('PrefixBigBlind', 'BigBlind', 'PostfixBigBlind'),
			('PrefixSmallBlind', 'SmallBlind', 'PostfixSmallBlind'),
			)
		self.actionSettings = []
		for actionPrefix, actionName, actionPostfix in actionSettings:
			editPrefix = TableCrabConfig.LineEdit(
					settingsKey='PokerStarsHandGrabber/handFornmatterHtmlTabular/%s' % actionPrefix,
					default=getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPrefix),
					parent=self
					)
			editPrefix.setMaxLength(TableCrabConfig.MaxHandGrabberPrefix)
			labelAction = QtGui.QLabel(actionName, self)
			if actionPostfix is not None:
				editPostfix = TableCrabConfig.LineEdit(
						settingsKey='PokerStarsHandGrabber/handFornmatterHtmlTabular/%s' % actionPostfix,
						default=getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPostfix),
						parent=self
						)
				editPostfix.setMaxLength(TableCrabConfig.MaxHandGrabberPrefix)
			else:
				editPostfix = None
			self.actionSettings.append( (editPrefix, labelAction, editPostfix) )

		self.labelMaxPlayerName = QtGui.QLabel('Max Player Name:', self)
		self.spinMaxPlayerName = TableCrabConfig.SpinBox(
				settingsKey='PokerStarsHandGrabber/HandFornmatterHtmlTabular/MaxPlayerName',
				default=PokerStarsHandGrabber.HandFormatterHtmlTabular.MaxPlayerName,
				minimum=-1,
				maximum=999,
				parent=self
				)
		self.checkNoFloatingPoint = TableCrabConfig.CheckBox(
				'Floating Point To Integer',
				settingsKey='PokerStarsHandGrabber/HandFornmatterHtmlTabular/NoFloatingPoint',
					default=False,
				parent=self
				)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.clicked.connect(self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)

		grid.addWidget(self.labelPrefix, 0, 0)
		grid.addWidget(self.labelAction, 0, 1)
		grid.addWidget(self.labelPostfix, 0, 2)
		for i, (editPrefix, labelAction, editPostfix) in enumerate(self.actionSettings):
			grid.addWidget(editPrefix, i+1, 0)
			grid.addWidget(labelAction, i+1, 1)
			if editPostfix is not None:
				grid.addWidget(editPostfix, i+1, 2)
		grid.addWidget(self.labelMaxPlayerName, i+2, 0)
		grid.addWidget(self.spinMaxPlayerName, i+2, 1)
		grid.addWidget(self.checkNoFloatingPoint, i+3, 0, 1, 2)

		grid.addLayout(TableCrabConfig.VStretch(), i+4, 0)

		grid.addWidget(TableCrabConfig.HLine(self), i+5, 0, 1, 3)
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, i+7, 0, 1, 3)
		grid2.addWidget(self.buttonBox, 0, 0)

	def onButtonHelpClicked(self, checked):
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
		self.buttonRestoreDefault.clicked.connect(self.onButtonRestoreDefaultClicked)
		self.buttonRestoreDefault.setToolTip('Restores the default style sheet')
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)

		self.buttonOpen = QtGui.QPushButton('Open..', self)
		self.buttonOpen.setToolTip('Loads a style sheet from disk')
		self.buttonOpen.clicked.connect(self.onButtonOpenClicked)
		self.buttonBox.addButton(self.buttonOpen, self.buttonBox.ActionRole)

		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonSave.setToolTip('Saves the style sheet to disk')
		self.buttonSave.clicked.connect(self.onButtonSaveClicked)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ActionRole)


		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.clicked.connect(self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)


		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.edit, 0, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 1, 0)
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 2, 0)
		grid2.addWidget(self.buttonBox, 0, 0)

	def onButtonOpenClicked(self, checked):
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

	def onButtonSaveClicked(self, checked):
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

	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('settingsHandStyleSheet', parent=self)

	#TODO: resetting document jumps to top of widget. store/restore position would be nice
	def onButtonRestoreDefaultClicked(self):
		self.edit.setPlainText(PokerStarsHandGrabber.HandFormatterHtmlTabular.StyleSheet)

	def onMaxCharsExceeded(self, flag):
		TableCrabConfig.globalObject.feedback.emit(self, ('Style sheet too big -- maximum Is %s chars' % TableCrabConfig.MaxHandStyleSheet) if flag else '')


class FrameSettings(QtGui.QFrame):

	class ListWidget(QtGui.QListWidget):
		def __init__(self, parent=None):
			QtGui.QListWidget.__init__(self, parent)
		def keyReleaseEvent(self, event):
			if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
				event.accept()
				item = self.currentItem()
				if item is not None:
					self.itemPressed.emit(item)
				return
			return QtGui.QListWidget.keyReleaseEvent(self, event)

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.listWidget = self.ListWidget(self)
		self.listWidget.itemPressed.connect(self.onSettingSelected)
		self.listWidget.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )

		self.stack = QtGui.QStackedWidget(self)

		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.listWidget)
		self.splitter.addWidget(self.stack)

		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSettingAlternatingRowColorsChanged)

		#
		self.addSetting('Global', FrameSettingsGlobal(parent=self.stack) )
		self.addSetting('PokerStars', FrameSettingsPokerStars(parent=self.stack) )
		self.addSetting('Hand', FrameSettingsHand(parent=self.stack) )
		self.addSetting('Hand Style Sheet', FrameSettingsHandSyleSheet(parent=self.stack) )

		self.layout()
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Settings/SplitterState', QtCore.QByteArray()).toByteArray() )
		self.listWidget.setCurrentRow( TableCrabConfig.settingsValue('Gui/Settings/CurrentIndex', 0).toInt()[0] )
		self.onSettingSelected(self.listWidget.currentItem())

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.splitter, 0, 0)

	def addSetting(self, name, widget):
		self.listWidget.addItem(QtGui.QListWidgetItem(name, self.listWidget))
		self.stack.addWidget(widget)

	def onSettingSelected(self, item):
		settings = self.stack.currentWidget()
		self.stack.setCurrentIndex(self.listWidget.row(item))

	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Settings/SplitterState', self.splitter.saveState())
		TableCrabConfig.settingsSetValue('Gui/Settings/CurrentIndex', self.stack.currentIndex())

	def onSettingAlternatingRowColorsChanged(self, flag):
		self.listWidget.setAlternatingRowColors(flag)


#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	import TableCrabMainWindow
	g = TableCrabMainWindow.MainWindow()
	g.setCentralWidget(FrameSettings(g))
	g.start()

