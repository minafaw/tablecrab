
import time

from ctypes import *
from ctypes.wintypes import *
LRESULT = c_ulong

user32 = windll.user32
kernel32 = windll.kernel32
#***********************************************************************************************

class MouseManager(object):
	Type = 'MouseManager'
	EvtStart = 'start'
	EvtStop = 'stop'
	EvtMouseButtonUp = 'mouseButtonUp'
	EvtMouseButtonDown = 'mouseButtonDown'
	
	ButtonLeft = 'left'
	ButtonRight = 'right'
	ButtonMiddle = 'middle'
	
	class Win32Consts:
		TRUE = 1
		MOUSEHOOKPROCLL = WINFUNCTYPE(LRESULT, c_int, WPARAM, LPARAM)
		
		WH_MOUSE_LL = 14
		HC_ACTION = 0
		
		WM_LBUTTONDOWN = 513
		WM_LBUTTONUP = 514
		WM_RBUTTONDOWN = 516
		WM_RBUTTONUP = 517
		WM_MBUTTONDOWN = 519
		WM_MBUTTONUP = 520
		
		MOUSEEVENTF_MOVE = 1
		MOUSEEVENTF_LEFTDOWN = 2
		MOUSEEVENTF_LEFTUP = 4
		MOUSEEVENTF_RIGHTDOWN = 8
		MOUSEEVENTF_RIGHTUP = 16
		MOUSEEVENTF_MIDDLEDOWN = 32
		MOUSEEVENTF_MIDDLEUP = 64
		MOUSEEVENTF_WHEEL = 0x0800
		MOUSEEVENTF_ABSOLUTE = 32768
				
		
	def __init__(self, cb=None):
		self._cb = (lambda *args, **kws: False) if cb is None else cb
		self._isStarted = False
		self._hHook = None
		self._pHookProc = self.Win32Consts.MOUSEHOOKPROCLL(self._hookProc)
		self._mouseButtonsDown = []
		
	def _hookProc(self, code, wParam, lParam):
		
		if code == self.Win32Consts.HC_ACTION:
						
			button = evt = None
			if wParam == self.Win32Consts.WM_LBUTTONDOWN:
				button = self.ButtonLeft
				evt = self.EvtMouseButtonDown
			elif wParam == self.Win32Consts.WM_RBUTTONDOWN:
				button = self.ButtonRight
				evt = self.EvtMouseButtonDown
			elif wParam == self.Win32Consts.WM_MBUTTONDOWN:
				button = self.ButtonMiddle
				evt = self.EvtMouseButtonDown
			elif wParam == self.Win32Consts.WM_LBUTTONUP:
				button = self.ButtonLeft
				evt = self.EvtMouseButtonUp
			elif wParam == self.Win32Consts.WM_RBUTTONUP:
				button = self.ButtonRight
				evt = self.EvtMouseButtonUp
			elif wParam == self.Win32Consts.WM_MBUTTONUP:
				button = self.ButtonMiddle
				evt = self.EvtMouseButtonUp
			
			if evt is not None:
				if evt == self.EvtMouseButtonUp:
					if button in self._mouseButtonsDown:
						self._mouseButtonsDown.remove(button)
				else:
					if button not in self._mouseButtonsDown:
						self._mouseButtonsDown.append(button)
				result = self.callCB(self, evt, button)
				if result:
					return self.Win32Consts.TRUE
		return user32.CallNextHookEx(self._hHook, code, wParam, lParam)
	
	def setCB(self, cb):
		self._cb = cb
	
	def callCB(self, inst, evt, arg):
		return self._cb(inst, evt, arg)
		
	def isStarted(self): return self._isStarted
	
	def start(self):
		if self._hHook is None:
			self._hHook = user32.SetWindowsHookExW(
				self.Win32Consts.WH_MOUSE_LL, 
				self._pHookProc, 
				kernel32.GetModuleHandleA(None), 
				0
				)
			if not self._hHook:
				self._hHook = None
				raise WindowsError(GetLastError())
		self.callCB(self, self.EvtStart, '')	
		
	def stop(self):
		if self._hHook is not None:
			hHook, self._hHook = self._hHook, None
			if not user32.UnhookWindowsHookEx(hHook):
				raise WindowsError(GetLastError())
		self.callCB(self, self.EvtStop, '')	
		
	def mouseGetButtonsDown(self):
		"""returns list of mouse buttons currently down
		@return: (list) L{Consts}.BUTTON_*
		@note: we can not determine mouse buttons down when we start, so the list may not reflect
		the actual state if mouse buttons are initially down
		"""
		return self._mouseButtonsDown[:]
	
	
	def mousePressButton(self, button):
		"""presses the specified mouse button at the current mouse position
		@param button: (L{Consts}.BUTTON_*)
		"""
		# determine button to set down
		if button in self._mouseButtonsDown: return
		
		if button == self.ButtonLeft:
			bt = self.Win32Consts.MOUSEEVENTF_LEFTDOWN
		elif button == self.ButtonRight:
			bt = self.Win32Consts.MOUSEEVENTF_RIGHTDOWN
		elif button == self.ButtonMiddle:
			bt = self.Win32Consts.MOUSEEVENTF_MIDDLEDOWN
		else:
			raise ValueError('no such mouse button: %s' % button) 
		pt = self.mouseGetPos()
		user32.mouse_event(bt | self.Win32Consts.MOUSEEVENTF_ABSOLUTE, pt[0], pt[1], 0, None)
		
	def mouseReleaseButton(self, button):
		"""releases the specified mouse button at the current mouse position
		@param button: (L{Consts}.BUTTON_*)
		"""
		# determine button to set up
		if button not in self._mouseButtonsDown: return
		
		if button == self.ButtonLeft:
			bt = self.Win32Consts.MOUSEEVENTF_LEFTUP
		elif button == self.ButtonRight:
			bt = self.Win32Consts.MOUSEEVENTF_RIGHTUP
		elif button == self.ButtonMiddle:
			bt = self.Win32Consts.MOUSEEVENTF_MIDDLEUP
		else:
			raise ValueError('no such mouse button: %s' % button) 
		pt = self.mouseGetPos()
		user32.mouse_event(bt | self.Win32Consts.MOUSEEVENTF_ABSOLUTE, pt[0], pt[1], 0, None)	
	
	def mouseClickPoint(self, button, nClicks=1, pt=None):
		'''clicks a point with the desired mouse button
		@param button: (str) button to click: L{Consts}.BUTTON_*
		@param nClicks: (int) number of times to click (2 for a double-click)
		@param pt: (tuple) absolute coordinates to click. if None, the current cursor pos is taken
		@return: None	
		@todo: impl proper double click delay. GetSystemMetrics could do the trick if there is something like a min-double-click-interval defined
		@NOTE: the mouse is moved to the specified position in the call
		'''
		if self._mouseButtonsDown: return
		
		# move mouse to point
		if pt is not None:
			self.mouseSetPos(pt)
		
		# click button
		rng = list(range(nClicks))
		while rng:
			rng.pop()
			self.mousePressButton(button)
			self.mouseReleaseButton(button)
			if rng:
				time.sleep(0.1)

	def mouseClickLeft(self, pt):
		return self.mouseClickPoint(self.ButtonLeft, pt=pt, nClicks=1)
	def mouseClickLeftDouble(self, pt):
		return self.mouseClickPoint(self.ButtonLeft, pt=pt, nClicks=2)
	def mouseClickRight(self, pt):
		return self.mouseClickPoint(self.ButtonRight, pt=pt, nClicks=1)
	def mouseClickRightDouble(self, pt):
		return self.mouseClickPoint(self.ButtonRight, pt=pt, nClicks=2)
	def mouseClickMiddle(self, pt):
		return self.mouseClickPoint(self.ButtonMiddle, pt=pt, nClicks=1)
	def mouseClickMiddleDouble(self, pt):
		return self.mouseClickPoint(self.ButtonMiddle, pt=pt, nClicks=2)
	
	
	def mouseGetPos(self):
		'''returns the current position of the mouse pointer
		@param hwnd: if specified, returns the point in client coordinates of the window
		@return: (tuple) coordinates of the mouse cursor
		'''
		pt = POINT()
		if not user32.GetCursorPos(byref(pt)): raise WinError(GetLastError())
		return (pt.x, pt.y)

	def mouseSetPos(self, pt):
		"""moves the mouse pointer to the specified position
		@param pt: (tuple) point containing the coordiantes to move the mouse pointer to (in screen coordiantes)
		"""
		#NOTE: for some reason neither user32.mouse_event() not user32.SendInput() have any effect here (linux/wine).
		#           the only way i can get this to work is to move the cursor stepwise to its destination?!?
		step = 4
		ptX, ptY = pt
		curX, curY = self.mouseGetPos()
		pt = POINT()
		while curX != ptX or curY != ptY:
			if curX < ptX: 
				curX += step
				if curX > ptX: curX = ptX
			elif curX == ptX: pass
			else: 
				curX -= step
				if curX < ptX: curX = ptX
			if curY < ptY: 
				curY += step
				if curY > ptY: curY = ptY
			elif curY == ptY: pass
			else: 
				curY -= step
				if curY < ptY: curY = ptY
			pt.x, pt.y = curX, curY
			if not user32.SetCursorPos(pt): raise WinError(GetLastError()) 
