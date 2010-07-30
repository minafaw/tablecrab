
#****************************************************************************************
# setup minimal stuff to get at least some information in case something goes wrong
#
# every module should add this module as the very first import
#
#NOTE: if an exception occurs an error.log will be placed in the current directory. good or not?
#***************************************************************************************
import sys, os, traceback, logging
from logging import handlers

TableCrabApplicationName = 'TableCrab2'
TableCrabVersion = '0.1.0'
TableCrabReleaseName = '%s-%s' % (TableCrabApplicationName, TableCrabVersion)
TableCrabAuthor = 'JuergenUrner'
TableCrabErrorLogName = TableCrabApplicationName + '-Error.log'

logger = logging.getLogger(TableCrabApplicationName)
logger.addHandler(handlers.RotatingFileHandler(
		os.path.join(os.getcwd(), TableCrabErrorLogName),
		mode='a',
		maxBytes=32000,
		backupCount=0,
		))
def _excepthook(type, value, tb):
	# as failsave as possible
	p = ''
	p += 'TableCrab: %s\n' % TableCrabReleaseName
	p += 'Platform: %s\n' % sys.platform
	p += 'PythonVersion: %s\n' % sys.version.split()[0]
	try:
		from PyQt4.QtCore import qVersion, PYQT_VERSION_STR
		p += 'QtVersion: %s\n' % qVersion()
		p += 'PyQtVersion: %s\n' % PYQT_VERSION_STR
	except:
		p += 'QtVersion: Unknown\n'
		p += 'PyQtVersion: Unknown\n'
	try:
		import sipconfig
		p += 'SipVersion: %s\n' % sipconfig.Configuration().sip_version_str
	except:
		p += 'SipVersion: Unknown\n'
	try:
		signalEmit(None, 'feedbackException()')
	except: pass
	p += ''.join(traceback.format_exception(type, value, tb))
	try:	# try to log
		logger.critical(p)
	except:	# no success ..write to console
		print p
	
	raise type(value)
sys.excepthook = _excepthook

#************************************************************************************
#
#************************************************************************************
import posixpath, thread, time, re
from PyQt4 import QtCore, QtGui, QtWebKit

import TableCrabWin32
from TableCrabRes import Pixmaps, HtmlPages, StyleSheets

#***********************************************************************************
# global QSettings
#***********************************************************************************
configKey = ''		# for testing. set this to save settings to a different key
def settingsKeyJoin(*keys):
	keys = [(str(key) if isinstance(key, QtCore.QString) else key) for key in keys]
	return QtCore.QString( posixpath.join(*keys) )

_qSettings = QtCore.QSettings(TableCrabAuthor, TableCrabApplicationName)
def settingsValue(key, default):
	return _qSettings.value( settingsKeyJoin(configKey, key), default)
def settingsSetValue(key, value):
	_qSettings.setValue( settingsKeyJoin(configKey, key), QtCore.QVariant(value) )
def settingsRemoveKey(key):
	key = settingsKeyJoin(configKey, key)
	#TODO: for some reason QSettings.contains(key) always return false here even if the key exists 
	##print key, _qSettings.contains(key)
	#if _qSettings.contains(key):
	_qSettings.remove(key)
	
#***********************************************************************************
# global singal handling and messages
#***********************************************************************************
# global signal  'closeEvent(QEvent*)'
# global signal 'feedbackMessage(QString)'
# global signal 'feedbackException()'
# global signal 'widgetScreenshot(int, QPixmap*)'
# global signal 'widgetScreenshotSet(QPixmap*)'
# global signal 'widgetScreenshotDoubleClicked(QPixmap*, QPoint*)'
# global signal 'widgetScreenshotQuery()'
# global signal 'settingAlternatingRowColorsChanged(bool)'
# global signal 'settingChildItemIndicatorsChanged(bool)'
#
_qObject = QtCore.QObject()
def signalEmit(sender, signal, *params):
	if sender is None: _qObject.emit(QtCore.SIGNAL(signal), *params)
	else: sender.emit(QtCore.SIGNAL(signal), *params)
def signalConnect(sender, receiver, signal, slot):
	if sender is None: receiver.connect(_qObject, QtCore.SIGNAL(signal), slot)
	else: receiver.connect(sender, QtCore.SIGNAL(signal), slot)

#***********************************************************************************
# global help resources
#***********************************************************************************
def helpUrl(name):
	fileName = os.path.join(DirHelp, name + '.html')
	if not os.path.isfile(fileName):
		raise ValueError('no such help page')
	return QtCore.QUrl(fileName)

#***********************************************************************************
# global window methods
#***********************************************************************************
def widgetScreenshot(hwnd):
	pixmap = QtGui.QPixmap.grabWindow(hwnd, 0, 0, -1,-1)
	signalEmit(None, 'widgetScreenshot(int, QPixmap*)', hwnd, pixmap)

class _WindowForegroundHook(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)		
		self._lastWindowForeground = 0
		self._isStarted = False
	def lastWindowForeground(self):
		return self._lastWindowForeground
	def start(self):
		if not self._isStarted:
			self._isStarted = True
			thread.start_new_thread(self._hookProc, ())
		return self
	def stop(self):
		self._isStarted = False
	def isStarted(self): 
		return self._isStarted
	def _hookProc(self):
		while self._isStarted:
			hwnd = TableCrabWin32.user32.GetForegroundWindow()
			if hwnd != self._lastWindowForeground:
				self.emit(QtCore.SIGNAL('windowGainedForeground(int)'), hwnd)
				self._lastWindowForeground = hwnd
			time.sleep( settingsValue('WindowForegroundHook/Timeout', 0.3).toInt()[0] )

windowForegroundHook = _WindowForegroundHook()

class _WindowHook(QtCore.QObject):
	Timeout = 0.2
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)		
		self._isRunning = False
		self._hwndForeground = 0
		self._hwnds = []
	def stop(self):
		self._isStarted = False
	def start(self):
		if self._isRunning: raise ValueError('window hook already started')
		self._isRunning = True
		self._run()
	def _run(self):
		hwnds = [hwnd for hwnd in windowChildren(None)]
		hwndsDestroyed = [hwnd for hwnd in self._hwnds if hwnd not in hwnds]
		hwndsCreated = [hwnd for hwnd in hwnds if hwnd not in self._hwnds]
		self._hwnds = hwnds
		for hwnd in hwndsDestroyed:
			signalEmit(self, 'windowDestroyed(int)', hwnd)
		for hwnd in hwndsCreated:
			signalEmit(self, 'windowCreated(int)', hwnd)
		hwnd = windowForeground()
		if hwnd in self._hwnds and hwnd != self._hwndForeground:
			signalEmit(self, 'windowGainedForeground(int)', hwnd)
			self._hwndForeground = hwnd
		if self._isRunning:
			timer = QtCore.QTimer(self)
			timer.setSingleShot(True)
			timer.setInterval(self.Timeout * 1000)
			signalConnect(timer, self, 'timeout()', self._run)
			timer.start()
			#QtCore.QTimer.singleShot(
			#		self.Timeout * 1000, 
			#		self._run
			#		)

windowHook = _WindowHook()


def windowChildren(hwndParent=None):
	"""returns a the list of child windows of a window
	@param hwndParent: handle of the window or None to list all toplevel windows
	@return: (list) of windows of the specified parent
	"""
	L= []
	def f(hwnd, lp):
		L.append(hwnd)
		return TableCrabWin32.TRUE
	p = TableCrabWin32.ENUMWINDOWSPROC(f)
	TableCrabWin32.user32.EnumWindows(p, 0) if not hwndParent else TableCrabWin32.user32.EnumChildWindows(hwndParent, p, 0)
	return L

def windowWalkChildren(hwnd=None, report=False):
	"""walks over all child windows of a window
	@param report: (bool) if True report the current recursion level
	@return: if report is True, tuple(level, hwnd) for the next window in turn, else the hwnd in turn
	"""
	def walker(hwnd, level=0):
		if hwnd:
			yield level, hwnd if report else hwnd
		children = windowChildren(hwnd)
		hwnd=0 if hwnd is None else hwnd
		for child in children:
			if TableCrabWin32.user32.GetParent(child) == hwnd:
				for x in walker(child, level +1):
					yield x
	return walker(hwnd)

def windowGetText(hwnd):
	"""returns the window title of the specified window
	@param hwnd: handle of the window
	@return: (str)
	"""
	if not hwnd: return ''
	n = TableCrabWin32.user32.GetWindowTextLengthW(hwnd)
	if n:		
		result = TableCrabWin32.DWORD()
		p = TableCrabWin32.create_unicode_buffer(n+ 1)
		#
		TableCrabWin32.user32.SendMessageTimeoutW(
				hwnd, 
				TableCrabWin32.WM_GETTEXT, 
				TableCrabWin32.sizeof(p), 
				p, 
				TableCrabWin32.SMTO_ABORTIFHUNG, 
				TableCrabWin32.MY_SMTO_TIMEOUT, 
				TableCrabWin32.byref(result)
				)
		if not p.value:
			TableCrabWin32.user32.GetWindowTextW(hwnd, p, TableCrabWin32.sizeof(p))
		return p.value
	return ''

def windowGetClassName(hwnd):
	"""returns the class name of the specified window
	@param hwnd: handle of the window
	@return: (str)
	"""
	if not hwnd: return ''
	p = TableCrabWin32.create_unicode_buffer(TableCrabWin32.MY_MAX_CLASS_NAME)
	if not TableCrabWin32.user32.GetClassNameW(hwnd, p, TableCrabWin32.sizeof(p)):
		#NOTE: GetClassName() sometimes fails for some unknown reason, so we return '' here
		return ''
	return p.value

def windowGetRect(hwnd):
	"""returns the window rect of the specified window
	@param hwnd: handle of the window
	@return: (L{RECT})
	"""
	if not hwnd: return (-1, -1, -1, -1)
	rc = TableCrabWin32.RECT()
	TableCrabWin32.user32.GetWindowRect(hwnd, TableCrabWin32.byref(rc))
	return (rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)

def windowGetClientRect(hwnd):
	"""returns the window rect of the specified window
	@param hwnd: handle of the window
	@return: (L{RECT})
	"""
	if not hwnd: return (-1, -1, -1, -1)
	rc = TableCrabWin32.RECT()
	TableCrabWin32.user32.GetClientRect(hwnd, TableCrabWin32.byref(rc))
	return (rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)

def windowGetParent(hwnd):
	return TableCrabWin32.user32.GetParent(hwnd)

def windowGetTopLevelParent(hwnd):
	parent = hwnd
	while True:
		tmp_parent = TableCrabWin32.user32.GetParent(parent)
		if not tmp_parent:	break
		parent = tmp_parent
	return parent

def windowScreenPointToClientPoint(hwnd, pt):
	"""converts a point in screen coordiantes to point in window client coordinates
	@param pt: (tuple) (x, y)
	@return: (tuple) (x, y)
	"""
	pt = TableCrabWin32.POINT(*pt)
	TableCrabWin32.user32.ScreenToClient(hwnd, TableCrabWin32.byref(pt) )
	return (pt.x, pt.y) 
def windowClientPointToScreenPoint(hwnd, pt):
		"""converts a point in client coordiantes of a window screen coordinates
		@param pt: (tuple) (x, y)
		@return: (tuple) (x, y)
		"""
		pt = TableCrabWin32.POINT(*pt)
		TableCrabWin32.user32.ClientToScreen(hwnd, TableCrabWin32.byref(pt) )
		return (pt.x, pt.y) 

def windowIsVisible(hwnd):
	return bool(TableCrabWin32.user32.IsWindowVisible(hwnd))

def windowIsEnabled(hwnd):
	return bool(TableCrabWin32.user32.IsWindowEnabled(hwnd))

def windowFromPoint(x, y):
	return TableCrabWin32.user32.WindowFromPoint(TableCrabWin32.POINT(x, y))

def windowForeground():
	return TableCrabWin32.user32.GetForegroundWindow()

def windowGetButtons(hwnd):
	"""returns a dict containing buttons of a window
	@param hwnd: handle of the window
	@return: (dict) buttonName --> hwnd
	@note: if the window contains multiple buttons with the same text, the first button with this text is returned
	"""
	buttons = {}
	for hwnd in windowChildren(hwnd):
			if windowGetClassName(hwnd) == 'Button':
				text = windowGetText(hwnd)
				if text not in buttons:
					buttons[text] = hwnd
	return buttons

def windowClickButton(hwndButton):
		"""clicks a button in the window
		@param hwnd: handle of the button
		@return: (bool) True if the button was clicked successfuly, False otherwise
		"""
		if TableCrabWin32.user32.SendNotifyMessageW(hwndButton, TableCrabWin32.BM_CLICK, 0, 0): 
			return True
		return False

def windowFindChild(hwnd, className):
	"""finds a child window of a window
	@return: hwnd of the child window or None
	@todo: for some reason user32.FindWindowEx() always fails with an "Access Denied" error, so we use our own impl here 
	"""
	for hwnd in windowChildren(hwnd):
		if windowGetClassName(hwnd) == className:
			return hwnd
	return None

def windowSetText(self, hwnd, text=''):
		"""returns the window title of the specified window
		@param hwnd: handle of the window
		@todo: we currently send ANSI text only. 
		@return: (str)
		"""
		if not hwnd: raise ValueError('can not set text of desktop window')
		result = TableCrabWin32.DWORD()
		#TODO: user32.IsWindowUnicode(hwnd)
		TableCrabWin32.user32.SendMessageTimeoutA(
				hwnd, 
				TableCrabWin32.WM_SETTEXT, 
				0, 
				text, 
				TableCrabWin32.SMTO_ABORTIFHUNG, 
				TableCrabWin32.MY_SMTO_TIMEOUT, 
				TableCrabWin32.byref(result)
				)

def windowClose(hwnd):
	"""closes the specified window
	@param hwnd: handle of the window
	@return: None
	"""
	if not hwnd: raise ValueError('can not close desktop window')
	result = TableCrabWin32.DWORD()
	TableCrabWin32.user32.SendMessageTimeoutW(
			hwnd, 
			TableCrabWin32.WM_SYSCOMMAND, 
			TableCrabWin32.SC_CLOSE, 
			0, 
			TableCrabWin32.SMTO_ABORTIFHUNG, 
			TableCrabWin32.MY_SMTO_TIMEOUT, 
			TableCrabWin32.byref(result)
			)

def windowCheckboxIsChecked(hwnd):
	result = TableCrabWin32.DWORD()
	TableCrabWin32.user32.SendMessageTimeoutW(
			hwnd, 
			TableCrabWin32.BM_GETSTATE, 
			0, 
			0, 
			TableCrabWin32.SMTO_ABORTIFHUNG, 
			TableCrabWin32.MY_SMTO_TIMEOUT, 
			TableCrabWin32.byref(result)
			)
	return bool( result.value & TableCrabWin32.BST_CHECKED )
	
#***********************************************************************************
# global mouse methods
#***********************************************************************************
MouseButtonLeft = 'left'
MouseButtonRight = 'right'
MouseButtonMiddle = 'middle'
MouseWheelUp = '<MouseWheelUp>'
MouseWheelDown = '<MouseWheelDown>'

#NOTE: wine dies not orovide this info so we have to keep track ourselves
_mouseButtonsDown = []
def mouseButtonsDown():
	return _mouseButtonsDown[:]
	
def mousePressButton(button):
	"""presses the specified mouse button at the current mouse position
	@param button: (Button*)
	"""
	# determine button to set down
	if button in _mouseButtonsDown: return
	if button == MouseButtonLeft:
		bt = TableCrabWin32.MOUSEEVENTF_LEFTDOWN
	elif button == MouseButtonRight:
		bt = TableCrabWin32.MOUSEEVENTF_RIGHTDOWN
	elif button == MouseButtonMiddle:
		bt = TableCrabWin32.MOUSEEVENTF_MIDDLEDOWN
	else:
		raise ValueError('no such mouse button: %s' % button) 
	pt = mouseGetPos()
	TableCrabWin32.user32.mouse_event(bt | TableCrabWin32.MOUSEEVENTF_ABSOLUTE, pt[0], pt[1], 0, None)

def mouseReleaseButton(button):
	"""releases the specified mouse button at the current mouse position
	@param button: (Button)
	"""
	# determine button to set up
	if button not in _mouseButtonsDown: return
	if button == MouseButtonLeft:
		bt = TableCrabWin32.MOUSEEVENTF_LEFTUP
	elif button == MouseButtonRight:
		bt = TableCrabWin32.MOUSEEVENTF_RIGHTUP
	elif button == MouseButtonMiddle:
		bt = TableCrabWin32.MOUSEEVENTF_MIDDLEUP
	else:
		raise ValueError('no such mouse button: %s' % button) 
	pt = mouseGetPos()
	TableCrabWin32.user32.mouse_event(bt | TableCrabWin32.MOUSEEVENTF_ABSOLUTE, pt[0], pt[1], 0, None)	

def mouseClickPoint(button, nClicks=1, pt=None):
	'''clicks a point with the desired mouse button
	@param button: (str) button to click: (Button*)
	@param nClicks: (int) number of times to click (2 for a double-click)
	@param pt: (tuple) absolute coordinates to click. if None, the current cursor pos is taken
	@return: None	
	@todo: impl proper double click delay. GetSystemMetrics could do the trick if there is something like a min-double-click-interval defined
	@NOTE: the mouse is moved to the specified position in the call
	'''
	if _mouseButtonsDown: return
	# move mouse to point
	if pt is not None:
		mouseSetPos(pt)
	# click button
	rng = list(range(nClicks))
	while rng:
		rng.pop()
		mousePressButton(button)
		mouseReleaseButton(button)
		if rng:
			time.sleep(0.1)
	
def mouseClickLeft(pt):
	"""clicks the left mouse button at the specified point"""
	return mouseClickPoint(MouseButtonLeft, pt=pt, nClicks=1)
def mouseClickLeftDouble(pt):
	"""double clicks the left mouse button at the specified point"""
	return mouseClickPoint(MouseButtonLeft, pt=pt, nClicks=2)
def mouseClickRight(pt):
	"""clicks the right mouse button at the specified point"""
	return mouseClickPoint(MouseButtonRight, pt=pt, nClicks=1)
def mouseClickRightDouble(pt):
	"""double clicks the right mouse button at the specified point"""
	return mouseClickPoint(MouseButtonRight, pt=pt, nClicks=2)
def mouseClickMiddle(pt):
	"""clicks the middle mouse button at the specified point"""
	return self.mouseClickPoint(MouseButtonMiddle, pt=pt, nClicks=1)
def mouseClickMiddleDouble(pt):
	"""double clicks the middle mouse button at the specified point"""
	return mouseClickPoint(MouseButtonMiddle, pt=pt, nClicks=2)

def mouseGetPos():
	'''returns the current position of the mouse pointer
	@return: (tuple) x, y coordinates of the mouse cursor
	'''
	pt = TableCrabWin32.POINT()
	TableCrabWin32.user32.GetCursorPos(TableCrabWin32.byref(pt))
	return (pt.x, pt.y)

def mouseSetPos(pt):
	"""moves the mouse pointer to the specified position
	@param pt: (tuple) point containing the coordiantes to move the mouse pointer to (in screen coordiantes)
	"""
	#NOTE: for some reason neither user32.mouse_event() not user32.SendInput() have any effect here (linux/wine).
	#           the only way i can get this to work is to move the cursor stepwise to its destination?!?
	step = 4
	ptX, ptY = pt
	curX, curY = mouseGetPos()
	pt = TableCrabWin32.POINT()
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
		TableCrabWin32.user32.SetCursorPos(pt)

class _MouseHook(QtCore.QObject):
	"""win32 keyboard manager implementation
	@event EvtMouseButtonUp: event triggerered when a mouse  button is pressed. arg = Button*
	@event EvtMouseButtonDown: event triggerered when a mosue button is released. arg = Button*
	@event EvtMouseWheelScrolled: event triggerered when the mosue wheel is scrolled. arg = stepsScrolled
	"""
	
	def __init__(self, parent=None):
		"""
		@param cb: (function) event handler
		"""
		QtCore.QObject.__init__(self, parent)
		self._isStarted = False
		self._hHook = None
		self._pHookProc = TableCrabWin32.MOUSEHOOKPROCLL(self._hookProc)
		
	def _hookProc(self, code, wParam, lParam):
		"""private method, MOUSEHOOKPROCLL implementation"""
		
		if code == TableCrabWin32.HC_ACTION:
			if wParam == TableCrabWin32.WM_LBUTTONDOWN:
				if MouseButtonLeft not in _mouseButtonsDown:
					_mouseButtonsDown.append(MouseButtonLeft)
			elif wParam == TableCrabWin32.WM_RBUTTONDOWN:
				if MouseButtonRight not in _mouseButtonsDown:
					_mouseButtonsDown.append(MouseButtonRight)
			elif wParam == TableCrabWin32.WM_MBUTTONDOWN:
				if MouseButtonMiddle not in _mouseButtonsDown:
					_mouseButtonsDown.append(MouseButtonMiddle)
			elif wParam == TableCrabWin32.WM_LBUTTONUP:
				if MouseButtonLeft in _mouseButtonsDown:
					_mouseButtonsDown.remove(MouseButtonLeft)
			elif wParam == TableCrabWin32.WM_RBUTTONUP:
				if MouseButtonRight in _mouseButtonsDown:
					_mouseButtonsDown.remove(MouseButtonRight)
			elif wParam == TableCrabWin32.WM_MBUTTONUP:
				if MouseButtonMiddle in _mouseButtonsDown:
					_mouseButtonsDown.remove(MouseButtonMiddle)
					
			elif wParam == TableCrabWin32.WM_MOUSEWHEEL:
				mouseInfo = TableCrabWin32.MSLLHOOKSTRUCT.from_address(lParam)
				wheelDelta = TableCrabWin32.GET_WHEEL_DELTA_WPARAM(mouseInfo.mouseData)
				nSteps = wheelDelta / TableCrabWin32.WHEEL_DELTA
				if siteManager.handleInput(MouseWheelUp if nSteps >= 0 else MouseWheelDown, nSteps=nSteps):
					return TableCrabWin32.TRUE
		return TableCrabWin32.user32.CallNextHookEx(self._hHook, code, wParam, lParam)
	
	def isStarted(self): 
		"""cheks if the mouse manager is started"""
		return self._isStarted
	
	def start(self):
		"""starts the mouse manager"""
		if self._hHook is None:
			self._hHook = TableCrabWin32.user32.SetWindowsHookExW(
				TableCrabWin32.WH_MOUSE_LL, 
				self._pHookProc, 
				TableCrabWin32.kernel32.GetModuleHandleA(None), 
				0
				)
			if not self._hHook:
				self._hHook = None
				raise TableCrabWin32.WindowsError(TableCrabWin32.GetLastError())
				
	def stop(self):
		"""stops the mouse manager"""
		if self._hHook is not None:
			hHook, self._hHook = self._hHook, None
			if not TableCrabWin32.user32.UnhookWindowsHookEx(hHook):
				raise TableCrabWin32.WindowsError(TableCrabWin32.GetLastError())
		

mouseHook = _MouseHook()

#***********************************************************************************
# global keyboard methods
#***********************************************************************************
def keyboardLayoutName():
	"""returns the name of the current keyboard layout
	@return: (str) layout name or 'unknown'
	"""
	return TableCrabWin32.KEYBOARD_LAYOUT_NAMES.get(TableCrabWin32.kernel32.GetOEMCP(), 'unknown')
	
class _KeyboardHook(QtCore.QObject):
	"""win32 keyboard hook implementation"""
	def __init__(self, parent=None):
		"""
		@param cb: (function) event handler
		"""
		QtCore.QObject.__init__(self, parent)
		self._isStarted = False
		self._hHook = None
		self._pHookProc = TableCrabWin32.KEYBHOOKPROCLL(self._hookProc)
		
	def _hookProc(self, code, wParam, lParam):
		"""private method, KEYBHOOKPROCLL implementation"""
		if code == TableCrabWin32.HC_ACTION:
			keyInfo = TableCrabWin32.KBDLLHOOKSTRUCT.from_address(lParam)
			#HACK:(1)
			if wParam in (TableCrabWin32.WM_KEYDOWN, TableCrabWin32.WM_SYSKEYDOWN):
				TableCrabWin32.setKeyDown(keyInfo.vkCode, True)
			#<--HACK:(1)
			
			keyboardState = (TableCrabWin32.c_ubyte*256)()
			TableCrabWin32.user32.GetKeyboardState(TableCrabWin32.byref(keyboardState))
			key = self._keyFromKeyboardState(keyboardState=keyboardState)
			keydown = wParam in (TableCrabWin32.WM_KEYDOWN, TableCrabWin32.WM_SYSKEYDOWN)
			if keydown:
				signalEmit(self, 'keyPressed(QString)', key)
			else:
				signalEmit(self, 'keyReleased(QString)', key)
			
			#HACK:(1)
			if wParam in (TableCrabWin32.WM_KEYUP, TableCrabWin32.WM_SYSKEYUP):
				TableCrabWin32.setKeyDown(keyInfo.vkCode, False)
			#<--HACK:(1)
			
			if siteManager.handleInput(key, keydown=keydown):
				return TableCrabWin32.TRUE
		return TableCrabWin32.user32.CallNextHookEx(self._hHook, code, wParam, lParam)
		
	def _keyFromKeyboardState(self, keyboardState=None):
		"""@param keyboardState: (c_ubyte*256) holding a keyboar state or None"""
		value = ''
		if keyboardState:		
			for vkCode, tmp_value in enumerate(keyboardState):
				if tmp_value:
					if vkCode in (		# ignore these keys
							TableCrabWin32.VK_CONTROL,
							TableCrabWin32.VK_MENU,
							TableCrabWin32.VK_SHIFT,
							TableCrabWin32.VK_SCROLL,
							TableCrabWin32.VK_CAPITAL,
							TableCrabWin32.VK_NUMLOCK,
							):
						continue
					if value:
						value += ' %s' % TableCrabWin32.KEY_NAMES[vkCode]
					else:
						value = TableCrabWin32.KEY_NAMES[vkCode]
		return '<%s>' % value
	
	def isStarted(self): 
		"""cheks if the keyboard manager is started"""
		return self._isStarted
	
	def start(self):
		"""starts the keyboard manager"""
		if self._hHook is None:
			self._hHook = TableCrabWin32.user32.SetWindowsHookExW(
				TableCrabWin32.WH_KEYBOARD_LL, 
				self._pHookProc, 
				TableCrabWin32.kernel32.GetModuleHandleA(None), 
				0
				)
			if not self._hHook:
				self._hHook = None
				raise TableCrabWin32.WindowsError(TableCrabWin32.GetLastError())
			
	def stop(self):
		"""stops the keyboard manager"""
		if self._hHook is not None:
			hHook, self._hHook = self._hHook, None
			if not TableCrabWin32.user32.UnhookWindowsHookEx(hHook):
				raise TableCrabWin32.WindowsError(TableCrabWin32.GetLastError())

keyboardHook = _KeyboardHook()

#***********************************************************************************
# 
#***********************************************************************************
SiteNamePokerStars = 'PokerStars'

#***********************************************************************************
# types
#***********************************************************************************
pointNone = QtCore.QPoint()
sizeNone = QtCore.QSize()

class CallableString(QtCore.QString):
	def __call__(self):
		return self.__class__(self)
	
class CallableFloat(float):
	def __call__(self):
		return self
class CallableBool(object):
	def __init__(self, value):
		self.value = value
	def __call__(self):
		return self.value
	
ValueNone = 'None'

#***********************************************************************************
# persistent items
#***********************************************************************************

import inspect
class PersistentItemManager(QtCore.QObject):
	#NOTE: we can not use __metaclass__ along with QObject. so we have to track actions by hand
	def __init__(self, parent=None, key=None, maxItems=0,itemProtos=None):
		QtCore.QObject.__init__(self, parent)
		self._items = []
		self.maxItems = maxItems
		self.key = key
		self.itemProtos= [] if itemProtos is None else itemProtos
		self._readFinished = False
	def read(self):
		# read items
		if self._readFinished:
			raise ValueError('you can read items only once')
		self._items = []
		if self.key is not None:
			newItems = []
			for slot in xrange(self.maxItems):
				key = settingsKeyJoin(self.key, str(slot) )
				for itemProto in self.itemProtos:
					newItem = itemProto.fromConfig(key)
					if newItem is not None:
						newItems.append( (slot, newItem) )
			for _, item in sorted(newItems):
				self._items.append(item)
				signalEmit(self, 'itemRead(QObject*)', item)
			self.dump()
			self._readFinished = True
			signalEmit(self, 'readFinished()')
	def dump(self):
		settingsRemoveKey(self.key)
		slot = 0
		for item in self._items:
			key = settingsKeyJoin(self.key, str(slot) )
			if item.toConfig(key):
				slot += 1
	def __len__(self): return len(self._items)
	def __iter__(self):
		return iter(self._items)
	def index(self, item):
		return self._items.index(item)
	def canAddItem(self):
		return len(self) < self.maxItems
	def addItem(self, item):
		self._items.append(item)
		if self.key is not None:
			self.dump()
		signalEmit(item,'itemAdded(QObject*)', item)
	def removeItem(self, item):
		self._items.remove(item)
		if self.key is not None:
			self.dump()
		signalEmit(item, 'itemRemoved(QObject*)', item)
	def canMoveItemUp(self, item):
		return self.index(item) > 0
	def canMoveItemDown(self, item):
		return self.index(item) < len(self._items) -1
	def moveItemUp(self, item):
		if not self.canMoveItemUp(item):
			raise valueError('can not move item up')
		index = self.index(item)
		self._items.remove(item)
		self._items.insert(index-1, item)
		if self.key is not None:
			self.dump()
		signalEmit(item, 'itemMovedUp(QObject*, int)', item, index -1)
	def moveItemDown(self, item):
		if not self.canMoveItemDown(item):
			raise valueError('can not move item up')
		index = self.index(item)
		self._items.remove(item)
		self._items.insert(index+1, item)
		if self.key is not None:
			self.dump()
		signalEmit(item, 'itemMovedDown(QObject*, int)', item, index +1)
	def readFinished(self):
		return self._readFinished
	def setItemAttr(self, item, name, value):
		setattr(item, name, value)
		signalEmit(item, 'itemAttrChanged(QObject*, QString)', item, name)
		if self.key is not None:
			self.dump()
	def setItemAttrs(self, item, values):
		for name, value in values.items():
			setattr(item, name, value)
			signalEmit(item, 'itemAttrChanged(QObject*, QString)', item, name)
		if self.key is not None:
			self.dump()


class PersistentItem(QtCore.QObject):
	Attrs = (	# (name, valueType) ..if a kw is None an instance of valuetype is set as default
			)
	def __init__(self, 
			parent=None,
			**kws 
			):
		QtCore.QObject.__init__(self, parent)
		for name, valueType in self.Attrs:
			value = kws.get(name, None)
			if value is None:
				value= valueType()
			setattr(self, name, value)
	def iterAttrs(self):
		for name, _ in self.Attrs:
			yield name, getattr(self, name)

class ActionCheck(PersistentItem):
	Attrs = (
			('name', QtCore.QString),
			('hotkey', QtCore.QString),
			('hotkeyName', QtCore.QString),
			)
	@classmethod
	def itemName(klass):
		return 'Check'
	@classmethod
	def fromConfig(klass, key):
		itemName = settingsValue( settingsKeyJoin(key, 'ItemName'), '').toString()
		if itemName != klass.itemName(): return None
		hotkey = settingsValue( settingsKeyJoin(key, 'Hotkey'), ValueNone).toString()
		if hotkey == ValueNone: return None
		name = settingsValue( settingsKeyJoin(key, 'Name'), '').toString()
		hotkeyName = settingsValue( settingsKeyJoin(key, 'HotkeyName'), '').toString()
		return klass(name=name, hotkey=hotkey, hotkeyName=hotkeyName)
	def toConfig(self, key):
		settingsSetValue( settingsKeyJoin(key, 'ItemName'), self.itemName() )
		settingsSetValue( settingsKeyJoin(key, 'Name'), self.name )
		settingsSetValue( settingsKeyJoin(key, 'Hotkey'), self.hotkey )
		settingsSetValue( settingsKeyJoin(key, 'HotkeyName'), self.hotkeyName)
		return True

class ActionFold(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Fold'

class ActionRaise(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Raise'

class ActionScreenshot(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Screenshot'
		
class ActionHilightBetAmount(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'HilightBetAmount'

class ActionReplayer(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Replayer'

class ActionInstantHandHistory(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'InstantHandHistory'

class ActionAlterBetAmount(PersistentItem):
	BaseValues = ('BigBlind', 'SmallBlind', 'CurrentBet')
	Attrs = (
			('name', QtCore.QString),
			('hotkey', QtCore.QString),
			('hotkeyName', QtCore.QString),
			('baseValue', CallableString('BigBlind') ),
			('multiplier', CallableFloat(1.0)),
			)
	@classmethod
	def itemName(klass):
		return 'AlterBetAmount'
	@classmethod
	def fromConfig(klass, key):
		itemName = settingsValue( settingsKeyJoin(key, 'ItemName'), ValueNone).toString()
		if itemName != klass.itemName(): return None
		hotkey = settingsValue( settingsKeyJoin(key, 'Hotkey'), ValueNone).toString()
		if hotkey == ValueNone: return None
		hotkeyName = settingsValue( settingsKeyJoin(key, 'HotkeyName'), '').toString()
		baseValue = settingsValue( settingsKeyJoin(key, 'BaseValue'), ValueNone).toString()
		if baseValue not in klass.BaseValues: return None
		multiplier, ok = settingsValue( settingsKeyJoin(key, 'Multiplier'), 1.0).toDouble()
		if not ok: return None
		name = settingsValue( settingsKeyJoin(key, 'Name'), ValueNone).toString()
		return klass(name=name, hotkey=hotkey, hotkeyName=hotkeyName, baseValue = baseValue, multiplier=multiplier)
	def toConfig(self, key):
		settingsSetValue( settingsKeyJoin(key, 'ItemName'), self.itemName() )
		settingsSetValue( settingsKeyJoin(key, 'Name'), self.name)
		settingsSetValue( settingsKeyJoin(key, 'HotkeyName'), self.hotkeyName)
		settingsSetValue( settingsKeyJoin(key, 'Hotkey'), self.hotkey)
		settingsSetValue( settingsKeyJoin(key, 'BaseValue'), self.baseValue)
		settingsSetValue( settingsKeyJoin(key, 'Multiplier'), self.multiplier)
		return  True

#NOTE: we can not use __metaclass__ along with QObject ..so we have to keep track by hand
Actions = (
		ActionCheck,
		ActionFold,
		ActionRaise,
		ActionAlterBetAmount,
		ActionHilightBetAmount,
		ActionScreenshot,
		)

MaxActions = 64
class _ActionItemManager(PersistentItemManager):
	def __init__(self, parent=None):
		PersistentItemManager.__init__(self, parent=parent, key='Hotkeys', maxItems=MaxActions, itemProtos=Actions)
		
actionItemManager = _ActionItemManager()


class SetupWidgetItemTablePokerStars(PersistentItem):
	Attrs = (		# name--> valueType
			('name', QtCore.QString),
			('size', QtCore.QSize), 
			('buttonCheck', QtCore.QPoint),
			('buttonFold', QtCore.QPoint),
			('buttonRaise', QtCore.QPoint),
			('checkboxFold', QtCore.QPoint),
			('instantHandHistory', QtCore.QPoint),
			('replayer', QtCore.QPoint),
			('itemIsExpanded', CallableBool(False)),
			)
	@classmethod
	def itemName(klass):
		return 'PokerStarsTable'
	@classmethod
	def fromConfig(klass, key):
		itemName = settingsValue( settingsKeyJoin(key, 'ItemName'), ValueNone).toString()
		if itemName != klass.itemName(): return None
		name = settingsValue(settingsKeyJoin(key, 'Name'), 'None').toString()
		size = settingsValue(settingsKeyJoin(key, 'Size'), sizeNone).toSize()
		buttonCheck = settingsValue(settingsKeyJoin(key, 'ButtonCheck'), pointNone).toPoint()
		buttonFold = settingsValue(settingsKeyJoin(key, 'ButtonFold'), pointNone).toPoint()
		buttonRaise = settingsValue(settingsKeyJoin(key, 'ButtonRaise'), pointNone).toPoint()
		instantHandHistory = settingsValue(settingsKeyJoin(key, 'InstantHandHistory'), pointNone).toPoint()
		replayer = settingsValue(settingsKeyJoin(key, 'Replayer'), pointNone).toPoint()
		checkboxFold = settingsValue(settingsKeyJoin(key, 'CheckboxFold'), pointNone).toPoint()
		itemIsExpanded = settingsValue(settingsKeyJoin(key, 'ItemIsExpanded'), False).toBool()
		return klass(name=name, size=size, buttonCheck=buttonCheck, 
				buttonFold=buttonFold, buttonRaise=buttonRaise, replayer=replayer, instantHandHistory=instantHandHistory, 
				checkboxFold=checkboxFold, itemIsExpanded=itemIsExpanded)
	def toConfig(self, key):
		settingsSetValue( settingsKeyJoin(key, 'ItemName'), self.itemName() )
		settingsSetValue(settingsKeyJoin(key, 'Name'), self.name)
		settingsSetValue(settingsKeyJoin(key, 'Size'), self.size)
		settingsSetValue(settingsKeyJoin(key, 'ButtonCheck'), self.buttonCheck)
		settingsSetValue(settingsKeyJoin(key, 'ButtonFold'), self.buttonFold)
		settingsSetValue(settingsKeyJoin(key, 'ButtonRaise'), self.buttonRaise)
		settingsSetValue(settingsKeyJoin(key, 'CheckboxFold'), self.checkboxFold)
		settingsSetValue(settingsKeyJoin(key, 'Replayer'), self.replayer)
		settingsSetValue(settingsKeyJoin(key, 'InstantHandHistory'), self.instantHandHistory)
		settingsSetValue(settingsKeyJoin(key, 'ItemIsExpanded'), self.itemIsExpanded)
		return True

SetupWidgetItems = (
		SetupWidgetItemTablePokerStars,
		)
MaxSetupWidgetItems = 64
class _SetupWidgetItemManager(PersistentItemManager):
	def __init__(self, parent=None):
		PersistentItemManager.__init__(self, parent=parent, key='Setup/Widgets', maxItems=MaxSetupWidgetItems, itemProtos=SetupWidgetItems)
		
setupWidgetItemManager = _SetupWidgetItemManager()

#***********************************************************************************
# 
#***********************************************************************************
class _SiteManager(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		signalConnect(windowHook, self, 'windowCreated(int)', self.onWindowCreated)
		signalConnect(windowHook, self, 'windowDestroyed(int)', self.onWindowDestroyed)
		signalConnect(windowHook, self, 'windowGainedForeground(int)', self.onWindowGainedForeground)
		self._pokerStarsLoginBox = None
	
	def onWindowDestroyed(self, hwnd):
		##print 'destroyed: ', hwnd, "'%s'" % windowGetClassName(hwnd), "'%s'" %  windowGetText(hwnd)
		if hwnd == self._pokerStarsLoginBox:
			self._pokerStarsLoginBox = None
		
	def onWindowGainedForeground(self, hwnd):
		##print 'gainedForeground: ', hwnd, "'%s'" % windowGetClassName(hwnd), "'%s'" %  windowGetText(hwnd)
		pass
		
	def onWindowCreated(self, hwnd):
		##print 'created: ',  hwnd, "'%s'" % windowGetClassName(hwnd), "'%s'" %  windowGetText(hwnd)
		
		if self.windowIsPokerStarsPopupNews(hwnd):
			if settingsValue('PokerStars/AutoClosePopupNews', False).toBool():
				windowClose(hwnd)
		
		elif self.windowIsPokerStarsTourneyRegistrationMessageBox(hwnd):
			if settingsValue('PokerStars/AutoCloseTourneyRegistrationBoxes', False).toBool():
				buttons = windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				##windowClose(hwnd)
				windowClickButton(buttons['OK'])
		
		elif self.windowIsPokerStarsTableMessageBox(hwnd):
			if settingsValue('PokerStars/AutoCloseTableMessageBoxes', False).toBool():
				buttons = windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				windowClickButton(buttons['OK'])
		
		elif self.windowIsPokerStarsLogIn(hwnd):
			if self._pokerStarsLoginBox is None: 
				self._pokerStarsLoginBox = hwnd
				if settingsValue('PokerStars/AutoCloseLogin', False).toBool():
					buttons = windowGetButtons(hwnd)
					if sorted(buttons) == ['', 'Cancel', 'Create New Account...', 'Forgot User ID / Password...', 'OK']:
						if windowCheckboxIsChecked(buttons['']):
							if windowIsEnabled(buttons['OK']):
								windowClickButton(buttons['OK'])
		
	def handleInput(self, input, keydown=None, nSteps=None):
		hwnd = windowForeground()
		if not hwnd:
			return False
			
		for actionItem in actionItemManager:
			if not actionItem.hotkey: continue
			if not actionItem.hotkey == input: continue
				
			actionName = actionItem.itemName()
			if actionName == ActionScreenshot.itemName():
				if not keydown or nSteps is not None:
					widgetScreenshot(hwnd)
				return True
				
			elif actionName == ActionCheck.itemName():
				if not keydown or nSteps is not None:
					if self.windowIsPokerStarsTable(hwnd):
						widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)	
						if widgetItem is not None:
							self.pokerStarsTableHandleCheck(actionItem, widgetItem, hwnd)
				return True
					
			elif actionName == ActionFold.itemName():
				if not keydown or nSteps is not None:
					if self.windowIsPokerStarsTable(hwnd):
						widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)	
						if widgetItem is not None:
							self.pokerStarsTableHandleFold(actionItem, widgetItem, hwnd)
				return True		
			
			elif actionName == ActionRaise.itemName():
				if not keydown or nSteps is not None:
					if self.windowIsPokerStarsTable(hwnd):
						widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)	
						if widgetItem is not None:
							self.pokerStarsTableHandleRaise(actionItem, widgetItem, hwnd)
				return True	
			
			elif actionName == ActionAlterBetAmount.itemName():
				if not keydown or nSteps is not None:
					if self.windowIsPokerStarsTable(hwnd):
						widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)	
						if widgetItem is not None:
							self.pokerStarsTableHandleAlterBetAmount(actionItem, widgetItem, hwnd)
				return True	
			
			elif actionName == ActionHilightBetAmount.itemName():
				if not keydown or nSteps is not None:
					if self.windowIsPokerStarsTable(hwnd):
						widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)	
						if widgetItem is not None:
							self.pokerStarsTableHandleHilightBetAmount(actionItem, widgetItem, hwnd, nSteps=nSteps)
				return True

			elif actionName == ActionReplayer.itemName():
				if not keydown or nSteps is not None:
					if self.windowIsPokerStarsTable(hwnd):
						widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)	
						if widgetItem is not None:
							self.pokerStarsTableHandleReplayer(actionItem, widgetItem, hwnd)
				return True
			
			elif actionName == ActionInstantHandHistory.itemName():
				if not keydown or nSteps is not None:
					if self.windowIsPokerStarsTable(hwnd):
						widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)	
						if widgetItem is not None:
							self.pokerStarsTableHandleInstantHandHistory(actionItem, widgetItem, hwnd)
				return True
			
		return False
		
	# PokerStars	
	#-----------------------------------------------------------------------------------------
	def pokerStarsGetTableWidgetItem(self, hwnd):
		w, h = windowGetClientRect(hwnd)[2:]
		for persistentItem in setupWidgetItemManager:
			if persistentItem.itemName() == 'PokerStarsTable':
				if (persistentItem.size.width(), persistentItem.size.height()) == (w, h):
					return persistentItem
		return None

	
	PokerStarsPatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PokerStarsPatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	PokerStarsClassTableBetAmountBox = 'PokerStarsSliderEditorClass'
	def pokerStarsTableReadData(self, hwnd):
		data = {}
		text = windowGetText(hwnd)
		match = self.PokerStarsPatAmountSB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %s' % text)
		data['smallBlind'] = float(match.group(1))
		match = self.PokerStarsPatAmountBB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %s' % text)
		data['bigBlind'] = float(match.group(1))
		hwndBetAmountBox = windowFindChild(hwnd, self.PokerStarsClassTableBetAmountBox)
		data['hwndBetAmountBox'] =  hwndBetAmountBox
		data['betAmountBoxIsVisible'] = windowIsVisible(hwndBetAmountBox )
		data['betAmount'] = None
		if data['hwndBetAmountBox']:
			p = windowGetText(hwndBetAmountBox)
			try:
				data['betAmount'] = float(p)
			except ValueError: pass
		return data
		
	def pokerStarsTableHandleCheck(self, actionItem, widgetItem, hwnd):
		data = self.pokerStarsTableReadData(hwnd)
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		point = widgetItem.buttonCheck
		if not point.isNull():
			pt = windowClientPointToScreenPoint(hwnd, (point.x(), point.y()) )
			mouseClickLeft(pt)
		
	def pokerStarsTableHandleFold(self, actionItem, widgetItem, hwnd):
		data = self.pokerStarsTableReadData(hwnd)
		if not data['hwndBetAmountBox']: return
		if data['betAmountBoxIsVisible']:
			point = widgetItem.buttonFold
		else:
			point = widgetItem.checkboxFold
		if not point.isNull():
			pt = windowClientPointToScreenPoint(hwnd, (point.x(), point.y()) )
			mouseClickLeft(pt)
	
	def pokerStarsTableHandleRaise(self, actionItem, widgetItem, hwnd):
		data = self.pokerStarsTableReadData(hwnd)
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		point = widgetItem.buttonRaise
		if not point.isNull():
			pt = windowClientPointToScreenPoint(hwnd, (point.x(), point.y()) )
			mouseClickLeft(pt)
	
	def pokerStarsTableHandleAlterBetAmount(self, actionItem, widgetItem, hwnd, nSteps=None):
		data = self.pokerStarsTableReadData(hwnd)
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		
		if nSteps == 0: return
		nSteps = 1 if nSteps is None else abs(nSteps)	
		
		if actionItem.baseValue == 'BigBlind':
			baseValue = data['bigBlind']
		elif actionItem.baseValue == 'SmallBlind':
			baseValue = data['smallBlind']
		elif	actionItem.baseValue == 'CurrentBet':
			baseValue = data['betAmount']
		else: raise ValueError('unknown baseVale: %s' %actionItem.baseVale)
			
		newBetAmount = round(baseValue * actionItem.multiplier * nSteps, 2)
		if int(newBetAmount) == newBetamount:
			newbetAmount = int(newbetAmount)
		newBetAmount = 0 if newBetAmount < 0 else newBetAmount
		windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		
	def pokerStarsTableHandleHiligthBetAmount(self, actionItem, widgetItem, hwnd):
		data = pokerStarsTableReadData(hwnd)
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		x, y = windowClientPointToScreenPoint(hwnd, (0, 0) )
		mouseClickLeftDouble( (x, y) )	#TODO: maybe we need to add a bit of an offset
		
	def pokerStarsTableReplayer(self, actionItem, widgetItem, hwnd):
		point = widgetItem.replayer
		if not point.isNull():
			pt = windowClientPointToScreenPoint(hwnd, (point.x(), point.y()) )
			mouseClickLeft(pt)
			pt = windowClientPointToScreenPoint(hwnd, (0, 0) )
			mouseClickLeft(pt)
		
	def pokerStarsTableHandleInstantHandHistory(self, actionItem, widgetItem, hwnd):
		point = widgetItem.instantHandHistory
		if not point.isNull():
			pt = windowClientPointToScreenPoint(hwnd, (point.x(), point.y()) )
			mouseClickLeft(pt)
			pt = windowClientPointToScreenPoint(hwnd, (0, 0) )
			mouseClickLeft(pt)
		
	
	#NOTE: not easy to determine if a window is a PokerStarswindow. i don't feel like messing around with psapi.dll to get the exefilename.
	# so ..i use a hack. we identify a window as being a stars window if it (or one of its parents) contains a widget classname.startswith('PokerStars')
	# nasty and errorprone, but the most reasonalbe i could come up with now
	def windowHasPokerStarsWidgets(self, hwnd):
		for hwnd in windowChildren(hwnd):
			if windowGetClassName(hwnd).startswith('PokerStars'):	return True
		return False
	
	def windowIsPokerStarsWindow(self, hwnd):
		while hwnd:
			if self.windowHasPokerStarsWidgets(hwnd): return True
			hwnd = windowGetParent(hwnd)
		return False	
	
	PokerStarsTitleLobby = 'PokerStars Lobby'
	PokerStarsClassLobby = '#32770'	# duh, stars. main windows should never be dialogs
	def windowIsPokerStarsLobby(self, hwnd):
		if not windowGetClassName(hwnd) == self.PokerStarsClassLobby: return False
		if not windowGetText(hwnd).startswith(self.PokerStarsTitleLobby): return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True
		
	PokerStarsClassTable = 'PokerStarsTableFrameClass'
	def windowIsPokerStarsTable(self, hwnd):
		if not windowGetClassName(hwnd) == self.PokerStarsClassTable: return False
		return True	

	PokerStarsClassInstantHandHistory = '#32770'
	PokerStarsTitleInstantHandHistory = 'Instant Hand History'
	def windowIsPokerStarsInstantHandHistory(self, hwnd):
		if not windowGetClassName(hwnd) == self.PokerStarsClassInstantHandHistory: return False
		if not windowGetText(hwnd) == self.PokerStarsTitleInstantHandHistory: return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True
		
	PokerStarsClassNews = '#32770'
	PokerStarsTitleNews = 'News'
	def windowIsPokerStarsPopupNews(self, hwnd):
		if not windowGetClassName(hwnd) == self.PokerStarsClassNews: return False
		if not windowGetText(hwnd) == self.PokerStarsTitleNews: return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True
		
	PokerStarsTitleTourneyRegistrationMessageBox = 'Tournament Registration'
	PokerStarsClassTourneyRegistrationMessageBox = '#32770'
	def windowIsPokerStarsTourneyRegistrationMessageBox(self, hwnd):
		if not windowGetClassName(hwnd) == self.PokerStarsClassTourneyRegistrationMessageBox: return False
		if not windowGetText(hwnd) == self.PokerStarsTitleTourneyRegistrationMessageBox: return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True

	PokerStarsTitleTableMessageBox = 'Tournament Registration'
	PokerStarsClassTableMessageBox = '#32770'
	def windowIsPokerStarsTableMessageBox(self, hwnd):
		if not windowGetClassName(hwnd) == self.PokerStarsClassTableMessageBox: return False
		if not windowGetText(hwnd) == self.PokerStarsTitleTableMessageBox: return False
		hwndParent = windowGetParent(hwnd)
		if not self.windowIsPokerStarsTable(hwndParent): return False
		return True
		
	PokerStarsTitleLogIn = 'Log In'
	PokerStarsClassLogIn = '#32770'
	def windowIsPokerStarsLogIn(self, hwnd):
		if not windowGetClassName(hwnd) == self.PokerStarsClassLogIn: return False
		if not windowGetText(hwnd) == self.PokerStarsTitleLogIn: return False
		hwndParent = windowGetParent(hwnd)
		if not self.windowIsPokerStarsLobby(hwndParent): return False
		return True


siteManager = _SiteManager()

#***********************************************************************************
# Qt widgets
#***********************************************************************************
class TableCrabAction(QtGui.QAction):
	def __init__(self, 
				parent=None,
				text='', 
				menu=None,
				icon=None,
				slot=None,
				isEnabled=True,
				):
		if icon is not None:
			QtGui.QAction.__init__(self, icon, text, parent)
		else:
			QtGui.QAction.__init__(self, parent)
		self.setText(text)
		self.setMenu(menu)
		if slot is not None and parent is not None: parent.connect(self, QtCore.SIGNAL('triggered(bool)'), slot)
		self.setEnabled(isEnabled)
		#if icon is not None: self.setIcon(icon)
		
		
class TableCrabWebViewToolBar(QtGui.QToolBar):
	ZoomIncrement = 0.1
	def __init__(self, webView, settingsKeyZoomFactor=None, settingsKeyZoomIncrement=None):
		QtGui.QToolBar.__init__(self, webView)
		self.webView = webView
		self.settingsKeyZoomFactor = settingsKeyZoomFactor
		self.settingsKeyZoomIncrement = settingsKeyZoomIncrement
		
		self.addAction( self.webView.pageAction(QtWebKit.QWebPage.Back) )
		self.addAction( self.webView.pageAction(QtWebKit.QWebPage.Forward) )
		
		self.actionZoomIn = TableCrabAction(
				parent=self,
				text='Zoom+',
				icon=QtGui.QIcon(Pixmaps.magnifierPlus() ),
				slot=self.onActionZoomInTriggered,
				)
		self.addAction(self.actionZoomIn)
		
		self.actionZoomOut = TableCrabAction(
				parent=self,
				text='Zoom-',
				icon=QtGui.QIcon(Pixmaps.magnifierMinus() ),
				slot=self.onActionZoomOutTriggered,
				)
		self.addAction(self.actionZoomOut)
	
	def onActionZoomInTriggered(self):
		zoomIncrement = self.ZoomIncrement
		if self.settingsKeyZoomIncrement is not None:
			zoomIncrement = settingsValue(self.settingsKeyZoomIncrement, self.ZoomIncrement).toDouble()[0]
		self.webView.setZoomFactor(self.webView.zoomFactor() + zoomIncrement)
		if self.settingsKeyZoomFactor is not None:
			settingsSetValue(self.settingsKeyZoomFactor, self.webView.zoomFactor())
		#TODO: what is MaxZoom?
		self.actionZoomOut.setEnabled(True)
	
	def onActionZoomOutTriggered(self):
		zoomIncrement = self.ZoomIncrement
		if self.settingsKeyZoomIncrement is not None:
			zoomIncrement = settingsValue(self.settingsKeyZoomIncrement, self.ZoomIncrement).toDouble()[0]
		zoom = self.webView.zoomFactor() - zoomIncrement
		if zoom > 0:
			self.webView.setZoomFactor(zoom)
			if self.settingsKeyZoomFactor is not None:
				settingsSetValue(self.settingsKeyZoomFactor, self.webView.zoomFactor())
		else:
			self.actionZoomOut.setEnabled(False)
	
#TODO: rename to TableCrab...
class LineEdit(QtGui.QLineEdit):
	def __init__(self, default='', settingsKey=None, parent=None):
		QtGui.QLineEdit.__init__(self, parent)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			self.setText(default)
		else:
			self.setText( settingsValue(self.settingsKey, default).toString() )
			self.connect(self, QtCore.SIGNAL('editingFinished()'), self.onValueChanged)
	def onValueChanged(self):
			if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.text())

class PlainTextEdit(QtGui.QPlainTextEdit):
	def __init__(self, default='', settingsKey=None, parent=None):
		QtGui.QPlainTextEdit.__init__(self, parent)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			self.setPlainText(default)
		else:
			self.setPlainText( settingsValue(self.settingsKey, default).toString() )
			self.connect(self, QtCore.SIGNAL('textChanged()'), self.onValueChanged)
	def onValueChanged(self):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.toPlainText())

class DoubleSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, default=1.0, minimum=0.0, maximum=99.99, step=1.0, precision=2, settingsKey=None, parent=None):
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self.settingsKey = settingsKey
		self.setRange(minimum, maximum)
		self.setSingleStep(step)
		self.setDecimals(precision)
		if self.settingsKey is None:
			self.setValue(default)
		else:
			self.setValue(  settingsValue(self.settingsKey, default).toDouble()[0] )
			self.connect(self, QtCore.SIGNAL('valueChanged(double)'), self.onValueChanged)
	def onValueChanged(self):
			if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.value())
				
class SpinBox(QtGui.QSpinBox):
	def __init__(self, default=1, minimum=0, maximum=99, settingsKey=None, parent=None):
		QtGui.QSpinBox.__init__(self, parent)
		self.settingsKey = settingsKey
		self.setRange(minimum, maximum)
		if self.settingsKey is None:
			self.setValue(default)
		else:
			self.setValue(  settingsValue(self.settingsKey, default).toInt()[0] )
			self.connect(self, QtCore.SIGNAL('valueChanged(int)'), self.onValueChanged)
	def onValueChanged(self):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.value())

class CheckBox(QtGui.QCheckBox):
	def __init__(self, text, default=False, settingsKey=None, parent=None):
		QtGui.QCheckBox.__init__(self, text, parent)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			self.setCheckState(  QtCore.Qt.Checked if default else QtCore.Qt.Unchecked )
		else:
			self.setCheckState(  QtCore.Qt.Checked if settingsValue(self.settingsKey, default).toBool() else QtCore.Qt.Unchecked )
			self.connect(self, QtCore.SIGNAL('stateChanged(int)'), self.onStateChanged)
	def onStateChanged(self):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.checkState() == QtCore.Qt.Checked)

class ComboBox(QtGui.QComboBox):
	def __init__(self, choices, default='', failsave=False, settingsKey=None, parent=None):
		QtGui.QComboBox.__init__(self, parent)
		self.addItems(choices)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			value = default
		else:
			value = settingsValue(self.settingsKey, default).toString()
			self.connect(self, QtCore.SIGNAL('currentIndexChanged(QString)'), self.onCurrentIndexChanged)
		if failsave:
			if value in choices:
				self.setCurrentIndex(choices.index(value))
		else:
			self.setCurrentIndex(choices.index(value))
	def 	onCurrentIndexChanged(self, qString):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, qString)

contentsMargins = QtCore.QMargins(2, 2, 2, 2)
class VBox(QtGui.QVBoxLayout):
	def __init__(self, *args):
		QtGui.QVBoxLayout.__init__(self, *args)
		self.setContentsMargins(contentsMargins)
		
class HBox(QtGui.QHBoxLayout):
	def __init__(self, *args):
		QtGui.QHBoxLayout.__init__(self, *args)
		self.setContentsMargins(contentsMargins)

class GridBox(QtGui.QGridLayout):
	def __init__(self, *args):
		QtGui.QGridLayout.__init__(self, *args)
		self.setContentsMargins(contentsMargins)
		
class HLine(QtGui.QFrame):
	def __init__(self, *args):
		QtGui.QFrame.__init__(self, *args)
		self.setFrameStyle(self.HLine | self.Sunken)
class HStretch(HBox):
	def __init__(self, *args):
		HBox.__init__(self, *args)
		self.addStretch(999)
class VStretch(VBox):
	def __init__(self, *args):
		VBox.__init__(self, *args)
		self.addStretch(999)

class TreeWidgetItemIterator(QtGui.QTreeWidgetItemIterator):
	def __init__(self, *args):
		QtGui.QTreeWidgetItemIterator.__init__(self, *args)
	def __iter__(self):
		while True:
			self.__iadd__(1)
			value = self.value()
			if value:
				yield value
			else:
				break
		raise StopIteration

def MsgWarning(parent, msg):
	QtGui.QMessageBox.critical(parent, TableCrabApplicationName, msg)

def MsgCritical(msg):
	QtGui.QMessageBox.critical(parent, TableCrabApplicationName, msg)

#***********************************************************************************
# type converters
#***********************************************************************************
def pointToString(qPoint):
	return '%s,%s' % (qPoint.x(), qPoint.y())

def sizeToString(qSize):
	if qSize.isEmpty():
		return 'None'
	return '%sx%s' % (qSize.width(), qSize.height())

#***********************************************************************************
# global Application and ainWindow object
#***********************************************************************************

class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.setWindowTitle(TableCrabReleaseName)
		self.setWindowIcon( QtGui.QIcon(Pixmaps.tableCrab()) )
		font = QtGui.QFont()
		if font.fromString(settingsValue('Gui/Font', '').toString() ):
			QtGui.qApp.setFont(font)
		self.restoreGeometry( settingsValue('Gui/Geometry', QtCore.QByteArray()).toByteArray() )
	def show(self):
		style = settingsValue('Gui/Style', '').toString()
		QtGui.qApp.setStyle(QtGui.QStyleFactory.create(style))
		QtGui.QMainWindow.show(self)
		mouseHook.start()
		keyboardHook.start()
		windowHook.start()
		actionItemManager.read()
		setupWidgetItemManager.read()
	def closeEvent(self, event):
		signalEmit(None, 'closeEvent(QEvent*)', event)
		mouseHook.stop()
		keyboardHook.stop()
		windowHook.stop()
		settingsSetValue('Gui/Geometry', self.saveGeometry() )
		return QtGui.QMainWindow.closeEvent(self, event)
	def start(self):
		self.show()
		application.exec_()
	
application = QtGui.QApplication(sys.argv)

#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': MainWindow().start()
	
	
	




