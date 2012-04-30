# -*- coding: utf-8 -*-

"""win32 specific methods
"""

#************************************************************************************
#LICENCE: AGPL
#
# Copyright 2012 Jürgen Urner (jUrner<at>arcor.de)
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>. In the "official"
# distribution you can find the license in agpl-3.0.txt.
#************************************************************************************

import os
from ctypes import *
from ctypes.wintypes import *

__all__ = ['WindowManager', ]

#************************************************************************************
# win32
#************************************************************************************
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi

#NOTE: hope i got tGetModuleFileNameEx() right..
# looks like there are other methods to get application that createed a window:
#    - psapi.GetProcessImageFileName() - xp+
#    - kernel32.QueryFullProcessImageName() - vista+
#NOTE: we use ansi version here because a)there is a bug in whine with the unicode
#      version filed in wine bugzilla as [Bug 30543] and b) ansi may be sufficient
GetModuleFileNameEx = None
# looks like GetModuleFileNameEx is a moving target ..try to catch it
try:
	GetModuleFileNameEx = psapi.GetModuleFileNameExA
except AttributeError:
	try:
		GetModuleFileNameEx = kernel.K32GetModuleFileNameExA
	except AttributeError:
		pass
if GetModuleFileNameEx is None:
	raise OSError('GetModuleFileNameEx not found, but we need it here!')

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
# helpers
#
#NOTE: we do not errorcheck most api calls here because we may work on dead windows
#************************************************************************************
def get_window_application(hwnd):
	result = ''
	pId = DWORD()
	user32.GetWindowThreadProcessId(hwnd, byref(pId))
	if pId:
		hProcess = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pId)
		if hProcess:
			try:
				#NOTE: GetModuleFileNameEx() gives no information on buffer size required
				# seems like we have to do trial and error
				bufferSize = MAX_PATH +1
				while True:
					p = create_string_buffer(bufferSize)
					nChars = GetModuleFileNameEx(hProcess, None, p, sizeof(p))
					if sizeof(p) == nChars +1:
						bufferSize *= 2
					else:
						break
			finally:
				kernel32.CloseHandle(hProcess)
			#NOTE: we retrieve executable name only. not much use returning the file path
			# because a) it is not guaranteed to point to the folder where the executable
			# resildes in and b) we have to make this method uniform cross platforms.
			#NOTE: GetModuleFileNameEx() may return short paths "micros~1" so expand it first
			nChars = kernel32.GetLongPathNameA(p, None, 0)
			pLongPath = create_string_buffer(nChars +1)
			kernel32.GetLongPathNameA(p, pLongPath, sizeof(pLongPath))
			path = os.path.normpath(pLongPath.value)
			result = os.path.basename(path)
	return result

def get_window_geometry(hwnd):
	rc = RECT()
	user32.GetClientRect(hwnd, byref(rc))
	pt = POINT()
	user32.ClientToScreen(hwnd, byref(pt))
	return (pt.x, pt.y, rc.right-rc.left, rc.bottom-rc.top)

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

def toplevel_windows():
	hwnds = []
	def cb(hwnd, lp):
		hwnds.append(hwnd)
		return TRUE
	if not user32.EnumWindows(ENUMWINDOWSPROC(cb), 0):
		raise WindowsError(FormatError(GetLastError()))
	windows = []
	for hwnd in hwnds:
		windows.append(Window(
				hwnd,
				get_window_title(hwnd),
				get_window_application(hwnd),
				get_window_geometry(hwnd),
				))
	return windows

#NOTE: for some reason creating gdk windows via gtk.gdk.window_foreign_new()
# segfaults on win32 when called after a gui has been initialized. no idea why
# as a workaround we reimplement gtks window_set_transient_for() [gdkwindow-win32.c]
def set_window_transient_for(gtkWindow, hwnd):
	#TODO: make shure gtkWindows is not a child window
	# looks like we have to use SetWindowLong here

	#NOTE:

	# #ifdef _WIN64
	# WINUSERAPI LONG_PTR    WINAPI GetWindowLongPtrA(HWND,INT);
	# WINUSERAPI LONG_PTR    WINAPI GetWindowLongPtrW(HWND,INT);
	# #else
	# #define                       GetWindowLongPtrA GetWindowLongA
	# #define                       GetWindowLongPtrW GetWindowLongW
	# #endif

	# so SetWindowLongPtr is only defined on 64 bit windows
	# have to use code like this to make it work on all versions:
	#
	#try:
	#	SetWindowLongPtr = user32.SetWindowLongPtrW
	#except AttributeError:
	#	SetWindowLongPtr = user32.SetWindowLongW
	#
	##SetWindowLongPtr(window_id, GWLP_HWNDPARENT, (LONG_PTR) parent_id)
	pass

#************************************************************************************
# window manager implementation
#
#NOTES:
# - windows are not guaranteed to be alive when we handle them
# - we can not guarantee the identity of a window. another window may have been
#   created with the same handle from the same application at any time.
#
# so i found best approach is to retrieve all data for a window on every hop and let
# the user deal with eventual troubles.
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

	run the manager as generator and process the events it returns on L{next}

	@cvar EVENT_WINDOW_CREATED: event generated when a window has been created. param: L{Window}
	@cvar EVENT_WINDOW_GEOMETRY_CHANGED: event generated when the geometry of a window has changed. param: L{Window}
	@cvar EVENT_WINDOW_DESTROYED: event generated when a window has been destroyed. param: L{Window}

	@note: L{Window}s passed in events are snapshots of windows not actual windows.
	they are meant for emidiate use. that is, the instances passed are never updated.
	instead	a new instance is passed on every event.
	"""
	EVENT_WINDOW_CREATED = 'window-created'
	EVENT_WINDOW_GEOMETRY_CHANGED = 'window-geometry-changed'
	EVENT_WINDOW_DESTROYED = 'window-destroyed'

	def __init__(self):
		"""constructor"""
		self._windows = []

	def __iter__(self):
		"""yes, we are a generator"""
		return self

	def next(self):
		"""returns next event in turn generated by the manager
		@return: (list) of (EVENT_*, param) tuples
		"""
		events = []
		windowsOld = self._windows[:]
		self._windows = toplevel_windows()
		for window in self._windows:
			if window in windowsOld:
				if window.geometry != windowsOld[windowsOld.index(window)].geometry:
					events.append((self.EVENT_WINDOW_GEOMETRY_CHANGED, window))
			else:
				events.append((self.EVENT_WINDOW_CREATED, window))
				events.append((self.EVENT_WINDOW_GEOMETRY_CHANGED, window))
		for window in windowsOld:
			if window not in self._windows:
				events.append((self.EVENT_WINDOW_DESTROYED, window))
		return events

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
	for events in wm:
		for event, param in events:
			if isinstance(param, Window):
				window = param
				print '%s: 0x%x "%s" ("%s") %s' % (event, window.handle, window.title, window.application, window.geometry)
		time.sleep(0.5)
