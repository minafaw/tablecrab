
import TableCrabConfig
import TableCrabGuiHelp
import PokerStarsHandGrabber
from PyQt4 import QtGui

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
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelMaxPlayerName).col(self.spinMaxPlayerName)
		grid.row()
		grid.col(self.checkNoFloatingPoint, colspan=3)
		grid.row()
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelPrefix).col(self.labelAction).col(self.labelPostfix)
		for i, (editPrefix, labelAction, editPostfix, _, _) in enumerate(self.actionWidgets):
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
