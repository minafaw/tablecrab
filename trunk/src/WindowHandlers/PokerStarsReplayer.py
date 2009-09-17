"""window handler for PokerStars tables
""" 
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import Registry
from . import PokerStarsWindowBase

#********************************************************************************************
class PokerStarsReplayer(object):		#NOTE: we do not register this class as Windowhandler. it is initialized through PokerStarsTable
	"""PokerStars table implementation"""
	Type = Registry.WindowHandlerType
	Site = 'PokerStars'
	Window = 'Replayer'
	
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		raise ValueError('this class does is not intended to be used as registered WindowHandler')
				
	def __init__(self, cli, hWindow):
		self.cli = cli
		self.hWindow = hWindow
		self.cli.log(self, 'created hWindow="%s" title="%s"' % (self.hWindow, self.cli.application.windowManager.windowGetText(self.hWindow)) )
		self.cli.application.windowManager.windowSetClientSize(self.hWindow, size=self.cli.config['pokerstars-replayer']['size'])
		
	
	def doHandStart(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		if size == self.cli.config['pokerstars-replayer']['size']:
			pt = self.cli.config['pokerstars-replayer']['point-button-start']
			if pt is not None:
				pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
				self.cli.application.mouseManager.mouseClickLeft(pt)
				self.cli.log(self, 'hand-start')
				return True
		return False
	
	def doHandStop(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		if size == self.cli.config['pokerstars-replayer']['size']:
			pt = self.cli.config['pokerstars-replayer']['point-button-stop']
			if pt is not None:
				pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
				self.cli.application.mouseManager.mouseClickLeft(pt)
				self.cli.log(self, 'hand-stop')
				return True
		return False	
	
	def doHandNext(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		if size == self.cli.config['pokerstars-replayer']['size']:
			pt = self.cli.config['pokerstars-replayer']['point-button-next']
			if pt is not None:
				pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
				self.cli.application.mouseManager.mouseClickLeft(pt)
				self.cli.log(self, 'hand-next')
				return True
		return False	
	
	def doHandPrev(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		if size == self.cli.config['pokerstars-replayer']['size']:
			pt = self.cli.config['pokerstars-replayer']['point-button-prev']
			if pt is not None:
				pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
				self.cli.application.mouseManager.mouseClickLeft(pt)
				self.cli.log(self, 'hand-prev')
				return True
		return False	
	
	def doHandFirst(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		if size == self.cli.config['pokerstars-replayer']['size']:
			pt = self.cli.config['pokerstars-replayer']['point-button-first']
			if pt is not None:
				pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
				self.cli.application.mouseManager.mouseClickLeft(pt)
				self.cli.log(self, 'hand-first')
				return True
		return False	
	
	def doHandLast(self):
		size = self.cli.application.windowManager.windowGetClientSize(self.hWindow)
		if size == self.cli.config['pokerstars-replayer']['size']:
			pt = self.cli.config['pokerstars-replayer']['point-button-last']
			if pt is not None:
				pt = self.cli.application.windowManager.windowClientPointToScreenPoint(self.hWindow, pt)
				self.cli.application.mouseManager.mouseClickLeft(pt)
				self.cli.log(self, 'hand-last')
				return True
		return False	
	
	
	def handleWindowDestroyed(self, cli, hWindow):
		self.cli.log(self, 'destroyed hWindow="%s"' % self.hWindow)
		return False
	
	def handleWindowGainForeground(self, cli, hWindow):
		return False
		
	def handleWindowLooseForeground(self, cli, hWindow):
		return False	
	
	def handleKeyPressed(self, cli, key):
		if key == self.cli.config['pokerstars-replayer']['key-button-start']:
			if self.doHandStart(): return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-stop']:
			if self.doHandStop(): return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-next']:
			if self.doHandNext(): return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-prev']:
			if self.doHandPrev(): return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-first']:
			if self.doHandFirst(): return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-last']:
			if self.doHandLast(): return True
		return False	
	
	def handleKeyReleased(self,  cli, key):
		if key == self.cli.config['pokerstars-replayer']['key-button-start']:
			return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-stop']:
			return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-next']:
			return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-prev']:
			return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-first']:
			return True
		elif key == self.cli.config['pokerstars-replayer']['key-button-last']:
			return True
		return False	
		

PokerStarsReplayer.Type = Registry.WindowHandlerMeta.createTypeName(PokerStarsReplayer)
