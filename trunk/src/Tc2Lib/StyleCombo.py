

from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************
class StyleCombo(QtGui.QComboBox):

	styleChanged = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self, parent=None, style=None):
		QtGui.QComboBox.__init__(self, parent)
		#NOTE: QtGui.qApp.style().objectName() # undocumented, but works
		self._style = QtGui.qApp.style().objectName() if style is None else style
		self._styleDefault = self._style

		styleNames = QtGui.QStyleFactory().keys()
		self.addItems(styleNames)
		self.setStyle(self._style)
		#NOTE: for some reason pyqtSlot decorator is not working, so we connect old style here
		self.connect(self, QtCore.SIGNAL('currentIndexChanged(QString)'), self.setStyle)

	def style(self):
		return self._style

	def setStyle(self, style):
		self._style = style
		i = self.findText(style, QtCore.Qt.MatchFixedString)
		#TODO: we default style here, good idea or not?
		if i < 0:
			i = self.findText(self._styleDefault, QtCore.Qt.MatchFixedString)
			self._style = self._styleDefault
		self.setCurrentIndex(i)
		self.styleChanged.emit(style)

	def resetStyle(self):
		self.setStyle(self._styleDefault)

	def onButtonClicked(self):
		#NOTE: the dialog derrives its style sheet from the button, so we have to
		# use our parent as parent for the dialog
		color = QtGui.QColorDialog.getColor(self.color(), self.parent(), self.toolTip() )
		if color.isValid():
			self.setColor(color)


class GroupStyleCombo(QtGui.QLabel):

	styleChanged = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self, parent=None, style=None, text=''):
		QtGui.QLabel.__init__(self, text, parent)

		self._styleCombo = StyleCombo(parent=self, style=style)
		self._resetButton = QtGui.QPushButton('Reset', self)

		self._styleCombo.styleChanged.connect(lambda style: self.styleChanged.emit(style) )
		self._resetButton.clicked.connect(self._styleCombo.resetStyle)

	def style(self):
		return self._styleCombo.style()

	def setStyle(self, style):
		self._styleCombo.setStyle(style)

	def label(self):
		return self

	def styleCombo(self):
		return self._styleCombo

	def resetButton(self):
		return self._resetButton



















