
#NOTE: we can not import TableCrabConfig here (cross import)

import TableCrabConfig
import TableCrabWin32
import TableCrabActionHandler
import TableCrabPokerStars

from PyQt4 import QtCore
import thread

#****************************************************************************************
#
#**************************************************************************************

class SiteManager(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		self._lock = thread.allocate_lock()
		
		TableCrabConfig.mouseHook.setEventHandler(self)
		TableCrabConfig.keyboardHook.setEventHandler(self)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowCreated(int)', self.onWindowCreated)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowDestroyed(int)', self.onWindowDestroyed)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowGainedForeground(int)', self.onWindowGainedForeground)
		TableCrabConfig.signalConnect(TableCrabConfig.windowHook, self, 'windowLostForeground(int)', self.onWindowLostForeground)
		TableCrabConfig.signalConnect(TableCrabConfig.keyboardHook, self, 'inputEvent(QObject*)', self.onInputEvent)
		TableCrabConfig.signalConnect(TableCrabConfig.mouseHook, self, 'inputEvent(QObject*)', self.onInputEvent)
		
		self._tableCrabActionHandler = TableCrabActionHandler.ActionHandler(parent=self)
		self._handlers = (
				self._tableCrabActionHandler,	# should always be first item
				TableCrabPokerStars.ActionHandler(parent=self),
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
		
	def onInputEvent(self, inputEvent):
		if TableCrabConfig.hotkeyManager is None or TableCrabConfig.templateManager is None:
			return
		hwnd = TableCrabWin32.windowForeground()
		if hwnd:
			for hotkey in TableCrabConfig.hotkeyManager:
				if not hotkey.hotkey() or hotkey.hotkey() != inputEvent.key: 
					continue
				for handler in self._handlers:
					if handler.handleInputEvent(hwnd, hotkey, inputEvent):
						return
						
						



