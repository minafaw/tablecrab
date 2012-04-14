# warning: runs on windows only!


from  ctypes import *
from ctypes.wintypes import *
user32 = windll.user32
#************************************************************************************
# windows api methods
#************************************************************************************
ENUMWINDOWSPROC = WINFUNCTYPE(INT, HANDLE, LPARAM)
MY_MAX_CLASS_NAME = 100
SMTO_ABORTIFHUNG = 2
MY_SMTO_TIMEOUT = 2000	# in miliseconds
WM_GETTEXT = 13
WM_GETTEXTLENGTH = 0x000E

def sendMessageTimeout(hwnd, msg, wParam,lParam, isUnicode=True):
	result = DWORD()
	if isUnicode:
		user32.SendMessageTimeoutW(hwnd, msg, wParam, lParam, SMTO_ABORTIFHUNG, MY_SMTO_TIMEOUT, byref(result))
	else:
		user32.SendMessageTimeoutA(hwnd, msg, wParam, lParam, SMTO_ABORTIFHUNG, MY_SMTO_TIMEOUT, byref(result))
	return result.value

def windowChildren(hwndParent=None):
	"""returns a the list of child windows of a window
	@param hwndParent: handle of the window or None to list all toplevel windows
	@return: (list) of windows of the specified parent
	"""
	L= []
	def f(hwnd, lp):
		L.append(hwnd)
		return 1
	p = ENUMWINDOWSPROC(f)
	user32.EnumWindows(p, 0) if not hwndParent else user32.EnumChildWindows(hwndParent, p, 0)
	return L

def windowGetClassName(hwnd):
	"""returns the class name of the specified window
	@param hwnd: handle of the window
	@return: (unicode)
	"""
	if not hwnd: return ''
	p = create_unicode_buffer(MY_MAX_CLASS_NAME)
	if not user32.GetClassNameW(hwnd, p, sizeof(p)):
		#NOTE: GetClassName() sometimes fails for some unknown reason, so we return '' here
		return ''
	return p.value

def windowGetTextLength(hwnd):
	n = user32.GetWindowTextLengthW(hwnd)
	if not n:
		result = DWORD()
		user32.SendMessageTimeoutW(hwnd, WM_GETTEXTLENGTH, 0, 0, SMTO_ABORTIFHUNG, MY_SMTO_TIMEOUT, byref(result))
		n = result.value
	return n

def windowGetText(hwnd, maxSize=-1):
	"""returns the window title of the specified window
	@param hwnd: handle of the window
	 @param maxSize: (int) maximum size of text to retrieve. if -1 text is retrieved
	 unconditionally. else only text <= maxSize is retrieved
	@return: (unicode)
	"""
	if not hwnd or maxSize == 0: return ''

	#NOTE: see: [ http://blogs.msdn.com/b/oldnewthing/archive/2003/08/21/54675.aspx ]
	#           "the secret live of GetWindowtext" for details

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

#************************************************************************************
#
#************************************************************************************
# poked around in stars client and found the NoteSelector wich is a standard combobox
#
# NoteSelector behaves like this:
# regular poker - list of players at the table (excluding hero) + players from other tables
#                 + players that already left. seems like stars removes players who left
#                 after a certain time
# zoom poker - list of players at the table (excluding hero)
#
# missing information:
# - seat numbers of the players at current table. no idea where to get this from. i doubt
# that stars keeps this around somewhere in easily available form.
#
#
PokerStarsMainClass = '#32770'
PokerStarsTableClass = 'PokerStarsTableFrameClass'
PokerStarsNoteSelectorClass = 'PokerStarsNoteSelectorClass'

# Combo Box messages
CB_GETEDITSEL            = 320
CB_LIMITTEXT             = 321
CB_SETEDITSEL            = 322
CB_ADDSTRING             = 323
CB_DELETESTRING          = 324
CB_DIR                   = 325
CB_GETCOUNT              = 326
CB_GETCURSEL             = 327
CB_GETLBTEXT             = 328
CB_GETLBTEXTLEN          = 329
CB_INSERTSTRING          = 330
CB_RESETCONTENT          = 331
CB_FINDSTRING            = 332
CB_SELECTSTRING          = 333
CB_SETCURSEL             = 334
CB_SHOWDROPDOWN          = 335
CB_GETITEMDATA           = 336
CB_SETITEMDATA           = 337
CB_GETDROPPEDCONTROLRECT = 338
CB_SETITEMHEIGHT         = 339
CB_GETITEMHEIGHT         = 340
CB_SETEXTENDEDUI         = 341
CB_GETEXTENDEDUI         = 342
CB_GETDROPPEDSTATE       = 343
CB_FINDSTRINGEXACT       = 344
CB_SETLOCALE             = 345
CB_GETLOCALE             = 346
CB_GETTOPINDEX           = 347
CB_SETTOPINDEX           = 348
CB_GETHORIZONTALEXTENT   = 349
CB_SETHORIZONTALEXTENT   = 350
CB_GETDROPPEDWIDTH       = 351
CB_SETDROPPEDWIDTH       = 352
CB_INITSTORAGE           = 353
CB_MULTIPLEADDSTRING     = 355
CB_GETCOMBOBOXINFO       = 356
#************************************************************************************
#
#************************************************************************************
#NOTES:
# - this is a proove of concept, all sorts of evil things can happen.
def getTableData():
	"""grabs all player names from all note selectors from all tables
	@return: (dict)
		- 'hero': hero name (if logged in)
		- 'tables': (list) of lists [hwndTable, list playerNames]
	@note: hero is never included in the player name lists
	"""

	SMTO = sendMessageTimeout	# being lazy here

	data = {
		'hero': None,
		'tables': [],
		}

	# find lobby + all tables
	for hwnd in windowChildren():
		className = windowGetClassName(hwnd)
		if className == PokerStarsMainClass:
			title = windowGetText(hwnd)
			if title.startswith('PokerStars Lobby - Logged in as '):
				title = title.split('\x20', 6)
				if len(title) != 7:
					raise ValueError('something went wrong here!')
				data['hero'] = title[6]
		elif className == PokerStarsTableClass:
			data['tables'].append(hwnd)

	# get player names for each table from notes selector
	for iTable, hwnd in enumerate(data['tables']):
		playerNames = []
		data['tables'][iTable] = [hwnd, playerNames]

		# find note selector
		for hwnd in windowChildren(hwnd):
			className = windowGetClassName(hwnd)
			if className == PokerStarsNoteSelectorClass:

				# get list of player names
				nItems = sendMessageTimeout(hwnd, CB_GETCOUNT, 0, 0)
				for i in xrange(nItems):
					n = sendMessageTimeout(hwnd, CB_GETLBTEXTLEN, i, 0)
					p = create_unicode_buffer(n+1)
					n = sendMessageTimeout(hwnd, CB_GETLBTEXT, i, p)
					playerNames.append(p.value)

				break

	return data
# 0 == 1031
#4294967295
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	data = getTableData()
	print data['hero']
	for table in data['tables']:
		print table


