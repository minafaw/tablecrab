
import Tc2Config
import  Tc2GuiHelp
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingKeyBase = 'PokerStars'
	SettingsKeyAutoClosePopupNews = SettingKeyBase + '/AutoClosePopupNews'
	SettingsKeyAutoCloseTourneyRegistrationBoxes = SettingKeyBase + '/AutoCloseTourneyRegistrationBoxes'
	SettingsKeyAutoCloseTableMessageBoxes = SettingKeyBase + '/AutoCloseTableMessageBoxes'
	SettingsKeyAutoCloseLogin = SettingKeyBase + '/AutoCloseLogin'
	SettingsKeyMoveMouseToActiveTable = SettingKeyBase + '/MoveMouseToActiveTable'

	autoClosePopupNewsChanged = QtCore.pyqtSignal(bool)
	autoCloseTourneyRegistrationBoxesChanged = QtCore.pyqtSignal(bool)
	autoCloseTableMessageBoxesChanged = QtCore.pyqtSignal(bool)
	autoCloseloginChanged = QtCore.pyqtSignal(bool)
	moveMouseToActiveTableChanged = QtCore.pyqtSignal(bool)

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.checkAutoClosePopupNews = QtGui.QCheckBox('Close popup &news', self)
		self.checkAutoCloseTourneyRegistrationBoxes = QtGui.QCheckBox('Close t&ourney registration boxes', self)
		self.checkAutoCloseTableMessageBoxes = QtGui.QCheckBox('Close &table message boxes', self)
		self.checkAutoCloselogin = QtGui.QCheckBox('Close &log In box', self)
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
		grid.col(self.checkAutoCloselogin)
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

	def autoClosePopupNews(self):
		return self.checkAutoClosePopupNews.checkState() == QtCore.Qt.Checked

	def setAutoClosePopupNews(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyAutoClosePopupNews, value)
		self.autoClosePopupNewsChanged.emit(value)

	def autoCloseTourneyRegistrationBoxes(self):
		return self.checkAutoTourneyRegistrationBoxes.checkState() == QtCore.Qt.Checked

	def setAutoCloseTourneyRegistrationBoxes(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyAutoCloseTourneyRegistrationBoxes, value)
		self.autoCloseTourneyRegistrationBoxesChanged.emit(value)

	def autoCloseTableMessageBoxes(self):
		return self.checkAutoCloseTableMessageBoxes.checkState() == QtCore.Qt.Checked

	def setAutoCloseTableMessageBoxes(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyAutoCloseTableMessageBoxes, value)
		self.autoCloseTableMessageBoxesChanged.emit(value)

	def autoCloseLogin(self):
		return self.checkAutoCloselogin.checkState() == QtCore.Qt.Checked

	def setAutoCloseLogin(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyAutoCloseLogin, value)
		self.autoCloseloginChanged.emit(value)

	def moveMouseToActiveTable(self):
		return self.checkMoveMouseToActiveTable.checkState() == QtCore.Qt.Checked

	def setMoveMouseToActiveTable(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyMoveMouseToActiveTable, value)
		self.moveMouseToActiveTableChanged.emit(value)

	def onInit(self):
		self.layout()

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyAutoClosePopupNews, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoClosePopupNews.setCheckState(value)
		self.checkAutoClosePopupNews.stateChanged.connect(
				lambda value, self=self: self.setAutoClosePopupNews(self.checkAutoClosePopupNews.checkState() == QtCore.Qt.Checked)
				)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyAutoCloseTourneyRegistrationBoxes, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoCloseTourneyRegistrationBoxes.setCheckState(value)
		self.checkAutoCloseTourneyRegistrationBoxes.stateChanged.connect(
				lambda value, self=self: self.setAutoCloseTourneyRegistrationBoxes(self.checkAutoCloseTourneyRegistrationBoxes.checkState() == QtCore.Qt.Checked)
				)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyAutoCloseTableMessageBoxes, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoCloseTableMessageBoxes.setCheckState(value)
		self.checkAutoCloseTableMessageBoxes.stateChanged.connect(
				lambda value, self=self: self.setAutoCloseTableMessageBoxes(self.checkAutoCloseTableMessageBoxes.checkState() == QtCore.Qt.Checked)
				)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyAutoCloseLogin, False).toBool() else QtCore.Qt.Unchecked
		self.checkAutoCloselogin.setCheckState(value)
		self.checkAutoCloselogin.stateChanged.connect(
				lambda value, self=self: self.setAutoCloseLogin(self.checkAutoCloselogin.checkState() == QtCore.Qt.Checked)
				)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyMoveMouseToActiveTable, False).toBool() else QtCore.Qt.Unchecked
		self.checkMoveMouseToActiveTable.setCheckState(value)
		self.checkMoveMouseToActiveTable.stateChanged.connect(
				lambda value, self=self: self.setMoveMouseToActiveTable(self.checkMoveMouseToActiveTable.checkState() == QtCore.Qt.Checked)
				)

		Tc2Config.globalObject.objectCreatedSettingsPokerStars.emit(self)

