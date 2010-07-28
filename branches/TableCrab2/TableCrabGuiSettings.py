
import TableCrabConfig
from PyQt4 import QtCore, QtGui

import PSHandGrabber
import TableCrabGuiHelp

#**********************************************************************************************
#
#**********************************************************************************************

class FrameSettingsGlobal(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.labelGuiFont = QtGui.QLabel('Global Font:', self)
		self.buttonGuiFont = QtGui.QPushButton('..', self)
		TableCrabConfig.signalConnect(self.buttonGuiFont, self, 'clicked(bool)', self.onButtonGuiFontClicked)
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
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
			
		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		
		
		grid.addWidget(self.labelGuiFont, 0, 0)
		grid.addWidget(self.buttonGuiFont, 0, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 0, 2)
			
		grid.addWidget(self.labelZoomIncrement, 1, 0)
		grid.addWidget(self.spinZoomIncrement, 1, 1)
		grid.addLayout(TableCrabConfig.HStretch(), 1, 2)
			
		grid.addLayout(TableCrabConfig.VStretch(), 2, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 3, 0, 1, 3)
			
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 4, 0, 1, 3)
		grid2.addWidget(self.buttonBox, 0, 0)
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('SettingsGlobal', parent=self)
		
	def onButtonGuiFontClicked(self, checked):
		font, ok = QtGui.QFontDialog.getFont(QtGui.qApp.font(), self)
		if ok:
			QtGui.qApp.setFont(font)
			TableCrabConfig.settingsSetValue('Gui/Font', font.toString())


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
		TableCrabGuiHelp.dialogHelp('SettingsPokerStars', parent=self)
	

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
					default=getattr(PSHandGrabber.HandFormatterHtmlTabular, actionPrefix), 
					parent=self
					)
			labelAction = QtGui.QLabel(actionName, self)
			if actionPostfix is not None:
				editPostfix = TableCrabConfig.LineEdit(
						settingsKey='PsHandGrabber/handFornmatterHtmlTabular/%s' % actionPostfix, 
						default=getattr(PSHandGrabber.HandFormatterHtmlTabular, actionPostfix),  
						parent=self
						)
			else:
				editPostfix = None
			self.actionSettings.append( (editPrefix, labelAction, editPostfix) )
			
		self.labelMaxPlayerName = QtGui.QLabel('MaxPlayerName:', self)
		self.spinMaxPlayerName = TableCrabConfig.SpinBox(
				settingsKey='PsHandGrabber/HandFornmatterHtmlTabular/MaxPlayerName', 
				default=PSHandGrabber.HandFormatterHtmlTabular.MaxPlayerName, 
				minimum=-1, 
				maximum=999, 
				parent=self
				)
		self.labelGrabTimeout = QtGui.QLabel('GrabTimeout:', self)
		self.spinGrabTimeout = TableCrabConfig.DoubleSpinBox(
				settingsKey='PsHandGrabber/GrabTimeout', 
				default=PSHandGrabber.HandGrabber.GrabTimeout,
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
		TableCrabGuiHelp.dialogHelp('SettingsHand', parent=self)
		

class FrameSettingsHandCss(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.editCss = TableCrabConfig.PlainTextEdit(
				settingsKey='PsHandGrabber/handFornmatterHtmlTabular/Css', 
				default=PSHandGrabber.HandFormatterHtmlTabular.Css
				)
		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		TableCrabConfig.signalConnect(self.buttonRestoreDefault, self, 'clicked(bool)', self.onButtonRestoreDefaultClicked)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)
		
		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.editCss, 0, 0)
		
		grid.addWidget(TableCrabConfig.HLine(self), 1, 0)
		grid2 = TableCrabConfig.GridBox()
		grid.addLayout(grid2, 2, 0)
		grid2.addWidget(self.buttonBox, 0, 0)
			
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('SettingsHandCss', parent=self)
				
	#TODO: resetting document jumps to top of widget. store/restore position would be nice
	def onButtonRestoreDefaultClicked(self):
		self.editCss.setPlainText(PSHandGrabber.HandFormatterHtmlTabular.Css)


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


#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	g = TableCrabConfig.MainWindow()
	g.setCentralWidget(FrameSettings(g))
	g.start()
	
	

