
import time
from ctypes import *
from ctypes.wintypes import *

user32 = windll.user32
kernel32 = windll.kernel32

from PyQt4 import QtCore, QtGui

#**************************************************************
#
#**************************************************************

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
VK_CAPITAL = 014
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
KEYBOARD_LAYOUT_NAMES= {		# taken from: MSDN - "Code Page Identifiers"
		37: 'IBM EBCDIC US-Canada',
		437: 'OEM United States',
		500: 'IBM EBCDIC International',
		708: 'Arabic (ASMO 708)',
		709: 'Arabic (ASMO-449+, BCON V4)',
		710: 'Arabic - Transparent Arabic',
		720: 'Arabic (Transparent ASMO); Arabic (DOS)',
		737: 'OEM Greek (formerly 437G); Greek (DOS)',
		775: 'OEM Baltic; Baltic (DOS)',
		850: 'OEM Multilingual Latin 1; Western European (DOS)',
		852: 'OEM Latin 2; Central European (DOS)',
		855: 'OEM Cyrillic (primarily Russian)',
		857: 'OEM Turkish; Turkish (DOS)',
		858: 'OEM Multilingual Latin 1 + Euro symbol',
		860: 'OEM Portuguese; Portuguese (DOS)',
		861: 'OEM Icelandic; Icelandic (DOS)',
		862: 'OEM Hebrew; Hebrew (DOS)',
		863: 'OEM French Canadian; French Canadian (DOS)',
		864: 'OEM Arabic; Arabic (864)',
		865: 'OEM Nordic; Nordic (DOS)',
		866: 'OEM Russian; Cyrillic (DOS)',
		869: 'OEM Modern Greek; Greek, Modern (DOS)',
		870: 'IBM EBCDIC Multilingual/ROECE (Latin 2); IBM EBCDIC Multilingual Latin 2',
		874: 'ANSI/OEM Thai (same as 28605, ISO 8859-15); Thai (Windows)',
		875: 'IBM EBCDIC Greek Modern',
		932: 'ANSI/OEM Japanese; Japanese (Shift-JIS)',
		936: 'ANSI/OEM Simplified Chinese (PRC, Singapore); Chinese Simplified (GB2312)',
		949: 'ANSI/OEM Korean (Unified Hangul Code)',
		950: 'ANSI/OEM Traditional Chinese (Taiwan; Hong Kong SAR, PRC); Chinese Traditional (Big5)',
		1026: 'IBM EBCDIC Turkish (Latin 5)',
		1047: 'IBM EBCDIC Latin 1/Open System',
		1140: 'IBM EBCDIC US-Canada (037 + Euro symbol); IBM EBCDIC (US-Canada-Euro)',
		1141: 'IBM EBCDIC Germany (20273 + Euro symbol); IBM EBCDIC (Germany-Euro)',
		1142: 'IBM EBCDIC Denmark-Norway (20277 + Euro symbol); IBM EBCDIC (Denmark-Norway-Euro)',
		1143: 'IBM EBCDIC Finland-Sweden (20278 + Euro symbol); IBM EBCDIC (Finland-Sweden-Euro)',
		1144: 'IBM EBCDIC Italy (20280 + Euro symbol); IBM EBCDIC (Italy-Euro)',
		1145: 'IBM EBCDIC Latin America-Spain (20284 + Euro symbol); IBM EBCDIC (Spain-Euro)',
		1146: 'IBM EBCDIC United Kingdom (20285 + Euro symbol); IBM EBCDIC (UK-Euro)',
		1147: 'IBM EBCDIC France (20297 + Euro symbol); IBM EBCDIC (France-Euro)',
		1148: 'IBM EBCDIC International (500 + Euro symbol); IBM EBCDIC (International-Euro)',
		1149: 'IBM EBCDIC Icelandic (20871 + Euro symbol); IBM EBCDIC (Icelandic-Euro)',
		1200: 'Unicode UTF-16, little endian byte order (BMP of ISO 10646); available only to managed applications',
		1201: 'Unicode UTF-16, big endian byte order; available only to managed applications',
		1250: 'ANSI Central European; Central European (Windows)',
		1251: 'ANSI Cyrillic; Cyrillic (Windows)',
		1252: 'ANSI Latin 1; Western European (Windows)',
		1253: 'ANSI Greek; Greek (Windows)',
		1254: 'ANSI Turkish; Turkish (Windows)',
		1255: 'ANSI Hebrew; Hebrew (Windows)',
		1256: 'ANSI Arabic; Arabic (Windows)',
		1257: 'ANSI Baltic; Baltic (Windows)',
		1258: 'ANSI/OEM Vietnamese; Vietnamese (Windows)',
		1361: 'Korean (Johab)',
		10000: 'MAC Roman; Western European (Mac)',
		10001: 'Japanese (Mac)',
		10002: 'MAC Traditional Chinese (Big5); Chinese Traditional (Mac)',
		10003: 'Korean (Mac)',
		10004: 'Arabic (Mac)',
		10005: 'Hebrew (Mac)',
		10006: 'Greek (Mac)',
		10007: 'Cyrillic (Mac)',
		10008: 'MAC Simplified Chinese (GB 2312); Chinese Simplified (Mac)',
		10010: 'Romanian (Mac)',
		10017: 'Ukrainian (Mac)',
		10021: 'Thai (Mac)',
		10029: 'MAC Latin 2; Central European (Mac)',
		10079: 'Icelandic (Mac)',
		10081: 'Turkish (Mac)',
		10082: 'Croatian (Mac)',
		12000: 'Unicode UTF-32, little endian byte order; available only to managed applications',
		12001: 'Unicode UTF-32, big endian byte order; available only to managed applications',
		20000: 'CNS Taiwan; Chinese Traditional (CNS)',
		20001: 'TCA Taiwan',
		20002: 'Eten Taiwan; Chinese Traditional (Eten)',
		20003: 'IBM5550 Taiwan',
		20004: 'TeleText Taiwan',
		20005: 'Wang Taiwan',
		20105: 'IA5 (IRV International Alphabet No. 5, 7-bit); Western European (IA5)',
		20106: 'IA5 German (7-bit)',
		20107: 'IA5 Swedish (7-bit)',
		20108: 'IA5 Norwegian (7-bit)',
		20127: 'US-ASCII (7-bit)',
		20261: 'T.61',
		20269: 'ISO 6937 Non-Spacing Accent',
		20273: 'IBM EBCDIC Germany',
		20277: 'IBM EBCDIC Denmark-Norway',
		20278: 'IBM EBCDIC Finland-Sweden',
		20280: 'IBM EBCDIC Italy',
		20284: 'IBM EBCDIC Latin America-Spain',
		20285: 'IBM EBCDIC United Kingdom',
		20290: 'IBM EBCDIC Japanese Katakana Extended',
		20297: 'IBM EBCDIC France',
		20420: 'IBM EBCDIC Arabic',
		20423: 'IBM EBCDIC Greek',
		20424: 'IBM EBCDIC Hebrew',
		20833: 'IBM EBCDIC Korean Extended',
		20838: 'IBM EBCDIC Thai',
		20866: 'Russian (KOI8-R); Cyrillic (KOI8-R)',
		20871: 'IBM EBCDIC Icelandic',
		20880: 'IBM EBCDIC Cyrillic Russian',
		20905: 'IBM EBCDIC Turkish',
		20924: 'IBM EBCDIC Latin 1/Open System (1047 + Euro symbol)',
		20932: 'Japanese (JIS 0208-1990 and 0121-1990)',
		20936: 'Simplified Chinese (GB2312); Chinese Simplified (GB2312-80)',
		20949: 'Korean Wansung',
		21025: 'IBM EBCDIC Cyrillic Serbian-Bulgarian',
		21027: '(deprecated)',
		21866: 'Ukrainian (KOI8-U); Cyrillic (KOI8-U)',
		28591: 'ISO 8859-1 Latin 1; Western European (ISO)',
		28592: 'ISO 8859-2 Central European; Central European (ISO)',
		28593: 'ISO 8859-3 Latin 3',
		28594: 'ISO 8859-4 Baltic',
		28595: 'ISO 8859-5 Cyrillic',
		28596: 'ISO 8859-6 Arabic',
		28597: 'ISO 8859-7 Greek',
		28598: 'ISO 8859-8 Hebrew; Hebrew (ISO-Visual)',
		28599: 'ISO 8859-9 Turkish',
		28603: 'ISO 8859-13 Estonian',
		28605: 'ISO 8859-15 Latin 9',
		29001: 'Europa 3',
		38598: 'ISO 8859-8 Hebrew; Hebrew (ISO-Logical)',
		50220: 'ISO 2022 Japanese with no halfwidth Katakana; Japanese (JIS)',
		50221: 'ISO 2022 Japanese with halfwidth Katakana; Japanese (JIS-Allow 1 byte Kana)',
		50222: 'ISO 2022 Japanese JIS X 0201-1989; Japanese (JIS-Allow 1 byte Kana - SO/SI)',
		50225: 'ISO 2022 Korean',
		50227: 'ISO 2022 Simplified Chinese; Chinese Simplified (ISO 2022)',
		50229: 'ISO 2022 Traditional Chinese',
		50930: 'EBCDIC Japanese (Katakana) Extended',
		50931: 'EBCDIC US-Canada and Japanese',
		50933: 'EBCDIC Korean Extended and Korean',
		50935: 'EBCDIC Simplified Chinese Extended and Simplified Chinese',
		50936: 'EBCDIC Simplified Chinese',
		50937: 'EBCDIC US-Canada and Traditional Chinese',
		50939: 'EBCDIC Japanese (Latin) Extended and Japanese',
		51932: 'EUC Japanese',
		51936: 'EUC Simplified Chinese; Chinese Simplified (EUC)',
		51949: 'EUC Korean',
		51950: 'EUC Traditional Chinese',
		52936: 'HZ-GB2312 Simplified Chinese; Chinese Simplified (HZ)',
		54936: 'Windows XP and later: GB18030 Simplified Chinese (4 byte); Chinese Simplified (GB18030)',
		57002: 'ISCII Devanagari',
		57003: 'ISCII Bengali',
		57004: 'ISCII Tamil',
		57005: 'ISCII Telugu',
		57006: 'ISCII Assamese',
		57007: 'ISCII Oriya',
		57008: 'ISCII Kannada',
		57009: 'ISCII Malayalam',
		57010: 'ISCII Gujarati',
		57011: 'ISCII Punjabi',
		65000: 'Unicode (UTF-7)',
		65001: 'Unicode (UTF-8)',
		}
KEY_VALUES = {		# keyName --> vkCode
		'LBUTTON': 0x01,
		'RBUTTON': 0x02,
		'CANCEL': 0x03,
		'MBUTTON': 0x04,
		'XBUTTON1': 0x05,
		'XBUTTON2': 0x06,
		'BACK': 0x08,
		'TAB': 0x09,
		'CLEAR': 0x0C,
		'RETURN': 0x0D,
		'SHIFT': 0x10,
		'CONTROL': 0x11,
		'MENU': 0x12,
		'PAUSE': 0x13,
		'CAPITAL': 0x14,
		'KANA': 0x15,
		'HANGEUL': 0x15,
		'JUNJA': 0x17,
		'FINAL': 0x18,
		'HANJA': 0x19,
		'KANJI': 0x19,
		'ESCAPE': 0x1B,
		'CONVERT': 0x1C,
		'NONCONVERT': 0x1D,
		'ACCEPT': 0x1E,
		'MODECHANGE': 0x1F,
		'SPACE': 0x20,
		'PRIOR': 0x21,
		'NEXT': 0x22,
		'END': 0x23,
		'HOME': 0x24,
		'LEFT': 0x25,
		'UP': 0x26,
		'RIGHT': 0x27,
		'DOWN': 0x28,
		'SELECT': 0x29,
		'PRINT': 0x2A,
		'EXECUTE': 0x2B,
		'SNAPSHOT': 0x2C,
		'INSERT': 0x2D,
		'DELETE': 0x2E,
		'HELP': 0x2F,
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
		'LWIN': 0x5B,
		'RWIN': 0x5C,
		'APPS': 0x5D,
		'SLEEP': 0x5f,
		'NUMPAD0': 0x60,
		'NUMPAD1': 0x61,
		'NUMPAD2': 0x62,
		'NUMPAD3': 0x63,
		'NUMPAD4': 0x64,
		'NUMPAD5': 0x65,
		'NUMPAD6': 0x66,
		'NUMPAD7': 0x67,
		'NUMPAD8': 0x68,
		'NUMPAD9': 0x69,
		'MULTIPLY': 0x6A,
		'ADD': 0x6B,
		'SEPARATOR': 0x6C,
		'SUBTRACT': 0x6D,
		'DECIMAL': 0x6E,
		'DIVIDE': 0x6F,
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
		'NUMLOCK': 0x90,
		'SCROLL': 0x91,
		'OEM-NEC-EQUAL': 0x92,
		'OEM-FJ-JISHO': 0x92,
		'OEM-FJ-MASSHOU': 0x93,
		'OEM-FJ-TOUROKU': 0x94,
		'OEM-FJ-LOYA': 0x95,
		'OEM-FJ-ROYA': 0x96,
		'LSHIFT': 0xA0,
		'RSHIFT': 0xA1,
		'LCONTROL': 0xA2,
		'RCONTROL': 0xA3,
		'LMENU': 0xA4,
		'RMENU': 0xA5,
		'BROWSER-BACK': 0xA6,
		'BROWSER-FORWARD': 0xA7,
		'BROWSER-REFRESH': 0xA8,
		'BROWSER-STOP': 0xA9,
		'BROWSER-SEARCH': 0xAA,
		'BROWSER-FAVORITES': 0xAB,
		'BROWSER-HOME': 0xAC,
		'VOLUME-MUTE': 0xAD,
		'VOLUME-DOWN': 0xAE,
		'VOLUME-UP': 0xAF,
		'MEDIA-NEXT-TRACK': 0xB0,
		'MEDIA-PREV-TRACK': 0xB1,
		'MEDIA-STOP': 0xB2,
		'MEDIA-PLAY-PAUSE': 0xB3,
		'LAUNCH-MAIL': 0xB4,
		'LAUNCH-MEDIA-SELECT': 0xB5,
		'LAUNCH-APP1': 0xB6,
		'LAUNCH-APP2': 0xB7,
		'OEM-1': 0xBA,
		'OEM-PLUS': 0xBB,
		'OEM-COMMA': 0xBC,
		'OEM-MINUS': 0xBD,
		'OEM-PERIOD': 0xBE,
		'OEM-2': 0xBF,
		'OEM-3': 0xC0,
		'OEM-4': 0xDB,
		'OEM-5': 0xDC,
		'OEM-6': 0xDD,
		'OEM-7': 0xDE,
		'OEM-8': 0xDF,
		'OEM-AX': 0xE1,
		'OEM-102': 0xE2,
		'ICO-HELP': 0xE3,
		'ICO-00': 0xE4,
		'PROCESSKEY': 0xE5,
		'ICO-CLEAR': 0xE6,
		'PACKET': 0xE7,
		'OEM-RESET': 0xE9,
		'OEM-JUMP': 0xEA,
		'OEM-PA1': 0xEB,
		'OEM-PA2': 0xEC,
		'OEM-PA3': 0xED,
		'OEM-WSCTRL': 0xEE,
		'OEM-CUSEL': 0xEF,
		'OEM-ATTN': 0xF0,
		'OEM-FINISH': 0xF1,
		'OEM-COPY': 0xF2,
		'OEM-AUTO': 0xF3,
		'OEM-ENLW': 0xF4,
		'OEM-BACKTAB': 0xF5,
		'ATTN': 0xF6,
		'CRSEL': 0xF7,
		'EXSEL': 0xF8,
		'EREOF': 0xF9,
		'PLAY': 0xFA,
		'ZOOM': 0xFB,
		'NONAME': 0xFC,
		'PA1': 0xFD,
		'OEM-CLEAR': 0xFE,
		}
KEY_NAMES = dict([(i[1], i[0]) for i in KEY_VALUES.items()])	# vkCode --> keyName
	
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

HORZRES = 8
VERTRES = 10

#****************************************************************************************************
#
#****************************************************************************************************
#HACK:(1)
#wine specific hack
#	
#	KBDLLHOOKSTRUCT.flags is unusable when running in wine. same goses for user32.GetKeyboardState(), 
#	user32.GetAsyncKeyState(). reason is: <quote>wine does not capture all system wide keys</quote>. 
#	
#	we emulate the functions as much as necesssary here to track keyboard state by hand. this makes VK_MENU,
#	VK_CONTROL and VK_SHIFT work. no way to track numlock, capslock and other toggle keys because we do not 
#	know their initial states. side effect is that holding own keys ahead of L{KeyboardManager.start} will never be honored.
#
# ..then it is up to a keyboard hook to call setKeyDown() when appropriate
#		
#	@todo: synchronize this stuff
#	@warning: this hack overwrites user32.GetAsyncKeyState + user32.GetKeyboardState

_keyboardState = [0] * 256

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

def setKeyDown(vkCode, flag):
	"""this method should always be called whenever a keyboard manager notices a key press/release
	@param vkCode: VK_*
	@param flag: (bool) True if the key was pressed, False if it was released
	"""
	value = 0x80 if flag else 0x00
	_keyboardState[vkCode] = value
	if vkCode in (VK_LCONTROL, VK_RCONTROL): _keyboardState[VK_CONTROL] = value		
	elif vkCode in (VK_LMENU, VK_RMENU): _keyboardState[VK_MENU] = value
	elif vkCode in (VK_LSHIFT, VK_RSHIFT): _keyboardState[VK_SHIFT] = value

#HACK:(1)

#****************************************************************************************************
# window methods
#****************************************************************************************************
class WindowForegroundHook(QtCore.QObject):
	Timeout = 0.2
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
			hwnd = user32.GetForegroundWindow()
			if hwnd != self._lastWindowForeground:
				self.emit(QtCore.SIGNAL('windowGainedForeground(int)'), hwnd)
				self._lastWindowForeground = hwnd
			time.sleep(self.Timeout)

class WindowHook(QtCore.QObject):
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
			self.emit(QtCore.SIGNAL('windowDestroyed(int)'), hwnd)
		for hwnd in hwndsCreated:
			self.emit(QtCore.SIGNAL('windowCreated(int)'), hwnd)
		hwnd = windowForeground()
		if hwnd in self._hwnds and hwnd != self._hwndForeground:
			self.emit(QtCore.SIGNAL('windowGainedForeground(int)'), hwnd)
			self._hwndForeground = hwnd
		if self._isRunning:
			timer = QtCore.QTimer(self)
			timer.setSingleShot(True)
			timer.setInterval(self.Timeout * 1000)
			self.connect(timer, QtCore.SIGNAL('timeout()'), self._run)
			timer.start()
			#QtCore.QTimer.singleShot(
			#		self.Timeout * 1000, 
			#		self._run
			#		)

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

def windowGetText(hwnd):
	"""returns the window title of the specified window
	@param hwnd: handle of the window
	@return: (str)
	"""
	if not hwnd: return ''
	n = user32.GetWindowTextLengthW(hwnd)
	if n:		
		result = DWORD()
		p = create_unicode_buffer(n+ 1)
		#
		user32.SendMessageTimeoutW(
				hwnd, 
				WM_GETTEXT, 
				sizeof(p), 
				p, 
				SMTO_ABORTIFHUNG, 
				MY_SMTO_TIMEOUT, 
				byref(result)
				)
		if not p.value:
			user32.GetWindowTextW(hwnd, p, sizeof(p))
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
	while True:
		tmp_parent = user32.GetParent(parent)
		if not tmp_parent:	break
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

def windowSetText(hwnd, text=''):
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
				WM_SETTEXT, 
				0, 
				text, 
				SMTO_ABORTIFHUNG, 
				MY_SMTO_TIMEOUT, 
				byref(result)
				)

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

class MouseInput(object):
	def __init__(self):
		self._input = []
		
	def _addMousePoint(self, event, point, hwnd=None):
		x, y = point.x(), point.y()
		if hwnd:
			pt = POINT( point.x(), point.y() )
			user32.ClientToScreen(hwnd, byref(pt) )
			x, y = pt.x, pt.y
		x, y = self._worldCoords(x, y)
		mi = MOUSEINPUT(
				dx=x,
				dy=y,
				dwFlags= event | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE_NOCOALESCE,
				)
		input = INPUT()
		input.type = INPUT_MOUSE
		input.mi = mi
		self._input.append(input)
	
	def _worldCoords(self, x, y):
		x = float(x * 0xFFFF) / user32.GetSystemMetrics(SM_CXSCREEN)
		y = float(y * 0xFFFF) / user32.GetSystemMetrics(SM_CYSCREEN)
		return (
				int( round(x, 0) ),
				int( round(y, 0) ),
				)
	
	def send(self):
		if not self._input:
			raise ValueError('No input to send')
		arr = (INPUT*len(self._input))(*self._input)
		self._input = []
		return user32.SendInput(len(arr), arr, sizeof(INPUT))
		
	def leftDown(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_LEFTDOWN, point, hwnd=hwnd)
	def leftUp(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_LEFTUP, point, hwnd=hwnd)
	def leftClick(self, point, hwnd=None):
		self.leftDown(point, hwnd=hwnd)
		self.leftUp(point, hwnd=hwnd)
	def rightDown(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_RIGHTDOWN, point, hwnd=hwnd)
	def rightUp(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_RIGHTTUP, point, hwnd=hwnd)
	def rightClick(self, point, hwnd=None):
		self.rightDown(point, hwnd=hwnd)
		self.rightUp(point, hwnd=hwnd)
	def middleDown(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_MIDDLEDOWN, point, hwnd=hwnd)
	def middleUp(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_MIDDLETUP, point, hwnd=hwnd)
	def middleClick(self, point, hwnd=None):
		self.middleDown(point, hwnd=hwnd)
		self.middleUp(point, hwnd=hwnd)	
	def move(self, point, hwnd=None):
		self._addMousePoint(MOUSEEVENTF_MOVE, point, hwnd=hwnd)
	#TODO: not tested
	def wheelScroll(self, nSteps):
		mi = MOUSEINPUT(
				dwFlags= MOUSEEVENTF_WHEEL | MOUSEEVENTF_ABSOLUTE,
				mouseData=nSteps,
				)
		input = INPUT()
		input.type = INPUT_MOUSE
		input.mi = mi
		self._input.append(input)

def mouseButtonsDown():
	return _mouseButtonsDown[:]
	
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

def mouseClickPoint(button, nClicks=1, point=None):
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
		mouseSetPos(point)
	# click button
	rng = list(range(nClicks))
	while rng:
		rng.pop()
		mousePressButton(button)
		mouseReleaseButton(button)
		if rng:
			time.sleep(0.1)
	
def mouseClickLeft(point):
	"""clicks the left mouse button at the specified point"""
	return mouseClickPoint(MouseButtonLeft, point=point, nClicks=1)
def mouseClickLeftDouble(point):
	"""double clicks the left mouse button at the specified point"""
	return mouseClickPoint(MouseButtonLeft, point=point, nClicks=2)
def mouseClickRight(point):
	"""clicks the right mouse button at the specified point"""
	return mouseClickPoint(MouseButtonRight, point=point, nClicks=1)
def mouseClickRightDouble(point):
	"""double clicks the right mouse button at the specified point"""
	return mouseClickPoint(MouseButtonRight, point=point, nClicks=2)
def mouseClickMiddle(pt):
	"""clicks the middle mouse button at the specified point"""
	return self.mouseClickPoint(MouseButtonMiddle, point=point, nClicks=1)
def mouseClickMiddleDouble(point):
	"""double clicks the middle mouse button at the specified point"""
	return mouseClickPoint(MouseButtonMiddle, point=point, nClicks=2)

def mouseGetPos():
	'''returns the current position of the mouse pointer
	@return: (QPoint) coordinates of the mouse cursor
	'''
	pt = POINT()
	user32.GetCursorPos(byref(pt))
	return QtCore.QPoint(pt.x, pt.y)

def mouseSetPos(point, step=4):
	"""moves the mouse pointer to the specified position
	@param pt: (tuple) point containing the coordiantes to move the mouse pointer to (in screen coordiantes)
	"""
	#NOTE: for some reason neither user32.mouse_event() not user32.SendInput() have any effect here (linux/wine).
	#           the only way i can get this to work is to move the cursor stepwise to its destination?!?
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
		

class MouseHook(QtCore.QObject):
	"""win32 keyboard manager implementation
	@event EvtMouseButtonUp: event triggerered when a mouse  button is pressed. arg = Button*
	@event EvtMouseButtonDown: event triggerered when a mosue button is released. arg = Button*
	@event EvtMouseWheelScrolled: event triggerered when the mosue wheel is scrolled. arg = stepsScrolled
	"""
	
	def __init__(self, parent=None, eventHandler=None):
		"""
		@param cb: (function) event handler
		"""
		QtCore.QObject.__init__(self, parent)
		self._isStarted = False
		self._hHook = None
		self._pHookProc = MOUSEHOOKPROCLL(self._hookProc)
		self._eventHandler = eventHandler
		
	def setEventhandler(self, eventHandler):
		self._eventHandler = eventHandler
	
	def _hookProc(self, code, wParam, lParam):
		"""private method, MOUSEHOOKPROCLL implementation"""
		
		if code == HC_ACTION:
			if wParam == WM_LBUTTONDOWN:
				if MouseButtonLeft not in _mouseButtonsDown:
					_mouseButtonsDown.append(MouseButtonLeft)
			elif wParam == WM_RBUTTONDOWN:
				if MouseButtonRight not in _mouseButtonsDown:
					_mouseButtonsDown.append(MouseButtonRight)
			elif wParam == WM_MBUTTONDOWN:
				if MouseButtonMiddle not in _mouseButtonsDown:
					_mouseButtonsDown.append(MouseButtonMiddle)
			elif wParam == WM_LBUTTONUP:
				if MouseButtonLeft in _mouseButtonsDown:
					_mouseButtonsDown.remove(MouseButtonLeft)
			elif wParam == WM_RBUTTONUP:
				if MouseButtonRight in _mouseButtonsDown:
					_mouseButtonsDown.remove(MouseButtonRight)
			elif wParam == WM_MBUTTONUP:
				if MouseButtonMiddle in _mouseButtonsDown:
					_mouseButtonsDown.remove(MouseButtonMiddle)
					
			elif wParam == WM_MOUSEWHEEL:
				mouseInfo = MSLLHOOKSTRUCT.from_address(lParam)
				wheelDelta = GET_WHEEL_DELTA_WPARAM(mouseInfo.mouseData)
				nSteps = wheelDelta / WHEEL_DELTA
				if self._eventHandler is not None:
					if  self._eventHandler.handleInput(MouseWheelUp if nSteps >= 0 else MouseWheelDown, nSteps=nSteps):
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
def keyboardLayoutName():
	"""returns the name of the current keyboard layout
	@return: (str) layout name or 'unknown'
	"""
	return KEYBOARD_LAYOUT_NAMES.get(kernel32.GetOEMCP(), 'unknown')
	
class KeyboardHook(QtCore.QObject):
	"""win32 keyboard hook implementation"""
	def __init__(self, parent=None, eventHandler=None):
		"""
		@param cb: (function) event handler
		"""
		QtCore.QObject.__init__(self, parent)
		self._isStarted = False
		self._hHook = None
		self._pHookProc = KEYBHOOKPROCLL(self._hookProc)
		self._eventHandler = eventHandler
		
	def setEventhandler(self, eventHandler):
		self._eventHandler = eventHandler
	
	def _hookProc(self, code, wParam, lParam):
		"""private method, KEYBHOOKPROCLL implementation"""
		if code == HC_ACTION:
			keyInfo = KBDLLHOOKSTRUCT.from_address(lParam)
			#HACK:(1)
			if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
				setKeyDown(keyInfo.vkCode, True)
			#<--HACK:(1)
			
			keyboardState = (c_ubyte*256)()
			user32.GetKeyboardState(byref(keyboardState))
			key = self._keyFromKeyboardState(keyboardState=keyboardState)
			keydown = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
			if keydown:
				self.emit(QtCore.SIGNAL('keyPressed(QString)'), key)
			else:
				self.emit(QtCore.SIGNAL('keyReleased(QString)'), key)
			
			#HACK:(1)
			if wParam in (WM_KEYUP, WM_SYSKEYUP):
				setKeyDown(keyInfo.vkCode, False)
			#<--HACK:(1)
			
			if self._eventHandler is not None:
				if  self._eventHandler.handleInput(key, keydown=keydown, nSteps=None):
					return TRUE
		return user32.CallNextHookEx(self._hHook, code, wParam, lParam)
		
	def _keyFromKeyboardState(self, keyboardState=None):
		"""@param keyboardState: (c_ubyte*256) holding a keyboar state or None"""
		value = ''
		if keyboardState:		
			for vkCode, tmp_value in enumerate(keyboardState):
				if tmp_value:
					if vkCode in (		# ignore these keys
							VK_CONTROL,
							VK_MENU,
							VK_SHIFT,
							VK_SCROLL,
							VK_CAPITAL,
							VK_NUMLOCK,
							):
						continue
					if value:
						value += ' %s' % KEY_NAMES[vkCode]
					else:
						value = KEY_NAMES[vkCode]
		return '<%s>' % value
	
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


