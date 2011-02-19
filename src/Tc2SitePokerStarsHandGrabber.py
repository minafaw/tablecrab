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
	StreetPreflop = 2
	StreetFlop  = 3
	StreetTurn = 4
	StreetRiver = 5
	StreetShowdown = 6
	StreetSummary = 7
	GameTypeNone = 0x0
	GameTypeHoldem = 1 << 0
	GameTypeOmaha = 1 << 1
	GameSubTypeHiLo = 1 << 20
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
		def __init__(self, player=None, type=TypeNone, amount=0.0):
			self.player = player
			self.type = type
			self.amount = amount
	class Player(object):
		def __init__(self, name='', stack=0.0, cards=None):
			self.name = name
			self.stack = stack
			self.cards = ['', ''] if cards is None else cards
	def __init__(self):
		QtCore.QObject.__init__(self)
		self.handHistory = ''
		self.gameType = self.GameTypeNone
		self.numPlayercards = 0
		self.seats = []					# len(seats) == maxPlayers. empty seat is set to None
		self.cards = ['', '', '', '', '']
		self.blindAnte = 0.0
		self.blindSmall = 0.0
		self.blindBig = 0.0
		self.hasCents = True		# flag indicating if bet cents is discovered or not
		self.seatNoButton = None
		self.tableName = ''
		self.actions = {
				self.StreetBlinds: [],
				self.StreetPreflop: [],
				self.StreetFlop: [],
				self.StreetTurn: [],
				self.StreetRiver: [],
				}

	def calcPotSizes(self):
		streets = (self.StreetBlinds, self.StreetPreflop, self.StreetFlop, self.StreetTurn, self.StreetRiver)
		result = dict([(street, 0.0) for street in streets])
		players = [player for player in self.seats if player is not None]
		bets = dict( [(player, 0.0) for player in players])
		for street in streets:
			for player in players:
				actions = [action for action in self.actions[street] if action.player is player]
				for action in actions:
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
	GameTypeMapping= {
			"Hold'em No Limit": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitNoLimit,
					'numPlayerCards': 2,
					},
			"Hold'em Pot Limit": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitPotLimit,
					'numPlayerCards': 2,
					},
			"Hold'em Limit": {
					'gameType': Hand.GameTypeHoldem | Hand.GameLimitLimit,
					'numPlayerCards': 2,
					},
			'Omaha Limit': {
					'gameType': Hand.GameTypeOmaha | Hand.GameLimitLimit,
					'numPlayerCards': 4,
					},
			'Omaha Pot Limit': {
					'gameType': Hand.GameTypeOmaha | Hand.GameLimitPotLimit,
					'numPlayerCards': 4,
					},
			'Omaha Hi/Lo Limit': {
					'gameType': Hand.GameTypeOmaha | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'numPlayerCards': 4,
					},
			'Omaha Hi/Lo Pot Limit':	{
					'gameType': Hand.GameTypeOmaha | Hand.GameSubTypeHiLo | Hand.GameLimitLimit,
					'numPlayerCards': 4,
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

	PatGameHeader = re.compile('^PokerStars\s (Home\s)? Game\s \#[0-9]+\:\s .*? \s(?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
	def matchGameHeader(self, hand, streetCurrent, line):
		result = self.PatGameHeader.match(line)
		if result is not None:
			gameType = self.GameTypeMapping[result.group('gameType')]
			hand.gameType = gameType['gameType']
			hand.numPlayerCards = gameType['numPlayerCards']
		return result is not None

	#NOTE: in tourneys <tableName> is composed of 'tourneyID tableNo'. no idea if this is of any relevance to us
	PatternTableInfo = re.compile('^Table \s \' (?P<tableName>.+?) \' \s (?P<maxPlayers>[0-9]+)\-max \s Seat \s \#(?P<seatNoButton>[0-9]+) \s is \s the \s button', re.X)
	def matchTableInfo(self, hand, streetCurrent, line):
		result = self.PatternTableInfo.match(line)
		if result is not None:
			hand.tableName = result.group('tableName')
			hand.seats = [None for i in range( int(result.group('maxPlayers') ))]
			hand.seatNoButton = int(result.group('seatNoButton')) -1
		return result is not None

	PatternSeat = re.compile('^Seat \s(?P<seatNo>[0-9]+)\:\s   (?P<player>.*) \s\( [%s]? (?P<stack>[\d\.]+)\s?.*  \)' % Currencies, re.X)
	def matchSeat(self, hand, streetCurrent, line):
		result= self.PatternSeat.match(line)
		if result is not None:
			player = hand.Player(
					name=result.group('player'),
					stack=self.stringToFloat(result.group('stack')),
					cards=[''] * hand.numPlayerCards,
					)
			seatNo = int(result.group('seatNo')) -1
			hand.seats[seatNo] = player
		return result is not None

	PatternDealtTo = re.compile('Dealt \s to \s (?P<player>.+?) \s \[  (?P<cards>.+?) \]', re.X)
	def matchDealtTo(self, hand, streetCurrent, line):
		result = self.PatternDealtTo.match(line)
		if result is not None:
			hand.playerFromName(result.group('player')).cards = self.stringToCards(result.group('cards'))
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

	PatternBoardCards = re.compile('^Board \s \[  (?P<cards>.*?)   \]', re.X)
	def matchBoardCards(self, hand, streetCurrent, line):
		result = self.PatternBoardCards.match(line)
		if result is not None:
			hand.cards = self.stringToCards(result.group('cards'), zfill=5)
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

	PatternCheck = re.compile('^(?P<player>.+?) \:\s checks', re.X)
	def matchCheck(self, hand, streetCurrent, line):
		result = self.PatternCheck.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeCheck)
			hand.actions[streetCurrent].append(action)
		return result is not None

	PatternFold = re.compile('^(?P<player>.+?) \:\s folds', re.X)
	def matchFold(self, hand, streetCurrent, line):
		result = self.PatternFold.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeFold)
			hand.actions[streetCurrent].append(action)
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

		# clean handHistory up a bit to make it easier on us..
		handHistory = hand.handHistory.replace('(small blind) ', '').replace('(big blind) ', '').replace('(button) ', '').replace('(Play Money) ', '')

		for lineno, line in enumerate(handHistory.split('\n')):
			line = line.strip()
			if not line: continue

			if lineno == 0:
				if self.matchGameHeader(hand, streetCurrent, line): continue
				raise NoGameHeaderError('No gane header found')

			# determine street we are in
			if line.startswith('*** HOLE CARDS ***'):
				streetCurrent = hand.StreetPreflop
				continue
			elif line.startswith('*** FLOP ***'):
				streetCurrent = hand.StreetFlop
				continue
			elif line.startswith('*** TURN ***'):
				streetCurrent = hand.StreetTurn
				continue
			elif line.startswith('*** RIVER ***'):
				streetCurrent = hand.StreetRiver
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
			elif streetCurrent == hand.StreetShowdown:
				#TODO: just a guess that it is possible to show cards on showdown
				if self.matchShowsCards(hand, streetCurrent, line): continue
			elif streetCurrent == hand.StreetSummary:
				if self.matchBoardCards(hand, streetCurrent, line): continue
				if self.matchShowedCards(hand, streetCurrent, line): continue
				if self.matchMuckedCards(hand, streetCurrent, line): continue
			else:
				if streetCurrent == hand.StreetPreflop:
					if self.matchDealtTo(hand, streetCurrent, line): continue

				if self.matchShowsCards(hand, streetCurrent, line): continue
				if self.matchCheck(hand, streetCurrent, line): continue
				if self.matchFold(hand, streetCurrent, line): continue
				if self.matchCall(hand, streetCurrent, line): continue
				if self.matchBet(hand, streetCurrent, line): continue
				if self.matchRaise(hand, streetCurrent, line): continue

		# postprocess hand
		hand.hasCents = (hand.blindAnte, hand.blindSmall, hand.blindBig) != (int(hand.blindAnte), int(hand.blindSmall), int(hand.blindBig))

		# errorcheck
		if hand.seatNoButton is None:
			raise ValueError('Could not determine button player')
		return hand

#********************************************************************************************************
# hand formatters
#********************************************************************************************************
HtmlCardSuitMapping = {		# suit --> (entity, htmlKlass)
		's': ('&spades;', 'cardSuitSpade'),
		'c': ('&clubs;', 'cardSuitClub'),
		'd': ('&diams;', 'cardSuitDiamond'),
		'h': ('&hearts;', 'cardSuitHeart'),
		}

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
	PrefixCheck = 'ck'
	PrefixFold = 'f'

	MaxPlayerName = -1
	# and this is the css for the html file
	StyleSheet = '''.handBody{}
.handTable{
        border-spacing: 0px;
        border-collapse: collapse;
        }
.handSource{margin-top: 1em;}


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
        margin-left: auto;        /* centers contents of the cell */
        margin-right: auto;    /* centers contents of the cell */
        }
.boardCards{
        border: 0px;
        border-spacing: 0px;
        margin-left: auto;        /* centers contents of the cell */
        margin-right: auto;    /* centers contents of the cell */
        }


.cardCell{padding: 0px;}
.card{
        border: solid 1px;
        background-color: red;
        border-spacing: 0px;
        margin-left: auto;        /* centers contents of the cell */
        margin-right: auto;    /* centers contents of the cell */
        }
.cardShape{
        padding: 0px 0px 0px 0px;
        background-color: white;
        }
.cardSuit{
        text-indent:0.3em;
        padding: 0px 0px 0px 0px;
        background-color: white;
        }
.cardSuitSpade{color: black;}
.cardSuitClub{color: black;}
.cardSuitHeart{color: red;}
.cardSuitDiamond{color: red;}
.cardBack{
        color: #355b73;
        background-color: #355b73;
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

	def htmlFormatCards(self, p, cardsType, *cards):
		if cardsType == 'playerCards':
			p >> '<table class="playerCards">'
		elif  cardsType == 'boardCards':
			p >> '<table class="boardCards">'
		else:
			raise ValueError('unknown cardsType: %s' % cardsType)
		p >> '<tr>'
		for card in cards:
			if not card:
				#TODO: == card back. dont realy know what to return in this case - i am not not a Css guru.
				shape = '&nbsp;'
				htmlSuit = '&nbsp;&nbsp;'
				htmlKlass = 'cardBack'
			else:
				shape = card[0]
				htmlSuit, htmlKlass = HtmlCardSuitMapping[card[1]]
			p >> '<td class="cardCell">'
			#p >> '<div class="card">'
			p | '<div class="card"><div class="cardShape %s">%s</div><div class="cardSuit %s">%s</div></div>' % (htmlKlass, shape, htmlKlass, htmlSuit)
			#p << '</div>'
			p <<  '</td>'
		p << '</tr>'
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

		for player in hand.seats:
			if player is None: continue

			p >> '<tr>'

			# add player summary column
			p >> '<td class="playerCell">'
			p | '<div class="playerName">%s</div><div class="playerStack">%s</div>' % (
						self.formatPlayerName(player.name),
						self.formatNum(hand, player.stack)
						)
			p << '</td>'

			# add pocket cards column
			p >> '<td class="playerCardsCell">'
			self.htmlFormatCards(p, 'playerCards', *player.cards)
			p << '</td>'

			# add player actions
			for street in (hand.StreetBlinds, hand.StreetPreflop, hand.StreetFlop, hand.StreetTurn, hand.StreetRiver):
				actions = [action for action in hand.actions[street] if action.player is player]
				p >> '<td class="playerActionsCell">'
				nActions = None
				for nActions, action in enumerate(actions):
					if action.type == action.TypeFold:
						p | '<div class="playerActionFold">%s</div>' % self.settingsHandViewer.actionPrefix('Fold')
					elif action.type == action.TypeCheck:
						p |  '<div class="playerActionCheck">%s</div>' % self.settingsHandViewer.actionPrefix('Check')
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

				if nActions is None:
					p | '&nbsp;'
				p << '</td>'

			p << '</tr>'

		# add pot size
		p >> '<tr>'
		pot = hand.calcPotSizes()
		#TODO: to save some space we don't display ante for individual player. good idea or not?
		potCellExtra = (
				self.settingsHandViewer.actionPrefix('Ante') +
				self.formatNum(hand, hand.blindAnte) +
				self.settingsHandViewer.actionPostfix('Ante')
				) if hand.blindAnte else '&nbsp;'
		p | '<td colspan="2" class="potCellExtra">%s</td>' % potCellExtra
		p | '<td class="potCell">%s</td>' % self.formatNum(hand, pot[hand.StreetBlinds])
		p | '<td class="potCell">%s</td>' % self.formatNum(hand, pot[hand.StreetPreflop])
		p | '<td class="potCell">%s</td>' % (self.formatNum(hand, pot[hand.StreetFlop]) if hand.cards[2] else '&nbsp;')
		p | '<td class="potCell">%s</td>' % (self.formatNum(hand, pot[hand.StreetTurn]) if hand.cards[3] else '&nbsp;')
		p | '<td class="potCell">%s</td>' % (self.formatNum(hand, pot[hand.StreetRiver]) if hand.cards[4] else '&nbsp;')
		p << '</tr>'

		# add board cards + hand history source
		p >> '<tr>'
		p | '<td class="boardCardCellExtra" colspan="4">&nbsp;</td>'
		p >> '<td class="boardCardCell">'
		self.htmlFormatCards(p, 'boardCards', hand.cards[0], hand.cards[1], hand.cards[2])
		p << '</td>'
		p >> '<td class="boardCardCell">'
		self.htmlFormatCards(p, 'boardCards', hand.cards[3])
		p << '</td>'
		p >> '<td class="boardCardCell">'
		self.htmlFormatCards(p, 'boardCards', hand.cards[4])
		p << '</td>'
		p << '</tr>'

		# dump html to file
		p << '</table>'
		p | '<pre class="handSource">%s</pre>' % self.htmlEscapeString(hand.handHistory, spaces=False)
		p << '</body>'
		p << '</html>'

		return p.data.encode('utf-8')

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
			if line.startswith('PokerStars Game #') or line.startswith('PokerStars Home Game #'):
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
			if data.startswith(u'\ufeff'):
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



