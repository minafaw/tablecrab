"""win32 application implementation
"""
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
	"""win32 application implementation
	
	@cvar EvtStart: event triggered when the application starts. arg = always None
	@cvar EvtStop: event triggered when the application stops. arg = reason or None
	"""
	Type = 'Application'
	EvtStart = 'start'
	EvtStop = 'stop'
	
	
	class Win32Consts:
		STATUS_CONTROL_C_EXIT = 0xC000013A
	
	def __init__(self, cb=None):
		"""
		@param cb: (function) to be called when an event occurs. the function should take two arguments: Evt*, arg
		"""
		self._cb = (lambda *args, **kws: False) if cb is None else cb
		self._isMainloop = False
		self._isStarted = False
		self._postedQuitMessage = False
		
		self.windowManager = WindowManager.WindowManager()
		self.mouseManager = MouseManager.MouseManager()
		self.keyboardManager = KeyboardManager.KeyboardManager()
			
	def setCB(self, cb):
		"""sets the callback function
		@param cb: (function)
		@return: None
		"""
		self._cb = cb
	
	def triggerEvent(self, inst, evt, arg):
		"""triggers an event"""
		return self._cb(inst, evt, arg)
	
	def isMainloop(self): 
		"""cheks if the application runs a mainloop
		@return: (bool)
		"""
		return self._isMainloop
	def isStarted(self): 
		"""cheks if the application is started
		@return: (bool)
		"""
		return self._isStarted
		
	def start(self, isMainloop=True):
		"""starts the application
		@param isMainloop: (bool) if True a message pump is started, if False you have to run your own message pump
		"""
		self._isMainloop = isMainloop
		self._postedQuitMessage = False
		self._isStarted = True
		
		self.triggerEvent(self, self.EvtStart, '')
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
					self.triggerEvent(self, self.EvtStop, 'keyboard interrupt')
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
		"""stops the application. if L{isMainloop} is True the application is terminated"""
		if self.isStarted():
			self._isStarted = False
			for o in (self.windowManager, self.mouseManager, self.keyboardManager):
				o.stop()
			if self.isMainloop() and not self._postedQuitMessage:
				self._postedQuitMessage = True
				user32.PostQuitMessage(0)
			self.triggerEvent(self, self.EvtStop, '')
			
			
