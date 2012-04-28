"""win32 specific methods
"""

from ctypes import *
from ctypes.wintypes import *

__all__ = ['WindowManager', ]
#************************************************************************************
# win32 consts
#************************************************************************************
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi

GetModuleFileNameEx = None
# looks like GetModuleFileNameEx is a moving target ..try to catch it
try:
	GetModuleFileNameEx = kernel32.GetModuleFileNameExW
except AttributeError:
	try:
		GetModuleFileNameEx = psapi.GetModuleFileNameExW
	except AttributeError:
		GetModuleFileNameEx = psapi.K32GetModuleFileNameExW
if GetModuleFileNameEx is None:
	raise ValueError('GetModuleFileNameEx not found, but we need it here!')

MAX_PATH = 260
PROCESS_VM_READ = 16
PROCESS_QUERY_INFORMATION = 1024
TRUE = 1
ENUMWINDOWSPROC = WINFUNCTYPE(INT, HANDLE, LPARAM)
WM_GETTEXT = 13
WM_GETTEXTLENGTH = 0x000E
SMTO_ABORTIFHUNG = 2
MY_SMTO_TIMEOUT = 2000

#************************************************************************************
#
#************************************************************************************
def toplevel_windows():
	windows = []
	def cb(hwnd, lp):
		windows.append(PlatformWindow(hwnd))
		return TRUE
	user32.EnumWindows(ENUMWINDOWSPROC(cb), 0)
	return windows

#NOTE: for some reason creating gdk windows via gtk.gdk.window_foreign_new()
# segfaults on win32 when called after a gui has been initialized. no idea why
# as a workaround we reimplement gtks window_set_transient_for() [gdkwindow-win32.c]
def set_window_transient_for(gtkWindow, hwnd):
	#TODO: make shure gtkWindows is not a child window
	# looks like we have to use SetWindowLong here

	##SetWindowLongPtr(window_id, GWLP_HWNDPARENT, (LONG_PTR) parent_id)
	pass

def get_window_title(hwnd):
	#NOTE: see: [ http://blogs.msdn.com/b/oldnewthing/archive/2003/08/21/54675.aspx ] "the secret live of GetWindowtext" for details
	# try GetWindowText first
	nChars = user32.GetWindowTextLengthW(hwnd)
	nChars = 0
	if nChars:
		p = create_unicode_buffer(nChars +1)
		if user32.GetWindowTextW(hwnd, p, sizeof(p)):
			return p.value.encode('utf-8')
	# some text can only be retrieved by WM_GETTEXT, so here we go
	nChars = DWORD()
	result = user32.SendMessageTimeoutW(
			hwnd,
			WM_GETTEXTLENGTH,
			0,
			0,
			SMTO_ABORTIFHUNG,
			MY_SMTO_TIMEOUT,
			byref(nChars)
			)
	if nChars:
		p = create_unicode_buffer(nChars.value +1)
		result = user32.SendMessageTimeoutW(
			hwnd,
			WM_GETTEXT,
			sizeof(p),
			p,
			SMTO_ABORTIFHUNG,
			MY_SMTO_TIMEOUT,
			byref(nChars)
			)
		return p.value.encode('utf-8')
	return ''

def get_window_geometry(hwnd):
	rc = RECT()
	user32.GetClientRect(hwnd, byref(rc))
	pt = POINT()
	user32.ClientToScreen(hwnd, byref(pt))
	return (pt.x, pt.y, rc.right-rc.left, rc.bottom-rc.top)

def get_window_executable(hwnd):
	pId = DWORD()
	user32.GetWindowThreadProcessId(hwnd, byref(pId))
	if not pId:
		return ''
	hProcess = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pId)
	if not hProcess:
		raise WindowsError(GetLastError())
	try:
		p= create_unicode_buffer(MAX_PATH+1)
		GetModuleFileNameEx(hProcess, None, p, sizeof(p))
	finally:
		kernel32.CloseHandle(hProcess)
	return p.value

def toplevel_windows():
	hwnds = []
	def cb(hwnd, lp):
		hwnds.append(hwnd)
		return TRUE
	user32.EnumWindows(ENUMWINDOWSPROC(cb), 0)
	windows = []
	for hwnd in hwnds:
		windows.append(Window(
				hwnd,
				get_window_title(hwnd),
				get_window_executable(hwnd),
				get_window_geometry(hwnd),

				))
	return windows

#************************************************************************************
#
#************************************************************************************
class Window(object):
	"""window implementation
	@ivar application: (str) appllication that created the window
	@ivar geometry: (tuple) client area coordinates (x, y, w, h) relative to the screen
	@ivar handle: (int) platform dependend window handle
	@ivar title: (unicode) title of the window
	"""
	def __init__(self, handle, title, application, geometry):
		self.application = application
		self.geometry = geometry
		self.handle = handle
		self.title = title
	def __eq__(self, other):
		return self.handle == other.handle and self.application == other.application
	def __ne__(self, other): return not self.__eq__(other)

class WindowManager(object):
	"""window manager implementation

	run the manager as generator and process the messages it returns on L{next}

	@cvar MSG_WINDOW_CREATED: message generated when a window has been created. param: L{Window}
	@cvar MSG_WINDOW_GEOMETRY_CHANGED: message generated when the geometry of a window has changed. param: L{Window}
	@cvar MSG_WINDOW_DESTROYED: message generated when a window has been destroyed. param: L{Window}
	"""
	MSG_WINDOW_CREATED = 'window-created'
	MSG_WINDOW_GEOMETRY_CHANGED = 'window-geometry-changed'
	MSG_WINDOW_DESTROYED = 'window-destroyed'

	def __init__(self):
		"""constructor"""
		self._windows = []

	def __iter__(self):
		"""yes, we are a generator"""
		return self

	def next(self):
		"""returns next messages in turn generated by the manager
		@return: (list) of (MSG_*, param) tuples
		"""
		messages = []
		windowsOld = self._windows[:]
		self._windows = toplevel_windows()
		for window in self._windows:
			if window not in windowsOld:
				messages.append((self.MSG_WINDOW_CREATED, window))
				messages.append((self.MSG_WINDOW_GEOMETRY_CHANGED, window,))
		for window in windowsOld:
			if window in self._windows:
				if window.geometry != self._windows[self._windows.index(window)].geometry:
					messages.append((self.MSG_WINDOW_GEOMETRY_CHANGED, window))
			else:
				messages.append((self.MSG_WINDOW_DESTROYED, window))
		return messages

	def windows(self):
		"""returns list of L{Window}s currently known to the manager"""
		return self._windows

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	# sample code + run WindowManager (CAUTION: will run unconditionally until keyboard interrupt!!)
	import time
	wm = WindowManager()
	for messages in wm:
		for message, param in messages:
			if isinstance(param, Window):
				window = param
				print '%s: 0x%x "%s" ("%s") %s' % (message, window.handle, window.title, window.application, window.geometry)
		time.sleep(0.5)




