 

from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import PokerStarsWindowBase

#********************************************************************************************
class PokerStarsPopupNews(PokerStarsWindowBase.PokerStarsWindowBase):
	""""""
	Window = 'PopupNews'
		
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		if klass.psIsPopupNews(cli, hWindow):
			return klass(cli, hWindow)
		return None
	
	def __init__(self, cli, hWindow):
		self.cli = cli
		self.hWindow = hWindow
		if cli.config['pokerstars']['bool-close-popup-news']:
			cli.application.windowManager.windowClose(self.hWindow)
			
		
		