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
class Window(WindowManagerBase.Window):
	def set_size(self, w, h):
		 set_window_size(self.handle, w, h)

	#NOTE: attatching a foreign window to a window is a terrible hack. all sorts of evil
	# things may happen. MSDN explicitely warns to not do this. unlike linux the win32 api
	# does not provide any means to do so in a clean way.
	#NOTE: windows removes minimize button from the parent, so i guess we are treated like a modeless dialog
	#NOTE: strangely enough the call to SetWindowLong() does not have the desired efect
	# when put into a method. have to test this. for now the call should stay here.
	def attatch(self, child):
		#TODO: check if child is a toplevel window
		user32.SetWindowLongPtrW(child, GWL_HWNDPARENT, self.handle)

class WindowManager(WindowManagerBase.WindowManagerBase):
	def window_list(self):
		return window_list()

#************************************************************************************
# win32
#************************************************************************************
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi

#NOTE: hope i got tGetModuleFileNameEx() right..
# looks like there are other methods to get application that created a window:
#    - psapi.GetProcessImageFileName() - xp+
#    - kernel32.QueryFullProcessImageName() - vista+
#NOTE: acc to MSDN GetModuleFileNameEx() is either exported psapi.dll or by kernel32.dll
#      as K32GetModuleFileNameEx()
try:
	psapi.GetModuleFileNameExA
except AttributeError:
	psapi.GetModuleFileNameExA = kernel.K32GetModuleFileNameExA
#NOTE: GetModuleFileNameExW segfaults on wine (up to version 1.5.3) see <Bug 30543> 0on http://bugs.winehq.org
try:
	psapi.GetModuleFileNameExW
except AttributeError:
	psapi.GetModuleFileNameExW = kernel.K32GetModuleFileNameExW

#NOTE: user32.GetWindowLongPtr is only exported on 64 bit windows, use SetWindowLong instead
# on 32 bit builds
try:
	user32.SetWindowLongPtrA
except AttributeError:
	user32.SetWindowLongPtrA = user32.SetWindowLongA
try:
	user32.SetWindowLongPtrW
except AttributeError:
	user32.SetWindowLongPtrW = user32.SetWindowLongW

MAX_PATH = 260
PROCESS_VM_READ = 16
PROCESS_QUERY_INFORMATION = 1024
TRUE = 1
ENUMWINDOWSPROC = WINFUNCTYPE(INT, HANDLE, LPARAM)
WM_GETTEXT = 13
WM_GETTEXTLENGTH = 0x000E
SMTO_ABORTIFHUNG = 2
MY_SMTO_TIMEOUT = 2000
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOOWNERZORDER = 0x0200
SWP_NOACTIVATE = 0x0010
GWL_HWNDPARENT = -8

#************************************************************************************
# helpers
#
#NOTE: we do not errorcheck most api calls here because we may work on dead windows
#************************************************************************************

def set_window_size(hwnd, w, h):
	user32.SetWindowPos(hwnd, 0, 0, 0, w, h, SWP_NOMOVE|SWP_NOZORDER|SWP_NOOWNERZORDER|SWP_NOACTIVATE)

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

def get_window_rect(handle):
	rc = RECT()
	user32.GetWindowRect(handle, byref(rc))
	return (rc.left, rc.top, rc.right-rc.left, rc.bottom-rc.top)

def get_window_client_rect(handle):
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
	geometry = get_window_rect(handle)
	window = Window(
				None,
				handle,
				get_window_title(handle),
				get_window_application(handle),
				WindowManagerBase.Rectangle(*geometry),
				WindowManagerBase.Rectangle(*geometry),
				get_window_is_visible(handle),
				)
	handles = []
	def cb(handle, lp):
		handles.append(handle)
		return TRUE
	user32.EnumWindows(ENUMWINDOWSPROC(cb), 0)
	windows = [window, ]
	for handle in handles:
		childWindow = Window(
				window,
				handle,
				get_window_title(handle),
				get_window_application(handle),
				WindowManagerBase.Rectangle(*get_window_rect(handle)),
				WindowManagerBase.Rectangle(*get_window_client_rect(handle)),
				get_window_is_visible(handle),
				)
		windows.append(childWindow)
	return windows

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
				print '%s: 0x%x "%s" ("%s") %s %s visible=%s' % (
						event,
						window.handle,
						window.title,
						window.application,
						window.frameRect.to_tuple(),
						window.clientRect.to_tuple(),
						window.isVisible,
						)
		time.sleep(0.5)

