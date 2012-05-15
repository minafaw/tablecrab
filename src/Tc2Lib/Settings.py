
from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************
class SettingTemp(QtCore.QObject):
	"""Temporary setting that never gets written to disk"""

	changed = QtCore.pyqtSignal(QtCore.QObject)

	def __init__(self, settings, key, defaultValue=None):
		QtCore.QObject.__init__(self)

		self._settings = settings
		self._key = key
		self._value = None
		self._defaultValue = defaultValue
		self.setDefaultValue(defaultValue)

	def defaultValue(self):
		return self._defaultValue

	def setDefaultValue(self, value):
		self._defaultValue = value

	def toSettings(self, qSettings, key, value):
		pass

	def fromSettings(self, qSettings, key):
		return True, self._default

	def init(self):
		ok, value = self.fromSettings(self._settings.qSettings(), self._key)
		if ok:
			self._value = value
		else:
			self._value = self._defaultValue
			self.toSettings(self._settings.qSettings(), self._key, self._value)
		self.changed.emit(self)

	def value(self):
		return self._value

	def setValue(self, value):
		self._value = value
		self.toSettings(self._settings.qSettings(), self._key, self._value)
		self._settings.qSettings().sync()
		self.changed.emit(self)

	def resetValue(self):
		self.setValue(self._defaultValue)

class SettingByteArray(SettingTemp):

	def __init__(self, settings, key, defaultValue=None):
		SettingTemp.__init__(self, settings, key, defaultValue=defaultValue)

	def toSettings(self, qSettings, key, value):
		qSettings.setValue(key, QtCore.QVariant(value))

	def fromSettings(self, qSettings, key):
		#TODO: no idea if to check for QByteArray.isNull() here
		return True, qSettings.value(key).toByteArray()


class SettingBool(SettingTemp):

	def __init__(self, settings, key, defaultValue=0, maxValue=None, minValue=None):
		SettingTemp.__init__(self, settings, key, defaultValue=defaultValue)
		self._checkBox = None

	def toSettings(self, qSettings, key, value):
		qSettings.setValue(key, QtCore.QVariant(bool(value)))

	def fromSettings(self, qSettings, key):
		ok, value = False, False
		if qSettings.contains(key):
			ok = True
			value = qSettings.value(key).toBool()
		return ok, value

	def setCheckBox(self, checkBox):
		self._checkBox = checkBox
		checkBox.setCheckState(QtCore.Qt.Checked if self.value() else QtCore.Qt.Unchecked)
		checkBox.stateChanged.connect(self.onCheckBoxStateChanged)

	def init(self):
		SettingTemp.init(self)
		if self._checkBox is not None:
			self._checkBox.stateChanged.disconnect(self.onCheckBoxStateChanged)
			self._checkBox.setCheckState(QtCore.Qt.Checked if self.value() else QtCore.Qt.Unchecked)
			self._checkBox.stateChanged.connect(self.onCheckBoxStateChanged)

	def setValue(self, value):
		SettingTemp.setValue(self, value)
		if self._checkBox is not None:
			self._checkBox.stateChanged.disconnect(self.onCheckBoxStateChanged)
			self._checkBox.setCheckState(QtCore.Qt.Checked if value else QtCore.Qt.Unchecked)
			self._checkBox.stateChanged.connect(self.onCheckBoxStateChanged)

	def onCheckBoxStateChanged(self, state):
		self.setValue(state == QtCore.Qt.Checked)


class SettingInt(SettingTemp):

	def __init__(self, settings, key, defaultValue=0, maxValue=None, minValue=None):
		SettingTemp.__init__(self, settings, key, defaultValue=defaultValue)
		self._maxValue = maxValue
		self._minValue = minValue
		self._spinBox = None

	def toSettings(self, qSettings, key, value):
		qSettings.setValue(key, QtCore.QVariant(value))

	def fromSettings(self, qSettings, key):
		value, ok =qSettings.value(key).toInt()
		if ok:
			if self._minValue is not None:
				if value < self._minValue:
					ok = False
			if self._maxValue is not None:
				if value > self._maxValue:
					ok = False
		return ok, value

	def maxValue(self):
		return self._maxValue

	def minValue(self):
		return self._minValue

	def setSpinBox(self, spinBox):
		self._spinBox = spinBox
		spinBox.setRange(self.minValue(), self.maxValue())
		spinBox.valueChanged.connect(self.onSpinBoxValueChanged)

	def init(self):
		SettingTemp.init(self)
		if self._spinBox is not None:
			self._spinBox.valueChanged.disconnect(self.onSpinBoxValueChanged)
			self._spinBox.setValue(self.value())
			self._spinBox.valueChanged.connect(self.onSpinBoxValueChanged)

	def setValue(self, value):
		SettingTemp.setValue(self, value)
		if self._spinBox is not None:
			self._spinBox.valueChanged.disconnect(self.onSpinBoxValueChanged)
			self._spinBox.setValue(value)
			self._spinBox.valueChanged.connect(self.onSpinBoxValueChanged)

	def onSpinBoxValueChanged(self, value):
		self.setValue(value)


class SettingChooseString(SettingTemp):

	def __init__(self, settings, key, defaultValue=None, choices=None):
		self._choices = [] if choices is None else choices
		self._comboBox = None
		SettingTemp.__init__(self, settings, key, defaultValue=defaultValue)

	def choices(self):
		return self._choices

	def toSettings(self, qSettings, key, value):
		qSettings.setValue(key, QtCore.QVariant(value))

	def fromSettings(self, qSettings, key):
		ok = False
		value = unicode(qSettings.value(key).toString().toUtf8(), 'utf-8')
		if value in self._choices:
			ok = True
		return ok, value

	def setComboBox(self, comboBox):
		self._comboBox = comboBox
		comboBox.addItems(self.choices())
		comboBox.currentIndexChanged.connect(self.onComboBoxValueChanged)

	def init(self):
		SettingTemp.init(self)
		if self._comboBox is not None:
			self._comboBox.currentIndexChanged.disconnect(self.onComboBoxValueChanged)
			i = self._comboBox.findText(self.value())
			self._comboBox.setCurrentIndex(i)
			self._comboBox.currentIndexChanged.connect(self.onComboBoxValueChanged)

	def setValue(self, value):
		SettingTemp.setValue(self, value)
		if self._comboBox is not None:
			self._comboBox.currentIndexChanged.disconnect(self.onComboBoxValueChanged)
			i = self._comboBox.findText(value)
			self._comboBox.setCurrentIndex(i)
			self._comboBox.currentIndexChanged.connect(self.onComboBoxValueChanged)

	def onComboBoxValueChanged(self, value):
		self.setValue(unicode(self._comboBox.currentText().toUtf8(), 'utf-8'))


class SettingFont(SettingTemp):

	def __init__(self, settings, key, defaultValue=None):
		SettingTemp.__init__(self, settings, key, defaultValue=defaultValue)
		self._fontButton = None

	def toSettings(self, qSettings, key, value):
		qSettings.setValue(key, QtCore.QVariant(value.toString()))

	def fromSettings(self, qSettings, key):
		ok = False
		value = QtGui.QFont()
		if value.fromString( qSettings.value(key).toString()):
			ok = True
		return ok, value

	def setFontButton(self, fontButton):
		self._fontButton = fontButton
		fontButton.fontChanged.connect(self.onFontButtonFontChanged)

	def init(self):
		SettingTemp.init(self)
		if self._fontButton is not None:
			self._fontButton.fontChanged.disconnect(self.onFontButtonFontChanged)
			self._fontButton.setFont(self.value())
			self._fontButton.fontChanged.connect(self.onFontButtonFontChanged)

	def setValue(self, value):
		SettingTemp.setValue(self, value)
		if self._fontButton is not None:
			self._fontButton.fontChanged.disconnect(self.onFontButtonFontChanged)
			self._fontButton.setFont(value)
			self._fontButton.fontChanged.connect(self.onFontButtonFontChanged)

	def onFontButtonFontChanged(self, value):
		self.setValue(value)




#************************************************************************************
#
#************************************************************************************
class Settings(QtCore.QObject):

	inited = QtCore.pyqtSignal(QtCore.QObject)

	def __init__(self, qSettings=None):
		QtCore.QObject.__init__(self)
		self._qSettings = qSettings
		self._settings = {}	# key-->setting
	def qSettings(self):
		return self._qSettings
	def setSettings(self, qSettings):
		self._qSettings = qSettings
		for setting in self._settings.values():
			setting._value = None
	def __getitem__(self, key):
		return self._settings[key]
	def int(self, key, defaultValue=0, maxValue=None, minValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingInt(self, key, defaultValue=defaultValue, maxValue=maxValue, minValue=minValue)
		self._settings[key] = setting
		return setting
	def bool(self, key, defaultValue=False):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingBool(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting
	def temp(self, key, defaultValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingTemp(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting
	def chooseString(self, key, defaultValue=None, choices=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingChooseString(self, key, defaultValue=defaultValue, choices=choices)
		self._settings[key] = setting
		return setting
	def font(self, key, defaultValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingFont(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting
	def byteArray(self, key, defaultValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingByteArray(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting

	def init(self):
		for setting in self._settings.values():
			setting.init()
		self._qSettings.sync()
		self.inited.emit(self)
	def clean(self):
		for key in self._qSettings.allKeys():
			key = unicode(key.toUtf8(), 'utf-8')
			if key not in self._settings:
				self._qSettings.remove(key)
		self._qSettings.sync()



if __name__ == '__main__':
	import os
	fileName = os.path.join(os.path.dirname(os.path.abspath(__file__)), '000.ini')
	s = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
	print s.fileName()
	s = Settings(s)
	st = s.int('Gui/foo', 1)
	print s.bool('Gui/bar', 1)

	s.init()
	s.clean()

	st.setValue(33)
	st.resetValue()











