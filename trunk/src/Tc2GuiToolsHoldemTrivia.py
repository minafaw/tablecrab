
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
class FrameTool(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self._inited = False

		self.browser = QtGui.QTextEdit(self)
		self.browser.setReadOnly(True)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.browser)

	def toolTip(self):
		return 'HoldemTrivia'

	def displayName(self):
		return 'HoldemTrivia'

	def handleSetCurrent(self):
		if self._inited:
			return
		self._inited = True
		self.layout()
		holdemCalculations = PokerTools.HoldemCalculations()

		p = '<html><head></head>'
		p += '<body>'

		p += '<h4>Cards</h4>'
		p += 'Total number of seven card combinations: %s' % fmtInt(holdemCalculations.nSevenCardCombinations() )
		p += '<table border="1" cellspacing="0" ellpadding="0">'
		tr = '<tr><td>%s</td><td align="right">%s</td><td align="right">%s%%</td></tr>'
		p += tr % ('unpaired', fmtInt(holdemCalculations.nNoPairCombinations() ), holdemCalculations.pctNoPairCombinations(round_=2) )
		p += tr % ('one pair', fmtInt(holdemCalculations.nOnePairCombinations() ), holdemCalculations.pctOnePairCombinations(round_=2) )
		p += tr % ('two pair', fmtInt(holdemCalculations.nTwoPairCombinations() ), holdemCalculations.pctTwoPairCombinations(round_=2) )
		p += tr % ('three of kind', fmtInt(holdemCalculations.nThreeOfKindCombinations() ), holdemCalculations.pctThreeOfKindCombinations(round_=2) )
		p += tr % ('straights', fmtInt(holdemCalculations.nStraightCombinations() ), holdemCalculations.pctStraightCombinations(round_=2) )
		p += tr% ('flushs', fmtInt(holdemCalculations.nFlushCombinations() ), holdemCalculations.pctFlushCombinations(round_=2) )
		p += tr% ('full houses', fmtInt(holdemCalculations.nFullHouseCombinations() ), holdemCalculations.pctFullHouseCombinations(round_=2) )
		p += tr %  ('four of a kind', fmtInt(holdemCalculations.nFourOfKindCombinations() ), holdemCalculations.pctFourOfKindCombinations(round_=2) )
		p += tr % ('straight flushs', fmtInt(holdemCalculations.nStraightFlushCombinations() ), holdemCalculations.pctStraightFlushCombinations(round_=2) )
		p += tr %  ('royal flushs', fmtInt(holdemCalculations.nRoyalFlushCombinations() ), '%f' % holdemCalculations.pctRoyalFlushCombinations(round_=None) )
		p += '</table>'

		# see: Brian Alspach --> http://www.math.sfu.ca/~alspach/comp16/
		p += '<h4>Flop</h4>'
		p += 'there are %s possible 3 card cobinations on the flop' % fmtInt(holdemCalculations.nFlopCombinations() )
		p += '<ul>'
		p += '<li>flop is a straight flush: %s%%' % holdemCalculations.pctFlopIsStraightFlush(round_=2)
		p += '<li>flop is three of a kind: %s%%' % holdemCalculations.pctFlopIsThreeOfKind(round_=2)
		p += '<li>flop is a straight: %s%%' % holdemCalculations.pctFlopIsStraight(round_=2)
		p += '<li>flop is a flush: %s%%' % holdemCalculations.pctFlopIsFlush(round_=2)
		p += '<li>flop is a pair: %s%%' % holdemCalculations.pctFlopIsPair(round_=2)
		p += '<li>flop contains two suited cards: %s%%' % holdemCalculations.pctFlopIsTwoSuited(round_=2)
		p += '<li>flop contains two connected cards: %s%%' % holdemCalculations.pctFlopIsTwoConnected(round_=2)
		p += '</ul>'

		propFlopPair = holdemCalculations.pFlopPair()
		p += 'if no player holds a pocket pair, what is the chance of noone making a pair on the flop'
		p += '<table border="1" cellspacing="0" cellpadding="0">'
		p += '<tr><th>nPlayers</th><th>Chance</th></tr>'
		for i in range(2, 11):
			n = PokerTools.probToPct( (1-propFlopPair)**i)
			p += '<tr><td>%s</td><td align="right">%.02f%%</td></tr>' % (i, n)
		p += '</table>'

		p += '<h4>Turn</h4>'
		p += 'there are %s possible 4 card combinations on the turn' % fmtInt(holdemCalculations.nTurnCombinations() )

		p += '<h4>River</h4>'
		p += '<li>there are %s possible 5 card combinations on the river' % fmtInt(holdemCalculations.nRiverCombinations() )

		p += '<h4>Starting hands</h4>'
		p += 'there are %s starting hands in holdem' % fmtInt(holdemCalculations.nStartingHands() )
		p += '<ul>'
		p += '<li>pocket pairs: %i (%.02f%%)' % (holdemCalculations.nPocketPairs(), holdemCalculations.pctPocketPairs(round_=2) )
		p += '<li>suited hands: %i (%.02f%%)' % (holdemCalculations.nPocketsSuited(),  holdemCalculations.pctPocketsSuited(round_=2) )
		p += '<li>unsuited hands: %i (%.02f%%)' % (holdemCalculations.nPocketsOffsuit(),  holdemCalculations.pctPocketsOffsuit(round_=2) )
		p += '<li>chance of being dealt a specific hand: %s%%' % holdemCalculations.pctStartingHand(round_=3)
		p += '</ul>'

		p +=  '<h4>Pocket pairs</h4>'
		p += '<ul>'
		p += '<li>there are %i ways to form a pocket pair' % holdemCalculations.nCombinationsPocketsPair()
		p += '<li>being dealt a specific pocket pair: %s%%' % holdemCalculations.pctPocketPair(round_=2)
		p += '<li>being dealt any pocket pair: %s%%' % holdemCalculations.pctPocketPairs(round_=2)
		p += '<li>flopping a set or better: %0.2f%%' % holdemCalculations.pctFlopSet()
		p += '</ul>'

		p += 'if you hold a pocket pair, what is the chance of at leat one villain holding a better one (1-9 villains)</th></tr>'
		p += '<table border="1" cellspacing="0" cellpadding="0">'
		p += '<tr><th>Pair</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th></tr>'
		for pair, data in holdemCalculations.pPocketPairsHigher():
			p += '<tr><td>%s</td>' % pair
			for prob, pct in data:
				p += '<td align="right">%s%%</td>' % pct
			p += '</tr>'
		p += '</table>'

		p += '<br><br>'
		p += 'chance that at least one overcard hits the flop if you hold a pair'
		p += '<table border="1" cellspacing="0" cellpadding="0">'
		p += '<tr><th>Pair</th><th>Chance</th></tr>'
		for pair, prob, pct in holdemCalculations.pPocketPairFlopOvercards():
			p += '<tr><td>%s</td><td>%.02f%%</td></tr>' % (pair, pct)
		p += '</table>'

		p += '</body></html>'
		self.browser.setHtml(p)

