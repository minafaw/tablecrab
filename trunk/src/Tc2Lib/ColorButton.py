
from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************
class ColorButton(QtGui.QPushButton):

	StyleSheet = 'background-color: %s;'
	colorChanged = QtCore.pyqtSignal(QtGui.QColor)

	def __init__(self, parent=None, color=None, toolTip=''):
		QtGui.QPushButton.__init__(self, parent)
		self._color = QtGui.QColor() if color is None else color
		#NOTE: tool tips derrive style sheets from our button, so we can not really use it here
		self._toolTip = toolTip
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
		self.setColor(QtGui.QColor() )

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

