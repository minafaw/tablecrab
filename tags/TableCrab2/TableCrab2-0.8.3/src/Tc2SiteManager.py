
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
		self._tableCrabSiteHandler = Tc2SiteTableCrab.SiteHandler(parent=self)
		self._siteHandlers = [
				self._tableCrabSiteHandler,	# should always be first item
				Tc2SitePokerStars.SiteHandler(parent=self),
				]
		Tc2Config.globalObject.objectCreatedSiteManager.emit(self)
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		globalObject.mouseHook.inputEvent.connect(self.onInputEvent)
		globalObject.keyboardHook.inputEvent.connect(self.onInputEvent)
		globalObject.windowHook.windowCreated.connect(self.onWindowCreated)
		globalObject.windowHook.windowDestroyed.connect(self.onWindowDestroyed)
		globalObject.windowHook.windowGainedForeground.connect(self.onWindowGainedForeground)
		globalObject.windowHook.windowLostForeground.connect(self.onWindowLostForeground)

	def __iter__(self):
		return iter(self._siteHandlers)

	def siteHandler(self, siteName):
		for siteHandler in self._siteHandlers:
			if siteHandler.siteName() == siteName:
				return siteHandler
		return None

	def addSiteHander(self, siteHandler):
		self._siteHandlers.append(siteHandler)

	def onWindowDestroyed(self, hwnd):
		for handler in self._siteHandlers:
			if handler.handleWindowDestroyed(hwnd):
				return

	def onWindowCreated(self, hwnd):
		for handler in self._siteHandlers:
			if handler.handleWindowCreated(hwnd):
				return

	def onWindowGainedForeground(self, hwnd):
		for handler in self._siteHandlers:
			if handler.handleWindowGainedForeground(hwnd):
				return

	def onWindowLostForeground(self, hwnd):
		for handler in self._siteHandlers:
			if handler.handleWindowLostForeground(hwnd):
				return

	def onInputEvent(self, inputEvent):
		if Tc2Config.globalObject.hotkeyManager is None or Tc2Config.globalObject.templateManager is None:
			return
		hwnd = Tc2Win32.windowForeground()
		if hwnd:
			for hotkey in Tc2Config.globalObject.hotkeyManager:
				if not hotkey.key() or hotkey.key() != inputEvent.key:
					continue
				#NOTE: have to stop hooks here so we do not get recursive
				Tc2Config.globalObject.keyboardHook.setEnabled(False)
				Tc2Config.globalObject.mouseHook.setEnabled(False)
				try:
					for handler in self._siteHandlers:
						if handler.handleInputEvent(hwnd, hotkey, inputEvent):
							break
				finally:
					Tc2Config.globalObject.keyboardHook.setEnabled(True)
					Tc2Config.globalObject.mouseHook.setEnabled(True)





