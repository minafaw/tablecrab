
import Tc2Config
import Tc2GuiHelp
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingsKeyBase = 'Clock'
	SettingsKeySpeed = SettingsKeyBase + '/Speed'
	SettingsKeyPrecission = SettingsKeyBase + '/Precission'
	SettingsKeyIncrement = SettingsKeyBase + '/Increment'
	SettingsKeyRandomMode = SettingsKeyBase + '/RandomMode'
	SettingsKeyIsOn = SettingsKeyBase + '/IsOn'

	speedChanged = QtCore.pyqtSignal(float)
	precissionChanged = QtCore.pyqtSignal(int)
	incrementChanged = QtCore.pyqtSignal(int)
	randomModeChanged = QtCore.pyqtSignal(bool)
	isOnChanged = QtCore.pyqtSignal(bool)

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.labelSpeed = QtGui.QLabel('&Speed:', self)
		self.spinSpeed = QtGui.QDoubleSpinBox(self)
		self.labelSpeed.setBuddy(self.spinSpeed)
		self.spinSpeed.setRange(Tc2Config.ClockLabel.SpeedMin, Tc2Config.ClockLabel.SpeedMax)
		self.spinSpeed.setSingleStep(0.1)
		self.spinSpeed.setDecimals(1)

		self.labelPrecission = QtGui.QLabel('&Precission:', self)
		self.spinPrecission = QtGui.QSpinBox(self)
		self.labelPrecission.setBuddy(self.spinPrecission)
		self.spinPrecission.setRange(Tc2Config.ClockLabel.PrecissionMin, Tc2Config.ClockLabel.PrecissionMax)

		self.labelIncrement = QtGui.QLabel('&Increment:', self)
		self.spinIncrement = QtGui.QSpinBox(self)
		self.labelIncrement.setBuddy(self.spinIncrement)
		self.spinIncrement.setRange(Tc2Config.ClockLabel.IncrementMin, Tc2Config.ClockLabel.IncrementMax)

		self.checkRandomMode = QtGui.QCheckBox('&Random mode', self)
		self.checkIsOn = QtGui.QCheckBox('&On', self)

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
		grid.col(self.checkIsOn).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelSpeed).col(self.spinSpeed).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelPrecission).col(self.spinPrecission).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelIncrement).col(self.spinIncrement).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.checkRandomMode).col(Tc2Config.HStretch())
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onInitSettings(self):
		self.layout()

		value, ok = Tc2Config.settingsValue(self.SettingsKeySpeed, '').toFloat()
		if not ok or value > Tc2Config.ClockLabel.SpeedMax or value < Tc2Config.ClockLabel.SpeedMin:
			value = Tc2Config.DefaultClockSpeed
		self.spinSpeed.setValue(value)
		self.spinSpeed.valueChanged.connect(self.setSpeed)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyPrecission, '').toInt()
		if not ok or value > Tc2Config.ClockLabel.PrecissionMax or value < Tc2Config.ClockLabel.PrecissionMin:
			value = Tc2Config.DefaultClockPrecission
		self.spinPrecission.setValue(value)
		self.spinPrecission.valueChanged.connect(self.setPrecission)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyIncrement, '').toInt()
		if not ok or value > Tc2Config.ClockLabel.IncrementMax or value < Tc2Config.ClockLabel.IncrementMin:
			value = Tc2Config.DefaultClockIncrement
		self.spinIncrement.setValue(value)
		self.spinIncrement.valueChanged.connect(self.setIncrement)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyRandomMode, False).toBool() else QtCore.Qt.Unchecked
		self.checkRandomMode.setCheckState(value)
		self.checkRandomMode.stateChanged.connect(
				lambda value, self=self: self.setRandomMode(self.checkRandomMode.checkState() == QtCore.Qt.Checked)
				)

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyIsOn, True).toBool() else QtCore.Qt.Unchecked
		self.checkIsOn.setCheckState(value)
		self.checkIsOn.stateChanged.connect(
				lambda value, self=self: self.setIsOn(self.checkIsOn.checkState() == QtCore.Qt.Checked)
				)



		Tc2Config.globalObject.objectCreatedSettingsClock.emit(self)

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsClock', parent=self)

	def speed(self):
		return self.spinSpeed.value()

	def setSpeed(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeySpeed, value)
		self.speedChanged.emit(value)

	def precission(self):
		return self.spinPrecission.value()

	def setPrecission(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyPrecission, value)
		self.precissionChanged.emit(value)

	def increment(self):
		return self.spinIncrement.value()

	def setIncrement(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyIncrement, value)
		self.incrementChanged.emit(value)

	def randomMode(self):
		return self.checkRandomMode.checkState() == QtCore.Qt.Checked

	def setRandomMode(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyRandomMode, value)
		self.randomModeChanged.emit(value)

	def isOn(self):
		return self.checkIsOn.checkState() == QtCore.Qt.Checked

	def setIsOn(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyIsOn, value)
		self.isOnChanged.emit(value)







