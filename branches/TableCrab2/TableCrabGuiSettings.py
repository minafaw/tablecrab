
import TableCrabConfig
import PokerStarsHandGrabber
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************

class FrameSettingsGlobal(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.labelBackup = QtGui.QLabel('Backup TableCrab:', self)
		self.buttonBackup = QtGui.QPushButton('..', self)
		TableCrabConfig.signalConnect(self.buttonBackup, self, 'clicked(bool)', self.onButtonBackupClicked)
		
		self.labelGuiStyle = QtGui.QLabel('Global Style:', self)
		self.comboGuiStyle = TableCrabConfig.ComboBox(
				[style for style in QtGui.QStyleFactory().keys()] , 
				settingsKey='Gui/Style', 
				default=QtGui.qApp.style().objectName(),	#HACK:  not documented for getting style name but the lights are on. so i assume it works
				failsave=True,
				parent=self,
				)
		self.labelGuiFont = QtGui.QLabel('Global Font:', self)
		self.buttonGuiFont = QtGui.QPushButton('..', self)
		TableCrabConfig.signalConnect(self.buttonGuiFont, self, 'clicked(bool)', self.onButtonGuiFontClicked)
		
		TableCrabConfig.signalConnect(self.comboGuiStyle, self, 'currentIndexChanged(QString)', self.onComboGuiStyleCurrentIndexChanged)
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
		
		self.checkAlternatingRowColors = TableCrabConfig.CheckBox('Use Alternating Row Colors', default=False, settingsKey='Gui/AlternatingRowColors', parent=self)
		TableCrabConfig.signalConnect(self.checkAlternatingRowColors, self, 'stateChanged(int)', self.onAlternatingRowColorsChanged)
		self.checkChildItemIndicators = TableCrabConfig.CheckBox('Show Child Item Indicators', default=True, settingsKey='Gui/ChildItemIndicators', parent=self)
		TableCrabConfig.signalConnect(self.checkChildItemIndicators, self, 'stateChanged(int)', self.onChildItemIndicatorsChanged)
		
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
			
		self.layout()
	
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		
		grid.addWidget(self.labelBackup, 0, 0)
		grid.addWidget(self.buttonBackup, 0, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 0, 2)
		
		grid.addWidget(self.labelGuiStyle, 1, 0)
		grid.addWidget(self.comboGuiStyle, 1, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 1, 2)
		
		grid.addWidget(self.labelGuiFont, 2, 0)
		grid.addWidget(self.buttonGuiFont, 2, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 2, 2)
				
		grid.addWidget(self.labelZoomIncrement, 3, 0)
		grid.addWidget(self.spinZoomIncrement, 3, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 3, 2)
			
		grid.addWidget(self.checkAlternatingRowColors, 4, 0)
		grid.addWidget(self.checkChildItemIndicators, 5, 0)
		
		grid.addLayout(TableCrabConfig.VStretch(), 6, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 7, 0, 1, 3)
			
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 8, 0, 1, 3)
		grid2.addWidget(self.buttonBox, 0, 0)
		
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
		
	def onButtonGuiFontClicked(self, checked):
		font, ok = QtGui.QFontDialog.getFont(QtGui.qApp.font(), self)
		if ok:
			QtGui.qApp.setFont(font)
			#TODO: for some reason font changes are reflected when we run this module but not when we run from TableCrabGui.py
			#				setting style explicitely fixes this. hack fro now 
			QtGui.qApp.setStyle(QtGui.QStyleFactory.create( TableCrabConfig.settingsValue('Gui/Style', '').toString() ))
			TableCrabConfig.settingsSetValue('Gui/Font', font.toString())
	
	def onComboGuiStyleCurrentIndexChanged(self, qString):
		QtGui.qApp.setStyle(QtGui.QStyleFactory.create(qString))
		
	def onAlternatingRowColorsChanged(self, state):
		TableCrabConfig.signalEmit(None, 'settingAlternatingRowColorsChanged(bool)', state == QtCore.Qt.Checked)
	
	def onChildItemIndicatorsChanged(self, state):
		TableCrabConfig.signalEmit(None, 'settingChildItemIndicatorsChanged(bool)', state == QtCore.Qt.Checked)

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
		
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		
		
		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.checkAutoClosePopupNews, 0, 0)
		grid.addWidget(self.checkAutoCloseTourneyRegistrationBoxes, 1, 0) 
		grid.addWidget(self.checkAutoCloseTableMessageBoxes, 2, 0)
		grid.addWidget(self.checkAutoLogIn, 3, 0)
		grid.addLayout(TableCrabConfig.VStretch(), 4, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 5, 0)
			
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 6, 0)
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
			('PrefixRaise', 'Raise', 'PostfixRaise'),
			('PrefixCall', 'Call', 'PostfixCall'),
			('PrefixAnte', 'Ante', 'PostfixAnte'),
			('PrefixSmallBlind', 'SmallBlind', 'PostfixSmallBlind'),
			('PrefixBigBlind', 'BigBlind', 'PostfixBigBlind'),
			('PrefixCheck', 'Check', None),
			('PrefixFold', 'Fold', None),
			)
		self.actionSettings = []
		for actionPrefix, actionName, actionPostfix in actionSettings:
			editPrefix = TableCrabConfig.LineEdit(
					settingsKey='PsHandGrabber/handFornmatterHtmlTabular/%s' % actionPrefix, 
					default=getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPrefix), 
					parent=self
					)
			labelAction = QtGui.QLabel(actionName, self)
			if actionPostfix is not None:
				editPostfix = TableCrabConfig.LineEdit(
						settingsKey='PsHandGrabber/handFornmatterHtmlTabular/%s' % actionPostfix, 
						default=getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, actionPostfix),  
						parent=self
						)
			else:
				editPostfix = None
			self.actionSettings.append( (editPrefix, labelAction, editPostfix) )
			
		self.labelMaxPlayerName = QtGui.QLabel('MaxPlayerName:', self)
		self.spinMaxPlayerName = TableCrabConfig.SpinBox(
				settingsKey='PsHandGrabber/HandFornmatterHtmlTabular/MaxPlayerName', 
				default=PokerStarsHandGrabber.HandFormatterHtmlTabular.MaxPlayerName, 
				minimum=-1, 
				maximum=999, 
				parent=self
				)
		self.labelGrabTimeout = QtGui.QLabel('GrabTimeout:', self)
		self.spinGrabTimeout = TableCrabConfig.DoubleSpinBox(
				settingsKey='PsHandGrabber/GrabTimeout', 
				default=PokerStarsHandGrabber.HandGrabber.GrabTimeout,
				minimum=0.2, 
				maximum=4.9,
				precision=1,
				step=0.1,
				parent=self
				)
		
		self.checkNoFloatingPoint = TableCrabConfig.CheckBox(
				'Floating Point To Integer', 
				settingsKey='PsHandGrabber/HandFornmatterHtmlTabular/NoFloatingPoint', 
					default=False, 
				parent=self
				)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
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
		grid.addWidget(self.labelGrabTimeout, i+3, 0)
		grid.addWidget(self.spinGrabTimeout, i+3, 1)
		grid.addWidget(self.checkNoFloatingPoint, i+4, 0)
		
		grid.addLayout(TableCrabConfig.VStretch(), i+5, 0)
		
		grid.addWidget(TableCrabConfig.HLine(self), i+6, 0, 1, 3)
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, i+7, 0, 1, 3)
		grid2.addWidget(self.buttonBox, 0, 0)
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('settingsHand', parent=self)
		

class FrameSettingsHandCss(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.edit = TableCrabConfig.PlainTextEdit(
				settingsKey='PsHandGrabber/handFornmatterHtmlTabular/Css', 
				default=PokerStarsHandGrabber.HandFormatterHtmlTabular.Css
				)
		
		self.buttonBox = QtGui.QDialogButtonBox(self)
		
		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		TableCrabConfig.signalConnect(self.buttonRestoreDefault, self, 'clicked(bool)', self.onButtonRestoreDefaultClicked)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)
		
		self.buttonOpen = QtGui.QPushButton('Open..', self)
		TableCrabConfig.signalConnect(self.buttonOpen, self, 'clicked(bool)', self.onButtonOpenClicked)
		self.buttonBox.addButton(self.buttonOpen, self.buttonBox.ActionRole)
		
		self.buttonSave = QtGui.QPushButton('Save..', self)
		TableCrabConfig.signalConnect(self.buttonSave, self, 'clicked(bool)', self.onButtonSaveClicked)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ActionRole)
		
		
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
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
				title='Open Stylesheet..',
				fileFilters=('Stylesheets (*.css)', 'All Files (*)'), 
				settingsKey='Gui/Settings/HandCss/DialogOpen/State',
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = open(fileName, 'r')
			self.edit.setPlainText(fp.read() )
		except Exception, d:
			TableCrabConfig.msgWarning(self, 'Could Not Open Stylesheet\n\n%s' % d)
		finally: 
			if fp is not None: fp.close()
			
	def onButtonSaveClicked(self, checked):
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Stylesheet..',
				fileFilters=('Stylesheets (*.css)', 'All Files (*)'), 
				settingsKey='Gui/Settings/HandCss/DialogSave/State',
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
			TableCrabConfig.msgWarning(self, 'Could Not Save Stylesheet\n\n%s' % d)
		finally: 
			if fp is not None: fp.close()
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('settingsHandCss', parent=self)
				
	#TODO: resetting document jumps to top of widget. store/restore position would be nice
	def onButtonRestoreDefaultClicked(self):
		self.edit.setPlainText(PokerStarsHandGrabber.HandFormatterHtmlTabular.Css)


class FrameSettings(QtGui.QFrame):
	
	class ListWidget(QtGui.QListWidget):
		def __init__(self, parent=None):
			QtGui.QListWidget.__init__(self, parent)
		def keyReleaseEvent(self, event):
			if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
				event.accept()
				item = self.currentItem()
				if item is not None:
					TableCrabConfig.signalEmit(self, 'itemPressed(QListWidgetItem*)', item)
				return
			return QtGui.QListWidget.keyReleaseEvent(self, event)
		
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.splitter = QtGui.QSplitter(self)
		self.listWidget = self.ListWidget(self)
		self.stack = QtGui.QStackedWidget(self)
		
		self.splitter.addWidget(self.listWidget)
		self.splitter.addWidget(self.stack)
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
		TableCrabConfig.signalConnect(self.listWidget, self, 'itemPressed(QListWidgetItem*)', self.onSettingSelected)
		
		self.listWidget.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		TableCrabConfig.signalConnect(None, self, 'settingAlternatingRowColorsChanged(bool)', self.onSettingAlternatingRowColorsChanged)	
		
		#
		self.addSetting('Global', FrameSettingsGlobal(parent=self.stack) )
		self.addSetting('PokerStars', FrameSettingsPokerStars(parent=self.stack) )
		self.addSetting('Hand', FrameSettingsHand(parent=self.stack) )
		self.addSetting('Hand-Css', FrameSettingsHandCss(parent=self.stack) )
			
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
	
	

