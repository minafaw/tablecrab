""""""

from PyQt4 import QtCore, QtGui
import itertools
import PokerTools
import TexasHoldem
import HandTypesHoldemWidget
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
		self.valueChanged.connect(self.onValueChanged)
		self.setValue(self.floatValue)
	def onValueChanged(self, value):
		self.setFormat('%s%.02f%%' % (self.prefix, self.floatValue*100))
	def setValue(self, value):
		self.floatValue = value
		QtGui.QProgressBar.setValue(self, int(value*10000))
			

class FlopEvalWidget(QtGui.QFrame):
	
	
	def __init__(self, parent=None, styleSheet=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.handEval = TexasHoldem.HandEval()
		self.flopEval = FlopEval.FlopEval()
		
		self.labelHandRange = QtGui.QLabel('Select a hand range', self)
		self.handRangeWidget = HandTypesHoldemWidget.HandTypesHoldemWidget(parent=self, pct=15)
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
				['nStraightFlushs', 'StraightFlushs: ', None],
				['nQuads', 'Quads: ', None],
				['nFullHouses', 'FullHouse: ', None],
				['nFlushs', 'Flush: ', None],
				['nStraights', 'Straight: ', None],
				['nSets', 'Set: ', None],
				['nTwoPairs', 'TwoPair: ', None],
				['nOverPairs', 'OverPair: ', None],
				['nTopPairs', 'TopPair: ', None],
				['nPairs', 'Pair: ', None],
				['nFlushDraws', 'FlushDraw: ', None],
				['nStraightDraws', 'StraightDraw: ', None],
				]
		#TODO: hard code stylefroprogress bars. good idea or not?
		#some styles display progress text tothe right of the bar
		# obv we don't like that.
		style = QtGui.QStyleFactory.create('plastique')
		for i, data in enumerate(self.progressBars):
			widget = FloatProgressBar(self, data[1])
			widget.setStyle(style)
			self.progressBars[i][2] = widget
					
		
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
		
		
		box2 = QtGui.QHBoxLayout()
		box0.addLayout(box2)
			
		
		for i, data in enumerate(self.progressBars):
			if i == 0 or i == 6:
				box = QtGui.QVBoxLayout()
				box2.addLayout(box)
			box.addWidget(data[2])
		
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
			data[2].setValue(0.0)	
	
	def _setResult(self, result):
		nFlops = float(result['nFlops'])
		for data in self.progressBars:
			value = result[data[0]]
			if value:
				value = value / float(nFlops)
			data[2].setValue(value)
			
	def _makeResult(self):
		result = {}
		for data in self.progressBars:
			result[data[0]] = 0
		result['nFlops'] = 0
		return result
				
	def _evalFlop(self, hand, flop, result):
		result['nFlops'] += 1
		cards = list(hand.cards) + flop
		
		if self.handEval.getStraightFlush(cards):
			result['nStraightFlushs'] += 1
			return
		if self.handEval.getQuads(cards):
			result['nQuads'] += 1
			return
		#TODO: case flop is set
		if self.handEval.getFullHouse(cards):
			result['nFullHouses'] += 1
			return
		if self.handEval.getFlush(cards):
			result['nFlushs'] += 1
			return
		
		flushDraw = self.handEval.getFlush(cards, count=4)
		if flushDraw:
			result['nFlushDraws'] += 1
				
		if self.handEval.getStraight(cards):
			result['nStraights'] += 1
			return
						
		straightDraw = self.handEval.getInsideStraightDraw(cards)
		if straightDraw:
			result['nStraightDraws'] += 1
		straightDraw = self.handEval.getOutsideStraightDraw(cards)
		if straightDraw:
			result['nStraightDraws'] += 1	
				
		trips =  self.handEval.getTrips(cards)
		if trips:
			# filter flop trips
			n = len([i for i in flop if i in trips[:3]])
			if n < 3:
				result['nSets'] += 1
			return
				
		twoPair = self.handEval.getTwoPair(cards)
		if twoPair:
			# filter flop pairs
			pair1 = twoPair[:2]
			pair2 = twoPair[2:4]
			# count cards flop contributed to pairs
			n1 = len([i for i in flop if i in pair1])
			n2 = len([i for i in flop if i in pair2])
			if n1 == 1 and n2 == 1:
				# flopped 2pair
				result['nTwoPairs'] += 1
			elif n1 == 1 and n2 == 2:
				# flopped top pair	
				result['nTopPairs'] += 1
			elif n1 == 2 and n2 == 1:
				# flopped < top pair
				result['nPairs'] += 1
			elif n1 == 0 and n2 == 2 and twoPair[0].rank() > twoPair[4].rank():
				# we have an overpair
				result['nOverPairs'] += 1
			return
			
		pair = self.handEval.getPair(cards)
		if pair:
			# filter flop pair
			n = len([i for i in flop if i in pair[:2]])
			if n == 0:
				# we have a pocket pair
				if pair[0].rank() > pair[2].rank():
					# we have an overpair
					result['nOverPairs'] += 1
				else:
					result['nPairs'] += 1
			elif n == 1:
				if pair[0].rank() and not [i for i in flop if i.rank() > pair[0].rank()]:
					# we have topPair
					result['nTopPairs'] += 1
				else:
					result['nPairs'] += 1
			return
					
	def onButtonEvalFlopClicked(self):
		self._resetResult()
		flop = self.flopWidget.cards()
		handRange = self.handRangeWidget.handRange()
		result = self._makeResult()
		for hand in handRange:
			# skip hands with cards on flop
			if [i for i in hand.cards if i in flop]:
				continue
			self._evalFlop(hand, flop, result)
		self._setResult(result)
		
	def onButtonEvalRandomClicked(self):
		self._resetResult()
		handRange = self.handRangeWidget.handRange()
		result = self._makeResult()
		result.update(self.flopEval.evalHandRange(handRange))
		self._setResult(result)
			
	def onflopWidgetCardsSelectionChanged(self, widget):
		self.buttonEvalFlop.setEnabled(widget.cardCount() == 3)

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = FlopEvalWidget()
	gui.show()
	application.exec_()
