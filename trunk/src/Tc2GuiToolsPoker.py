
import Tc2Config
from Tc2Lib import PokerTools
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
def fmtInt(n):
	return Tc2Config.locale.toString(int(n))


#************************************************************************************
#
#************************************************************************************
class PaneNone(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

	def displayName(self):
		return 'None'

	def handleSetCurrent(self):
		pass




class PaneHoldemTrivia(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self._inited = False

		self.browser = QtGui.QTextEdit(self)
		self.browser.setReadOnly(True)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.browser)

	def displayName(self):
		return 'Holdem trivia'

	def handleSetCurrent(self):
		if self._inited:
			return
		self._inited = True
		self.layout()

		p = '<html><head></head>'
		p += '<body>'


		nHandsTotal = PokerTools.numSevenCardCombinations()
		p += '<h4>Cards</h4>'
		p += 'Total number of seven card combinations: %s' % fmtInt(nHandsTotal)
		p += '<table border="1" cellspacing="0" ellpadding="0">'
		nNoPair = PokerTools.numNoPair()
		p += '<tr><td>unpaired</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nNoPair),  PokerTools.probToPercent(nNoPair / float(nHandsTotal)) )

		nOnePair = PokerTools.numOnePair()
		p += '<tr><td>one pair</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nOnePair),  PokerTools.probToPercent(nOnePair / float(nHandsTotal)) )

		nTwoPair = PokerTools.numTwoPair()
		p += '<tr><td>two pair</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nTwoPair),  PokerTools.probToPercent(nTwoPair / float(nHandsTotal)) )

		nThreeOfKind = PokerTools.numThreeOfKind()
		p += '<tr><td>three of a kind</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nThreeOfKind),  PokerTools.probToPercent(nThreeOfKind / float(nHandsTotal)) )

		nStraights = PokerTools.numStraights()
		p += '<tr><td>straights</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nStraights),  PokerTools.probToPercent(nStraights / float(nHandsTotal)) )

		nFlushs = PokerTools.numFlushs()
		p += '<tr><td>flushs</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nFlushs),  PokerTools.probToPercent(nFlushs / float(nHandsTotal)) )

		nFullHouses = PokerTools.numFullHouses()
		p += '<tr><td >full houses</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nFullHouses),  PokerTools.probToPercent(nFullHouses / float(nHandsTotal)) )

		nFourOfKind = PokerTools.numFourOfKind()
		p += '<tr><td>four of a kind</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nFourOfKind),  PokerTools.probToPercent(nFourOfKind / float(nHandsTotal)) )

		nStraightFlushs = PokerTools.numStraightFlushs()
		p += '<tr><td>straight flushs</td><td align="right">%s</td><td align="right">%s%%</td></tr>' % (fmtInt(nStraightFlushs),  PokerTools.probToPercent(nStraightFlushs / float(nHandsTotal)) )

		p += '<tr><td>straight flushs</td><td align="right">%s</td><td align="right">%f%%</td></tr>' %  (4, PokerTools.probToPercent(4 / float(nHandsTotal), 20))

		p += '</table>'


		# see: Brian Alspach --> http://www.math.sfu.ca/~alspach/comp16/
		p += '<h4>Flop</h4>'
		p += 'there are %s possible 3 card cobinations on the flop' % fmtInt(PokerTools.binom(52, 3))
		p += '<ul>'
		p += '<li>flop is a straight flush: %s%%' % PokerTools.probToPercent(48 / PokerTools.binom(52, 3))
		p += '<li>flop is three of a kind: %s%%' % PokerTools.probToPercent(4*13 / PokerTools.binom(52, 3))	# or binom(4, 3)*13 / binom(52, 3)
		p += '<li>flop is a straight: %s%%' % PokerTools.probToPercent(  (4**3*12 - 48) / PokerTools.binom(52, 3) )
		p += '<li>flop is a flush: %s%%' % PokerTools.probToPercent(  ((PokerTools.binom(13, 3) - 12)*4) / PokerTools.binom(52, 3) )
		p += '<li>flop is a pair: %s%%' % PokerTools.probToPercent(  (PokerTools.binom(4, 2) *13*48) / PokerTools.binom(52, 3) )
		# 13  ways you can oick the first card * 12 you can pick the second * 39 you can pick the third * 2 combinations for the board
		p += '<li>flop contains two suited cards: %s%%' % PokerTools.probToPercent( (13*12*39*2) / PokerTools.binom(52, 3) )
		#TODO: dono if this calculation is correct
		p += '<li>flop contains two connected cards: %s%%' % PokerTools.probToPercent(PokerTools.prob(6, 51)*(1- PokerTools.prob(6, 50) )*4)
		p += '</ul>'

		propFlopPair = PokerTools.prob(6, 50) + PokerTools.prob(6, 49) + PokerTools.prob(6, 48)
		p += 'if no player holds a pocket pair, what is the chance of noone making a pair on the flop'
		p += '<table border="1" cellspacing="0" cellpadding="0">'
		p += '<tr><th>nPlayers</th><th>Chance</th></tr>'
		for i in range(2, 11):
			n = PokerTools.probToPercent( (1-propFlopPair)**i)
			p += '<tr><td>%s</td><td>%.02f%%</td></tr>' % (i, n)
		p += '</table>'



		p += '<h4>Turn</h4>'
		p += 'there are %s possible 4 card combinations on the turn' % fmtInt(PokerTools.binom(52, 4))

		p += '<h4>River</h4>'
		p += '<li>there are %s possible 5 card combinations on the river' % fmtInt(PokerTools.binom(52, 5))

		p += '<h4>Starting hands</h4>'
		nStartingHands = PokerTools.numStartingHands()
		p += 'there are %s starting hands in holdem' % fmtInt(nStartingHands)
		p += '<ul>'
		nPocketPairs = PokerTools.numPocketPairs()
		p += '<li>pocket pairs: %i (%.02f%%)' % (nPocketPairs, PokerTools.probToPercent(nPocketPairs / nStartingHands) )
		nSuitedHands = PokerTools.binom(13, 2) * PokerTools.binom(4, 1)
		p += '<li>suited hands: %i (%.02f%%)' % (nSuitedHands, PokerTools.probToPercent(nSuitedHands / nStartingHands) )
		nUnsuitedHands = PokerTools.binom(13, 2) * PokerTools.binom(4, 1) * PokerTools.binom(3, 1)
		p += '<li>unsuited hands: %i (%.02f%%)' % (nUnsuitedHands,   PokerTools.probToPercent(nUnsuitedHands / nStartingHands) )
		p += '<li>chance of being dealt a specific hand: %s%%' % PokerTools.probToPercent( PokerTools.prob(1, 52)* PokerTools.prob(1, 51) )
		p += '</ul>'

		p +=  '<h4>Pocket pairs</h4>'
		p += '<ul>'
		p += '<li>there are %i ways to form a pocket pair' % PokerTools.binom(4, 2)
		p += '<li>being dealt a specific pocket pair: %s%%' % PokerTools.probToPercent( PokerTools.binom(4, 2) / PokerTools.binom(52, 2) )
		p += '<li>being dealt any pocket pair: %s%%' % PokerTools.probToPercent(PokerTools.binom(13, 2) / PokerTools.binom(52, 2) )
		pFlopSet = ( (float(2)/50) + (float(2)/49) + (float(2)/48) ) * 100
		p += '<li>flopping a set or better: every %0.2f times (%0.2f%%)' % (100/pFlopSet,  pFlopSet)
		p += '</ul>'


		p += 'if you hold a pocket pair, what is the chance of at leat one villain holding a better one (1-9 villains)</th></tr>'
		p += '<table border="1" cellspacing="0" cellpadding="0">'
		p += '<tr><th>Pair</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th></tr>'
		for rank in range(len(PokerTools.Card.Ranks) -2, -1, -1):
			p += '<tr><td>%s</td>' %(PokerTools.Card.Ranks[rank] * 2)
			for i in xrange(1, 10):
				p += '<td>%s%%</td>' % PokerTools.probToPercent( PokerTools.probHigherPair(rank, nOponents=i) )
			p += '</tr>'
		p += '</table>'

		p += '<br><br>'
		p += 'chance that at least one overcard hits the flop if you hold a pair'
		p += '<table border="1" cellspacing="0" cellpadding="0">'
		p += '<tr><th>Pair</th><th>Chance</th></tr>'
		for rank in range(len(PokerTools.Card.Ranks) -2, -1, -1):
			n = round(PokerTools.percentOvercardsToPair(rank, 3), 2)
			p += '<tr><td>%s</td><td>%s%%</td></tr>' % (PokerTools.Card.Ranks[rank] * 2, n)
		p += '</table>'



		p += '</body></html>'
		self.browser.setHtml(p)


#************************************************************************************
#
#************************************************************************************
class FrameTool(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/PokerTools'
	SettingsKeyIndexToolCurrent = SettingsKeyBase + '/ToolCurrent'

	PaneClasses = (
			PaneNone,
			PaneHoldemTrivia,
			)

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.comboBox = QtGui.QComboBox(self)
		self.stack = QtGui.QStackedWidget(self)
		for paneClass in self.PaneClasses:
			pane = paneClass(self)
			self.addPane(pane)
		self.comboBox.currentIndexChanged.connect(self.onComboCurrentIndexChanged)

		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.comboBox)
		grid.row()
		grid.col(self.stack)

	def addPane(self, pane):
		self.stack.addWidget(pane)
		self.comboBox.addItem(pane.displayName(), QtCore.QVariant(self.stack.count() -1) )

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		value, ok = Tc2Config.settingsValue(self.SettingsKeyIndexToolCurrent, 0).toInt()
		if ok:
			self.setCurrentIndex(value)

	def onComboCurrentIndexChanged(self, i):
		self.stack.setCurrentIndex(i)
		pane = self.stack.currentWidget()
		pane.handleSetCurrent()
		Tc2Config.settingsSetValue(self.SettingsKeyIndexToolCurrent, i)

	def currentIndex(self):
		return self.stack.currentIndex()

	def setCurrentIndex(self, i):
		if i > -1 and i < self.stack.count():
			self.comboBox.setCurrentIndex(i)
			return True
		return False

	def toolName(self):
		return 'PokerTools'





