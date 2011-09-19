# -*- coding: utf-8 -*-
"""texas holdem card game implementation"""

#TODO: int vs float
#TODO: minChip?

import random
import operator
import PokerTools
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
		"""
		@param game: (L{Game}) instance
		@param choices: (dict) eventType --> eventInstance
		@return: eventInstance
		"""
		raise NotImplementedError()
		

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
		self.players = list(players)
		self.pot = Pot(players)
		self.deck = PokerTools.CardDeck()
		self.boardCards = []
		self.handEval = HandEval()
		for name, klass in EventClasses.items():
			setattr(self, name, klass)
		
		#
		for player in self.players:
			if player.stack <= 0:
				raise Valueerror('player "%s" has no stack' % player.name)
			player.pocketCards = []
			player.seatName = ''
					
	def run(self, event):
		self.deck.shuffle()
		self.eventsIn.append(event)
		while self.eventsIn:
			event = self.eventsIn.pop(0)
			result = event.trigger()
			self.eventsOut.insert(0, result)
			yield result
		raise StopIteration()

#************************************************************************************
# pot class
#************************************************************************************
class Pot(object):
	"""pot"""
	
	class Sidepot(object):
		"""sidepot"""
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
			
	def player(self, name):
		"""returns a player given its name
		@param name: (str) player name
		@return: L{Player}
		"""
		for player in self.players:
			if player.name == name:
				return player
		raise ValueError('no such player')
	
	def playerBets(self, player):
		"""returns total of bets player has bet so far
		@param player: (L{Player})
		@return: (float) bets
		"""
		return self.bets[self.players.index(player)]
	
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
	
	def getStraightFlush(self, hand, count=5):
		"""
		@param count: (int) minimum number of cards to take into account
		"""
		# we need at least 5 suited cards to form a straight flush
		flushSuit = None
		ranks = []
		suits = [card.suit() for card in hand]
		for suit in (0, 1, 2, 3):
			if suits.count(suit) >= count:
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
			if len([i for i in expected if i in ranks]) == count:
				straight = expected
				break
			
		if straight:
			if straight[-1] == -1:
				straight[-1]  = 12
			flushSuitName = PokerTools.Card.SuitNames[flushSuit]
			return [ PokerTools.Card( PokerTools.Card.RankNames[rank] + flushSuitName) for rank in straight]
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
						
	def getFlush(self, hand, count=5):
		"""
		@param count: (int) minimum number of cards to take into account
		"""
		flushSuit = None
		flushRanks = []
		suits = [card.suit() for card in hand]
		for suit in (0, 1, 2, 3):
			if suits.count(suit) >= count:
				flushSuit = suit
				flushRanks = [hand[iSuit].rank() for iSuit, mySuit in enumerate(suits) if suit==mySuit]
				break
		if flushRanks:
			flushRanks.sort(reverse=True)
			flushSuitName =  PokerTools.Card.SuitNames[flushSuit]
			return [PokerTools.Card(PokerTools.Card.RankNames[rank] + flushSuitName) for rank in flushRanks]
		return []		
	
	#TODO: getGutshot / getDoubleGutshot		
	def getStraight(self, hand, count=5):
		"""
		@param count: (int) minimum number of cards to take into account
		"""
		ranks = [card.rank() for card in hand]
		# Ace can be high or low. no conflicts possible so simply append
		ranks.sort(reverse=True)
		if 12 in ranks:
			ranks.append(-1)
		
		# check if we can form a straight from ranks
		straight = []
		for rank in ranks:
			expected = range(rank, rank-count, -1)
			if len([i for i in expected if i in ranks]) >= count:
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
							PokerTools.Card.RankNamesDict[cards[-1].rank()][0],
							PokerTools.Card.RankNamesDict[cards[0].rank()][0],
							)
			return self.Result(self, self.HandTypeStraightFlush, cards, details)
		
		cards = self.getQuads(hand)
		if cards:
			details = 'quad %s (kicker: %s)' % (
							PokerTools.Card.RankNamesDict[cards[0].rank()][1], 
							PokerTools.Card.RankNamesDict[cards[-1].rank()][0]
							)
			return  self.Result(self,	self.HandTypeQuads, cards, details)
		
		cards = self.getFullHouse(hand)
		if cards:
			details = 'a full house %s full of %s' % (
							PokerTools.Card.RankNamesDict[cards[0].rank()][1], 
							PokerTools.Card.RankNamesDict[cards[4].rank()][1]
							)
			return  self.Result(self,	self.HandTypeFullHouse, cards, details)
			
		cards = self.getFlush(hand)
		if cards:
			details = 'a flush %s high' % PokerTools.Card.RankNamesDict[cards[0].rank()][0]
			return  self.Result(self,	self.HandTypeFlush, cards, details)
		
		cards = self.getStraight(hand)
		if cards:
			details = 'a straight %s to %s' % (
							PokerTools.Card.RankNamesDict[cards[-1].rank()][0],
							PokerTools.Card.RankNamesDict[cards[0].rank()][0],
							)
			return  self.Result(self,	self.HandTypeStraight, cards, details)
		
		cards = self.getTrips(hand)
		if cards:
			details = 'trip %s (kicker: %s, %s)' % (
							PokerTools.Card.RankNamesDict[cards[0].rank()][1], 
							PokerTools.Card.RankNamesDict[cards[3].rank()][0], 
							PokerTools.Card.RankNamesDict[cards[4].rank()][0]
							)
			return  self.Result(self,	self.HandTypeTrips, cards, details)
		
		cards = self.getTwoPair(hand)
		if cards:
			details = 'two pair %s and %s (kicker: %s)' % (
							PokerTools.Card.RankNamesDict[cards[0].rank()][1],
							PokerTools.Card.RankNamesDict[cards[2].rank()][1],
							PokerTools.Card.RankNamesDict[cards[4].rank()][0],
							)
			return  self.Result(self,	self.HandTypeTwoPair, cards, details)
		
		cards = self.getPair(hand)
		if cards:
			details = 'a pair of %s (kicker: %s, %s, %s)' % (
							PokerTools.Card.RankNamesDict[cards[0].rank()][1],
							PokerTools.Card.RankNamesDict[cards[2].rank()][0],
							PokerTools.Card.RankNamesDict[cards[3].rank()][0],
							PokerTools.Card.RankNamesDict[cards[4].rank()][0],
							)
			return  self.Result(self,	self.HandTypePair, cards, details)
		
		cards = self.getHighCard(hand)
		if cards:
			details = 'high card %s' % PokerTools.Card.RankNamesDict[cards[0].rank()][0]
			return  self.Result(self,	self.HandTypeHighCard, cards, details)
			
		raise ValueError('something went wrong here!')
		
	def getInsideStraightDraw(self, hand):
		if len(hand) < 5:
			return []
		
		# Q x T 9 8 x 6
		ranks = [card.rank() for card in hand]
		ranks.sort(reverse=True)
		if 12 in ranks:
			ranks.append(-1)
			
		draw = []
		for i, rank in enumerate(ranks):
			h = ranks[i:i+5]
			if len(h) < 5:
				break
			#print h
			expected = (rank, rank-2, rank-3, rank-4, rank-6)
			#print '>>', expected
			if len([i for i in expected if i in h]) == 5:
				draw = h
				break
		if draw:
			if draw[-1] == -1:
				draw[-1]  = 12
			# pick a random card acc to rank from lookup dict
			cards = dict([(card.rank(), card) for card in hand])
			return [cards[rank] for rank in draw]
		return []
		
	def getOutsideStraightDraw(self, hand):
		ranks = [card.rank() for card in hand]
		ranks.sort(reverse=True)
		if 12 in ranks:
			ranks.append(-1)
		
		draw = []
		for i, rank in enumerate(ranks):
			if rank == 12 or rank-3 == -1:
				continue
			if rank+1 in ranks or rank-4 in ranks:
				continue
			
			expected = range(rank, rank-4, -1)
			if len([i for i in expected if i in ranks]) == 4:
				draw = expected
				break
		
		if draw:
			if draw[-1] == -1:
				draw[-1]  = 12
			# pick a random card acc to rank from lookup dict
			cards = dict([(card.rank(), card) for card in hand])
			return [cards[rank] for rank in draw]	
		return []
		
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
			event = self.game.EventDeterminePlayerRolesStart(self.game)
		else:
			event =  self.game.EventGameEndNotEnoughPlayers(self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '#Game start' 
		

class EventGameEnd(EventBase):
	def __init__(self, game,):
		self.game = game
	def trigger(self):
		return self
	def toString(self):
		return '#Game end' 
				
class EventGameEndNotEnoughPlayers(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		return self
	def toString(self):
		return '#Game end (not enough players)' 

#************************************************************************************
# events - determine player roles
#************************************************************************************
class EventDeterminePlayerRolesStart(EventBase):
	def __init__(self, game):
		self.game = game
		self.players = self.game.players[:]
	def trigger(self):
		eventClass = self.game.EventDeterminePlayerRole
		numPlayers = len(self.game.players)
		for i, player in enumerate(self.players):
			seatName = PokerTools.Seats.seatName(numPlayers, i)
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
			event = self.game.EventPostAntesStart(self.game)
		elif self.game.smallBlind or self.game.bigBlind:
			event = self.game.EventPostBlindsStart(self.game)
		else:
			event = self.game.EventDealPocketCardsStart(self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /PlayerRoles *****'


class EventDeterminePlayerRole(EventBase):
	def __init__(self, game, player, seatName):
		self.game = game
		self.player = player
		self.player.seatName = seatName
	def trigger(self):
		if self.game.EventDeterminePlayerRole not in self.game.eventsIn:
			event = self.game.EventDeterminePlayerRolesEnd(self.game)
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
		eventClass = self.game.EventPlayerPostsAnte
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
		event = self.game.EventPostBlindsStart(self.game)
		if event.isValid:
			self.game.eventsIn.append(event)
		else:
			event = self.game.EventDealPocketCardsStart(self.game)
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
		if self.game.EventPlayerPostsAnte not in self.game.eventsIn:
			event = self.game.EventPostAntesEnd(self.game)
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
		if self.game.smallBlind and self.playerSmallBlind.stack:
			event = self.game.EventPlayerPostsSmallBlind(
											self.game, 
											self.numPlayers, 
											self.playerSmallBlind, 
											self.playerBigBlind
											)
			self.game.eventsIn.append(event)
		if self.game.bigBlind and self.playerBigBlind.stack:
			event = self.game.EventPlayerPostsBigBlind(
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
		event = self.game.EventDealPocketCardsStart(self.game)
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
		if  self.game.EventPlayerPostsBigBlind not in self.game.eventsIn:
			event = self.game.EventPostBlindsEnd(self.game)
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
		event = self.game.EventPostBlindsEnd(self.game)
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
		eventClass = self.game.EventDealPocketCard
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
		event = self.game.EventPreflopStart(self.game)
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
		if self.game.EventDealPocketCard not in self.game.eventsIn:
			event = self.game.EventDealPocketCardsEnd(self.game)
			self.game.eventsIn.append(event)
		return self
	def toString(self):
		return 'player "%s" gets dealt [%s]' % (self.player.name, self.card.name())
	
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
				
		classEventPlayerTurn = self.game.EventPlayerTurn
		
		# determine actions player can choose from
		event = self.game.EventPlayerFolds(self.game, self.street, self.player)
		choices = {self.game.EventPlayerFolds: event}
		amountToCall = self.game.pot.toCall(self.player)
		
		if amountToCall:
			event = self.game.EventPlayerCalls(self.game, self.street, self.player, amountToCall)
			choices[self.game.EventPlayerCalls] = event
			
			#RULE: a player can raise if..
			# ..he has more chips than the amount to call
			# ..raising is not dissalowed due to an an incomplete bet
			# ..at least one player has some stack to call the raise
			if \
				self.player.stack > amountToCall and \
				not self.flagIncompleteBet and \
				len([p for p in self.street.players if p.stack and p in self.game.pot.playersActive]) > 1:
				
				event = self.game.EventPlayerRaises(
							self.game,
							self.street, 
							self.player, 
							amountMin=min(self.street.lastRaise, self.player.stack - amountToCall), 
							amountMax=self.player.stack - amountToCall,
							amountToCall=amountToCall,
							)
				choices[ self.game.EventPlayerRaises] = event
			
		else:
			event = self.game.EventPlayerChecks(self.game, self.street, self.player)
			choices[self.game.EventPlayerChecks] = event
			event = self.game.EventPlayerBets(
						self.game, 
						self.street,
						self.player, 
						amountMin=min(self.street.lastRaise, self.player.stack), 
						amountMax=self.player.stack,
						)
			choices[self.game.EventPlayerBets] = event
					
		# let player pick an action
		event = self.player.act(self.game, choices)
			
		# process action
		if event == self.game.EventPlayerFolds:
			self.game.pot.fold(self.player)
			#RULE: player can not act when all players have folded to him
			# ..remove player turn from input event queue
			if len(self.game.pot.playersActive) == 1:
				_eventsRemaining=  [_e for _e in self.game.eventsIn if _e == classEventPlayerTurn]
				if len(_eventsRemaining) > 1:
					raise valueError('something went wrong here')
				for _e in _eventsRemaining:
					self.game.eventsIn.remove(_e)
				
		elif event == self.game.EventPlayerChecks:
			pass
		
		elif event == self.game.EventPlayerCalls:
			self.game.pot.addBet(self.player, event.amount)
		
		elif event in (self.game.EventPlayerBets, self.game.EventPlayerRaises):
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
		event = self.game.EventPlayerTurn
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
			event = self.game.EventPreflopEnd(self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.EventPlayerTurn
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Preflop *****'
	def streetEnd(self):
		return self.game.EventPreflopEnd(self.game)
		

class EventPreflopEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.EventShowdownStart(self.game)
		else:
			event = self.game.EventFlopStart(self.game)
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
			event = self.game.EventShowdownStart(self.game)
			self.game.eventsIn.append(event)
			return self
		
		# deal board cards
		for i in range(3):
			self.game.boardCards.append(self.game.deck.nextCard())
				
		if len(self.players) < 2:
			event = self.game.EventFlopEnd(self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.EventPlayerTurn
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Flop [%s %s %s] *****' % tuple([c.name() for c in self.game.boardCards])
	def streetEnd(self):
		return self.game.EventFlopEnd(self.game)


class EventFlopEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.EventShowdownStart(self.game)
		else:
			event = self.game.EventTurnStart(self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Flop *****'


class EventTurnStart(EventFlopStart):
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.EventShowdownStart(self.game)
			self.game.eventsIn.append(event)
			return self
		
		# deal board cards
		self.game.boardCards.append(self.game.deck.nextCard())
			
		if len(self.players) < 2:
			event = self.game.EventTurnEnd(self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.EventPlayerTurn
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Turn [%s %s %s %s] *****' %  tuple([c.name() for c in self.game.boardCards])
	def streetEnd(self):
		return self.game.EventTurnEnd(self.game)


class EventTurnEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.EventShowdownStart(self.game)
		else:
			event = self.game.EventRiverStart(self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Turn *****'


class EventRiverStart(EventFlopStart):
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.EventShowdownStart(self.game)
			self.game.eventsIn.append(event)
			return self
			
		# deal board cards
		self.game.boardCards.append(self.game.deck.nextCard())
		
		if len(self.players) < 2:
			event = self.game.EventRiverEnd(self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.EventPlayerTurn
			for player in self.players:
				event = eventClass(self.game, self, player)
				self.game.eventsIn.append(event)
		return self
		
	def streetEnd(self):
		return self.game.EventRiverEnd(self.game)
	def toString(self):
		return '***** River [%s %s %s %s %s] *****' %  tuple([c.name() for c in self.game.boardCards])


class EventRiverEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		event = self.game.EventShowdownStart(self.game)
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
				event = self.game.EventPlayerReceivesUnclaimedBet(self.game, player, amount)
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
				event = self.game.EventPlayerWinsUncontested(self.game, player, amount,potNo)
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
				event = self.game.EventPlayerWins(self.game, player, sum(pot.bets), potNo, hands[0][1])
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
				event = self.game.EventPlayerTies(
						self.game, 
						player, 
						(amount + remainder) if i==0 else amount, 
						potNo, 
						 hands[i],
						)
				self.game.eventsIn.append(event)
				
		# finally		
		event = self.game.EventShowdownEnd(self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Showdown *****'


class EventShowdownEnd(EventBase):
	def __init__(self, game):
		self.game = game
	def trigger(self):
		event = self.game.EventGameEnd(self.game)
		self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** /Showdown *****'

#************************************************************************************
#
#************************************************************************************
def sampleImpl():
	class MyPlayer(Player):
		def act(self, game, choices):	
			event = random.choice(choices.values())
			if event in (game.EventPlayerBets, game.EventPlayerRaises):
				amount = random.randint(event.amountMin, event.amountMax)
				if amount < event.amountMin:
					amount = event.amountMin
				if amount > event.amountMax:
					amount = event.amountMax
				event.amount = amount
			return event
		def act2(self, game, choices):	
			i = choices.index(EventPlayerFolds)
			return choices[i]
	
	players = [
			MyPlayer('foo', 100),
			MyPlayer('bar', 100),
			MyPlayer('baz', 200),
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
						player.pocketCards[0].name(),
						player.pocketCards[1].name(),
						)
			
		print event.toString()


#if __name__ == '__main__': sampleImpl()	





