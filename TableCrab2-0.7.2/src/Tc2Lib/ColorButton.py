
from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************
class ColorButton(QtGui.QPushButton):

	StyleSheet = 'background-color: %s;'
	colorChanged = QtCore.pyqtSignal(QtGui.QColor)

	def __init__(self, parent=None, defaultColor=None, toolTip=''):
		QtGui.QPushButton.__init__(self, parent)
		self._color = QtGui.QColor() if defaultColor is None else defaultColor
		self._defaultColor = self._color
		#NOTE: tool tips derrive style sheets from our button, so we can not really use it here
		self._toolTip = toolTip

		self.setColor(self._color)
		self.clicked.connect(self.onButtonClicked)

	def color(self):
		return self._color

	def setColor(self, color):
		self._color = color
		if color.isValid():
			self.setStyleSheet(self.StyleSheet % color.name() )
		else:
			self.setStyleSheet('')
		self.colorChanged.emit(color)

	def resetColor(self):
		self.setColor(self._defaultColor)

	def toolTip(self):
		return self._toolTip

	def setToolTip(self, text):
		self._toolTip = text

	def onButtonClicked(self):
		#NOTE: the dialog derrives its style sheet from the button, so we have to
		# use our parent as parent for the dialog
		color = QtGui.QColorDialog.getColor(self.color(), self.parent(), self.toolTip() )
		if color.isValid():
			self.setColor(color)


class GroupColorButton(QtGui.QLabel):

	colorChanged = QtCore.pyqtSignal(QtGui.QColor)

	def __init__(self, parent=None, defaultColor=None, text='', toolTip=''):
		QtGui.QLabel.__init__(self, text, parent)

		self._colorButton = ColorButton(parent=self, defaultColor=defaultColor, toolTip=toolTip)
		self._resetButton = QtGui.QPushButton('Reset', self)
		self.setBuddy(self._colorButton)

		self._colorButton.colorChanged.connect(lambda color: self.colorChanged.emit(color) )
		self._resetButton.clicked.connect(self._colorButton.resetColor)

	def color(self):
		return self._colorButton.color()

	def setColor(self, color):
		self._colorButton.setColor(color)

	def label(self):
		return self

	def colorButton(self):
		return self._colorButton

	def resetButton(self):
		return self._resetButton



















