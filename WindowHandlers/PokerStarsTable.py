
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import PokerStarsWindowBase

#********************************************************************************************
class PokerStarsTable(PokerStarsWindowBase.PokerStarsWindowBase):
	"""fallback window handler if no handler is present for a window"""
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
		
	def getBlinds(self):
		blinds = {'smallBlind': 0.0, 'bigBlind': 0.0}
		title = self.cli.application.windowManager.windowGetText(self.hWindow)
		match = self.PatAmountSB.match(title)
		if match is None:
			raise ValueError('could not determine smallBlind: %s' % title)
		blinds['smallBlind'] = float(match.group(1))
		match = self.PatAmountBB.match(title)
		if match is None:
			raise ValueError('could not determine smallBlind: %s' % title)
		blinds['bigBlind'] = float(match.group(1))
		return blinds
		
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
			value = str(value)
			value = 0 if value < 0 else value
			self.cli.application.windowManager.windowSetText(hWindow, text=value)
	
	
	def doAddOneBB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(betAmount + blinds['bigBlind'])
			self.cli.log(self, 'add one BB')
			return True
		
	def doSubtractOneBB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(betAmount - blinds['bigBlind'])
			self.cli.log(self, 'subtract one BB')
			return True
	
	def doAddOneSB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(betAmount + blinds['smallBlind'])
			self.cli.log(self, 'add one SB')
			return True
		
	def doSubtractOneSB(self):
		betAmount = self.getBetAmount()
		if betAmount is not None:
			blinds = self.getBlinds()
			self.setBetAmount(betAmount + blinds['smallBlind'])
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
		return False
	
	def handleWindowGainForeground(self, cli, hWindow):
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
		

