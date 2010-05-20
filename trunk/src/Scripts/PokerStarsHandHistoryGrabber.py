'''PokerStars "instant hand history" grabber

this programm runs a standalone to grab, format and dump to html the hand history currently
displayed in PokerStars "instant hand history". there is no viewer for the file, so an idea is to load 
the dumped file into a browser and set the browser to autorefresh every N seconds.

requires: python >= 2.6
usage: path/to/python PokerStarsHandHistoryGrabber.py

'''

import re, time, sys

#***********************************************************************************************
# user settings (adjust to your needs)
#***********************************************************************************************
PrefixSmallBlind = 'sb'				# prefixes for player actions
PrefixBigBlind = 'bb'
PrefixAnte = 'ante '
PrefixCheck = 'ck'
PrefixBet = 'b'
PrefixFold = 'f'
PrefixCall = 'c'
PrefixRaise = 'r'

MaxPlayerName = 10					# truncate player names to this size (set to 0 to  not truncate at all)
DumpTimeout = 0.4					# check if there is a new hand history every N seconds
NoFloatingPoint = True				# if True, converts stacks and bets on tables with cents to non floating point values
HandFormatter = 'HtmlTabular'	# what hand formatter too use
HandFormatterOutputFile = 'c:\\PokerStarsHandHistory.html'		# where to output the formatted hand history?

# and this is the css for the html file
Css = '''
		.handHistoryBody{margin-left:0px;margin-top:0px;}
		.handHistoryTable{}
		.handHistorySource{margin-top:10em;}
		
		.playerCell{vertical-align:top;}
		.playerName{}
		.playerStack{}
				
		.playerCardsCell{}
		.playerActionsCell{white-space:nowrap;vertical-align:top;padding-left:0.1em;}
		
		.potCell{
				text-align: center;
				}
		.potCellExtra{padding-left:1em;}
		
		.boardCardCell{}
		.boardCardCellExtra{}
		
		.card{
				border:solid 1px;
				background-color:red;
				border-spacing:0px;
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
	
	'''

#***********************************************************************************************
#
#***********************************************************************************************
class Hand(object):
	StreetNone = ''
	StreetBlinds = 'blinds'
	StreetPreflop = 'preflop'
	StreetFlop  = 'flop'
	StreetTurn = 'turn'
	StreetRiver = 'river'
	StreetShowdown = 'showdown'
	StreetSummary = 'summary'
	class Action(object):
		TypeNone = ''
		TypeBet = 'bet'
		TypeCheck = 'check'
		TypeCall = 'call'
		TypeFold= 'fold'
		TypeRaise  = 'raise'
		def __init__(self, player=None, type=TypeNone, amount=0.0):
			self.player = player
			self.type = type
			self.amount = amount
	class Player(object):
		def __init__(self, name='', seatNo=0, stack=0.0, cards=None, blindAnte=0.0, blindSmall=0.0, blindBig=0.0):
			self.name = name
			self.seatNo = seatNo
			self.stack = stack
			self.cards = ['', ''] if cards is None else cards
			self.blindAnte = blindAnte
			self.blindSmall = blindSmall
			self.blindBig = blindBig
	def __init__(self):
		self.handHistory = ''
		self.cards = ['', '', '', '', '']
		self.blindAnte = 0.0
		self.blindSmall = 0.0
		self.blindBig = 0.0
		self.hasCents = True		# flag indicating if cent bets is allowed or not
		self.players = {}
		self.playerButton = ''
		self.seatNoButton = None
		self.tableName = ''
		self.maxPlayers = 0
		self.actions = {
				self.StreetPreflop: [],
				self.StreetFlop: [],
				self.StreetTurn: [],
				self.StreetRiver: [],
				}
	
	def calcPotSizes(self):
		streets = (self.StreetBlinds, self.StreetPreflop, self.StreetFlop, self.StreetTurn, self.StreetRiver)
		result = dict([(street, 0.0) for street in streets])
		players = self.players.items()
		
		bets = dict( [(name, 0.0) for name in self.players])
		for (name, player) in players:
			bets[name] += player.blindSmall + player.blindBig + player.blindAnte
			result[self.StreetBlinds] += player.blindSmall + player.blindBig + player.blindAnte
			
		for street in streets[1:]:
			for (name, player) in players:
				actions = [action for action in self.actions[street] if action.player is player]
				for action in actions:
					amount = action.amount
					if action.type == action.TypeRaise:
						amount -= bets[name]
					bets[name] += amount
					result[street] += amount
			
			bets = dict( [(name, 0.0) for name in self.players] )
			result[street] += result[streets[streets.index(street)-1]]
		return result
	
#********************************************************************************************************
# hand parser
#********************************************************************************************************
class HandHistoryParser(object):
		
	def __init__(self): pass
		
	def stringToFloat(self, string):
		return float(string.replace(',', ''))
		
	def stringToCards(self, string, zfill=None):
		cards = string.split(' ')
		if zfill:
			cards += ['']*zfill
			return cards[:zfill]
		return cards
		
	PatternTableInfo = re.compile('^Table \s \' (?P<tableName>.+?) \' \s (?P<maxPlayers>[0-9]+)\-max \s Seat \s \#(?P<seatNoButton>[0-9]+) \s is \s the \s button', re.X)
	def matchTableInfo(self, hand, streetCurrent, line):
		result = self.PatternTableInfo.match(line)
		if result is not None:
			hand.tableName = result.group('tableName')
			hand.maxPlayers = int(result.group('maxPlayers'))
			hand.seatNoButton = int(result.group('seatNoButton'))
		return result is not None
			
	PatternSeat = re.compile('^Seat \s(?P<seatNo>[1-9]+)\:\s   (?P<player>.*?) \s\(  [\$\EUR]?(?P<stack>.*?)\s.*  \)', re.X)
	def matchSeat(self, hand, streetCurrent, line):
		result= self.PatternSeat.match(line)
		if result is not None:
			player = hand.Player(name=result.group('player'), seatNo=result.group('seatNo'), stack=self.stringToFloat(result.group('stack')))
			hand.players[player.name] = player
			if player.seatNo == hand.seatNoButton:
				hand.playerButton = player.name
		return result is not None
	
	PatternDealtTo = re.compile('Dealt \s to \s (?P<player>.+?) \s \[  (?P<cards>.+?) \]', re.X)
	def matchDealtTo(self, hand, streetCurrent, line):
		result = self.PatternDealtTo.match(line)
		if result is not None:
			hand.players[result.group('player')].cards = self.stringToCards(result.group('cards'))
		return result is not None
	
	PatternAnte =  re.compile('^(?P<player>.*?)\: \s posts \s the \s ante \s [\$\EUR]? (?P<amount>[0-9\.\,]+ )', re.X)
	def matchAnte(self, hand, streetCurrent, line):
		result = self.PatternAnte.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			if amount:
				hand.blindAnte = amount
				hand.players[result.group('player')].blindAnte = amount
		return result is not None
		
	PatternSmallBlind = re.compile('^(?P<player>.*?)\: \s posts \s small \s blind \s [\$\EUR]? (?P<amount>[0-9\.\,]+)', re.X)
	def matchSmallBlind(self, hand, streetCurrent, line):
		result = self.PatternSmallBlind.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			if amount:
				hand.blindSmall = amount
				hand.players[result.group('player')].blindSmall = amount
		return result is not None
	
	PatternBigBlind = re.compile('^(?P<player>.*?)\: \s posts \s big \s blind \s [\$\EUR]? (?P<amount>[0-9\.\,]+ )', re.X)
	def matchBigBlind(self, hand, streetCurrent, line):
		result = self.PatternBigBlind.match(line)
		if result is not None:
			amount = self.stringToFloat(result.group('amount'))
			if amount:
				hand.blindBig = amount
				hand.players[result.group('player')].blindBig = amount
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
			hand.players[result.group('player')].cards = self.stringToCards(result.group('cards'))
		return result is not None
	
	PatternShowedCards = re.compile('^Seat\s[1-9]+\:\s (?P<player>.+?) \s showed \s\[  (?P<cards>.+?) \]', re.X)
	def matchShowedCards(self, hand, streetCurrent, line):
		result = self.PatternShowedCards.match(line)
		if result is not None:
			hand.players[result.group('player')].cards = self.stringToCards(result.group('cards'))
		return result is not None
	
	PatternMuckedCards = re.compile('^Seat\s[1-9]+\:\s (?P<player>.+?) \s mucked \s\[  (?P<cards>.+?) \]', re.X)
	def matchMuckedCards(self, hand, streetCurrent, line):
		result = self.PatternMuckedCards.match(line)
		if result is not None:
			hand.players[result.group('player')].cards = self.stringToCards(result.group('cards'))
		return result is not None
	
	PatternCheck = re.compile('^(?P<player>.+?) \:\s checks', re.X)
	def matchCheck(self, hand, streetCurrent, line):
		result = self.PatternCheck.match(line)
		if result is not None:
			player = hand.players[result.group('player')]
			action = hand.Action(player=player, type=hand.Action.TypeCheck)
			hand.actions[streetCurrent].append(action)
		return result is not None
	
	PatternFold = re.compile('^(?P<player>.+?) \:\s folds', re.X)
	def matchFold(self, hand, streetCurrent, line):
		result = self.PatternFold.match(line)
		if result is not None:
			player = hand.players[result.group('player')]
			action = hand.Action(player=player, type=hand.Action.TypeFold)
			hand.actions[streetCurrent].append(action)
		return result is not None
	
	PatternCall = re.compile('^(?P<player>.+?) \:\s calls \s [\$\EUR]? (?P<amount>[0-9\.\,]+)', re.X)
	def matchCall(self, hand, streetCurrent, line):
		result = self.PatternCall.match(line)
		if result is not None:
			player = hand.players[result.group('player')]
			action = hand.Action(player=player, type=hand.Action.TypeCall, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None
	
	PatternBet = re.compile('^(?P<player>.+?) \:\s bets \s [\$\EUR]? (?P<amount>[0-9\.\,]+)', re.X)
	def matchBet(self, hand, streetCurrent, line):
		result = self.PatternBet.match(line)
		if result is not None:
			player = hand.players[result.group('player')]
			action = hand.Action(player=player, type=hand.Action.TypeBet, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None
	
	PatternRaise = re.compile('^(?P<player>.+?) \:\s raises \s [\$\EUR]? .*?\s to \s [\$\EUR]?  (?P<amount>[0-9\.\,]+)', re.X)
	def matchRaise(self, hand, streetCurrent, line):
		result = self.PatternRaise.match(line)
		if result is not None:
			player = hand.players[result.group('player')]
			action = hand.Action(player=player, type=hand.Action.TypeRaise, amount=self.stringToFloat(result.group('amount')))
			hand.actions[streetCurrent].append(action)
		return result is not None
	
	def parse(self,handHistory):
		
		# create new hand object
		hand = Hand()
		hand.handHistory = handHistory.replace('\r', '')
		streetCurrent = hand.StreetNone
			
		# clean handHistory up a bit to make it easier on us..
		handHistory = handHistory.replace('(small blind) ', '').replace('(big blind) ', '').replace('(button) ', '').replace('(Play Money) ', '')
		
		for line in handHistory.split('\n'):
			line = line.strip()
			if not line: continue
				
			# determine Street we are in
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
			if streetCurrent == hand.StreetNone:
				if self.matchTableInfo(hand, streetCurrent, line): continue
				if self.matchSeat(hand, streetCurrent, line): continue
				if self.matchAnte(hand, streetCurrent,line): continue
				if self.matchSmallBlind(hand, streetCurrent,line): continue
				if self.matchBigBlind(hand, streetCurrent,line): continue
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
	def __new__(klass, name, bases, kws):
		newKlass = type.__new__(klass, name, bases, kws)
		if newKlass.Name is not None:
			HandFormatters[newKlass.Name] = newKlass
		return newKlass
		
class HandFormatterBase(object):
	__metaclass__ = HandFormatterMeta
	Name = None
	

class HandFormatterHtmlTabular(HandFormatterBase):
	"""Hand formatter that formats a hand as a tabular html"""
	Name = 'HtmlTabular'
		
	def __init__(self):
		pass
	
	def formatNum(self, hand, num):
		if not num:
			result = ''
		elif hand.hasCents:
			if NoFloatingPoint:
				result = str(int(num*100))
			else:
				str(num)
		else:
			result = str(int(num))
		return result
			
	def htmlFormatCard(self, card):
		if not card:
			shape = 'A'
			htmlSuit = '&diams;'
			htmlKlass = 'cardBack'
		else:
			shape = card[0]
			htmlSuit, htmlKlass = HtmlCardSuitMapping[card[1]]
		return '''<table class="card">
		<tr>
			<td class="cardShape %s">%s</td>
		</tr>
		<tr>
			<td class="cardSuit %s">%s</td>
		</tr>
		</table>''' % (htmlKlass, shape, htmlKlass, htmlSuit)
		
	def truncateText(self, text, n):
		if n and len(text) > n:
			text = text[:n-2] + '..'
		return text
		
	def dump(self, hand):
		p = '<html><head><style type="text/css">%s</style></head><body class="handHistoryBody"><table class="handHistoryTable" border="1" cellspacing="0" cellpadding="0">'	% Css		
		
		# sort players
		def sortf(a, b):
			return cmp(a[1].seatNo, b[1].seatNo)
		players = hand.players.items()
		players.sort(cmp=sortf)
		
		for name, player in players:
			p += '<tr>'
				
			# add player summary column
			p += '<td class="playerCell">'
			p += '<div class="playerName">%s</div>' % self.truncateText(name, MaxPlayerName)
			p += '<div class="playerStack">%s</div>' % self.formatNum(hand, player.stack)
			p += '</td>'
				
			# add pocket cards column
			p += '<td class="playerCardsCell">%s</td>' % self.htmlFormatCard(player.cards[0])
			p += '<td class="playerCardsCell">%s</td>' % self.htmlFormatCard(player.cards[1])
			
			# add blinds column
			prefix, blind = PrefixBigBlind, player.blindBig
			if not blind:
				prefix, blind = PrefixSmallBlind, player.blindSmall
				if not blind:
					prefix, blind = '&nbsp;', ''
			p += '<td class="playerActionsCell">%s%s</td>' % (prefix, self.formatNum(hand, blind))
				
			# add preflop and postflop actions
			for street in (hand.StreetPreflop, hand.StreetFlop, hand.StreetTurn, hand.StreetRiver):
				actions = [action for action in hand.actions[street] if action.player is player]
				if street == hand.StreetFlop:
					p += '<td class="playerActionsCell" colspan="3">'
				else:
					p += '<td class="playerActionsCell">'
				nActions = None
				for nActions, action in enumerate(actions):
					if action.type == action.TypeFold: 
						p += '<div class="playerActionFold">%s</div>' % PrefixFold
					elif action.type == action.TypeCheck: 
						p +=  '<div class="playerActionCheck">%s</div>' % PrefixCheck
					elif action.type == action.TypeBet:
						p += '<div class="playerActionBet">%s%s</div>' % (PrefixBet, self.formatNum(hand, action.amount) )
					elif action.type == action.TypeRaise:
						p += '<div class="playerActionRaise">%s%s</div>' % (PrefixRaise, self.formatNum(hand, action.amount) )
					elif action.type == action.TypeCall:
						p += '<div class="playerActionCall">%s%s</div>' % (PrefixCall, self.formatNum(hand, action.amount) )
				if nActions is None:
					p += '&nbsp;'
				p += '</td>'		
				
			p += '</tr>'
				
		# add pot size
		p += '<tr>'
		pot = hand.calcPotSizes()
		potCellExtra = PrefixAnte + self.formatNum(hand, hand.blindAnte) if hand.blindAnte else '&nbsp;'
		p += '<td colspan="3" class="potCellExtra">%s</td>' % potCellExtra
		p += '<td class="potCell">%s</td>' % self.formatNum(hand, pot[hand.StreetBlinds])
		p += '<td class="potCell">%s</td>' % self.formatNum(hand, pot[hand.StreetPreflop])
		p += '<td class="potCell" colspan="3">%s</td>' % (self.formatNum(hand, pot[hand.StreetFlop]) if hand.cards[2] else '&nbsp;')
		p += '<td class="potCell">%s</td>' % (self.formatNum(hand, pot[hand.StreetTurn]) if hand.cards[3] else '&nbsp;')
		p += '<td class="potCell">%s</td>' % (self.formatNum(hand, pot[hand.StreetRiver]) if hand.cards[4] else '&nbsp;')
		p += '</tr>'
			
		# add board cards + hand history source
		p += '<tr>'
		p += '<td class="boardCardCellExtra" colspan="5">&nbsp;</td>'
		p += '<td class="boardCardCell">%s</td>' % self.htmlFormatCard(hand.cards[0])
		p += '<td class="boardCardCell">%s</td>' % self.htmlFormatCard(hand.cards[1])
		p += '<td class="boardCardCell">%s</td>' % self.htmlFormatCard(hand.cards[2])
		p += '<td class="boardCardCell">%s</td>' % self.htmlFormatCard(hand.cards[3])
		p += '<td class="boardCardCell">%s</td>' % self.htmlFormatCard(hand.cards[4])
		p += '</tr>'
		
		# dump html to file
		p += '</table><pre class="handHistorySource">%s</pre></body></html>' % hand.handHistory
		with open(HandFormatterOutputFile, 'w') as fp: fp.write(p.encode('utf-8'))


#**********************************************************************************************************
# hand grabber (only available on win32 platforms)
#**********************************************************************************************************
InstantHandHistoryGrabber = None
if sys.platform == 'win32':
	class InstantHandHistoryGrabber(object):
		WindowClassName = '#32770'
		WindowTitle = 'Instant Hand History'
		WidgetClassName = 'PokerStarsViewClass'
		
		def __init__(self, handParser, handFormatter):
			self.handParser = handParser
			self.handFormatter = handFormatter
			
		def runServer(self):
			print 'starting hand history dumper'
			
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
				
			while True:
			
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
								self.handFormatter.dump(hand)
								lastHandHistory = p.value
						break
					break
				time.sleep(DumpTimeout)

#*********************************************************************************************************************
if __name__ == '__main__':
	if InstantHandHistoryGrabber is None:
		print 'HandHistoryGrabber is not supported on your platform: %s' % sys.platform
		sys.exit(1)
		
	grabber = InstantHandHistoryGrabber(HandHistoryParser(), HandFormatters[HandFormatter]())
	grabber.runServer()

