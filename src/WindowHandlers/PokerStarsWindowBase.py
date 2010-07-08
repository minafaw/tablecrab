"""base implementatio for PokerStars windows
""" 
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import re

from . import Registry

#********************************************************************************************
class PokerStarsWindowBase(Registry.WindowHandlerBase):
	"""base class for PokerStars windows"""
	
	Type = None
	Site = None
	Window = None
	
	PsTitleLobby = 'PokerStars Lobby'
	PsClassLobby = '#32770'	# duh, stars. main windows should never be dialogs
	PsClassTable = 'PokerStarsTableFrameClass'
	PsClassNews = '#32770'
	PsTitleNews = 'News'
	PsClassInstantHandHistory = '#32770'
	PsTitleInstantHandHistory = 'Instant Hand History'
	PsTitleTourneyRegistrationMessageBox = 'Tournament Registration'
	PsClassTourneyRegistrationMessageBox = '#32770'
	PsTitleTableMessageBox = 'PokerStars'
	PsClassTableMessageBox = '#32770'
	
	
	#NOTE: not easy to determine if a window is a PokerStarswindow. i don't feel like messing around with psapi.dll to get the exefilename.
	# so ..i use a hack. we identify a window as being a stars window if it (or one of its parents) contains a widget classname.startswith('PokerStars')
	# nasty and errorprone, but the most reasonalbe i could come up with now
	@classmethod
	def _psHasPokerStarsWidgets(klass, cli, hWindow):
		for hWindow in cli.application.windowManager.windowChildren(hWindow):
			if cli.application.windowManager.windowGetClassName(hWindow).startswith('PokerStars'):	return True
		return False
	@classmethod
	def psIsPokerStarsWindow(klass, cli, hWindow):
		while hWindow:
			if klass._psHasPokerStarsWidgets(cli, hWindow): return True
			hWindow = cli.application.windowManager.windowGetParent(hWindow)
		return False	
	
	@classmethod
	def psIsLobby(klass, cli, hWindow):
		if not cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassLobby: return False
		if not cli.application.windowManager.windowGetText(hWindow).startswith(klass.PsTitleLobby): return False
		if not klass.psIsPokerStarsWindow(cli, hWindow): return False
		return False
		
	@classmethod
	def psIsTable(klass, cli, hWindow):
		if not cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassTable: return False
		return True
		
	@classmethod
	def psIsPopupNews(klass, cli, hWindow):
		if not cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassNews: return False
		if not cli.application.windowManager.windowGetText(hWindow) == klass.PsTitleNews: return False
		if not klass.psIsPokerStarsWindow(cli, hWindow): return False
		return True
		
	@classmethod
	def psIsInstantHandHistory(klass, cli, hWindow):
		if not cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassInstantHandHistory: return False
		if not cli.application.windowManager.windowGetText(hWindow) == klass.PsTitleInstantHandHistory: return False
		if not klass.psIsPokerStarsWindow(cli, hWindow): return False
		return True

	@classmethod
	def psIsTourneyRegistrationMessageBox(klass, cli, hWindow):
		if not cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassTourneyRegistrationMessageBox: return False
		if not cli.application.windowManager.windowGetText(hWindow) == klass.PsTitleTourneyRegistrationMessageBox: return False
		if not klass.psIsPokerStarsWindow(cli, hWindow): return False
		return True
	
	@classmethod
	def psIsTableMessageBox(klass, cli, hWindow):
		if not cli.application.windowManager.windowGetClassName(hWindow) == klass.PsClassTableMessageBox: return False
		if not cli.application.windowManager.windowGetText(hWindow) == klass.PsTitleTableMessageBox: return False
		hWindowParent = cli.application.windowManager.windowGetParent(hWindow)
		if not klass.psIsTable(hWindowParent): return False
		return True


