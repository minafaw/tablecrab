
from PyQt4 import QtCore

import Config, Window
import GuiHotkeys

#**********************************************************************************
#
#**********************************************************************************

class SiteManager(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		Config.registerGlobalObject(self, Config.GlobalObjectSiteManager)
		
	def start(self):
		pass
	
	def stop(self):
		pass
	def handleInput(self, input, keydown=None, nSteps=None):
		hwnd = Window.windowForeground()
		if not hwnd:
			return False
			
		
		#if windowIsPokerStarsPopupNews(hwnd):
		#	if Config.value('PokerStars/AutoClosePopupNews', False).toBool():
				
		#		return 
			
		
		
		for action in Config.hotkeyManager:
			#print hotkey.hotkey, input
			if action.hotkey == input:
				if action.actionName() == GuiHotkeys.ActionScreenshot.actionName():
					if not keydown or nSteps is not None:
						Config.globalObject(Config.GlobalObjectScreenshot).takeScreenshot(hwnd)
					return True
				elif action.actionName() == GuiHotkeys.ActionWindowInfo.actionName():
					
					return Trues
		
		
		return False
		
	# PokerStars	
	#-----------------------------------------------------------------------------------------
	#NOTE: not easy to determine if a window is a PokerStarswindow. i don't feel like messing around with psapi.dll to get the exefilename.
	# so ..i use a hack. we identify a window as being a stars window if it (or one of its parents) contains a widget classname.startswith('PokerStars')
	# nasty and errorprone, but the most reasonalbe i could come up with now
	def windowHasPokerStarsWidgets(self, hWindow):
		for hWindow in Window.windowChildren(hWindow):
			if Window.windowGetClassName(hWindow).startswith('PokerStars'):	return True
		return False
	
	def windowIsPokerStarsWindow(self, hWindow):
		while hWindow:
			if self.windowHasPokerStarsWidgets(cli, hWindow): return True
			hWindow = Window.windowGetParent(hWindow)
		return False	
	
	PsTitleLobby = 'PokerStars Lobby'
	PsClassLobby = '#32770'	# duh, stars. main windows should never be dialogs
	def windowIsPokerStarsLobby(self, hWindow):
		if not window.windowGetClassName(hWindow) == self.PsClassLobby: return False
		if not window.windowGetText(hWindow).startswith(self.PsTitleLobby): return False
		if not self.psIsPokerStarsWindow(hWindow): return False
		return False
		
	PsClassTable = 'PokerStarsTableFrameClass'
	def windowIsPokerStarsTable(self, hWindow):
		if not cWindow.windowGetClassName(hWindow) == klass.PsClassTable: return False
		return True	

	PsClassInstantHandHistory = '#32770'
	PsTitleInstantHandHistory = 'Instant Hand History'
	def windowIsPokerStarsInstantHandHistory(self, hWindow):
		if not cWindow.windowGetClassName(hWindow) == self.PsClassInstantHandHistory: return False
		if not Window.windowGetText(hWindow) == self.PsTitleInstantHandHistory: return False
		if not self.windowIsPokerStarsWindow(hWindow): return False
		return True
		
	PsClassNews = '#32770'
	PsTitleNews = 'News'
	def windowIsPokerStarsPopupNews(self, hWindow):
		if not Window.windowGetClassName(hWindow) == self.PsClassNews: return False
		if not cWindow.windowGetText(hWindow) == self.PsTitleNews: return False
		if not self.windowIsPokerStarsWindow(hWindow): return False
		return True
		
	PsTitleTourneyRegistrationMessageBox = 'Tournament Registration'
	PsClassTourneyRegistrationMessageBox = '#32770'
	def IsPokerStarsTourneyRegistrationMessageBox(self, hWindow):
		if not Window.windowGetClassName(hWindow) == self.PsClassTourneyRegistrationMessageBox: return False
		if not Window.windowGetText(hWindow) == self.PsTitleTourneyRegistrationMessageBox: return False
		if not self.windowIsPokerStarsWindow(hWindow): return False
		return True

	def windowIsPokerStarsTableMessageBox(self, hWindow):
		if not cWindow.windowGetClassName(hWindow) == self.PsClassTableMessageBox: return False
		if not Window.windowGetText(hWindow) == self.PsTitleTableMessageBox: return False
		hWindowParent = Window.windowGetParent(hWindow)
		if not self.windowIsPokerStarsTable(hWindowParent): return False
		return True


