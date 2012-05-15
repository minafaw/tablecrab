
import Tc2Config
import Tc2GuiHelp
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Settings/Network'
	SettingsKeyProxyHostName = SettingsKeyBase + '/ProxyHostName'
	SettingsKeyProxyPort = SettingsKeyBase + '/ProxyPort'
	SettingsKeyProxyUserName = SettingsKeyBase + '/ProxyUserName'
	SettingsKeyFetchTimeout = SettingsKeyBase + '/FetchTimeout'

	proxyHostNameChanged = QtCore.pyqtSignal(QtCore.QString)
	proxyPortChanged = QtCore.pyqtSignal(int)
	proxyUserNameChanged = QtCore.pyqtSignal(QtCore.QString)
	proxyPasswordChanged = QtCore.pyqtSignal(QtCore.QString)
	fetchTimeoutChanged = QtCore.pyqtSignal(float)

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)


		self.labelProxyHostName = QtGui.QLabel('Pro&xy host:')
		self.editProxyHostName = QtGui.QLineEdit(self)
		self.editProxyHostName.setMaxLength(Tc2Config.MaxProxyHostName)
		self.labelProxyHostName.setBuddy(self.editProxyHostName)

		self.labelProxyPort = QtGui.QLabel('Proxy &port:')
		self.spinProxyPort = QtGui.QSpinBox(self)
		self.spinProxyPort.setRange(Tc2Config.MinProxyPort, Tc2Config.MaxProxyPort)
		self.labelProxyPort.setBuddy(self.spinProxyPort)

		self.labelProxyUserName = QtGui.QLabel('Proxy user &name:')
		self.editProxyUserName = QtGui.QLineEdit(self)
		self.editProxyUserName.setMaxLength(Tc2Config.MaxProxyUserName)
		self.labelProxyUserName.setBuddy(self.editProxyUserName)

		self.labelProxyPassword = QtGui.QLabel('Proxy pass&word:')
		self.editProxyPassword = QtGui.QLineEdit(self)
		self.editProxyPassword.setEchoMode(self.editProxyPassword.PasswordEchoOnEdit)

		self.editProxyPassword.setMaxLength(Tc2Config.MaxProxyPassword)
		self.labelProxyPassword.setBuddy(self.editProxyPassword)

		self.labelFetchTimeout = QtGui.QLabel('&Fetch timeout:', self)
		self.spinFetchTimeout = QtGui.QDoubleSpinBox(self)
		self.labelFetchTimeout.setBuddy(self.spinFetchTimeout)
		self.spinFetchTimeout.setRange(Tc2Config.MinFetchTimeout, Tc2Config.MaxFetchTimeout)
		self.spinFetchTimeout.setSingleStep(0.1)
		self.spinFetchTimeout.setDecimals(1)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)
		self.addAction(action)

		Tc2Config.globalObject.initSettings.connect(self.onInitSettings)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=2)
		grid.row()
		grid.col(self.labelProxyHostName).col(self.editProxyHostName)
		grid.row()
		grid.col(self.labelProxyPort).col(self.spinProxyPort)
		grid.row()
		grid.col(self.labelProxyUserName).col(self.editProxyUserName)
		grid.row()
		grid.col(self.labelProxyPassword).col(self.editProxyPassword)
		grid.row()
		grid.col(self.labelFetchTimeout).col(self.spinFetchTimeout)
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=2)
		grid.row()
		grid.col(self.buttonBox, colspan=2)


	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsNetwork', parent=self)

	def onInitSettings(self):
		self.layout()

		value = Tc2Config.settingsValue(self.SettingsKeyProxyHostName, '').toString()
		self.editProxyHostName.setText(value)
		self.editProxyHostName.textChanged.connect(self.setProxyHostName)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyProxyPort, '').toInt()
		if not ok or value > Tc2Config.MaxProxyPort or value < Tc2Config.MinProxyPort:
			value = Tc2Config.DefaultProxyPort
		self.spinProxyPort.setValue(value)
		self.spinProxyPort.valueChanged.connect(self.setProxyPort)

		value = Tc2Config.settingsValue(self.SettingsKeyProxyUserName, '').toString()
		self.editProxyUserName.setText(value)
		self.editProxyUserName.textChanged.connect(self.setProxyUserName)

		self.editProxyPassword.textChanged.connect(self.setProxyPassword)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyFetchTimeout, '').toDouble()
		if not ok or value > Tc2Config.MaxFetchTimeout or value < Tc2Config.MinFetchTimeout:
			value = Tc2Config.DefaultFetchTimeout
		self.spinFetchTimeout.setValue(value)
		self.spinFetchTimeout.valueChanged.connect(self.setFetchTimeout)

		Tc2Config.globalObject.objectCreatedSettingsNetwork.emit(self)

	def proxyHostName(self):
		return self.editProxyHostName.text()

	def setProxyHostName(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyProxyHostName, value)
		self.proxyHostNameChanged.emit(value)

	def proxyPort(self):
		return self.spinProxyPort.value()

	def setProxyPort(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyProxyPort, value)
		self.proxyPortChanged.emit(value)

	def proxyUserName(self):
		return self.editProxyUserName.text()

	def setProxyUserName(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyProxyUserName, value)
		self.proxyUserNameChanged.emit(value)

	def proxyPassword(self):
		return self.editProxyPassword.text()

	def setProxyPassword(self, value):
		#NOTE: proxy password is never stored
		self.proxyPasswordChanged.emit(value)

	def fetchTimeout(self):
		return self.spinFetchTimeout.value()

	def setFetchTimeout(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyFetchTimeout, value)
		self.fetchTimeoutChanged.emit(value)



