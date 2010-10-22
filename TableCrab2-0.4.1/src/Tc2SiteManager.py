
#NOTE: we can not import Tc2Config here (cross import)

import Tc2Config
import Tc2Win32
import Tc2SiteTableCrab
import Tc2SitePokerStars

from PyQt4 import QtCore
import thread

#****************************************************************************************
#
#**************************************************************************************

class SiteManager(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		self._lock = thread.allocate_lock()

		Tc2Config.windowHook.windowCreated.connect(self.onWindowCreated)
		Tc2Config.windowHook.windowDestroyed.connect(self.onWindowDestroyed)
		Tc2Config.windowHook.windowGainedForeground.connect(self.onWindowGainedForeground)
		Tc2Config.windowHook.windowLostForeground.connect(self.onWindowLostForeground)
		Tc2Config.keyboardHook.inputEvent.connect(self.onInputEvent)
		Tc2Config.mouseHook.inputEvent.connect(self.onInputEvent)

		self._tableCrabActionHandler = Tc2SiteTableCrab.EventHandler(parent=self)
		self._handlers = (
				self._tableCrabActionHandler,	# should always be first item
				Tc2SitePokerStars.EventHandler(parent=self),
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
		if Tc2Config.hotkeyManager is None or Tc2Config.templateManager is None:
			return
		hwnd = Tc2Win32.windowForeground()
		if hwnd:
			for hotkey in Tc2Config.hotkeyManager:
				if not hotkey.key() or hotkey.key() != inputEvent.key:
					continue
				for handler in self._handlers:
					if handler.handleInputEvent(hwnd, hotkey, inputEvent):
						return





