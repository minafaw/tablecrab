
import Tc2Config
import Tc2GuiHelp
import Tc2SitePokerStarsHandGrabber
from PyQt4 import QtCore, QtGui
import operator

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	#TODO: typo in settings key. should be "Formatter" not "Fornmatter"
	SettingsKeyBase = 'PokerStarsHandGrabber/HandFornmatterHtmlTabular'
	SettingsKeyStyleSheet = SettingsKeyBase + '/StyleSheet'
	SettingsKeyMaxPlayerName = SettingsKeyBase + '/MaxPlayerName'
	SettingsKeyNoFloatingPoint = SettingsKeyBase + '/NoFloatingPoint'
	SettingsKeyPrefixFold = SettingsKeyBase + '/PrefixFold'
	SettingsKeyPrefixCheck = SettingsKeyBase + '/PrefixCheck'
	SettingsKeyPrefixBet = SettingsKeyBase + '/PrefixBet'
	SettingsKeyPostfixBet = SettingsKeyBase + '/PostfixBet'
	SettingsKeyPrefixRaise = SettingsKeyBase + '/PrefixRaise'
	SettingsKeyPostfixRaise = SettingsKeyBase + '/PostfixRaise'
	SettingsKeyPrefixCall = SettingsKeyBase + '/PrefixCall'
	SettingsKeyPostfixCall = SettingsKeyBase + '/PotfixCall'
	SettingsKeyPrefixAnte = SettingsKeyBase + '/PrefixAnte'
	SettingsKeyPostfixAnte = SettingsKeyBase + '/PostfixAnte'
	SettingsKeyPrefixBigBlind = SettingsKeyBase + '/PrefixBigBlind'
	SettingsKeyPostfixBigBlind = SettingsKeyBase + '/PostfixBigBlind'
	SettingsKeyPrefixSmallBlind = SettingsKeyBase + '/PrefixSmallBlind'
	SettingsKeyPostfixSmallBlind = SettingsKeyBase + '/PostfixSmallBlind'

	SettingsKeySideBarPosition = 'Gui/HandViewer/SideBarPosition'

	actionPrefixChanged = QtCore.pyqtSignal(QtCore.QString)
	actionPostfixChanged = QtCore.pyqtSignal(QtCore.QString)
	maxPlayerNameChanged = QtCore.pyqtSignal(int)
	noFloatingPoint = QtCore.pyqtSignal(bool)
	sideBarPositionChanged = QtCore.pyqtSignal(QtCore.QString)

	ActionPrefixes = (
			('Bet', SettingsKeyPrefixBet, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixBet, SettingsKeyPostfixBet, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PostfixBet),
			('Call', SettingsKeyPrefixCall, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixCall, SettingsKeyPostfixCall, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PostfixCall),
			('Check', SettingsKeyPrefixCheck, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixCheck, None, None),
			('Fold', SettingsKeyPrefixFold, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixFold, None, None),
			('Raise', SettingsKeyPrefixRaise, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixRaise, SettingsKeyPostfixRaise, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PostfixRaise),
			('Ante', SettingsKeyPrefixAnte, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixAnte, SettingsKeyPostfixAnte, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PostfixAnte),
			('BigBlind', SettingsKeyPrefixBigBlind, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixBigBlind, SettingsKeyPostfixBigBlind, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PostfixBigBlind),
			('SmallBlind', SettingsKeyPrefixSmallBlind, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PrefixSmallBlind, SettingsKeyPostfixSmallBlind, Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.PostfixSmallBlind),
			)

	class ActionLineEdit(QtGui.QLineEdit):
		def __init__(self, parent=None, actionName='', text='', settingsKey=None, default=None):
			QtGui.QLineEdit.__init__(self, text, parent)
			self.settingsKey = settingsKey
			self.default = default
			self.actionName = actionName

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.labelPrefix = QtGui.QLabel('<i>Prefix</i>', self)
		self.labelAction = QtGui.QLabel('<i>Action</i>', self)
		self.labelPostfix = QtGui.QLabel('<i>Postfix</i>', self)

		self.actionWidgets = {}
		for i,(actionName, settingsKeyPrefix, defaultPrefix, settingsKeyPostfix, defaultPostfix) in enumerate(self.ActionPrefixes):
			editPrefix = self.ActionLineEdit(parent=self, actionName=actionName, settingsKey= settingsKeyPrefix, default=defaultPrefix)
			editPrefix.setMaxLength(Tc2Config.MaxHandGrabberPrefix)
			labelAction = QtGui.QLabel('<i>' + actionName + '</i>', self)
			labelAction.setBuddy(editPrefix)
			if settingsKeyPostfix is not None:
				editPostfix =  self.ActionLineEdit(parent=self, actionName=actionName, settingsKey= settingsKeyPostfix, default=defaultPostfix)
				editPostfix.setMaxLength(Tc2Config.MaxHandGrabberPrefix)
			else:
				editPostfix = None
			self.actionWidgets[actionName] = {'EditPrefix': editPrefix, 'LabelAction': labelAction, 'EditPostfix': editPostfix, 'no': i}

		self.comboSideBarPosition = QtGui.QComboBox(self)
		self.comboSideBarPosition.addItems(Tc2Config.HandViewerSideBarPositions)
		self.labelSideBarPosition = QtGui.QLabel('&Side bar position:', self)
		self.labelSideBarPosition.setBuddy(self.comboSideBarPosition)

		self.spinMaxPlayerName = QtGui.QSpinBox(self)
		self.spinMaxPlayerName.setRange(Tc2Config.HandViewerMaxPlayerNameMin, Tc2Config.HandViewerMaxPlayerNameMax)
		self.labelMaxPlayerName = QtGui.QLabel('Ma&x Player Name:', self)
		self.labelMaxPlayerName.setBuddy(self.spinMaxPlayerName)

		self.checkNoFloatingPoint = QtGui.QCheckBox('Floating &Point To Integer', self)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		self.buttonRestoreDefault.setToolTip('Restore Default (Ctrl+R)')
		self.buttonRestoreDefault.clicked.connect(self.onRestoreDefault)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+R') )
		action.triggered.connect(self.onRestoreDefault)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		Tc2Config.globalObject.initSettings.connect(self.onInitSettings)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelSideBarPosition).col(self.comboSideBarPosition)
		grid.row()
		grid.col(self.labelMaxPlayerName).col(self.spinMaxPlayerName)
		grid.row()
		grid.col(self.checkNoFloatingPoint, colspan=3)
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelPrefix).col(self.labelAction).col(self.labelPostfix)

		actions = sorted(self.actionWidgets.values(), key=operator.itemgetter('no'))
		for data in actions:
			grid.row()
			grid.col(data['EditPrefix']).col(data['LabelAction'])
			if data['EditPostfix'] is not None:
				grid.col(data['EditPostfix'])
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onRestoreDefault(self, *args):
		for data in self.actionWidgets.values():
			editPrefix = data['EditPrefix']
			editPrefix.setText(editPrefix.default)
			editPrefix.editingFinished.emit()
			editPostfix = data['EditPostfix']
			if editPostfix is not None:
				editPostfix.setText(editPostfix.default)
				editPostfix.editingFinished.emit()

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsHandViewer', parent=self)

	def actionPrefix(self, actionName):
		return self.actionWidgets[actionName]['EditPrefix'].text()

	def actionPostfix(self, actionName):
		edit = self.actionWidgets[actionName]['EditPostfix']
		if edit is None:
			raise ValueError('no postfix for action: %s' % actionName)
		return edit.text()

	def setActionPrefix(self, actionName, value):
		edit = self.actionWidgets[actionName]['EditPrefix']
		Tc2Config.settingsSetValue(edit.settingsKey, value)
		self.actionPrefixChanged.emit(actionName)

	def setActionPostfix(self, actionName, value):
		edit = self.actionWidgets[actionName]['EditPostfix']
		if edit is None:
			raise ValueError('no postfix for action: %s' % actionName)
		Tc2Config.settingsSetValue(edit.settingsKey, value)
		self.actionPostfixChanged.emit(actionName)

	def maxPlayerName(self):
		return self.spinMaxPlayerName.value()

	def setMaxPlayerName(self, value):
		Tc2Config.settingsSetValue(Tc2SitePokerStarsHandGrabber.HandFormatterHtmlTabular.SettingsKeyMaxPlayerName, value)
		self.maxPlayerNameChanged.emit(value)

	def noFloatingPoint(self):
		return self.checkNoFloatingPoint.checkState() == QtCore.Qt.Checked

	def setNoFloatingPoint(self, value):
		Tc2Config.settingsSetValue(c2HandGrabberPokerStars.HandFormatterHtmlTabular.SettingsKeyNoFloatingPoint, value)
		self.noFloatingPoint.emit(value)

	def sideBarPosition(self):
		return self.comboSideBarPosition.currentText()

	def setSideBarPosition(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeySideBarPosition, value)
		self.sideBarPositionChanged.emit(value)

	def onInitSettings(self):
		self.layout()

		value = Tc2Config.settingsValue(self.SettingsKeySideBarPosition, '').toString()
		if value not in Tc2Config.HandViewerSideBarPositions:
			value = Tc2Config.HandViewerSideBarPositionDefault
		self.comboSideBarPosition.setCurrentIndex( self.comboSideBarPosition.findText(value, QtCore.Qt.MatchExactly) )
		#NOTE: pySlot decorator does not work as expected so we have to connect slot the old fashioned way
		self.connect(self.comboSideBarPosition, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setSideBarPosition)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyMaxPlayerName, Tc2Config.HandViewerMaxPlayerNameDefault).toInt()
		if not ok or value < Tc2Config.HandViewerMaxPlayerNameMin or value > Tc2Config.HandViewerMaxPlayerNameMax:
			value = Tc2Config.WebView.HandViewerMaxPlayerNameDefault
		self.spinMaxPlayerName.setValue(value)
		self.spinMaxPlayerName.valueChanged.connect(self.setMaxPlayerName)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyNoFloatingPoint, False).toBool() else QtCore.Qt.Unchecked
		self.checkNoFloatingPoint.setCheckState(value)
		self.checkNoFloatingPoint.stateChanged.connect(
				lambda value, self=self: self.setNoFloatingPoint(self.checkNoFloatingPoint.checkState() == QtCore.Qt.Checked)
				)

		for data in self.actionWidgets.values():
			editPrefix = data['EditPrefix']
			text = Tc2Config.settingsValue(editPrefix.settingsKey, editPrefix.default).toString()
			editPrefix.setText(text)
			editPrefix.textChanged.connect(
					lambda text, edit=editPrefix: self.setActionPrefix(edit.actionName, text)
					)
			editPostfix = data['EditPostfix']
			if editPostfix is not None:
				text = Tc2Config.settingsValue(editPostfix.settingsKey, editPostfix.default).toString()
				editPostfix.setText(text)
				editPostfix.textChanged.connect(
					lambda text, edit=editPostfix: self.setActionPostfix(edit.actionName, text)
					)

		Tc2Config.globalObject.objectCreatedSettingsHandViewer.emit(self)




