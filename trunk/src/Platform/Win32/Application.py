from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

from ctypes import *
from ctypes.wintypes import *

user32 = windll.user32

from . import WindowManager
from . import KeyboardManager
from . import MouseManager

#**********************************************************************************************
class Application(object):
	Type = 'Application'
	EvtStart = 'start'
	EvtStop = 'stop'
	
	
	class Win32Consts:
		STATUS_CONTROL_C_EXIT = 0xC000013A
	
	def __init__(self, cb=None):
		self._cb = (lambda *args, **kws: False) if cb is None else cb
		self._isMainloop = False
		self._isStarted = False
		self._postedQuitMessage = False
		
		self.windowManager = WindowManager.WindowManager()
		self.mouseManager = MouseManager.MouseManager()
		self.keyboardManager = KeyboardManager.KeyboardManager()
			
	def setCB(self, cb):
		self._cb = cb
	
	def callCB(self, inst, evt, arg):
		return self._cb(inst, evt, arg)
	
	def isMainloop(self): return self._isMainloop
	def isStarted(self): return self._isStarted
		
	def start(self, isMainloop=True):
		self._isMainloop = isMainloop
		self._postedQuitMessage = False
		self._isStarted = True
		
		self.callCB(self, self.EvtStart, '')
		for o in (self.windowManager, self.mouseManager, self.keyboardManager):
			o.start()
		if not self.isMainloop(): return
			
		# start mainloop
		msg = MSG()
		while True:
					
			# hopefuly we catch all errors here, so we can exit clean, uninstalling our hook
			try:		# CTRL-C will throw an exception here. god knows what else....
				result = user32.GetMessageA(byref(msg), None, 0, 0)
			except WindowsError, d:
				errno = c_ulong(d.winerror).value
				if errno == self.Win32Consts.STATUS_CONTROL_C_EXIT:
					self.callCB(self, self.EvtStop, 'keyboard interrupt')
					self._isMainloop = False
					if not self._postedQuitMessage:
						self.stop()
					break
				else:
					self._isMainloop = False
					self.stop()
					raise WindowsError(d)
			except Exception, d:
				self._isMainloop = False
				self.stop()
				raise Exception(d)
				break
			else:
				if result < 0:	# an error occured, no idea if we ever reach this or if it iscaptured in the try ..except clause
					self._isMainloop = False
					self.stop()
					raise WinError(GetLastError())
				elif result == 0:	# received WM_QUIT
					self._isMainloop = False
					if not self._postedQuitMessage:
						self.stop()
					break
				else:
					user32.TranslateMessage(byref(msg))
					user32.DispatchMessageA(byref(msg))
		self._isStarted = False

	def stop(self):
		if self.isStarted():
			self._isStarted = False
			for o in (self.windowManager, self.mouseManager, self.keyboardManager):
				o.stop()
			if self.isMainloop() and not self._postedQuitMessage:
				self._postedQuitMessage = True
				user32.PostQuitMessage(0)
			self.callCB(self, self.EvtStop, '')
			
			
