
from ctypes import *
from ctypes.wintypes import *

user32 = windll.user32
kernel32 = windll.kernel32

#**************************************************************
#
#**************************************************************

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

MOUSEEVENTF_MOVE = 1
MOUSEEVENTF_LEFTDOWN = 2
MOUSEEVENTF_LEFTUP = 4
MOUSEEVENTF_RIGHTDOWN = 8
MOUSEEVENTF_RIGHTUP = 16
MOUSEEVENTF_MIDDLEDOWN = 32
MOUSEEVENTF_MIDDLEUP = 64
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 32768

WHEEL_DELTA =120
	
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

