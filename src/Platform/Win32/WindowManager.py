"""win32 window manager implementation
"""
import thread, time
from ctypes import *
from ctypes.wintypes import *

user32 = windll.user32
#TDODO:
#    - for compat we should return a default value in all method calls that fail when called with 
#      the desktop window as param. for example user32.GetClassName(None) raises. instead 
#      we should return ""
#
#***********************************************************************************************

class WindowManager(object):
	
	"""win32 keyboard manager implementation
	
	@cvar EvtStart: event triggered when the keyboard manager starts. arg = (str) current keyboard layout name or 'unknown'
	@cvar EvtStop: event triggered when the keyboard manager stops. arg = always None
	@cvar EvtWindowCreated: event triggerered when a new to us window is detected. arg = hWindow
	@cvar EvtWindowDestroyed: event triggerered when a window we keeptrack of is no longer present. arg = hWindow
	@cvar EvtWindowGainForeground: event triggerered when a window we keeptrack gets foreground status. arg = hWindow
	@cvar EvtWindowLooseForeground: event triggerered when a window we keeptrack looses foreground status. arg = hWindow
		
	@warning: this thing is a bit nasty and may break anything. window handles passed to the callback may or may not be valid 
	"""
	
	Type = 'WindowManager'
	EvtStart = 'start'
	EvtStop = 'stop'
	EvtWindowCreated = 'windowCreated'
	EvtWindowDestroyed = 'windowDestroyed'
	EvtWindowLooseForeground = 'windowLooseForeground'
	EvtWindowGainForeground = 'windowGainForeground'
	
	
	class Win32Consts:
		TRUE = 1
		WM_SYSCOMMAND = 274
		WM_GETTEXT = 13
		WM_SETTEXT = 12
		
		SMTO_ABORTIFHUNG = 2
		SC_CLOSE = 61536
		
		SWP_NOSIZE = 1
		SWP_NOMOVE = 2
		SWP_NOZORDER = 4
		SWP_NOACTIVATE = 16
		
		ENUMWINDOWSPROC = WINFUNCTYPE(INT, HANDLE, LPARAM)
		
		MY_TIMEOUT = 0.1
		MY_SMTO_TIMEOUT = 1000
		MY_MAX_CLASS_NAME = 64
		
		BM_CLICK =245
		
		
	def __init__(self, cb=None):
		"""
		@param cb: (function) event handler
		"""
		self._cb = (lambda *args, **kws: False) if cb is None else cb
		self._isStarted = False
		self._windowsMonitored = []
		self._windowForeground = None
			
	def setCB(self, cb):
		"""sets the callback function to be called when an event is triggered
		@param cb: (function)
		@return: None
		"""
		self._cb = cb
	
	def triggerEvent(self, inst, evt, arg):
		"""triggers an event"""
		return self._cb(inst, evt, arg)
	
	def isStarted(self): 
		"""cheks if the window manager is started
		@return: (bool)
		"""
		return self._isStarted
	
	def start(self):
		"""starts the keyboard manager
		@return: None
		"""
		if not self.isStarted():
			self._isStarted = True
			thread.start_new_thread(self._hookProc, ())
			self.triggerEvent(self, self.EvtStart, '')
			
	def stop(self):
		"""stops the window manager
		@return: None
		"""
		if self.isStarted():
			self._isStarted = False
		self.triggerEvent(self, self.EvtStop, '')
		
	#TODO: if we capture an exception here we can not terminate our application,, hread specific???
	def _hookProc(self):
		"""private method, home-brewn window hook implementation"""
		print		#threads and sys.stdout. for some reason we have to print here to get messages through
		
		while self.isStarted():
				
			#self._lock.acquire()
			
			toplevelWindows = self.windowChildren(hwndParent=None)
			for hwnd in self._windowsMonitored[:]:
				if hwnd not in toplevelWindows:
					self._windowsMonitored.remove(hwnd)
					self.triggerEvent(self, self.EvtWindowDestroyed, hwnd)
			for hwnd in toplevelWindows:
				if hwnd not in self._windowsMonitored:
					self.triggerEvent(self, self.EvtWindowCreated, hwnd)
					self._windowsMonitored.append(hwnd)
					
			hwndForeground = user32.GetForegroundWindow()
			if hwndForeground not in self._windowsMonitored: 
				hwndForeground = None
			
			if hwndForeground == self._windowForeground:
				# idle, nothing to do
				pass
			elif hwndForeground not in self._windowsMonitored:
				if self._windowForeground in self._windowsMonitored:
					self.triggerEvent(self, self.EvtWindowLooseForeground, self._windowForeground)
					self.triggerEvent(self, self.EvtWindowGainForeground, hwndForeground)
			else:
				self.triggerEvent(self, self.EvtWindowLooseForeground, self._windowForeground)
				self.triggerEvent(self, self.EvtWindowGainForeground, hwndForeground)
			self._windowForeground = hwndForeground
						
			#self._lock.release()
			time.sleep(self.Win32Consts.MY_TIMEOUT)
			
	def windowForeground(self):
		"""returns the handle of current the foreground window"""
		hwnd = user32.GetForegroundWindow()
		return hwnd if hwnd else None
			
	def windowActive(self):
		"""returns the handle of the currently active window"""
		hwnd = user32.GetActiveWindow()
		return hwnd if hwnd else None
		
	def windowChildren(self, hwndParent=None):
		"""returns a the list of child windows of a window
		@param hwndParent: handle of the window or None to list all toplevel windows
		@return: (list) of windows of the specified parent
		"""
		L= []
		def f(hwnd, lp):
			L.append(hwnd)
			return self.Win32Consts.TRUE
		p = self.Win32Consts.ENUMWINDOWSPROC(f)
		user32.EnumWindows(p, 0) if hwndParent is None else user32.EnumChildWindows(hwndParent, p, 0)
		return L
		
	def windowFindChild(self, hwnd, className):
		"""finds a child window of a window
		@return: hwnd of the child window or None
		@todo: for some reason user32.FindWindowEx() always fails with an "Access Denied" error, so we use our own impl here 
		"""
		for hwnd in self.windowChildren(hwnd):
			if self.windowGetClassName(hwnd) == className:
				return hwnd
		return None
		
	def windowClose(self, hwnd):
		"""closes the specified window
		@param hwnd: handle of the window
		@return: None
		"""
		if not hwnd: raise ValueError('can not close desktop window')
		result = DWORD()
		user32.SendMessageTimeoutW(
				hwnd, 
				self.Win32Consts.WM_SYSCOMMAND, 
				self.Win32Consts.SC_CLOSE, 
				0, 
				self.Win32Consts.SMTO_ABORTIFHUNG, 
				self.Win32Consts.MY_SMTO_TIMEOUT, 
				byref(result)
				)
	
	def windowGetClassName(self, hwnd):
		"""returns the class name of the specified window
		@param hwnd: handle of the window
		@return: (str)
		"""
		if not hwnd: raise ValueError('can not retrieve className of desktop window')
		p = create_unicode_buffer(self.Win32Consts.MY_MAX_CLASS_NAME)
		if not user32.GetClassNameW(hwnd, p, sizeof(p)):
			#NOTE: GetClassName() sometimes fails for some unknown reason, so we return '' here
			return ''
		return p.value
	
	def windowGetClientRect(self, hwnd, toScreen=False):
		"""returns the client rect of the specified window
		@param hwnd: handle of the window
		@param toScreen: if True the client coordiantes are converted to screen coordiantes in the call
		@return: (tuple) (left, top, width, height)
		"""
		if not hwnd: raise ValueError('can not retrieve clientRect of desktop window')
		rc = RECT()
		if not user32.GetClientRect(hwnd, byref(rc)):
			raise WinError(GetLastError())
		if toScreen:
			pt1 = POINT(rc.left, rc.top)
			pt2 = POINT(rc.right, rc.bottom)
			if not user32.ClientToScreen(hwnd, byref(pt1)): raise WinError(GetLastError())
			if not user32.ClientToScreen(hwnd, byref(pt2)): raise WinError(GetLastError())
			rc.left, rc.top = pt1.x, pt1.y
			rc.right, rc.bottom = pt2.x, pt2.y
		return (rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)
		
	def windowGetRect(self, hwnd):
		"""returns the window rect of the specified window
		@param hwnd: handle of the window
		@return: (L{RECT})
		"""
		if not hwnd: raise ValueError('can not set rect of desktop window')
		rc = RECT()
		if not user32.GetWindowRect(hwnd, byref(rc)): raise WinError(GetLastError())
		return (rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)
		
	def windowGetSize(self, hwnd):
		"""returns the size of a window
		@return: (tuple) w, h
		"""
		return self.windowGetRect(hwnd)[2: ]
	
	def windowSetClientSize(self, hwnd, size=None):
		"""adjusts the specified windows size to fit the specified size of the client area
		@param hwnd: handle of the window
		@param size: (tuple) width, height
		@return: None
		"""
		if not hwnd: raise ValueError('can not set clientSize of desktop window')
		rc = self.windowGetRect(hwnd)
		rcCli = self.windowGetClientRect(hwnd, toScreen=False)
		newW = rc[2] - rcCli[2] + size[0]
		newH = rc[3] - rcCli[3] + size[1]
		self.windowSetPosAndSize(hwnd, pos=None, size=(newW, newH) )
			
	def windowGetClientSize(self, hwnd):
		"""returns the size of the client area of a window
		@return: (tuple) w, h
		"""
		return self.windowGetClientRect(hwnd)[2: ]
	
	def windowGetText(self, hwnd):
		"""returns the window title of the specified window
		@param hwnd: handle of the window
		@return: (str)
		"""
		if not hwnd: raise ValueError('can not retrieve text of desktop window')
		n = user32.GetWindowTextLengthW(hwnd)
		if n:		
			result = DWORD()
			p = create_unicode_buffer(n+ 1)
			#
			user32.SendMessageTimeoutW(
					hwnd, 
					self.Win32Consts.WM_GETTEXT, 
					sizeof(p), p, 
					self.Win32Consts.SMTO_ABORTIFHUNG, 
					self.Win32Consts.MY_SMTO_TIMEOUT, 
					byref(result)
					)
			if not p.value:
				user32.GetWindowTextW(hwnd, p, sizeof(p))
			return p.value
		return ''
	
	def windowSetText(self, hwnd, text=''):
		"""returns the window title of the specified window
		@param hwnd: handle of the window
		@todo: we currently send ANSI text only. 
		@return: (str)
		"""
		if not hwnd: raise ValueError('can not set text of desktop window')
		result = DWORD()
		#TODO: user32.IsWindowUnicode(hwnd)
		user32.SendMessageTimeoutA(
				hwnd, 
				self.Win32Consts.WM_SETTEXT, 
				0, 
				text, 
				self.Win32Consts.SMTO_ABORTIFHUNG, 
				self.Win32Consts.MY_SMTO_TIMEOUT, 
				byref(result)
				)
	
	def windowSetPosAndSize(self, hwnd, pos=None, size=None):
		"""sets size and position of the specified windows 
		@param hwnd: handle of the window
		@param pos: (tuple) x, y (in screen coordiantes) or None to leave position unchanged
		@param size: (tuple) width, height or None to leave size unchanged
		@return: None
		"""
		if not hwnd: raise ValueError('can not set posAndSize of desktop window')
		flags = self.Win32Consts.SWP_NOZORDER | self.Win32Consts.SWP_NOACTIVATE
		if pos is None:
			flags |= self.Win32Consts.SWP_NOMOVE
		if size is None:
			flags |= self.Win32Consts.SWP_NOSIZE
		x, y = (0, 0) if pos is None else pos
		w, h = (0, 0) if size is None else size	
		#NOTE: SetWindowPos seems broken in lucid. looks like SetWindowPos always returns 0, doing nothing
		##if not user32.SetWindowPos(hwnd, None, x, y, w, h, flags): raise WinError(GetLastError())
		user32.SetWindowPos(hwnd, None, x, y, w, h, flags)
	
	def windowWalkChildren(self, hwnd=None, report=False):
		"""walks over all child windows of a window
		@param report: (bool) if True report the current recursion level
		@return: if report is True, tuple(level, hwnd) for the next window in turn, else the hwnd in turn
		"""
		def walker(self, hwnd, level=0):
			if hwnd:
				yield level, hwnd if report else hwnd
			children = self.windowChildren(hwnd)
			hwnd=0 if hwnd is None else hwnd
			for child in children:
				if user32.GetParent(child) == hwnd:
					for x in walker(self, child, level +1):
						yield x
		return walker(self, hwnd)
		
	def windowIsVisible(self, hwnd):
		"""checks if a window is visible
		@return: (bool)
		"""
		return bool(user32.IsWindowVisible(hwnd))
		
	def windowClientPointToScreenPoint(self, hwnd, pt):
		"""converts a point in client coordiantes of a window screen coordinates
		@param pt: (tuple) (x, y)
		@return: (tuple) (x, y)
		"""
		pt = POINT(*pt)
		if not user32.ClientToScreen(hwnd, byref(pt)): raise WinError(GetLastError())
		return (pt.x, pt.y) 
		
	def windowScreenPointToClientPoint(self, hwnd, pt):
		"""converts a point in screen coordiantes to point in window client coordinates
		@param pt: (tuple) (x, y)
		@return: (tuple) (x, y)
		"""
		pt = POINT(*pt)
		if not user32.ScreenToClient(hwnd, byref(pt)): raise WinError(GetLastError())
		return (pt.x, pt.y) 
		
	def windowFromPoint(self, pt):
		"""returns the handle of the window at a specified point
		"""
		hwnd = user32.WindowFromPoint(POINT(*pt))
		return hwnd if hwnd else None
	
	def windowGetParent(self, hwnd):
		"""returns the handle of the parent of a window"""
		hwnd = user32.GetParent(hwnd)
		return hwnd if hwnd else None
			
	def windowClickButton(self, hwnd, buttonText):
		for hwnd in self.windowChildren(hwnd):
			if self.windowGetClassName(hwnd) == 'Button':
				if self.windowGetText(hwnd) == buttonText:
					if user32.SendNotifyMessageW(hwnd, self.Win32Consts.BM_CLICK, 0, 0): return True
					break
		return False
		
		
		
		
		
		
		
			
			
