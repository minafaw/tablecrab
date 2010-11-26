
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

	def proxyHostName(self):
		return Tc2Config.settingsValue(self.SettingsKeyProxyHostName, '').toString()

	def proxyPort(self):
		value, ok = Tc2Config.settingsValue(self.SettingsKeyProxyPort, '').toInt()
		if not ok or value > Tc2Config.MaxProxyPort or value < Tc2Config.MinProxyPort:
			value = Tc2Config.DefaultProxyPort
		return value

	def proxyUserName(self):
		return Tc2Config.settingsValue(self.SettingsKeyProxyUserName, '').toString()

	def proxyPassword(self):
		return self.editProxyPassword.text()

	def fetchTimeout(self):
		value, ok = Tc2Config.settingsValue(self.SettingsKeyFetchTimeout, '').toDouble()
		if not ok or value > Tc2Config.MaxFetchTimeout or value < Tc2Config.MinFetchTimeout:
			value = Tc2Config.DefaultFetchTimeout
		return value


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

		Tc2Config.globalObject.init.connect(self.onInit)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelProxyHostName).col(self.editProxyHostName).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelProxyPort).col(self.spinProxyPort).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelProxyUserName).col(self.editProxyUserName).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelProxyPassword).col(self.editProxyPassword).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelFetchTimeout).col(self.spinFetchTimeout).col(Tc2Config.HStretch())
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)


	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsNetwork', parent=self)

	def onInit(self):
		self.layout()

		self.editProxyHostName.setText(self.proxyHostName())
		self.editProxyHostName.editingFinished.connect(self.onEditProxyHostNameEditingFinished)
		self.spinProxyPort.setValue(self.proxyPort())
		self.spinProxyPort.valueChanged.connect(self.onSpinProxyPortValueChanged)
		self.editProxyUserName.setText(self.proxyUserName())
		self.editProxyUserName.editingFinished.connect(self.onEditProxyUserNameEditingFinished)
		#NOTE: proxy password is never stored
		self.editProxyPassword.editingFinished.connect(self.onEditProxyPasswordEditingFinished)
		self.spinFetchTimeout.setValue(self.fetchTimeout())
		self.spinFetchTimeout.valueChanged.connect(self.onSpinFetchTimeoutValueChanged)

		Tc2Config.globalObject.objectCreatedSettingsNetwork.emit(self)

	def onEditProxyHostNameEditingFinished(self):
		edit = self.sender()
		Tc2Config.settingsSetValue(self.SettingsKeyProxyHostName, edit.text())

	def onSpinProxyPortValueChanged(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyProxyPort, value)

	def onEditProxyUserNameEditingFinished(self):
		edit = self.sender()
		Tc2Config.settingsSetValue(self.SettingsKeyProxyUserName, edit.text())

	def onEditProxyPasswordEditingFinished(self):
		edit = self.sender()
		self.__class__.ProxyPassword = edit.text()

	def onSpinFetchTimeoutValueChanged(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyFetchTimeout, value)








