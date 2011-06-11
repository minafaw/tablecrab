
import unittest
import random
import TexasHoldem
import PokerTools
#************************************************************************************
# unittest for texasholdem.py
#************************************************************************************
class TestPot(unittest.TestCase):
	
	def test_bet(self):
		pot = TexasHoldem.Pot([TexasHoldem.Player('a', 100), TexasHoldem.Player('b', 100)])
		self.assertEqual(sum(pot.bets), 0)
		pot.addBet(pot.player('a'), 50)
		self.assertEqual(pot.player('a').stack, 50)
		self.assertEqual(pot.playerBets(pot.player('a')), 50)
		self.assertEqual(pot.toCall(pot.player('b')), 50)
		pot.addBet(pot.player('b'), 50)
		self.assertEqual(pot.player('b').stack, 50)
		self.assertEqual(pot.toCall(pot.player('b')), 0)
		
	def test_sidepots(self):
		pot = TexasHoldem.Pot([TexasHoldem.Player('a', 50), TexasHoldem.Player('b', 100), TexasHoldem.Player('c', 100)])
		pot.addBet(pot.player('a'), 50)
		pot.addBet(pot.player('b'), 100)
		pot.addBet(pot.player('c'), 100)
		self.assertEqual(len(pot.sidepots), 2)
		self.assertEqual(sum(pot.sidepots[0].bets), 100)
		self.assertEqual(sum(pot.sidepots[1].bets), 150)
		
	def test_unclaimedBet(self):
		pot = TexasHoldem.Pot([TexasHoldem.Player('a', 50), TexasHoldem.Player('b', 150)])
		pot.addBet(pot.player('a'), 50)	# player is all-in
		pot.addBet(pot.player('b'), 100)
		self.assertEqual(len(pot.sidepots), 2)
		#NOTE: case when a player bets and everyone folds is not covered by pot object
			
	def test_playerBetsMoreThanStack(self):
		pot = TexasHoldem.Pot([TexasHoldem.Player('a', 100), TexasHoldem.Player('b', 100)])
		self.assertRaises(ValueError, pot.addBet, pot.player('a'), 500)
		
	def test_fold(self):
		pot = TexasHoldem.Pot([TexasHoldem.Player('a', 100), TexasHoldem.Player('b', 100)])
		self.assertEqual(len(pot.playersActive), 2)
		pot.fold(pot.player('a'))
		self.assertEqual(len(pot.playersActive), 1)
		

class TestHandEval(unittest.TestCase):
	
	@classmethod
	def HAND(klass, *cards):
		return [ PokerTools.Card(card) for card in cards]
		
	def test_straightFlush(self):
		e = TexasHoldem.HandEval()
		
		# test straight flush
		hand = self.HAND('Ah', '2h', '3h',  '4h', '5h', 'Ks', 'Ad')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeStraightFlush)
		self.assertEqual(result.cards[0].name(),  '5h')
		self.assertEqual(result.cards[1].name(),  '4h')
		self.assertEqual(result.cards[2].name(),  '3h')
		self.assertEqual(result.cards[3].name(),  '2h')
		self.assertEqual(result.cards[4].name(),  'Ah')
		
		# test higher straight flush
		hand = self.HAND('6h', '2h', '3h',  '4h', '5h', 'Ks', 'Ad')
		result2 = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeStraightFlush)
		self.assertEqual(result2.cards[0].name(),  '6h')
		self.assertTrue(result2 > result)

	def test_quads(self):
		e = TexasHoldem.HandEval()
		
		# test quads
		hand = self.HAND('Jh', '2h', '3h',  '4h', 'Jc', 'Js', 'Jd')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeQuads)
		quads = [i.name() for i in result.cards]
		self.assertEqual(len([i for i in ('Jh', 'Js', 'Jc', 'Jd') if i in quads]), 4)
		self.assertEqual(result.cards[4].name(),  '4h')
		
		# test higher quads
		hand = self.HAND('2h', 'Kh', '3h',  '4h', 'Kc', 'Ks', 'Kd')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypeQuads)
		self.assertEqual(result2.cards[0].rankName(),  'K')
		self.assertTrue(result < result2)
		
		# test quads with better kicker
		hand = self.HAND('Jh', 'Th', '3h',  '4h', 'Jc', 'Js', 'Jd')
		result3 = e.eval(hand)
		self.assertEqual(result3.handType, e.HandTypeQuads)
		self.assertTrue(result < result3)
		
	def test_fullHouse(self):
		e = TexasHoldem.HandEval()
		
		# test full house
		hand = self.HAND('Jh', 'Kh', '3h',  'Qs', 'Qd', 'Qs', 'Jd')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeFullHouse)
		self.assertEqual(result.cards[0].rankName(),  'Q')
		self.assertEqual(result.cards[1].rankName(),  'Q')
		self.assertEqual(result.cards[2].rankName(),  'Q')
		self.assertEqual(result.cards[3].rankName(),  'J')
		self.assertEqual(result.cards[4].rankName(),  'J')
		
		# test higher full house
		hand = self.HAND('Ah', 'Kh', '3h',  'Qs', 'Qd', 'Qs', 'Ad')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypeFullHouse)
		self.assertTrue(result < result2)
		
	def test_flush(self):
		e = TexasHoldem.HandEval()
		
		# test flush
		hand = self.HAND('Ah', 'Kh', '4h',  '3h', '2h', 'Qs', 'Jd')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeFlush)
		self.assertEqual(result.cards[0].name(),  'Ah')
		self.assertEqual(result.cards[1].name(),  'Kh')
		self.assertEqual(result.cards[2].name(),  '4h')
		self.assertEqual(result.cards[3].name(),  '3h')
		self.assertEqual(result.cards[4].name(),  '2h')
				
		# test higher flush
		hand = self.HAND('Ah', 'Kh', 'Th',  '3h', '2h', 'Qs', 'Jd')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypeFlush)
		self.assertTrue(result < result2)
		
	def test_straight(self):
		e = TexasHoldem.HandEval()
		
		# test straight
		hand = self.HAND('Jh', 'Td', '9s',  '8h', '7h', 'Ks', 'Ad')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeStraight)
		self.assertEqual(result.cards[0].name(),  'Jh')
		self.assertEqual(result.cards[1].name(),  'Td')
		self.assertEqual(result.cards[2].name(),  '9s')
		self.assertEqual(result.cards[3].name(),  '8h')
		self.assertEqual(result.cards[4].name(),  '7h')
		
		# test higher straight
		hand = self.HAND('Jh', 'Td', '9s',  '8h', 'Qh', 'Ks', 'Ad')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypeStraight)
		self.assertTrue(result < result2)
		
	def test_trips(self):
		e = TexasHoldem.HandEval()
		
		# test trips
		hand = self.HAND('Th', 'Td', 'Ts',  '8h', '7h', 'Ks', 'Qd')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeTrips)
		self.assertEqual(result.cards[0].rankName(),  'T')
		self.assertEqual(result.cards[1].rankName(),  'T')
		self.assertEqual(result.cards[2].rankName(),  'T')
		self.assertEqual(result.cards[3].rankName(),  'K')
		self.assertEqual(result.cards[4].rankName(),  'Q')
		
		# test higher trips
		hand = self.HAND('Jh', 'Jd', 'Js',  '8h', '7h', 'Ks', 'Qd')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypeTrips)
		self.assertTrue(result < result2)
		
		# test higher kicker
		hand = self.HAND('Th', 'Td', 'Ts',  '8h', '7h', 'Ks', 'Ad')
		result3 = e.eval(hand)
		self.assertEqual(result3.handType, e.HandTypeTrips)
		self.assertTrue(result < result3)
		
	def test_twoPair(self):
		e = TexasHoldem.HandEval()
		
		# test two pair
		hand = self.HAND('Th', 'Td', '8s',  '8h', '7h', 'Ks', 'Qd')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeTwoPair)
		self.assertEqual(result.cards[0].rankName(),  'T')
		self.assertEqual(result.cards[1].rankName(),  'T')
		self.assertEqual(result.cards[2].rankName(),  '8')
		self.assertEqual(result.cards[3].rankName(),  '8')
		self.assertEqual(result.cards[4].name(),  'Ks')
		
		# test higher two pair
		hand = self.HAND('Th', 'Td', '9s',  '9h', '7h', 'Ks', 'Qd')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypeTwoPair)
		self.assertTrue(result < result2)
		
		# test higher kicker
		hand = self.HAND('Th', 'Td', '8s',  '8h', '7h', 'Ks', 'Ad')
		result3 = e.eval(hand)
		self.assertEqual(result3.handType, e.HandTypeTwoPair)
		self.assertTrue(result < result3)
		
	def test_pair(self):
		e = TexasHoldem.HandEval()
		
		# test pair
		hand = self.HAND('Th', 'Td', '2s',  '8h', '7h', 'Ks', 'Qd')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypePair)
		self.assertEqual(result.cards[0].rankName(),  'T')
		self.assertEqual(result.cards[1].rankName(),  'T')
		self.assertEqual(result.cards[2].name(),  'Ks')
		self.assertEqual(result.cards[3].name(),  'Qd')
		self.assertEqual(result.cards[4].name(),  '8h')
		
		# test higher pair
		hand = self.HAND('Jh', 'Jd', '9s',  '2h', '7h', 'Ks', 'Qd')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypePair)
		self.assertTrue(result < result2)
		
		# test higher kicker
		hand = self.HAND('Th', 'Td', '8s',  '2h', '7h', 'Ks', 'Ad')
		result3 = e.eval(hand)
		self.assertEqual(result3.handType, e.HandTypePair)
		self.assertTrue(result < result3)
		
	def test_highCard(self):
		e = TexasHoldem.HandEval()
		
		# test high cards
		hand = self.HAND('Th', '3d', '2s',  '8h', '7h', 'Ks', 'Qd')
		result = e.eval(hand)
		self.assertEqual(result.handType, e.HandTypeHighCard)
		self.assertEqual(result.cards[0].name(),  'Ks')
		self.assertEqual(result.cards[1].name(),  'Qd')
		self.assertEqual(result.cards[2].name(),  'Th')
		self.assertEqual(result.cards[3].name(),  '8h')
		self.assertEqual(result.cards[4].name(),  '7h')
		
		# test higher high cards
		hand = self.HAND('Jh', '3d', '9s',  '2h', '7h', 'Ks', 'Qd')
		result2 = e.eval(hand)
		self.assertEqual(result2.handType, e.HandTypeHighCard)
		self.assertTrue(result < result2)
		
	def test_handTypes(self):
		e = TexasHoldem.HandEval()
		
		hands = (
				(self.HAND('Ah', '2h', '3h',  '4h', '5h', 'Ks', 'Ad'), TexasHoldem.HandEval.HandTypeStraightFlush),
				(self.HAND('Jh', '2h', '3h',  '4h', 'Jc', 'Js', 'Jd'), TexasHoldem.HandEval.HandTypeQuads),
				(self.HAND('Jh', 'Kh', '3h',  'Qs', 'Qd', 'Qs', 'Jd'), TexasHoldem.HandEval.HandTypeFullHouse),
				(self.HAND('Ah', 'Kh', '4h',  '3h', '2h', 'Qs', 'Jd'), TexasHoldem.HandEval.HandTypeFlush),
				(self.HAND('Jh', 'Td', '9s',  '8h', '7h', 'Ks', 'Ad'), TexasHoldem.HandEval.HandTypeStraight),
				(self.HAND('Th', 'Td', 'Ts',  '8h', '7h', 'Ks', 'Qd'), TexasHoldem.HandEval.HandTypeTrips),
				(self.HAND('Th', 'Td', '8s',  '8h', '7h', 'Ks', 'Qd'), TexasHoldem.HandEval.HandTypeTwoPair),
				(self.HAND('Th', 'Td', '2s',  '8h', '7h', 'Ks', 'Qd'), TexasHoldem.HandEval.HandTypePair),
				(self.HAND('Th', '3d', '2s',  '8h', '7h', 'Ks', 'Qd'), TexasHoldem.HandEval.HandTypeHighCard),
				)
		results = []
		for hand, handType in hands:
			result = e.eval(hand)
			self.assertEqual(handType, result.handType)
			results.append(result)
		random.shuffle(results)
		
		# soert results ascending and comp
		results.sort(reverse=True)
		for i, result in enumerate(results):
			self.assertEqual(result.handType, hands[i][1])
			
		# sort results descending and comp
		results.sort()
		n =0
		for i, result in enumerate(results):
			n -= 1
			self.assertEqual(result.handType, hands[n][1])

#************************************************************************************
#
#************************************************************************************
class MyTestGameEventHandler(object):
		def __init__(self, test, players=None, smallBlind=0.0, bigBlind=0.0, ante=0.0):
			self.test = test
			self.actionNo = 0
			self.done = False
			self.players = [TexasHoldem.Player(name, stack) for (name, stack) in players]
			self.game = TexasHoldem.Game(self.players, smallBlind=smallBlind, bigBlind=bigBlind, ante=ante)
			for player in self.players:
				player.act = self
		
		def __call__(self, game, choices):
			self.actionNo += 1
			return self.handlePlayerAction(game, choices)			
				
		def run(self):
			for event in self.game.run(self.game.EventGameStart(self.game)):
				self.handleGameEvent(event)
				if self.done:
					break
		def handlePlayerAction(self, game, choices):
			raise NotImplementedError()
			
		def handleGameEvent(self, event):
			pass


class TestGame(unittest.TestCase):
	
		
	def test_blindRulesTwoPlayers(self):
		
		# test blind rules for two players
		
		class EventHandler(MyTestGameEventHandler):
			
			def handlePlayerAction(self, game, choices):
											
				# preflop
				
				# player 'a' first to act completes the big blind
				if self.actionNo == 1:
					event = choices[game.EventPlayerCalls]
					self.test.assertEqual(event.player.name, 'a')
					self.test.assertEqual(event.player.seatName, PokerTools.Seats.SeatNameSB)
					return event
				
				# player 'b' checks his bis blind
				elif self.actionNo == 2:
					event = choices[game.EventPlayerChecks]
					self.test.assertEqual(event.player.name, 'b')
					self.test.assertEqual(event.player.seatName, PokerTools.Seats.SeatNameBB)
					return event
				
				# postflop
				
				# player 'b' first to act checks
				elif self.actionNo == 3:
					event = choices[game.EventPlayerChecks]
					self.test.assertEqual(event.player.name, 'b')
					return event
				
				# player 'a' checks behind
				elif self.actionNo == 4:
					event = choices[game.EventPlayerChecks]
					self.test.assertEqual(event.player.name, 'a')
					self.done = True
					return event
				
		# run event handler
		eh = EventHandler(self, players=(
				('a', 10),
				('b', 10),
				),
				smallBlind=2,
				bigBlind=5,
				)
		eh.run()
			
		
	def test_blindRulesThreePlayers(self):
		
		# test blind rules for three players
		
		class EventHandler(MyTestGameEventHandler):
			
			def handlePlayerAction(self, game, choices):
											
				# preflop
				
				# player 'a' first to act limps
				if self.actionNo == 1:
					event = choices[game.EventPlayerCalls]
					self.test.assertEqual(event.player.name, 'a')
					self.test.assertEqual(event.player.seatName, PokerTools.Seats.SeatNameBTN)
					return event
				
				# player 'b' completes the big blind
				elif self.actionNo == 2:
					event = choices[game.EventPlayerCalls]
					self.test.assertEqual(event.player.name, 'b')
					self.test.assertEqual(event.player.seatName, PokerTools.Seats.SeatNameSB)
					return event
				
				elif self.actionNo == 3:
					event = choices[game.EventPlayerChecks]
					self.test.assertEqual(event.player.name, 'c')
					self.test.assertEqual(event.player.seatName, PokerTools.Seats.SeatNameBB)
					return event
							
				# postflop
				
				# player 'b' first to act checks
				elif self.actionNo == 4:
					event = choices[game.EventPlayerChecks]
					self.test.assertEqual(event.player.name, 'b')
					return event
				
				# player 'c' checks
				elif self.actionNo == 5:
					event = choices[game.EventPlayerChecks]
					self.test.assertEqual(event.player.name, 'c')
					return event
					
				# player 'a' checks behind
				elif self.actionNo == 6:
					event = choices[game.EventPlayerChecks]
					self.test.assertEqual(event.player.name, 'a')
					self.done = True
					return event
				
		# run event handler
		eh = EventHandler(self, players=(
				('a', 10),
				('b', 10),
				('c', 10),
				
				),
				smallBlind=2,
				bigBlind=5,
				)
		eh.run()
	
	def test_incompeteBet(self):
		
		# test raise not allowed when incomplete bet reopend the action
		
		class EventHandler(MyTestGameEventHandler):
			
			
			def handlePlayerAction(self, game, choices):
											
				# preflop (no blinds)
				
				# player 'a' bets a chip less than player 'b' stack
				if self.actionNo == 1:
					event = choices[game.EventPlayerBets]
					self.test.assertEqual(event.player.name, 'a')
					event.amount = 8
					return event
				
				# player 'b' raises for his last chip
				elif self.actionNo == 2:
					event = choices[game.EventPlayerRaises]
					self.test.assertEqual(event.player.name, 'b')
					event.amount = 1
					return event
				
				# player 'c' just calls the raise
				elif self.actionNo == 3:
					event = choices[game.EventPlayerCalls]
					self.test.assertEqual(event.player.name, 'c')
					return event
				
				# now player 'a' is not allowed to raise
				elif self.actionNo == 4:
					self.test.assertNotIn(game.EventPlayerRaises, choices)
					self.done = True
					event = choices[game.EventPlayerCalls]
					self.test.assertEqual(event.player.name, 'a')
					return event
			
		# run event handler
		eh = EventHandler(self, players=(
				('a', 10),
				('b', 9),
				('c', 10)
				))
		eh.run()
				
		#
		#
		
		# test raising allowed when incomplete bet did not reopen the action
		class EventHandler(MyTestGameEventHandler):
			
			def handlePlayerAction(self, game, choices):
											
				# preflop (no blinds)
				
				# player 'a' bets a chip less than player 'b' stack
				if self.actionNo == 1:
					event = choices[game.EventPlayerBets]
					event.amount = 9
					return event
				
				# player 'b' raises for his last chip
				elif self.actionNo == 2:
					event = choices[game.EventPlayerRaises]
					event.amount = 1
					return event
				
				# player 'c' reraises
				elif self.actionNo == 3:
					event = choices[game.EventPlayerRaises]
					event.amount = 20
					return event
								
				# now player 'a' is allowed to raise
				elif self.actionNo == 4:
					self.test.assertIn(game.EventPlayerRaises, choices)
					event = choices[game.EventPlayerRaises]
					event.amount = event.amountMax
					self.done = True
					return event
			
				# player 'c' calls
				elif self.actionNo == 5:
					return choices[game.EventPlayerCalls]
				
		# run event handler
		eh = EventHandler(self, players=(
				('a', 100),
				('b', 10),
				('c', 100)
				))
		eh.run()

#************************************************************************************
# run unittests
#************************************************************************************
def suite():
	suite = unittest.TestSuite()
	for name, o in globals().items():
		if name.startswith('Test'):
			suite.addTest(unittest.makeSuite(o))
	return suite

def test():
	runner = unittest.TextTestRunner(verbosity=2)
	runner.run(suite())
		
if __name__ == '__main__': test()	
	
