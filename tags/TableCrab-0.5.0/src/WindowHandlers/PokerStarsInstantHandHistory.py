"""window handler for PokerStars instant hand history
""" 
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import Registry
from . import PokerStarsWindowBase

#********************************************************************************************

class PokerStarsInstantHandHistory(PokerStarsWindowBase.PokerStarsWindowBase):
	"""PokerStars table implementation"""
	Type = Registry.WindowHandlerType
	Site = 'PokerStars'
	Window = 'InstantHandHistory'
	
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		if klass.psIsInstantHandHistory(cli, hWindow):
			return klass(cli, hWindow)
		return None
		
	def __init__(self, cli, hWindow):
		self.cli = cli
		self.hWindow = hWindow
		self.cli.log(self, 'created hWindow="%s" title="%s"' % (self.hWindow, self.cli.application.windowManager.windowGetText(self.hWindow)) )
		
	def handleWindowDestroyed(self, cli, hWindow):
		return False
	
	def handleWindowGainForeground(self, cli, hWindow):
		return False
	
	def handleWindowLooseForeground(self, cli, hWindow):
		return False
	
	def handleKeyPressed(self, cli, key):
		return False
	
	def handleKeyReleased(self, cli, key):
		return False

	