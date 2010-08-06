"""handler for global actions"""


import TableCrabConfig
import TableCrabHotkeys

#**********************************************************************************************
#
#**********************************************************************************************

class ActionHandler(object):
	def __init__(self):
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
				inputEvent.accept = True
			return True
		return False
		