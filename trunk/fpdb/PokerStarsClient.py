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
# poked around in stars client and found the NoteSelector quite intersting. was able
# to snoop out some messages to control it.
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

# PokerStars note selector messages
#
# ..less here?
#NOTESELECTOR_? = 0x00000142
#NOTESELECTOR_? = 0x00000143	# lParam: buffer
NOTESELECTOR_REMOVE_ITEM = 0x00000144	# wParam: index lParam: 0 return: nItems or -1
#NOTESELECTOR_? = 0x00000145	# lParam: buffer
NOTESELECTOR_GET_ITEM_COUNT = 0x00000146
NOTESELECTOR_GET_CURRENT_INDEX = 0x00000147			# wParam: 0 lParam: 0 return: index or -1
NOTESELECTOR_GET_ITEM_TEXT = 0x00000148			# wParam: index lParam: buffer return: nChars or -1
NOTESELECTOR_GET_ITEM_TEXT_LENGHT = 0x00000149	# wParam: index lParam:0 return: nChars or -1
NOTESELECTOR_INSERT_ITEM = 0x0000014a	# wParam: index lParam: buffer return: index or -1
NOTESELECTOR_CLEAR = 0x0000014b	# wParam: 0 lParam: 0 return: bool (?)
#OTESELECTOR_? = 0x0000014c	# wParam: ? lParam: buffer return: index (?)
#OTESELECTOR_? = 0x0000014d	# wParam: ? lParam: buffer return: index (?)
NOTESELECTOR_SET_CURRENT_INDEX = 0x0000014e			# wParam: index lParam: 0 return: index or -1
#NOTESELECTOR_? = 0x0000014f	# wParam: ? lParam: ? return: index (?)
#NOTESELECTOR_? = 0x00000150	# wParam: ? lParam: ? return: ?
#NOTESELECTOR_? = 0x00000151	# wParam: ? lParam: ? return: ?
#NOTESELECTOR_? = 0x00000152	# wparam: 0 lParam: buffer returns: some bytes ('i\x03\x00\x00\x81\x03\x00\x00\xf6\x03\x00\x00\xd9\x03\x00')
#NOTESELECTOR_? = 0x00000153
#NOTESELECTOR_? = 0x00000154	# returns: some N
#NOTESELECTOR_? = 0x00000155
#NOTESELECTOR_? = 0x00000156
#NOTESELECTOR_? = 0x00000157
NOTESELECTOR_FIND_ITEM = 0x00000158				# wParam: 0 lParam: playerName return: index or -1
#NOTESELECTOR_? = 0x00000159
#NOTESELECTOR_? = 0x00000160	# seems to return some byte count?
# ..more here?

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
			if className != PokerStarsNoteSelectorClass:
				continue

			# get list of player names
			nItems = SMTO(hwnd, NOTESELECTOR_GET_ITEM_COUNT, 0, 0)
			for i in xrange(nItems):
				n = SMTO(hwnd, NOTESELECTOR_GET_ITEM_TEXT_LENGHT, i, 0)
				p = create_unicode_buffer(n+1)
				n = SMTO(hwnd, NOTESELECTOR_GET_ITEM_TEXT, i, p)
				playerNames.append(p.value)

	return data

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	data = getTableData()
	print data['hero']
	for table in data['tables']:
		print table


