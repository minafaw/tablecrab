""""""

#TODO: how to give feedback when user enters an invalid hand range? current approach
#      of flashing handRangeButtons is a bit well ..weird.

from PyQt4 import QtCore, QtGui
import itertools
import PokerTools
import TexasHoldem
import HandRangeWidget
import CardSelectorWidget
import FlopEval
#************************************************************************************
#
#************************************************************************************
class FloatProgressBar(QtGui.QProgressBar):
	def __init__(self, parent=None, prefix=''):
		QtGui.QProgressBar.__init__(self, parent)
		self.floatValue = 0.0
		self.prefix = prefix
		self.setMaximum(10000)
		self.setValue(self.floatValue)
	def setValue(self, value):
		self.floatValue = value
		QtGui.QProgressBar.setValue(self, int(value*10000))
		value = self.floatValue*100
		if value and round(value, 2) == 0:
			fmt = '%s+%.02f%%' % (self.prefix, value)
		else:
			fmt = '%s%.02f%%' % (self.prefix, value)
		self.setFormat(fmt)
			

class FlopEvalWidget(QtGui.QFrame):
	
	
	class ErrTimer(QtCore.QTimer):
		def __init__(self, parent):
			QtCore.QTimer.__init__(self, parent)
			self.setSingleShot(False)
			self.timeout.connect(self.onTimeout)
			self.handRange = None
			self.handRangeText = None
			self.n = 0
		def start(self):
			self.handRange = self.parent().handRangeWidget.handRangeFromHandTypes()
			self.handRangeText = self.parent().handRangeWidget.handRangeText()
			QtCore.QTimer.start(self, 100)
		def onTimeout(self):
			self.n += 1
			if self.n == 1:
				self.parent().handRangeWidget.setHandRange(
				PokerTools.HandRangeHoldem.fromString(
						'K4o,K3o,Q4o, T4o,T3o,94o, 74o,73o,64o'
						))
			elif self.n == 2:
				self.parent().handRangeWidget.setHandRange(self.handRange)
				self.parent().handRangeWidget.setHandRangeText(self.handRangeText)
				self.n = 0
				self.stop()
		
	
	def __init__(self, parent=None, styleSheet=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.handEval = TexasHoldem.HandEval()
		self.errTimer = self.ErrTimer(self)
		
		self.labelHandRange = QtGui.QLabel('Select a hand range', self)
		self.handRangeWidget = HandRangeWidget.HandRangeWidget(parent=self, pct=15)
		self.handRangeWidget.invalidHandRangeEntered.connect(self.onInvalidHandRangeEntered)
		self.labelFlop = QtGui.QLabel('Select a flop', self)
		self.labelFlop.setWordWrap(True)
		self.flopWidget = CardSelectorWidget.CardSelectorWidget(parent=self, maxCards=3)
		self.flopWidget.cardsSelectionChanged.connect(self.onflopWidgetCardsSelectionChanged)
				
		self.buttonEvalFlop = QtGui.QPushButton('Evaluate flop', self)
		self.buttonEvalFlop.setEnabled(False)
		self.buttonEvalFlop.clicked.connect(self.onButtonEvalFlopClicked)
		self.buttonEvalRandom = QtGui.QPushButton('Evaluate randon', self)
		self.buttonEvalRandom.clicked.connect(self.onButtonEvalRandomClicked)
		
		self.progressBars = [
				['StraightFlush', None],
				['Quads', None],
				['FullHouse', None],
				['Flush', None],
				['Straight', None],
				['Set', None],
				['TwoPair', None],
				['OverPair', None],
				['TopPair', None],
				['Pair', None],
				['FlushDraw', None],
				['StraightDraw', None],
				]
		#TODO: hard code stylefroprogress bars. good idea or not?
		#some styles display progress text tothe right of the bar
		# obv we don't like that.
		style = QtGui.QStyleFactory.create('plastique')
		for i, data in enumerate(self.progressBars):
			widget = FloatProgressBar(self, data[0] + ': ')
			widget.setStyle(style)
			self.progressBars[i][1] = widget
					
		
		# layout
		
		box0 = QtGui.QVBoxLayout(self)
		
		box1 = QtGui.QHBoxLayout()
		box0.addLayout(box1)
		
		box2 = QtGui.QVBoxLayout()
		box1.addLayout(box2)
		box2.addWidget(self.labelHandRange)
		box2.addWidget(self.handRangeWidget)
		
		box2 = QtGui.QVBoxLayout()
		box1.addLayout(box2)
		box2.addWidget(self.labelFlop)
		box2.addWidget(self.flopWidget, 0, QtCore.Qt.AlignHCenter)
		box2.addWidget(self.buttonEvalFlop)
		box2.addWidget(self.buttonEvalRandom)
			
		hLine = QtGui.QFrame()
		hLine.setFrameStyle(hLine.HLine | hLine.Sunken)
		box0.addWidget(hLine)
			
		box2 = QtGui.QHBoxLayout()
		box0.addLayout(box2)
				
		for i, data in enumerate(self.progressBars):
			if i == 0 or i == 6:
				box = QtGui.QVBoxLayout()
				box2.addLayout(box)
			box.addWidget(data[1])
		
		s = QtGui.QVBoxLayout()
		s.addStretch(999)
		box0.addLayout(s)
		
		#TODO: add right stretch. good idea or not?
		s = QtGui.QHBoxLayout()
		s.addStretch(999)
		box1.addLayout(s)
		
	def handleFontChanged(self, font=None):
		self.handRangeWidget.handleFontChanged(font=font)
		self.flopWidget.handleFontChanged(font=font)
		
	def _resetResult(self):
		for data in self.progressBars:
			data[1].setValue(0.0)	
	
	def _setResult(self, result):
		for data in self.progressBars:
			p = result[data[0]]
			data[1].setValue(p)
			
	def onButtonEvalFlopClicked(self):
		self._resetResult()
		flop = self.flopWidget.cards()
		handRange = self.handRangeWidget.handRange()
		if handRange is None:
			return
		result = FlopEval.evalBoard(handRange, flop)
		self._setResult(result)
		
	def onButtonEvalRandomClicked(self):
		self._resetResult()
		handRange = self.handRangeWidget.handRange()
		if handRange is None:
			return
		result = FlopEval.evalHandRange(handRange)
		self._setResult(result)
			
	def onflopWidgetCardsSelectionChanged(self, widget):
		self.buttonEvalFlop.setEnabled(widget.cardCount() == 3)
		
	def onInvalidHandRangeEntered(self, handRangeWidget):
		self.errTimer.start()

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = FlopEvalWidget()
	gui.show()
	application.exec_()
