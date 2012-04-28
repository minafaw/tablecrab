"""win32 specific methods
"""

from ctypes import *
from ctypes.wintypes import *

__all__ = ['toplevel_windows', ]
#************************************************************************************
# win32 consts
#************************************************************************************
user32 = windll.user32
TRUE = 1
ENUMWINDOWSPROC = WINFUNCTYPE(INT, HANDLE, LPARAM)
WM_GETTEXT = 13
WM_GETTEXTLENGTH = 0x000E
SMTO_ABORTIFHUNG = 2
MY_SMTO_TIMEOUT = 2000

#************************************************************************************
# platform implementation
#************************************************************************************
class PlatformWindow(object):
	def __init__(self, handle):
		self.handle = handle

	def __eq__(self, other): return self.handle == other.handle
	def __ne__(self, other): return not self.__eq__(other)

	def get_title(self):
		#NOTE: see: [ http://blogs.msdn.com/b/oldnewthing/archive/2003/08/21/54675.aspx ] "the secret live of GetWindowtext" for details
		# try GetWindowText first
		nChars = user32.GetWindowTextLengthW(self.handle)
		nChars = 0
		if nChars:
			p = create_unicode_buffer(nChars +1)
			if user32.GetWindowTextW(self.handle, p, sizeof(p)):
				return p.value.encode('utf-8')
		# some text can only be retrieved by WM_GETTEXT, so here we go
		nChars = DWORD()
		result = user32.SendMessageTimeoutW(
				self.handle,
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
				self.handle,
				WM_GETTEXT,
				sizeof(p),
				p,
				SMTO_ABORTIFHUNG,
				MY_SMTO_TIMEOUT,
				byref(nChars)
				)
			return p.value.encode('utf-8')
		return ''

	def get_geometry(self):
		rc = RECT()
		user32.GetClientRect(self.handle, byref(rc))
		return (rc.left, rc.top, rc.right-rc.left, rc.bottom-rc.top)


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

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	for window in toplevel_windows():
		print 'window: "%s" %s' % (window.get_title(), window.get_geometry())



