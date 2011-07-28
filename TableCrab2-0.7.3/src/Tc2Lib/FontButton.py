
from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************
class FontButton(QtGui.QPushButton):

	fontChanged = QtCore.pyqtSignal(QtGui.QFont)

	def __init__(self, parent=None, defaultFont=None, toolTip=''):
		QtGui.QPushButton.__init__(self, parent)
		self._font = QtGui.QFont() if defaultFont is None else defaultFont
		self._defaultFont = self._font
		self._toolTip = toolTip

		self.setFont(self._font)
		self.clicked.connect(self.onButtonClicked)

	def font(self):
		return self._font

	def setFont(self, font):
		self._font = font
		self.setText( QtCore.QString('%1 %2').arg(font.family()).arg(font.pointSize()) )
		self.fontChanged.emit(font)

	def resetFont(self):
		self.setFont(self._defaultFont)

	def toolTip(self):
		return self._toolTip

	def setToolTip(self, text):
		self._toolTip = text

	def onButtonClicked(self):
		font, ok = QtGui.QFontDialog.getFont(self.font(), self, self.toolTip() )
		if ok:
			self.setFont(font)


class GroupFontButton(QtGui.QLabel):

	fontChanged = QtCore.pyqtSignal(QtGui.QFont)

	def __init__(self, parent=None, defaultFont=None, text='', toolTip=''):
		QtGui.QLabel.__init__(self, text, parent)

		self._fontButton = FontButton(parent=self, defaultFont=defaultFont, toolTip=toolTip)
		self._resetButton = QtGui.QPushButton('Reset', self)
		self.setBuddy(self._fontButton)

		self._fontButton.fontChanged.connect(lambda font: self.fontChanged.emit(font) )
		self._resetButton.clicked.connect(self._fontButton.resetFont)

	def font(self):
		return self._fontButton.font()

	def setFont(self, font):
		self._fontButton.setFont(font)

	def label(self):
		return self

	def fontButton(self):
		return self._fontButton

	def resetButton(self):
		return self._resetButton


