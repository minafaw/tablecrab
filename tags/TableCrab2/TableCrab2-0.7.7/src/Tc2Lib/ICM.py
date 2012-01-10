
import itertools, random
#************************************************************************************
#
#************************************************************************************
def sliceStacks(iStack, stacks):
	"""sums up slice of stacks
	@param iStack: index of the stack to slice stacks for
	@param stacks: iterable of stacks
	@return: (list) sliced stacks
	"""
	result = [0 for i in xrange(len(stacks))]
	for i, stack in enumerate(stacks):
		if i == iStack:
			result[iStack] += stacks[iStack]
		else:
			if stack > stacks[iStack]:
				result[iStack] += stacks[iStack]
				result[i] = stacks[i] - stacks[iStack]
			else:
				result[iStack] += stacks[i]
				result[i] = 0
	return result		


def tourneyEV(stacks, payouts):
	"""calculates tourney ev for each player (ICM)
	@param stacks: (list) of player stacks
	@param payouts: (list) of tourney payouts
	@return: (list) tourney ev for each stack
	"""
	def evPlayer(stacks, payouts, total, player, depth):
		ev = stacks[player] / total * payouts[depth]
		if depth + 1 < len(payouts):
			for otherPlayer, stack in enumerate(stacks):
				if otherPlayer == player or stack <= 0.0: continue
				stacks[otherPlayer] = 0.0
				ev += evPlayer(stacks, payouts, total - stack, player, depth + 1) * stack / total
				stacks[otherPlayer] = stack
		return ev
	stacks = [float(i) for i in stacks]
	total = sum(stacks)
	return [evPlayer(stacks, payouts, total, player, 0) for player in xrange(len(stacks))]

	
def bubbleFactors(stacks, payouts):
	"""calculates the bubble factors of each player matchup
	@param stacks: (list) of player stacks
	@param payouts: (list) of tourney payouts
	@return: (liat) matrix of bubble factors for stack vs stack in stacks
	"""
	if len(stacks) < len(payouts):
		payouts = payouts[:len(stacks)]
	
	result = [[None for i in xrange(len(stacks))] for j in xrange(len(stacks))]
	
	evs = tourneyEV(stacks, payouts)
	for hero, villain in itertools.permutations(range(len(stacks)), 2):
		
		evWin = evLoose = 0
			
		# case hero wins
		stacksNew = list(stacks[:])
		stacksNew[hero], stacksNew[villain] = sliceStacks(0, (stacks[hero], stacks[villain]) )
		if stacksNew[villain] <= 0:
			del stacksNew[villain]
			evsNew = tourneyEV(stacksNew, payouts)
			evWin = evsNew[hero] if hero < villain else evsNew[hero -1]
		else:
			evsNew = tourneyEV(stacksNew, payouts)
			evWin = evsNew[hero]
			
		# case hero looses
		stacksNew = list(stacks[:])
		stacksNew[hero], stacksNew[villain] = sliceStacks(1, (stacks[hero], stacks[villain]) )
		if stacksNew[hero] <= 0:
			del stacksNew[hero]
			if len(stacksNew) < len(payouts):
				evLoose = payouts[-1]
		else:
			evsNew = tourneyEV(stacksNew, payouts)
			evLoose = evsNew[hero]
			
		result[hero] [villain] = abs( ( evLoose - evs[hero] ) / (evWin - evs[hero] ) )
			
	return result		
	

def taxFactor(bubbleFactor):
	"""returns icm tax facor given bubble factor"""
	return 1 - 1/bubbleFactor
	
	
def sicm(stacks, payouts, iterations=1000, randfloat=random.random):
	'''
	simulatedICM algorithm

	Given n players
	Given stack sizes S = S1, S2, ...Sn

	Get normalized stack sizes Q = Q1, Q2, ...Qn by dividing S by average stack
	Given prizes Z = Z1, Z2, ... Zn
	Simulate 1 tournament:
	- For each player i, generate a "place" for each player (Pi) by generating a random 
	  number between 0 and 1 and raising it to the power of 1/Qi. Pi = rand ^ (1.0 / Qi)
	- Sort players by their place P - higher is better
	- Award prizes Z according to P

	Repeat for as many tournaments as desired and calculate the average prize value for each player. 
	The error will be proportional to 1/sqrt(iterations) so the more iterations you run, 
	the more accurate it will be.

	see: [http://forumserver.twoplustwo.com/15/poker-theory/new-algorithm-calculate-icm-large-tournaments-1098489/]
	'''
	avgStack = sum(stacks) / float(len(stacks))
	# equivalent to line below
	##normStacks = [1 / (s / avgStack) for s in stacks]
	normStacks = [avgStack / s for s in stacks]
	players = range(len(stacks))
	result = [0]*len(stacks)
	for i in xrange(iterations):
		# equivalent to line below
		##weights = [log(randfloat()) * q for q in normStacks]
		weights = [randfloat() ** q for q in normStacks]
		score = zip(weights, players)
		score.sort(reverse=True)
		for i, payout in enumerate(payouts):
			player = score[i][1]
			result[player] += payout
	##print 'err: %s' % (1.0 / sqrt(iterations))
	return [float(i) / iterations for i in result]
	
