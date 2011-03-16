

from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************
#TODO: currently values are handled case insensitively. value is guaranteed to
# always be the corrosponding value from the list of values
class ComboBox(QtGui.QComboBox):

	valueChanged = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self, parent=None, defaultValue='', values=QtCore.QStringList()):
		"""
		@param vaules: (QStringList)
		"""
		QtGui.QComboBox.__init__(self, parent)
		if not values.contains(defaultValue, QtCore.Qt.CaseInsensitive):
			raise ValueError('no such value: %s' % defaultValue)
		self._value = None
		self._defaultValue = defaultValue
		if len(values):
			self.addItems(values)
		self.setValue(defaultValue)
		#NOTE: for some reason pyqtSlot decorator is not working, so we connect old style here
		self.connect(self, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setValue)

	def value(self):
		return self._value

	def setValue(self, value):
		"""
		@return: (bool) True if the value could be set, False otherwise
		"""
		i = self.findText(value, QtCore.Qt.MatchFixedString)
		if i > -1:
			value = self.itemText(i)
			if self._value != value:
				self._value = self.itemText(i)
				self.setCurrentIndex(i)
				self.valueChanged.emit(value)
			return True
		return False

	def resetValue(self):
		self.setValue(self._defaultValue)


class GroupComboBox(QtGui.QLabel):

	valueChanged = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self, parent=None, defaultValue=None, values=None, text=''):
		QtGui.QLabel.__init__(self, text, parent)

		self._comboBox = ComboBox(parent=self, defaultValue=defaultValue, values=values)
		self._resetButton = QtGui.QPushButton('Reset', self)

		self._comboBox.valueChanged.connect(lambda value: self.valueChanged.emit(value) )
		self._resetButton.clicked.connect(self._comboBox.resetValue)

	def value(self):
		return self._comboBox.value()

	def setValue(self, value):
		self._comboBox.setValue(value)

	def label(self):
		return self

	def comboBox(self):
		return self._comboBox

	def resetButton(self):
		return self._resetButton



















