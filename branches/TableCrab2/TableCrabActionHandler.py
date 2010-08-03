"""handler for global actions"""


import TableCrabConfig
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
		
	def handleInput(self, hwnd, actionItem, keydown=None, nSteps=None):
		if hwnd == self._hwndMain:
			return True
		if actionItem.itemName() == TableCrabConfig.ActionScreenshot.itemName():
			if keydown is True:
				TableCrabConfig.widgetScreenshot(hwnd)
			return True
		return False
		