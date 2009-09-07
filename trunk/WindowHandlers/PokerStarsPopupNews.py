 

from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import Registry

#********************************************************************************************
class PokerStarsPopupNews(Registry.WindowHandlerBase):
	"""fallback window handler if no handler is present for a window"""
	Type = Registry.WindowHandlerType
	Site = 'PokerStars'
	Window = 'PopupNews'
	
	PsTitleLobby = 'PokerStars Lobby'
	PsClassNews = '#32770'
	PsTitleNews = 'News'
	
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		if cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassNews and \
							cli.application.windowManager.windowGetText(hWindow) == klass.PsTitleNews:
			hWindowParent = cli.application.windowManager.windowGetParent(hWindow)
			if hWindowParent and cli.application.windowManager.windowGetText(hWindowParent).startswith(klass.PsTitleLobby):
				return klass(cli, hWindow)
		return None
	
	def __init__(self, cli, hWindow):
		self.cli = cli
		self.hWindow = hWindow
		if cli.config['pokerstars']['bool-close-popup-news']:
			cli.application.windowManager.windowClose(hWindow)
			
		
		