# -*- coding: utf-8 -*-

#TODO: int vs float
#TODO: minChip?

import random
import operator
#************************************************************************************
# helpers
#************************************************************************************
def reorderList(L, i):
	return L[i: ] + L[:i]
	
def sliceInt(n, lower, upper):
	upper = upper - lower
	n = n - lower
	n = min(n, upper)
	return 0 if n < 0 else n
		
def UINT(n):
	if n < 0:
		raise ValueError('unsigned int expected')
	return n

#************************************************************************************
# game classes
#************************************************************************************
class Player(object):
	def __init__(self, name, stack):
		self.name = name
		self.stack = stack
		self.pocketCards = []
		self.seatName = ''
	def act(self, game, choices):
		event = random.choice(choices)
		if event in (EventPlayerBets, EventPlayerRaises):
			amount = random.randint(event.amountMin, event.amountMax*100)
			if amount < event.amountMin:
				amount = event.amountMin
			if amount > event.amountMax:
				amount = event.amountMax
			event.amount = amount
		return event
			
	def act2(self, game, choices):	
		i = choices.index(EventPlayerFolds)
		return choices[i]
		

class Game(object):
	def __init__(self, players, bigBlind=0.0, smallBlind=0.0, ante=0.0, minChip=0.0, minBet=0.0, currencySymbol=''):
		"""
		@param players: (list) of players, button player first
		"""
		self.eventsIn = []
		self.eventsOut = []
		self.bigBlind = UINT(bigBlind)
		self.smallBlind = UINT(smallBlind)
		self.ante = UINT(ante)
		self.minChip = UINT(minChip)
		self.minBet = UINT(minBet)
		self.currencySymbol = currencySymbol
		self.players = players[:]
		self.pot = Pot(players)
		self.eventClasses = EventClasses.copy()
		self.deck = Deck()
		self.boardCards = []
		self.handEval = HandEval()
		
		#
		for player in self.players:
			if player.stack <= 0:
				raise Valueerror('player "%s" has no stack' % player.name)
			player.pocketCards = []
					
	def run(self, event):
		self.deck.shuffle()
		self.eventsIn.append(event)
		while self.eventsIn:
			event = self.eventsIn.pop(0)
			result = event.trigger()
			self.eventsOut.insert(0, result)
			yield result
		raise StopIteration()

	
class Pot(object):
	
	class Sidepot(object):
		def __init__(self, players, bets, playersActive):
			self.players = players
			self.bets = bets
			self.playersActive = playersActive
		
	def __init__(self, players):
		self.bets = []
		self.players = players[:]
		self.playersActive = players[:]
		self.sidepots = []
		self.lastHeight = 0.0
		#
		for player in players:
			if player.stack <= 0:
				raise ValueError('player "%s" has no stack')
			self.bets.append(0.0)
		
		
	def fold(self, player):
		self.playersActive.remove(player)
		self.genSidepots()
		
	def addBet(self, player, amount):
		if player.stack <= 0:
			raise ValueError('player has no stack')
		if amount <= 0:
			raise ValueError('player bets <= 0')
		if amount > player.stack:
			raise ValueError('player bets more than his stack')
		
		# add player bet
		player.stack -= amount
		iPlayer = self.players.index(player)
		self.bets[iPlayer] += amount
		if self.bets[iPlayer] < max(self.bets) and player.stack > 0:
			raise valueError('player underbets pot')
				
		self.genSidepots()
		
	def genSidepots(self):
		# generate sidepots
		slices = []
		for iPlayer, player in enumerate(self.players):
			if not player.stack:
				bets = self.bets[iPlayer]
				if bets not in slices:
					slices.append(bets)
		if not slices or max(self.bets) > max(slices):
			if max(self.bets) > 0:	#NOTE: keep this line, just in case we iso as method
				slices.append(max(self.bets))
		slices = sorted(slices)
				
		self.sidepots = []
		lastSlice = 0
		for slice in slices:
			bets = []
			for iBet, bet in enumerate(self.bets):
				bet = sliceInt(bet, lastSlice, slice)
				bets.append(bet)
			players = [p for p in self.players if bets[self.players.index(p)]]
			playersActive = [p for p in players if p in self.playersActive]
			bets = [b for b in bets if b]
			sidepot = self.Sidepot(players, bets, playersActive)
			self.sidepots.insert(0, sidepot)			
			lastSlice = slice
		
	
	def toCall(self, player):
		bet = self.bets[self.players.index(player)]
		maxBet = max(self.bets)
		if bet < maxBet:
			toCall = maxBet - bet
			return min(toCall, player.stack)
		return 0
			
	def newStreet(self):
		self.lastHeight = max(self.bets)
		
	def calcRaiseSize(self, player):
		iPlayer = self.players.index(player)
		bets = self.bets[iPlayer]
		bets -= self.lastHeight
		return bets
		
	def pprint(self):
		for i, sidepot in enumerate(self.sidepots):
			print '%ssidepot (%s)' % ('    '*i, i)
			for iPlayer, player in enumerate(sidepot.players):
				bet = sidepot.bets[iPlayer]
				print '%s%s: %s (%s)' % (
							'    '*(i+1), 
							player.name, 
							bet, 'x' if player in sidepot.playersActive else ' ',
							)
				
			
def test():			
	players = [
				Player('foo', 10),
				Player('bar', 17),
				Player('baz', 50),
				Player('goo', 100),
				]				
	pot = Pot(players)
	pot.addBet(players[3], 5)
	pot.fold(players[3])
	pot.addBet(players[0], 10)
	pot.addBet(players[1], 17)
	pot.addBet(players[2], 30)

	pot.pprint()
	
class Card(int):
	"""poker card object

	@cvar Shapes: (str) card shapes
	@cvar Suits: (str) card suits
	@cvar MinCard: (int) minimum card value
	@cvar MaxCard: (int) maximum card value
	@cvar BitsMax: (int) maximum number of bits required to store a card
	@cvar BitMask: (int) card bit mask
	"""
	Shapes = '23456789TJQKA'
	Suits = 'hdcs'
	MinCard = 0
	MaxCard = len(Shapes) * len(Suits) -1
	
	RankNames = {
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
	
	
	def _tmp_maxBit(value):
		"""returns the maximum bit set in a given number"""
		if value <= 0:	return 0
		n = 1
		while (1 << n) <= value: n += 1
		return n
	BitsMax = _tmp_maxBit(MaxCard)
	del _tmp_maxBit
	BitMask = 2**BitsMax -1

	def __new__(klass, no):
		"""creates a new card
		@param no: (int or string) can be either a string like 'Ah' or another card or an integer card value
		"""
		if isinstance(no, (int, long)):
			if no < klass.MinCard or no > klass.MaxCard:
				raise ValueError('invalid card')
		else:
			try:
				shape = klass.Shapes.index(no[0])
				suit = klass.Suits.index(no[1])
			except IndexError:
				raise ValueError('invalid card')
			no = suit * len(klass.Shapes) + shape
		return int.__new__(klass, no)

	def __repr__(self):
		return '<%s.%s object %r at 0x%x>' % (__name__, self.__class__.__name__, self.toString(), id(self))
	def __str__(self): return self.__repr__()
	def __unicode__(self): return self.__repr__()

	def rank(self):
		"""returns the numeric rank of the card
		return: (int) rank (0-12)
		"""
		return self % len(self.Shapes)
		 
	def suit(self):
		"""returns the suite of the card
		@return: (int) suit
		"""
		return int(self / len(self.Shapes))

	def toString(self):
		"""returns the string representation of the card, i.e. 'Ah'
		@return: 8str) card
		"""
		return self.rankToString() + self.suitToString()

	def rankToString(self):
		"""returns the string representation of the shape of the the card, i.e. 'A'
		@return: str) shape
		"""
		return self.Shapes[self.rank()]

	def suitToString(self):
		"""returns the string representation of the suit of the the card, i.e. 'h'
		@return: 8str) shape
		"""
		return self.Suits[self.suit()]
		

class Deck(object):
	"""poker deck object"""
	__fields__ = ('_cards', )
	Cards = [Card(shape+suit) for suit in Card.Suits for shape in Card.Shapes]

	def __init__(self):
		"""creates a new 52 cards deck"""
		self.cards = None
		self.reset()

	def reset(self):
		self.cards = self.Cards[:]

	def __iter__(self):
		return iter(self.cards())

	def __len__(self): return len(self.cards)

	def shuffle(self, shuffle=random.shuffle):
		'''shuffles the deck in place'''
		shuffle(self.cards)

	def nextCard(self):
		"""returns the next card in the deck
		@return: (L{Card})
		"""
		return self.cards.pop(0)


class Seats(object):
	Names = {		# nPlayers --> seat names
			2: ('SB', 'BB'),
			3: ('BTN', 'SB', 'BB'),
			4: ('BTN', 'SB', 'BB', 'UTG'),
			5: ('BTN', 'SB', 'BB', 'UTG', 'MP'),
			6: ('BTN', 'SB', 'BB', 'UTG', 'MP', 'CO'),
			7: ('BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'MP', 'CO'),
			8: ('BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'MP1', 'MP2', 'CO', ),
			9: ('BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'MP1', 'MP2', 'CO'),
			10: ('BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'MP1', 'MP2', 'MP3', 'CO'),
			}
	
	@classmethod
	def seatName(klass, nSeats, seatNo):
		"""
		@param nSeats: (int) number of seats total
		@param seatNo: (int) index of the seat to retrieve name for. 0 == player first to act preflop
		@return: (str) seat name
		"""
		seatNames = klass.Names[nSeats]
		return seatNames[seatNo]


class HandEval(object):
	
	HandTypeStraightFlush = 'straight-flush'
	HandTypeQuads = 'quads'
	HandTypeFullHouse = 'full-house'
	HandTypeFlush = 'flush'
	HandTypeStraight = 'straight'
	HandTypeTrips = 'trips'
	HandTypeTwoPair = 'two-pair'
	HandTypePair = 'pair'
	HandTypeHighCard = 'high-card'
	HandTypes = (
			HandTypeStraightFlush,
			HandTypeQuads,
			HandTypeFullHouse,
			HandTypeFlush,
			HandTypeStraight,
			HandTypeTrips,
			HandTypeTwoPair,
			HandTypePair,
			HandTypeHighCard,
			)
		
	class Result(object):
		def __init__(self, handEval, handType, cards, details):
			self.handEval = handEval
			self.handType = handType
			self.cards = cards
			self.details = details
		
		def comp(self, other):
			iSelf = self.handEval.HandTypes.index(self.handType)
			iOther = self.handEval.HandTypes.index(other.handType)
			if iSelf < iOther:
				return 1
			elif iSelf > iOther:
				return -1
				
			# straight-flush | straight
			if self.handType in (self.handEval.HandTypeStraightFlush, self.handEval.HandTypeStraight):
				return cmp(self.cards[0].rank(), other.cards[0].rank())
			
			# quads | full-house
			elif self.handType in (self.handEval.HandTypeQuads, self.handEval.HandTypeFullHouse):
				result = cmp(self.cards[0].rank(), other.cards[0].rank())
				if not result:
					# compare kicker (pairing card for full-house)
					result = cmp(self.cards[-1].rank(), other.cards[-1].rank())
				return result
			
			# flush | high-card
			elif self.handType in (self.handEval.HandTypeFlush, self.handEval.HandTypeHighCard):
				for i, card in enumerate(self.cards):
					cardOther = other.cards[i]
					result = cmp(card.rank(), cardOther.rank())
					if result:
						return result
				return 0
			
			# trips
			elif self.handType == self.handEval.HandTypeTrips:
				result = cmp(self.cards[0].rank(), other.cards[0].rank())
				if not result:
					# compare kickers
					for i, card in enumerate(self.cards[4:]):
						cardOther = other.cards[i+4]
						result = cmp(card.rank(), cardOther.rank())
						if result:
							return result
				return result
			
			# two-pair
			elif self.handType == self.handEval.HandTypeTwoPair:
				result = cmp(self.cards[0].rank(), other.cards[0].rank())
				if not result:
					result = cmp(self.cards[2].rank(), other.cards[2].rank())
					if not result:
						# compare kicker
						result = cmp(self.cards[-1].rank(), other.cards[-1].rank())
				return result
			
			# pair
			elif self.handType == self.handEval.HandTypePair:
				result = cmp(self.cards[0].rank(), other.cards[0].rank())
				if not result:
					# compare kickers
					for i, card in enumerate(self.cards[2:]):
						cardOther = other.cards[i+2]
						result = cmp(card.rank(), cardOther.rank())
						if result:
							return result
				return result
			
			raise ValueError('something went wrong here!')
			
		def __eq__(self, other):	return self.comp(other) == 0
		def __ne__(self): return not self.__eq__(other)
		def __lt__(self, other): return self.comp(other) < 0
		def __le__(self, other): return self.comp(other) <= 0
		def __gt__(self, other): return self.comp(other) > 0
		def __ge__(self, other): return self.comp(other) >= 0
		
	
	def __init__(self): pass
	
	def getStraightFlush(self, hand):
		# we need at least 5 suited cards to form a straight flush
		flushSuit = None
		ranks = []
		suits = [card.suit() for card in hand]
		for suit in (0, 1, 2, 3):
			if suits.count(suit) >= 5:
				flushSuit = suit
				ranks = [hand[iSuit].rank() for iSuit, mySuit in enumerate(suits) if suit==mySuit]
				break
		if not ranks:
			return []
			
		# Ace can be high or low. no conflicts possible so simply append
		ranks.sort(reverse=True)
		if 12 in ranks:
			ranks.append(-1)
			
		# check if we can form a straight from flushing cards
		straight = []
		for rank in ranks:
			expected = range(rank, rank-5, -1)
			if len([i for i in expected if i in ranks]) == 5:
				straight = expected
				break
			
		if straight:
			if straight[-1] == -1:
				straight[-1]  = 12
			flushSuitName = Card.Suits[flushSuit]
			return [Card(Card.Shapes[rank] + flushSuitName) for rank in straight]
		return []
			
	def getQuads(self, hand):
		quads = []
		ranks = [card.rank() for card in hand]
		for rank in ranks:
			if ranks.count(rank) == 4:
				kicker = -1
				iKicker = -1
				for iRank, myRank in enumerate(ranks):
					if rank == myRank:
						quads.append(hand[iRank])
					else:
						if myRank > kicker:
							kicker = myRank
							iKicker = iRank
				quads.append(hand[iKicker])
				break
		return quads
		
	def getFullHouse(self, hand):
		trips = []
		pair = []
		ranks = [card.rank() for card in hand]
		counts = [(ranks.count(rank), rank) for rank in range(0, 13)]
		for count, rank in sorted(counts, reverse=True):
			if not trips:
				if count == 3:
					trips = [hand[iRank] for iRank, myRank in enumerate(ranks) if myRank==rank]
			else:
				if count >= 2:
					pair =  [hand[iRank] for iRank, myRank in enumerate(ranks) if myRank==rank][:2]
					break
		if trips and pair:
			return trips + pair
		return []
						
	def getFlush(self, hand):
		flushSuit = None
		flushRanks = []
		suits = [card.suit() for card in hand]
		for suit in (0, 1, 2, 3):
			if suits.count(suit) >= 5:
				flushSuit = suit
				flushRanks = [hand[iSuit].rank() for iSuit, mySuit in enumerate(suits) if suit==mySuit]
				break
		if flushRanks:
			flushRanks.sort(reverse=True)
			flushSuitName = Card.Suits[flushSuit]
			return [Card(Card.Shapes[rank] + flushSuitName) for rank in flushRanks]
		return []		
			
	def getStraight(self, hand):
		ranks = [card.rank() for card in hand]
		# Ace can be high or low. no conflicts possible so simply append
		ranks.sort(reverse=True)
		if 12 in ranks:
			ranks.append(-1)
		
		# check if we can form a straight from ranks
		straight = []
		for rank in ranks:
			expected = range(rank, rank-5, -1)
			if len([i for i in expected if i in ranks]) == 5:
				straight = expected
				break
			
		if straight:
			if straight[-1] == -1:
				straight[-1]  = 12
			# pick a random card acc to rank from lookup dict
			cards = dict([(card.rank(), card) for card in hand])
			return [cards[rank] for rank in straight]
		return []
		
	def getTrips(self, hand):
		trips = []
		kickers = []
		ranks = [card.rank() for card in hand]
		counts = [(ranks.count(rank), rank) for rank in range(0, 13)]
		for count, rank in sorted(counts, reverse=True):
			if count == 3:
				trips = [hand[iRank] for iRank, myRank in enumerate(ranks) if myRank==rank]
				kickers = [(card.rank(), card) for card in hand if card not in trips]
				kickers.sort(reverse=True)
				kickers = [i[1] for i in kickers[:2]]			
				break
		if trips:
			return trips + kickers
		return []

	def getTwoPair(self, hand):
		pair1 = []
		pair2 = []
		kicker = None
		ranks = [card.rank() for card in hand]
		counts = [(ranks.count(rank), rank) for rank in range(0, 13)]
		for count, rank in sorted(counts, reverse=True):
			if not pair1:
				if count == 2:
					pair1 = [hand[iRank] for iRank, myRank in enumerate(ranks) if myRank==rank]
			else:
				if count >= 2:
					pair2 =  [hand[iRank] for iRank, myRank in enumerate(ranks) if myRank==rank][:2]
					# get kicker
					pairingCards = pair1 + pair2
					kickers = [(card.rank(), card) for card in hand if card not in pairingCards]
					kickers.sort(reverse=True)
					kicker = kickers[0][1]
					break
		if pair1 and pair2:
			return pair1 + pair2 + [kicker]
		return []
		
	def getPair(self, hand):
		pair = []
		kickers = []
		ranks = [card.rank() for card in hand]
		counts = [(ranks.count(rank), rank) for rank in range(0, 13)]
		for count, rank in sorted(counts, reverse=True):
			if not pair:
				if count == 2:
					pair = [hand[iRank] for iRank, myRank in enumerate(ranks) if myRank==rank]
					# get kickers
					kickers = [(card.rank(), card) for card in hand if card not in pair]
					kickers.sort(reverse=True)
					kickers = [i[1] for i in kickers[:3]]
					break
		if pair:
			return pair + kickers
		return []
		
	def getHighCard(self, hand):
		ranks = [card.rank() for card in hand]
		ranks.sort(reverse=True)
		# pick a random card acc to rank from lookup dict
		cards = dict([(card.rank(), card) for card in hand])
		return [cards[rank] for rank in ranks[:5]]
		
	def eval(self, hand):
		
		cards = self.getStraightFlush(hand)
		if cards:
			details = 'a straight flush %s to %s' % (
							Card.RankNames[cards[-1].rank()][0],
							Card.RankNames[cards[0].rank()][0],
							)
			return self.Result(self, self.HandTypeStraightFlush, cards, details)
		
		cards = self.getQuads(hand)
		if cards:
			details = 'quad %s (kicker: %s)' % (
							Card.RankNames[cards[0].rank()][1], 
							Card.RankNames[cards[-1].rank()][0]
							)
			return  self.Result(self,	self.HandTypeQuads, cards, details)
		
		cards = self.getFullHouse(hand)
		if cards:
			details = 'a full house %s full of %s' % (
							Card.RankNames[cards[0].rank()][1], 
							Card.RankNames[cards[4].rank()][1]
							)
			return  self.Result(self,	self.HandTypeFullHouse, cards, details)
			
		cards = self.getFlush(hand)
		if cards:
			details = 'a flush %s high' % Card.RankNames[cards[0].rank()][0]
			return  self.Result(self,	self.HandTypeFlush, cards, details)
		
		cards = self.getStraight(hand)
		if cards:
			details = 'a straight %s to %s' % (
							Card.RankNames[cards[-1].rank()][0],
							Card.RankNames[cards[0].rank()][0],
							)
			return  self.Result(self,	self.HandTypeStraight, cards, details)
		
		cards = self.getTrips(hand)
		if cards:
			details = 'trip %s (kicker: %s, %s)' % (
							Card.RankNames[cards[0].rank()][1], 
							Card.RankNames[cards[3].rank()][0], 
							Card.RankNames[cards[4].rank()][0]
							)
			return  self.Result(self,	self.HandTypeTrips, cards, details)
		
		cards = self.getTwoPair(hand)
		if cards:
			details = 'two pair %s and %s (kicker: %s)' % (
							Card.RankNames[cards[0].rank()][1],
							Card.RankNames[cards[2].rank()][1],
							Card.RankNames[cards[4].rank()][0],
							)
			return  self.Result(self,	self.HandTypeTwoPair, cards, details)
		
		cards = self.getPair(hand)
		if cards:
			details = 'a pair of %s (kicker: %s, %s, %s)' % (
							Card.RankNames[cards[0].rank()][1],
							Card.RankNames[cards[2].rank()][0],
							Card.RankNames[cards[3].rank()][0],
							Card.RankNames[cards[4].rank()][0],
							)
			return  self.Result(self,	self.HandTypePair, cards, details)
		
		cards = self.getHighCard(hand)
		if cards:
			details = 'high card %s' % Card.RankNames[cards[0].rank()][0]
			return  self.Result(self,	self.HandTypeHighCard, cards, details)
			
		raise ValueError('something went wrong here!')

#************************************************************************************
# event type
#************************************************************************************	
EventClasses = {}	# dict containing all event classes

class EventMeta(type):
	def __new__(klass, name, bases, kws):
		newClass = type.__new__(klass, name, bases, kws)
		# assume it is not our base class
		if not object in bases:
			EventClasses[name] = newClass
		return newClass

class EventBase(object):
		__metaclass__ = EventMeta
		def __init__(self, game):
			self.game = game
		def __eq__(self, eventClass):
			return self.__class__ == eventClass
		def __ne__(self, eventClass): return not self.__eq__(eventClass)
		def trigger(self):
			raise NotImplementedError()
			
#************************************************************************************
# events
#************************************************************************************	
class EventGameStart(EventBase):
	def trigger(self):
		if len(self.game.players) > 1:
			event = self.game.eventClasses['EventDeterminePlayerRolesStart'](self.game)
		else:
			event =  self.game.eventClasses['EventGameEnd'](self.game, reason=EventGameEnd.ReasonNotEnoughPlayers)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '#Game start' 
		

class EventGameEnd(EventBase):
	ReasonGameEnd = 'gameEnd'
	ReasonNotEnoughPlayers = 'notEnoughPlayers'
	def __init__(self, game, reason=ReasonGameEnd):
		self.game = game
		self.reason = reason
	
	def trigger(self):
		return self
	def toString(self):
		return '#Game end' 
				
#************************************************************************************
# events - determine player roles
#************************************************************************************
class EventDeterminePlayerRolesStart(EventBase):
	def __init__(self, game):
		self.game = game
		self.players = self.game.players[:]
	def trigger(self):
		eventClass = self.game.eventClasses['EventPlayerRole']
		numPlayers = len(self.game.players)
		for i, player in enumerate(self.players):
			seatName = Seats.seatName(numPlayers, i)
			event = eventClass(self.game, player, seatName)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** PlayerRoles *****'


class EventDeterminePlayerRolesEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		if self.game.ante:
			event = self.game.eventClasses['EventPostAntesStart'](self.game)
		else:
			event = self.game.eventClasses['EventPostBlindsStart'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /PlayerRoles *****'


class EventPlayerRole(EventBase):
	def __init__(self, game, player, seatName):
		self.game = game
		self.player = player
		self.player.seatName = seatName
	def trigger(self):
		if self.game.eventClasses['EventPlayerRole'] not in self.game.eventsIn:
			event = self.game.eventClasses['EventDeterminePlayerRolesEnd'](self.game)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '%s - player "%s" (%s%s)' % (
						self.player.seatName, 
						self.player.name,
						self.game.currencySymbol,
						self.player.stack,
						)

#************************************************************************************
# events - post antes
#************************************************************************************
class EventPostAntesStart(EventBase):
	def __init__(self, game):
		self.game = game
		self.players = self.game.players[:]
		self.players.append(self.players.pop(0))
				
	def trigger(self):
		eventClass = self.game.eventClasses['EventPlayerPostsAnte']
		for player in self.players:
			event = eventClass(self.game, player)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** PostAntes *****'


class EventPostAntesEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		event = self.game.eventClasses['EventPostBlindsStart'](self.game)
		if event.isValid:
			self.game.eventsIn.append(event)
		else:
			event = self.game.eventClasses['EventDealPocketCardsStart'](self.game)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /PostAntes *****'


class EventPlayerPostsAnte(EventBase):
	def __init__(self, game, player):
		self.game = game
		self.player = player
		self.amount = 0.0
	def trigger(self):
		self.amount = min(self.player.stack, self.game.ante)
		self.game.pot.addBet(self.player, self.amount)
		if self.game.eventClasses['EventPlayerPostsAnte'] not in self.game.eventsIn:
			event = self.game.eventClasses['EventPostAntesEnd'](self.game)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		s = 'player "%s" posts ante (%s%s)' % (self.player.name, self.game.currencySymbol, self.amount)
		if not self.player.stack:
			s += ' and is all-in'
		return s

#************************************************************************************
# events - post blinds
#************************************************************************************
class EventPostBlindsStart(EventBase):
	
	def __init__(self, game):
		self.isValid = True
		self.game = game
		self.numPlayers = len(self.game.players)
		if self.numPlayers == 2:
			self.playerSmallBlind = self.game.players[0]
			self.playerBigBlind = self.game.players[1]
			#RULE: (heads-up) no blinds are posted when either p1 or p2 has no stack left
			if not self.playerSmallBlind.stack or not self.playerBigBlind.stack:
				self.isValid = False
		else:
			self.playerSmallBlind = self.game.players[1]
			self.playerBigBlind = self.game.players[2]
			#RULE: no blinds are posted when neither p1 nor p2 has any stack left
			if not self.playerSmallBlind.stack and not self.playerbigBlind.stack:
				self.isValid = False
			
	def trigger(self):
		if not self.isValid:
			raise valueError('no blinds are posted due to rules')
		if self.playerSmallBlind.stack:
			event = self.game.eventClasses['EventPlayerPostsSmallBlind'](
											self.game, 
											self.numPlayers, 
											self.playerSmallBlind, 
											self.playerBigBlind
											)
			self.game.eventsIn.append(event)
		if self.playerBigBlind.stack:
			event = self.game.eventClasses['EventPlayerPostsBigBlind'](
											self.game, 
											self.numPlayers, 
											self.playerSmallBlind, 
											self.playerBigBlind
											)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** PostBlinds *****'

		
class EventPostBlindsEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		event = self.game.eventClasses['EventDealPocketCardsStart'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Postblinds *****'


class EventPlayerPostsSmallBlind(EventBase):
	def __init__(self, game, numPlayers, playerSmallBlind, playerBigBlind):
		self.game = game
		self.player = playerSmallBlind
		self.playerBigBlind = playerBigBlind
		self.numPlayers = numPlayers
		self.amount = 0.0
	def trigger(self):
		if self.numPlayers == 2:
			self.amount = min(self.player.stack, self.game.smallBlind, self.playerBigBlind.stack)
		else:
			self.amount = min(self.player.stack, self.game.smallBlind)
		self.game.pot.addBet(self.player, self.amount)
		if  self.game.eventClasses['EventPlayerPostsBigBlind'] not in self.game.eventsIn:
			event = self.game.eventClasses['EventPostBlindsEnd'](self.game)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		s = 'player "%s" posts small blind (%s%s)' % (self.player.name, self.game.currencySymbol, self.amount)
		if not self.player.stack:
			s += ' and is all-in'
		return s

class EventPlayerPostsBigBlind(EventBase):
	def __init__(self, game, numPlayers, playerSmallBlind, playerBigBlind):
		self.game = game
		self.player = playerBigBlind
		self.playerSmallBlind = playerSmallBlind
		self.numPlayers = numPlayers
		self.amount = 0.0
	def trigger(self):
		if self.numPlayers == 2:
			self.amount = min(self.player.stack, self.game.bigBlind, self.playerSmallBlind.stack)
		else:
			self.amount = min(self.player.stack, self.game.bigBlind)
		self.game.pot.addBet(self.player, self.amount)
		event = self.game.eventClasses['EventPostBlindsEnd'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		s = 'player "%s" posts big blind (%s%s)' % (self.player.name, self.game.currencySymbol, self.amount)
		if not self.player.stack:
			s += ' and is all-in'
		return s
		
#************************************************************************************
# events - deal pocket cards
#************************************************************************************
class EventDealPocketCardsStart(EventBase):
	def __init__(self, game):
		self.game = game
		self.players = self.game.players[:]
		self.players.append(self.players.pop(0))
	def trigger(self):
		eventClass = self.game.eventClasses['EventDealPocketCard']
		for i in range(2):
			for player in self.players:
				card = self.game.deck.nextCard()
				event = eventClass(self.game, player, card)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** DealPocketCards *****'


class EventDealPocketCardsEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		event = self.game.eventClasses['EventPreflopStart'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /DealPocketCards *****'


class EventDealPocketCard(EventBase):
	def __init__(self, game, player, card):
		self.game = game
		self.player = player
		self.card = card
		self.player.pocketCards.append(self.card)
	def trigger(self):
		if self.game.eventClasses['EventDealPocketCard'] not in self.game.eventsIn:
			event = self.game.eventClasses['EventDealPocketCardsEnd'](self.game)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		return 'player "%s" gets dealt [%s]' % (self.player.name, self.card.toString())
	

##################################################
##################################################
##################################################

#************************************************************************************
# events - player actions
#************************************************************************************
class EventPlayerTurn(EventBase):
	def __init__(self, game, street, player):
			self.game = game
			self.player = player
			self.street = street
			self.flagIncompleteBet = False
	def trigger(self):
				
		classEventPlayerTurn = self.game.eventClasses['EventPlayerTurn']
		
		# determine actions player can choose from
		event = self.game.eventClasses['EventPlayerFolds'](self.game, self.street, self.player)
		choices = [event, ]
		amountToCall = self.game.pot.toCall(self.player)
		
		if amountToCall:
			event = self.game.eventClasses['EventPlayerCalls'](self.game, self.street, self.player, amountToCall)
			choices.append(event)
			
			#RULE: a player can raise if..
			# ..he has more chips than the amount to call
			# ..raising is not dissalowed due to an an incomplete bet
			# ..at least one player has some stack to call the raise
			if \
				self.player.stack > amountToCall and \
				not self.flagIncompleteBet and \
				len([p for p in self.street.players if p.stack and p in self.game.pot.playersActive]) > 1:
				
				event = self.game.eventClasses['EventPlayerRaises'](
							self.game,
							self.street, 
							self.player, 
							amountMin=min(self.street.lastRaise, self.player.stack - amountToCall), 
							amountMax=self.player.stack - amountToCall,
							amountToCall=amountToCall,
							)
				choices.append(event)
			
		else:
			event = self.game.eventClasses['EventPlayerChecks'](self.game, self.street, self.player)
			choices.append(event)
			event = self.game.eventClasses['EventPlayerBets'](
						self.game, 
						self.street,
						self.player, 
						amountMin=min(self.street.lastRaise, self.player.stack), 
						amountMax=self.player.stack,
						)
			choices.append(event)
					
		# let player pick an action
		event = self.player.act(self.game, choices)
			
		# process action
		if event == self.game.eventClasses['EventPlayerFolds']:
			self.game.pot.fold(self.player)
			#RULE: player can not act when all players have folded to him
			# ..remove player turn from input event queue
			if len(self.game.pot.playersActive) == 1:
				_eventsRemaining=  [_e for _e in self.game.eventsIn if _e == classEventPlayerTurn]
				if len(_eventsRemaining) > 1:
					raise valueError('something went wrong here')
				for _e in _eventsRemaining:
					self.game.eventsIn.remove(_e)
				
		elif event == self.game.eventClasses['EventPlayerChecks']:
			pass
		
		elif event == self.game.eventClasses['EventPlayerCalls']:
			self.game.pot.addBet(self.player, event.amount)
		
		elif event in (self.game.eventClasses['EventPlayerBets'], self.game.eventClasses['EventPlayerRaises']):
			# validate bet/raise
			if event.amount > event.amountMax or event.amount < event.amountMin:
				raise ValueError('invalid bet amount')
						
			# check if we have an incomplete bet
			flagIncompleteBet = False
			if event == EventPlayerBets:
				self.game.pot.addBet(self.player, event.amount)
				if event.amount < self.game.minBet:
					flagIncompleteBet = True
			else:
				self.game.pot.addBet(self.player, event.amountToCall + event.amount)
				if event.amount < self.street.lastRaise:
					# player must be is all-in to make incomplete betting ok
 					if self.player.stack > 0:
						raise ValueError('player placed an incomplete bet but is not all-in')
					flagIncompleteBet = True
						
			if flagIncompleteBet:
				self.street.lastRaise = max(self.street.lastRaise, self.game.minBet)
			else:
				self.street.lastRaise = event.amount
				# clear incomplete bet flag for all players in queue if bet was complete
				# (raise overwrites former incompleteBet flags)
				for _event in self.game.eventsIn:
					if _event == classEventPlayerTurn:
						_event.flagIncompleteBet = False
			
			# 
			players = self.street.players
			i = players.index(self.player)
			players = reorderList(players, i)
			players.pop(0)
			players = [p for p in players if p.stack and p in self.game.pot.playersActive]
			
			# get players already in queue
			playersInQueue = self.playersInQueue()
									
			# append players for who betting was reopend to queue
			for player in players:
				if player not in playersInQueue:
					_event = classEventPlayerTurn(self.game, self.street, player)
					# flag event as response to an incomplete bet that does not reopen betting
					_event.flagIncompleteBet = flagIncompleteBet
					self.game.eventsIn.append(_event)
							 
		#
		if classEventPlayerTurn not in self.game.eventsIn:
			self.game.eventsIn.append(self.street.streetEnd())
		return event
	
	def toString(self):
		return 'Players turn: %s' % self.player.name
		
	def playersInQueue(self):
		event = self.game.eventClasses['EventPlayerTurn']
		return [e.player for e in  self.game.eventsIn if e == event]
		

class EventPlayerChecks(EventBase):
		def __init__(self, game, street, player):
			self.game = game
			self.player = player
			self.street = street
		def toString(self):
			return 'Player "%s" checks' % self.player.name 
		

class EventPlayerBets(EventBase):
		#TODO: chip size
		def __init__(self, game, street, player, amountMin=0.0, amountMax=0.0):
			self.game = game
			self.player = player
			self.street = street
			self.amountMin = amountMin
			self.amountMax = amountMax
			self.amount = 0.0
		def toString(self):
			s = 'Player "%s" bets (%s%s)' % (self.player.name, self.game.currencySymbol, self.amount)
			if not self.player.stack:
				s += ' and is all-in'
			return s
		

class EventPlayerCalls(EventBase):
		def __init__(self, game, street, player, amount):
			self.game = game
			self.player = player
			self.street = street
			self.amount = amount
		def toString(self):
			s = 'Player "%s" calls (%s%s)' % (self.player.name, self.game.currencySymbol, self.amount)
			if not self.player.stack:
				s += ' and is all-in'
			return s
		

class EventPlayerRaises(EventBase):
		#TODO: chip size
		def __init__(self, game, street, player, amountToCall=0.0, amountMin=0.0, amountMax=0.0):
			self.game = game
			self.player = player
			self.street = street
			self.amountMin = amountMin
			self.amountMax = amountMax
			self.amountToCall = amountToCall
			self.amount = 0.0 # only raise amount. total == amountToCall + amount
		def toString(self):
			s = 'Player "%s" raises (%s%s) to (%s%s)' % (
							self.player.name,
							self.game.currencySymbol,
							self.amount,
							self.game.currencySymbol,
							self.game.pot.calcRaiseSize(self.player),
							)
			if not self.player.stack:
				s += ' and is all-in'
			return s


class EventPlayerFolds(EventBase):
		def __init__(self, game, street, player):
			self.game = game
			self.player = player
			self.street = street
		def toString(self):
			return 'Player "%s" folds' % self.player.name 

class EventPlayerReceivesUnclaimedBet(EventBase):
	def __init__(self, game, player, amount):
		self.game = game
		self.player = player
		self.amount = amount
	def trigger(self):
		self.player.stack += self.amount
		return self
	def toString(self):
		return 'player "%s" receives unclaimed bet (%s%s)' % (
						self.player.name, 
						self.game.currencySymbol, 
						self.amount
						)

class EventPlayerWinsUncontested(EventBase):
	def __init__(self, game, player, amount, potNo):
		self.game = game
		self.player = player
		self.amount = amount
		self.potNo = potNo
	def trigger(self):
		self.player.stack += self.amount
		return self
	def toString(self):
		if self.potNo == 0:
			s =  'player "%s" wins main pot (%s%s)' % (
						self.player.name, 
						self.game.currencySymbol, 
						self.amount
						)
		else:
			s =  'player "%s" wins side pot %s (%s%s)' % (
						self.player.name,
						self.potNo, 
						self.game.currencySymbol, 
						self.amount
						)
		return s
		

class EventPlayerWins(EventBase):
	def __init__(self, game, player, amount, potNo, hand):
		self.game = game
		self.player = player
		self.amount = amount
		self.potNo = potNo
		self.hand = hand
	def trigger(self):
		self.player.stack += self.amount
		return self
	def toString(self):
		if self.potNo == 0:
			s =  'player "%s" wins main pot (%s%s) with %s' % (
						self.player.name, 
						self.game.currencySymbol, 
						self.amount,
						self.hand.details,
						)
		else:
			s =  'player "%s" wins side pot %s (%s%s) with %s' % (
						self.player.name,
						self.potNo, 
						self.game.currencySymbol, 
						self.amount,
						self.hand.details,
						)
		return s	 


class EventPlayerTies(EventBase):
	def __init__(self, game, player, amount, potNo, hand):
		self.game = game
		self.player = player
		self.amount = amount
		self.potNo = potNo
		self.hand = hand
	def trigger(self):
		self.player.stack += self.amount
		return self
	def toString(self):
		if self.potNo == 0:
			s =  'player "%s" ties main pot (%s%s) with %s' % (
						self.player.name, 
						self.game.currencySymbol, 
						self.amount,
						self.hand.details,
						)
		else:
			s =  'player "%s" ties side pot %s (%s%s) with %s' % (
						self.player.name,
						self.potNo, 
						self.game.currencySymbol, 
						self.amount,
						self.hand.details,
						)
		return s

#************************************************************************************
# events - streets
#************************************************************************************
class EventPreflopStart(EventBase):
	def __init__(self, game):
		self.game = game
		self.players = self.game.players[:]
		if len(self.players) == 2:
			#RULE: (heads-up) button starts action pre
			pass
		else:
			#RULE: player following BB starts action pre
			for i in range(3):
				self.players.append(self.players.pop(0))
		self.players = [p for p in self.players if p.stack and p in self.game.pot.playersActive]
		self.lastRaise = self.game.minBet
			
	def trigger(self):
		if len(self.players) < 2:
			event = self.game.eventClasses['EventPreflopEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Preflop *****'
	def streetEnd(self):
		return self.game.eventClasses['EventPreflopEnd'](self.game)
		

class EventPreflopEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.eventClasses['EventShowdownStart'](self.game)
		else:
			event = self.game.eventClasses['EventFlopStart'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Preflop *****'


class EventFlopStart(EventBase):
	def __init__(self, game):
		self.game = game
		self.players = self.game.players[:]
		#RULE: (heads-up) BB starts action post
		#RULE: SB starts action post
		self.players.append(self.players.pop(0))
		self.players = [p for p in self.players if p.stack and p in self.game.pot.playersActive]
		self.lastRaise = self.game.minBet
		self.game.pot.newStreet()
				
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.eventClasses['EventShowdownStart'](self.game)
			self.game.eventsIn.append(event)
			return self
		
		# deal board cards
		for i in range(3):
			self.game.boardCards.append(self.game.deck.nextCard())
				
		if len(self.players) < 2:
			event = self.game.eventClasses['EventFlopEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Flop [%s %s %s] *****' % tuple([c.toString() for c in self.game.boardCards])
	def streetEnd(self):
		return self.game.eventClasses['EventFlopEnd'](self.game)


class EventFlopEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.eventClasses['EventShowdownStart'](self.game)
		else:
			event = self.game.eventClasses['EventTurnStart'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Flop *****'


class EventTurnStart(EventFlopStart):
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.eventClasses['EventShowdownStart'](self.game)
			self.game.eventsIn.append(event)
			return self
		
		# deal board cards
		self.game.boardCards.append(self.game.deck.nextCard())
			
		if len(self.players) < 2:
			event = self.game.eventClasses['EventTurnEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Turn [%s %s %s %s] *****' %  tuple([c.toString() for c in self.game.boardCards])
	def streetEnd(self):
		return self.game.eventClasses['EventTurnEnd'](self.game)


class EventTurnEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.eventClasses['EventShowdownStart'](self.game)
		else:
			event = self.game.eventClasses['EventRiverStart'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Turn *****'


class EventRiverStart(EventFlopStart):
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.eventClasses['EventShowdownStart'](self.game)
			self.game.eventsIn.append(event)
			return self
			
		# deal board cards
		self.game.boardCards.append(self.game.deck.nextCard())
		
		if len(self.players) < 2:
			event = self.game.eventClasses['EventRiverEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
		
	def streetEnd(self):
		return self.game.eventClasses['EventRiverEnd'](self.game)
	def toString(self):
		return '***** River [%s %s %s %s %s] *****' %  tuple([c.toString() for c in self.game.boardCards])


class EventRiverEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		event = self.game.eventClasses['EventShowdownStart'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /River *****'


class EventShowdownStart(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		
		# check for unclaimed bet
		pot = self.game.pot.sidepots[0]
		if len(pot.playersActive) == 1:
			# case1: noone has put money into this pot so far
			if len(pot.bets) > 1:
				bets = zip(pot.bets, pot.players)
				bets.sort(key=operator.itemgetter(0), reverse=True)
				amount = bets[0][0] - bets[1][0]
				player = bets[0][1]
			# case2: a player has put money into this pot so far (blinds for example) 
			else:
				amount = pot.bets[0]
				player = pot.playersActive[0]
			if amount > 0:
				iPlayer = pot.players.index(player)
				pot.bets[iPlayer] -= amount
				event = self.game.eventClasses['EventPlayerReceivesUnclaimedBet'](self.game, player, amount)
				self.game.eventsIn.append(event)
		
		# skip main pot if pot only contains an unclaimed bet
		if sum(pot.bets) == 0:
			sidepots = self.game.pot.sidepots[1:]
		else:
			sidepots = self.game.pot.sidepots		
				
		# eval sidepots
		for potNo, pot in enumerate(sidepots):
			
			# player wins uncontested
			if len(pot.playersActive) == 1:
				player = pot.playersActive[0]
				amount = sum(pot.bets)
				event = self.game.eventClasses['EventPlayerWinsUncontested'](self.game, player, amount,potNo)
				self.game.eventsIn.append(event)
				continue
				
			# gen hands competing for the pot
			hands = []
			for player in pot.playersActive:
				hands.append((player, self.game.handEval.eval(player.pocketCards + self.game.boardCards)))
			hands.sort(key=operator.itemgetter(1), reverse=True)
			hands = [h for h in hands if h[1] == hands[0][1]]
			
			# pot has a winner
			if len(hands) == 1:
				event = self.game.eventClasses['EventPlayerWins'](self.game, player, sum(pot.bets), potNo, hands[0][1])
				self.game.eventsIn.append(event)
				continue
				
			# pot ties
			players, hands = zip(*hands)
			#RULE: pot remainder is passed to first player after button player
			# ..so order players button last
			myPlayers = self.game.players[:]
			myPlayers.append(myPlayers.pop(0))
			players = [player for player in myPlayers if player in players]
			
			# split pot
			amount = sum(pot.bets)
			amount, remainder = divmod(amount, len(players))
			for i, player in enumerate(players):
				event = self.game.eventClasses['EventPlayerTies'](
						self.game, 
						player, 
						(amount + remainder) if i==0 else amount, 
						potNo, 
						 hands[i],
						)
				self.game.eventsIn.append(event)
				
		# finally		
		event = self.game.eventClasses['EventShowdownEnd'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Showdown *****'


class EventShowdownEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		event = self.game.eventClasses['EventGameEnd'](self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Showdown *****'





			

def test():
	players = [
			Player('foo', 100),
			Player('bar', 100),
			Player('baz', 200),
			]			
	game = Game(
			players, 
			bigBlind=5, 
			smallBlind=2, 
			minBet=5, 
			minChip=1,
			ante=1,
			)
	
	eventDealPocketCards = None
	for event in game.run(EventGameStart(game)):
		
		# accumulate pocket cards dealing for better reads
		if event == EventDealPocketCard:
			continue
		elif event == EventDealPocketCardsStart:
			eventDealPocketCards = event
		elif event == EventDealPocketCardsEnd:
			for player in eventDealPocketCards.players:
				print 'player "%s" gets dealt [%s %s]' % (
						player.name, 
						player.pocketCards[0].toString(),
						player.pocketCards[1].toString(),
						)
			
		print event.toString()


#test()
		

	

