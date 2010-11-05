
import Tc2Config
import  Tc2GuiHelp
import Tc2SitePokerStars
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.checkAutoClosePopupNews = QtGui.QCheckBox('Close popup &news', self)
		self.checkAutoCloseTourneyRegistrationBoxes = QtGui.QCheckBox('Close t&ourney registration boxes', self)
		self.checkAutoCloseTableMessageBoxes = QtGui.QCheckBox('Close &table message boxes', self)
		self.checkAutoLogIn = QtGui.QCheckBox('Close &log In box', self)
		self.checkMoveMouseToActiveTable = QtGui.QCheckBox('Move &mouse To active table', self)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		Tc2Config.globalObject.init.connect(self.onInit)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
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
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsPokerStars', parent=self)

	def onAutoClosePopupNewsChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoClosePopupNews, flag)

	def onAutoCloseTourneyRegistrationBoxesChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoCloseTourneyRegistrationBoxes, flag)

	def onAutoCloseTableMessageBoxesChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoCloseTableMessageBoxes, flag)

	def onAutoLogInChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoCloseLogin, flag)

	def onMoveMouseToActiveTable(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2SitePokerStars.SiteHandler.SettingsKeyMoveMouseToActiveTable, flag)

	def onInit(self):
		self.layout()

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoClosePopupNews, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoClosePopupNews.setCheckState(state)
		self.checkAutoClosePopupNews.stateChanged.connect(self.onAutoClosePopupNewsChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoCloseTourneyRegistrationBoxes, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoCloseTourneyRegistrationBoxes.setCheckState(state)
		self.checkAutoCloseTourneyRegistrationBoxes.stateChanged.connect(self.onAutoCloseTourneyRegistrationBoxesChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoCloseTableMessageBoxes, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoCloseTableMessageBoxes.setCheckState(state)
		self.checkAutoCloseTableMessageBoxes.stateChanged.connect(self.onAutoCloseTableMessageBoxesChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2SitePokerStars.SiteHandler.SettingsKeyAutoCloseLogin, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoLogIn.setCheckState(state)
		self.checkAutoLogIn.stateChanged.connect(self.onAutoLogInChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2SitePokerStars.SiteHandler.SettingsKeyMoveMouseToActiveTable, False).toBool() else QtCore.Qt.Unchecked
		self.checkMoveMouseToActiveTable.setCheckState(state)
		self.checkMoveMouseToActiveTable.stateChanged.connect(self.onMoveMouseToActiveTable)

