"""handler for global actions"""

import Tc2Config
import Tc2ConfigHotkeys
import Tc2Win32
import Tc2GuiToolsCardProtector
from PyQt4 import QtCore

#**********************************************************************************************
#
#**********************************************************************************************
class SiteHandler(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)

		self._hwndMain = None
		self._widgetCardProtector = None
		Tc2Config.globalObject.objectCreatedMainWindow.connect(self.onMainWindowCreated)

	def setHwndMain(self, hwnd):
		self._hwndMain = hwnd

	def handleWindowCreated(self, hwnd):
		if Tc2Win32.windowIsSameProcess(hwnd, self._hwndMain):
			return True
		return False

	def handleWindowDestroyed(self, hwnd):
		if Tc2Win32.windowIsSameProcess(hwnd, self._hwndMain):
			return True
		return False

	def handleWindowGainedForeground(self, hwnd):
		if Tc2Win32.windowIsSameProcess(hwnd, self._hwndMain):
			return True
		return False

	def handleWindowLostForeground(self, hwnd):
		if Tc2Win32.windowIsSameProcess(hwnd, self._hwndMain):
			return True
		return False

	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		if Tc2Win32.windowIsSameProcess(hwnd, self._hwndMain):
			return True
		if hotkey.id() == Tc2ConfigHotkeys.HotkeyScreenshot.id():
			if inputEvent.keyIsDown:
				Tc2Config.widgetScreenshot(hwnd)
				Tc2Config.globalObject.feedbackMessage.emit(hotkey.action() )
			inputEvent.accept = True
			return True
		#TODO: implement hide card protector if card protector has focus. we'd have
		#		to translate Qt keyboard events to input events to do so. too much trouble for now.
		elif hotkey.id() == Tc2ConfigHotkeys.HotkeyCardProtector.id():
			self._widgetCardProtector.handleInputEvent(hwnd, hotkey, inputEvent)
			return True

	def onMainWindowCreated(self, window):
		hwnd = window.effectiveWinId()
		if hwnd is None:
			raise RuntimeError('main window has no valid hwnd')
		self._hwndMain = ( int(hwnd) )

		self._widgetCardProtector = Tc2GuiToolsCardProtector.CardProtector(parent=None)







