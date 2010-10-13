
#NOTE: we can not import TableCrabConfig here (cross import)

import TableCrabConfig
import TableCrabWin32
import TableCrabSiteTableCrab
import TableCrabSitePokerStars

from PyQt4 import QtCore
import thread

#****************************************************************************************
#
#**************************************************************************************

class SiteManager(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		self._lock = thread.allocate_lock()

		TableCrabConfig.windowHook.windowCreated.connect(self.onWindowCreated)
		TableCrabConfig.windowHook.windowDestroyed.connect(self.onWindowDestroyed)
		TableCrabConfig.windowHook.windowGainedForeground.connect(self.onWindowGainedForeground)
		TableCrabConfig.windowHook.windowLostForeground.connect(self.onWindowLostForeground)
		TableCrabConfig.keyboardHook.inputEvent.connect(self.onInputEvent)
		TableCrabConfig.mouseHook.inputEvent.connect(self.onInputEvent)

		self._tableCrabActionHandler = TableCrabSiteTableCrab.EventHandler(parent=self)
		self._handlers = (
				self._tableCrabActionHandler,	# should always be first item
				TableCrabSitePokerStars.EventHandler(parent=self),
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
				if not hotkey.key() or hotkey.key() != inputEvent.key:
					continue
				for handler in self._handlers:
					if handler.handleInputEvent(hwnd, hotkey, inputEvent):
						return





