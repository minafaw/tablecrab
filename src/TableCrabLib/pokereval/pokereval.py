
import os, subprocess
#************************************************************************************
# helpers
#************************************************************************************
# locate gocr.exe in PyInstaler it is included in data dir == os.environ _MEIPASS2
DirData = os.environ.get('_MEIPASS2', None)
if DirData is None:
	DirData = os.path.dirname(os.path.abspath(__file__))
FileNamePokerEnum = os.path.join(DirData, 'pokenum133.exe')

GameHoldem = 'Holdem',
GameHoldemHiLo8 = 'HoldemHiLo8',
GameOmaha = 'Omaha',
GameOmahaHiLo = 'OmahaHiLo8'
GameSevenCardStud = 'SevenCardStud'
GameSevenCardStudHiLo8 = 'SevenCardStudHiLo'
GameSevenCardStudHiLo = 'SevenCardStudHiLo'
GameRazz = 'Razz'
GameFiveCardDraw = 'FiveCardDraw'
GameFiveCardDrawHiLo8 = 'FiveCardDrawhiLo8'
GameFiveCardDrawHiLo = 'FiveCardDrawHiLo'
GameFiveCardDraw27Lowball = 'FiveCardDraw27Lowball'

_GameMapping = {
		GameHoldem: '-h',
		GameHoldemHiLo8: '-h8',
		GameOmaha: '-o',
		GameHoldemHiLo8: '-o8',
		GameSevenCardStud: '-7s',
		GameSevenCardStudHiLo8: '-7s8',
		GameSevenCardStudHiLo: '-7snsq',
		GameRazz: '-r',
		GameFiveCardDraw: '-5d',
		GameFiveCardDrawHiLo8: '-5d8',
		GameFiveCardDrawHiLo8: '-5dnsq',
		GameFiveCardDraw27Lowball: '-l27',
		}
#************************************************************************************
#
#************************************************************************************
# NOTE: not implemented flags
#           -t  terse output (one line, list of EV values)
#           -O compute and output detailed relative rank ordering histogram
def pokerEval(game, board, cards, deadCards=None, nIterations=0):
	"""
	@param game: (Game*)
	@param board: (cards) list of board cards ('Ah', 'Qs', ...)
	@param cards: (list) list of pocket cards for each player (('4h', '3d'), ...)
	@param nIterations: (int) if 0 exhaustve enumeration. if > 0 monte carlo enumeration
	@param deadCards: (cards) list containing dead cards
	@return: (list) of dicts containing evaluation for each player. the dict has the following members:
	    * cards: cards of player
	    * win: win percentage
	    * loose: loose percentage
	    * tie: tie percentage
	    * ev: ev
	"""
	args = ''
	for cards in cards:
		if args:
			args += ' - '
		args += ' '.join(cards)
	args += ' -- ' + ' '.join(board)
	game = _GameMapping.get(game, None)
	if game is None:
		raise ValueError('no such game: %s' % game)
	enumeration = ''
	if nIterations:
		enumeration = '-mc %s' % nIterations
	args = '"%s" %s %s %s' % (FileNamePokerEnum, game, enumeration, args)
	if deadCards:
		args += ' /%s' % ' '.join(deadCards)
	#print args
	p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = p.communicate()
	#print out
	if p.returncode:
		raise ValueError(out)
	if err:
		raise ValueError(err)
	result = []
	out = out.split('\n')
	out.pop(0)
	out.pop(0)
	for line in out:
		if not line: continue
		p = line.split()
		d = {
				'cards': (p[0], p[1]),
				'win': float(p[3]),
				'loose': float(p[5]),
				'tie': float(p[7]),
				'ev': float(p[8])
				}
		result.append(d)
	return result

#************************************************************************************
#
#************************************************************************************
def _test():
	result = pokerEval(
			GameHoldem,
			('As', '2h', '3h', 'Js'),
			(
				('Ah', '7d'),
				('Ad', '6s'),
				('Ks', 'Qs'),
			),
			nIterations=1000,
			)
	for i in result:
		print i

if __name__ == '__main__': _test()


