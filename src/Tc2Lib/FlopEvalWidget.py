""""""

from PyQt4 import QtCore, QtGui
import itertools
import PokerTools
import TexasHoldem
import HandTypesHoldemWidget
import CardSelectorWidget
#************************************************************************************
#
#************************************************************************************
class Flopalyzer(object):
	
	def __init__(self):
				
		#
		#
		
		# total number of flops
		##self.nFlops =  PokerTools.binom(50, 3)
		self.nFlops = 19600
		
		
		# straight flush #
		
		# s: (A) (K) Q J T
		self.pStraightFlushAK = self.nFlops * 1
		self.nStraightFlushAK = 1
		# s: (A) (K) Q J T
		self.pStraightFlushAK = self.nFlops * 1
		self.nStraightFlushAK = 1
		# s: (A) K (Q) J T
		self.pStraightFlushAQ = self.nFlops * 1
		self.nStraightFlushAQ = 1
		# s: (A) K (Q) J T
		self.pStraightFlushAQ = self.nFlops * 1
		self.nStraightFlushAQ = 1
		# s: (A) K Q (J) T
		self.pStraightFlushAJ = self.nFlops * 1
		self.nStraightFlushAJ = 1
		# s: (A) K Q (J) T
		self.pStraightFlushAJ = self.nFlops * 1
		self.nStraightFlushAJ = 1
		# s: (A) K Q J (T)
		self.pStraightFlushAT = self.nFlops * 1
		self.nStraightFlushAT = 1
		# s: (A) K Q J (T)
		self.pStraightFlushAT = self.nFlops * 1
		self.nStraightFlushAT = 1
		#
		self.pStraightFlushA9 = 0.0
		self.nStraightFlushA9 = 0
		#
		self.pStraightFlushA9 = 0.0
		self.nStraightFlushA9 = 0
		#
		self.pStraightFlushA8 = 0.0
		self.nStraightFlushA8 = 0
		#
		self.pStraightFlushA8 = 0.0
		self.nStraightFlushA8 = 0
		#
		self.pStraightFlushA7 = 0.0
		self.nStraightFlushA7 = 0
		#
		self.pStraightFlushA7 = 0.0
		self.nStraightFlushA7 = 0
		#
		self.pStraightFlushA6 = 0.0
		self.nStraightFlushA6 = 0
		#
		self.pStraightFlushA6 = 0.0
		self.nStraightFlushA6 = 0
		# s: (5) 4 3 2 (A)
		self.pStraightFlushA5 = self.nFlops * 1
		self.nStraightFlushA5 = 1
		# s: (5) 4 3 2 (A)
		self.pStraightFlushA5 = self.nFlops * 1
		self.nStraightFlushA5 = 1
		# s: 5 (4) 3 2 (A)
		self.pStraightFlushA4 = self.nFlops * 1
		self.nStraightFlushA4 = 1
		# s: 5 (4) 3 2 (A)
		self.pStraightFlushA4 = self.nFlops * 1
		self.nStraightFlushA4 = 1
		# s: 5 4 (3) 2 (A)
		self.pStraightFlushA3 = self.nFlops * 1
		self.nStraightFlushA3 = 1
		# s: 5 4 (3) 2 (A)
		self.pStraightFlushA3 = self.nFlops * 1
		self.nStraightFlushA3 = 1
		# s: 5 4 3 (2) (A)
		self.pStraightFlushA2 = self.nFlops * 1
		self.nStraightFlushA2 = 1
		# s: 5 4 3 (2) (A)
		self.pStraightFlushA2 = self.nFlops * 1
		self.nStraightFlushA2 = 1
		# s: A (K) (Q) J T
		# s: (K) (Q) J T 9
		self.pStraightFlushKQ = self.nFlops * 2
		self.nStraightFlushKQ = 2
		# s: A (K) (Q) J T
		# s: (K) (Q) J T 9
		self.pStraightFlushKQ = self.nFlops * 2
		self.nStraightFlushKQ = 2
		# s: A (K) Q (J) T
		# s: (K) Q (J) T 9
		self.pStraightFlushKJ = self.nFlops * 2
		self.nStraightFlushKJ = 2
		# s: A (K) Q (J) T
		# s: (K) Q (J) T 9
		self.pStraightFlushKJ = self.nFlops * 2
		self.nStraightFlushKJ = 2
		# s: A (K) Q J (T)
		# s: (K) Q J (T) 9
		self.pStraightFlushKT = self.nFlops * 2
		self.nStraightFlushKT = 2
		# s: A (K) Q J (T)
		# s: (K) Q J (T) 9
		self.pStraightFlushKT = self.nFlops * 2
		self.nStraightFlushKT = 2
		# s: (K) Q J T (9)
		self.pStraightFlushK9 = self.nFlops * 1
		self.nStraightFlushK9 = 1
		# s: (K) Q J T (9)
		self.pStraightFlushK9 = self.nFlops * 1
		self.nStraightFlushK9 = 1
		#
		self.pStraightFlushK8 = 0.0
		self.nStraightFlushK8 = 0
		#
		self.pStraightFlushK8 = 0.0
		self.nStraightFlushK8 = 0
		#
		self.pStraightFlushK7 = 0.0
		self.nStraightFlushK7 = 0
		#
		self.pStraightFlushK7 = 0.0
		self.nStraightFlushK7 = 0
		#
		self.pStraightFlushK6 = 0.0
		self.nStraightFlushK6 = 0
		#
		self.pStraightFlushK6 = 0.0
		self.nStraightFlushK6 = 0
		#
		self.pStraightFlushK5 = 0.0
		self.nStraightFlushK5 = 0
		#
		self.pStraightFlushK5 = 0.0
		self.nStraightFlushK5 = 0
		#
		self.pStraightFlushK4 = 0.0
		self.nStraightFlushK4 = 0
		#
		self.pStraightFlushK4 = 0.0
		self.nStraightFlushK4 = 0
		#
		self.pStraightFlushK3 = 0.0
		self.nStraightFlushK3 = 0
		#
		self.pStraightFlushK3 = 0.0
		self.nStraightFlushK3 = 0
		#
		self.pStraightFlushK2 = 0.0
		self.nStraightFlushK2 = 0
		#
		self.pStraightFlushK2 = 0.0
		self.nStraightFlushK2 = 0
		# s: A K (Q) (J) T
		# s: K (Q) (J) T 9
		# s: (Q) (J) T 9 8
		self.pStraightFlushQJ = self.nFlops * 3
		self.nStraightFlushQJ = 3
		# s: A K (Q) (J) T
		# s: K (Q) (J) T 9
		# s: (Q) (J) T 9 8
		self.pStraightFlushQJ = self.nFlops * 3
		self.nStraightFlushQJ = 3
		# s: A K (Q) J (T)
		# s: K (Q) J (T) 9
		# s: (Q) J (T) 9 8
		self.pStraightFlushQT = self.nFlops * 3
		self.nStraightFlushQT = 3
		# s: A K (Q) J (T)
		# s: K (Q) J (T) 9
		# s: (Q) J (T) 9 8
		self.pStraightFlushQT = self.nFlops * 3
		self.nStraightFlushQT = 3
		# s: K (Q) J T (9)
		# s: (Q) J T (9) 8
		self.pStraightFlushQ9 = self.nFlops * 2
		self.nStraightFlushQ9 = 2
		# s: K (Q) J T (9)
		# s: (Q) J T (9) 8
		self.pStraightFlushQ9 = self.nFlops * 2
		self.nStraightFlushQ9 = 2
		# s: (Q) J T 9 (8)
		self.pStraightFlushQ8 = self.nFlops * 1
		self.nStraightFlushQ8 = 1
		# s: (Q) J T 9 (8)
		self.pStraightFlushQ8 = self.nFlops * 1
		self.nStraightFlushQ8 = 1
		#
		self.pStraightFlushQ7 = 0.0
		self.nStraightFlushQ7 = 0
		#
		self.pStraightFlushQ7 = 0.0
		self.nStraightFlushQ7 = 0
		#
		self.pStraightFlushQ6 = 0.0
		self.nStraightFlushQ6 = 0
		#
		self.pStraightFlushQ6 = 0.0
		self.nStraightFlushQ6 = 0
		#
		self.pStraightFlushQ5 = 0.0
		self.nStraightFlushQ5 = 0
		#
		self.pStraightFlushQ5 = 0.0
		self.nStraightFlushQ5 = 0
		#
		self.pStraightFlushQ4 = 0.0
		self.nStraightFlushQ4 = 0
		#
		self.pStraightFlushQ4 = 0.0
		self.nStraightFlushQ4 = 0
		#
		self.pStraightFlushQ3 = 0.0
		self.nStraightFlushQ3 = 0
		#
		self.pStraightFlushQ3 = 0.0
		self.nStraightFlushQ3 = 0
		#
		self.pStraightFlushQ2 = 0.0
		self.nStraightFlushQ2 = 0
		#
		self.pStraightFlushQ2 = 0.0
		self.nStraightFlushQ2 = 0
		# s: A K Q (J) (T)
		# s: K Q (J) (T) 9
		# s: Q (J) (T) 9 8
		# s: (J) (T) 9 8 7
		self.pStraightFlushJT = self.nFlops * 4
		self.nStraightFlushJT = 4
		# s: A K Q (J) (T)
		# s: K Q (J) (T) 9
		# s: Q (J) (T) 9 8
		# s: (J) (T) 9 8 7
		self.pStraightFlushJT = self.nFlops * 4
		self.nStraightFlushJT = 4
		# s: K Q (J) T (9)
		# s: Q (J) T (9) 8
		# s: (J) T (9) 8 7
		self.pStraightFlushJ9 = self.nFlops * 3
		self.nStraightFlushJ9 = 3
		# s: K Q (J) T (9)
		# s: Q (J) T (9) 8
		# s: (J) T (9) 8 7
		self.pStraightFlushJ9 = self.nFlops * 3
		self.nStraightFlushJ9 = 3
		# s: Q (J) T 9 (8)
		# s: (J) T 9 (8) 7
		self.pStraightFlushJ8 = self.nFlops * 2
		self.nStraightFlushJ8 = 2
		# s: Q (J) T 9 (8)
		# s: (J) T 9 (8) 7
		self.pStraightFlushJ8 = self.nFlops * 2
		self.nStraightFlushJ8 = 2
		# s: (J) T 9 8 (7)
		self.pStraightFlushJ7 = self.nFlops * 1
		self.nStraightFlushJ7 = 1
		# s: (J) T 9 8 (7)
		self.pStraightFlushJ7 = self.nFlops * 1
		self.nStraightFlushJ7 = 1
		#
		self.pStraightFlushJ6 = 0.0
		self.nStraightFlushJ6 = 0
		#
		self.pStraightFlushJ6 = 0.0
		self.nStraightFlushJ6 = 0
		#
		self.pStraightFlushJ5 = 0.0
		self.nStraightFlushJ5 = 0
		#
		self.pStraightFlushJ5 = 0.0
		self.nStraightFlushJ5 = 0
		#
		self.pStraightFlushJ4 = 0.0
		self.nStraightFlushJ4 = 0
		#
		self.pStraightFlushJ4 = 0.0
		self.nStraightFlushJ4 = 0
		#
		self.pStraightFlushJ3 = 0.0
		self.nStraightFlushJ3 = 0
		#
		self.pStraightFlushJ3 = 0.0
		self.nStraightFlushJ3 = 0
		#
		self.pStraightFlushJ2 = 0.0
		self.nStraightFlushJ2 = 0
		#
		self.pStraightFlushJ2 = 0.0
		self.nStraightFlushJ2 = 0
		# s: K Q J (T) (9)
		# s: Q J (T) (9) 8
		# s: J (T) (9) 8 7
		# s: (T) (9) 8 7 6
		self.pStraightFlushT9 = self.nFlops * 4
		self.nStraightFlushT9 = 4
		# s: K Q J (T) (9)
		# s: Q J (T) (9) 8
		# s: J (T) (9) 8 7
		# s: (T) (9) 8 7 6
		self.pStraightFlushT9 = self.nFlops * 4
		self.nStraightFlushT9 = 4
		# s: Q J (T) 9 (8)
		# s: J (T) 9 (8) 7
		# s: (T) 9 (8) 7 6
		self.pStraightFlushT8 = self.nFlops * 3
		self.nStraightFlushT8 = 3
		# s: Q J (T) 9 (8)
		# s: J (T) 9 (8) 7
		# s: (T) 9 (8) 7 6
		self.pStraightFlushT8 = self.nFlops * 3
		self.nStraightFlushT8 = 3
		# s: J (T) 9 8 (7)
		# s: (T) 9 8 (7) 6
		self.pStraightFlushT7 = self.nFlops * 2
		self.nStraightFlushT7 = 2
		# s: J (T) 9 8 (7)
		# s: (T) 9 8 (7) 6
		self.pStraightFlushT7 = self.nFlops * 2
		self.nStraightFlushT7 = 2
		# s: (T) 9 8 7 (6)
		self.pStraightFlushT6 = self.nFlops * 1
		self.nStraightFlushT6 = 1
		# s: (T) 9 8 7 (6)
		self.pStraightFlushT6 = self.nFlops * 1
		self.nStraightFlushT6 = 1
		#
		self.pStraightFlushT5 = 0.0
		self.nStraightFlushT5 = 0
		#
		self.pStraightFlushT5 = 0.0
		self.nStraightFlushT5 = 0
		#
		self.pStraightFlushT4 = 0.0
		self.nStraightFlushT4 = 0
		#
		self.pStraightFlushT4 = 0.0
		self.nStraightFlushT4 = 0
		#
		self.pStraightFlushT3 = 0.0
		self.nStraightFlushT3 = 0
		#
		self.pStraightFlushT3 = 0.0
		self.nStraightFlushT3 = 0
		#
		self.pStraightFlushT2 = 0.0
		self.nStraightFlushT2 = 0
		#
		self.pStraightFlushT2 = 0.0
		self.nStraightFlushT2 = 0
		# s: Q J T (9) (8)
		# s: J T (9) (8) 7
		# s: T (9) (8) 7 6
		# s: (9) (8) 7 6 5
		self.pStraightFlush98 = self.nFlops * 4
		self.nStraightFlush98 = 4
		# s: Q J T (9) (8)
		# s: J T (9) (8) 7
		# s: T (9) (8) 7 6
		# s: (9) (8) 7 6 5
		self.pStraightFlush98 = self.nFlops * 4
		self.nStraightFlush98 = 4
		# s: J T (9) 8 (7)
		# s: T (9) 8 (7) 6
		# s: (9) 8 (7) 6 5
		self.pStraightFlush97 = self.nFlops * 3
		self.nStraightFlush97 = 3
		# s: J T (9) 8 (7)
		# s: T (9) 8 (7) 6
		# s: (9) 8 (7) 6 5
		self.pStraightFlush97 = self.nFlops * 3
		self.nStraightFlush97 = 3
		# s: T (9) 8 7 (6)
		# s: (9) 8 7 (6) 5
		self.pStraightFlush96 = self.nFlops * 2
		self.nStraightFlush96 = 2
		# s: T (9) 8 7 (6)
		# s: (9) 8 7 (6) 5
		self.pStraightFlush96 = self.nFlops * 2
		self.nStraightFlush96 = 2
		# s: (9) 8 7 6 (5)
		self.pStraightFlush95 = self.nFlops * 1
		self.nStraightFlush95 = 1
		# s: (9) 8 7 6 (5)
		self.pStraightFlush95 = self.nFlops * 1
		self.nStraightFlush95 = 1
		#
		self.pStraightFlush94 = 0.0
		self.nStraightFlush94 = 0
		#
		self.pStraightFlush94 = 0.0
		self.nStraightFlush94 = 0
		#
		self.pStraightFlush93 = 0.0
		self.nStraightFlush93 = 0
		#
		self.pStraightFlush93 = 0.0
		self.nStraightFlush93 = 0
		#
		self.pStraightFlush92 = 0.0
		self.nStraightFlush92 = 0
		#
		self.pStraightFlush92 = 0.0
		self.nStraightFlush92 = 0
		# s: J T 9 (8) (7)
		# s: T 9 (8) (7) 6
		# s: 9 (8) (7) 6 5
		# s: (8) (7) 6 5 4
		self.pStraightFlush87 = self.nFlops * 4
		self.nStraightFlush87 = 4
		# s: J T 9 (8) (7)
		# s: T 9 (8) (7) 6
		# s: 9 (8) (7) 6 5
		# s: (8) (7) 6 5 4
		self.pStraightFlush87 = self.nFlops * 4
		self.nStraightFlush87 = 4
		# s: T 9 (8) 7 (6)
		# s: 9 (8) 7 (6) 5
		# s: (8) 7 (6) 5 4
		self.pStraightFlush86 = self.nFlops * 3
		self.nStraightFlush86 = 3
		# s: T 9 (8) 7 (6)
		# s: 9 (8) 7 (6) 5
		# s: (8) 7 (6) 5 4
		self.pStraightFlush86 = self.nFlops * 3
		self.nStraightFlush86 = 3
		# s: 9 (8) 7 6 (5)
		# s: (8) 7 6 (5) 4
		self.pStraightFlush85 = self.nFlops * 2
		self.nStraightFlush85 = 2
		# s: 9 (8) 7 6 (5)
		# s: (8) 7 6 (5) 4
		self.pStraightFlush85 = self.nFlops * 2
		self.nStraightFlush85 = 2
		# s: (8) 7 6 5 (4)
		self.pStraightFlush84 = self.nFlops * 1
		self.nStraightFlush84 = 1
		# s: (8) 7 6 5 (4)
		self.pStraightFlush84 = self.nFlops * 1
		self.nStraightFlush84 = 1
		#
		self.pStraightFlush83 = 0.0
		self.nStraightFlush83 = 0
		#
		self.pStraightFlush83 = 0.0
		self.nStraightFlush83 = 0
		#
		self.pStraightFlush82 = 0.0
		self.nStraightFlush82 = 0
		#
		self.pStraightFlush82 = 0.0
		self.nStraightFlush82 = 0
		# s: T 9 8 (7) (6)
		# s: 9 8 (7) (6) 5
		# s: 8 (7) (6) 5 4
		# s: (7) (6) 5 4 3
		self.pStraightFlush76 = self.nFlops * 4
		self.nStraightFlush76 = 4
		# s: T 9 8 (7) (6)
		# s: 9 8 (7) (6) 5
		# s: 8 (7) (6) 5 4
		# s: (7) (6) 5 4 3
		self.pStraightFlush76 = self.nFlops * 4
		self.nStraightFlush76 = 4
		# s: 9 8 (7) 6 (5)
		# s: 8 (7) 6 (5) 4
		# s: (7) 6 (5) 4 3
		self.pStraightFlush75 = self.nFlops * 3
		self.nStraightFlush75 = 3
		# s: 9 8 (7) 6 (5)
		# s: 8 (7) 6 (5) 4
		# s: (7) 6 (5) 4 3
		self.pStraightFlush75 = self.nFlops * 3
		self.nStraightFlush75 = 3
		# s: 8 (7) 6 5 (4)
		# s: (7) 6 5 (4) 3
		self.pStraightFlush74 = self.nFlops * 2
		self.nStraightFlush74 = 2
		# s: 8 (7) 6 5 (4)
		# s: (7) 6 5 (4) 3
		self.pStraightFlush74 = self.nFlops * 2
		self.nStraightFlush74 = 2
		# s: (7) 6 5 4 (3)
		self.pStraightFlush73 = self.nFlops * 1
		self.nStraightFlush73 = 1
		# s: (7) 6 5 4 (3)
		self.pStraightFlush73 = self.nFlops * 1
		self.nStraightFlush73 = 1
		#
		self.pStraightFlush72 = 0.0
		self.nStraightFlush72 = 0
		#
		self.pStraightFlush72 = 0.0
		self.nStraightFlush72 = 0
		# s: 9 8 7 (6) (5)
		# s: 8 7 (6) (5) 4
		# s: 7 (6) (5) 4 3
		# s: (6) (5) 4 3 2
		self.pStraightFlush65 = self.nFlops * 4
		self.nStraightFlush65 = 4
		# s: 9 8 7 (6) (5)
		# s: 8 7 (6) (5) 4
		# s: 7 (6) (5) 4 3
		# s: (6) (5) 4 3 2
		self.pStraightFlush65 = self.nFlops * 4
		self.nStraightFlush65 = 4
		# s: 8 7 (6) 5 (4)
		# s: 7 (6) 5 (4) 3
		# s: (6) 5 (4) 3 2
		self.pStraightFlush64 = self.nFlops * 3
		self.nStraightFlush64 = 3
		# s: 8 7 (6) 5 (4)
		# s: 7 (6) 5 (4) 3
		# s: (6) 5 (4) 3 2
		self.pStraightFlush64 = self.nFlops * 3
		self.nStraightFlush64 = 3
		# s: 7 (6) 5 4 (3)
		# s: (6) 5 4 (3) 2
		self.pStraightFlush63 = self.nFlops * 2
		self.nStraightFlush63 = 2
		# s: 7 (6) 5 4 (3)
		# s: (6) 5 4 (3) 2
		self.pStraightFlush63 = self.nFlops * 2
		self.nStraightFlush63 = 2
		# s: (6) 5 4 3 (2)
		self.pStraightFlush62 = self.nFlops * 1
		self.nStraightFlush62 = 1
		# s: (6) 5 4 3 (2)
		self.pStraightFlush62 = self.nFlops * 1
		self.nStraightFlush62 = 1
		# s: 8 7 6 (5) (4)
		# s: 7 6 (5) (4) 3
		# s: 6 (5) (4) 3 2
		# s: (5) (4) 3 2 A
		self.pStraightFlush54 = self.nFlops * 4
		self.nStraightFlush54 = 4
		# s: 8 7 6 (5) (4)
		# s: 7 6 (5) (4) 3
		# s: 6 (5) (4) 3 2
		# s: (5) (4) 3 2 A
		self.pStraightFlush54 = self.nFlops * 4
		self.nStraightFlush54 = 4
		# s: 7 6 (5) 4 (3)
		# s: 6 (5) 4 (3) 2
		# s: (5) 4 (3) 2 A
		self.pStraightFlush53 = self.nFlops * 3
		self.nStraightFlush53 = 3
		# s: 7 6 (5) 4 (3)
		# s: 6 (5) 4 (3) 2
		# s: (5) 4 (3) 2 A
		self.pStraightFlush53 = self.nFlops * 3
		self.nStraightFlush53 = 3
		# s: 6 (5) 4 3 (2)
		# s: (5) 4 3 (2) A
		self.pStraightFlush52 = self.nFlops * 2
		self.nStraightFlush52 = 2
		# s: 6 (5) 4 3 (2)
		# s: (5) 4 3 (2) A
		self.pStraightFlush52 = self.nFlops * 2
		self.nStraightFlush52 = 2
		# s: 7 6 5 (4) (3)
		# s: 6 5 (4) (3) 2
		# s: 5 (4) (3) 2 A
		self.pStraightFlush43 = self.nFlops * 3
		self.nStraightFlush43 = 3
		# s: 7 6 5 (4) (3)
		# s: 6 5 (4) (3) 2
		# s: 5 (4) (3) 2 A
		self.pStraightFlush43 = self.nFlops * 3
		self.nStraightFlush43 = 3
		# s: 6 5 (4) 3 (2)
		# s: 5 (4) 3 (2) A
		self.pStraightFlush42 = self.nFlops * 2
		self.nStraightFlush42 = 2
		# s: 6 5 (4) 3 (2)
		# s: 5 (4) 3 (2) A
		self.pStraightFlush42 = self.nFlops * 2
		self.nStraightFlush42 = 2
		# s: 6 5 4 (3) (2)
		# s: 5 4 (3) (2) A
		self.pStraightFlush32 = self.nFlops * 2
		self.nStraightFlush32 = 2
		# s: 6 5 4 (3) (2)
		# s: 5 4 (3) (2) A
		self.pStraightFlush32 = self.nFlops * 2
		self.nStraightFlush32 = 2

				
			
		# quads ##
		
		
		# p flopping quads
		#
		# paired hands
		#
		# 1) one card to make you trips
		# 2) one card that makes you quads
		# 3) random card
		# * 3 ways these cards can flop
		##p = (2.0/50)*(1.0/49)*(48.0/48) * 3
		self.pQuadsPair = 0.00244897959184
		self.nQuadsPair = 48
		#
		# unpairde hands
		#p = (6.0/50)*(2.0/49)*(1.0/48) * 3 * 2
		self.pQuadsUnpaired = 0.000612244897959
		self.nQuadsUnpaired = 12				
				
		
		# full house #
		
				
		# p floping a full house
		#
		# paird hands
		#
		# two ways to flop a full house
		# a) set to our pockets and a pair on the board
		# 1) two cards to make you trips
		# 2) one card that does not make you quads
		# 3) one card that pairs this card
		# * 3 ways these cards can flop
		##p = (2.0/50)*(48.0/49)*(3.0/48) * 3
		self.pFullHouseSetPair = 0.00734693877551
		self.nFullHouseSetPair = 144
		# b) trips on the board
		# 1) one card that does not trip you up
		# 2) one card that pairs it
		# 3) one card that trips the board
		# * 3 ways these cards can flop
		##p = (48.0/50)*(3.0/49)*(2.0/48) * 3
		self.pFullHouseTripsPair = 0.00734693877551
		self.nFullHouseTripsPair = 144
		#
		# unpaired hands
		#
		#p = (6.0/50)*(2.0/49)*(3.0/48) * 3 * 2
		self.pFullHouseSetUnaired = 0.00183673469388
		self.nFullHouseSetUnpaired = 36
		#
		self.pFullHouseTripsUnpired = 0.0
		self.nFullHouseTripsUnpired = 0
		
		
		# flush #
		
		p = (11.0/50)*(10.0/49)*(9.0/48)
		self.pFlush = 0.00841836734694
		self.nFlush = 165
				
		# straight #
		
		
		# probability for a flop of three distinct cards
		#ps = (4.0/50)*(4.0/49)*(4.0/48) * 6
		pThreeCards = 0.00326530612245
				
		# 4 ways to form a straight with JT-65
		#p = 4 * pThreeCards
		self.pStraightJT = 0.0130612244898
		self.nStraightJT = 256
		self.pStraightT9 = self.pStraightJT
		self.nStraightT9 = self.nStraightJT
		self.pStraight98 = self.pStraightJT
		self.nStraight98 = self.nStraightJT
		self.pStraight87 = self.pStraightJT
		self.nStraight87 = self.nStraightJT
		self.pStraight76 = self.pStraightJT
		self.nStraight76 = self.nStraightJT
		self.pStraight65 = self.pStraightJT
		self.nStraight65 = self.nStraightJT
				
		# 3 ways to form a straight with QT-53
		#p = 3 * pThreeCards
		self.pStraightQT = 0.00979591836735
		self.nStraightQT = 192
		self.pStraightT8 = self.pStraightQT
		self.nStraightT8 = self.nStraightQT
		self.pStraight86 = self.pStraightQT
		self.nStraight86 = self.nStraightQT
		self.pStraight64 = self.pStraightQT
		self.nStraight64 = self.nStraightQT
		self.pStraight53 = self.pStraightQT
		self.nStraight53 = self.nStraightQT
		#
		self.pStraightQJ = self.pStraightQT
		self.nStraightQJ = self.nStraightQT
		self.pStraightJ9 = self.pStraightQT
		self.nStraightJ9 = self.nStraightQT
		self.pStraightT8 = self.pStraightQT
		self.nStraightT8 = self.nStraightQT
		self.pStraight97 = self.pStraightQT
		self.nStraight97 = self.nStraightQT
		self.pStraight86 = self.pStraightQT
		self.nStraight86 = self.nStraightQT
		self.pStraight75 = self.pStraightQT
		self.nStraight75 = self.nStraightQT
		self.pStraight63 = self.pStraightQT
		self.nStraight63 = self.nStraightQT
				
		# 2 ways to form a straight with KT-52
		#p = 2 * pThreeCards
		self.pStraightKT = 0.0065306122449
		self.nStraightKT = 128
		self.pStraightQ9 = self.pStraightKT
		self.nStraightQ9 = self.nStraightKT
		self.pStraightJ8 = self.pStraightKT
		self.nStraightJ8 = self.nStraightKT
		self.pStraightT7 = self.pStraightKT
		self.nStraightT7 = self.nStraightKT
		self.pStraight96 = self.pStraightKT
		self.nStraight96 = self.nStraightKT
		self.pStraight85 = self.pStraightKT
		self.nStraight85 = self.nStraightKT
		self.pStraight74 = self.pStraightKT
		self.nStraight74 = self.nStraightKT
		self.pStraight63 = self.pStraightKT
		self.nStraight63 = self.nStraightKT
		self.pStraight52 = self.pStraightKT
		self.nStraight52 = self.nStraightKT
		self.pStraight54 = self.pStraightKT
		#
		self.pStraightKQ = self.pStraightKT
		self.nStraightKQ = self.nStraightKT
		self.pStraightKJ = self.pStraightKT
		self.nStraightKJ = self.nStraightKT
		#
		self.nStraight54 = self.nStraightKT
		self.pStraight43 = self.pStraightKT
		self.nStraight43 = self.nStraightKT
		#
		self.pStraight52 = self.pStraightKT
		self.nStraight52 = self.nStraightKT
		self.pStraight42 = self.pStraightKT
		self.nStraight42 = self.nStraightKT
		#
		self.pStraight32 = self.pStraightKT
		self.nStraight32 = self.nStraightKT
						
		# 1 way to form a straight 
		# p = pThreeCards
		self.pStraightAK = 0.00326530612245
		self.nStraightAK = 64
		self.pStraightAQ = self.pStraightAK
		self.nStraightAQ = self.nStraightAK
		self.pStraightAJ = self.pStraightAK
		self.nStraightAJ = self.nStraightAK
		self.pStraightAT = self.pStraightAK
		self.nStraightAT = self.nStraightAK
		#
		self.pStraightA5 = self.pStraightAK
		self.nStraightA5 = self.nStraightAK
		self.pStraightA4 = self.pStraightAK
		self.nStraightA4 = self.nStraightAK
		self.pStraightA3 = self.pStraightAK
		self.nStraightA3 = self.nStraightAK
		self.pStraightA2 = self.pStraightAK
		self.nStraightA2 = self.nStraightAK
		#
		self.pStraightK9 = self.pStraightAK
		self.nStraightK9 = self.nStraightAK
		self.pStraightQ8 = self.pStraightAK
		self.nStraightQ8 = self.nStraightAK
		self.pStraightJ7 = self.pStraightAK
		self.nStraightJ7 = self.nStraightAK
		self.pStraightT6 = self.pStraightAK
		self.nStraightT6 = self.nStraightAK
		self.pStraight95 = self.pStraightAK
		self.nStraight95 = self.nStraightAK
		self.pStraight84 = self.pStraightAK
		self.nStraight84 = self.nStraightAK
		self.pStraight73 = self.pStraightAK
		self.nStraight73 = self.nStraightAK
		self.pStraight62 = self.pStraightAK
		self.nStraight62 = self.nStraightAK
		
		# no way to form a straight
		self.pStraightAA = 0.0
		self.nStraightAA = 0
		self.pStraightA9 = 0.0
		self.nStraightA9 = 0
		self.pStraightA8 = 0.0
		self.nStraightA8 = 0
		self.pStraightA7 = 0.0
		self.nStraightA7 = 0
		self.pStraightA6 = 0.0
		self.nStraightA6 = 0
		self.pStraightKK = 0.0
		self.nStraightKK = 0
		self.pStraightK8 = 0.0
		self.nStraightK8 = 0
		self.pStraightK7 = 0.0
		self.nStraightK7 = 0
		self.pStraightK6 = 0.0
		self.nStraightK6 = 0
		self.pStraightK5 = 0.0
		self.nStraightK5 = 0
		self.pStraightK4 = 0.0
		self.nStraightK4 = 0
		self.pStraightK3 = 0.0
		self.nStraightK3 = 0
		self.pStraightK2 = 0.0
		self.nStraightK2 = 0
		self.pStraightQQ = 0.0
		self.nStraightQQ = 0
		self.pStraightQ7 = 0.0
		self.nStraightQ7 = 0
		self.pStraightQ6 = 0.0
		self.nStraightQ6 = 0
		self.pStraightQ5 = 0.0
		self.nStraightQ5 = 0
		self.pStraightQ4 = 0.0
		self.nStraightQ4 = 0
		self.pStraightQ3 = 0.0
		self.nStraightQ3 = 0
		self.pStraightQ2 = 0.0
		self.nStraightQ2 = 0
		self.pStraightJJ = 0.0
		self.nStraightJJ = 0
		self.pStraightJ6 = 0.0
		self.nStraightJ6 = 0
		self.pStraightJ5 = 0.0
		self.nStraightJ5 = 0
		self.pStraightJ4 = 0.0
		self.nStraightJ4 = 0
		self.pStraightJ3 = 0.0
		self.nStraightJ3 = 0
		self.pStraightJ2 = 0.0
		self.nStraightJ2 = 0
		self.pStraightTT = 0.0
		self.nStraightTT = 0
		self.pStraightT5 = 0.0
		self.nStraightT5 = 0
		self.pStraightT4 = 0.0
		self.nStraightT4 = 0
		self.pStraightT3 = 0.0
		self.nStraightT3 = 0
		self.pStraightT2 = 0.0
		self.nStraightT2 = 0
		self.pStraight99 = 0.0
		self.nStraight99 = 0
		self.pStraight94 = 0.0
		self.nStraight94 = 0
		self.pStraight93 = 0.0
		self.nStraight93 = 0
		self.pStraight92 = 0.0
		self.nStraight92 = 0
		self.pStraight88 = 0.0
		self.nStraight88 = 0
		self.pStraight83 = 0.0
		self.nStraight83 = 0
		self.pStraight82 = 0.0
		self.nStraight82 = 0
		self.pStraight77 = 0.0
		self.nStraight77 = 0
		self.pStraight72 = 0.0
		self.nStraight72 = 0
		self.pStraight66 = 0.0
		self.nStraight66 = 0
		self.pStraight55 = 0.0
		self.nStraight55 = 0
		self.pStraight44 = 0.0
		self.nStraight44 = 0
		self.pStraight33 = 0.0
		self.nStraight33 = 0
		self.pStraight22 = 0.0
		self.nStraight22 = 0
				
		
		# set #
		
		
		# paired hands
		#
		# flopping a set
		# 1) two cards to make you trips
		# 2) one card that does not quad you up
		# 3) one card that does not quad you up and does not pair the board
		# * 3 ways these cards can flop
		##p = (2.0/50)*(48.0/49)*(44.0/48) * 3
		self.pSetPair = 0.107755102041
		self.nSetPair = 2112
		#
		# unpaired hands
		#
		#p = (6.0/50)*(2.0/49)*(44.0/48)
		self.pSetUnpaired = 0.00448979591837
		self.nSetUnpaired = 88
		
		
		# two pair #
		#
		# 1st card pairing + second card pairing second card + a card that does not
		# boat up the hand * 6 ways for the flop to come
		#p = (3.0/50)*(3.0/49)*(44.0/48) * 6
		self.pTwoPairUnpaired = 0.0202040816327
		self.nTwoPairUnpaired = 396
		#NOTE: we do not count pocket pairs + paired flop a two pair
		self.pTwoPairPair = 0.0
		self.nTwoPairPair = 0
				
		
		# overpair #
		
		#		
		#p = (48.0/50)*(47.0/49)*(46.0/48)
		self.pOverPairAA = 0.882448979592
		self.nOverPairAA = 17296
		#p = (44.0/50)*(43.0/49)*(42.0/48)
		self.pOverPairKK = 0.675714285714
		self.nOverPairKK = 13244
		p = (40.0/50)*(39.0/49)*(38.0/48)
		self.pOverPairQQ = 0.504081632653
		self.nOverPairQQ = 9880
		#p = (36.0/50)*(35.0/49)*(34.0/48)
		self.pOverPairJJ = 0.206666666667
		self.nOverPairJJ = 7140
		#p = (32.0/50)*(31.0/49)*(29.0/48)
		self.pOverPairTT =  0.25306122449
		self.nOverPairTT = 4960
		#p = (28.0/50)*(27.0/49)*(26.0/48)
		self.pOverPair99 = 0.167142857143
		self.nOverPair99 = 3276
		#p = (24.0/50)*(23.0/49)*(22.0/48)
		self.pOverPair88 =  0.103265306122
		self.nOverPair88 = 2024
		#p = (20.0/50)*(19.0/49)*(18.0/48)
		self.pOverPair77 = 0.0581632653061
		self.nOverPair77 = 1140
		#p = (16.0/50)*(15.0/49)*(14.0/48)
		self.pOverPair66 = 0.0285714285714
		self.nOverPair66 = 560
		p = (12.0/50)*(11.0/49)*(10.0/48)
		self.pOverPair55 =0.0112244897959
		self.nOverPair55 = 220
		#p = (8.0/50)*(7.0/49)*(6.0/48)
		self.pOverPair44 = 0.00285714285714
		self.nOverPair44 = 56
		#p = (4.0/50)*(3.0/49)*(2.0/48)
		self.pOverPair33 = 0.000204081632653
		self.nOverPair33 = 4
		#p= 0.0
		self.pOverPair22 = 0.0
		self.nOverPair22 = 0
		
				
		# top pair #
		#
		#p2 = (3.0/50)*(12.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair86 = 0.0489795918367
		self.nTopPair86 = 960.0
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair85 = 0.0428571428571
		self.nTopPair85 = 840.0
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair84 = 0.0367346938776
		self.nTopPair84 = 720.0
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair83 = 0.030612244898
		self.nTopPair83 = 600.0
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair82 = 0.030612244898
		self.nTopPair82 = 600.0
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair76 = 0.0342857142857
		self.nTopPair76 = 672.0
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair75 = 0.029387755102
		self.nTopPair75 = 576.0
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair74 = 0.0244897959184
		self.nTopPair74 = 480.0
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair73 = 0.0195918367347
		self.nTopPair73 = 384.0
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair72 = 0.0195918367347
		self.nTopPair72 = 384.0
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair65 = 0.0183673469388
		self.nTopPair65 = 360.0
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair64 = 0.014693877551
		self.nTopPair64 = 288.0
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair63 = 0.0110204081633
		self.nTopPair63 = 216.0
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair62 = 0.0110204081633
		self.nTopPair62 = 216.0
		#p1 = (3.0/50)*(8.0/49)*(8.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(8.0/48) * 3
		#p = p1 + p2
		self.pTopPair54 = 0.00734693877551
		self.nTopPair54 = 144.0
		#p1 = (3.0/50)*(8.0/49)*(8.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(8.0/48) * 3
		#p = p1 + p2
		self.pTopPair53 = 0.00489795918367
		self.nTopPair53 = 96.0
		#p1 = (3.0/50)*(8.0/49)*(8.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(8.0/48) * 3
		#p = p1 + p2
		self.pTopPair52 = 0.00489795918367
		self.nTopPair52 = 96.0
		#p1 = (3.0/50)*(4.0/49)*(4.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(4.0/48) * 3
		#p = p1 + p2
		self.pTopPair43 = 0.00122448979592
		self.nTopPair43 = 24.0
		#p1 = (3.0/50)*(4.0/49)*(4.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(4.0/48) * 3
		#p = p1 + p2
		self.pTopPair42 = 0.00122448979592
		self.nTopPair42 = 24.0
		#p1 = (3.0/50)*(0.0/49)*(0.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(0.0/48) * 3
		#p = p1 + p2
		self.pTopPair32 = 0.0
		self.nTopPair32 = 0.0


		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(40.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairAK = 0.282857142857
		self.nTopPairAK = 5544
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(36.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairAQ = 0.269387755102
		self.nTopPairAQ = 5280
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(32.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairAJ = 0.255918367347
		self.nTopPairAJ = 5015
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(28.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairAT = 0.242448979592
		self.nTopPairAT = 4752
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(24.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA9 = 0.228979591837
		self.nTopPairA9 = 4488
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(20.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA8 = 0.215510204082
		self.nTopPairA8 = 4224
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(16.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA7 = 0.202040816327
		self.nTopPairA7 = 3959
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA6 = 0.188571428571
		self.nTopPairA6 = 3695
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA5 = 0.175102040816
		self.nTopPairA5 = 3432
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA4 = 0.161632653061
		self.nTopPairA4 = 3168
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA3 = 0.148163265306
		self.nTopPairA3 = 2904
		#p1 = (3.0/50)*(44.0/49)*(44.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(44.0/48) * 3
		#p = p1 + p2
		self.pTopPairA2 = 0.148163265306
		self.nTopPairA2 = 2904
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(36.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairKQ = 0.232653061224
		self.nTopPairKQ = 4560
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(32.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairKJ = 0.220408163265
		self.nTopPairKJ = 4320
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(28.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairKT = 0.208163265306
		self.nTopPairKT = 4080
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(24.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK9 = 0.195918367347
		self.nTopPairK9 = 3840
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(20.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK8 = 0.183673469388
		self.nTopPairK8 = 3599
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(16.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK7 = 0.171428571429
		self.nTopPairK7 = 3360
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK6 = 0.159183673469
		self.nTopPairK6 = 3120
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK5 = 0.14693877551
		self.nTopPairK5 = 2879
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK4 = 0.134693877551
		self.nTopPairK4 = 2640
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK3 = 0.122448979592
		self.nTopPairK3 = 2400
		#p1 = (3.0/50)*(40.0/49)*(40.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(40.0/48) * 3
		#p = p1 + p2
		self.pTopPairK2 = 0.122448979592
		self.nTopPairK2 = 2400
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(32.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQJ = 0.187346938776
		self.nTopPairQJ = 3672
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(28.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQT = 0.176326530612
		self.nTopPairQT = 3455
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(24.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ9 = 0.165306122449
		self.nTopPairQ9 = 3239
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(20.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ8 = 0.154285714286
		self.nTopPairQ8 = 3024
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(16.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ7 = 0.143265306122
		self.nTopPairQ7 = 2808
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ6 = 0.132244897959
		self.nTopPairQ6 = 2592
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ5 = 0.121224489796
		self.nTopPairQ5 = 2376
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ4 = 0.110204081633
		self.nTopPairQ4 = 2160
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ3 = 0.0991836734694
		self.nTopPairQ3 = 1944
		#p1 = (3.0/50)*(36.0/49)*(36.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(36.0/48) * 3
		#p = p1 + p2
		self.pTopPairQ2 = 0.0991836734694
		self.nTopPairQ2 = 1944
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(28.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJT = 0.14693877551
		self.nTopPairJT = 2879
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(24.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ9 = 0.137142857143
		self.nTopPairJ9 = 2687
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(20.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ8 = 0.127346938776
		self.nTopPairJ8 = 2495
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(16.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ7 = 0.117551020408
		self.nTopPairJ7 = 2304
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ6 = 0.107755102041
		self.nTopPairJ6 = 2111
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ5 = 0.0979591836735
		self.nTopPairJ5 = 1920
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ4 = 0.0881632653061
		self.nTopPairJ4 = 1728
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ3 = 0.0783673469388
		self.nTopPairJ3 = 1536
		#p1 = (3.0/50)*(32.0/49)*(32.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(32.0/48) * 3
		#p = p1 + p2
		self.pTopPairJ2 = 0.0783673469388
		self.nTopPairJ2 = 1536
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(24.0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT9 = 0.111428571429
		self.nTopPairT9 = 2184
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(20.0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT8 = 0.102857142857
		self.nTopPairT8 = 2015
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(16.0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT7 = 0.0942857142857
		self.nTopPairT7 = 1847
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT6 = 0.0857142857143
		self.nTopPairT6 = 1680
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT5 = 0.0771428571429
		self.nTopPairT5 = 1512
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT4 = 0.0685714285714
		self.nTopPairT4 = 1343
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT3 = 0.06
		self.nTopPairT3 = 1175
		#p1 = (3.0/50)*(28.0/49)*(28.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(28.0/48) * 3
		#p = p1 + p2
		self.pTopPairT2 = 0.06
		self.nTopPairT2 = 1175
		#p1 = (3.0/50)*(24.0/49)*(24.0/48) * 3
		#p2 = (3.0/50)*(20.0/49)*(24.0/48) * 3
		#p = p1 + p2
		self.pTopPair98 = 0.0808163265306
		self.nTopPair98 = 1584
		#p1 = (3.0/50)*(24.0/49)*(24.0/48) * 3
		#p2 = (3.0/50)*(16.0/49)*(24.0/48) * 3
		#p = p1 + p2
		self.pTopPair97 = 0.0734693877551
		self.nTopPair97 = 1439
		#p1 = (3.0/50)*(24.0/49)*(24.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(24.0/48) * 3
		#p = p1 + p2
		self.pTopPair96 = 0.0661224489796
		self.nTopPair96 = 1296
		#p1 = (3.0/50)*(24.0/49)*(24.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(24.0/48) * 3
		#p = p1 + p2
		self.pTopPair95 = 0.0587755102041
		self.nTopPair95 = 1152
		#p1 = (3.0/50)*(24.0/49)*(24.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(24.0/48) * 3
		#p = p1 + p2
		self.pTopPair94 = 0.0514285714286
		self.nTopPair94 = 1008
		#p1 = (3.0/50)*(24.0/49)*(24.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(24.0/48) * 3
		#p = p1 + p2
		self.pTopPair93 = 0.0440816326531
		self.nTopPair93 = 864
		#p1 = (3.0/50)*(24.0/49)*(24.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(24.0/48) * 3
		#p = p1 + p2
		self.pTopPair92 = 0.0440816326531
		self.nTopPair92 = 864
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(16.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair87 = 0.0551020408163
		self.nTopPair87 = 1080
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair86 = 0.0489795918367
		self.nTopPair86 = 960
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair85 = 0.0428571428571
		self.nTopPair85 = 840
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair84 = 0.0367346938776
		self.nTopPair84 = 719
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair83 = 0.030612244898
		self.nTopPair83 = 600
		#p1 = (3.0/50)*(20.0/49)*(20.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(20.0/48) * 3
		#p = p1 + p2
		self.pTopPair82 = 0.030612244898
		self.nTopPair82 = 600
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(12.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair76 = 0.0342857142857
		self.nTopPair76 = 671
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair75 = 0.029387755102
		self.nTopPair75 = 576
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair74 = 0.0244897959184
		self.nTopPair74 = 480
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair73 = 0.0195918367347
		self.nTopPair73 = 384
		#p1 = (3.0/50)*(16.0/49)*(16.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(16.0/48) * 3
		#p = p1 + p2
		self.pTopPair72 = 0.0195918367347
		self.nTopPair72 = 384
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(8.0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair65 = 0.0183673469388
		self.nTopPair65 = 359
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair64 = 0.014693877551
		self.nTopPair64 = 288
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair63 = 0.0110204081633
		self.nTopPair63 = 216
		#p1 = (3.0/50)*(12.0/49)*(12.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(12.0/48) * 3
		#p = p1 + p2
		self.pTopPair62 = 0.0110204081633
		self.nTopPair62 = 216
		#p1 = (3.0/50)*(8.0/49)*(8.0/48) * 3
		#p2 = (3.0/50)*(4.0/49)*(8.0/48) * 3
		#p = p1 + p2
		self.pTopPair54 = 0.00734693877551
		self.nTopPair54 = 144
		#p1 = (3.0/50)*(8.0/49)*(8.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(8.0/48) * 3
		#p = p1 + p2
		self.pTopPair53 = 0.00489795918367
		self.nTopPair53 = 96
		#p1 = (3.0/50)*(8.0/49)*(8.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(8.0/48) * 3
		#p = p1 + p2
		self.pTopPair52 = 0.00489795918367
		self.nTopPair52 = 96
		#p1 = (3.0/50)*(4.0/49)*(4.0/48) * 3
		#p2 = (3.0/50)*(0.0/49)*(4.0/48) * 3
		#p = p1 + p2
		self.pTopPair43 = 0.00122448979592
		self.nTopPair43 = 24
		#p1 = (3.0/50)*(4.0/49)*(4.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(4.0/48) * 3
		#p = p1 + p2
		self.pTopPair42 = 0.00122448979592
		self.nTopPair42 = 24
		#p1 = (3.0/50)*(0.0/49)*(0.0/48) * 3
		#p2 = (3.0/50)*(0/49)*(0.0/48) * 3
		#p = p1 + p2
		self.pTopPair32 = 0.0
		self.nTopPair32 = 0

				
		# pair #

		
		#NOTE: pairs include TopPairs and OverPairs
		
		
		# two ways of hitting a pair on the flop
		# 1) hitting a pair and the board not pairing
		# 2) hitting a pair and the board pairing
		#p1 = (6.0/50)*(44.0/49)*(40.0/48) * 3
		#p2 = (6.0/50)*(44.0/49)*(3.0/48) * 3
		#p = p1 + p2
		self.pPairUnpaired = 0.289591836735
		self.nPairUnpaired = 5676
		#
		#p = 1- (self.pQuadsPair + self.pFullHouseSetPair + self.pSetPair)
		self.pPairPair = 0.882448979592
		self.nPairPair = 17296
		
		
		# flush draw #
		
		# holding two unsuited cards		
		#p = (24.0/50)*(11.0/49)*(10.0/48)
		self.pFlushDrawOffsuit = 0.0224489795918
		self.nFlushDrawOffsuit = 440
		
		# holding two suited cards
		#p = (11.0/50)*(10.0/49)*(39.0/48) * 3
		self.pFlushDrawSuited = 0.10943877551
		self.nFlushDrawSuited = 2145
		#
		# holding a pair
		self.pFlushDrawPair = self.pFlushDrawOffsuit
		self.nFlushDrawPair = self.nFlushDrawOffsuit
		
		
			
		
		# straight daw #
		# inside straight draw #
		
		#print pThreeCards
		
		# straight draws are calculated by No of flops that make a draw * pDraw
		pDraw = (4.0/50)*(4.0/49)*(40.0/48) * 6
		
		# inside straight draws are calculated by No of flops that make a draw * pThreeCards
		# straight draws for pairs are calculated like inside straight draws
		
		#
		self.pOutsideStraightDrawAA = 0.0
		self.nOutsideStraightDrawAA = 0
		self.pInsideStraightDrawAA = 0.0
		self.nInsideStraightDrawAA = 0
		#
		self.pOutsideStraightDrawAK = 0.0
		self.nOutsideStraightDrawAK = 0
		self.pInsideStraightDrawAK = 0.0
		self.nInsideStraightDrawAK = 0
		# b: (A) _ (Q) J T _ 8
		self.pOutsideStraightDrawAQ = 0.0
		self.nOutsideStraightDrawAQ = 0
		self.pInsideStraightDrawAQ = pThreeCards * 1
		self.nInsideStraightDrawAQ = 64
		# b: (A) _ Q (J) T _ 8
		self.pOutsideStraightDrawAJ = 0.0
		self.nOutsideStraightDrawAJ = 0
		self.pInsideStraightDrawAJ = pThreeCards * 1
		self.nInsideStraightDrawAJ = 64
		# b: (A) _ Q J (T) _ 8
		self.pOutsideStraightDrawAT = 0.0
		self.nOutsideStraightDrawAT = 0
		self.pInsideStraightDrawAT = pThreeCards * 1
		self.nInsideStraightDrawAT = 64
		#
		self.pOutsideStraightDrawA9 = 0.0
		self.nOutsideStraightDrawA9 = 0
		self.pInsideStraightDrawA9 = 0.0
		self.nInsideStraightDrawA9 = 0
		# b: (A) _ Q J T _ (8)
		self.pOutsideStraightDrawA8 = 0.0
		self.nOutsideStraightDrawA8 = 0
		self.pInsideStraightDrawA8 = pThreeCards * 1
		self.nInsideStraightDrawA8 = 64
		# b: (7) _ 5 4 3 _ (A)
		self.pOutsideStraightDrawA7 = 0.0
		self.nOutsideStraightDrawA7 = 0
		self.pInsideStraightDrawA7 = pThreeCards * 1
		self.nInsideStraightDrawA7 = 64
		#
		self.pOutsideStraightDrawA6 = 0.0
		self.nOutsideStraightDrawA6 = 0
		self.pInsideStraightDrawA6 = 0.0
		self.nInsideStraightDrawA6 = 0
		# b: 7 _ (5) 4 3 _ (A)
		self.pOutsideStraightDrawA5 = 0.0
		self.nOutsideStraightDrawA5 = 0
		self.pInsideStraightDrawA5 = pThreeCards * 1
		self.nInsideStraightDrawA5 = 64
		# b: 7 _ 5 (4) 3 _ (A)
		self.pOutsideStraightDrawA4 = 0.0
		self.nOutsideStraightDrawA4 = 0
		self.pInsideStraightDrawA4 = pThreeCards * 1
		self.nInsideStraightDrawA4 = 64
		# b: 7 _ 5 4 (3) _ (A)
		self.pOutsideStraightDrawA3 = 0.0
		self.nOutsideStraightDrawA3 = 0
		self.pInsideStraightDrawA3 = pThreeCards * 1
		self.nInsideStraightDrawA3 = 64
		#
		self.pOutsideStraightDrawA2 = 0.0
		self.nOutsideStraightDrawA2 = 0
		self.pInsideStraightDrawA2 = 0.0
		self.nInsideStraightDrawA2 = 0
		# s: _ (K) Q J T _
		self.pOutsideStraightDrawKK = pThreeCards * 1
		self.nOutsideStraightDrawKK = 64
		self.pInsideStraightDrawKK = 0.0
		self.nInsideStraightDrawKK = 0
		# s: _ (K) (Q) J T _
		self.pOutsideStraightDrawKQ = pDraw * 1
		self.nOutsideStraightDrawKQ = 640
		self.pInsideStraightDrawKQ = 0.0
		self.nInsideStraightDrawKQ = 0
		# s: _ (K) Q (J) T _
		# b: (K) _ (J) T 9 _ 7
		self.pOutsideStraightDrawKJ = pDraw * 1
		self.nOutsideStraightDrawKJ = 640
		self.pInsideStraightDrawKJ = pThreeCards * 1
		self.nInsideStraightDrawKJ = 64
		# s: _ (K) Q J (T) _
		# b: (K) _ J (T) 9 _ 7
		self.pOutsideStraightDrawKT = pDraw * 1
		self.nOutsideStraightDrawKT = 640
		self.pInsideStraightDrawKT = pThreeCards * 1
		self.nInsideStraightDrawKT = 64
		# b: (K) _ J T (9) _ 7
		self.pOutsideStraightDrawK9 = 0.0
		self.nOutsideStraightDrawK9 = 0
		self.pInsideStraightDrawK9 = pThreeCards * 1
		self.nInsideStraightDrawK9 = 64
		#
		self.pOutsideStraightDrawK8 = 0.0
		self.nOutsideStraightDrawK8 = 0
		self.pInsideStraightDrawK8 = 0.0
		self.nInsideStraightDrawK8 = 0
		# b: (K) _ J T 9 _ (7)
		self.pOutsideStraightDrawK7 = 0.0
		self.nOutsideStraightDrawK7 = 0
		self.pInsideStraightDrawK7 = pThreeCards * 1
		self.nInsideStraightDrawK7 = 64
		#
		self.pOutsideStraightDrawK6 = 0.0
		self.nOutsideStraightDrawK6 = 0
		self.pInsideStraightDrawK6 = 0.0
		self.nInsideStraightDrawK6 = 0
		#
		self.pOutsideStraightDrawK5 = 0.0
		self.nOutsideStraightDrawK5 = 0
		self.pInsideStraightDrawK5 = 0.0
		self.nInsideStraightDrawK5 = 0
		#
		self.pOutsideStraightDrawK4 = 0.0
		self.nOutsideStraightDrawK4 = 0
		self.pInsideStraightDrawK4 = 0.0
		self.nInsideStraightDrawK4 = 0
		#
		self.pOutsideStraightDrawK3 = 0.0
		self.nOutsideStraightDrawK3 = 0
		self.pInsideStraightDrawK3 = 0.0
		self.nInsideStraightDrawK3 = 0
		#
		self.pOutsideStraightDrawK2 = 0.0
		self.nOutsideStraightDrawK2 = 0
		self.pInsideStraightDrawK2 = 0.0
		self.nInsideStraightDrawK2 = 0
		# s: _ K (Q) J T _
		# s: _ (Q) J T 9 _
		self.pOutsideStraightDrawQQ = pThreeCards * 2
		self.nOutsideStraightDrawQQ = 128
		self.pInsideStraightDrawQQ = 0.0
		self.nInsideStraightDrawQQ = 0
		# s: _ K (Q) (J) T _
		# s: _ (Q) (J) T 9 _
		# b: A _ (Q) (J) T _ 8
		self.pOutsideStraightDrawQJ = pDraw * 2
		self.nOutsideStraightDrawQJ = 1280
		self.pInsideStraightDrawQJ = pThreeCards * 1
		self.nInsideStraightDrawQJ = 64
		# s: _ K (Q) J (T) _
		# s: _ (Q) J (T) 9 _
		# b: A _ (Q) J (T) _ 8
		# b: (Q) _ (T) 9 8 _ 6
		self.pOutsideStraightDrawQT = pDraw * 2
		self.nOutsideStraightDrawQT = 1280
		self.pInsideStraightDrawQT = pThreeCards * 2
		self.nInsideStraightDrawQT = 128
		# s: _ (Q) J T (9) _
		# b: (Q) _ T (9) 8 _ 6
		self.pOutsideStraightDrawQ9 = pDraw * 1
		self.nOutsideStraightDrawQ9 = 640
		self.pInsideStraightDrawQ9 = pThreeCards * 1
		self.nInsideStraightDrawQ9 = 64
		# b: A _ (Q) J T _ (8)
		# b: (Q) _ T 9 (8) _ 6
		self.pOutsideStraightDrawQ8 = 0.0
		self.nOutsideStraightDrawQ8 = 0
		self.pInsideStraightDrawQ8 = pThreeCards * 2
		self.nInsideStraightDrawQ8 = 128
		#
		self.pOutsideStraightDrawQ7 = 0.0
		self.nOutsideStraightDrawQ7 = 0
		self.pInsideStraightDrawQ7 = 0.0
		self.nInsideStraightDrawQ7 = 0
		# b: (Q) _ T 9 8 _ (6)
		self.pOutsideStraightDrawQ6 = 0.0
		self.nOutsideStraightDrawQ6 = 0
		self.pInsideStraightDrawQ6 = pThreeCards * 1
		self.nInsideStraightDrawQ6 = 64
		#
		self.pOutsideStraightDrawQ5 = 0.0
		self.nOutsideStraightDrawQ5 = 0
		self.pInsideStraightDrawQ5 = 0.0
		self.nInsideStraightDrawQ5 = 0
		#
		self.pOutsideStraightDrawQ4 = 0.0
		self.nOutsideStraightDrawQ4 = 0
		self.pInsideStraightDrawQ4 = 0.0
		self.nInsideStraightDrawQ4 = 0
		#
		self.pOutsideStraightDrawQ3 = 0.0
		self.nOutsideStraightDrawQ3 = 0
		self.pInsideStraightDrawQ3 = 0.0
		self.nInsideStraightDrawQ3 = 0
		#
		self.pOutsideStraightDrawQ2 = 0.0
		self.nOutsideStraightDrawQ2 = 0
		self.pInsideStraightDrawQ2 = 0.0
		self.nInsideStraightDrawQ2 = 0
		# s: _ K Q (J) T _
		# s: _ Q (J) T 9 _
		# s: _ (J) T 9 8 _
		self.pOutsideStraightDrawJJ = pThreeCards * 3
		self.nOutsideStraightDrawJJ = 192
		self.pInsideStraightDrawJJ = 0.0
		self.nInsideStraightDrawJJ = 0
		# s: _ K Q (J) (T) _
		# s: _ Q (J) (T) 9 _
		# s: _ (J) (T) 9 8 _
		# b: A _ Q (J) (T) _ 8
		# b: K _ (J) (T) 9 _ 7
		self.pOutsideStraightDrawJT = pDraw * 3
		self.nOutsideStraightDrawJT = 1920
		self.pInsideStraightDrawJT = pThreeCards * 2
		self.nInsideStraightDrawJT = 128
		# s: _ Q (J) T (9) _
		# s: _ (J) T (9) 8 _
		# b: K _ (J) T (9) _ 7
		# b: (J) _ (9) 8 7 _ 5
		self.pOutsideStraightDrawJ9 = pDraw * 2
		self.nOutsideStraightDrawJ9 = 1280
		self.pInsideStraightDrawJ9 = pThreeCards * 2
		self.nInsideStraightDrawJ9 = 128
		# s: _ (J) T 9 (8) _
		# b: A _ Q (J) T _ (8)
		# b: (J) _ 9 (8) 7 _ 5
		self.pOutsideStraightDrawJ8 = pDraw * 1
		self.nOutsideStraightDrawJ8 = 640
		self.pInsideStraightDrawJ8 = pThreeCards * 2
		self.nInsideStraightDrawJ8 = 128
		# b: K _ (J) T 9 _ (7)
		# b: (J) _ 9 8 (7) _ 5
		self.pOutsideStraightDrawJ7 = 0.0
		self.nOutsideStraightDrawJ7 = 0
		self.pInsideStraightDrawJ7 = pThreeCards * 2
		self.nInsideStraightDrawJ7 = 128
		#
		self.pOutsideStraightDrawJ6 = 0.0
		self.nOutsideStraightDrawJ6 = 0
		self.pInsideStraightDrawJ6 = 0.0
		self.nInsideStraightDrawJ6 = 0
		# b: (J) _ 9 8 7 _ (5)
		self.pOutsideStraightDrawJ5 = 0.0
		self.nOutsideStraightDrawJ5 = 0
		self.pInsideStraightDrawJ5 = pThreeCards * 1
		self.nInsideStraightDrawJ5 = 64
		#
		self.pOutsideStraightDrawJ4 = 0.0
		self.nOutsideStraightDrawJ4 = 0
		self.pInsideStraightDrawJ4 = 0.0
		self.nInsideStraightDrawJ4 = 0
		#
		self.pOutsideStraightDrawJ3 = 0.0
		self.nOutsideStraightDrawJ3 = 0
		self.pInsideStraightDrawJ3 = 0.0
		self.nInsideStraightDrawJ3 = 0
		#
		self.pOutsideStraightDrawJ2 = 0.0
		self.nOutsideStraightDrawJ2 = 0
		self.pInsideStraightDrawJ2 = 0.0
		self.nInsideStraightDrawJ2 = 0
		# s: _ K Q J (T) _
		# s: _ Q J (T) 9 _
		# s: _ J (T) 9 8 _
		# s: _ (T) 9 8 7 _
		self.pOutsideStraightDrawTT = pThreeCards * 4
		self.nOutsideStraightDrawTT = 256
		self.pInsideStraightDrawTT = 0.0
		self.nInsideStraightDrawTT = 0
		# s: _ Q J (T) (9) _
		# s: _ J (T) (9) 8 _
		# s: _ (T) (9) 8 7 _
		# b: K _ J (T) (9) _ 7
		# b: Q _ (T) (9) 8 _ 6
		self.pOutsideStraightDrawT9 = pDraw * 3
		self.nOutsideStraightDrawT9 = 1920
		self.pInsideStraightDrawT9 = pThreeCards * 2
		self.nInsideStraightDrawT9 = 128
		# s: _ J (T) 9 (8) _
		# s: _ (T) 9 (8) 7 _
		# b: A _ Q J (T) _ (8)
		# b: Q _ (T) 9 (8) _ 6
		# b: (T) _ (8) 7 6 _ 4
		self.pOutsideStraightDrawT8 = pDraw * 2
		self.nOutsideStraightDrawT8 = 1280
		self.pInsideStraightDrawT8 = pThreeCards * 3
		self.nInsideStraightDrawT8 = 192
		# s: _ (T) 9 8 (7) _
		# b: K _ J (T) 9 _ (7)
		# b: (T) _ 8 (7) 6 _ 4
		self.pOutsideStraightDrawT7 = pDraw * 1
		self.nOutsideStraightDrawT7 = 640
		self.pInsideStraightDrawT7 = pThreeCards * 2
		self.nInsideStraightDrawT7 = 128
		# b: Q _ (T) 9 8 _ (6)
		# b: (T) _ 8 7 (6) _ 4
		self.pOutsideStraightDrawT6 = 0.0
		self.nOutsideStraightDrawT6 = 0
		self.pInsideStraightDrawT6 = pThreeCards * 2
		self.nInsideStraightDrawT6 = 128
		#
		self.pOutsideStraightDrawT5 = 0.0
		self.nOutsideStraightDrawT5 = 0
		self.pInsideStraightDrawT5 = 0.0
		self.nInsideStraightDrawT5 = 0
		# b: (T) _ 8 7 6 _ (4)
		self.pOutsideStraightDrawT4 = 0.0
		self.nOutsideStraightDrawT4 = 0
		self.pInsideStraightDrawT4 = pThreeCards * 1
		self.nInsideStraightDrawT4 = 64
		#
		self.pOutsideStraightDrawT3 = 0.0
		self.nOutsideStraightDrawT3 = 0
		self.pInsideStraightDrawT3 = 0.0
		self.nInsideStraightDrawT3 = 0
		#
		self.pOutsideStraightDrawT2 = 0.0
		self.nOutsideStraightDrawT2 = 0
		self.pInsideStraightDrawT2 = 0.0
		self.nInsideStraightDrawT2 = 0
		# s: _ Q J T (9) _
		# s: _ J T (9) 8 _
		# s: _ T (9) 8 7 _
		# s: _ (9) 8 7 6 _
		self.pOutsideStraightDraw99 = pThreeCards * 4
		self.nOutsideStraightDraw99 = 256
		self.pInsideStraightDraw99 = 0.0
		self.nInsideStraightDraw99 = 0
		# s: _ J T (9) (8) _
		# s: _ T (9) (8) 7 _
		# s: _ (9) (8) 7 6 _
		# b: Q _ T (9) (8) _ 6
		# b: J _ (9) (8) 7 _ 5
		self.pOutsideStraightDraw98 = pDraw * 3
		self.nOutsideStraightDraw98 = 1920
		self.pInsideStraightDraw98 = pThreeCards * 2
		self.nInsideStraightDraw98 = 128
		# s: _ T (9) 8 (7) _
		# s: _ (9) 8 (7) 6 _
		# b: K _ J T (9) _ (7)
		# b: J _ (9) 8 (7) _ 5
		# b: (9) _ (7) 6 5 _ 3
		self.pOutsideStraightDraw97 = pDraw * 2
		self.nOutsideStraightDraw97 = 1280
		self.pInsideStraightDraw97 = pThreeCards * 3
		self.nInsideStraightDraw97 = 192
		# s: _ (9) 8 7 (6) _
		# b: Q _ T (9) 8 _ (6)
		# b: (9) _ 7 (6) 5 _ 3
		self.pOutsideStraightDraw96 = pDraw * 1
		self.nOutsideStraightDraw96 = 640
		self.pInsideStraightDraw96 = pThreeCards * 2
		self.nInsideStraightDraw96 = 128
		# b: J _ (9) 8 7 _ (5)
		# b: (9) _ 7 6 (5) _ 3
		self.pOutsideStraightDraw95 = 0.0
		self.nOutsideStraightDraw95 = 0
		self.pInsideStraightDraw95 = pThreeCards * 2
		self.nInsideStraightDraw95 = 128
		#
		self.pOutsideStraightDraw94 = 0.0
		self.nOutsideStraightDraw94 = 0
		self.pInsideStraightDraw94 = 0.0
		self.nInsideStraightDraw94 = 0
		# b: (9) _ 7 6 5 _ (3)
		self.pOutsideStraightDraw93 = 0.0
		self.nOutsideStraightDraw93 = 0
		self.pInsideStraightDraw93 = pThreeCards * 1
		self.nInsideStraightDraw93 = 64
		#
		self.pOutsideStraightDraw92 = 0.0
		self.nOutsideStraightDraw92 = 0
		self.pInsideStraightDraw92 = 0.0
		self.nInsideStraightDraw92 = 0
		# s: _ J T 9 (8) _
		# s: _ T 9 (8) 7 _
		# s: _ 9 (8) 7 6 _
		# s: _ (8) 7 6 5 _
		self.pOutsideStraightDraw88 = pThreeCards * 4
		self.nOutsideStraightDraw88 = 256
		self.pInsideStraightDraw88 = 0.0
		self.nInsideStraightDraw88 = 0
		# s: _ T 9 (8) (7) _
		# s: _ 9 (8) (7) 6 _
		# s: _ (8) (7) 6 5 _
		# b: J _ 9 (8) (7) _ 5
		# b: T _ (8) (7) 6 _ 4
		self.pOutsideStraightDraw87 = pDraw * 3
		self.nOutsideStraightDraw87 = 1920
		self.pInsideStraightDraw87 = pThreeCards * 2
		self.nInsideStraightDraw87 = 128
		# s: _ 9 (8) 7 (6) _
		# s: _ (8) 7 (6) 5 _
		# b: Q _ T 9 (8) _ (6)
		# b: T _ (8) 7 (6) _ 4
		# b: (8) _ (6) 5 4 _ 2
		self.pOutsideStraightDraw86 = pDraw * 2
		self.nOutsideStraightDraw86 = 1280
		self.pInsideStraightDraw86 = pThreeCards * 3
		self.nInsideStraightDraw86 = 192
		# s: _ (8) 7 6 (5) _
		# b: J _ 9 (8) 7 _ (5)
		# b: (8) _ 6 (5) 4 _ 2
		self.pOutsideStraightDraw85 = pDraw * 1
		self.nOutsideStraightDraw85 = 640
		self.pInsideStraightDraw85 = pThreeCards * 2
		self.nInsideStraightDraw85 = 128
		# b: T _ (8) 7 6 _ (4)
		# b: (8) _ 6 5 (4) _ 2
		self.pOutsideStraightDraw84 = 0.0
		self.nOutsideStraightDraw84 = 0
		self.pInsideStraightDraw84 = pThreeCards * 2
		self.nInsideStraightDraw84 = 128
		#
		self.pOutsideStraightDraw83 = 0.0
		self.nOutsideStraightDraw83 = 0
		self.pInsideStraightDraw83 = 0.0
		self.nInsideStraightDraw83 = 0
		# b: (8) _ 6 5 4 _ (2)
		self.pOutsideStraightDraw82 = 0.0
		self.nOutsideStraightDraw82 = 0
		self.pInsideStraightDraw82 = pThreeCards * 1
		self.nInsideStraightDraw82 = 64
		# s: _ T 9 8 (7) _
		# s: _ 9 8 (7) 6 _
		# s: _ 8 (7) 6 5 _
		# s: _ (7) 6 5 4 _
		self.pOutsideStraightDraw77 = pThreeCards * 4
		self.nOutsideStraightDraw77 = 256
		self.pInsideStraightDraw77 = 0.0
		self.nInsideStraightDraw77 = 0
		# s: _ 9 8 (7) (6) _
		# s: _ 8 (7) (6) 5 _
		# s: _ (7) (6) 5 4 _
		# b: T _ 8 (7) (6) _ 4
		# b: 9 _ (7) (6) 5 _ 3
		self.pOutsideStraightDraw76 = pDraw * 3
		self.nOutsideStraightDraw76 = 1920
		self.pInsideStraightDraw76 = pThreeCards * 2
		self.nInsideStraightDraw76 = 128
		# s: _ 8 (7) 6 (5) _
		# s: _ (7) 6 (5) 4 _
		# b: J _ 9 8 (7) _ (5)
		# b: 9 _ (7) 6 (5) _ 3
		# b: (7) _ (5) 4 3 _ A
		self.pOutsideStraightDraw75 = pDraw * 2
		self.nOutsideStraightDraw75 = 1280
		self.pInsideStraightDraw75 = pThreeCards * 3
		self.nInsideStraightDraw75 = 192
		# s: _ (7) 6 5 (4) _
		# b: T _ 8 (7) 6 _ (4)
		# b: (7) _ 5 (4) 3 _ A
		self.pOutsideStraightDraw74 = pDraw * 1
		self.nOutsideStraightDraw74 = 640
		self.pInsideStraightDraw74 = pThreeCards * 2
		self.nInsideStraightDraw74 = 128
		# b: 9 _ (7) 6 5 _ (3)
		# b: (7) _ 5 4 (3) _ A
		self.pOutsideStraightDraw73 = 0.0
		self.nOutsideStraightDraw73 = 0
		self.pInsideStraightDraw73 = pThreeCards * 2
		self.nInsideStraightDraw73 = 128
		#
		self.pOutsideStraightDraw72 = 0.0
		self.nOutsideStraightDraw72 = 0
		self.pInsideStraightDraw72 = 0.0
		self.nInsideStraightDraw72 = 0
		# s: _ 9 8 7 (6) _
		# s: _ 8 7 (6) 5 _
		# s: _ 7 (6) 5 4 _
		# s: _ (6) 5 4 3 _
		self.pOutsideStraightDraw66 = pThreeCards * 4
		self.nOutsideStraightDraw66 = 256
		self.pInsideStraightDraw66 = 0.0
		self.nInsideStraightDraw66 = 0
		# s: _ 8 7 (6) (5) _
		# s: _ 7 (6) (5) 4 _
		# s: _ (6) (5) 4 3 _
		# b: 9 _ 7 (6) (5) _ 3
		# b: 8 _ (6) (5) 4 _ 2
		self.pOutsideStraightDraw65 = pDraw * 3
		self.nOutsideStraightDraw65 = 1920
		self.pInsideStraightDraw65 = pThreeCards * 2
		self.nInsideStraightDraw65 = 128
		# s: _ 7 (6) 5 (4) _
		# s: _ (6) 5 (4) 3 _
		# b: T _ 8 7 (6) _ (4)
		# b: 8 _ (6) 5 (4) _ 2
		self.pOutsideStraightDraw64 = pDraw * 2
		self.nOutsideStraightDraw64 = 1280
		self.pInsideStraightDraw64 = pThreeCards * 2
		self.nInsideStraightDraw64 = 128
		# s: _ (6) 5 4 (3) _
		# b: 9 _ 7 (6) 5 _ (3)
		self.pOutsideStraightDraw63 = pDraw * 1
		self.nOutsideStraightDraw63 = 640
		self.pInsideStraightDraw63 = pThreeCards * 1
		self.nInsideStraightDraw63 = 64
		# b: 8 _ (6) 5 4 _ (2)
		self.pOutsideStraightDraw62 = 0.0
		self.nOutsideStraightDraw62 = 0
		self.pInsideStraightDraw62 = pThreeCards * 1
		self.nInsideStraightDraw62 = 64
		# s: _ 8 7 6 (5) _
		# s: _ 7 6 (5) 4 _
		# s: _ 6 (5) 4 3 _
		# s: _ (5) 4 3 2 _
		self.pOutsideStraightDraw55 = pThreeCards * 4
		self.nOutsideStraightDraw55 = 256
		self.pInsideStraightDraw55 = 0.0
		self.nInsideStraightDraw55 = 0
		# s: _ 7 6 (5) (4) _
		# s: _ 6 (5) (4) 3 _
		# s: _ (5) (4) 3 2 _
		# b: 8 _ 6 (5) (4) _ 2
		# b: 7 _ (5) (4) 3 _ A
		self.pOutsideStraightDraw54 = pDraw * 3
		self.nOutsideStraightDraw54 = 1920
		self.pInsideStraightDraw54 = pThreeCards * 2
		self.nInsideStraightDraw54 = 128
		# s: _ 6 (5) 4 (3) _
		# s: _ (5) 4 (3) 2 _
		# b: 9 _ 7 6 (5) _ (3)
		# b: 7 _ (5) 4 (3) _ A
		self.pOutsideStraightDraw53 = pDraw * 2
		self.nOutsideStraightDraw53 = 1280
		self.pInsideStraightDraw53 = pThreeCards * 2
		self.nInsideStraightDraw53 = 128
		# s: _ (5) 4 3 (2) _
		# b: 8 _ 6 (5) 4 _ (2)
		self.pOutsideStraightDraw52 = pDraw * 1
		self.nOutsideStraightDraw52 = 640
		self.pInsideStraightDraw52 = pThreeCards * 1
		self.nInsideStraightDraw52 = 64
		# s: _ 7 6 5 (4) _
		# s: _ 6 5 (4) 3 _
		# s: _ 5 (4) 3 2 _
		self.pOutsideStraightDraw44 = pThreeCards * 3
		self.nOutsideStraightDraw44 = 192
		self.pInsideStraightDraw44 = 0.0
		self.nInsideStraightDraw44 = 0
		# s: _ 6 5 (4) (3) _
		# s: _ 5 (4) (3) 2 _
		# b: 7 _ 5 (4) (3) _ A
		self.pOutsideStraightDraw43 = pDraw * 2
		self.nOutsideStraightDraw43 = 1280
		self.pInsideStraightDraw43 = pThreeCards * 1
		self.nInsideStraightDraw43 = 64
		# s: _ 5 (4) 3 (2) _
		# b: 8 _ 6 5 (4) _ (2)
		self.pOutsideStraightDraw42 = pDraw * 1
		self.nOutsideStraightDraw42 = 640
		self.pInsideStraightDraw42 = pThreeCards * 1
		self.nInsideStraightDraw42 = 64
		# s: _ 6 5 4 (3) _
		# s: _ 5 4 (3) 2 _
		self.pOutsideStraightDraw33 = pThreeCards * 2
		self.nOutsideStraightDraw33 = 128
		self.pInsideStraightDraw33 = 0.0
		self.nInsideStraightDraw33 = 0
		# s: _ 5 4 (3) (2) _
		self.pOutsideStraightDraw32 = pDraw * 1
		self.nOutsideStraightDraw32 = 640
		self.pInsideStraightDraw32 = 0.0
		self.nInsideStraightDraw32 = 0
		# s: _ 5 4 3 (2) _
		self.pOutsideStraightDraw22 = pThreeCards * 1
		self.nOutsideStraightDraw22 = 64
		self.pInsideStraightDraw22 = 0.0
		self.nInsideStraightDraw22 = 0


			
		
		
	
	
	def evalHandRange(self, handRange):
		result = {
				'nFlops': 0,
				'nStraightFlushs': 0,
				'nQuads': 0,
				'nFlushs': 0,
				'nFullHouses': 0,
				'nStraights': 0,
				'nSets': 0,
				'nTwoPairs': 0,
				'nOverPairs': 0,
				'nTopPairs': 0,
				'nPairs': 0,
				'nFlushDraws': 0,
				
				'nStraightDraws': 0,
				}
		
		for hand in handRange:
			result['nFlops'] += self.nFlops
			
			handType = PokerTools.handTypeFromHand(hand)
			myHandType = handType[:2]
			if PokerTools.handTypeIsPair(handType):
				result['nQuads'] += self.nQuadsPair
				result['nFullHouses'] += self.nFullHouseSetPair
				result['nSets'] += self.nSetPair
				nOverpairs = getattr(self, 'nOverPair%s' % myHandType)
				result['nOverPairs'] += nOverpairs
				result['nPairs'] += self.nPairPair - nOverpairs
				result['nFlushDraws'] += self.nFlushDrawPair
				nInsideDraws = getattr(self, 'nInsideStraightDraw%s' % myHandType)
				nOutsideDraws = getattr(self, 'nOutsideStraightDraw%s' % myHandType)
				result['nStraightDraws'] += nInsideDraws + nOutsideDraws
				
			elif PokerTools.handTypeIsSuited(handType):
				result['nStraightFlushs'] += getattr(self, 'nStraightFlush%s' % myHandType)
				result['nQuads'] += self.nQuadsUnpaired
				result['nFullHouses'] += self.nFullHouseSetUnpaired
				result['nFlushs'] += self.nFlush
				result['nStraights'] += getattr(self, 'nStraight%s' % myHandType)
				result['nSets'] += self.nSetUnpaired
				result['nTwoPairs'] += self.nTwoPairUnpaired
				nTopPairs = getattr(self, 'nTopPair%s' % myHandType)
				result['nTopPairs'] += nTopPairs
				result['nPairs'] += self.nPairUnpaired - nTopPairs
				result['nFlushDraws'] += self.nFlushDrawSuited
				nInsideDraws = getattr(self, 'nInsideStraightDraw%s' % myHandType)
				nOutsideDraws = getattr(self, 'nOutsideStraightDraw%s' % myHandType)
				result['nStraightDraws'] += nInsideDraws + nOutsideDraws
			else:
				result['nQuads'] += self.nQuadsUnpaired
				result['nFullHouses'] += self.nFullHouseSetUnpaired
				result['nStraights'] += getattr(self, 'nStraight%s' % myHandType)
				result['nSets'] += self.nSetUnpaired
				result['nTwoPairs'] += self.nTwoPairUnpaired
				nTopPairs = getattr(self, 'nTopPair%s' % myHandType)
				result['nTopPairs'] += nTopPairs
				result['nPairs'] += self.nPairUnpaired - nTopPairs
				result['nFlushDraws'] += self.nFlushDrawOffsuit
				nInsideDraws = getattr(self, 'nInsideStraightDraw%s' % myHandType)
				nOutsideDraws = getattr(self, 'nOutsideStraightDraw%s' % myHandType)
				result['nStraightDraws'] += nInsideDraws + nOutsideDraws
				
		return result		

class FloatProgressBar(QtGui.QProgressBar):
	def __init__(self, parent=None, prefix=''):
		QtGui.QProgressBar.__init__(self, parent)
		self.floatValue = 0.0
		self.prefix = prefix
		self.setMaximum(10000)
		self.valueChanged.connect(self.onValueChanged)
		self.setValue(self.floatValue)
	def onValueChanged(self, value):
		self.setFormat('%s%.02f%%' % (self.prefix, self.floatValue*100))
	def setValue(self, value):
		self.floatValue = value
		QtGui.QProgressBar.setValue(self, int(value*10000))
			

class FlopEvalWidget(QtGui.QFrame):
	
	
	def __init__(self, parent=None, styleSheet=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.handEval = TexasHoldem.HandEval()
		self.flopalyzer = Flopalyzer()
		
		self.labelHandRange = QtGui.QLabel('Select a hand range', self)
		self.handRangeWidget = HandTypesHoldemWidget.HandTypesHoldemWidget(parent=self, pct=15)
		self.labelFlop = QtGui.QLabel('Select a flop', self)
		self.labelFlop.setWordWrap(True)
		self.flopWidget = CardSelectorWidget.CardSelectorWidget(parent=self, maxCards=3)
		self.flopWidget.cardsSelectionChanged.connect(self.onflopWidgetCardsSelectionChanged)
				
		self.buttonEvalFlop = QtGui.QPushButton('Evaluate flop', self)
		self.buttonEvalFlop.setEnabled(False)
		self.buttonEvalFlop.clicked.connect(self.onButtonEvalFlopClicked)
		self.buttonEvalRandom = QtGui.QPushButton('Evaluate randon', self)
		self.buttonEvalRandom.clicked.connect(self.onButtonEvalRandomClicked)
		
		self.progressBars = [
				['nStraightFlushs', 'StraightFlushs: ', None],
				['nQuads', 'Quads: ', None],
				['nFullHouses', 'FullHouse: ', None],
				['nFlushs', 'Flush: ', None],
				['nStraights', 'Straight: ', None],
				['nSets', 'Set: ', None],
				['nTwoPairs', 'TwoPair: ', None],
				['nOverPairs', 'OverPair: ', None],
				['nTopPairs', 'TopPair: ', None],
				['nPairs', 'Pair: ', None],
				['nFlushDraws', 'FlushDraw: ', None],
				['nStraightDraws', 'StraightDraw: ', None],
				]
		#TODO: hard code stylefroprogress bars. good idea or not?
		#some styles display progress text tothe right of the bar
		# obv we don't like that.
		style = QtGui.QStyleFactory.create('plastique')
		for i, data in enumerate(self.progressBars):
			widget = FloatProgressBar(self, data[1])
			widget.setStyle(style)
			self.progressBars[i][2] = widget
					
		
		# layout
		
		box0 = QtGui.QVBoxLayout(self)
		
		box1 = QtGui.QHBoxLayout()
		box0.addLayout(box1)
		
		box2 = QtGui.QVBoxLayout()
		box1.addLayout(box2)
		box2.addWidget(self.labelHandRange)
		box2.addWidget(self.handRangeWidget)
		
		box2 = QtGui.QVBoxLayout()
		box1.addLayout(box2)
		box2.addWidget(self.labelFlop)
		box2.addWidget(self.flopWidget, 0, QtCore.Qt.AlignHCenter)
		box2.addWidget(self.buttonEvalFlop)
		box2.addWidget(self.buttonEvalRandom)
		
		
		box2 = QtGui.QHBoxLayout()
		box0.addLayout(box2)
			
		
		for i, data in enumerate(self.progressBars):
			if i == 0 or i == 6:
				box = QtGui.QVBoxLayout()
				box2.addLayout(box)
			box.addWidget(data[2])
		
		s = QtGui.QVBoxLayout()
		s.addStretch(999)
		box0.addLayout(s)
		
		#TODO: add right stretch. good idea or not?
		s = QtGui.QHBoxLayout()
		s.addStretch(999)
		box1.addLayout(s)
		
	def handleFontChanged(self, font=None):
		self.handRangeWidget.handleFontChanged(font=font)
		self.flopWidget.handleFontChanged(font=font)
		
	def _resetResult(self):
		for data in self.progressBars:
			data[2].setValue(0.0)	
	
	def _setResult(self, result):
		nFlops = float(result['nFlops'])
		for data in self.progressBars:
			value = result[data[0]]
			if value:
				value = value / float(nFlops)
			data[2].setValue(value)
			
	def _makeResult(self):
		result = {}
		for data in self.progressBars:
			result[data[0]] = 0
		result['nFlops'] = 0
		return result
				
	def _evalFlop(self, hand, flop, result):
		result['nFlops'] += 1
		cards = list(hand.cards) + flop
		
		if self.handEval.getStraightFlush(cards):
			result['nStraightFlushs'] += 1
			return
		if self.handEval.getQuads(cards):
			result['nQuads'] += 1
			return
		#TODO: case flop is set
		if self.handEval.getFullHouse(cards):
			result['nFullHouses'] += 1
			return
		if self.handEval.getFlush(cards):
			result['nFlushs'] += 1
			return
		
		flushDraw = self.handEval.getFlush(cards, count=4)
		if flushDraw:
			result['nFlushDraws'] += 1
				
		if self.handEval.getStraight(cards):
			result['nStraights'] += 1
			return
						
		straightDraw = self.handEval.getInsideStraightDraw(cards)
		if straightDraw:
			result['nStraightDraws'] += 1
		straightDraw = self.handEval.getOutsideStraightDraw(cards)
		if straightDraw:
			result['nStraightDraws'] += 1	
				
		trips =  self.handEval.getTrips(cards)
		if trips:
			# filter flop trips
			n = len([i for i in flop if i in trips[:3]])
			if n < 3:
				result['nSets'] += 1
			return
				
		twoPair = self.handEval.getTwoPair(cards)
		if twoPair:
			# filter flop pairs
			pair1 = twoPair[:2]
			pair2 = twoPair[2:4]
			# count cards flop contributed to pairs
			n1 = len([i for i in flop if i in pair1])
			n2 = len([i for i in flop if i in pair2])
			if n1 == 1 and n2 == 1:
				# flopped 2pair
				result['nTwoPairs'] += 1
			elif n1 == 1 and n2 == 2:
				# flopped top pair	
				result['nTopPairs'] += 1
			elif n1 == 2 and n2 == 1:
				# flopped < top pair
				result['nPairs'] += 1
			elif n1 == 0 and n2 == 2 and twoPair[0].rank() > twoPair[4].rank():
				# we have an overpair
				result['nOverPairs'] += 1
			return
			
		pair = self.handEval.getPair(cards)
		if pair:
			# filter flop pair
			n = len([i for i in flop if i in pair[:2]])
			if n == 0:
				# we have a pocket pair
				if pair[0].rank() > pair[2].rank():
					# we have an overpair
					result['nOverPairs'] += 1
				else:
					result['nPairs'] += 1
			elif n == 1:
				if pair[0].rank() and not [i for i in flop if i.rank() > pair[0].rank()]:
					# we have topPair
					result['nTopPairs'] += 1
				else:
					result['nPairs'] += 1
			return
					
	def onButtonEvalFlopClicked(self):
		self._resetResult()
		flop = self.flopWidget.cards()
		handRange = self.handRangeWidget.handRange()
		result = self._makeResult()
		for hand in handRange:
			# skip hands with cards on flop
			if [i for i in hand.cards if i in flop]:
				continue
			self._evalFlop(hand, flop, result)
		self._setResult(result)
		
	def onButtonEvalRandomClicked(self):
		self._resetResult()
		handRange = self.handRangeWidget.handRange()
		result = self._makeResult()
		result.update(self.flopalyzer.evalHandRange(handRange))
		self._setResult(result)
			
	def onflopWidgetCardsSelectionChanged(self, widget):
		self.buttonEvalFlop.setEnabled(widget.cardCount() == 3)

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = FlopEvalWidget()
	gui.show()
	application.exec_()
