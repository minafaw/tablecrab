# -*- coding: UTF-8 -*-

#TODO: tons. maybe iso hand to a generic library of poker hand types and work from there

import Tc2Config
from PyQt4 import QtCore
import re, codecs

import Tc2HandTypes

#************************************************************************************
# hand parser
#************************************************************************************
class NoGameHeaderError(Exception): pass

class HandParser(object):
	"""hand history parser
	"""

	Currencies = u'$€£'
	GameTypeMapping = {
			"Hold'em No Limit": {
					'gameType': Tc2HandTypes.PokerHand.GameTypeHoldem | Tc2HandTypes.PokerHand.GameLimitNoLimit,
					'gameName': 'Holdem (No Limt)',
					},
			"Hold'em Pot Limit": {
					'gameType': Tc2HandTypes.PokerHand.GameTypeHoldem | Tc2HandTypes.PokerHand.GameLimitPotLimit,
					'gameName': 'Holdem (Pot Limt)',
					},
			"Hold'em Limit": {
					'gameType': Tc2HandTypes.PokerHand.GameTypeHoldem | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Holdem (Limt)',
					},

			'Omaha Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Omaha (Limt)',
					},
			'Omaha Pot Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameLimitPotLimit,
					'gameName': 'Omaha Pot (Limt)',
					},
			'Omaha Hi/Lo Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Omaha Hi/Lo (Limt)',
					},
			'Omaha Hi/Lo Pot Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitPotLimit,
					'gameName': 'Omaha Hi/Lo Pot (Limt)',
					},

			'7 Card Stud Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': '7 Card Stud (Limt)',
					},
			'7 Card Stud Hi/Lo Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': '7 Card Stud Hi/Lo (Limt)',
					},

			'Razz Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeRazz | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Razz (Limt)',
					},

			'5 Card Draw No Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeFiveCardDraw | Tc2HandTypes.PokerHand.GameLimitNoLimit,
					'numPlayerCards': 5,
					'gameName': '5 Crad Draw (No Limt)',
					},
			'5 Card Draw Pot Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeFiveCardDraw | Tc2HandTypes.PokerHand.GameLimitPotLimit,
					'numPlayerCards': 5,
					'gameName': '5 Crad Draw (Pot Limt)',
					},
			'5 Card Draw Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeFiveCardDraw | Tc2HandTypes.PokerHand.GameLimitLimit,
					'numPlayerCards': 5,
					'gameName': '5 Crad Draw (Limt)',
					},

			'Single Draw 2-7 Lowball No Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeFiveCardDraw | Tc2HandTypes.PokerHand.GameSubTypeLo | Tc2HandTypes.PokerHand.GameLimitNoLimit,
					'gameName': 'Single Draw 2-7 Lowball (No Limit)',
					},

			'Triple Draw 2-7 Lowball No Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeTrippleDraw | Tc2HandTypes.PokerHand.GameSubTypeLo | Tc2HandTypes.PokerHand.GameLimitNoLimit,
					'gameName': 'Triple Draw 2-7 Lowball (No Limit)',
					},
			'Triple Draw 2-7 Lowball Pot Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeTrippleDraw | Tc2HandTypes.PokerHand.GameSubTypeLo | Tc2HandTypes.PokerHand.GameLimitPotLimit,
					'gameName': 'Triple Draw 2-7 Lowball (Pot Limit)',
					},
			'Triple Draw 2-7 Lowball Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeTrippleDraw | Tc2HandTypes.PokerHand.GameSubTypeLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Triple Draw 2-7 Lowball (Limit)',
					},

			'Badugi Limit': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeBadugi | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Badugi (Limit)',
					},


			"HORSE (Hold'em Limit,": {
					'gameType': Tc2HandTypes.PokerHand.GameTypeHoldem | Tc2HandTypes.PokerHand.GameLimitNoLimit,
					'gameName': 'Holdem (Limit)',
					},
			'HORSE (Omaha Hi/Lo Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Omaha Hi/Lo (Limit)',
					},
			'HORSE (7 Card Stud Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': '7 Card Stud (Limit)',
					},
			'HORSE (7 Card Stud Hi/Lo Limit,':	{
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': '7 Card Stud Hi/Lo (Limit)',
					},
			'HORSE (Razz Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeRazz | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Razz (Limit)',
					},

			"Mixed NLH/PLO (Hold'em No Limit,": {
					'gameType': Tc2HandTypes.PokerHand.GameTypeHoldem | Tc2HandTypes.PokerHand.GameLimitNoLimit,
					'gameName': 'Holdem (No Limit)',
					},
			'Mixed NLH/PLO (Omaha Pot Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameLimitPotLimit,
					'gameName': 'Omaha (Pot Limit)',
					},

			'8-Game (Razz Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeRazz | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Razz (Limit)',
					},
			'8-Game (Omaha Hi/Lo Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Omaha Hi/Lo (Limit)',
					},
			'8-Game (7 Card Stud Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': '7 Card Stud (Limit)',
					},
			'8-Game (7 Card Stud Hi/Lo Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': '7 Card Stud Hi/Lo (Limit)',
					},
			"8-Game (Hold'em No Limit,": {
					'gameType': Tc2HandTypes.PokerHand.GameTypeHoldem | Tc2HandTypes.PokerHand.GameLimitNoLimit,
					'gameName': 'Holdem (No Limt)',
					},
			"8-Game (Hold'em Limit,": {
					'gameType': Tc2HandTypes.PokerHand.GameTypeHoldem | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Holdem (Limt)',
					},
			'8-Game (Omaha Pot Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeOmaha | Tc2HandTypes.PokerHand.GameLimitPotLimit,
					'gameName': 'Omaha (Pot Limt)',
					},
			'8-Game (Triple Draw 2-7 Lowball Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeTrippleDraw | Tc2HandTypes.PokerHand.GameSubTypeLo | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Triple Draw 2-7 Lowball (Limit)',
					},

			'Triple Stud (7 Card Stud Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': '7 Card Stud (Limit)',
					},
			'Triple Stud (Razz Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeRazz | Tc2HandTypes.PokerHand.GameLimitLimit,
					'gameName': 'Razz (Limit)',
					},
			'Triple Stud (7 Card Stud Hi/Lo Limit,': {
					'gameType': Tc2HandTypes.PokerHand.GameTypeStud | Tc2HandTypes.PokerHand.GameSubTypeHiLo | Tc2HandTypes.PokerHand.GameLimitLimit,
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

	PatGameHeader1 = re.compile('^PokerStars\s (Home\s)? Game\s \#[0-9]+\:\s* .*? (?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
	PatGameHeader2 = re.compile('^PokerStars\s (Home\sGame\s)? Hand\s \#[0-9]+\:\s* .*? (?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
	PatGameHeader3 = re.compile('^PokerStars\s Zoom\s Hand\s \#[0-9]+\:\s*  .*? (?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
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
				cards = self.stringToCards(cards)
				if len(cards) == 3:
					hand.playerFromName(result.group('player')).cards = cards
				else:
					hand.playerFromName(result.group('player')).cards += cards
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
		@return: L{Tc2HandTypes.PokerHand} or None if string could not be parsed
		"""

		# create new hand object
		hand = Tc2HandTypes.PokerHand()
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

s = '''PokerStars Hand #80908721832:  7 Card Stud Limit ($0.04/$0.08 USD) - 2012/05/23 23:24:52 CET [2012/05/23 17:24:52 ET]
Table 'Equinox IV' 8-max
Seat 1: gugulu300 ($1.52 in chips)
Seat 2: AMKIreland ($0.97 in chips)
Seat 3: RomiTu ($0.49 in chips)
Seat 4: tobberdje ($1.49 in chips)
Seat 5: Kirilma ($0.61 in chips)
Seat 6: failertb ($2.85 in chips)
Seat 7: BNDee ($9.46 in chips)
Seat 8: raaah73 ($1.45 in chips)
gugulu300: posts the ante $0.01
AMKIreland: posts the ante $0.01
RomiTu: posts the ante $0.01
tobberdje: posts the ante $0.01
Kirilma: posts the ante $0.01
failertb: posts the ante $0.01
BNDee: posts the ante $0.01
raaah73: posts the ante $0.01
*** 3rd STREET ***
Dealt to gugulu300 [Ah]
Dealt to AMKIreland [8h]
Dealt to RomiTu [2d]
Dealt to tobberdje [As]
Dealt to Kirilma [Ts]
Dealt to failertb [6d Jd Jc]
Dealt to BNDee [9d]
Dealt to raaah73 [8d]
RomiTu: brings in for $0.02
tobberdje: calls $0.02
Kirilma: calls $0.02
failertb: raises $0.02 to $0.04
BNDee: folds
raaah73: calls $0.04
gugulu300: calls $0.04
AMKIreland: folds
RomiTu: raises $0.04 to $0.08
tobberdje: folds
Kirilma: calls $0.06
failertb: calls $0.04
raaah73: calls $0.04
gugulu300: calls $0.04
*** 4th STREET ***
Dealt to gugulu300 [Ah] [4h]
Dealt to RomiTu [2d] [Th]
Dealt to Kirilma [Ts] [Qd]
Dealt to failertb [6d Jd Jc] [5s]
Dealt to raaah73 [8d] [5h]
gugulu300: checks
RomiTu: bets $0.04
Kirilma: raises $0.04 to $0.08
failertb: folds
raaah73: folds
gugulu300: calls $0.08
RomiTu: raises $0.04 to $0.12
Kirilma: raises $0.04 to $0.16
Betting is capped
gugulu300: calls $0.08
RomiTu: calls $0.04
*** 5th STREET ***
Dealt to gugulu300 [Ah 4h] [Js]
Dealt to RomiTu [2d Th] [9c]
Dealt to Kirilma [Ts Qd] [Td]
Kirilma: bets $0.08
gugulu300: calls $0.08
RomiTu: raises $0.08 to $0.16
Kirilma: raises $0.08 to $0.24
gugulu300: calls $0.16
RomiTu: calls $0.08 and is all-in
*** 6th STREET ***
Dealt to gugulu300 [Ah 4h Js] [4s]
Dealt to RomiTu [2d Th 9c] [3s]
Dealt to Kirilma [Ts Qd Td] [6s]
Kirilma: bets $0.08
gugulu300: calls $0.08
*** RIVER ***
Kirilma: bets $0.04 and is all-in
gugulu300: calls $0.04
*** SHOW DOWN ***
Kirilma: shows [7h 2h Ts Qd Td 6s 4d] (a pair of Tens)
gugulu300: shows [5d 4c Ah 4h Js 4s Qs] (three of a kind, Fours)
gugulu300 collected $0.24 from side pot
RomiTu: shows [Kh Ks 2d Th 9c 3s Ad] (a pair of Kings)
gugulu300 collected $1.66 from main pot
*** SUMMARY ***
Total pot $1.94 Main pot $1.66. Side pot $0.24. | Rake $0.04
Seat 1: gugulu300 showed [5d 4c Ah 4h Js 4s Qs] and won ($1.90) with three of a kind, Fours
Seat 2: AMKIreland folded on the 3rd Street (didn't bet)
Seat 3: RomiTu showed [Kh Ks 2d Th 9c 3s Ad] and lost with a pair of Kings
Seat 4: tobberdje folded on the 3rd Street
Seat 5: Kirilma showed [7h 2h Ts Qd Td 6s 4d] and lost with a pair of Tens
Seat 6: failertb folded on the 4th Street
Seat 7: BNDee folded on the 3rd Street (didn't bet)
Seat 8: raaah73 folded on the 4th Street

'''

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
