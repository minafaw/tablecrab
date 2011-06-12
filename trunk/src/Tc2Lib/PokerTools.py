
import functools
import itertools
import math
import random
import re
#************************************************************************************
# math
#************************************************************************************
def binom(n, k):
	if 0 <= k <= n:
		p = 1
		for t in xrange(min(k, n - k)):
			p = (p * (n - t)) // (t + 1)
		return float(p)
	else:
		return float(0)

# taken from: http://introcs.cs.princeton.edu/21function/ErrorFunction.java.html
def cdf(z):
	return 0.5 * (1.0 + erf(z / math.sqrt(2.0)) )

def deviation(variance):
	return math.sqrt(variance)

def distance(x, y):
	return x - y

try:
	from math import erf		# new in Python 2.7
except ImportError:
	# taken from: http://introcs.cs.princeton.edu/21function/ErrorFunction.java.html
	def erf(z):
		"""error function."""
		t = 1.0 / (1.0 + 0.5 * abs(z))
		ans = 1 - t * math.exp( -z * z - 1.26551223 +
				t * ( 1.00002368 +
				t * ( 0.37409196 +
				t * ( 0.09678418 +
				t * (-0.18628806 +
				t * ( 0.27886807 +
				t * (-1.13520398 +
				t * ( 1.48851587 +
				t * (-0.82215223 +
				t * 0.17087277)))))))))
		return ans if z >= 0 else -ans

def expectation(distribution):
	result = 0.0
	for outcome, p in distribution:
		result += p * outcome
	return result

def factorial(n):
	total = n
	while n > 1:
		total *= (n - 1)
		n -= 1
	return total

def mean(values):
	return sum(values) / float(len(values))

def normalDistribution(x, d, m, v):
	return (
		(1 / (d * math.sqrt(2 * math.pi)) ) *
		math.exp( - ( (x - m)**2 ) / (2*v) )
		)

def oddsToPct(odds):
	return 100.0 / odds
	
def oddsFromPct(pcnt):
	return (100.0 / pcnt) -1

def prob(a, b):
	return float(a) / b
	
def probComplement(p):
	return 1 - p
	
def probFromPct(pct):
	return p / 100.0
	
def probIntersection(p1, p2):
	return p1 * p2

def probToPct(p):
	return p * 100

def probUnion(p1, p2, intersection=None):
	if intersection is None:
		return p1 + p2
	return  p1 + p2 - intersection

def pct(value, base=100):
	return 100*float(value)/base
	
def pctBase(value, percent):
	return 100*float(value) / percent

def pctValue(percent, base=100):
	return float(base) / 100 * percent

def product(numbers):
	return functools.reduce(operator.mul, numbers, 1)

def variance(ev, values):
	p = [distance(i, ev)**2 for i in values]
	return sum(p) / len(p)

def variationK(ev, stdDeviation):
	return (stdDeviation / ev) if ev else stdDeviation

#************************************************************************************
# others
#************************************************************************************
def splitIterable(iterable, condition):
	result = []
	for c, group in itertools.groupby(iterable, key=condition):
		if not c:
			result.append( [i for i in group] )
	return result

#************************************************************************************
#
#************************************************************************************
class Card(int):
	"""card object"""
	Ranks = range(0, 13)
	Suits = range(0, 4)
	MinCard = 0
	MaxCard = len(Ranks) * len(Suits) -1
	RankNames = '23456789TJQKA'
	SuitNames = 'hdcs'
	RankNamesDict = {
			0: ('deuce', 'deuces'),
			1: ('trey', 'treys'),
			2: ('four', 'fours'),
			3: ('five', 'fives'),
			4: ('six', 'sixes'),
			5: ('seven', 'sevens'),
			6: ('eight', 'eights'),
			7: ('nine', 'nines'),
			8: ('ten', 'tens'),
			9: ('jack', 'jacks'),
			10: ('queen', 'quens'),
			11: ('king', 'kings'),
			12: ('ace', 'aces'),
			}
	SuitNamesDict = {
			0: ('heart', 'hearts'),
			1: ('diamond', 'diamonds'),
			2: ('cross', 'crosses'),
			3: ('spade', 'spades'),
			}
		
	def __new__(klass, no):
		"""creates a new card
		@param no: (int or string) can be either a string like 'Ah' or another card or an integer card value
		"""
		if isinstance(no, (int, long)):
			if no < klass.MinCard or no > klass.MaxCard:
				raise ValueError('invalid card')
		else:
			try:
				rank = klass.RankNames.index(no[0])
				suit = klass.SuitNames.index(no[1])
			except IndexError:
				raise ValueError('invalid card')
			no = suit * len(klass.RankNames) + rank
		return int.__new__(klass, no)

	def __repr__(self):
		return '<%s.%s object %r at 0x%x>' % (__name__, self.__class__.__name__, self.name(), id(self))
	def __str__(self): return self.__repr__()
	def __unicode__(self): return self.__repr__()

	def __eq__(self, other): return self.value() == other.value()
	def __ne__(self, other): return not self.__eq__(other)
	
	def name(self):
		"""returns the string representation of the card, i.e. 'Ah'
		@return: (str) card
		"""
		return self.rankName() + self.suitName()

	def rank(self):
		"""returns the rank of the card
		@return: (int) rank
		"""
		return self % len(self.RankNames)

	def rankName(self):
		"""returns the string representation of the rank of the the card, i.e. 'A'
		@return: (str) shape
		"""
		return self.RankNames[self.rank()]

	def suit(self):
		"""returns the suite of the card
		@return: (int) suit
		"""
		return int(self / len(self.RankNames))

	def suitName(self):
		"""returns the string representation of the suit of the the card, i.e. 'h'
		@return: (str) shape
		"""
		return self.SuitNames[self.suit()]

	def value(self):
		"""returns the integer representation of the card
		@return: (int) value
		"""
		return int(self)


class CardDeck(object):
	"""poker card deck object"""
	__fields__ = ('_cards', )
	Cards = [Card(no) for no in xrange(Card.MinCard, Card.MaxCard +1)]

	def __init__(self):
		"""creates a new odered 52 card deck"""
		self._cards = None
		self.reset()

	def reset(self):
		"""resets the deck to an ordered set of 52 cards"""
		self._cards = self.Cards[:]

	def __iter__(self):
		return iter(self._cards)

	def __len__(self): return len(self._cards)

	def shuffle(self, shuffle=random.shuffle):
		'''shuffles the deck in place
		@param shuffle: (func) function to shuffle the decs list of cards in-place
		'''
		shuffle(self._cards)

	def nextCard(self):
		"""pops and returns the next card in the deck
		@return: (L{Card})
		"""
		return self._cards.pop(0)


class Hand(object):
	def __init__(self, *cards):
		self.cards = cards
		# no duplicate cards allowed in a hand
		for card in cards:
			if cards.count(card) > 1:
				raise ValueError('duplicate cards in hand')
	def __eq__(self, other):
		if len(self.cards) == len(other.cards):
			if not [card for card in self.cards if card not in other.cards]:
				return True
		return False
	def __ne__(self, other): return not self.__eq__(other)
	def toString(self):
		return '[%s]' % ' '.join([card.name() for card in self.cards]) 

#************************************************************************************
#
#************************************************************************************
def genHandTypes():
	"""
	@return: (list) of hand types ['AA', 'AKs', 'AKo', ... '32o', '22']
	"""
	result = []
	ranks = Card.RankNames[::-1]
	for iRank, rank in enumerate(ranks):
		result.append(rank + rank)
		for rank2 in ranks[iRank+1:]:
			result.append(rank + rank2 + 's')
			result.append(rank + rank2 + 'o')
	return result

#for i in genHandTypes():
#	print i

def genHandTypeTable():
	"""creates a table of hand types
	AA   AKs   AQs  ...
	AKo  KK     ...
	...
	@return: (list)
	"""
	handTypes = genHandTypes()
	cardRankNames = Card.RankNames[::-1]
	table = []
	for i in xrange(13):
		table.append( [None for i in xrange(13)] )
		
	for handType in handTypes:
		x = cardRankNames.index(handType[1])
		y = cardRankNames.index(handType[0])
		if handType[-1] == 'o':
			table[x][y] = handType
		else:
			table[y][x] = handType
	return table

def handTypeFromHand(hand):
	"""
	@param hand: L{Hand} containing two L{Card}s
	@return:(str) hand type of the hand ('AKo' or whatevs)
	"""
	if len(hand.cards) != 2:
		raise ValueError('expected a two card hand')
	
	card0, card1  = hand.cards
	if card0.rank() == card1.rank():
		return card0.rankName() + card1.rankName()
	flag = 's'
	if card1.suit() != card0.suit():
		flag= 'o'
	if card1.rank() > card0.rank():
		return card1.rankName() + card0.rankName() + flag
	return card0.rankName() + card1.rankName()+ flag

#************************************************************************************
# hand ranges
#************************************************************************************
#NOTE: neither is this beast below 100% compatible to PokerTracker nor is it tested
# in any depth.
class HandRange(object):
	
	class ParseError(Exception): pass
	
	ReRanks = '|'.join(Card.RankNames)
	ReSuits = '|'.join(Card.SuitNames)
	ReCard = '(%s)(%s)' % (ReRanks, ReSuits)
	PatHand = re.compile('''
					\A
					(?P<card1>%s)
					(?P<card2>%s)
					\Z
					''' % (ReCard, ReCard), re.X)
	PatHandTypePair = re.compile('''
					\A
					(?P<rank>%s)
					(?P=rank)
					(?P<qualifier>\+)?
					\Z
					''' % ReRanks, re.X)
	PatHandTypePairRange = re.compile('''
					\A(?P<rank1>%s)
					(?P=rank1)
					\-
					(?P<rank2>%s)
					(?P=rank2)
					\Z
					''' % (ReRanks, ReRanks), re.X)
	PatHandTypeSuit = re.compile('''
					\A
					(?P<rank1>%s)
					(?P<rank2>%s)
					(?P<suit>s|o)?
					(?P<qualifier>\+)?
					\Z
					''' % (ReRanks, ReRanks), re.X)
	PatHandTypeSuitRange = re.compile('''
					\A
					(?P<rank1>%s)
					(?P<rank2>%s)
					(?P<suit1>s|o)?
					\-
					(?P<rank3>%s)
					(?P<rank4>%s)
					(?P<suit2>s|o)?
					\Z
					''' % (ReRanks, ReRanks, ReRanks, ReRanks), re.X)
	
	def __init__(self, hands=None):
		self.hands = []
		if hands is not None:
			for hand in hands:
				if hand not in self.hands:
					self.hands.append(hand) 
			
	@classmethod
	def fromString(klass, string):
		handRange = klass()
		# clean string
		p = string.replace(' ', '').replace('\t', '')
		p = p.split(',')
		for s in p:
			
			# substring is a hand --> 'Kh7d'
			#
			result = klass.PatHand.match(s)
			if result is not None:
				card1, card2 = Card(result.group('card1')), Card(result.group('card2'))
				hand = Hand(card1, card2)
				if hand not in handRange.hands:
					handRange.hands.append(hand)
				continue
				
			# substring is a handTypePair --> 'TT' or 'TT+'
			#
			result = klass.PatHandTypePair.match(s)
			if result is not None:
				rank = result.group('rank')[0]
				hands =  klass._combinationsPair(rank)
				for hand in hands:
					if hand not in handRange.hands:
						handRange.hands.append(hand)
				
				# expand pattern if necessary
				qualifier = result.group('qualifier')
				if qualifier:
					iRank = Card.RankNames.index(rank)
					for otherRank in Card.RankNames[iRank +1:]:
						p.append(otherRank + otherRank)
				continue
								
			# substring is a handTypeSuit --> 'KTs', 'KTs+', 'KTo' or 'KT'
			#
			#NOTE: PokerTracker handles 'KT' but not 'KT+', we do
			result = klass.PatHandTypeSuit.match(s)
			if result is not None:
				rank1 = result.group('rank1')
				rank2 = result.group('rank2')
				rank1, rank2 = klass._sortedCardRanks(rank1, rank2, revert=True)
				suit = result.group('suit')
				qualifier = result.group('qualifier')
										
				# got a pair - assume typo - PokerStove does so as well (?)
				if rank1 == rank2:
					if qualifier:
						p.append('%s%s%s' % (rank1, rank1, qualifier))
					else:
						p.append('%s%s' % (rank1, rank1))
					continue
							
				if suit == 's':
					hands = klass._combinationsSuited(rank1, rank2)
				elif suit == 'o':
					hands = klass._combinationsOffsuit(rank1, rank2)
				else:
					hands = klass._combinations(rank1, rank2)
				for hand in hands:
					if hand not in handRange.hands:
						handRange.hands.append(hand)
				
				# expand pattern if necessary
				if qualifier:
					iRank = Card.RankNames.index(rank2)
					for otherRank in Card.RankNames[iRank +1:]:
						if otherRank == rank1: continue
						if suit:
							p.append(rank1 + otherRank + suit)
						else:
							p.append(rank1 + otherRank + 's')
							p.append(rank1 + otherRank + 'o')
				continue
				
			# substring is a handTypePairRange --> '22-TT'
			#
			result = klass.PatHandTypePairRange.match(s)
			if result is not None:
				rank1 = result.group('rank1')
				rank2 = result.group('rank2')
				rank1, rank2 = klass._sortedCardRanks(rank1, rank2, revert=False)
				iRank1 = Card.RankNames.index(rank1)
				iRank2 = Card.RankNames.index(rank2)
														
				# expand pattern
				ranks = Card.RankNames[iRank1:iRank2+1]
				for rank in ranks:
					p.append(rank + rank)
				continue
							
			# substring is a handTypeSuiteRange --> 'K7s-KTs', 'KT-K7', 'KTo-K7', ...
			#
			result = klass.PatHandTypeSuitRange.match(s)
			if result is not None:
				rank1 = result.group('rank1')
				rank2 = result.group('rank2')
				rank1, rank2 = klass._sortedCardRanks(rank1, rank2, revert=True)
				rank3 = result.group('rank3')
				rank4 = result.group('rank4')
				rank3, rank4 = klass._sortedCardRanks(rank3, rank4, revert=True)
				# sort rank2 and 4 once again so we get ascending ranks for expanding
				rank2, rank4 = klass._sortedCardRanks(rank2, rank4, revert=False)
				if rank1 != rank3:
					raise klass.ParseError('invalid range: %s' % s)
				# determine suit
				suit1 = result.group('suit1')
				suit2 = result.group('suit2')
				if suit1:
					suit = suit1
				elif suit2:
					suit = suit2
				else:
					suit = None
							
				# expand pattern
				iRank2 = Card.RankNames.index(rank2)
				iRank4 = Card.RankNames.index(rank4)
				ranks = Card.RankNames[iRank2:iRank4+1]
				for rank in ranks:
					if suit:
						p.append(rank1 + rank + suit)
					else:
						p.append(rank1 + rank + 's')
						p.append(rank1 + rank + 'o')		
				continue
		
		# finally		
		return handRange
			
	@classmethod
	def _sortedCardRanks(self, rank1, rank2, revert=False):
		iRank1 = Card.RankNames.index(rank1)
		iRank2 = Card.RankNames.index(rank2)
		if revert and iRank1 < iRank2:
			return [rank2, rank1]
		elif not revert and iRank2 < iRank1:
			return [rank2, rank1]
		return [rank1, rank2]
		
	@classmethod
	def _combinations(klass, rank1, rank2):
		cards1 = [Card(rank1 + suit) for suit in Card.SuitNames]
		cards2 = [Card(rank2 + suit) for suit in Card.SuitNames]
		result = []
		for card1, card2 in itertools.product(cards1, cards2):
			result.append(Hand(card1, card2))
		return result	
	
	@classmethod
	def _combinationsPair(klass, rank):
		cards = [Card(rank + suit) for suit in Card.SuitNames]
		return [Hand(*cards) for cards in itertools.combinations(cards, 2)]
		
	@classmethod
	def _combinationsSuited(klass, rank1, rank2):
		result = []
		for suit in Card.SuitNames:
			hand = Hand(Card(rank1 + suit), Card(rank2 + suit))
			result.append(hand)
		return result
			
	@classmethod
	def _combinationsOffsuit(klass, rank1, rank2):
		return [hand for hand in klass._combinations(rank1, rank2) if hand.cards[0].suit() != hand.cards[1].suit()]
			
	def toString(self):

		class HandType(object):
			def __init__(self, handtype, hands):
				self.handType = handType
				self.hands = hands
				self.rank1 = Card.RankNames.index(handType[0])
				self.rank2 = Card.RankNames.index(handType[1])
								
		# dump our hands to handType table
		table = genHandTypeTable()
		for iRow, row in enumerate(table):
			for iCol, handType in enumerate(row):
				hands = []
				for hand in self.hands:
					if handTypeFromHand(hand) == handType:
						hands.append(hand)
				##print handType, hands
				row[iCol] = HandType(handType, hands)
				
		result = []
		pairs =[]
		suited = []
		offsuit = []
		
		for row in table:
			for handType in row:
				if len(handType.handType) == 2:
					nCardsExpected = 6
					rankSignificant = 'rank1'
					rng = pairs
				elif handType.handType[-1] == 's':
					nCardsExpected = 4
					rankSignificant = 'rank2'
					rng = suited
				else:
					nCardsExpected = 12
					rankSignificant = 'rank2'
					rng = offsuit
				
				if not handType.hands:
					continue
				if len(handType.hands)  == nCardsExpected:
					if not rng:
						rng.append([])
					last = rng[-1]
					if not last:
						last.append(handType)
					else:
						rankCurrent = getattr(handType, rankSignificant)
						rankLast = getattr(last[-1], rankSignificant)
						if rankCurrent +1 == rankLast:
							last.append(handType)
						else:
							rng.append([handType, ])
				else:
					rng.append([handType, ])
					
				
		for rng in (pairs, suited, offsuit):
			for r in rng:
				if len(r) > 1:
					result.append( '%s-%s' % (r[0].handType, r[-1].handType) )
				elif len(r[0].hands) == 6:
					result.append( r[0].handType)
				else:
					for hand in r[0].hands:
						s = hand.toString()
						s = s.replace('[', '').replace(']', '').replace('\x20', '')
						result.append(s)		
		
		return ', '.join(result)
		
#************************************************************************************
#
#************************************************************************************
class Seats(object):
	SeatNameBTN = 'BTN'
	SeatNameSB = 'SB'
	SeatNameBB = 'BB'
	SeatNameUTG = 'UTG'
	SeatNameUTG1 = 'UTG1'
	SeatNameUTG2 = 'UTG2'
	SeatNameMP = 'MP'
	SeatNameMP1 = 'MP1'
	SeatNameMP2 = 'MP2'
	SeatNameCO = 'CO'
	SeatNames = {		# nPlayers --> seat names
			2: (SeatNameSB, SeatNameBB),
			3: (SeatNameBTN, SeatNameSB, SeatNameBB),
			4: (SeatNameBTN, SeatNameSB, SeatNameBB, SeatNameUTG),
			5: (SeatNameBTN, SeatNameSB, SeatNameBB, SeatNameUTG, SeatNameMP),
			6: (SeatNameBTN, SeatNameSB, SeatNameBB, SeatNameUTG, SeatNameMP, SeatNameCO),
			7: (SeatNameBTN, SeatNameSB, SeatNameBB, SeatNameUTG, SeatNameUTG1, SeatNameMP, SeatNameCO),
			8: (SeatNameBTN, SeatNameSB, SeatNameBB, SeatNameUTG, SeatNameUTG1, SeatNameMP, SeatNameMP1, SeatNameCO),
			9: (SeatNameBTN, SeatNameSB, SeatNameBB, SeatNameUTG, SeatNameUTG1, SeatNameUTG2, SeatNameMP, SeatNameMP1, SeatNameCO),
			10: (SeatNameBTN, SeatNameSB, SeatNameBB, SeatNameUTG, SeatNameUTG1, SeatNameUTG2, SeatNameMP, SeatNameMP1, SeatNameMP2, SeatNameCO),
			}
	@classmethod
	def seatName(klass, nSeats, seatNo):
		"""
		@param nSeats: (int) number of seats total
		@param seatNo: (int) index of the seat to retrieve name for. 0 == player first to act preflop
		@return: (str) seat name
		"""
		seatNames = klass.SeatNames[nSeats]
		return seatNames[seatNo]

#************************************************************************************
# holdem trivia
#************************************************************************************
class HoldemCalculations(object):

	def __init__(self):
		self._nSevenCardCombinations = None
		self._nNoPairCombinations = None
		self._pNoPairCombinations = None
		self._nOnePairCombinations = None
		self._pOnePairCombinations = None
		self._nTwoPairCombinations = None
		self._pTwoPairCombinations = None
		self._nThreeOfKindCombinations = None
		self._pThreeOfKindCombinations = None
		self._nStraightCombinations = None
		self._pStraightCombinations = None
		self._nFlushCombinations = None
		self._pFlushCombinations = None
		self._nFullHouseCombinations = None
		self._pFullHouseCombinations = None
		self._nFourOfKindCombinations = None
		self._pFourOfKindCombinations = None
		self._nStraightFlushCombinations = None
		self._pStraightFlushCombinations = None
		self._nRoyalFlushCombinations = None
		self._pRoyalFlushCombinations = None

		self._nFlopCombinations = None
		self._nFlopIsStraighFlush = None
		self._pFlopIsStraightFlush= None
		self._nFlopIsThreeOfKind = None
		self._pFlopIsThreeOfKind = None
		self._nFlopIsStraight = None
		self._pFlopIsStraight = None
		self._nFlopIsFlush = None
		self._pFlopIsFlush = None
		self._nFlopIsPair = None
		self._pFlopIsPair = None
		self._nFlopIsTwoSuited = None
		self._pFlopIsTwoSuited = None
		self._nFlopIsTwoConnected = None
		self._pFlopIsTwoConnected = None

		self._nTurnCombinations = None
		self._nRiverCombinations = None

		self._nStartingHands = None
		self._pStartingHand = None
		self._nPocketPairs = None
		self._pPocketPairs = None
		self._nPocketsSuited = None
		self._pPocketsSuited = None
		self._nPocketsOffsuit = None
		self._pPocketsOffsuit = None
		self._pPocketPair = None
		self._pPocketPairHigher = None


		self._nCombinationsPocketsPair = None
		self._nCombinationsPocketsSuited = None
		self._nCombinationsPocketsOffsuit = None

		self._pPocketPairFlopOvercards = None
		self._pAcesHigher = None
		self._pFlopPair = None
		self._pFlopSet = None

	def nSevenCardCombinations(self):
		"""returns the number of seven card combinations"""
		if self._nSevenCardCombinations is None:
			self._nSevenCardCombinations = binom(52, 7)
		return self._nSevenCardCombinations

	def nNoPairCombinations(self):
		"""returns the number of no pairs"""
		if self._nNoPairCombinations is None:
			nSetsOfRanks = binom(13, 7) - 8 - (2 * binom(6, 1) + 7 * binom(5, 1)) - (2 * binom(7, 2) + 8  * binom(6, 2))
			nSuits = binom(4, 1)**7 - 844
			self._nNoPairCombinations = nSetsOfRanks * nSuits
		return self._nNoPairCombinations

	def pNoPairCombinations(self):
		"""returns the probability of no pair"""
		if self._pNoPairCombinations is None:
			self._pNoPairCombinations = self.nNoPairCombinations() / self.nSevenCardCombinations()
		return self._pNoPairCombinations

	def pctNoPairCombinations(self, round_=None):
		"""returns the percent chance of no pair"""
		if round_ is None:
			return self.pNoPairCombinations() * 100
		else:
			return round(self.pNoPairCombinations() * 100, round_)

	def nOnePairCombinations(self):
		"""returns the number of a pairs"""
		if self._nOnePairCombinations is None:
			nSetsOfRanks = binom(13, 6) - 9 - (2 * binom(7, 1) + 8 * binom(6, 1))
			nSuits = binom(4, 1)**5 - 34
			nRanks = binom(6, 1) * binom(4, 2)
			self._nOnePairCombinations = nSetsOfRanks * nSuits * nRanks
		return self._nOnePairCombinations

	def pOnePairCombinations(self):
		"""returns the probability of a pair"""
		if self._pOnePairCombinations is None:
			self._pOnePairCombinations = self.nOnePairCombinations() / self.nSevenCardCombinations()
		return self._pOnePairCombinations

	def pctOnePairCombinations(self, round_=None):
		"""returns the percent chance of a pair"""
		if round_ is None:
			return self.pOnePairCombinations() * 100
		else:
			return round(self.pOnePairCombinations() * 100, round_)

	def nTwoPairCombinations(self):
		"""returns the number of two pairs"""
		if self._nTwoPairCombinations is None:
			nThreePairOneKicker = binom(13, 4) * binom(4, 3) * binom(4, 2)**3 * binom(4, 1)
			nTwoPairsThreeKickers = (binom(13, 5) -10) * binom(5, 2) * 2268
			self._nTwoPairCombinations = nThreePairOneKicker + nTwoPairsThreeKickers
		return self._nTwoPairCombinations

	def pTwoPairCombinations(self):
		"""returns the probability of a two pair"""
		if self._pTwoPairCombinations is None:
			self._pTwoPairCombinations = self.nTwoPairCombinations() / self.nSevenCardCombinations()
		return self._pTwoPairCombinations

	def pctTwoPairCombinations(self, round_=None):
		"""returns the percent chance of a two pair"""
		if round_ is None:
			return self.pTwoPairCombinations() * 100
		else:
			return round(self.pTwoPairCombinations() * 100, round_)

	def nThreeOfKindCombinations(self):
		"""returns the number of three of a kinds"""
		if self._nThreeOfKindCombinations is None:
			nSetsOfRanks = binom(13, 5) - 10
			nTripples = binom(5, 1) * binom(4, 3)
			nSuits = binom(4, 1)**4 - binom(3, 1)
			self._nThreeOfKindCombinations = nSetsOfRanks * nTripples * nSuits
		return self._nThreeOfKindCombinations

	def pThreeOfKindCombinations(self):
		"""returns the probability of a three of a kind"""
		if self._pThreeOfKindCombinations is None:
			self._pThreeOfKindCombinations = self.nThreeOfKindCombinations() / self.nSevenCardCombinations()
		return self._pThreeOfKindCombinations

	def pctThreeOfKindCombinations(self, round_=None):
		"""returns the percent chance of a three of a kind"""
		if round_ is None:
			return self.pThreeOfKindCombinations() * 100
		else:
			return round(self.pThreeOfKindCombinations() * 100, round_)

	def nStraightCombinations(self):
		"""returns the number of a straights"""
		if self._nStraightCombinations is None:
			nSetsOfRanks = binom(8, 2) + binom(9, 1) *binom(7,2)
			nSetsOfSuits = binom(4, 1)**7
			nFlushes = binom(4, 1) * (1+binom(7, 6) * binom(3, 1) + binom(7, 5) * binom(3, 1)**2)
			nSevenDistinctRanks = nSetsOfRanks * (nSetsOfSuits - nFlushes)

			nSetsOfRanks = binom(8, 1) + binom(9, 1) * binom(7, 1)
			nPairs = binom(6, 1) * binom(4, 2)
			nSetsOfSuits = binom(4, 1)**5
			nFlushs = binom(4, 1) + binom(5, 4) * binom(2, 1) * binom(3, 1)
			nPairs = binom(6, 1) * binom(4, 2)
			nSixDistinctRanks = nSetsOfRanks *  nPairs * (nSetsOfSuits - nFlushs)

			nTripples = binom(5, 1) * binom(4, 3)
			nStraightsNotFlush = binom(4, 1)**4 - binom(3, 1)
			nSetsOfRanks = 10
			nFiveDistinctRanksPlusTripple = nSetsOfRanks * nTripples * nStraightsNotFlush

			nPairs = binom(5, 2)
			nSuitsOfPairs = binom(4, 2)**2
			nSuitsNotFlush = 6 * (64 - binom(2, 1)) + 24 * (64 - 1) + 6 * 64
			nFiveDistinctRanksTwoPairs = nPairs * nPairs * nSuitsNotFlush

			self._nStraightCombinations = (
					nSevenDistinctRanks +
					nSixDistinctRanks +
					nFiveDistinctRanksPlusTripple +
					nFiveDistinctRanksTwoPairs
					)
		return self._nStraightCombinations

	def pStraightCombinations(self):
		"""returns the probability of a straight"""
		if self._pStraightCombinations is None:
			self._pStraightCombinations = self.nStraightCombinations() / self.nSevenCardCombinations()
		return self._pStraightCombinations

	def pctStraightCombinations(self, round_=None):
		"""returns the percent chance of a straight"""
		if round_ is None:
			return self.pStraightCombinations() * 100
		else:
			return round(self.pStraightCombinations() * 100, round_)

	def nFlushCombinations(self):
		"""returns the number of flushs"""
		if self._nFlushCombinations is None:
			self._nFlushCombinations = binom(4, 1) * (binom(13, 5) * binom(39, 2) + binom(13, 6) * binom(39, 1) + binom(13, 7)) - 41584
		return self._nFlushCombinations

	def pFlushCombinations(self):
		"""returns the probability of a flush"""
		if self._pFlushCombinations is None:
			self._pFlushCombinations = self.nFlushCombinations() / self.nSevenCardCombinations()
		return self._pFlushCombinations

	def pctFlushCombinations(self, round_=None):
		"""returns the percent chance of a flush"""
		if round_ is None:
			return self.pFlushCombinations() * 100
		else:
			return round(self.pFlushCombinations() * 100, round_)

	def nFullHouseCombinations(self):
		"""returns the number of full houses"""
		if self._nFullHouseCombinations is None:
			self._nFullHouseCombinations = (
						(binom(13, 1) * binom(4, 3) * binom(12, 1) * binom(4, 2) * binom(11, 2) * binom(4, 1)**2) +
						(binom(13, 2) * binom(4, 2)**2 * binom(11, 1) * binom(4, 1)) +
						(binom(13, 2) * binom(4, 3)**2 * binom(11, 1) * binom(4, 1))
						)
		return self._nFullHouseCombinations

	def pFullHouseCombinations(self):
		"""returns the probability of a full house"""
		if self._pFullHouseCombinations is None:
			self._pFullHouseCombinations = self.nFullHouseCombinations() / self.nSevenCardCombinations()
		return self._pFullHouseCombinations

	def pctFullHouseCombinations(self, round_=None):
		"""returns the percent chance of a full house"""
		if round_ is None:
			return self.pFullHouseCombinations() * 100
		else:
			return round(self.pFullHouseCombinations() * 100, round_)

	def nFourOfKindCombinations(self):
		"""returns the number of four of a kinds"""
		if self._nFourOfKindCombinations is None:
			self._nFourOfKindCombinations = binom(13, 1) * binom(48, 3)
		return self._nFourOfKindCombinations

	def pFourOfKindCombinations(self):
		"""returns the probability of a four of a kind"""
		if self._pFourOfKindCombinations is None:
			self._pFourOfKindCombinations = self.nFourOfKindCombinations() / self.nSevenCardCombinations()
		return self._pFourOfKindCombinations

	def pctFourOfKindCombinations(self, round_=None):
		"""returns the percent chance of a four of a kind"""
		if round_ is None:
			return self.pFourOfKindCombinations() * 100
		else:
			return round(self.pFourOfKindCombinations() * 100, round_)

	def nStraightFlushCombinations(self):
		"""returns the number of straight flushs"""
		if self._nStraightFlushCombinations is None:
			self._nStraightFlushCombinations = binom(4,1) * (binom(47, 2) + binom(9, 1) * binom(46, 2) )
		return self._nStraightFlushCombinations

	def pStraightFlushCombinations(self):
		"""returns the probability chance of a straight flush"""
		if self._pStraightFlushCombinations is None:
			self._pStraightFlushCombinations = self.nStraightFlushCombinations() / self.nSevenCardCombinations()
		return self._pStraightFlushCombinations

	def pctStraightFlushCombinations(self, round_=None):
		"""returns the percent chance of a straight flush"""
		if round_ is None:
			return self.pStraightFlushCombinations() * 100
		else:
			return round(self.pStraightFlushCombinations() * 100, round_)

	def nRoyalFlushCombinations(self):
		"""returns the number of royal flushs"""
		if self._nRoyalFlushCombinations is None:
			self._nRoyalFlushCombinations = 4
		return self._nRoyalFlushCombinations

	def pRoyalFlushCombinations(self):
		"""returns the probability of a royal flush"""
		if self._pRoyalFlushCombinations is None:
			self._pRoyalFlushCombinations = self.nRoyalFlushCombinations() / self.nSevenCardCombinations()
		return self._pRoyalFlushCombinations

	def pctRoyalFlushCombinations(self, round_=None):
		"""returns the percent chance of a royal flush"""
		if round_ is None:
			return self.pRoyalFlushCombinations() * 100
		else:
			return round(self.pRoyalFlushCombinations() * 100, round_)

	def nFlopCombinations(self):
		"""returns the total number of flop combinations"""
		if self._nFlopCombinations is None:
			self._nFlopCombinations = binom(52, 3)
		return self._nFlopCombinations

	#--> see: Brian Alspach --> http://www.math.sfu.ca/~alspach/comp16/
	def nFlopIsStraightFlush(self):
		"""returns the number of flops being a straight flush"""
		if self._nFlopIsStraighFlush is None:
			self._nFlopIsStraighFlush = 48
		return self._nFlopIsStraighFlush

	def pFlopIsStraighFlush(self):
		"""returns the probability of the flop being a straight flush"""
		if self._pFlopIsStraightFlush is None:
			self._pFlopIsStraightFlush = self.nFlopIsStraightFlush() / self.nFlopCombinations()
		return self._pFlopIsStraightFlush

	def pctFlopIsStraightFlush(self, round_=None):
		"""returns the percent chance of the flop being a straight flush"""
		if round_ is None:
			return self.pFlopIsStraighFlush() * 100
		else:
			return round(self.pFlopIsStraighFlush() * 100, round_)

	def nFlopIsThreeOfKind(self):
		"""returns the number of the flops being a straight"""
		if self._nFlopIsThreeOfKind is None:
			self._nFlopIsThreeOfKind = 4 * 13 	# or binom(4, 3)*13
		return self._nFlopIsThreeOfKind

	def pFlopIsThreeOfKind(self):
		"""returns the probability of the flop being a straight"""
		if self._pFlopIsThreeOfKind is None:
			self._pFlopIsThreeOfKind = self.nFlopIsThreeOfKind() / self.nFlopCombinations()
		return self._pFlopIsThreeOfKind

	def pctFlopIsThreeOfKind(self, round_=None):
		"""returns the percent chance of the flop being a three of a kind"""
		if round_ is None:
			return self.pFlopIsThreeOfKind() * 100
		else:
			return round(self.pFlopIsThreeOfKind() * 100, round_)

	def nFlopIsStraight(self):
		"""returns the number of flops being a straight"""
		if self._nFlopIsStraight is None:
			self._nFlopIsStraight = 4**3*12 - self.nFlopIsStraightFlush()
		return self._nFlopIsStraight

	def pFlopIsStraight(self):
		"""returns the probability of the flop being a straight"""
		if self._pFlopIsStraight is None:
			self._pFlopIsStraight = self.nFlopIsStraight() / self.nFlopCombinations()
		return self._pFlopIsStraight

	def pctFlopIsStraight(self, round_=None):
		"""returns the percent chance of the flop being a straight"""
		if round_ is None:
			return self.pFlopIsStraight() * 100
		else:
			return round(self.pFlopIsStraight() * 100, round_)

	def nFlopIsFlush(self):
		"""returns the number of flops being a flush"""
		if self._nFlopIsFlush is None:
			self._nFlopIsFlush = binom(13, 3) * 4 - self.nFlopIsStraightFlush()
		return self._nFlopIsFlush

	def pFlopIsFlush(self):
		"""returns the probability of the flop being a flush"""
		if self._pFlopIsFlush is None:
			self._pFlopIsFlush = self.nFlopIsFlush() / self.nFlopCombinations()
		return self._pFlopIsFlush

	def pctFlopIsFlush(self, round_=None):
		"""returns the percent chance of the flop being a flush"""
		if round_ is None:
			return self.pFlopIsFlush() * 100
		else:
			return round(self.pFlopIsFlush() * 100, round_)

	def nFlopIsPair(self):
		"""returns the number of flops being paired"""
		if self._nFlopIsPair is None:
			self._nFlopIsPair = binom(4, 2) *13*48
		return self._nFlopIsPair

	def pFlopIsPair(self):
		"""returns the probability of the flop being paired"""
		if self._pFlopIsPair is None:
			self._pFlopIsPair = self.nFlopIsPair() / self.nFlopCombinations()
		return self._pFlopIsPair

	def pctFlopIsPair(self, round_=None):
		"""returns the percent chance of the flop being paired"""
		if round_ is None:
			return self.pFlopIsPair() * 100
		else:
			return round(self.pFlopIsPair() * 100, round_)

	# 13  ways you can pick the first card * 12 you can pick the second * 39 you can pick the third * 2 combinations for the board
	def nFlopIsTwoSuited(self):
		"""returns the number of flops containng two of a suit"""
		if self._nFlopIsTwoSuited is None:
			self._nFlopIsTwoSuited = 13*12*39*2
		return self._nFlopIsTwoSuited

	def pFlopIsTwoSuited(self):
		"""returns the probability of the flop containing two of sa suit"""
		if self._pFlopIsTwoSuited is None:
			self._pFlopIsTwoSuited = self.nFlopIsTwoSuited() / self.nFlopCombinations()
		return self._pFlopIsTwoSuited

	def pctFlopIsTwoSuited(self, round_=None):
		"""returns the percent chance of the flop containing two of sa suit"""
		if round_ is None:
			return self.pFlopIsTwoSuited() * 100
		else:
			return round(self.pFlopIsTwoSuited() * 100, round_)

	#TODO: no idea how to calculate this. we take if from pFlopIsTwoConnected() for now
	def nFlopIsTwoConnected(self):
		"""returns the number of flops containing two connected cards"""
		if self._nFlopIsTwoConnected is None:
			self._nFlopIsTwoConnected = int( self.pFlopIsTwoConnected() * self.nFlopCombinations() )
		return self._nFlopIsTwoConnected

	def pFlopIsTwoConnected(self):
		"""returns the probability of the flop containing two connected cards"""
		if self._pFlopIsTwoConnected is None:
			self._pFlopIsTwoConnected = prob(6, 51)*(1-prob(6, 50) )*4
		return self._pFlopIsTwoConnected

	def pctFlopIsTwoConnected(self, round_=None):
		"""returns the percent chance of the flop containing two connected cards"""
		if round_ is None:
			return self.pFlopIsTwoConnected() * 100
		else:
			return round(self.pFlopIsTwoConnected() * 100, round_)

	#<-- Brian Alspach

	def nTurnCombinations(self):
		"""retuturns the total number of turn card combinations"""
		if self._nTurnCombinations is None:
			self._nTurnCombinations = binom(52, 4)
		return self._nTurnCombinations

	def nRiverCombinations(self):
		"""returns the total number of river card combinations"""
		if self._nRiverCombinations is None:
			self._nRiverCombinations = binom(52, 5)
		return self._nRiverCombinations

	def nStartingHands(self):
		"""returns the total number of starting hands"""
		if self._nStartingHands is None:
			self._nStartingHands = binom(52, 2)
		return self._nStartingHands

	def pStartingHand(self):
		'''returns the probability of getting dealt a specific starting hand'''
		if self._pStartingHand is None:
			self._pStartingHand = prob(1, 52)* prob(1, 51)
		return self._pStartingHand

	def pctStartingHand(self, round_=None):
		"""returns the percent chance of getting dealt a specific starting hand"""
		if round_ is None:
			return self.pStartingHand() * 100
		else:
			return round(self.pStartingHand() * 100, round_)

	def nPocketPairs(self):
		"""returns the number of pocket pairs"""
		if self._nPocketPairs is None:
			self._nPocketPairs = binom(13, 2)
		return self._nPocketPairs

	def pPocketPairs(self):
		"""returns the probability of getting dealt a pocket pair"""
		if self._pPocketPairs is None:
			self._pPocketPairs = self.nPocketPairs() / self.nStartingHands()
		return self._pPocketPairs

	def pctPocketPairs(self, round_=None):
		"""returns the percent chance of getting dealt a pocket pair"""
		if round_ is None:
			return self.pPocketPairs() * 100
		else:
			return round(self.pPocketPairs() * 100, round_)

	def nPocketsSuited(self):
		'''returns the number of suited starting hands'''
		if self._nPocketsSuited is None:
			self._nPocketsSuited = binom(13, 2) * binom(4, 1)
		return self._nPocketsSuited

	def pPocketsSuited(self):
		"""returns the probability of getting dealt a suited starting hand"""
		if self._pPocketsSuited is None:
			self._pPocketsSuited = self.nPocketsSuited() / self.nStartingHands()
		return self._pPocketsSuited

	def pctPocketsSuited(self, round_=None):
		"""returns the percent chancre of getting dealt a suited starting hand"""
		if round_ is None:
			return self.pPocketsSuited() * 100
		else:
			return round(self.pPocketsSuited() * 100, round_)

	def nPocketsOffsuit(self):
		"""returns the number of offsuited unpaired starting hands"""
		if self._nPocketsOffsuit is None:
			self._nPocketsOffsuit = binom(13, 2) * binom(4, 1) * binom(3, 1)
		return self._nPocketsOffsuit

	def pPocketsOffsuit(self):
		"""returns the probability of getting dealt an offsuited unpaired starting hand"""
		if self._pPocketsOffsuit is None:
			self._pPocketsOffsuit = self.nPocketsOffsuit() / self.nStartingHands()
		return self._pPocketsOffsuit

	def pctPocketsOffsuit(self, round_=None):
		"""returns the percent chancre of getting dealt an offsuited unpaired starting hand"""
		if round_ is None:
			return self.pPocketsOffsuit() * 100
		else:
			return round(self.pPocketsOffsuit() * 100, round_)

	def nCombinationsPocketsPair(self):
		"""returns the number of ways to form a paired starting hand"""
		if self._nCombinationsPocketsPair is None:
			self._nCombinationsPocketsPair = binom(4, 2)
		return self._nCombinationsPocketsPair

	def nCombinationsPocketsSuited(self):
		"""returns the number of ways to form a suited starting hand"""
		if self._nCombinationsPocketsSuited is None:
			self._nCombinationsPocketsSuited = binom(4, 1)
		return self._nCombinationsPocketsSuited

	def nCombinationsPocketsOffsuit(self):
		"""returns the number of ways to form an unpaired offsuit starting hand"""
		if self._nCombinationsPocketsOffsuit is None:
			self._nCombinationsPocketsOffsuit = binom(4, 1) * binom(3, 1)
		return self._nCombinationsPocketsOffsuit

	def pPocketPair(self):
		"""returns probability of getting dealt a specific pocket pair"""
		if self._pPocketPair is None:
			self._pPocketPair = self.nCombinationsPocketsPair() / self.nStartingHands()
		return self._pPocketPair

	#-->wikipedia: http://en.wikipedia.org/wiki/Poker_probability_%28Texas_hold_%27em%29

	def pctPocketPair(self, round_=None):
		"""returns percent chance of getting dealt a specific pocket pair"""
		if round_ is None:
			return self.pPocketPair() * 100
		else:
			return round(self.pPocketPair() * 100, round_)

	# calculates the probability that at least one  opponent is holding a higher pair
	def pPocketPairHigher(self, cardRank, nOponents=1):
		"""calculates probability of at least one opponent holding a better pair if you hold a pair
		@param cardRank: (int) rank of the pocket pair
		@param nOpponents: (int) number of opponents to calculate probsability for
		@return: (float) probability
		"""
		if cardRank < 0 or cardRank > 12: raise ValueError('cardRank must be in 0-12')
		return (84 - (6*(cardRank + 2))) / float(1225) * nOponents

	def pctPocketPairHigher(self, cardRank, nOponents=1):
		return self.pPocketPairHigher(self, cardRank, nOponents=nOpponents) * 100

	def pPocketPairsHigher(self):
		"""returns probability / percent chance of at least one player holding a higher pocket pair (1 - 9 opponents)
		@return: (tuple) (strPocketPair, ( (pOpponents1, pctOpponents1), (pOpponents2, ...), ..) ) for each pocket pair
		"""
		if self._pPocketPairHigher is None:
			result = []
			for rank in range(len(Card.RankNames) -2, -1, -1):
				pair = Card.RankNames[rank] * 2
				ps = []
				pp = [pair, ]
				for i in xrange(1, 10):
					p = self.pPocketPairHigher(rank, nOponents=i)
					pct = round(probToPct(p), 2)
					ps.append( (p, pct) )
				pp.append(tuple(ps))
				result.append(tuple(pp) )
			self._pPocketPairHigher = tuple(result)
		return self._pPocketPairHigher

	def pOvercardsToPair(self, cardRank, nCards):
		"""calculates probability of at least one overcard to come if you hold a pair
		@param cardRank: (int) rank of the pocket pair
		@param nCards: (int) number of cards to come
		@return: (float) probability
		"""
		if cardRank < 0 or cardRank > 12: raise ValueError('cardRank must be in 0-12')
		nOvercards = (12 - cardRank) * 4
		nBoardsWithoutOvercards = binom(52-nOvercards, nCards)
		if nBoardsWithoutOvercards:
			nBoards = binom(52, nCards)
			return (1 - (nBoardsWithoutOvercards / nBoards))
		return 1.0

	def pctOvercardsToPair(self, cardRank, nCards):
		return self.pOvercardsToPair(cardRank, nCards) * 100

	def pPocketPairFlopOvercards(self):
		"""returns probability of at least one overcard on the flop if you hold a pocketpair
		@return: (tuple) ( (strPair, probability, percentChance), ...)
		"""
		if self._pPocketPairFlopOvercards is None:
			result = []
			for rank in range(len(Card.RankNames) -2, -1, -1):
				pair = Card.RankNames[rank] * 2
				p = self.pOvercardsToPair(rank, 3)
				result.append( (pair, p, round(probToPct(p), 2)) )
			self._pPocketPairFlopOvercards = tuple(result)

		return self._pPocketPairFlopOvercards

	def pAceHigher(self, cardRank):
		"""returns the probability that an opponent has an ace with a better kicker
		@param cardRank: rank of the kicker to the ace
		"""
		rank = cardRank +2
		return (159 - (12 * rank) ) / 1225.0

	def pAcesHigher(self):
		"""returns the probability of (1-9) opponents holding an ace wih a beter kicker
		@return: (tuple) ('Ax', (pVillains1, percentChanceVillains1), (pVilainsN, percentChanceVillainsN) )
		for each Ax
		"""
		if self._pAcesHigher is None:
			result = []
			for cardRank in xrange(11, -1, -1):
				ace = ['A' + Card.RankNames[cardRank], ]
				p = self.pAceHigher(cardRank)
				players = []
				for nPlayers in xrange(1, 10):
					pp =  (1- (1 - p) ** nPlayers)
					players.append( (pp, round(probToPct(pp), 2)) )
				ace.append(tuple(players))
				result.append(tuple(ace))
			self._pAcesHigher = tuple(result)
		return self._pAcesHigher

	# <-- wikipedia

	def pFlopPair(self):
		"""returns the probability of flopping a pair"""
		if self._pFlopPair is None:
			self._pFlopPair = prob(6, 50) + prob(6, 49) + prob(6, 48)
		return self._pFlopPair

	def pctFlopPair(self):
		"""returns the percent chance of flopping a pair"""
		return round(probToPct(self.pFlopPair() ), 2)

	def pFlopSet(self):
		"""returns the probability of flopping a set"""
		if self._pFlopSet is None:
			self._pFlopSet = prob(2, 50) + prob(2, 49) + prob(2, 48)
		return self._pFlopSet

	def pctFlopSet(self):
		"""returns the percent chance of flopping a set"""
		return round(probToPct(self.pFlopSet() ), 2)




