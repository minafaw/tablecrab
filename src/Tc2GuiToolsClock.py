"""shot clock"""

import Tc2Config

from PyQt4 import QtCore, QtGui
import random

#***********************************************************************************
#
#***********************************************************************************
class ClockLabel(QtGui.QLabel):
	SpeedMin = 0.2
	SpeedMax = 5.0
	PrecissionMin = 1
	PrecissionMax = 5
	IncrementMin = 1
	IncrementMax = 100

	StyleSheet = 'color: %s; background-color: %s'

	def __init__(self, parent=None, precission=PrecissionMin, increment=IncrementMin, speed=SpeedMin, randomMode=False):
		QtGui.QLabel.__init__(self, parent)
		self._precission = precission
		self. _increment = increment
		self._randomMode = randomMode
		self._value = 0
		self.setText(str(self._value).zfill(self._precission))
		self._timer = QtCore.QTimer(self)
		self._timer.setInterval(speed * 1000)
		self._timer.timeout.connect(self.tick)
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		settings = globalObject.settingsClock
		self.setOn(settings.isOn())
		settings.isOnChanged.connect(self.setOn)
		self.setIncrement(settings.increment())
		settings.incrementChanged.connect(self.setIncrement)
		self.setPrecission(settings.precission())
		settings.precissionChanged.connect(self.setPrecission)
		self.setSpeed(settings.speed())
		settings.speedChanged.connect(self.setSpeed)
		self.setRandomMode(settings.randomMode())
		settings.randomModeChanged.connect(self.setRandomMode)

		settings.foregroundColorChanged.connect(self.setColor)
		settings.backgroundColorChanged.connect(self.setColor)
		self.setColor(QtGui.QColor())

	def setIncrement(self, value):
		wasOn = self.setOn(False)
		self._increment = value
		if wasOn: self.setOn(True)

	def setPrecission(self, value):
		wasOn = self.setOn(False)
		self._precission = value
		if wasOn: self.setOn(True)

	def setSpeed(self, value):
		wasOn = self.setOn(False)
		self._timer.setInterval(value * 1000)
		if wasOn: self.setOn(True)

	def setRandomMode(self, flag):
		self._randomMode = flag

	def isOn(self):
		return self._timer.isActive()

	def setOn(self, flag):
		wasOn = self._timer.isActive()
		self._timer.start() if flag else self._timer.stop()
		return wasOn

	def tick(self):
		maxValue = 10**self._precission
		if self._randomMode:
			value = random.randint(1, maxValue)
			f = float(value) / self._increment
			self._value = int(self._increment * round(f, 0) )
		else:
			self._value += self._increment
		if self._value >= maxValue:
			self._value = 0
		self.setText(str(self._value).zfill(self._precission))

	def setColor(self, color):
		settings = Tc2Config.globalObject.settingsClock
		styleSheet = ''
		color = settings.foregroundColor()
		if color.isValid():
			styleSheet += 'color: %s;' % color.name()
		color = settings.backgroundColor()
		if color.isValid():
			styleSheet += 'background-color: %s' % color.name()
		self.setStyleSheet(styleSheet)






