
import TableCrabConfig
import TableCrabGuiHelp
from PyQt4 import QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):
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
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.checkAutoClosePopupNews)
		grid.row()
		grid.col(self.checkAutoCloseTourneyRegistrationBoxes)
		grid.row()
		grid.col(self.checkAutoCloseTableMessageBoxes)
		grid.row()
		grid.col(self.checkAutoLogIn)
		grid.row()
		grid.col(self.checkMoveMouseToActiveTable)
		grid.row()
		grid.col(TableCrabConfig.VStretch())
		grid.row()
		grid.col(TableCrabConfig.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('settingsPokerStars', parent=self)
