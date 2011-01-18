
def probToPercent(probability, round_=2):
	return round(probability * 100, round_)

# la place experiment
def prob(a, b):
	return float(a) / float(b)

def binom(n, k):
    if 0 <= k <= n:
        p = 1
        for t in xrange(min(k, n - k)):
            p = (p * (n - t)) // (t + 1)
        return float(p)
    else:
        return float(0)

#************************************************************************************
#
#************************************************************************************
class Card:
	Ranks = '23456789TJQKA'
	Suits = 'hdcs'

#************************************************************************************
# holdem trivia
#************************************************************************************
# calculates the probability that at least one  opponent is holding a higher pair
def probHigherPair(cardRank, nOponents=1):
	if cardRank < 0 or cardRank > 12: raise ValueError('cardRank must be in 0-12')
	return (84 - (6*(cardRank + 2))) / float(1225) * nOponents

def numSevenCardCombinations():
	return binom(52, 7)

def numStraightFlushs():
	return binom(4,1) * (binom(47, 2) + binom(9, 1) * binom(46, 2) )

def numFourOfKind():
	return binom(13, 1) * binom(48, 3)

def numFullHouses():
	return (
			(binom(13, 1) * binom(4, 3) * binom(12, 1) * binom(4, 2) * binom(11, 2) * binom(4, 1)**2) +
			(binom(13, 2) * binom(4, 2)**2 * binom(11, 1) * binom(4, 1)) +
			(binom(13, 2) * binom(4, 3)**2 * binom(11, 1) * binom(4, 1))
			)

def numFlushs():
	return binom(4, 1) * (binom(13, 5) * binom(39, 2) + binom(13, 6) * binom(39, 1) + binom(13, 7)) - 41584

def numStraights():

	nSetsOfRanks = binom(8, 2) + binom(9, 1) *binom(7,2)
	nSetsOfSuits = binom(4, 1)**7
	nFlushes = binom(4, 1) * (1+binom(7, 6) * binom(3, 1) + binom(7, 5) * binom(3, 1)**2)
	nSevenDistinctRanks = nSetsOfRanks * (nSetsOfSuits - nFlushes)

	nSetsOfRanks = binom(8, 1) + binom(9, 1) * binom(7, 1)
	nPairs = binom(6, 1) * binom(4, 2)
	nSetsOfSuits = binom(4, 1)**5
	nFlushs = binom(4, 1) + binom(5, 4) * binom(2, 1) * binom(3, 1)
	nPairs = binom(6, 1) * binom(4, 2)
	nSixDistinctRanks = nSetsOfRanks *  nPairs * (nSetsOfSuits - nFlushs)

	nTripples = binom(5, 1) * binom(4, 3)
	nStraightsNotFlush = binom(4, 1)**4 - binom(3, 1)
	nSetsOfRanks = 10
	nFiveDistinctRanksPlusTripple = nSetsOfRanks * nTripples * nStraightsNotFlush

	nPairs = binom(5, 2)
	nSuitsOfPairs = binom(4, 2)**2
	nSuitsNotFlush = 6 * (64 - binom(2, 1)) + 24 * (64 - 1) + 6 * 64
	nFiveDistinctRanksTwoPairs = nPairs * nPairs * nSuitsNotFlush

	return (
			nSevenDistinctRanks +
			nSixDistinctRanks +
			nFiveDistinctRanksPlusTripple +
			nFiveDistinctRanksTwoPairs
			)

def numThreeOfKind():
	nSetsOfRanks = binom(13, 5) - 10
	nTripples = binom(5, 1) * binom(4, 3)
	nSuits = binom(4, 1)**4 - binom(3, 1)
	return nSetsOfRanks * nTripples * nSuits

def numTwoPair():
	nThreePairOneKicker = binom(13, 4) * binom(4, 3) * binom(4, 2)**3 * binom(4, 1)
	nTwoPairsThreeKickers = (binom(13, 5) -10) * binom(5, 2) * 2268
	return nThreePairOneKicker + nTwoPairsThreeKickers

def numOnePair():
	nSetsOfRanks = binom(13, 6) - 9 - (2 * binom(7, 1) + 8 * binom(6, 1))
	nSuits = binom(4, 1)**5 - 34
	nRanks = binom(6, 1) * binom(4, 2)
	return nSetsOfRanks * nSuits * nRanks

def numNoPair():
	nSetsOfRanks = binom(13, 7) - 8 - (2 * binom(6, 1) + 7 * binom(5, 1)) - (2 * binom(7, 2) + 8  * binom(6, 2))
	nSuits = binom(4, 1)**7 - 844
	return nSetsOfRanks * nSuits

def numStartingHands():
	return binom(52, 2)

def numPocketPairs():
	return binom(13, 2)

# if you hold a pocket pair, how likely is it that there is ta least one overcard on the board
def percentOvercardsToPair(cardRank, nCards):
	if cardRank < 0 or cardRank > 12: raise ValueError('cardRank must be in 0-12')
	nOvercards = (12 - cardRank) * 4
	nBoardsWithoutOvercards = binom(52-nOvercards, nCards)
	if nBoardsWithoutOvercards:
		nBoards = binom(52, nCards)
		return (1 - (nBoardsWithoutOvercards / nBoards)) * 100
	return 100.0
