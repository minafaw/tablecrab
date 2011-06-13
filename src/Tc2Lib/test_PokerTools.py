
import unittest
import itertools
from PokerTools import *
#************************************************************************************
# unittest for PokerTools.py
#************************************************************************************
class TestHandRangeHoldem(unittest.TestCase):
	
	def test_noRange(self):
		h = HandRangeHoldem.fromString('')
		self.assertEqual(h.toString(), '')
		self.assertEqual(len(h.hands), 0)
	
	def test_onePair(self):
		h = HandRangeHoldem.fromString('TT')
		self.assertEqual(h.toString(), 'TT')
		self.assertEqual(len(h.hands), 6)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	def test_pairRange(self):
		h = HandRangeHoldem.fromString('TT-88')
		self.assertEqual(h.toString(), 'TT-88')
		self.assertEqual(len(h.hands), 18)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	def test_pairRangeAndOverpair(self):
		h = HandRangeHoldem.fromString('AA, TT-88')
		self.assertEqual(h.toString(), 'AA, TT-88')
		self.assertEqual(len(h.hands), 24)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	def test_pairRangeAndUnderpair(self):
		h = HandRangeHoldem.fromString('33, TT-88')
		self.assertEqual(h.toString(), 'TT-88, 33')
		self.assertEqual(len(h.hands), 24)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	
	def test_suitedHand(self):
		h = HandRangeHoldem.fromString('JTs')
		self.assertEqual(h.toString(), 'JTs')
		self.assertEqual(len(h.hands), 4)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	def test_suitedHandRange(self):
		h = HandRangeHoldem.fromString('J9s-J7s')
		self.assertEqual(h.toString(), 'J9s-J7s')
		self.assertEqual(len(h.hands), 12)
		#TODO: no idea how to test HandRangeHoldem.hands
		
		# tst alternatives
		h = HandRangeHoldem.fromString('J9s-J7')
		self.assertEqual(h.toString(), 'J9s-J7s')
		
		h = HandRangeHoldem.fromString('J9-J7s')
		self.assertEqual(h.toString(), 'J9s-J7s')
	
	def test_suitedHandRangeAndOverhand(self):
		h = HandRangeHoldem.fromString('KQs, J9s-J7s')
		self.assertEqual(h.toString(), 'KQs, J9s-J7s')
		self.assertEqual(len(h.hands), 16)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	def test_suitedHandRangeAndUnderhand(self):
		h = HandRangeHoldem.fromString('65s, J9s-J7s')
		self.assertEqual(h.toString(), 'J9s-J7s, 65s')
		self.assertEqual(len(h.hands), 16)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	
	def test_offsuitHand(self):
		h = HandRangeHoldem.fromString('JTo')
		self.assertEqual(h.toString(), 'JTo')
		self.assertEqual(len(h.hands), 12)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	def test_offsuitHandRange(self):
		h = HandRangeHoldem.fromString('J9o-J7o')
		self.assertEqual(h.toString(), 'J9o-J7o')
		self.assertEqual(len(h.hands), 36)
		#TODO: no idea how to test HandRangeHoldem.hands
		
		# tst alternatives
		h = HandRangeHoldem.fromString('J9o-J7')
		self.assertEqual(h.toString(), 'J9o-J7o')
		
		h = HandRangeHoldem.fromString('J9-J7o')
		self.assertEqual(h.toString(), 'J9o-J7o')
		
	def test_offsuitHandRangeAndOverhand(self):
		h = HandRangeHoldem.fromString('KQo, J9o-J7o')
		self.assertEqual(h.toString(), 'KQo, J9o-J7o')
		self.assertEqual(len(h.hands), 48)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	def test_offsuitHandRangeAndUnderhand(self):
		h = HandRangeHoldem.fromString('65o, J9o-J7o')
		self.assertEqual(h.toString(), 'J9o-J7o, 65o')
		self.assertEqual(len(h.hands), 48)
		#TODO: no idea how to test HandRangeHoldem.hands
		
		
	def test_nosuitHand(self):
		h = HandRangeHoldem.fromString('JT')
		self.assertEqual(h.toString(), 'JTs, JTo')
		self.assertEqual(len(h.hands), 16)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	def test_nosuitHandRange(self):
		h = HandRangeHoldem.fromString('J9-J7')
		self.assertEqual(h.toString(), 'J9s-J7s, J9o-J7o')
		self.assertEqual(len(h.hands), 48)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	def test_nosuitHandRangeAndOverhand(self):
		h = HandRangeHoldem.fromString('KQ, J9-J7')
		self.assertEqual(h.toString(), 'KQs, J9s-J7s, KQo, J9o-J7o')
		self.assertEqual(len(h.hands), 64)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	def test_nosuitHandRangeAndUnderhand(self):
		h = HandRangeHoldem.fromString('65, J9-J7')
		self.assertEqual(h.toString(), 'J9s-J7s, 65s, J9o-J7o, 65o')
		self.assertEqual(len(h.hands), 64)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	
	def test_singleHand(self):
		h = HandRangeHoldem.fromString('JhTd')
		self.assertEqual(h.toString(), 'JhTd')
		self.assertEqual(len(h.hands), 1)
		#TODO: no idea how to test HandRangeHoldem.hands
		
		
	def test_pairAscending(self):
		h = HandRangeHoldem.fromString('TT+')
		self.assertEqual(h.toString(), 'TT+')
		self.assertEqual(len(h.hands), 30)
		#TODO: no idea how to test HandRangeHoldem.hands
		
	def test_pairAscendingAndUnderrange(self):
		h = HandRangeHoldem.fromString('TT+, 88-77')
		self.assertEqual(h.toString(), 'TT+, 88-77')
		self.assertEqual(len(h.hands), 42)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	def test_suitedAscending(self):
		h = HandRangeHoldem.fromString('J8s+')
		self.assertEqual(h.toString(), 'J8s+')
		self.assertEqual(len(h.hands), 12)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	def test_suitedAscendingAndUnderrange(self):
		h = HandRangeHoldem.fromString('J8s+, J6s-J5s')
		self.assertEqual(h.toString(), 'J8s+, J6s-J5s')
		self.assertEqual(len(h.hands), 20)
		#TODO: no idea how to test HandRangeHoldem.hands	
	
	def test_offsuitAscending(self):
		h = HandRangeHoldem.fromString('J8o+')
		self.assertEqual(h.toString(), 'J8o+')
		self.assertEqual(len(h.hands), 36)
		#TODO: no idea how to test HandRangeHoldem.hands
	
	def test_offsuitAscendingAndUnderrange(self):
		h = HandRangeHoldem.fromString('J8o+, J6o-J5o')
		self.assertEqual(h.toString(), 'J8o+, J6o-J5o')
		self.assertEqual(len(h.hands), 60)
		#TODO: no idea how to test HandRangeHoldem.hands
	
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
