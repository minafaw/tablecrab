
import Tc2Config
import Tc2GuiHelp
import Tc2HandTypes
from PyQt4 import QtCore, QtGui
import operator

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	#TODO: typo in settings key. should be "Formatter" not "Fornmatter"
	SettingsKeyBase = 'PokerStarsHandGrabber/HandFornmatterHtmlTabular'
	SettingsKeyDeckStyle = SettingsKeyBase + '/DeckStyle'
	SettingsKeyMaxPlayerName = SettingsKeyBase + '/MaxPlayerName'
	SettingsKeyNoFloatingPoint = SettingsKeyBase + '/NoFloatingPoint'

	SettingsKeySideBarPosition = 'Gui/HandViewer/SideBarPosition'


	sideBarPositionChanged = QtCore.pyqtSignal(QtCore.QString)

	HandActionsMapping = {	# action --> (name, settingsKeyPrefix, settingsKeyPostfix)
			Tc2HandTypes.PokerHand.Action.TypeCheck: ('Check', SettingsKeyBase + '/PrefixCheck', None),
			Tc2HandTypes.PokerHand.Action.TypeFold: ('Fold', SettingsKeyBase + '/PrefixFold', None),
			Tc2HandTypes.PokerHand.Action.TypeBet: ('Bet', SettingsKeyBase + '/PrefixBet', SettingsKeyBase + '/PostfixBet'),
			Tc2HandTypes.PokerHand.Action.TypeCall: ('Call', SettingsKeyBase + '/PrefixCall', SettingsKeyBase + '/PostfixCall'),
			Tc2HandTypes.PokerHand.Action.TypeRaise: ('Raise', SettingsKeyBase + '/PrefixRaise', SettingsKeyBase + '/PostfixRaise'),
			Tc2HandTypes.PokerHand.Action.TypePostBlindAnte: ('Ante', SettingsKeyBase + '/PrefixAnte', SettingsKeyBase + '/PostfixAnte'),
			Tc2HandTypes.PokerHand.Action.TypePostBlindSmall: ('SmallBlind', SettingsKeyBase + '/PrefixSmallBlind', SettingsKeyBase + '/PostfixSmallBlind'),
			Tc2HandTypes.PokerHand.Action.TypePostBlindBig: ('BigBlind', SettingsKeyBase + '/PrefixBigBlind', SettingsKeyBase + '/PostfixBigBlind'),
			Tc2HandTypes.PokerHand.Action.TypePostBuyIn: ('BuyIn', SettingsKeyBase + '/PrefixBuyIn', SettingsKeyBase + '/PostfixBuyIn'),
			Tc2HandTypes.PokerHand.Action.TypePostBringIn: ('BringIn', SettingsKeyBase + '/PrefixBringIn', SettingsKeyBase + '/PostfixBringIn'),
			}

	class ActionLineEdit(QtGui.QLineEdit):
		def __init__(self, parent, action, isPrefix=True):
			QtGui.QLineEdit.__init__(self, parent)
			self.action = action
			self.isPrefix = isPrefix


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.labelPrefix = QtGui.QLabel('<i>Prefix</i>', self)
		self.labelAction = QtGui.QLabel('<i>Action</i>', self)
		self.labelPostfix = QtGui.QLabel('<i>Postfix</i>', self)

		self.actionWidgets = {}
		formatter = Tc2Config.handFormatter('HtmlTabular')
		for i, action in enumerate(formatter.listHandActions()):
			prefix, postfix = formatter.actionPrefix(action), formatter.actionPostfix(action)
			editPrefix = self.ActionLineEdit(self, action, isPrefix=True)
			editPrefix.setMaxLength(Tc2Config.MaxHandGrabberPrefix)
			labelAction = QtGui.QLabel('<i>%s</i>' % self.HandActionsMapping[action][0], self)
			editPostfix = None
			if postfix is not None:
				editPostfix =  self.ActionLineEdit(self, action, isPrefix=False)
				editPostfix.setMaxLength(Tc2Config.MaxHandGrabberPrefix)

			self.actionWidgets[action] = {'EditPrefix': editPrefix, 'LabelAction': labelAction, 'EditPostfix': editPostfix, 'no': i}

		self.comboSideBarPosition = QtGui.QComboBox(self)
		self.comboSideBarPosition.addItems(Tc2Config.HandViewerSideBarPositions)
		self.labelSideBarPosition = QtGui.QLabel('&Side bar position:', self)
		self.labelSideBarPosition.setBuddy(self.comboSideBarPosition)

		self.comboDeckStyle = QtGui.QComboBox(self)
		self.comboDeckStyle.addItems(formatter.deckStyles())
		self.labelDeckStyle = QtGui.QLabel('Deck st&yle:', self)
		self.labelDeckStyle.setBuddy(self.comboDeckStyle)

		self.spinMaxPlayerName = QtGui.QSpinBox(self)
		self.spinMaxPlayerName.setRange(Tc2Config.HandViewerMaxPlayerNameMin, Tc2Config.HandViewerMaxPlayerNameMax)
		self.labelMaxPlayerName = QtGui.QLabel('Ma&x Player Name:', self)
		self.labelMaxPlayerName.setBuddy(self.spinMaxPlayerName)

		self.checkNoFloatingPoint = QtGui.QCheckBox('No floating &Point', self)

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
		grid.col(self.labelDeckStyle).col(self.comboDeckStyle)
		grid.row()
		grid.col(self.labelMaxPlayerName).col(self.spinMaxPlayerName)
		grid.row()
		grid.col(self.checkNoFloatingPoint, colspan=3)
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelPrefix, align=QtCore.Qt.AlignHCenter).col(self.labelAction, align=QtCore.Qt.AlignHCenter).col(self.labelPostfix, align=QtCore.Qt.AlignHCenter)
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)

		actions = sorted(self.actionWidgets.values(), key=operator.itemgetter('no'))
		for data in actions:
			grid.row()
			grid.col(data['EditPrefix']).col(data['LabelAction'], align=QtCore.Qt.AlignHCenter)
			if data['EditPostfix'] is not None:
				grid.col(data['EditPostfix'])
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onRestoreDefault(self, *args):
		formatter = Tc2Config.handFormatter('HtmlTabular')
		formatter.resetHandActions()
		for data in self.actionWidgets.values():
			editPrefix = data['EditPrefix']
			editPrefix.setText(formatter.actionPrefix(editPrefix.action))
			editPrefix.editingFinished.emit()
			editPostfix = data['EditPostfix']
			if editPostfix is not None:
				editPostfix.setText(formatter.actionPostfix(editPostfix.action))
				editPostfix.editingFinished.emit()

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsHandViewer', parent=self)

	def sideBarPosition(self):
		return self.comboSideBarPosition.currentText()

	def setSideBarPosition(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeySideBarPosition, value)
		self.sideBarPositionChanged.emit(value)

	def onInitSettings(self):
		self.layout()
		formatter = Tc2Config.handFormatter('HtmlTabular')

		value = Tc2Config.settingsValue(self.SettingsKeySideBarPosition, '').toString()
		if value not in Tc2Config.HandViewerSideBarPositions:
			value = Tc2Config.HandViewerSideBarPositionDefault
		self.comboSideBarPosition.setCurrentIndex( self.comboSideBarPosition.findText(value, QtCore.Qt.MatchExactly) )
		#NOTE: pySlot decorator does not work as expected so we have to connect slot the old fashioned way
		self.connect(self.comboSideBarPosition, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setSideBarPosition)

		value = Tc2Config.settingsValue(self.SettingsKeyDeckStyle, '').toString()
		if value not in formatter.deckStyles():
			value = Tc2Config.HandViewerDeckStyleDefault
		formatter.setDeckStyle(unicode(value.toUtf8(), 'utf-8'))
		self.comboDeckStyle.setCurrentIndex( self.comboDeckStyle.findText(value, QtCore.Qt.MatchExactly) )
		#NOTE: pySlot decorator does not work as expected so we have to connect slot the old fashioned way
		self.connect(self.comboDeckStyle, QtCore.SIGNAL('currentIndexChanged(QString)'), self.onDeckStyleChanged)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyMaxPlayerName, Tc2Config.HandViewerMaxPlayerNameDefault).toInt()
		if not ok or value < Tc2Config.HandViewerMaxPlayerNameMin or value > Tc2Config.HandViewerMaxPlayerNameMax:
			value = Tc2Config.WebView.HandViewerMaxPlayerNameDefault
		formatter.setMaxPlayerName(value)
		self.spinMaxPlayerName.setValue(value)
		self.spinMaxPlayerName.valueChanged.connect(self.onMaxPlayerNameChanged)

		value = Tc2Config.settingsValue(self.SettingsKeyNoFloatingPoint, Tc2Config.HandViewerNoFloatingPointDefault).toBool()
		formatter.setNoFloatingPoint(value)
		self.checkNoFloatingPoint.setCheckState(value)
		self.checkNoFloatingPoint.stateChanged.connect(self.onNoFloatingPointChanged)

		for data in self.actionWidgets.values():
			editPrefix = data['EditPrefix']
			settingsKey = self.HandActionsMapping[editPrefix.action][1]
			text = Tc2Config.settingsValue(settingsKey, formatter.actionPrefix(editPrefix.action)).toString()
			editPrefix.setText(text)
			formatter.setActionPrefix(editPrefix.action, text)
			editPrefix.textChanged.connect(
					lambda text, edit=editPrefix: self.onActionValueChanged(edit, text)
					)

			editPostfix = data['EditPostfix']
			if editPostfix is not None:
				settingsKey = self.HandActionsMapping[editPrefix.action][2]
				text = Tc2Config.settingsValue(settingsKey, formatter.actionPostfix(editPostfix.action)).toString()
				editPostfix.setText(text)
				formatter.setActionPostfix(editPostfix.action, text)
				editPostfix.textChanged.connect(
					lambda text, edit=editPostfix: self.onActionValueChanged(edit, text)
					)
		Tc2Config.globalObject.objectCreatedSettingsHandViewer.emit(self)


	def onActionValueChanged(self, edit, text):
		formatter = Tc2Config.handFormatter('HtmlTabular')
		if edit.isPrefix:
			formatter.setActionPrefix(edit.action, text)
			settingsKey = self.HandActionsMapping[edit.action][1]
		else:
			formatter.setActionPostfix(edit.action, text)
			settingsKey = self.HandActionsMapping[edit.action][2]
		Tc2Config.settingsSetValue(settingsKey, text)

	def onDeckStyleChanged(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyDeckStyle, value)
		formatter = Tc2Config.handFormatter('HtmlTabular')
		formatter.setDeckStyle(unicode(value.toUtf8(), 'utf-8'))

	def onMaxPlayerNameChanged(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyMaxPlayerName, value)
		formatter = Tc2Config.handFormatter('HtmlTabular')
		formatter.setMaxPlayerName(value)

	def onNoFloatingPointChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(self.SettingsKeyNoFloatingPoint, flag)
		formatter = Tc2Config.handFormatter('HtmlTabular')
		formatter.setNoFloatingPoint(flag)








