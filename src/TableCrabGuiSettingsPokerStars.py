
import TableCrabConfig
import TableCrabGuiHelp
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.checkAutoClosePopupNews = QtGui.QCheckBox('Close Popup &News', self)
		self.checkAutoCloseTourneyRegistrationBoxes = QtGui.QCheckBox('Close T&ourney Registration Boxes', self)
		self.checkAutoCloseTableMessageBoxes = QtGui.QCheckBox('PokerStars/AutoCloseTableMessageBoxes', self)
		self.checkAutoLogIn = QtGui.QCheckBox('Close &Log In Box', self)
		self.checkMoveMouseToActiveTable = QtGui.QCheckBox('Move &Mouse To Active table', self)

		self.buttonBox = QtGui.QDialogButtonBox(self)

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

	def onAutoClosePopupNewsChanged(self, state):
		flag = state == QtCore.Qt.Checked
		TableCrabConfig.settingsSetValue('PokerStars/AutoClosePopupNews', flag)

	def onAutoCloseTourneyRegistrationBoxesChanged(self, state):
		flag = state == QtCore.Qt.Checked
		TableCrabConfig.settingsSetValue('PokerStars/AutoCloseTourneyRegistrationBoxes', flag)

	def onAutoCloseTableMessageBoxesChanged(self, state):
		flag = state == QtCore.Qt.Checked
		TableCrabConfig.settingsSetValue('PokerStars/AutoCloseTableMessageBoxes', flag)

	def onAutoLogInChanged(self, state):
		flag = state == QtCore.Qt.Checked
		TableCrabConfig.settingsSetValue('PokerStars/AutoCloseLogin', flag)

	def onMoveMouseToActiveTable(self, state):
		flag = state == QtCore.Qt.Checked
		TableCrabConfig.settingsSetValue('PokerStars/MoveMouseToActiveTable', flag)

	def onInit(self):
		self.layout()

		state = QtCore.Qt.Checked if TableCrabConfig.settingsValue('PokerStars/AutoClosePopupNews', False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoClosePopupNews.setCheckState(state)
		self.checkAutoClosePopupNews.stateChanged.connect(self.onAutoClosePopupNewsChanged)

		state = QtCore.Qt.Checked if TableCrabConfig.settingsValue('PokerStars/AutoCloseTourneyRegistrationBoxes', False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoCloseTourneyRegistrationBoxes.setCheckState(state)
		self.checkAutoCloseTourneyRegistrationBoxes.stateChanged.connect(self.onAutoCloseTourneyRegistrationBoxesChanged)

		state = QtCore.Qt.Checked if TableCrabConfig.settingsValue('PokerStars/AutoCloseTableMessageBoxes', False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoCloseTableMessageBoxes.setCheckState(state)
		self.checkAutoCloseTableMessageBoxes.stateChanged.connect(self.onAutoCloseTableMessageBoxesChanged)

		state = QtCore.Qt.Checked if TableCrabConfig.settingsValue('PokerStars/AutoCloseLogin', False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoLogIn.setCheckState(state)
		self.checkAutoLogIn.stateChanged.connect(self.onAutoLogInChanged)

		state = QtCore.Qt.Checked if TableCrabConfig.settingsValue('PokerStars/MoveMouseToActiveTable', False).toBool() else QtCore.Qt.Unchecked
		self.checkMoveMouseToActiveTable.setCheckState(state)
		self.checkMoveMouseToActiveTable.stateChanged.connect(self.onMoveMouseToActiveTable)
