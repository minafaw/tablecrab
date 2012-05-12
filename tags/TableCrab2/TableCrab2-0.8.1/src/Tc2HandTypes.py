"""
"""

from PyQt4 import QtCore

#************************************************************************************
#
#************************************************************************************
class PokerHand(QtCore.QObject):
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
