"""handler for global actions"""

import Tc2Config
import Tc2ConfigHotkeys
import Tc2Win32

from PyQt4 import QtCore

#**********************************************************************************************
#
#**********************************************************************************************
class EventHandler(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)

		self._hwndMain = None

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
			if inputEvent.keyIsDown or inputEvent.steps:
				Tc2Config.widgetScreenshot(hwnd)
				Tc2Config.globalObject.feedbackMessage.emit(hotkey.action() )
				inputEvent.accept = True
			return True
		return False
