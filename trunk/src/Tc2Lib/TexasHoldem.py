# -*- coding: utf-8 -*-

import random
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
		#i = choices.index(EventPlayerFolds)
		#return choices[i]
		return random.choice(choices)
		

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
		#
		for player in players:
			if player.stack <= 0:
				raise ValueError('player "%s" has no stack')
			self.bets.append(0.0)
		
		
	def fold(self, player):
		self.playersActive.remove(player)
		
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

	def shape(self):
		"""returns theshape of the card
		@return: (int) shape
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
		return self.shapeToString() + self.suitToString()

	def shapeToString(self):
		"""returns the string representation of the shape of the the card, i.e. 'A'
		@return: 8str) shape
		"""
		return self.Shapes[self.shape()]

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


#************************************************************************************
# event type
#************************************************************************************	
EventClasses = {}	# dict of all event classes

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
		return 'Game end' 
				
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
	def __init__(self, game, player):
			self.game = game
			self.player = player
	def trigger(self):
				
		street = self.streetCurrent()
		
		# determine actions player can choose from
		event = self.game.eventClasses['EventPlayerFolds'](self.game, self.player)
		choices = [event, ]
		if self.actionSoFar():
			event = self.game.eventClasses['EventPlayerCalls'](self.game, self.player, 1)
			choices.append(event)
		else:
			event = self.game.eventClasses['EventPlayerChecks'](self.game, self.player)
			choices.append(event)
			event = self.game.eventClasses['EventPlayerBets'](self.game, self.player, amountMin=1, amountMax=1)
			choices.append(event)
					
		# let player pick an action
		event = self.player.act(self.game, choices)
			
		# process action
		if event == EventPlayerFolds:
			self.game.pot.fold(self.player)
			# if only one player is left, remove players turn from queue
			if len([p for p in street.players if p.stack and p in self.game.pot.playersActive]) == 1:
				eventsRemaining = [_e for _e in self.game.eventsIn if _e == EventPlayerTurn]
				if len(eventsRemaining) > 1:
					raise valueError('something went wrong here')
				for _e in eventsRemaining:
					self.game.eventsIn.remove(_e)
					
		elif event == EventPlayerChecks:
			pass
		elif event == EventPlayerCalls:
			pass
		elif event in (EventPlayerBets, EventPlayerRaises):
			
			# 
			players = street.players
			i = players.index(self.player)
			players = reorderList(players, i)
			players.pop(0)
			players = [p for p in players if p.stack and p in self.game.pot.playersActive]
			
			# get players already in queue
			playersInQueue = self.playersInQueue()
			
			# append players who have to act to the event to queue
			for player in players:
				if player not in playersInQueue:
					_event = self.game.eventClasses['EventPlayerTurn'](self.game, player)
					self.game.eventsIn.append(_event)
							 
		#
		if self.game.eventClasses['EventPlayerTurn'] not in self.game.eventsIn:
			self.game.eventsIn.append(street.streetEnd())
		return event
	
	def toString(self):
		return 'Players turn: %s' % self.player.name
		
	def actionSoFar(self):
		"""return True if there has been action in the current street so far"""
		for event in self.game.eventsOut:
			if event in (EventStreetFlopStart, EventFlopStart, EventTurnStart, EventRiverStart):
				break
			elif event in (EventPlayerBets, EventPlayerRaises):
				return True
		return False
	
	def streetCurrent(self):
		"""returns the the current street"""
		for event in self.game.eventsOut:
			if event in (EventPreflopStart, EventFlopStart, EventTurnStart, EventRiverStart):
				return event
				
	def playersInQueue(self):
		return [event.player for event in  self.game.eventsIn if event == EventPlayerTurn]
		

class EventPlayerChecks(EventBase):
		def __init__(self, game, player):
			self.game = game
			self.player = player
		def toString(self):
			return 'Player "%s" checks' % self.player.name 
		

class EventPlayerBets(EventBase):
		#TODO: chip size
		def __init__(self, game, player, amountMin=0.0, amountMax=0.0):
			self.game = game
			self.player = player
			self.amountMin = amountMin
			self.amountMax = amountMax
		def toString(self):
			return 'Player "%s" bets' % self.player.name 
		

class EventPlayerCalls(EventBase):
		def __init__(self, game, player, amount):
			self.game = game
			self.player = player
			self.amount = amount
		def toString(self):
			return 'Player "%s" calls' % self.player.name 	
		

class EventPlayerRaises(EventBase):
		#TODO: chip size
		def __init__(self, game, player, amountMin=0.0, amountMax=0.0):
			self.game = game
			self.player = player
			self.amountMin = amountMin
			self.amountMax = amountMax
		def toString(self):
			return 'Player "%s" raises' % self.player.name 


class EventPlayerFolds(EventBase):
		def __init__(self, game, player):
			self.game = game
			self.player = player
		def toString(self):
			return 'Player "%s" folds' % self.player.name 

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
			
	def trigger(self):
		if len(self.players) < 2:
			event = self.game.eventClasses['EventPreflopEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, player)
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
	def trigger(self):
		if len(self.game.pot.playersActive) < 2:
			event = self.game.eventClasses['EventShowdownStart'](self.game)
			self.game.eventsIn.append(event)
			return self
		
		#TODO: deal board cards
		if len(self.players) < 2:
			event = self.game.eventClasses['EventFlopEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Flop *****'
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
		
		#TODO: deal board cards
		if len(self.players) < 2:
			event = self.game.eventClasses['EventTurnEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, player)
				self.game.eventsIn.append(event)
		return self
	def toString(self):
		return '***** Turn *****'
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
			
		#TODO: deal board cards
		if len(self.players) < 2:
			event = self.game.eventClasses['EventRiverEnd'](self.game)
			self.game.eventsIn.append(event)
		else:
			eventClass = self.game.eventClasses['EventPlayerTurn']
			for player in self.players:
				event = eventClass(self.game, player)
				self.game.eventsIn.append(event)
			return self
		
	def streetEnd(self):
		return self.game.eventClasses['EventRiverEnd'](self.game)
	def toString(self):
		return '***** River *****'


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


##################################################
##################################################
##################################################

class EventStreetFlopStart(EventBase):
	
	def __init__(self, game, players):
		self.game = game
		self.players = players[:]
	
	def trigger(self):
		if len(self.game.players) > 1:
			for player in self.players:
				self.game.eventsIn.append(EventPlayerTurn(self.game, player))
		else:
			self.game.eventsIn.append(EventGameEnd(self.game))
		return self
	def toString(self):
		return '***** Flop *****'
	def end(self):
		return EventStreetFlopEnd(self.game, self.players)
		
class EventStreetFlopEnd(EventBase):
	def __init__(self, game, players):
		self.game = game
		self.players = players
	
	def trigger(self):
		self.game.eventsIn.append(EventGameEnd(self.game))
		return self
	def toString(self):
		return '***** EndFlop *****' 
	


			

def test():
	players = [
			Player('foo', 100),
			Player('bar', 100),
			Player('baz', 100),
			]			
	game = Game(
			players, 
			bigBlind=0.05, 
			smallBlind=0.02, 
			minBet=0.05, 
			minChip=0.01,
			ante=0.01,
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


test()
		

	

