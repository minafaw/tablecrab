# -*- coding: utf-8 -*-

"""win32 window manager implementattion
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
#************************************************************************************
#
#NOTE: linux/wine
# - the window manager does not work 1000% on wine. unlike native windows neither EnumWindows()
#   nor GetWindow() not GetNextWindow() provide reliable information on window stacking order.

#NOTE: executable path
# - we use ansi version of GetModuleFileNameEx() because there is a bug in wine (1.5)
#   filed in bugzilla as [Bug 30543]. wide version segfaults overflowing output buffer.
#************************************************************************************


import os
from ctypes import *
from ctypes.wintypes import *
import WindowManagerBase

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
#NOTE: acc to MSDN GetModuleFileNameEx() is either exported psapi.dll or by kernel32.dll
#      as K32GetModuleFileNameEx()
try:
	psapi.GetModuleFileNameExA
except AttributeError:
	psapi.GetModuleFileNameExA = kernel.K32GetModuleFileNameExA

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
def get_window_application(handle):
	result = ''
	pId = DWORD()
	user32.GetWindowThreadProcessId(handle, byref(pId))
	if pId:
		hProcess = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pId)
		if hProcess:
			try:
				#NOTE: GetModuleFileNameEx() gives no information on buffer size required
				# seems like we have to do trial and error
				bufferSize = MAX_PATH +1
				while True:
					p = create_string_buffer(bufferSize)
					nChars = psapi.GetModuleFileNameExA(hProcess, None, p, sizeof(p))
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

def get_window_geometry(handle):
	rc = RECT()
	user32.GetClientRect(handle, byref(rc))
	pt = POINT()
	user32.ClientToScreen(handle, byref(pt))
	return (pt.x, pt.y, rc.right-rc.left, rc.bottom-rc.top)

def get_window_title(handle):
	#NOTE: see: [ http://blogs.msdn.com/b/oldnewthing/archive/2003/08/21/54675.aspx ] "the secret live of GetWindowtext" for details
	# try GetWindowText first
	nChars = user32.GetWindowTextLengthW(handle)
	nChars = 0
	if nChars:
		p = create_unicode_buffer(nChars +1)
		if user32.GetWindowTextW(handle, p, sizeof(p)):
			return p.value.encode('utf-8')
	# some text can only be retrieved by WM_GETTEXT, so here we go
	nChars = DWORD()
	result = user32.SendMessageTimeoutW(
			handle,
			WM_GETTEXTLENGTH,
			0,
			0,
			SMTO_ABORTIFHUNG,
			MY_SMTO_TIMEOUT,
			byref(nChars)
			)
	#NOTE: WM_GETTEXTLENGTH returns LRESULT so we have to cast here
	nChars = c_long(nChars.value)
	if nChars > 0:
		p = create_unicode_buffer(nChars.value +1)
		result = user32.SendMessageTimeoutW(
			handle,
			WM_GETTEXT,
			sizeof(p),
			p,
			SMTO_ABORTIFHUNG,
			MY_SMTO_TIMEOUT,
			byref(nChars)
			)
		return p.value.encode('utf-8')
	return ''

def get_window_is_visible(handle):
	isVisible = False
	if user32.IsWindowVisible(handle):
		if not user32.IsIconic(handle):
			isVisible = True
	return isVisible

#NOTE: stacking order
# - undocumented feature of EnumWindows() is hat windows are enumerated in stacking order.
#   this feature is documented for EnumChildWindows(). if something goes wroong we have
#   to use GetWindow() tosort windows in stacking order by hand.
#
#NOTE: child windows
# - for pratical reasons we do not include child windows in the enumeration, so list is
#   toplevel windows only. if we ever include child windows we have to keep in mind
#   that WM_GETTEXT retrieves text of a window not its title.
#
def window_list():
	"""returns a list of all windows currently open
	@note: list should always start at the root window (the desktop)
	@note: the list should be sorted in stacking oder. desktop first, topmost window last
	"""
	handle = user32.GetDesktopWindow()
	window = WindowManagerBase.Window(
				None,
				handle,
				get_window_title(handle),
				get_window_application(handle),
				WindowManagerBase.Rectangle(*get_window_geometry(handle)),
				get_window_is_visible(handle),
				)
	handles = []
	def cb(handle, lp):
		handles.append(handle)
		return TRUE
	user32.EnumWindows(ENUMWINDOWSPROC(cb), 0)
	windows = [window, ]
	for handle in handles:
		childWindow = WindowManagerBase.Window(
				window,
				handle,
				get_window_title(handle),
				get_window_application(handle),
				WindowManagerBase.Rectangle(*get_window_geometry(handle)),
				get_window_is_visible(handle),
				)
		windows.append(childWindow)
	return windows

#NOTE: for some reason creating gdk windows via gtk.gdk.window_foreign_new()
# segfaults on win32 when called after a gui has been initialized. no idea why
# as a workaround we reimplement gtks window_set_transient_for() [gdkwindow-win32.c]
def set_window_transient_for(gtkWindow, handle):
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
class WindowManager(WindowManagerBase.WindowManagerBase):
	def window_list(self):
		return window_list()

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	# sample code + run WindowManager (CAUTION: will run unconditionally until keyboard interrupt!!)
	import time
	wm = WindowManager()
	for events in wm:
		for event, param in events:
			if isinstance(param, WindowManagerBase.Window):
				window = param
				print '%s: 0x%x "%s" ("%s") %s visible=%s' % (
						event,
						window.handle,
						window.title,
						window.application,
						window.geometry.to_tuple(),
						window.isVisible,
						)
		time.sleep(0.5)




