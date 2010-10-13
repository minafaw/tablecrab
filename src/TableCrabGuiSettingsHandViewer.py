
import TableCrabConfig
import TableCrabGuiHelp
import PokerStarsHandGrabber
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

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
			editPrefix = QtGui.QLineEdit(self)
			editPrefix.setObjectName(actionPrefix)
			editPrefix.setMaxLength(TableCrabConfig.MaxHandGrabberPrefix)
			labelAction = QtGui.QLabel('<i>' + actionName + '</i>', self)
			labelAction.setBuddy(editPrefix)

			if actionPostfix is not None:
				editPostfix = QtGui.QLineEdit(self)
				editPostfix.setObjectName(actionPostfix)
				editPostfix.setMaxLength(TableCrabConfig.MaxHandGrabberPrefix)
			else:
				editPostfix = None
			self.actionWidgets.append( (editPrefix, labelAction, editPostfix) )

		self.spinMaxPlayerName = QtGui.QSpinBox(self)
		self.spinMaxPlayerName.setRange(-1, 999)
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

		TableCrabConfig.globalObject.init.connect(self.onInit)

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelMaxPlayerName).col(self.spinMaxPlayerName)
		grid.row()
		grid.col(self.checkNoFloatingPoint, colspan=3)
		grid.row()
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelPrefix).col(self.labelAction).col(self.labelPostfix)
		for i, (editPrefix, labelAction, editPostfix) in enumerate(self.actionWidgets):
			grid.row()
			grid.col(editPrefix).col(labelAction)
			if editPostfix is not None:
				grid.col(editPostfix)
		grid.row()
		grid.col(TableCrabConfig.VStretch())
		grid.row()
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onRestoreDefault(self, *args):
		for editPrefix, _, editPostfix in self.actionWidgets:
			default = getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, str(editPrefix.objectName()) )
			editPrefix.setText(default)
			editPrefix.editingFinished.emit()
			if editPostfix is not None:
				default = getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, str(editPostfix.objectName()) )
				editPostfix.setText(default)
				editPostfix.editingFinished.emit()

	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('settingsHandViewer', parent=self)

	def onSpinMaxPlayerNameValueChanged(self, value):
		TableCrabConfig.settingsSetValue('PokerStarsHandGrabber/HandFornmatterHtmlTabular/MaxPlayerName', value)

	def onNoFloatingPointChanged(self, state):
		flag = state == QtCore.Qt.Checked
		TableCrabConfig.settingsSetValue('PokerStarsHandGrabber/HandFornmatterHtmlTabular/NoFloatingPoint', flag)

	def onActionWidgetValueChanged(self):
		edit = self.sender()
		TableCrabConfig.settingsSetValue('PokerStarsHandGrabber/handFornmatterHtmlTabular/%s' % str(edit.objectName()), edit.text() )

	def onInit(self):
		self.layout()

		maxPlayerName = TableCrabConfig.settingsValue('PokerStarsHandGrabber/HandFornmatterHtmlTabular/MaxPlayerName', -1).toInt()[0]
		self.spinMaxPlayerName.setValue(maxPlayerName)
		self.spinMaxPlayerName.valueChanged.connect(self.onSpinMaxPlayerNameValueChanged)

		state = QtCore.Qt.Checked if TableCrabConfig.settingsValue('PokerStarsHandGrabber/HandFornmatterHtmlTabular/NoFloatingPoint', False).toBool() else QtCore.Qt.Unchecked
		self.checkNoFloatingPoint.setCheckState(state)
		self.checkNoFloatingPoint.stateChanged.connect(self.onNoFloatingPointChanged)

		for editPrefix, _, editPostfix in self.actionWidgets:
			prefix = str(editPrefix.objectName())
			default = getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, prefix)
			text = TableCrabConfig.settingsValue('PokerStarsHandGrabber/handFornmatterHtmlTabular/%s' % prefix, default).toString()
			editPrefix.setText(text)
			editPrefix.editingFinished.connect(self.onActionWidgetValueChanged)
			if editPostfix is not None:
				postfix = str(editPostfix.objectName())
				default = getattr(PokerStarsHandGrabber.HandFormatterHtmlTabular, postfix)
				text = TableCrabConfig.settingsValue('PokerStarsHandGrabber/handFornmatterHtmlTabular/%s' % postfix, default).toString()
				editPostfix.setText(text)
				editPostfix.editingFinished.connect(self.onActionWidgetValueChanged)


