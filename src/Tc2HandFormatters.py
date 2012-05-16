
import re
import Tc2Config
import Tc2HandTypes
import Tc2SitePokerStarsHandGrabber

#TEST: hand viewer load html hand

#************************************************************************************
#
#************************************************************************************
#TODO: if small blind open folds markup is slightly messed up
class HandFormatterHtmlTabular(object):
	"""Hand formatter that formats a hand as a tabular html"""
	Name = 'HtmlTabular'
	HandActionsMapping = (	# action, prefix, postfix
			(Tc2HandTypes.PokerHand.Action.TypeCheck, 'c', None),
			(Tc2HandTypes.PokerHand.Action.TypeFold, 'f', None),
			(Tc2HandTypes.PokerHand.Action.TypeBet, 'b', ''),
			(Tc2HandTypes.PokerHand.Action.TypeCall, 'c', ''),
			(Tc2HandTypes.PokerHand.Action.TypeRaise, 'r', ''),
			(Tc2HandTypes.PokerHand.Action.TypePostBlindAnte, '', ''),
			(Tc2HandTypes.PokerHand.Action.TypePostBlindSmall, 'sb', ''),
			(Tc2HandTypes.PokerHand.Action.TypePostBlindBig, 'bb', ''),
			(Tc2HandTypes.PokerHand.Action.TypePostBuyIn, 'bi', ''),
			(Tc2HandTypes.PokerHand.Action.TypePostBringIn, 'br', ''),
			)

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
			margin-left: auto;    /* centers contents of the cell, seems broken now */
			margin-right: auto;    /* centers contents of the cell, seems broken now */
			}
		.boardCards{
			border: 0px;
			border-spacing: 0px;
			margin-left: auto;    /* centers contents of the cell, seems broken now */
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

		'''.replace('\t', '\x20'*4)

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
		self._handActions = dict([(action, [prefix, postfix]) for (action, prefix, postfix) in self.HandActionsMapping])
		self._deckStyle = self.DecKStyleDefault
		self._maxPlayerName = self.MaxPlayerName
		self._styleSheet = self.StyleSheet
		self._noFloatingPoint = False

	#------------------------------------------
	def name(self):
		return self.Name

	def actionPrefix(self, handAction):
		return self._handActions[handAction][0]

	def setActionPrefix(self, handAction, value):
		if self._handActions[handAction][0] is None:
			raise ValueError('unsupported action prefix: %s'  % handAction)
		self._handActions[handAction][0] = value

	def actionPostfix(self, handAction):
		return self._handActions[handAction][1]

	def setActionPostfix(self, handAction, value):
		if self._handActions[handAction][1] is None:
			raise ValueError('unsupported action postfix: %s'  % handAction)
		self._handActions[handAction][1] = value

	def listHandActions(self):
		return [i[0] for i in self.HandActionsMapping]

	def resetHandActions(self):
		self._handActions = dict([(action, [prefix, postfix]) for (action, prefix, postfix) in self.HandActionsMapping])

	def deckStyle(self):
		return self._deckStyle

	def setDeckStyle(self, value):
		if value not in self.DeckStyles:
			raise ValueError('unsupported deck style: %s'  % value)
		self._deckStyle = value

	def deckStyles(self):
		return self.DeckStyles

	def maxPlayerName(self):
		return self._maxPlayerName

	def setMaxPlayerName(self, value):
		self._maxPlayerName = value

	def styleSheet(self):
		return self._styleSheet

	def setStyleSheet(self, value):
		self._styleSheet = value

	def resetStyleSheet(self):
		self._styleSheet = self.StyleSheet

	def noFloatingPoint(self):
		self._noFloatingPoint

	def setNoFloatingPoint(self, flag):
		self._noFloatingPoint = flag

	#------------------------------------------

	def formatNum(self, hand, num):
		if not num:
			result = ''
		elif hand.hasCents:
			if self.noFloatingPoint():
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
				suit, rankKlass, suitKlass = self.HtmlCardSuitMapping[self.deckStyle()]['']
				trRank += '<td class="%s">%s</td>' % (rankKlass, rank)
				trSuit += '<td class=" %s">%s</td>' % (suitKlass, suit)
				trWidth += '<td class="cardWidth"></td>'
			else:
				rank = card[0]
				suit, rankKlass, suitKlass = self.HtmlCardSuitMapping[self.deckStyle()][card[1]]
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
		maxPlayerName = self.maxPlayerName()
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
		p | '<style type="text/css"><!-- %s --></style>' % self.styleSheet()
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
				prefix = self.actionPrefix(action.type)
				p | '<div class="playerActionFold">%s</div>' % (prefix if prefix else '&nbsp;')
			elif action.type == action.TypeCheck:
				prefix = self.actionPrefix(action.type)
				p |  '<div class="playerActionCheck">%s</div>' % (prefix if prefix else '&nbsp;')
			elif action.type == action.TypeBet:
				p | '<div class="playerActionBet">%s%s%s</div>' % (
						self.actionPrefix(action.type),
						self.formatNum(hand, action.amount),
						self.actionPostfix(action.type)
						)
			elif action.type == action.TypeRaise:
				p | '<div class="playerActionRaise">%s%s%s</div>' % (
						self.actionPrefix(action.type),
						self.formatNum(hand, action.amount),
						self.actionPostfix(action.type)
						)
			elif action.type == action.TypeCall:
				p | '<div class="playerActionCall">%s%s%s</div>' % (
						self.actionPrefix(action.type),
						self.formatNum(hand, action.amount),
						self.actionPostfix(action.type)
						)
			elif action.type == action.TypePostBlindBig:
				p | '<div class="playerActionPostBlindBig">%s%s%s</div>' % (
						self.actionPrefix(action.type),
						self.formatNum(hand, action.amount),
						self.actionPostfix(action.type)
						)
			elif action.type == action.TypePostBlindSmall:
				p | '<div class="playerActionPostBlindSmall">%s%s%s</div>' % (
						self.actionPrefix(action.type),
						self.formatNum(hand, action.amount),
						self.actionPostfix(action.type)
						)
			elif action.type == action.TypePostBuyIn:
				p | '<div class="playerActionPostBuyIn">%s%s%s</div>' % (
						self.actionPrefix(action.type),
						self.formatNum(hand, action.amount),
						self.actionPostfix(action.type)
						)
			elif action.type == action.TypePostBringIn:
				p | '<div class="playerActionPostBringIn">%s%s%s</div>' % (
						self.actionPrefix(action.type),
						self.formatNum(hand, action.amount),
						self.actionPostfix(action.type)
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
				self.actionPrefix(Tc2HandTypes.PokerHand.Action.TypePostBlindAnte) +
				self.formatNum(hand, hand.blindAnte) +
				self.actionPostfix(Tc2HandTypes.PokerHand.Action.TypePostBlindAnte)
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
		hand = Tc2HandTypes.PokerHand()
		result = self.PatternHand.search(html)
		if result is not None:
			handHistory = result.group(1)
			parser = Tc2SitePokerStarsHandGrabber.HandParser()
			try:
				hand = parser.parse(handHistory)
			except NoGameHeaderError:
				pass
		return hand
