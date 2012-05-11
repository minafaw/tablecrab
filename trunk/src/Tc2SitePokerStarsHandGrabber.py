# -*- coding: UTF-8 -*-

#TODO: tons. maybe iso hand to a generic library of poker hand types and work from there

import Tc2Config
from PyQt4 import QtCore
import re, codecs

#***********************************************************************************************
#
#***********************************************************************************************
class Hand(QtCore.QObject):
	"""dand object"""
	StreetNone = 0
	StreetBlinds = 1
	StreetFirst = 2
	StreetSecond  = 3
	StreetThird = 4
	StreetFourth = 5
	StreetRiver = 6
	StreetShowdown = 7
	StreetSummary = 8
	GameTypeNone = 0x0
	GameTypeHoldem = 1 << 0
	GameTypeOmaha = 1 << 1
	GameTypeStud = 1 << 2
	GameTypeRazz = 1 << 3
	GameTypeFiveCardDraw = 1 << 4
	GameTypeTrippleDraw = 1 << 5
	GameTypeBadugi = 1 << 6
	GameSubTypeHiLo = 1 << 20
	GameSubTypeLo = 1 << 21
	GameLimitNoLimit = 1 << 40
	GameLimitPotLimit = 1 << 41
	GameLimitLimit = 1 << 42
	class Action(object):
		TypeNone = 0
		TypeBet = 1
		TypeCheck = 2
		TypeCall = 3
		TypeFold = 4
		TypeRaise = 5
		TypePostBlindAnte = 6
		TypePostBlindSmall = 7
		TypePostBlindBig = 8
		TypePostBuyIn = 9
		TypePostBringIn = 10
		TypeDiscardCards = 11
		def __init__(self, player=None, type=TypeNone, amount=0.0):
			self.player = player
			self.type = type
			self.amount = amount
	class Player(object):
		def __init__(self, name='', stack=0.0, cards=None):
			self.name = name
			self.stack = stack
			self.cards = [] if cards is None else cards
	def __init__(self):
		QtCore.QObject.__init__(self)
		self.handHistory = ''
		self.gameType = self.GameTypeNone
		self.gameName = ''
		self.seats = []					# len(seats) == maxPlayers. empty seat is set to None
		self.cards = []
		self.blindAnte = 0.0
		self.blindSmall = 0.0
		self.blindBig = 0.0
		self.hasCents = True		# flag indicating if bet cents is discovered or not
		self.seatNoButton = None	# games with blinds only
		self.tableName = ''
		self.streets = []
		self.actions = {
				self.StreetBlinds: [],
				self.StreetFirst: [],
				self.StreetSecond: [],
				self.StreetThird: [],
				self.StreetFourth: [],
				self.StreetRiver: [],
				}

	def calcPotSizes(self):
		streets = (self.StreetBlinds, self.StreetFirst, self.StreetSecond, self.StreetThird, self.StreetFourth, self.StreetRiver)
		result = dict([(street, 0.0) for street in streets])
		players = [player for player in self.seats if player is not None]
		bets = dict( [(player, 0.0) for player in players])
		for street in streets:
			for player in players:
				actions = [action for action in self.actions[street] if action.player is player]
				for action in actions:
					if action.type == action.TypeDiscardCards:
						continue
					amount = action.amount
					if action.type == action.TypeRaise:
						amount -= bets[player]
					bets[player] += amount
					result[street] += amount
			bets = dict( [(player, 0.0) for player in players] )
			result[street] += result[streets[streets.index(street)-1]]
		return result

	def playerFromName(self, playerName):
		for player in self.seats:
			if player is None: continue
			if player.name == playerName:
				return player
		return None

	def seatsButtonOrdered(self):
		"""returns seats of hand orderd button player first, excluding empty seats"""
		if self.seatNoButton is None:
			seats = self.seats
		else:
			seats = self.seats[self.seatNoButton:] + self.seats[:self.seatNoButton]
		return [seat for seat in seats if seat is not None]

	def __nonzero__(self):
		return bool(self.seats)

#********************************************************************************************************
# hand parser
#********************************************************************************************************
class NoGameHeaderError(Exception): pass

class HandParser(object):
	"""hand history parser
	"""

	Currencies = u'$€£'
	GameTypeMapping = {
			"Hold'em No Limit": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitNoLimit,
					'gameName': 'Holdem (No Limt)',
					},
			"Hold'em Pot Limit": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitPotLimit,
					'gameName': 'Holdem (Pot Limt)',
					},
			"Hold'em Limit": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitLimit,
					'gameName': 'Holdem (Limt)',
					},

			'Omaha Limit': {
					'gameType': Hand.GameTypeOmaha | Hand.GameLimitLimit,
					'gameName': 'Omaha (Limt)',
					},
			'Omaha Pot Limit': {
					'gameType': Hand.GameTypeOmaha | Hand.GameLimitPotLimit,
					'gameName': 'Omaha Pot (Limt)',
					},
			'Omaha Hi/Lo Limit': {
					'gameType': Hand.GameTypeOmaha | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'gameName': 'Omaha Hi/Lo (Limt)',
					},
			'Omaha Hi/Lo Pot Limit': {
					'gameType': Hand.GameTypeOmaha | Hand.GameSubTypeHiLo | Hand.GameLimitPotLimit,
					'gameName': 'Omaha Hi/Lo Pot (Limt)',
					},

			'7 Card Stud Limit': {
					'gameType': Hand.GameTypeStud | Hand.GameLimitLimit,
					'gameName': '7 Card Stud (Limt)',
					},
			'7 Card Stud Hi/Lo Limit': {
					'gameType': Hand.GameTypeStud | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'gameName': '7 Card Stud Hi/Lo (Limt)',
					},

			'Razz Limit': {
					'gameType': Hand.GameTypeRazz | Hand.GameLimitLimit,
					'gameName': 'Razz (Limt)',
					},

			'5 Card Draw No Limit': {
					'gameType': Hand.GameTypeFiveCardDraw | Hand.GameLimitNoLimit,
					'numPlayerCards': 5,
					'gameName': '5 Crad Draw (No Limt)',
					},
			'5 Card Draw Pot Limit': {
					'gameType': Hand.GameTypeFiveCardDraw | Hand.GameLimitPotLimit,
					'numPlayerCards': 5,
					'gameName': '5 Crad Draw (Pot Limt)',
					},
			'5 Card Draw Limit': {
					'gameType': Hand.GameTypeFiveCardDraw | Hand.GameLimitLimit,
					'numPlayerCards': 5,
					'gameName': '5 Crad Draw (Limt)',
					},

			'Single Draw 2-7 Lowball No Limit': {
					'gameType': Hand.GameTypeFiveCardDraw | Hand.GameSubTypeLo | Hand.GameLimitNoLimit,
					'gameName': 'Single Draw 2-7 Lowball (No Limit)',
					},

			'Triple Draw 2-7 Lowball No Limit': {
					'gameType': Hand.GameTypeTrippleDraw | Hand.GameSubTypeLo | Hand.GameLimitNoLimit,
					'gameName': 'Triple Draw 2-7 Lowball (No Limit)',
					},
			'Triple Draw 2-7 Lowball Pot Limit': {
					'gameType': Hand.GameTypeTrippleDraw | Hand.GameSubTypeLo | Hand.GameLimitPotLimit,
					'gameName': 'Triple Draw 2-7 Lowball (Pot Limit)',
					},
			'Triple Draw 2-7 Lowball Limit': {
					'gameType': Hand.GameTypeTrippleDraw | Hand.GameSubTypeLo | Hand.GameLimitLimit,
					'gameName': 'Triple Draw 2-7 Lowball (Limit)',
					},

			'Badugi Limit': {
					'gameType': Hand.GameTypeBadugi | Hand.GameLimitLimit,
					'gameName': 'Badugi (Limit)',
					},


			"HORSE (Hold'em Limit,": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitNoLimit,
					'gameName': 'Holdem (Limit)',
					},
			'HORSE (Omaha Hi/Lo Limit,': {
					'gameType': Hand.GameTypeOmaha | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'gameName': 'Omaha Hi/Lo (Limit)',
					},
			'HORSE (7 Card Stud Limit,': {
					'gameType': Hand.GameTypeStud | Hand.GameLimitLimit,
					'gameName': '7 Card Stud (Limit)',
					},
			'HORSE (7 Card Stud Hi/Lo Limit,':	{
					'gameType': Hand.GameTypeStud | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'gameName': '7 Card Stud Hi/Lo (Limit)',
					},
			'HORSE (Razz Limit,': {
					'gameType': Hand.GameTypeRazz | Hand.GameLimitLimit,
					'gameName': 'Razz (Limit)',
					},

			"Mixed NLH/PLO (Hold'em No Limit,": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitNoLimit,
					'gameName': 'Holdem (No Limit)',
					},
			'Mixed NLH/PLO (Omaha Pot Limit,': {
					'gameType': Hand.GameTypeOmaha | Hand.GameLimitPotLimit,
					'gameName': 'Omaha (Pot Limit)',
					},

			'8-Game (Razz Limit,': {
					'gameType': Hand.GameTypeRazz | Hand.GameLimitLimit,
					'gameName': 'Razz (Limit)',
					},
			'8-Game (Omaha Hi/Lo Limit,': {
					'gameType': Hand.GameTypeOmaha | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'gameName': 'Omaha Hi/Lo (Limit)',
					},
			'8-Game (7 Card Stud Limit,': {
					'gameType': Hand.GameTypeStud | Hand.GameLimitLimit,
					'gameName': '7 Card Stud (Limit)',
					},
			'8-Game (7 Card Stud Hi/Lo Limit,': {
					'gameType': Hand.GameTypeStud | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'gameName': '7 Card Stud Hi/Lo (Limit)',
					},
			"8-Game (Hold'em No Limit,": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitNoLimit,
					'gameName': 'Holdem (No Limt)',
					},
			"8-Game (Hold'em Limit,": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitLimit,
					'gameName': 'Holdem (Limt)',
					},
			'8-Game (Omaha Pot Limit,': {
					'gameType': Hand.GameTypeOmaha | Hand.GameLimitPotLimit,
					'gameName': 'Omaha (Pot Limt)',
					},
			'8-Game (Triple Draw 2-7 Lowball Limit,': {
					'gameType': Hand.GameTypeTrippleDraw | Hand.GameSubTypeLo | Hand.GameLimitLimit,
					'gameName': 'Triple Draw 2-7 Lowball (Limit)',
					},

			'Triple Stud (7 Card Stud Limit,': {
					'gameType': Hand.GameTypeStud | Hand.GameLimitLimit,
					'gameName': '7 Card Stud (Limit)',
					},
			'Triple Stud (Razz Limit,': {
					'gameType': Hand.GameTypeRazz | Hand.GameLimitLimit,
					'gameName': 'Razz (Limit)',
					},
			'Triple Stud (7 Card Stud Hi/Lo Limit,': {
					'gameType': Hand.GameTypeStud | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'gameName': '7 Card Stud Hi/Lo (Limit)',
					},
			}

	def __init__(self,):
		""""""
		pass

	def stringToFloat(self, string):
		return float(string.replace(',', ''))

	def stringToCards(self, string, zfill=None):
		cards = string.split(' ')
		if zfill:
			cards += ['']*zfill
			return cards[:zfill]
		return cards

	PatGameHeader1 = re.compile('^PokerStars\s (Home\s)? Game\s \#[0-9]+\:\s* (?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
	PatGameHeader2 = re.compile('^PokerStars\s (Home\sGame\s)? Hand\s \#[0-9]+\:\s* (?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
	PatGameHeader3 = re.compile('^PokerStars\s Zoom\s Hand\s \#[0-9]+\:\s* (?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
	def matchGameHeader(self, hand, streetCurrent, line):
		result = self.PatGameHeader1.match(line)
		if result is None:
			result = self.PatGameHeader2.match(line)
			if result is None:
				result = self.PatGameHeader3.match(line)
		if result is not None:
			gameData = self.GameTypeMapping[result.group('gameType')]
			hand.gameType = gameData['gameType']
			hand.gameName = gameData['gameName']
		return result is not None

	#NOTE: in tourneys <tableName> is composed of 'tourneyID tableNo'. no idea if this is of any relevance to us
	PatternTableInfo1 = re.compile('^Table \s \' (?P<tableName>.+?) \' \s (?P<maxPlayers>[0-9]+)\-max \s Seat \s \#(?P<seatNoButton>[0-9]+) \s is \s the \s button', re.X)
	#NOTE: zoom poker does not indicate button player
	PatternTableInfo2 = re.compile('^Table \s \' (?P<tableName>.+?) \' \s (?P<maxPlayers>[0-9]+)\-max', re.X)
	def matchTableInfo(self, hand, streetCurrent, line):
		result = self.PatternTableInfo1.match(line)
		if result is not None:
			hand.tableName = result.group('tableName')
			hand.seats = [None for i in range( int(result.group('maxPlayers') ))]
			hand.seatNoButton = int(result.group('seatNoButton')) -1
		else:
			result = self.PatternTableInfo2.match(line)
			if result is not None:
				hand.tableName = result.group('tableName')
				hand.seats = [None for i in range( int(result.group('maxPlayers') ))]
		return result is not None

	PatternSeat = re.compile('^Seat \s(?P<seatNo>[0-9]+)\:\s   (?P<player>.*) \s\( [%s]? (?P<stack>[\d\.]+)\s?.*  \)' % Currencies, re.X)
	def matchSeat(self, hand, streetCurrent, line):
		result= self.PatternSeat.match(line)
		if result is not None:
			if hand.gameType & hand.GameTypeHoldem:
				cards = ['', '']
			elif hand.gameType & hand.GameTypeOmaha:
				cards = ['', '', '', '']
			elif hand.gameType & hand.GameTypeStud:
				cards = ['', '']
			elif hand.gameType & hand.GameTypeRazz:
				cards = ['', '']
			elif hand.gameType & hand.GameTypeFiveCardDraw:
				cards = ['', '', '', '', '']
			elif hand.gameType & hand.GameTypeTrippleDraw:
				cards = ['', '', '', '', '']
			elif hand.gameType & hand.GameTypeBadugi:
				cards = ['', '', '', '']
			else:
				raise ValueError('unsupported game type')
			player = hand.Player(
					name = result.group('player'),
					stack = self.stringToFloat(result.group('stack')),
					cards = cards
					)
			seatNo = int(result.group('seatNo')) -1
			hand.seats[seatNo] = player
		return result is not None

	#NOTE: can not find a way to repliably match "dealt to".  "dealt to" may contain previously
	# dealt cards: [card card][card]. can not find a way to match this, so do it by hand for now
	PatternDealtTo = re.compile('Dealt \s to \s (?P<player>.+?) \s  \[ (?P<cards>.+) \]\s*\Z', re.X)
	def matchDealtTo(self, hand, streetCurrent, line):
		result = self.PatternDealtTo.match(line)
		if result is not None:
			cards = result.group('cards')
			if '[' in cards:
				i = cards.index('[')
				cards = cards[i+1:]
			if hand.gameType & hand.GameTypeStud or hand.gameType & hand.GameTypeRazz:
				hand.playerFromName(result.group('player')).cards += self.stringToCards(cards)
			else:
				hand.playerFromName(result.group('player')).cards = self.stringToCards(cards)
		return result is not None

	#FIXME: determine hand.BlindAnte/BlindSmall/BlindBig from what player posted is quite stupid. have to parse hand header
	#            instead. but ..dont like parsing this mess + it is broken anyways. ante is not mentioned for cash games. maybe
	#            stars get their stuff sorted out somedays. gogogogo stars
	PatternPostAnte =  re.compile('^(?P<player>.*?)\: \s posts \s the \s ante \s [%s]? (?P<amount>[0-9\.\,]+ )' % Currencies, re.X)
	def matchPostAnte(self, hand, streetCurrent, line):
		result = self.PatternPostAnte.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypePostBlindAnte, amount=amount)
			hand.actions[streetCurrent].append(action)
			hand.blindAnte = max(amount, hand.blindAnte)
		return result is not None

	PatternPostSmallBlind = re.compile('^(?P<player>.*?)\: \s posts \s small \s blind \s [%s]? (?P<amount>[0-9\.\,]+)'  % Currencies, re.X)
	def matchPostSmallBlind(self, hand, streetCurrent, line):
		result = self.PatternPostSmallBlind.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypePostBlindSmall, amount=amount)
			hand.actions[streetCurrent].append(action)
			hand.blindSmall = max(amount, hand.blindSmall)
		return result is not None

	PatternPostBigBlind = re.compile('^(?P<player>.*?)\: \s posts \s big \s blind \s [%s]? (?P<amount>[0-9\.\,]+ )' % Currencies, re.X)
	def matchPostBigBlind(self, hand, streetCurrent, line):
		result = self.PatternPostBigBlind.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypePostBlindBig, amount=amount)
			hand.actions[streetCurrent].append(action)
			hand.blindBig = max(amount, hand.blindBig)
		return result is not None

	PatternBringsIn = re.compile('^(?P<player>.*?)\: \s brings \s in \s for \s [%s]? (?P<amount>[0-9\.\,]+ )' % Currencies, re.X)
	def matchBringsIn(self, hand, streetCurrent, line):
		result = self.PatternBringsIn.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypePostBringIn, amount=amount)
			hand.actions[streetCurrent].append(action)
		return result is not None

	PatternPostBuyIn = re.compile('^(?P<player>.*?)\: \s posts \s small \s & \s big \s blinds \s [%s]? (?P<amount>[0-9\.\,]+ )' % Currencies, re.X)
	def matchPostBuyIn(self, hand, streetCurrent, line):
		result = self.PatternPostBuyIn.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypePostBuyIn, amount=amount)
			hand.actions[streetCurrent].append(action)
			hand.blindBig = max(amount, hand.blindBig)
		return result is not None

	PatternBoardCards = re.compile('^Board \s \[  (?P<cards>.*?)   \]', re.X)
	def matchBoardCards(self, hand, streetCurrent, line):
		result = self.PatternBoardCards.match(line)
		if result is not None:
			hand.cards = self.stringToCards(result.group('cards'))
		return result is not None

	PatternShowsCards = re.compile('^(?P<player>.+?)\: \s shows \s\[  (?P<cards>.+?) \]', re.X)
	def matchShowsCards(self, hand, streetCurrent, line):
		result = self.PatternShowsCards.match(line)
		if result is not None:
			hand.playerFromName(result.group('player')).cards = self.stringToCards(result.group('cards'))
		return result is not None

	PatternShowedCards = re.compile('^Seat\s[1-9]+\:\s (?P<player>.+?) \s showed \s\[  (?P<cards>.+?) \]', re.X)
	def matchShowedCards(self, hand, streetCurrent, line):
		result = self.PatternShowedCards.match(line)
		if result is not None:
			hand.playerFromName(result.group('player')).cards = self.stringToCards(result.group('cards'))
		return result is not None

	PatternMuckedCards = re.compile('^Seat\s[1-9]+\:\s (?P<player>.+?) \s mucked \s\[  (?P<cards>.+?) \]', re.X)
	def matchMuckedCards(self, hand, streetCurrent, line):
		result = self.PatternMuckedCards.match(line)
		if result is not None:
			hand.playerFromName(result.group('player')).cards = self.stringToCards(result.group('cards'))
		return result is not None

	PatternDiscardCards = re.compile('^(?P<player>.+?) \:\s discards \s (?P<n>\d) \s card(s)?', re.X)
	def matchDiscardCards(self, hand, streetCurrent, line):
		result = self.PatternDiscardCards.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			n = int(result.group('n'))
			action = hand.Action(player=player, type=hand.Action.TypeDiscardCards, amount=n)
			hand.actions[streetCurrent].append(action)
		return result is not None

	PatternStandsPat = re.compile('^(?P<player>.+?) \:\s stands \s pat', re.X)
	def matchStandsPat(self, hand, streetCurrent, line):
		result = self.PatternStandsPat.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeDiscardCards, amount=0)
			hand.actions[streetCurrent].append(action)
		return result is not None

	PatternCheck = re.compile('^(?P<player>.+?) \:\s checks', re.X)
	def matchCheck(self, hand, streetCurrent, line):
		result = self.PatternCheck.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeCheck)
			hand.actions[streetCurrent].append(action)
		return result is not None

	#TODO: test. stars introduced "fold + show", so we may get to see some cards here. have only seen
	# show both so far. hope it works for show one as well.
	PatternFold = re.compile('^(?P<player>.+?) \:\s folds (\s \[  (?P<cards>.+?) \])?', re.X)
	def matchFold(self, hand, streetCurrent, line):
		result = self.PatternFold.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeFold)
			hand.actions[streetCurrent].append(action)
			if result.group('cards'):
				hand.playerFromName(result.group('player')).cards = self.stringToCards(result.group('cards'))
		return result is not None

	PatternCall = re.compile('^(?P<player>.+?) \:\s calls \s [%s]? (?P<amount>[0-9\.\,]+)' % Currencies, re.X)
	def matchCall(self, hand, streetCurrent, line):
		result = self.PatternCall.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeCall, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None

	PatternBet = re.compile('^(?P<player>.+?) \:\s bets \s [%s]? (?P<amount>[0-9\.\,]+)'  % Currencies, re.X)
	def matchBet(self, hand, streetCurrent, line):
		result = self.PatternBet.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeBet, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None

	PatternRaise = re.compile('^(?P<player>.+?) \:\s raises \s  .*?\s to \s [%s]? (?P<amount>[0-9\.\,]+)'  % Currencies, re.X)
	def matchRaise(self, hand, streetCurrent, line):
		result = self.PatternRaise.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeRaise, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None

	def parse(self, handHistory):
		"""parses a hand history from a string containing exactly one hand history
		@param handHistory: (str)
		@return: L{Hand} or None if string could not be parsed
		"""

		# create new hand object
		hand = Hand()
		hand.handHistory = handHistory.strip().replace('\r', '')
		streetCurrent = hand.StreetBlinds
		hand.streets.append(hand.StreetBlinds)

		# clean handHistory up a bit to make it easier on us..
		handHistory = hand.handHistory.replace('(small blind) ', '').replace('(big blind) ', '').replace('(button) ', '').replace('(Play Money) ', '')

		for lineno, line in enumerate(handHistory.split('\n')):
			line = line.strip()
			if not line: continue

			if lineno == 0:
				if self.matchGameHeader(hand, streetCurrent, line): continue
				raise NoGameHeaderError('No game header found')

			# determine street we are in
			if line.startswith('*** HOLE CARDS ***') or \
					line.startswith('*** 3rd STREET ***') or \
					line.startswith('*** DEALING HANDS ***'):
				streetCurrent = hand.StreetFirst
				hand.streets.append(hand.StreetFirst)
				continue
			elif line.startswith('*** FLOP ***') or \
					line.startswith('*** 4th STREET ***') or \
					line.startswith('*** FIRST DRAW ***'):
				streetCurrent = hand.StreetSecond
				hand.streets.append(hand.StreetSecond)
				continue
			elif line.startswith('*** TURN ***') or \
					line.startswith('*** 5th STREET ***') or \
					line.startswith('*** SECOND DRAW ***'):
				streetCurrent = hand.StreetThird
				hand.streets.append(hand.StreetThird)
				continue
			elif line.startswith('*** 6th STREET ***'):
				streetCurrent = hand.StreetFourth
				hand.streets.append(hand.StreetFourth)
				continue
			elif line.startswith('*** RIVER ***') or line.startswith('*** THIRD DRAW ***'):
				streetCurrent = hand.StreetRiver
				hand.streets.append(hand.StreetRiver)
				continue
			elif line.startswith('*** SHOWDOWN ***'):
				streetCurrent = hand.StreetShowdown
				continue
			elif line.startswith('*** SUMMARY ***'):
				streetCurrent = hand.StreetSummary
				continue

			# parse streets
			if streetCurrent == hand.StreetBlinds:
				if self.matchTableInfo(hand, streetCurrent, line): continue
				if self.matchSeat(hand, streetCurrent, line): continue
				if self.matchPostAnte(hand, streetCurrent,line): continue
				if self.matchPostSmallBlind(hand, streetCurrent,line): continue
				if self.matchPostBigBlind(hand, streetCurrent,line): continue
				if self.matchPostBuyIn(hand, streetCurrent,line): continue
			elif streetCurrent == hand.StreetShowdown:
				#TODO: just a guess that it is possible to show cards on showdown
				if self.matchShowsCards(hand, streetCurrent, line): continue
			elif streetCurrent == hand.StreetSummary:
				if self.matchBoardCards(hand, streetCurrent, line): continue
				if self.matchShowedCards(hand, streetCurrent, line): continue
				if self.matchMuckedCards(hand, streetCurrent, line): continue
			else:
				if self.matchBringsIn(hand, streetCurrent, line): continue
				if self.matchDealtTo(hand, streetCurrent, line): continue
				if self.matchShowsCards(hand, streetCurrent, line): continue
				if self.matchCheck(hand, streetCurrent, line): continue
				if self.matchFold(hand, streetCurrent, line): continue
				if self.matchCall(hand, streetCurrent, line): continue
				if self.matchBet(hand, streetCurrent, line): continue
				if self.matchRaise(hand, streetCurrent, line): continue
				if self.matchDiscardCards(hand, streetCurrent, line):
					#NOTE: stars does not report 1st draw
					if hand.gameType & hand.GameTypeFiveCardDraw:
						if streetCurrent == hand.StreetFirst:
							action = hand.actions[hand.StreetFirst].pop(-1)
							hand.actions[hand.StreetSecond].append(action)
							streetCurrent = hand.StreetSecond
					continue
				if self.matchStandsPat(hand, streetCurrent, line):
					#NOTE: stars does not report 1st draw
					if hand.gameType & hand.GameTypeFiveCardDraw:
						if streetCurrent == hand.StreetFirst:
							action = hand.actions[hand.StreetFirst].pop(-1)
							hand.actions[hand.StreetSecond].append(action)
							streetCurrent = hand.StreetSecond
					continue

		# postprocess hand
		hand.hasCents = (hand.blindAnte, hand.blindSmall, hand.blindBig) != (int(hand.blindAnte), int(hand.blindSmall), int(hand.blindBig))

		if hand.gameType & hand.GameTypeStud or hand.gameType & hand.GameTypeRazz:
			# we get no notification on river card, so patch here. if a player
			# has not folded until the river he has been dealt final card
			if hand.StreetRiver in hand.streets:
				for player in hand.seats:
					if player is None: continue
					if len(player.cards) != 6: continue
					actions = [action.type for action in hand.actions[hand.StreetFourth] if action.player is player]
					if not hand.Action.TypeFold in actions:
						player.cards.append('')

		else: # Draw / Holdem

			#NOTE: when introducing zoom poker stars missed indicating button player in
			# hand histories. following lines try our best to determine this player
			if hand.seatNoButton is None and hand.actions[hand.StreetBlinds]:

				players = [player for player in hand.seats if player is not None]
				if len(players) < 2:
					raise ValueError('too bad, we can not handle this case :-)')

				# try to find small blind player
				for action in hand.actions[hand.StreetBlinds]:
					if action.type == action.TypePostBlindSmall:
						i = players.index(action.player)
						if len(players) == 2:
							hand.seatNoButton = i
						else:
							player = players[i-1]
							hand.seatNoButton = hand.seats.index(player)
						break

				if hand.seatNoButton is None:
					# try to find big blind player
					for action in hand.actions[hand.StreetBlinds]:
						if action.type == action.TypePostBlindBig:
							i = players.index(action.player)
							if len(players) == 2:
								hand.seatNoButton = i-1
							else:
								player = players[i-2]
								hand.seatNoButton = hand.seats.index(player)
							break

				if hand.seatNoButton is None:
					# out of luck, hand may be ante only so we set random player as button
					hand.seatNoButton = hand.seats.index(players[0])

		return hand

#************************************************************************************
# hand formatters
#************************************************************************************
HandFormatters = {}
class HandFormatterMeta(type):
	"""meta class for hand formatters"""
	def __new__(klass, name, bases, kws):
		newKlass = type.__new__(klass, name, bases, kws)
		if newKlass.Name is not None:
			HandFormatters[newKlass.Name] = newKlass
		return newKlass

class HandFormatterBase(object):
	"""base class for hand formatters"""
	__metaclass__ = HandFormatterMeta
	Name = None

#TODO: if small blind open folds markup is slightly messed up
class HandFormatterHtmlTabular(HandFormatterBase):
	"""Hand formatter that formats a hand as a tabular html"""
	Name = 'HtmlTabular'

	PrefixBet = 'b'
	PostfixBet = ''
	PrefixRaise = 'r'
	PostfixRaise = ''
	PrefixCall = 'c'
	PostfixCall = ''
	PrefixAnte = ''
	PostfixAnte = ''
	PrefixSmallBlind = 'sb'
	PostfixSmallBlind = ''
	PrefixBigBlind = 'bb'
	PostfixBigBlind = ''
	PrefixBuyIn = 'bi'
	PostfixBuyIn = ''
	PrefixBringIn = 'br'
	PostfixBringIn = ''
	PrefixCheck = 'ck'
	PrefixFold = 'f'

	DecKStyleDefault = 'Default'
	DeckStyleFourColor = 'FourColor'
	DeckStyles = (DecKStyleDefault, DeckStyleFourColor)

	HtmlCardSuitMapping = {		# suit --> (entity, htmlKlass)
			DecKStyleDefault: {
				's': ('&spades;', 'cardRank cardRankSpade', 'cardSuit cardSuitSpade'),
				'c': ('&clubs;', 'cardRank cardRankClub', 'cardSuit cardSuitClub'),
				'd': ('&diams;', 'cardRank cardrankDiamond', 'cardSuit cardSuitDiamond'),
				'h': ('&hearts;', 'cardRank cardRankHeart', 'cardSuit cardSuitHeart'),
				'': ('&nbsp;', 'cardRank cardRankBack', 'cardSuit cardSuitBack'),
				},
			DeckStyleFourColor: {
				's': ('&spades;', 'cardRank4 cardRankSpade4', 'cardSuit4 cardSuitSpade4'),
				'c': ('&clubs;', 'cardRank4 cardRankClub4', 'cardSuit4 cardSuitClub4'),
				'd': ('&diams;', 'cardRank4 cardrankDiamond4', 'cardSuit4 cardSuitDiamond4'),
				'h': ('&hearts;', 'cardRank4 cardRankHeart4', 'cardSuit4 cardSuitHeart4'),
				'': ('&nbsp;', 'cardRank4 cardRankBack4', 'cardSuit4 cardSuitBack4'),
				},
			}

	MaxPlayerName = -1
	# and this is the css for the html file
	StyleSheet = '''.handBody{}
.handTable{
        border-spacing: 0px;
        border-collapse: collapse;
        }
.handSource{margin-top: 1em;}

.gameName{
    text-align: center;
    border: 1px solid black;
    }
.playerCell{
        vertical-align: top;
        border: 1px solid black;
        }
.playerName{}
.playerStack{}
.playerCardsCell{border: 1px solid black;}
.playerCards{
        border: 0px;
        border-spacing: 0px;
        width: 100%;
        }
.playerActionsCell{
        white-space: nowrap;
        vertical-align: top;
        padding-left: 0.1em;
        border: 1px solid black;
        }
.playerActionFold{}
.playerActionCall{background-color: #87CEFA ;}
.playerActionCheck{background-color: #98FB98;}
.playerActionBet{background-color: #FFA54F;}
.playerActionRaise{background-color: #FF6EB4;}
.playerActionPostBlindBig{}
.playerActionPostBlindSmall{}
.playerActionPostBuyIn{}
.playerActionPostBringIn{}
.playerActionDiscardCards{font-size: x-large;}
.playerActionNone{}


.potCellExtra{
        padding-left: 1em;
        border: 1px solid black;
        }
.potCell{
        text-align: center;
        border: 1px solid black;
        }


.boardCardCellExtra{border: 1px solid black; }
.boardCardCell{
        border:1px solid black;
        margin-left: auto;        /* centers contents of the cell, seems broken now */
        margin-right: auto;    /* centers contents of the cell, seems broken now */
        }
.boardCards{
        border: 0px;
        border-spacing: 0px;
        margin-left: auto;        /* centers contents of the cell, seems broken now */
        margin-right: auto;    /* centers contents of the cell, seems broken now */
        }


.cards{
	border-spacing: 0px;
	padding: 0px;
	empty-cells: show;
	}
.cardRank{
	text-align: center;
	color: white;

	padding: 0em 0em 0em 0em;
	border-top: 1px solid black;
	border-left: 1px solid black;
	border-bottom: none;
	border-right: 1px solid black;
	}
.cardSuit{
	text-align: center;
	color: white;
	/*font-size: 0pt;*/    /* uncomment to hide card suit */

	padding: 0em 0em 0em 0em;
	border-top: none;
	border-left: 1px solid black;
	border-bottom: 1px solid black;
	border-right: 1px solid black;
	}
.cardWidth{
	padding-left: 1.2em;	/* adjust card width via this padding */

	padding-top: 0em;
	padding-right: 0em;
	padding-bottom: 0em;
	height: 0px;
	border-top: none;
	border-bottom: none;
	}

.cardRankSpade{
	color: black;
	background-color: white;
	}
.cardSuitSpade{
	color: black;
	background-color: white;
	}
.cardRankClub{
	color: black;
	background-color: white;
	}
.cardSuitClub{
	color: black;
	background-color: white;
	}
.cardRankHeart{
	color: red;
	background-color: white;
	}
.cardSuitHeart{
	color: red;
	background-color: white;
	}
.cardRankDiamond{
	color: red;
	background-color: white;
	}
.cardSuitDiamond{
	color: red;
	background-color: white;
	}
.cardRankBack{
	color: #355b73;
	background-color: #355b73;
	}
.cardSuitBack{
	color: #355b73;
	background-color: #355b73;
	}
.cardNone{}

/* four color deck */
.cardRank4{
	text-align: center;
	color: white;

	padding: 0.2em 0em 0.2em 0em;
	border-top: 1px solid black;
	border-left: 1px solid black;
	border-bottom: none;
	border-right: 1px solid black;
	}
.cardSuit4{
	text-align: center;
	color: white;
	font-size: 0pt;    /* uncomment to hide card suit */

	padding: 0em 0em 0em 0em;
	border-top: none;
	border-left: 1px solid black;
	border-bottom: 1px solid black;
	border-right: 1px solid black;
	}.cardWidth4{
	padding-left: 2.8em;	/* adjust card width via this padding */

	padding-top: 0em;
	padding-right: 0em;
	padding-bottom: 0em;
	height: 0px;
	border-top: none;
	border-bottom: none;
	}

.cardRankSpade4{
	font-size: large;
	font-weight: bold;
	color: white;
	background-color: #8D8F8F;
	}
.cardSuitSpade4{
	background-color: #8D8F8F;
	}
.cardRankClub4{
	font-size: large;
	font-weight: bold;
	color: white;
	background-color: #5A9057;
	}
.cardSuitClub4{
	background-color: #5A9057;
	}
.cardRankHeart4{
	font-size: large;
	font-weight: bold;
	color: white;
	background-color: #C46953;
	}
.cardSuitHeart4{
	background-color: #C46953;
	}
.cardRankDiamond4{
	font-size: large;
	font-weight: bold;
	color: white;
	background-color: #587DC2;
	}
.cardSuitDiamond4{
	background-color: #587DC2;
	}
.cardRankBack4{
	font-size: large;
	font-weight: bold;
	color: white;
	background-color: white;
	}
.cardSuitBack4{
	background-color: white;
	}


'''

	class IndentBuffer(object):
		"""write buffer with indentation support"""
		def __init__(self, indent='\x20\x20\x20\x20'):
			"""
			@param indent: (str) chars to use for indentation
			@ivar indentLevel: (int) current level of indentation
			@ivar indent:  (str) chars to use for indentation
			@ivar: data: (str) data contained in the buffer
			"""
			self.indentLevel = 0
			self.indent = indent
			self.data = ''
		def __rshift__(self, chars):
			"""add chars to the buffer and increases indentLevel for all following adds
			"""
			self.data += (self.indent*self.indentLevel) + chars + '\n'
			self.indentLevel += 1
		def __lshift__(self, chars):
			"""decreases indentLevel and add chars to the buffer
			"""
			self.indentLevel -= 1
			if self.indentLevel < 0: raise ValueError('indent level exceeded')
			self.data += (self.indent*self.indentLevel) + chars + '\n'
		def __or__(self, chars):
			"""adds chars to the buffer without altering the current indentLevel"""
			self.data += (self.indent*self.indentLevel) + chars + '\n'

	def __init__(self):
		self.settingsHandViewer = None
		self.settingsHandViewerStyleSheet = None
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.settingsHandViewer = globalObject.settingsHandViewer
		self.settingsHandViewerStyleSheet = globalObject.settingsHandViewerStyleSheet

	def formatNum(self, hand, num):
		if not num:
			result = ''
		elif hand.hasCents:
			if self.settingsHandViewer.noFloatingPoint():
				result = Tc2Config.locale.toString( int(num*100) )
			else:
				result = Tc2Config.locale.toString(num, 'f', 2)
		else:
			result = Tc2Config.locale.toString( int(num))
		return result

	def htmlEscapeString(self, string, spaces=True):
		string = string.replace('&', '&#38;').replace('"', '&#34;').replace("'", '&#39;').replace('<', '&#60;').replace('>', '&#62;')
		if spaces:
			string = string.replace(' ', '&nbsp;')
		return string

	def htmlFormatCards(self, p, cards):
		"""
		@param cards: one or more cards (like 'Ad'). if a card is '' a card back is
		formatted, if card is None a placeholder is formatted
		"""
		deckStyle = str(self.settingsHandViewer.deckStyle())
		p >> '<table class="cards">'
		trRank = '<tr>'
		trSuit = '<tr>'
		trWidth = '<tr>'
		for card in cards:
			if card is None:
				trRank += '<td class="cardNone"></td>'
				trSuit += '<td class="cardNone"></td>'
				trWidth += '<td class="cardWidth"></td>'
			elif card == '':
				rank = '&nbsp;'
				suit, rankKlass, suitKlass = self.HtmlCardSuitMapping[deckStyle]['']
				trRank += '<td class="%s">%s</td>' % (rankKlass, rank)
				trSuit += '<td class=" %s">%s</td>' % (suitKlass, suit)
				trWidth += '<td class="cardWidth"></td>'
			else:
				rank = card[0]
				suit, rankKlass, suitKlass = self.HtmlCardSuitMapping[deckStyle][card[1]]
				trRank += '<td class="%s">%s</td>' % (rankKlass, rank)
				trSuit += '<td class="%s">%s</td>' % (suitKlass, suit)
				trWidth += '<td class="cardWidth"></td>'
		trRank += '</tr>'
		trSuit += '</tr>'
		trWidth += '</tr>'
		p | trRank
		p | trSuit
		p | trWidth
		p << '</table>'

	#TODO: use Tc2Config.truncateString()
	def formatPlayerName(self, playerName):
		maxPlayerName = self.settingsHandViewer.maxPlayerName()
		if maxPlayerName > -1 and len(playerName) > maxPlayerName:
			if maxPlayerName <= 0:
				playerName = ''
			elif maxPlayerName == 1:
				playerName = '.'
			else:
				playerName = playerName[:maxPlayerName-2] + '..'
		return self.htmlEscapeString(playerName, spaces=True)

	def dump(self, hand):

		p = self.IndentBuffer()
		# setup html page
		p >> '<html>'
		p >> '<head>'
		p | '<meta name="author" content="TableCrab">'
		p | '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		p | '<style type="text/css"><!-- %s --></style>' % self.settingsHandViewerStyleSheet.styleSheet()
		p << '</head>'
		p >> '<body class="handBody">'
		p >> '<table class="handTable">'
		p | '<tr><td class="gameName" colspan="99">%s</td></tr>' % hand.gameName

		if hand.gameType & hand.GameTypeHoldem or hand.gameType & hand.GameTypeOmaha:
			self.formattHandHoldem(p, hand)
		elif hand.gameType & hand.GameTypeStud or hand.gameType & hand.GameTypeRazz:
			self.formattHandStud(p, hand)
		elif hand.gameType & hand.GameTypeFiveCardDraw or \
				hand.gameType & hand.GameTypeTrippleDraw or \
				hand.gameType & hand.GameTypeBadugi:
			self.formattHandDraw(p, hand)
		else:
			raise ValueError('unsupported game type: %s' % hand.gameType)

		# dump html to file
		p << '</table>'
		p | '<pre class="handSource">%s</pre>' % self.htmlEscapeString(hand.handHistory, spaces=False)
		p << '</body>'
		p << '</html>'
		return p.data.encode('utf-8')


	def formattPlayerStart(self, p, hand, player):
		p >> '<tr>'

	def formattPlayerEnd(self, p, hand, player):
		p << '</tr>'


	def formattPlayerActions(self, p, hand, player, actions):

		p >> '<td class="playerActionsCell">'
		nActions = None
		for nActions, action in enumerate(actions):
			if action.type == action.TypeFold:
				prefix = self.settingsHandViewer.actionPrefix('Fold')
				p | '<div class="playerActionFold">%s</div>' % (prefix if prefix else '&nbsp;')
			elif action.type == action.TypeCheck:
				prefix = self.settingsHandViewer.actionPrefix('Check')
				p |  '<div class="playerActionCheck">%s</div>' % (prefix if prefix else '&nbsp;')
			elif action.type == action.TypeBet:
				p | '<div class="playerActionBet">%s%s%s</div>' % (
						self.settingsHandViewer.actionPrefix('Bet'),
						self.formatNum(hand, action.amount),
						self.settingsHandViewer.actionPostfix('Bet')
						)
			elif action.type == action.TypeRaise:
				p | '<div class="playerActionRaise">%s%s%s</div>' % (
						self.settingsHandViewer.actionPrefix('Raise'),
						self.formatNum(hand, action.amount),
						self.settingsHandViewer.actionPostfix('Raise')
						)
			elif action.type == action.TypeCall:
				p | '<div class="playerActionCall">%s%s%s</div>' % (
						self.settingsHandViewer.actionPrefix('Call'),
						self.formatNum(hand, action.amount),
						self.settingsHandViewer.actionPostfix('Call')
						)
			elif action.type == action.TypePostBlindBig:
				p | '<div class="playerActionPostBlindBig">%s%s%s</div>' % (
						self.settingsHandViewer.actionPrefix('BigBlind'),
						self.formatNum(hand, action.amount),
						self.settingsHandViewer.actionPostfix('BigBlind')
						)
			elif action.type == action.TypePostBlindSmall:
				p | '<div class="playerActionPostBlindSmall">%s%s%s</div>' % (
						self.settingsHandViewer.actionPrefix('SmallBlind'),
						self.formatNum(hand, action.amount),
						self.settingsHandViewer.actionPostfix('SmallBlind')
						)
			elif action.type == action.TypePostBuyIn:
				p | '<div class="playerActionPostBuyIn">%s%s%s</div>' % (
						self.settingsHandViewer.actionPrefix('BuyIn'),
						self.formatNum(hand, action.amount),
						self.settingsHandViewer.actionPostfix('BuyIn')
						)
			elif action.type == action.TypePostBringIn:
				p | '<div class="playerActionPostBringIn">%s%s%s</div>' % (
						self.settingsHandViewer.actionPrefix('BringIn'),
						self.formatNum(hand, action.amount),
						self.settingsHandViewer.actionPostfix('BringIn')
						)
			elif action.type == action.TypeDiscardCards:
				if action.amount < 0:
					p | '<div class="playerActionDiscardCards">&nbsp;</div>'
				else:
					p | '<div class="playerActionDiscardCards">%i</div>' % action.amount
		if nActions is None:
			p | '<div class="playerActionNone">&nbsp;</div>'
		p << '</td>'

	def formattPot(self, p, hand, amounts):
		p >> '<tr>'
		pot = hand.calcPotSizes()
		#TODO: to save some space we don't display ante for individual player. good idea or not?
		potCellExtra = (
				self.settingsHandViewer.actionPrefix('Ante') +
				self.formatNum(hand, hand.blindAnte) +
				self.settingsHandViewer.actionPostfix('Ante')
				) if hand.blindAnte else '&nbsp;'
		sumAnte = sum([i.amount for i in hand.actions[hand.StreetBlinds] if i.type == i.TypePostBlindAnte])
		if sumAnte:
			p | '<td colspan="2" class="potCellExtra">%s (%s)</td>' % (potCellExtra, self.formatNum(hand, sumAnte))
		else:
			p | '<td colspan="2" class="potCellExtra">&nbsp;</td>'
		for amount in amounts:
			if amount < 0:
				p | '<td class="potCell">&nbsp;</td>'
			else:
				p | '<td class="potCell">%s</td>' % self.formatNum(hand, amount)
		p << '</tr>'

	def formattPlayer(self, p, hand, player):
		# add player summary column
		p >> '<td class="playerCell">'
		p | '<div class="playerName">%s</div><div class="playerStack">%s</div>' % (
					self.formatPlayerName(player.name),
					self.formatNum(hand, player.stack)
					)
		p << '</td>'

	def formattPlayerCards(self, p, hand, player, cards):
		p >> '<td class="playerCardsCell" valign="top">'
		self.htmlFormatCards(p, cards)
		p << '</td>'


	def formattHandDraw(self, p, hand):
		for player in hand.seats:
			if player is None: continue

			self.formattPlayerStart(p, hand, player)

			# add player name, stack and cards
			self.formattPlayer(p, hand, player)
			self.formattPlayerCards(p, hand, player, player.cards)

			# add player actions
			streetActions = []
			for street in hand.streets:
				actions = [action for action in hand.actions[street] if action.player is player]
				if street == hand.StreetBlinds:
					streetActions.append(actions)
				elif street == hand.StreetFirst:
					streetActions.append(actions)
				else:
					if actions:
						streetActions.append([actions.pop(0), ])	# discard cards action
						streetActions.append(actions)
					else:
						action = hand.Action(player, hand.Action.TypeDiscardCards, -1)
						streetActions.append([action, ])	# dummy discard cards action
						streetActions.append([])
			for actions in streetActions:
				self.formattPlayerActions(p, hand, player, actions)

			self.formattPlayerEnd(p, hand, player)

		# add pot
		pot = hand.calcPotSizes()
		amounts = []
		for street in hand.streets:
			if street != hand.StreetBlinds and street != hand.StreetFirst:
				amounts.append(-1)
			amounts.append(pot[street])
		self.formattPot(p, hand, amounts)


	def formattHandHoldem(self, p, hand):
		for player in hand.seats:
			if player is None: continue

			self.formattPlayerStart(p, hand, player)

			# add player name, stack and cards
			self.formattPlayer(p, hand, player)
			self.formattPlayerCards(p, hand, player, player.cards)

			# add player actions
			for street in hand.streets:
				actions = [action for action in hand.actions[street] if action.player is player]
				if not actions:
					actions = []
				self.formattPlayerActions(p, hand, player, actions)

			self.formattPlayerEnd(p, hand, player)

		# add pot size
		pot = hand.calcPotSizes()
		amounts = [pot[street] for street in hand.streets]
		self.formattPot(p, hand, amounts)

		# add board cards
		p >> '<tr>'
		p | '<td class="boardCardCellExtra" colspan="4">&nbsp;</td>'
		for street in hand.streets[2:]:
			p >> '<td class="boardCardCell" align="center">'
			if street == hand.StreetSecond:
				self.htmlFormatCards(p, hand.cards[:3])
			elif street == hand.StreetThird:
				self.htmlFormatCards(p, [hand.cards[3], ])
			elif street == hand.StreetRiver:
				self.htmlFormatCards(p, [hand.cards[4], ])
			p << '</td>'
		p << '</tr>'


	def formattHandStud(self, p, hand):
		maxCards = max([len(player.cards) for player in hand.seats if player is not None])
		for player in hand.seats:
			if player is None: continue

			self.formattPlayerStart(p, hand, player)

			# add player name, stack and cards
			self.formattPlayer(p, hand, player)
			cards = player.cards[:]
			while len(cards) < maxCards:
				cards.append(None)
			self.formattPlayerCards(p, hand, player, cards)

			# add player actions
			for street in hand.streets[1:]:
				actions = [action for action in hand.actions[street] if action.player is player]
				self.formattPlayerActions(p, hand, player, actions)

			self.formattPlayerEnd(p, hand, player)

		# add pot size
		pot = hand.calcPotSizes()
		amounts = [pot[street] for street in hand.streets[1:]]
		self.formattPot(p, hand, amounts)

	PatternHand = re.compile('.*\<pre \s+ class=\"HandSource\"\>(.+)\<\/pre\>', re.X|re.I|re.M|re.S)
	def handFromHtml(self, html):
		hand = Hand()
		result = self.PatternHand.search(html)
		if result is not None:
			handHistory = result.group(1)
			parser = HandParser()
			try:
				hand = parser.parse(handHistory)
			except NoGameHeaderError:
				pass
		return hand

#************************************************************************************
#
#************************************************************************************
class HandHistoryFile(object):

	def __init__(self, filePath):
		self.filePath = filePath
		self._handHistories = []
		self._data = None
		self._parse()

	def _parse(self):
		self._data = self._readFileData(self.filePath)
		handHistory = None
		#TODO: we could do a replace('\r', '\n') here
		for line in self._data.split('\n'):
			line = line.strip()
			if line.startswith('PokerStars Game #') or \
				line.startswith('PokerStars Home Game #') or \
				line.startswith('PokerStars Hand #') or \
				line.startswith('PokerStars Home Game Hand #') or \
				line.startswith('PokerStars Zoom Hand #'):
				handHistory = [line, ]
				continue
			elif handHistory and line:
				handHistory.append(line)
			elif handHistory and not line:
				p = '\n'.join(handHistory)
				self._handHistories.append(p)
				handHistory = None
		if handHistory:
			p = '\n'.join(handHistory)
			self._handHistories.append(p)

	def _readFileData(self, filePath):
		# stars seems to have switched to utf-8 at some time. more or less a guess
		# that it used to be iso-8859-1 before.
		fp = codecs.open(self.filePath, encoding='utf-8')
		try:
			data = fp.read()
			#NOTE: remove BOM if present
			if data.startswith(unicode(codecs.BOM_UTF8, 'utf-8')):
				data = data[1:]
			return data
		except UnicodeDecodeError:	pass
		finally:
			fp.close()
		fp = codecs.open(self.filePath, encoding='iso-8859-1')
		try:
			return fp.read()
		finally:
			fp.close()

	def __len__(self): return len(self._handHistories)
	def __getitem__(self, i): return self._handHistories[i]
	def __iter__(self): return iter(self._handHistories)
	def raw(self): return self._data

