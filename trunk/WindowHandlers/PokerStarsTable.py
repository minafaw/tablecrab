
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import Registry
from . import PokerStarsWindowBase

#TODO:
#    - check if BB/SB as reflected in title may change while a hand is running (tourneys). cant remember right now
#
#********************************************************************************************
class PokerStarsTableTitle(object):
	PatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	def __init__(self, string):
		self.smallBlind = 0.0
		self.bigBlind = 0.0
		
		match = self.PatAmountSB.match(string)
		if match is None:
			raise ValueError('could not determine smallBlind: %s' % string)
		self.smallBlind = float(match.group(1))
		match = self.PatAmountBB.match(string)
		if match is None:
			raise ValueError('could not determine smallBlind: %s' % string)
		self.bigBlind = float(match.group(1))
	
	# throw in method for on the fly testing
	@classmethod
	def test(klass):
		TestTitles = (
				{
					'title': "$3.40 No Limit Hold'em - Tournament 189152637 Table 1 - Blinds $200/$400 Ante $25",
					'smallBlind': 200.0,
					'bigBlind': 400.0,
				},
				{
					'title': "Lepus II - 5/10 Play Money - No Limit Hold'em - Logged In as playerNameHere",
					'smallBlind': 5.0,
					'bigBlind': 10.0,
				},
				{
					'title': "Pele fast - $0.01/$0.02 - No Limit Hold'em",
					'smallBlind': 0.01,
					'bigBlind': 0.02,
				},
				{
					'title': "Siri III fast - $2/$4 - No Limit Hold'em",
					'smallBlind': 2.0,
					'bigBlind': 4.0,
				},
				{
					'title': "Hugo V 50BB min - $2/$4 - No Limit Hold'em",
					'smallBlind': 2.0,
					'bigBlind': 4.0,
				},
			)
				
		for p in TestTitles:
			t = klass(p['title'])
			assert t.smallBlind == p['smallBlind'], 'expectedSmallBlind: %s, got: %s, %s' % (p['smallBlind'], t.smallBlind, p['title'])
			assert t.bigBlind == p['bigBlind'], 'expectedBigBlind: %s, got: %s, "%s"' % (p['bigBlind'], t.bigBlind, p['title'])
		
#PokerStarsTableTitle.test()

#************************************************************************************************
class PokerStarsTable(PokerStarsWindowBase.PokerStarsWindowBase):
	"""fallback window handler if no handler is present for a window"""
	Type = Registry.WindowHandlerType
	Site = 'PokerStars'
	Window = 'Table'
	
	PsClassTableBetAmountBox = 'PokerStarsSliderEditorClass'
	PatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		if klass.psIsTable(cli, hWindow):
			return klass(cli, hWindow)
		return None
			
	def __init__(self, cli, hWindow):
		self.cli = cli
		self.hWindow = hWindow
		self.cli.log(self, 'created hWindow="%s" title="%s"' % (self.hWindow, self.cli.application.windowManager.windowGetText(self.hWindow)) )
		
	def getBlinds(self):
		title = self.cli.application.windowManager.windowGetText(self.hWindow)
		title = PokerStarsTableTitle(title)
		return {'smallBlind': title.smallBlind, 'bigBlind': title.bigBlind}
		
	def canBet(self):
		"""checks if the player currently can bet
		@return: (bool)
		"""
		hWindow = self.getBetAmountBox()
		if hWindow:
			return self.cli.application.windowManager.windowIsVisible(hWindow)
		return False
	
	def getBetAmountBox(self):
		hWindow = self.cli.application.windowManager.windowFindChild(self.hWindow, className=self.PsClassTableBetAmountBox)
		if hWindow:
			return hWindow
		return False
		
	
	def getBetAmount(self):
		"""returns the bet current bet height
		@return: float(amount) or None
		"""
		hWindow = self.getBetAmountBox()
		if hWindow:
			p = self.cli.application.windowManager.windowGetText(hWindow)
			if p:	return float(p)
		return None
				
	def setBetAmount(self, value=0.0):
		"""sets the current bet height
		@param hwnd: (hwnd) of the window to check or None to check the current foreground window
		@return: float(amount) or None
		"""
		hWindow = self.getBetAmountBox()
		if hWindow:
			if int(value) == value:
				value = int(value)
			value = 0 if value <= 0 else value
			value = str(value)
			self.cli.application.windowManager.windowSetText(hWindow, text=value)
	
	
	def doAddOneBB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(value=betAmount + blinds['bigBlind'])
			self.cli.log(self, 'add one BB')
			return True
		
	def doSubtractOneBB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(value=betAmount - blinds['bigBlind'])
			self.cli.log(self, 'subtract one BB')
			return True
	
	def doAddOneSB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(value=betAmount + blinds['smallBlind'])
			self.cli.log(self, 'add one SB')
			return True
		
	def doSubtractOneSB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(value=betAmount - blinds['smallBlind'])
			self.cli.log(self, 'subtract one SB')
			return True
	
	
	def doCheck(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		for table in self.cli.config['pokerstars-tables']:
			if table['size'] == size:
				pt = table['point-button-check']
				if pt is not None:
					pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
					self.cli.application.mouseManager.mouseClickLeft(pt)
					self.cli.log(self, 'check')
					return True
		return False
				
	def doFold(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		for table in self.cli.config['pokerstars-tables']:
			if table['size'] == size:
				if self.canBet():
					pt = table['point-button-fold']
					if pt is not None:
						pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
						self.cli.application.mouseManager.mouseClickLeft(pt)
						self.cli.log(self, 'fold')
						return True
				else:
					pt = table['point-checkbox-fold']
					if pt is not None:
						pt = table['point-checkbox-fold']
						pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
						self.cli.application.mouseManager.mouseClickLeft(pt)
						self.cli.log(self, 'fold')
						return True
		return False
		
	def doRaise(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		for table in self.cli.config['pokerstars-tables']:
			if table['size'] == size:
				pt = table['point-button-raise']
				if pt is not None:
					pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
					self.cli.application.mouseManager.mouseClickLeft(pt)
					self.cli.log(self, 'raise')
					return True
		return False
		
	def doShowReplayer(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		for table in self.cli.config['pokerstars-tables']:
			if table['size'] == size:
				pt = table['point-button-replayer-1']
				if pt is not None:
					pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
					self.cli.application.mouseManager.mouseClickLeft(pt)
					pt = table['point-button-replayer-2']
					if pt is not None:
						pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
						self.cli.application.mouseManager.mouseClickLeft(pt)
					self.cli.log(self, 'show/update replayer')
					return True
		return False
		
	def doHilightBetAmount(self):
		hWindow = self.getBetAmountBox()
		if hWindow:
			rc = self.cli.application.windowManager.windowGetRect(hWindow)
			self.cli.application.mouseManager.mouseClickLeftDouble( (rc[0] +3, rc[1] +3) )
			self.cli.log(self, 'hilight bet amount box')
			return True
	
	
	def handleWindowDestroyed(self, cli, hWindow):
		self.cli.log(self, 'destroyed hWindow="%s"' % self.hWindow)
		return False
	
	def handleWindowGainForeground(self, cli, hWindow):
		
		if cli.config['tables']['bool-move-mouse-to-active-table']:
			# skip if any mouse buttons are down
			if cli.application.mouseManager.mouseGetButtonsDown():
				#NOTE: mouse messages may come at any time. so this test does not work reliably
				# if mouse holds down left on self caption for example we get foreground status before
				# the new mouse status gets reported ++ all sorts of evil race conditions more
				return False
			# skip if the mouse is already on the window. have to check this this here, see note above
			x, y, w, h =  cli.application.windowManager.windowGetRect(hWindow)
			mX, mY = cli.application.mouseManager.mouseGetPos()
			if (mX >= x and mX <= x + w) and (mY >= y and mY <= y + h):
				return False
			rc = cli.application.windowManager.windowGetClientRect(hWindow, toScreen=True)
			cli.application.mouseManager.mouseSetPos( (rc[0] + rc[2], rc[1] + rc[3]) )
			return True
		
		return False
	
	def handleWindowLooseForeground(self, cli, hWindow):
		return False	
	
	def handleKeyPressed(self, cli, key):
		for table in self.cli.config['pokerstars-tables']:
			if key == table['key']:
				self.cli.log(self, 'handle table as:%s' % table['name'])
				hwnd = self.cli.application.windowManager.windowForeground()
				self.cli.application.windowManager.windowSetClientSize(hwnd, size=table['size'])
				return True
		
		if key == self.cli.config['table']['key-fold']:
			if self.doFold(): return True
		elif key == self.cli.config['table']['key-check']:
			if self.doCheck(): return True
		elif key == self.cli.config['table']['key-raise']:
			if self.doRaise(): return True
		elif key == self.cli.config['table']['key-replayer']:
			if self.doShowReplayer(): return True
		elif key == self.cli.config['table']['key-hilight-bet-amount']:
			if self.doHilightBetAmount(): return True
		elif key == self.cli.config['table']['key-add-one-bb']:
			if self.doAddOneBB(): return True
		elif key == self.cli.config['table']['key-subtract-one-bb']:
			if self.doSubtractOneBB(): return True
		elif key == self.cli.config['table']['key-add-one-sb']:
			if self.doAddOneSB(): return True
		elif key == self.cli.config['table']['key-subtract-one-sb']:
			if self.doSubtractOneSB(): return True
			
		return False	
	
	def handleKeyReleased(self,  cli, key):
		return False
		

