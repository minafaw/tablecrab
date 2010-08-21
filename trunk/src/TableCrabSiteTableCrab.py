"""handler for global actions"""

import TableCrabConfig
import TableCrabHotkeys

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
		if hwnd == self._hwndMain:
			return True
		return False

	def handleWindowDestroyed(self, hwnd):
		if hwnd == self._hwndMain:
			return True
		return False

	def handleWindowGainedForeground(self, hwnd):
		if hwnd == self._hwndMain:
			return True
		return False

	def handleWindowLostForeground(self, hwnd):
		if hwnd == self._hwndMain:
			return True
		return False

	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		if hwnd == self._hwndMain:
			return True
		if hotkey.id() == TableCrabHotkeys.HotkeyScreenshot.id():
			if inputEvent.keyIsDown or inputEvent.mouseSteps:
				TableCrabConfig.widgetScreenshot(hwnd)
				TableCrabConfig.globalObject.feedbackMessage.emit(hotkey.action() )
				inputEvent.accept = True
			return True
		return False
