
#TODO: use MapWindowPoints() instead of ClientToScreen() and ScreenToClient(). rly?

import time, atexit
from ctypes import *
from ctypes.wintypes import *

user32 = windll.user32
kernel32 = windll.kernel32

from PyQt4 import QtCore

#**************************************************************
#
#**************************************************************

ERROR_ACCESS_DENIED = 5
ERROR_INVALID_HANDLE = 183

BM_GETSTATE = 242
BST_CHECKED	= 1

LRESULT = c_ulong
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
WM_MOUSEWHEEL = 522

WHEEL_DELTA = 120

class MSLLHOOKSTRUCT(Structure):
	_fields_ = [
		('pt', POINT),
		('mouseData', DWORD),
		('flags', DWORD),
		('time', DWORD),
		('dwExtraInfo', POINTER(ULONG))
		]

def HIWORD(dword):
	return DWORD(dword).value >> 16
def MAKELONG(word1, word2): return word1 | (word2 << 16)

def pointToWorldCoords(point):
	x = float(point.x() * 0xFFFF) / user32.GetSystemMetrics(SM_CXSCREEN)
	y = float(point.y() * 0xFFFF) / user32.GetSystemMetrics(SM_CYSCREEN)
	return QtCore.QPoint(
			int( round(x, 0) ),
			int( round(y, 0) ),
			)

def getCurrentTime():
	return kernel32.GetTickCount()

def GET_WHEEL_DELTA_WPARAM(wParam):
	return c_short(HIWORD(wParam)).value

VK_CONTROL =  0x11
VK_LCONTROL =  0xA2
VK_RCONTROL =  0xA3
VK_MENU =  0x12
VK_LMENU =  0xA4
VK_RMENU =  0xA5
VK_SHIFT =  0x10
VK_LSHIFT =  0xA0
VK_RSHIFT =  0xA1
VK_SCROLL = 0x91
VK_CAPITAL = 0x14
VK_NUMLOCK = 0x90
VK_SHIFT = 0x10

WH_KEYBOARD_LL = 13
HC_ACTION = 0
KEYBHOOKPROCLL = WINFUNCTYPE(LRESULT, c_int, WPARAM, LPARAM)
class KBDLLHOOKSTRUCT(Structure):
	_fields_ = [
		('vkCode', DWORD),
		('scanCode', DWORD),
		('flags', DWORD),
		('time', DWORD),
		('dwExtraInfo', POINTER(ULONG))
		]

WM_KEYDOWN = 256
WM_KEYUP = 257
WM_SYSKEYDOWN = 260
WM_SYSKEYUP = 261

KEY_VALUES = {		# keyName --> vkCode
		'LeftButton': 0x01,
		'RightButton': 0x02,
		'Cancel': 0x03,
		'MiddleButton': 0x04,
		'XButton1': 0x05,
		'XButton2': 0x06,
		'Back': 0x08,
		'Tab': 0x09,
		'Clear': 0x0C,
		'Return': 0x0D,
		'Shift': 0x10,
		'Control': 0x11,
		'Menu': 0x12,
		'Pause': 0x13,
		'Capital': 0x14,
		'Kana': 0x15,
		'Hangeul': 0x15,
		'Junja': 0x17,
		'Final': 0x18,
		'Hanja': 0x19,
		'Kanji': 0x19,
		'Escape': 0x1B,
		'Convert': 0x1C,
		'NonConvert': 0x1D,
		'Accept': 0x1E,
		'Modechange': 0x1F,
		'Space': 0x20,
		'Prior': 0x21,
		'Next': 0x22,
		'End': 0x23,
		'Home': 0x24,
		'Left': 0x25,
		'Up': 0x26,
		'Right': 0x27,
		'Down': 0x28,
		'Select': 0x29,
		'Print': 0x2A,
		'Execute': 0x2B,
		'Snapshot': 0x2C,
		'Insert': 0x2D,
		'Delete': 0x2E,
		'Help': 0x2F,
		'0': 0x30,
		'1': 0x31,
		'2': 0x32,
		'3': 0x33,
		'4': 0x34,
		'5': 0x35,
		'6': 0x36,
		'7': 0x37,
		'8': 0x38,
		'9': 0x39,
		'A': 0x41,
		'B': 0x42,
		'C': 0x43,
		'D': 0x44,
		'E': 0x45,
		'F': 0x46,
		'G': 0x47,
		'H': 0x48,
		'I': 0x49,
		'J': 0x4A,
		'K': 0x4B,
		'L': 0x4C,
		'M': 0x4D,
		'N': 0x4E,
		'O': 0x4F,
		'P': 0x50,
		'Q': 0x51,
		'R': 0x52,
		'S': 0x53,
		'T': 0x54,
		'U': 0x55,
		'V': 0x56,
		'W': 0x57,
		'X': 0x58,
		'Y': 0x59,
		'Z': 0x5A,
		'LeftWin': 0x5B,
		'RightWin': 0x5C,
		'Apps': 0x5D,
		'Sleep': 0x5f,
		'Numpad0': 0x60,
		'Numpad1': 0x61,
		'Numpad2': 0x62,
		'Numpad3': 0x63,
		'Numpad4': 0x64,
		'Numpad5': 0x65,
		'Numpad6': 0x66,
		'Numpad7': 0x67,
		'Numpad8': 0x68,
		'Numpad9': 0x69,
		'Multiply': 0x6A,
		'Add': 0x6B,
		'Separator': 0x6C,
		'Subtract': 0x6D,
		'Decimal': 0x6E,
		'Divide': 0x6F,
		'F1': 0x70,
		'F2': 0x71,
		'F3': 0x72,
		'F4': 0x73,
		'F5': 0x74,
		'F6': 0x75,
		'F7': 0x76,
		'F8': 0x77,
		'F9': 0x78,
		'F10': 0x79,
		'F11': 0x7A,
		'F12': 0x7B,
		'F13': 0x7C,
		'F14': 0x7D,
		'F15': 0x7E,
		'F16': 0x7F,
		'F17': 0x80,
		'F18': 0x81,
		'F19': 0x82,
		'F20': 0x83,
		'F21': 0x84,
		'F22': 0x85,
		'F23': 0x86,
		'F24': 0x87,
		'Numlock': 0x90,
		'Scroll': 0x91,
		'Oem-Nec-Equal': 0x92,
		'Oem-FJ-Jisho': 0x92,
		'Oem-FJ-Masshou': 0x93,
		'Oem-FJ-Touroku': 0x94,
		'Oem-FJ-Loya': 0x95,
		'Oem-FJ-Roya': 0x96,
		'LeftShift': 0xA0,
		'RightShift': 0xA1,
		'LeftControl': 0xA2,
		'RightControl': 0xA3,
		'LeftMenu': 0xA4,
		'RightMenu': 0xA5,
		'Browser-Back': 0xA6,
		'Browser-Forward': 0xA7,
		'Browser-Refresh': 0xA8,
		'Browser-Stop': 0xA9,
		'Browser-Search': 0xAA,
		'Browser-Favorites': 0xAB,
		'Browser-Home': 0xAC,
		'Volume-Mute': 0xAD,
		'Volume-Down': 0xAE,
		'Volume-Up': 0xAF,
		'Media-Next-Track': 0xB0,
		'Media-Prev-Track': 0xB1,
		'Media-Stop': 0xB2,
		'Media-Play-Pause': 0xB3,
		'launch-Mail': 0xB4,
		'launch-Media-Select': 0xB5,
		'launch-App1': 0xB6,
		'launch-App2': 0xB7,
		'Oem-1': 0xBA,
		'Oem-Plus': 0xBB,
		'Oem-Comma': 0xBC,
		'Oem-Minus': 0xBD,
		'Oem-Period': 0xBE,
		'Oem-2': 0xBF,
		'Oem-3': 0xC0,
		'Oem-4': 0xDB,
		'Oem-5': 0xDC,
		'Oem-6': 0xDD,
		'Oem-7': 0xDE,
		'Oem-8': 0xDF,
		'Oem-AX': 0xE1,
		'Oem-102': 0xE2,
		'ICO-Help': 0xE3,
		'ICO-00': 0xE4,
		'Processkey': 0xE5,
		'Ico-Clear': 0xE6,
		'Packet': 0xE7,
		'Oem-Reset': 0xE9,
		'Oem-Jump': 0xEA,
		'Oem-PA1': 0xEB,
		'Oem-PA2': 0xEC,
		'Oem-PA3': 0xED,
		'Oem-Wsctrl': 0xEE,
		'Oem-Cusel': 0xEF,
		'Oem-Attn': 0xF0,
		'Oem-Finish': 0xF1,
		'Oem-Copy': 0xF2,
		'Oem-Auto': 0xF3,
		'Oem-Enlw': 0xF4,
		'Oem-Backtab': 0xF5,
		'Attn': 0xF6,
		'Crsel': 0xF7,
		'Exsel': 0xF8,
		'Ereof': 0xF9,
		'Play': 0xFA,
		'Zoom': 0xFB,
		'Noname': 0xFC,
		'PA1': 0xFD,
		'Oem-Clear': 0xFE,
		}
KEY_NAMES = dict([(i[1], i[0]) for i in KEY_VALUES.items()])	# vkCode --> keyName

WM_SYSCOMMAND = 274
WM_GETTEXT = 13
WM_GETTEXTLENGTH = 0x000E

WM_SETTEXT = 12

SMTO_ABORTIFHUNG = 2
SC_CLOSE = 61536

SWP_NOSIZE = 1
SWP_NOMOVE = 2
SWP_NOZORDER = 4
SWP_NOACTIVATE = 16

ENUMWINDOWSPROC = WINFUNCTYPE(INT, HANDLE, LPARAM)

MY_TIMEOUT = 0.1
MY_SMTO_TIMEOUT = 2000
MY_MAX_CLASS_NAME = 64

BM_CLICK = 245

#****************************************************************************************************
#
#****************************************************************************************************
#HACK:(1)
#wine specific hack
#
#	KBDLLHOOKSTRUCT.flags is unusable when running in wine. same goes for user32.GetKeyboardState(),
#	user32.GetAsyncKeyState(). reason is: <quote>wine does not capture all system wide keys</quote>.
#
#	we emulate the functions as much as necesssary here and track keyboard state by hand. this makes VK_MENU,
#	VK_CONTROL and VK_SHIFT work. no way to track numlock, capslock and other toggle keys because we do not
#	know their initial states. side effect is that holding own keys ahead of L{KeyboardManager.start} will never be honored.
#
# ..then it is up to a keyboard hook to call _setKeyDown() when appropriate
#
#	@todo: synchronize this stuff
#	@warning: this hack overwrites user32.GetAsyncKeyState + user32.GetKeyboardState

_keyboardState = [0] * 256
KEY_IS_DOWN = 0x80


def _MyGetKeyboardState(pKeyboardState):
	"""our implementation of user32.GetKeyboardState"""
	arr = pKeyboardState._obj
	for n, i in enumerate(_keyboardState):
		arr[n] = i
	return TRUE
user32.GetKeyboardState = _MyGetKeyboardState

def _MyGetAsyncKeyState(vkCode):
	"""our implementation of user32.GetAsyncKeyState
	@note: you can not pass a string as in orig GetAsyncKeyState. only VK_* works
	"""
	if isinstance(vkCode, basestring):
		raise NotImplemetedError('hey! dont stretch this hack too far')
	return _keyboardState[vkCode]
user32.GetAsyncKeyState = _MyGetAsyncKeyState

def _setKeyDown(vkCode, flag):
	"""this method should always be called whenever a keyboard hook or mouse hook notices a key press/release
	@param vkCode: VK_*
	@param flag: (bool) True if the key was pressed, False if it was released
	"""
	value = KEY_IS_DOWN if flag else 0x00
	_keyboardState[vkCode] = value
	if vkCode in (VK_LCONTROL, VK_RCONTROL): _keyboardState[VK_CONTROL] = value
	elif vkCode in (VK_LMENU, VK_RMENU): _keyboardState[VK_MENU] = value
	elif vkCode in (VK_LSHIFT, VK_RSHIFT): _keyboardState[VK_SHIFT] = value

#HACK:(1)

#****************************************************************************************************
#
#****************************************************************************************************
class InputEvent(QtCore.QObject):
	def __init__(self,
				key=None,
				keyIsDown=False,
				steps=1,
				accept=False,
				parent=None
				):
		QtCore.QObject.__init__(self, parent)
		self.key = key
		self.keyIsDown = keyIsDown
		self.steps = steps
		self.accept = accept

#************************************************************************************
#
#************************************************************************************
UOI_NAME = 2

#TODO: test single application scopes
class SingleApplication(object):
	ScopeNone = 'None'
	ScopeGlobal = 'Global'
	ScopeSession = 'Session'
	ScopeDesktop = 'Desktop'
	Scopes = (
			ScopeNone,
			ScopeSession,
			ScopeDesktop,
			ScopeGlobal,
			)
	class ErrorOtherInstanceRunning(Exception): pass
	def __init__(self, magicString, scope=ScopeSession, parent=None):
		if scope not in self.Scopes: raise ValueError('invalid scope: %s' % scope)
		self.hMutex = None
		self.magicString = magicString
		self.scope = scope
		atexit.register(self.close)
	def start(self):
		magic = 'Local\\%s' % self.magicString
		if self.scope == self.ScopeNone:
			magic = None
		elif self.scope == self.ScopeGlobal:
			magic = 'Global\\%s' % self.magicString
		elif 	self.scope == self.ScopeSession:
			pass
		else:
			#NOTE: if anything goes wrong here we default to session unique. good idea or not?
			hDesktop = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
			if hDesktop:
				len = DWORD()
				user32.GetUserObjectInformationW(hDesktop, UOI_NAME, None, 0, byref(len))
				if len.value:
					p = create_unicode_buffer(len.value +1)
					if user32.GetUserObjectInformationW(hDesktop, UOI_NAME, p, sizeof(p), byref(len)):
						magic = '%s\\%s' % (magic, p.value)
		if magic is not None:
			self.hMutex = kernel32.CreateMutexA(None, 1, magic)
			if GetLastError() in (ERROR_INVALID_HANDLE, ERROR_ACCESS_DENIED):
				self.close()
				raise self.ErrorOtherInstanceRunning()
	def close(self, closeFunc=kernel32.CloseHandle):	# need to hold reference to CloseHandle here. we get garbage collected otherwise
		if self.hMutex is not None:
			closeFunc(self.hMutex)
			self.hMutex = None

#****************************************************************************************************
# message methods
#****************************************************************************************************
def sendMessageTimeout(hwnd, msg, wParam,lParam, isUnicode=True):
	result = DWORD()
	if isUnicode:
		user32.SendMessageTimeoutW(hwnd, msg, wParam, lParam, SMTO_ABORTIFHUNG, MY_SMTO_TIMEOUT, byref(result))
	else:
		user32.SendMessageTimeoutA(hwnd, msg, wParam, lParam, SMTO_ABORTIFHUNG, MY_SMTO_TIMEOUT, byref(result))
	return result.value

def postMessage(hwnd,msg,wp,lp,isUnicode=True):
	if isUnicode:
		return user32.PostMessageW(hwnd,msg,wp,lp)
	else:
		return user32.PostMessageA(hwnd,msg,wp,lp)


#****************************************************************************************************
# window methods
#****************************************************************************************************
class WindowHook(QtCore.QObject):
	windowDestroyed = QtCore.pyqtSignal(int)
	windowCreated = QtCore.pyqtSignal(int)
	windowLostForeground = QtCore.pyqtSignal(int)
	windowGainedForeground = QtCore.pyqtSignal(int)

	def __init__(self, parent=None, timeout=0.2):
		QtCore.QObject.__init__(self, parent)
		self._isRunning = False
		self._hwndForeground = 0
		self._hwnds = []
		self._timeout = timeout
		self._timer = QtCore.QTimer(self)
		self._timer.setInterval(self._timeout * 1000)
		self._timer.timeout.connect(self._run)
	def stop(self):
		self._timer.stop()
	def start(self):
		self._timer.start()
	def _run(self):
		hwnds = [hwnd for hwnd in windowChildren(None)]
		hwndsDestroyed = [hwnd for hwnd in self._hwnds if hwnd not in hwnds]
		hwndsCreated = [hwnd for hwnd in hwnds if hwnd not in self._hwnds]
		self._hwnds = hwnds
		for hwnd in hwndsDestroyed:
			self.windowDestroyed.emit(hwnd)
		for hwnd in hwndsCreated:
			self.windowCreated.emit(hwnd)
		hwnd = windowForeground()
		if hwnd in self._hwnds and hwnd != self._hwndForeground:
			self.windowLostForeground.emit(self._hwndForeground)
			self.windowGainedForeground.emit(hwnd)
			self._hwndForeground = hwnd

def windowChildren(hwndParent=None):
	"""returns a the list of child windows of a window
	@param hwndParent: handle of the window or None to list all toplevel windows
	@return: (list) of windows of the specified parent
	"""
	L= []
	def f(hwnd, lp):
		L.append(hwnd)
		return TRUE
	p = ENUMWINDOWSPROC(f)
	user32.EnumWindows(p, 0) if not hwndParent else user32.EnumChildWindows(hwndParent, p, 0)
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
			if user32.GetParent(child) == hwnd:
				for x in walker(child, level +1):
					yield x
	return walker(hwnd)

def windowGetTextLength(hwnd):
	n = user32.GetWindowTextLengthW(hwnd)
	if not n:
		result = DWORD()
		user32.SendMessageTimeoutW(hwnd, WM_GETTEXTLENGTH, 0, 0, SMTO_ABORTIFHUNG, MY_SMTO_TIMEOUT, byref(result))
		n = result.value
	return n

#TODO: we get unhnadled read access page faults when trying to query less than what GetWindowTextLen() returns. no idea why. ansi version works.
#				unicode version segfaults. so ..as a workaround we don't query at all '' if len(text) exceeds maxSize. maybe later we can introduce a new
#				keyword "size".
def windowGetText(hwnd, maxSize=-1):
	"""returns the window title of the specified window
	@param hwnd: handle of the window
	 @param maxSize: (int) maximum size of text to retrieve. if -1 text is retrieved unconditionally. else only text <= maxSize is retrieved
	@return: (str)
	"""
	if not hwnd or maxSize == 0: return ''

	#NOTE: see: [ http://blogs.msdn.com/b/oldnewthing/archive/2003/08/21/54675.aspx ] "the secret live of GetWindowtext" for details

	# try GetWindowText first
	nChars = user32.GetWindowTextLengthW(hwnd)
	#nChars = nChars if maxSize < 0 else min(nChars, maxSize)		## this segfaults in TableCrab
	if nChars:
		if maxSize > 0 and nChars > maxSize:
			return  ''
		p = create_unicode_buffer(nChars +1)
		if user32.GetWindowTextW(hwnd, p, sizeof(p)):
			return p.value

	# some text can only be retrieved by WM_GETTEXT, so here we go
	result = DWORD()
	nChars = sendMessageTimeout(hwnd, WM_GETTEXTLENGTH, 0, 0)
	##nChars = nChars if maxSize < 0 else min(nChars, maxSize)		## this segfaults in TableCrab
	if nChars:
		if maxSize > 0 and nChars > maxSize:
			return ''
		p = create_unicode_buffer(nChars +1)
		sendMessageTimeout(hwnd, WM_GETTEXT, sizeof(p), p)
		return p.value
	return ''

def windowGetClassName(hwnd):
	"""returns the class name of the specified window
	@param hwnd: handle of the window
	@return: (str)
	"""
	if not hwnd: return ''
	p = create_unicode_buffer(MY_MAX_CLASS_NAME)
	if not user32.GetClassNameW(hwnd, p, sizeof(p)):
		#NOTE: GetClassName() sometimes fails for some unknown reason, so we return '' here
		return ''
	return p.value

def windowGetRect(hwnd):
	"""returns the window rect of the specified window
	@param hwnd: handle of the window
	@return: (QRect)
	"""
	if not hwnd: return QtCore.QRect(-1, -1, -1, -1)
	rc = RECT()
	user32.GetWindowRect(hwnd, byref(rc))
	return QtCore.QRect(rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top)

def windowGetClientRect(hwnd):
	"""returns the window rect of the specified window
	@param hwnd: handle of the window
	@return: (QRect)
	"""
	if not hwnd: return QtCore.QRect(-1, -1, -1, -1)
	rc = RECT()
	user32.GetClientRect(hwnd, byref(rc))
	return QtCore.QRect(rc.left, rc.top, abs(rc.right - rc.left), abs(rc.bottom - rc.top) )

def windowGetParent(hwnd):
	return user32.GetParent(hwnd)

def windowGetTopLevelParent(hwnd):
	parent = hwnd
	while parent:
		tmp_parent = user32.GetParent(parent)
		if not tmp_parent: break
		parent = tmp_parent
	return parent

def windowScreenPointToClientPoint(hwnd, point):
	"""converts a point in screen coordiantes to point in window client coordinates
	@param pt: (QPOint)
	@return: (QPoint)
	"""
	pt = POINT( point.x(), point.y() )
	user32.ScreenToClient(hwnd, byref(pt) )
	return QtCore.QPoint(pt.x, pt.y)

def windowClientPointToScreenPoint(hwnd, point):
		"""converts a point in client coordiantes of a window screen coordinates
		@param pt: (QPoint)
		@return: (QPoint)
		"""
		pt = POINT( point.x(), point.y() )
		user32.ClientToScreen(hwnd, byref(pt) )
		return QtCore.QPoint(pt.x, pt.y)

def windowIsVisible(hwnd):
	return bool(user32.IsWindowVisible(hwnd))

def windowIsEnabled(hwnd):
	return bool(user32.IsWindowEnabled(hwnd))

def windowFromPoint(point):
	"""returns the handl of the window at the specified point"""
	return user32.WindowFromPoint( POINT( point.x(), point.y() ) )

def windowForeground():
	return user32.GetForegroundWindow()

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
		if user32.SendNotifyMessageW(hwndButton, BM_CLICK, 0, 0):
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

def windowSetText(hwnd, text='', isUnicode=True):
		"""returns the window title of the specified window
		@param hwnd: handle of the window
		@todo: we currently send ANSI text only.
		@return: (str)
		"""
		if not hwnd: raise ValueError('can not set text of desktop window')
		sendMessageTimeout(hwnd, WM_SETTEXT, 0, text, isUnicode=isUnicode)

def windowClose(hwnd):
	"""closes the specified window
	@param hwnd: handle of the window
	@return: None
	"""
	if not hwnd: raise ValueError('can not close desktop window')
	result = DWORD()
	user32.SendMessageTimeoutW(
			hwnd,
			WM_SYSCOMMAND,
			SC_CLOSE,
			0,
			SMTO_ABORTIFHUNG,
			MY_SMTO_TIMEOUT,
			byref(result)
			)

def windowCheckboxIsChecked(hwnd):
	result = DWORD()
	user32.SendMessageTimeoutW(
			hwnd,
			BM_GETSTATE,
			0,
			0,
			SMTO_ABORTIFHUNG,
			MY_SMTO_TIMEOUT,
			byref(result)
			)
	return bool( result.value & BST_CHECKED )

def windowGetPos(hwnd):
	if not hwnd:
		return QtCore.QPoint(0, 0)
	hwndParent = windowGetParent(hwnd)
	if not hwndParent:
		return windowGetRect(hwnd).topLeft()
	point = windowClientPointToScreenPoint(hwnd, QtCore.QPoint(0, 0) )
	return windowScreenPointToClientPoint(hwndParent, point)



#NOTE: wine is not sending enter- exitsizemove messages. that is why PokerStars tables do not get repainted
# on resizing. found that manually wrapping resizes in in enter- exitsizemove messages around resizes
# triggers repainting as expected
WM_ENTERSIZEMOVE = 0x0231
WM_EXITSIZEMOVE = 0x0232
def windowSetSize(hwnd, size, sendSizeMove=False):
	"""sets size of the specified window
	@param hwnd: handle of the window
	@param size: (QSize)
	@return: None
	"""
	if not hwnd: raise ValueError('can not set posAndSize of desktop window')
	#NOTE: SetWindowPos broken in wine 1.1.42 - wine 1.3.X
	if sendSizeMove:
		user32.SendNotifyMessageA(hwnd, WM_ENTERSIZEMOVE, 0, 0)
	user32.SetWindowPos(hwnd, None, 0, 0, size.width(), size.height(), SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE)
	if sendSizeMove:
		user32.SendNotifyMessageA(hwnd, WM_EXITSIZEMOVE, 0, 0)


def windowSetClientSize(hwnd, size, sendSizeMove=False):
	"""adjusts the specified windows size to fit the specified size of the client area
	@param hwnd: handle of the window
	@param size: (QSize)
	@return: None
	"""
	if not hwnd: raise ValueError('can not set clientSize of desktop window')
	rect = windowGetRect(hwnd)
	rectCli = windowGetClientRect(hwnd)
	newW = rect.width() - rectCli.width() + size.width()
	newH = rect.height() - rectCli.height() + size.height()
	size = QtCore.QSize(newW, newH)
	windowSetSize(hwnd, size, sendSizeMove=sendSizeMove)

def windowIsSameProcess(hwnd, hwndOther):
	pid = DWORD()
	user32.GetWindowThreadProcessId(hwnd, byref(pid))
	pidOther = DWORD()
	user32.GetWindowThreadProcessId(hwndOther, byref(pidOther))
	return pid.value == pidOther.value

# ################################################
# alternative: use GetModuleFileNameEx to query executable filepath
# don't like it too much though. we would rely on this entirely. for example any file name
# change breaks us
#
#MAX_PATH = 260
#psapi = windll.psapi
#PROCESS_VM_READ = 16
#PROCESS_QUERY_INFORMATION = 1024
#GetModuleFileNameEx = None
## looks like GetModuleFileNameEx is a mooving target ..try to catch it
#try:
#	GetModuleFileNameEx = kernel32.GetModuleFileNameExW
#except AttributeError:
#	try:
#		GetModuleFileNameEx = psapi.GetModuleFileNameExW
#	except AttributeError:
#		GetModuleFileNameEx = psapi.K32GetModuleFileNameExW
#
#
#def windowGetExecutable(hwnd):
#	pId = DWORD()
#	user32.GetWindowThreadProcessId(hwnd, byref(pId))
#	if not pId:
#		return ''
#	hProcess = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pId)
#	if not hProcess: print FormatError(GetLastError())
#	try:
#		p= create_unicode_buffer(MAX_PATH+1)
#		GetModuleFileNameEx(hProcess, None, p, sizeof(p))
#	finally:
#		kernel32.CloseHandle(hProcess)
#	return p.value

#****************************************************************************************************
# mouse methods
#****************************************************************************************************
MouseButtonLeft = 'left'
MouseButtonRight = 'right'
MouseButtonMiddle = 'middle'
MouseWheelUp = '<MouseWheelUp>'
MouseWheelDown = '<MouseWheelDown>'

#NOTE: wine dies not orovide this info so we have to keep track ourselves
_mouseButtonsDown = []

#***********************************************************************************
# SendInput in all its glory
#
# we have to use SendInput() to simulate mouse events cos PokerStars bet slider
# seems to ignore everything send via user32.mouse_event(). we are not removing
# all the user32.mouse_event() methods because we may if we need them at some
# point.
#***********************************************************************************
MOUSEEVENTF_MOVE = 0x1
MOUSEEVENTF_LEFTDOWN = 0x2
MOUSEEVENTF_LEFTUP = 0x4
MOUSEEVENTF_RIGHTDOWN = 0x8
MOUSEEVENTF_RIGHTUP = 0x10
MOUSEEVENTF_MIDDLEDOWN = 0x20
MOUSEEVENTF_MIDDLEUP = 0x40
MOUSEEVENTF_XDOWN = 0x80
MOUSEEVENTF_XDOWN = 0x100
MOUSEEVENTF_WHEEL = 0x800
MOUSEEVENTF_MOVE_NOCOALESCE = 0x2000
MOUSEEVENTF_VIRTUALDESK = 0x4000
MOUSEEVENTF_ABSOLUTE = 0x8000

INPUT_MOUSE = 0x0
INPUT_KEYBOARD = 0x1
INPUT_HARDWARE = 0x2

KEYEVENTF_EXTENDEDKEY = 0x1
KEYEVENTF_KEYUP = 0x2
KEYEVENTF_SCANCODE = 0x8
KEYEVENTF_UNICODE = 0x4

SM_CXSCREEN = 0
SM_CYSCREEN = 1

class MOUSEINPUT(Structure):
	_fields_ = [
		('dx', LONG),
		('dy', LONG),
		('mouseData', DWORD),
		('dwFlags', DWORD),
		('time', DWORD),
		('dwExtraInfo', POINTER(ULONG))
		]
class KEYBDINPUT(Structure):
	_fields_ = [
		('wVk', WORD),
		('wScan', WORD),
		('dwFlags', DWORD),
		('time', DWORD),
		('dwExtraInfo', POINTER(ULONG))
		]
class HARDWAREINPUT(Structure):
	_fields_ = [
		('uMsg', DWORD),
		('wParamL', WORD),
		('wParamH', WORD),
		]
class _U(Union):
	_fields_ = [
		('mi', MOUSEINPUT),
		('ki', KEYBDINPUT),
		('hi', HARDWAREINPUT)
		]
class INPUT(Structure):
	_fields_ = [
		('type', DWORD),
		('u', _U),
		]
	_anonymous_ = ("u",)

#TODO: KeyboardInput() not used in TableCrab
class KeyboardInput(object):
	def __init__(self):
		self._input = []

	def keyDown(self, vk):
		ki = KEYBDINPUT()
		ki.wVK = vk
		ki.wScan = user32.MapVirtualKeyW(vk, 0)
		input = INPUT()
		input.type = INPUT_KEYBOARD
		input.ki = ki
		self._input.append(input)
		return self

	def keyUp(self, vk):
		ki = KEYBDINPUT()
		ki.wVK = vk
		ki.wScan = user32.MapVirtualKeyW(vk, 0)
		ki.dwFlags = KEYEVENTF_KEYUP
		input = INPUT()
		input.type = INPUT_KEYBOARD
		input.ki = ki
		self._input.append(input)
		return self

	def keyPress(self, vk):
		self.keyDown(vk)
		self.keyUp(vk)
		return self

	def send(self):
		if not self._input:
			raise ValueError('No input to send')
		arr = (INPUT*len(self._input))(*self._input)
		self._input = []
		user32.SendInput(len(arr), byref(arr), sizeof(INPUT))
		return self


class MouseInput(object):
	def __init__(self):
		self._input = []

	def _addMousePoint(self, event, point, hwnd=None):
		point = windowClientPointToScreenPoint(hwnd, point) if hwnd else point
		point = pointToWorldCoords(point)
		mi = MOUSEINPUT(
				dx=point.x(),
				dy=point.y(),
				dwFlags= event | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE_NOCOALESCE,
				time=getCurrentTime(),		#NOTE: have to set this. wine does not set it in SendInput()
														#          and looks like it has unwanted side effects in PS client
														#          like clicks getting ignored. filed a report [http://bugs.winehq.org/show_bug.cgi?id=24435]
				)
		input = INPUT()
		input.type = INPUT_MOUSE
		input.mi = mi
		self._input.append(input)

	def send(self, restoreCursor=False):
		if not self._input:
			raise ValueError('No input to send')
		if restoreCursor:
			pointLast = mouseGetPos()
		arr = (INPUT*len(self._input))(*self._input)
		self._input = []
		user32.SendInput(len(arr), byref(arr), sizeof(INPUT))
		#NOTE:
		# 1) wine: the mouse cursor is always moved around. SendInput() is very inaccurate
		#     so we use mouseSetPos() to restore the cursor position.
		# 2) winXP: the cursor is not moved around
		if restoreCursor and pointLast != mouseGetPos():
			mouseSetPos(pointLast, hwnd=None)
		return self

	def leftDown(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_LEFTDOWN, point, hwnd=hwnd)
		return self
	def leftUp(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_LEFTUP, point, hwnd=hwnd)
		return self
	def leftClick(self, point, hwnd=None):
		self.move(point, hwnd=hwnd)
		self.leftDown(point, hwnd=hwnd)
		self.leftUp(point, hwnd=hwnd)
		return self
	def leftClickDouble(self, point, hwnd=None):
		self.move(point, hwnd=hwnd)
		self.leftDown(point, hwnd=hwnd)
		self.leftUp(point, hwnd=hwnd)
		self.leftDown(point, hwnd=hwnd)
		self.leftUp(point, hwnd=hwnd)
		return self

	def rightDown(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_RIGHTDOWN, point, hwnd=hwnd)
		return self
	def rightUp(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_RIGHTTUP, point, hwnd=hwnd)
		return self
	def rightClick(self, point, hwnd=None):
		self.move(point, hwnd=hwnd)
		self.rightDown(point, hwnd=hwnd)
		self.rightUp(point, hwnd=hwnd)
		return self

	def middleDown(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_MIDDLEDOWN, point, hwnd=hwnd)
		return self
	def middleUp(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_MIDDLETUP, point, hwnd=hwnd)
		return self
	def middleClick(self, point, hwnd=None):
		self.move(point, hwnd=hwnd)
		self.middleDown(point, hwnd=hwnd)
		self.middleUp(point, hwnd=hwnd)
		return self
	def move(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_MOVE, point, hwnd=hwnd)
		return self
	#TODO: MouseInput.wheelScroll() not tested
	def wheelScroll(self, nSteps):
		mi = MOUSEINPUT(
				dwFlags= MOUSEEVENTF_WHEEL | MOUSEEVENTF_ABSOLUTE,
				mouseData=nSteps,
				)
		input = INPUT()
		input.type = INPUT_MOUSE
		input.mi = mi
		self._input.append(input)
		return self

	def leftDrag(self, pointStart, pointEnd, hwnd=None):
		self.move(pointStart, hwnd=hwnd)
		self.leftDown(pointStart, hwnd=hwnd)
		self.move(pointEnd, hwnd=hwnd)
		self.leftUp(pointEnd, hwnd=hwnd)
		return self


def mouseButtonsDown():
	"""checks if any mouse buttons are down
	@return: (bool) True if any of the mouse buttons are down, False otherwise
	"""
	return user32.GetAsyncKeyState(KEY_VALUES['LeftButton'] & KEY_IS_DOWN) or \
				user32.GetAsyncKeyState(KEY_VALUES['RightButton'] & KEY_IS_DOWN) or \
				user32.GetAsyncKeyState(KEY_VALUES['MiddleButton'] & KEY_IS_DOWN)

def mouseButtonIsDown(button):
	return button in _mouseButtonsDown

def mousePressButton(button):
	"""presses the specified mouse button at the current mouse position
	@param button: (Button*)
	"""
	# determine button to set down
	if mouseButtonIsDown(button): return
	if button == MouseButtonLeft:
		bt = MOUSEEVENTF_LEFTDOWN
	elif button == MouseButtonRight:
		bt = MOUSEEVENTF_RIGHTDOWN
	elif button == MouseButtonMiddle:
		bt = MOUSEEVENTF_MIDDLEDOWN
	else:
		raise ValueError('no such mouse button: %s' % button)
	point = mouseGetPos()
	user32.mouse_event(bt | MOUSEEVENTF_ABSOLUTE, point.x(), point.y(), 0, None)

def mouseReleaseButton(button):
	"""releases the specified mouse button at the current mouse position
	@param button: (Button)
	"""
	# determine button to set up
	if button not in _mouseButtonsDown: return
	if button == MouseButtonLeft:
		bt = MOUSEEVENTF_LEFTUP
	elif button == MouseButtonRight:
		bt = MOUSEEVENTF_RIGHTUP
	elif button == MouseButtonMiddle:
		bt = MOUSEEVENTF_MIDDLEUP
	else:
		raise ValueError('no such mouse button: %s' % button)
	point = mouseGetPos()
	user32.mouse_event(bt | MOUSEEVENTF_ABSOLUTE, point.x(), point.y(), 0, None)

def mouseClickPoint(button, nClicks=1, point=None, hwnd=None):
	'''clicks a point with the desired mouse button
	@param button: (str) button to click: (Button*)
	@param nClicks: (int) number of times to click (2 for a double-click)
	@param pt: (QPoint) absolute coordinates to click. if None, the current cursor pos is taken
	@return: None
	@todo: impl proper double click delay. GetSystemMetrics could do the trick if there is something like a min-double-click-interval defined
	@NOTE: the mouse is moved to the specified position in the call
	'''
	if _mouseButtonsDown: return
	# move mouse to point
	if point is not None:
		mouseSetPos(point, hwnd=hwnd)
	# click button
	rng = list(range(nClicks))
	while rng:
		rng.pop()
		mousePressButton(button)
		mouseReleaseButton(button)
		if rng:
			time.sleep(0.1)

def mouseClickLeft(point, hwnd=None):
	"""clicks the left mouse button at the specified point"""
	return mouseClickPoint(MouseButtonLeft, point=point, nClicks=1, hwnd=hwnd)
def mouseClickLeftDouble(point, hwnd=None):
	"""double clicks the left mouse button at the specified point"""
	return mouseClickPoint(MouseButtonLeft, point=point, nClicks=2, hwnd=hwnd)
def mouseClickRight(point, hwnd=None):
	"""clicks the right mouse button at the specified point"""
	return mouseClickPoint(MouseButtonRight, point=point, nClicks=1, hwnd=hwnd)
def mouseClickRightDouble(point, hwnd=None):
	"""double clicks the right mouse button at the specified point"""
	return mouseClickPoint(MouseButtonRight, point=point, nClicks=2, hwnd=hwnd)
def mouseClickMiddle(point, hwnd=None):
	"""clicks the middle mouse button at the specified point"""
	return self.mouseClickPoint(MouseButtonMiddle, point=point, nClicks=1, hwnd=None)
def mouseClickMiddleDouble(point, hwnd=None):
	"""double clicks the middle mouse button at the specified point"""
	return mouseClickPoint(MouseButtonMiddle, point=point, nClicks=2, hwnd=hwnd)

def mouseGetPos():
	'''returns the current position of the mouse pointer
	@return: (QPoint) coordinates of the mouse cursor
	'''
	pt = POINT()
	user32.GetCursorPos(byref(pt))
	return QtCore.QPoint(pt.x, pt.y)

def mouseSetPos(point, step=4, hwnd=None):
	"""moves the mouse pointer to the specified position
	@param pt: (tuple) point containing the coordiantes to move the mouse pointer to (in screen coordiantes)
	"""
	#NOTE: for some reason neither user32.mouse_event() not user32.SendInput() have any effect here (linux/wine).
	#           the only way i can get this to work is to move the cursor stepwise to its destination?!?
	if hwnd is not None:
		point = windowClientPointToScreenPoint(hwnd, point)
	ptX, ptY = point.x(), point.y()
	point2 = mouseGetPos()
	curX, curY = point2.x(), point2.y()
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
		user32.SetCursorPos(pt)

def mouseDoubleClickTime():
	return user32.GetDoubleClickTime()

class MouseHook(QtCore.QObject):
	"""win32 keyboard manager implementation
	@event EvtMouseButtonUp: event triggerered when a mouse  button is pressed. arg = Button*
	@event EvtMouseButtonDown: event triggerered when a mosue button is released. arg = Button*
	@event EvtMouseWheelScrolled: event triggerered when the mosue wheel is scrolled. arg = stepsScrolled
	"""

	inputEvent = QtCore.pyqtSignal(QtCore.QObject)

	def __init__(self, parent=None, eventHandler=None):
		"""
		@param cb: (function) event handler
		"""
		QtCore.QObject.__init__(self, parent)
		self._isStarted = False
		self._hHook = None
		self._pHookProc = MOUSEHOOKPROCLL(self._hookProc)
		self._eventHandler = eventHandler

	def _hookProc(self, code, wParam, lParam):
		"""private method, MOUSEHOOKPROCLL implementation"""

		if code == HC_ACTION:
			if wParam == WM_LBUTTONDOWN:
				_setKeyDown(KEY_VALUES['LeftButton'], True)
			elif wParam == WM_LBUTTONUP:
				_setKeyDown(KEY_VALUES['LeftButton'], False)
			elif wParam == WM_RBUTTONDOWN:
				_setKeyDown(KEY_VALUES['RightButton'], True)
			elif wParam == WM_RBUTTONUP:
				_setKeyDown(KEY_VALUES['RightButton'], False)
			elif wParam == WM_MBUTTONDOWN:
				_setKeyDown(KEY_VALUES['MiddleButton'], True)
			elif wParam == WM_MBUTTONUP:
				_setKeyDown(KEY_VALUES['MiddleButton'], False)
			elif wParam == WM_MOUSEWHEEL:
				mouseInfo = MSLLHOOKSTRUCT.from_address(lParam)
				wheelDelta = GET_WHEEL_DELTA_WPARAM(mouseInfo.mouseData)
				nSteps = wheelDelta / WHEEL_DELTA
				key = MouseWheelUp if nSteps >= 0 else MouseWheelDown
				if nSteps:
					e = InputEvent(key=key, steps=abs(nSteps), accept=False, keyIsDown=True, parent=self)
					self.inputEvent.emit(e)
					if e.accept:
						return TRUE
		return user32.CallNextHookEx(self._hHook, code, wParam, lParam)

	def isStarted(self):
		"""cheks if the mouse manager is started"""
		return self._isStarted

	def start(self):
		"""starts the mouse manager"""
		if self._hHook is None:
			self._hHook = user32.SetWindowsHookExW(
				WH_MOUSE_LL,
				self._pHookProc,
				kernel32.GetModuleHandleA(None),
				0
				)
			if not self._hHook:
				self._hHook = None
				raise WindowsError(GetLastError())

	def stop(self):
		"""stops the mouse manager"""
		if self._hHook is not None:
			hHook, self._hHook = self._hHook, None
			if not user32.UnhookWindowsHookEx(hHook):
				raise WindowsError(GetLastError())

#***********************************************************************************
# keyboard methods
#***********************************************************************************
class KeyboardHook(QtCore.QObject):
	"""win32 keyboard hook implementation"""

	inputEvent = QtCore.pyqtSignal(QtCore.QObject)

	def __init__(self, parent=None, eventHandler=None):
		"""
		@param cb: (function) event handler
		"""
		QtCore.QObject.__init__(self, parent)
		self._isStarted = False
		self._hHook = None
		self._pHookProc = KEYBHOOKPROCLL(self._hookProc)
		self._eventHandler = eventHandler

	def _hookProc(self, code, wParam, lParam):
		"""private method, KEYBHOOKPROCLL implementation"""
		if code == HC_ACTION:
			keyInfo = KBDLLHOOKSTRUCT.from_address(lParam)
			keyIsDown = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
			if keyIsDown:
				#HACK:(1)
				_setKeyDown(keyInfo.vkCode, True)
				#<--HACK:(1)
			keyboardState = (c_ubyte*256)()
			user32.GetKeyboardState(byref(keyboardState))
			key = self._keyFromKeyboardState(keyboardState)
			if not keyIsDown:
				#HACK:(1)
				_setKeyDown(keyInfo.vkCode, False)
				#<--HACK:(1)
			if key:
				e = InputEvent(key=key, steps=1, keyIsDown=keyIsDown, accept=False, parent=self)
				self.inputEvent.emit(e)
				if e.accept:
					return TRUE
		return user32.CallNextHookEx(self._hHook, code, wParam, lParam)

	def _keyFromKeyboardState(self, keyboardState):
		"""@param keyboardState: (c_ubyte*256) holding a keyboard state"""
		result = []
		for vkCode, flag in enumerate(keyboardState):
			if flag & KEY_IS_DOWN:
				if vkCode in (			# ignore these keys,
						VK_CONTROL,		# we pass left or right representation only
						VK_MENU,			# we pass left or right representation only
						VK_SHIFT,			# we can not know lock state
						VK_SCROLL,		# we can not know lock state
						VK_CAPITAL,		# we can not know lock state
						VK_NUMLOCK,	# we can not know lock state
						):
					continue
				keyName = KEY_NAMES.get(vkCode, None)
				if keyName is not None:
					result.append(keyName)
		if result:
			return '<%s>' % '+'.join(result)
		return ''

	def isStarted(self):
		"""cheks if the keyboard manager is started"""
		return self._isStarted

	def start(self):
		"""starts the keyboard manager"""
		if self._hHook is None:
			self._hHook = user32.SetWindowsHookExW(
				WH_KEYBOARD_LL,
				self._pHookProc,
				kernel32.GetModuleHandleA(None),
				0
				)
			if not self._hHook:
				self._hHook = None
				raise WindowsError(GetLastError())

	def stop(self):
		"""stops the keyboard manager"""
		if self._hHook is not None:
			hHook, self._hHook = self._hHook, None
			if not user32.UnhookWindowsHookEx(hHook):
				raise WindowsError(GetLastError())



