 
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import Registry

#********************************************************************************************
class PokerStarsWindowBase(Registry.WindowHandlerBase):
	"""base class for PokerStars windows"""
	
	Type = Registry.WindowHandlerType
	Site = 'PokerStars'
	Window = None
	
	PsTitleLobby = 'PokerStars Lobby'
	PsClassTable = 'PokerStarsTableFrameClass'
	PsClassNews = '#32770'
	PsTitleNews = 'News'
	
	@classmethod
	def psIsTable(klass, cli, hWindow):
		if cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassTable:
			return True
		return False
		
	@classmethod
	def psIsPopupNews(klass, cli, hWindow):
		if cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassNews and \
							cli.application.windowManager.windowGetText(hWindow) == klass.PsTitleNews:
			hWindowParent = cli.application.windowManager.windowGetParent(hWindow)
			if hWindowParent and cli.application.windowManager.windowGetText(hWindowParent).startswith(klass.PsTitleLobby):
				return True
		return False
	
	