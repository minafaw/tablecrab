# -*- coding: UTF-8 -*-s

'''standalone PokerStars "instant hand history" grabber

this programm runs a standalone to grab, format and dump to html the hand history currently
displayed in PokerStars "instant hand history". there is no viewer for the file, so an idea is to load 
the dumped file into a browser and set the browser to autorefresh every N seconds.

@requires: python >= 2.6
@usage: path/to/python PokerStarsHandHistoryGrabber.py [path/toMyConfig.cfg]

'''
from __future__ import with_statement
import re, time, sys, os, cStringIO, logging, logging.handlers, traceback
import ConfigParser

__application_name__ = 'PokerStarsHandHistoryGrabber'
__version__ = '0.1.0'
__author__ = 'juergen urner'
__email__ = 'jUrner@arcor.de'
__release_name__ = '%s-%s' % (__application_name__, __version__)
#***********************************************************************************************
#
#***********************************************************************************************
logger = logging.getLogger(__application_name__)
excHandler = logging.handlers.RotatingFileHandler(
		os.path.join(os.path.dirname(os.path.abspath(__file__)), 'User', 'Errlog.log'),
		mode='a',
		maxBytes=32000,
		backupCount=0,
		)
excHandler.setLevel(logging.CRITICAL)
logger.addHandler(excHandler)

class Config(object):
	"""ConfigParser wraper class"""
	def __init__(self, filename=None, string=None):
		"""
		@param filename: (str) filename of the file to parse for config values
		@param string: ..alteranatively a string to parse for config values
		"""
		self.filename = filename
		self._configParser = ConfigParser.ConfigParser()
		self._configParser.optionxform = lambda x: x
		if filename is not None: self._configParser.read([self.filename, ])
		elif string is not None: self._configParser.readfp(cStringIO.cStringIO(string))
	def flush(self):
		"""flushes config values to disk if possible
		@return: always None
		"""
		if self.filename is not None:
			with open(self.filename, 'w') as fp:
				self._configParser.write(fp)
	def get(self, section, option, default, valueType):
		"""returns a config value. if the config value is not present it will be created
		@param section: (str) section the config vsalue is located in
		@param option: (str) option name
		@param default: (str) default value of the value
		@param valueType: (method) to call to convert the value to a desired type. if the value can not be converted the method should raise a ValueError
		@return: whatever the valueType method returns
		"""
		isDirty = False
		if not self._configParser.has_section(section): 
			isDirty = True
			self._configParser.add_section(section)
		if not self._configParser.has_option(section, option):
			isDirty = True
			self._configParser.set(section, option, default)
		if isDirty: self.flush()
		value = default
		try: value = valueType(self._configParser.get(section, option))
		except ValueError: self._configParser.set(section, option, default)
		return value	
	def set(self, section, option, value, flush=True):
		"""sets a config value
		@param section: (str) section the config vsalue is located in
		@param option: (str) option name
		@param value: (str) string representation of the value
		@param flush: (bool) if True the config is flushed to disk in the call. if False not
		@return: always None
		"""
		if not self._configParser.has_section(section):
			self._configParser.add_section(section)
		self._configParser.set(section, option, value)
		if flush: self.flush()
	def bool(self, value):
		"""converts a config value to a python bool. recognized values are "true", "yes", "y", "1" (case-insensitive) as True. everything else is interpreted as False
		@param value: (str) value to convert
		@return: (bool)
		"""
		if value.lower() in ('true', 'yes', 'y', '1'):
			return True
		return False

#***********************************************************************************************
#
#***********************************************************************************************
class Hand(object):
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
		self.handHistory = ''
		self.gameType = self.GameTypeNone
		self.numPlayercards = 0
		self.seats = []					# len(seats) == maxPlayers. empty seat is set to None
		self.cards = ['', '', '', '', '']
		self.blindAnte = 0.0
		self.blindSmall = 0.0
		self.blindBig = 0.0
		self.hasCents = True		# flag indicating if cent bets is allowed or not
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
	
#********************************************************************************************************
# hand parser
#********************************************************************************************************
class HandHistoryParser(object):
	"""hand history parser
	"""	
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
		
	def __init__(self, config):
		"""
		@param config: L{Config}
		"""
		self.config = config
		
	def stringToFloat(self, string):
		return float(string.replace(',', ''))
		
	def stringToCards(self, string, zfill=None):
		cards = string.split(' ')
		if zfill:
			cards += ['']*zfill
			return cards[:zfill]
		return cards
		
	PatGameHeader = re.compile('^PokerStars\s Game\s \#[0-9]+\:\s .*? \s(?P<gameType>%s)\s.*' % '|'.join([re.escape(i).replace('\ ', '\s') for i in GameTypeMapping]), re.X)
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
			hand.seatNoButton = int(result.group('seatNoButton'))
		return result is not None
			
	PatternSeat = re.compile('^Seat \s(?P<seatNo>[1-9]+)\:\s   (?P<player>.*?) \s\( [$€]? (?P<stack>.*?)\s.*  \)', re.X)
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
	PatternPostAnte =  re.compile('^(?P<player>.*?)\: \s posts \s the \s ante \s [$€]? (?P<amount>[0-9\.\,]+ )', re.X)
	def matchPostAnte(self, hand, streetCurrent, line):
		result = self.PatternPostAnte.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypePostBlindAnte, amount=amount)
			hand.actions[streetCurrent].append(action)
			hand.blindAnte = max(amount, hand.blindAnte)
		return result is not None
		
	PatternPostSmallBlind = re.compile('^(?P<player>.*?)\: \s posts \s small \s blind \s [$€]? (?P<amount>[0-9\.\,]+)', re.X)
	def matchPostSmallBlind(self, hand, streetCurrent, line):
		result = self.PatternPostSmallBlind.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypePostBlindSmall, amount=amount)
			hand.actions[streetCurrent].append(action)
			hand.blindSmall = max(amount, hand.blindSmall)
		return result is not None
	
	PatternPostBigBlind = re.compile('^(?P<player>.*?)\: \s posts \s big \s blind \s [$€]? (?P<amount>[0-9\.\,]+ )', re.X)
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
	
	PatternCall = re.compile('^(?P<player>.+?) \:\s calls \s [$€]? (?P<amount>[0-9\.\,]+)', re.X)
	def matchCall(self, hand, streetCurrent, line):
		result = self.PatternCall.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeCall, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None
	
	PatternBet = re.compile('^(?P<player>.+?) \:\s bets \s [$€]? (?P<amount>[0-9\.\,]+)', re.X)
	def matchBet(self, hand, streetCurrent, line):
		result = self.PatternBet.match(line)
		if result is not None:
			player = hand.playerFromName(result.group('player'))
			action = hand.Action(player=player, type=hand.Action.TypeBet, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None
	
	PatternRaise = re.compile('^(?P<player>.+?) \:\s raises \s  .*?\s to \s [$€]? (?P<amount>[0-9\.\,]+)', re.X)
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
				return None
			
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
			raise ValueError('could not determine button player')
		
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
	# and this is the css for the html file
	Css = '''
						.handHistoryBody{
					margin-left:0px;
					margin-top:0px;
					}
			.handHistoryTable{
					border-spacing: 0px; 
					border-collapse:collapse;
					}
			.handHistorySource{margin-top:10em;}
			
			.playerCell{
					vertical-align:top; 
					border:1px solid black; 
					}
			.playerName{}
			.playerStack{}
					
			.playerCardsCell{border:1px solid black;}
			.playerActionsCell{
					white-space:nowrap;
					vertical-align:top;padding-left:0.1em; 
					border:1px solid black; 
					}
			
			.potCell{
					text-align: center;
					border:1px solid black; 
					}
			.potCellExtra{
					padding-left:1em; 
					border:1px solid black; 
					}
			
			.boardCardCell{border:1px solid black;}
			.boardCardCellExtra{border:1px solid black; }
			
			.cards{
					border: 0px; 
					border-spacing: 0px;
					}
			.cardCell{padding: 0px;}
			.card{
					border:solid 1px;
					background-color:red;
					border-spacing: 0px;
					margin-left:auto;		/* centers contents of the cell */
					margin-right:auto;	/* centers contents of the cell */
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
			.cardSuitSpade{color:black;}
			.cardSuitClub{color:black;}
			.cardSuitHeart{color:red;}
			.cardSuitDiamond{color:red;}
			.cardBack{
					color:#355b73;
					background-color:#355b73;
					}
					
			.playerActionFold{}
			.playerActionCall{background-color:#87CEFA ;}
			.playerActionCheck{background-color:#98FB98;}
			.playerActionBet{background-color:#FFA54F;}
			.playerActionRaise{background-color:#FF6EB4;}
			.playerActionPostBlindBig{}
			.playerActionPostBlindSmall{}
		
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
				
	def __init__(self, config):
		'''
		@param config: L{Config}
		'''
		self.config = config
	
	def formatNum(self, hand, num, toInt=False):
		if not num:
			result = ''
		elif hand.hasCents:
			if self.config.get('HandFornmatterHtmlTabular', 'NoFloatingPoint', 'yes', self.config.bool):
				result = str(int(num*100))
			else:
				result = str(num)
		else:
			result = str(int(num))
		return result
			
	def htmlEscapeString(self, string, spaces=True):
		string = string.replace('&', '&#38;').replace('"', '&#34;').replace("'", '&#39;').replace('<', '&#60;').replace('>', '&#62;')
		if spaces:
			string = string.replace(' ', '&nbsp;')
		return string
	
	def htmlFormatCards(self, p, *cards):
		p >> '<table class="cards">'
		p >> '<tr>'
		for card in cards:
			if not card:
				shape = 'A'
				htmlSuit = '&diams;'
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
			
	def formatPlayerName(self, playerName):
		maxPlayerName = self.config.get('HandFornmatterHtmlTabular', 'MaxPlayerName', '10', int)
		if maxPlayerName and len(playerName) > maxPlayerName:
			playerName = playerName[:maxPlayerName-2] + '..'
		return self.htmlEscapeString(playerName, spaces=True)
		
	def dump(self, hand):
		
		p = self.IndentBuffer()
		
		# setup html page
		p >> '<html>'
		p >> '<head>'
		p | '<meta name="author" content="TableCrab">'
		p | '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		p | '<style type="text/css"><!-- %s --></style>' % self.config.get('HandFornmatterHtmlTabular', 'Css', self.Css, str)
		p << '</head>'
		
		p >> '<body class="handHistoryBody">'
		p >> '<table class="handHistoryTable">'
		
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
			self.htmlFormatCards(p, *player.cards)
			p << '</td>'
			
			# add player actions
			for street in (hand.StreetBlinds, hand.StreetPreflop, hand.StreetFlop, hand.StreetTurn, hand.StreetRiver):
				actions = [action for action in hand.actions[street] if action.player is player]
				p >> '<td class="playerActionsCell">'
				nActions = None
				for nActions, action in enumerate(actions):
					if action.type == action.TypeFold: 
						p | '<div class="playerActionFold">%s</div>' % self.config.get('HandFornmatterHtmlTabular', 'PrefixFold', 'f', str)
					elif action.type == action.TypeCheck: 
						p |  '<div class="playerActionCheck">%s</div>' % self.config.get('HandFornmatterHtmlTabular', 'PrefixCheck', 'ck', str)
					elif action.type == action.TypeBet:
						p | '<div class="playerActionBet">%s%s%s</div>' % (
								self.config.get('HandFornmatterHtmlTabular', 'PrefixBet', 'b', str), 
								self.formatNum(hand, action.amount), 
								self.config.get('HandFornmatterHtmlTabular', 'PostfixBet', '', str)
								)
					elif action.type == action.TypeRaise:
						p | '<div class="playerActionRaise">%s%s%s</div>' % (
								self.config.get('HandFornmatterHtmlTabular', 'PrefixRaise', 'r', str), 
								self.formatNum(hand, action.amount), 
								self.config.get('HandFornmatterHtmlTabular', 'PostfixRaise', '', str)
								)
					elif action.type == action.TypeCall:
						p | '<div class="playerActionCall">%s%s%s</div>' % (
								self.config.get('HandFornmatterHtmlTabular', 'PrefixCall', 'c', str), 
								self.formatNum(hand, action.amount), 
								self.config.get('HandFornmatterHtmlTabular', 'PostixCall', '', str)
								)
					elif action.type == action.TypePostBlindBig:
						p | '<div class="playerActionPostBlindBig">%s%s%s</div>' % (
								self.config.get('HandFornmatterHtmlTabular', 'PrefixBigBlind', 'bb', str), 
								self.formatNum(hand, action.amount), 
								self.config.get('HandFornmatterHtmlTabular', 'PostfixBigBlind', '', str)
								)
					elif action.type == action.TypePostBlindSmall:
						p | '<div class="playerActionPostBlindSmall">%s%s%s</div>' % (
								self.config.get('HandFornmatterHtmlTabular', 'PrefixSmallBlind', 'sb', str), 
								self.formatNum(hand, action.amount), 
								self.config.get('HandFornmatterHtmlTabular', 'PostfixSmallBlind', '', str)
								)
				
				if nActions is None:
					p | '&nbsp;'
				p << '</td>'		
				
			p << '</tr>'
				
		# add pot size
		p >> '<tr>'
		pot = hand.calcPotSizes()
		#TODO: to save some space we don't display ante for individual player. good idea or not?
		potCellExtra = (self.config.get('HandFornmatterHtmlTabular', 'PrefixAnte', 'ante ', str) + self.formatNum(hand, hand.blindAnte) + self.config.get('HandFornmatterHtmlTabular', 'PostixAnte', '', str)) if hand.blindAnte else '&nbsp;'
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
		self.htmlFormatCards(p, hand.cards[0], hand.cards[1], hand.cards[2])
		p << '</td>'
		p >> '<td class="boardCardCell">'
		self.htmlFormatCards(p, hand.cards[3])
		p << '</td>'
		p >> '<td class="boardCardCell">'
		self.htmlFormatCards(p, hand.cards[4])
		p << '</td>'
		p << '</tr>'
		
		# dump html to file
		p << '</table>'
		p | '<pre class="handHistorySource">%s</pre>' % self.htmlEscapeString(hand.handHistory, spaces=False)
		p << '</body>'
		p << '</html>'
		
		#NOTE: we have to take care not to accidently dump an os dependend filename into default config. so keep default as ''
		filename = self.config.get('HandFornmatterHtmlTabular', 'OutputFile', '', str)
		if not filename:	
			filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'User', 'PokerStarsHandHistory.html')
		with open(filename, 'w') as fp:
			fp.write(p.data.encode('utf-8'))

#**********************************************************************************************************
# hand grabber (only available on win32 platforms)
#**********************************************************************************************************
InstantHandHistoryGrabber = None
if sys.platform == 'win32':
	class InstantHandHistoryGrabber(object):
		"""hand history grabber
		
		server to grab the current hand history from PokerStars InstantHandHistory dialog
		@note: this server is only available on windows oses. on other oses it is set to None
		"""
		
		WindowClassName = '#32770'
		WindowTitle = 'Instant Hand History'
		WidgetClassName = 'PokerStarsViewClass'
		
		def __init__(self, config, handParser, handFormatter):
			self.config = config
			self.handParser = handParser
			self.handFormatter = handFormatter
			self._isRunning = False
			
		def stopServer(self):
			"""stops the server
			@return: always None
			"""
			self._isRunning = False
				
		def startServer(self):
			"""starts the server
			@return: always None
			"""
			print 'starting hand history grabber'
			
			self._isRunning = True
			hwnds = []
			def enumWindowsCB(hwnd, lp):
				hwnds.append(hwnd)
				return 1
					
			from ctypes import windll, sizeof, byref, WinError, GetLastError, WINFUNCTYPE, create_unicode_buffer 
			from ctypes.wintypes import INT, HANDLE, LPARAM, DWORD
			user32 = windll.user32
			
			WM_GETTEXT = 13
			SMTO_ABORTIFHUNG = 2
			SMTO_TIMEOUT = 1000
			enumWindowsProc = WINFUNCTYPE(INT, HANDLE, LPARAM)(enumWindowsCB)
			pText = create_unicode_buffer(100)
			pResult = DWORD()
			lastHandHistory = None
				
			while self._isRunning:
			
				# find "instant hand history" dialog
				hwnds = []
				if not user32.EnumWindows(enumWindowsProc, 0): raise WinError(GetLastError())
				for hwnd in hwnds:
					
					# window title and className must match
					n = user32.GetWindowTextLengthW(hwnd)
					if n != len(self.WindowTitle): continue
					if not user32.GetWindowTextW(hwnd, pText, sizeof(pText)): raise WinError(GetLastError())
					if pText.value != self.WindowTitle: continue
					if not user32.GetClassNameW(hwnd, pText, sizeof(pText)): raise WinError(GetLastError())
					if pText.value != self.WindowClassName: continue
						
					# find hand history in dialog
					hwnds = []
					if not user32.EnumChildWindows(hwnd, enumWindowsProc, 0): raise WinError(GetLastError())
					for hwnd in hwnds:
						if not user32.GetClassNameW(hwnd, pText, sizeof(pText)): raise WinError(GetLastError())
						if pText.value != self.WidgetClassName: continue
							
						# grab hand history
						n = user32.GetWindowTextLengthW(hwnd)
						if n:
							p = create_unicode_buffer(n +1)
							user32.SendMessageTimeoutW(hwnd, WM_GETTEXT, sizeof(p), p, SMTO_ABORTIFHUNG, SMTO_TIMEOUT, byref(pResult))
							if p.value != lastHandHistory:
								# parse and dump hand history
								hand = self.handParser.parse(p.value)
								if hand is not None:
									self.handFormatter.dump(hand)
								lastHandHistory = p.value
						break
					break
				time.sleep(self.config.get('HandHistoryGrabber', 'GrabTimeout', '0.4', float))


#*********************************************************************************************************************
def main(config=None):
	if InstantHandHistoryGrabber is None:
		print 'HandHistoryGrabber is not supported on your platform: %s' % sys.platform
		return False
		
	def excepthook(Type, value, tb):
		p = [__release_name__ + '\n', ]
		p += traceback.format_exception(type, value, tb)
		logger.critical(''.join(p))
		raise Type(value)
	sys.excepthook = excepthook
	
	if len(sys.argv) > 1:
		config = Config(filename=sys.argv[1])
	else:
		config = Config()
		config.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'User', 'PokerStarsHandHistoryGrabber.cfg')
	
	handParser = HandHistoryParser(config)
	handFormatter = HandFormatters[config.get('Global', 'HandFormatter', 'HtmlTabular', str)](config)
	grabber = InstantHandHistoryGrabber(config, handParser, handFormatter)
	grabber.startServer()

#*********************************************************************************************************************
if __name__ == '__main__': main()

