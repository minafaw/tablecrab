
import itertools
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
	
	
def foo():
	payouts =  (0.5, 0.3, 0.2)
	stacks = [1000.0, 5100.0, 2000.0, 500.0]
	p = bubbleFactors(stacks, payouts)
	hero = 0
	for villain, f in enumerate(p[hero]):
		if f is None: continue
		
		f2 = p[villain][hero]
		
		tax = taxFactor(f)
		tax = int(round(tax*100, 0))
		
		tax2 = taxFactor(f2)
		tax2 = int(round(tax2*100, 0))
		
		print '(%s, %s)=%s/%s' % (hero, villain, tax, tax2)
		
#foo()
	
	
