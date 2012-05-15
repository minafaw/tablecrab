
from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************
class SettingTemp(QtCore.QObject):
	"""Temporary setting that never gets written to disk. may contain any value type"""

	changed = QtCore.pyqtSignal(QtCore.QObject)

	def __init__(self, settings, key, defaultValue=None):
		QtCore.QObject.__init__(self)
		self._settings = settings
		self._key = key
		self._value = None
		self._defaultValue = defaultValue
	def init(self):
		self.setValue(self._defaultValue)
	def key(self):
		return self._key
	def settings(self):
		return self._settings
	def defaultValue(self):
		return self._defaultValue
	def setDefaultValue(self, value):
		self._defaultValue = value
	def init(self):
		self._value = self._defaultValue
	def value(self):
		return self._value
	def setValue(self, value):
		self._value = value
		self.changed.emit(self)
	def resetValue(self):
		self.setValue(self._defaultValue)


class SettingPersistant(SettingTemp):
	"""base class for persistant settings"""
	def __init__(self, settings, key, defaultValue=False):
		SettingTemp.__init__(self, settings, key, defaultValue=defaultValue)
		self._widget = None
		self._widgetValueSetter = None
		self._widgetSignal = None
		self._widgetSlot = None
	def init(self):
		qSettings = self.settings().qSettings()
		ok, value = self.valueFromSettings(qSettings, self.key())
		if ok:
			self.setValue(value, store=False)
		else:
			self.setValue(self.defaultValue(), store=True)
	def setValue(self, value, store=True):
		SettingTemp.setValue(self, value)
		if store:
			qSettings = self.settings().qSettings()
			self.valueToSettings(qSettings, self.key(), value)
			##qSettings.sync()
		if self._widget is not None:
			self._widgetSignal.disconnect(self._widgetSlot)
			self._widgetValueSetter(value)
			self._widgetSignal.connect(self._widgetSlot)
		self.changed.emit(self)
	def setWidget(self, widget, setter, signal, slot):
		if self._widget is not None:
			raise ValueError('setting has already a widget assigned')
		self._widget = widget
		self._widgetValueSetter = setter
		self._widgetSignal = signal
		self._widgetSlot = slot
		self._widgetSignal.connect(self._widgetSlot)
	def valueFromSettings(self, qSettings, key):
		return qSettings.value(key)
	def valueToSettings(self, qSettings, key, value):
		qSettings.setValue(key, QtCore.QVariant(value))


class SettingBool(SettingPersistant):
	def valueFromSettings(self, qSettings, key):
		v = qSettings.value(key)
		return (True, v.toBool()) if v.isValid() else (False, None)
	def setCheckBox(self, checkBox):
		self.setWidget(
				checkBox,
				lambda value: checkBox.setCheckState(QtCore.Qt.Checked if value else QtCore.Qt.Unchecked),
				checkBox.stateChanged,
				lambda state: self.setValue(state == QtCore.Qt.Checked)
				)


class SettingInt(SettingPersistant):
	def __init__(self, settings, key, defaultValue=0, maxValue=None, minValue=None):
		SettingPersistant.__init__(self, settings, key, defaultValue=defaultValue)
		self._maxValue = maxValue
		self._minValue = minValue
	def minValue(self):
		return self._minValue
	def maxValue(self):
		return self._maxValue
	def valueFromSettings(self, qSettings, key):
		value, ok =qSettings.value(key).toInt()
		if ok:
			if self._minValue is not None:
				if value < self._minValue:
					ok, value = False, None
			if self._maxValue is not None:
				if value > self._maxValue:
					ok, value = False, None
		return ok, value
	def setSpinBox(self, spinBox):
		spinBox.setRange(self.minValue(), self.maxValue())
		self.setWidget(
				spinBox,
				spinBox.setValue,
				spinBox.valueChanged,
				self.setValue
				)


class SettingByteArray(SettingPersistant):
	def valueFromSettings(self, qSettings, key):
		#TODO: check for QByteArray.isNull() here?
		v = qSettings.value(key)
		return (True, v.toByteArray()) if v.isValid() else (False, None)


class SettingChooseString(SettingPersistant):
	def __init__(self, settings, key, defaultValue=None, choices=None):
		SettingPersistant.__init__(self, settings, key, defaultValue=defaultValue)
		self._choices = [] if choices is None else choices
	def choices(self):
		return self._choices
	def valueFromSettings(self, qSettings, key):
		ok = False
		value = unicode(qSettings.value(key).toString().toUtf8(), 'utf-8')
		if value in self._choices:
			ok = True
		else:
			value = None
		return ok, value
	def setComboBox(self, comboBox):
		comboBox.addItems(self.choices())
		self.setWidget(
				comboBox,
				lambda value: comboBox.setCurrentIndex(comboBox.findText(value)),
				comboBox.currentIndexChanged,
				lambda index: self.setValue(unicode(comboBox.currentText().toUtf8(), 'utf-8'))
				)


class SettingIndex(SettingPersistant):
	def valueFromSettings(self, qSettings, key):
		value, ok = qSettings.value(key).toInt()
		return (ok, value) if ok else (False, None)
	def setTabWidget(self, tabWidget):
		self.setWidget(
				tabWidget,
				tabWidget.setCurrentIndex,
				tabWidget.currentChanged,
				self.setValue
				)
	def setListWidget(self, listWidget):
		self.setWidget(
				listWidget,
				listWidget.setCurrentRow,
				listWidget.currentRowChanged,
				self.setValue
				)

class SettingFont(SettingPersistant):
	def __init__(self, settings, key, defaultValue=None):
		SettingPersistant.__init__(self, settings, key, defaultValue=defaultValue)
	def valueToSettings(self, qSettings, key, value):
		qSettings.setValue(key, QtCore.QVariant(value.toString()))
	def valueFromSettings(self, qSettings, key):
		ok = False
		value = QtGui.QFont()
		if value.fromString( qSettings.value(key).toString()):
			ok = True
		else:
			value = None
		return ok, value
	def setFontButton(self, fontButton):
		self.setWidget(
				fontButton,
				fontButton.setFont,
				fontButton.fontChanged,
				self.setValue
				)

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

	def Int(self, key, defaultValue=0, maxValue=None, minValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingInt(self, key, defaultValue=defaultValue, maxValue=maxValue, minValue=minValue)
		self._settings[key] = setting
		return setting
	def Bool(self, key, defaultValue=False):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingBool(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting
	def Temp(self, key, defaultValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingTemp(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting
	def ChooseString(self, key, defaultValue=None, choices=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingChooseString(self, key, defaultValue=defaultValue, choices=choices)
		self._settings[key] = setting
		return setting
	def Font(self, key, defaultValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingFont(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting
	def ByteArray(self, key, defaultValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingByteArray(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting
	def Index(self, key, defaultValue=None):
		if key in self._settings:
			raise ValueError('setting already present: %s' % key)
		setting = SettingIndex(self, key, defaultValue=defaultValue)
		self._settings[key] = setting
		return setting



