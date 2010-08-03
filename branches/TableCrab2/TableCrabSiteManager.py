
#NOTE: we can not import TableCrabConfig here (cross import)

import TableCrabConfig
import TableCrabWin32
import TableCrabActionHandler
import TableCrabPokerStars

from PyQt4 import QtCore
#****************************************************************************************
#
#**************************************************************************************

class SiteManager(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		
		TableCrabConfig.mouseHook.setEventHandler(self)
		TableCrabConfig.keyboardHook.setEventHandler(self)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowCreated(int)', self.onWindowCreated)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowDestroyed(int)', self.onWindowDestroyed)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowGainedForeground(int)', self.onWindowGainedForeground)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowLostForeground(int)', self.onWindowLostForeground)
		
		self._tableCrabActionHandler = TableCrabActionHandler.ActionHandler()
		self._handlers = (
				self._tableCrabActionHandler,	# should always be first item
				TableCrabPokerStars.ActionHandler(),
				)
			
	def tableCrabActionHandler(self):
		return self._tableCrabActionHandler
		
	def onWindowDestroyed(self, hwnd):
		for handler in self._handlers:
			if handler.handleWindowDestroyed(hwnd):
				return
	
	def onWindowCreated(self, hwnd):
		for handler in self._handlers:
			if handler.handleWindowCreated(hwnd):
				return
		
	def onWindowGainedForeground(self, hwnd):
		for handler in self._handlers:
			if handler.handleWindowGainedForeground(hwnd):
				return
	
	def onWindowLostForeground(self, hwnd):
		for handler in self._handlers:
			if handler.handleWindowLostForeground(hwnd):
				return
	
	def handleInput(self, input, keydown=None, nSteps=None):
		hwnd = TableCrabWin32.windowForeground()
		if hwnd:
			for actionItem in TableCrabConfig.actionManager.items():
				if not actionItem.hotkey or actionItem.hotkey != input: 
					continue
				for handler in self._handlers:
					if handler.handleInput(hwnd, actionItem, keydown=keydown, nSteps=nSteps):
						return True
		return False
		
		


