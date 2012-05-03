# -*- coding: utf-8 -*-

"""x11 specific methods via xlib
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
#TODO:
#
# - get_window_text() should return unicode
#************************************************************************************

from ctypes import *
import WindowManagerBase

__all__ = ['WindowManager', ]

#************************************************************************************
# Xlib
#************************************************************************************
#NOTE: CDLL() raises OSError when library is not present
libx11 = CDLL('libX11.so')
dsp = libx11.XOpenDisplay(None)
if not dsp:
	raise OSError('no X server running!')
libx11.XCloseDisplay(dsp)

XID = c_ulong
XWindow = c_ulong
Success = 0
STRING = POINTER(c_char)
VisualID = c_ulong
Colormap = XID
XPointer = STRING

# map states
IsUnmapped = 0
IsUnviewable = 1
IsViewable = 2

class _XGC(Structure):
	pass
_XGC._fields_ = [
]
GC = POINTER(_XGC)

class XDisplay(Structure):
	_fields_ = []

class XErrorEvent(Structure):
	_fields_ = [
	('type', c_int),
	('display', POINTER(XDisplay)),
	('resourceid', XID),
	('serial', c_ulong),
	('error_code', c_ubyte),
	('request_code', c_ubyte),
	('minor_code', c_ubyte),
	]

class XClassHint(Structure):
	_fields_ = [
			('res_name', c_char_p),
			('res_class', c_char_p),
			]

class _XExtData(Structure):
	pass
_XExtData._fields_ = [
	('number', c_int),
	('next', POINTER(_XExtData)),
	('free_private', CFUNCTYPE(c_int, POINTER(_XExtData))),
	('private_data', XPointer),
]
XExtData = _XExtData

class Visual(Structure):
	_fields_ = [
			('ext_data', POINTER(XExtData)),
			('visualid', VisualID),
			('c_class', c_int),
			('red_mask', c_ulong),
			('green_mask', c_ulong),
			('blue_mask', c_ulong),
			('bits_per_rgb', c_int),
			('map_entries', c_int),
			]

class Depth(Structure):
   _fields_ = [
			('depth', c_int),
			('nvisuals', c_int),
			('visuals', POINTER(Visual)),
			]

class Screen(Structure):
	   _fields_ = [
			('ext_data', POINTER(XExtData)),
			('display', POINTER(XDisplay)),
			('root', XWindow),
			('width', c_int),
			('height', c_int),
			('mwidth', c_int),
			('mheight', c_int),
			('ndepths', c_int),
			('depths', POINTER(Depth)),
			('root_depth', c_int),
			('root_visual', POINTER(Visual)),
			('default_gc', GC),
			('cmap', Colormap),
			('white_pixel', c_ulong),
			('black_pixel', c_ulong),
			('max_maps', c_int),
			('min_maps', c_int),
			('backing_store', c_int),
			('save_unders', c_int),
			('root_input_mask', c_long),
			]

class XWindowAttributes(Structure):
	_fields_ = [
			('x', c_int),
			('y', c_int),
			('width', c_int),
			('height', c_int),
			('border_width', c_int),
			('depth', c_int),
			('visual', POINTER(Visual)),
			('root', XWindow),
			('c_class', c_int),
			('bit_gravity', c_int),
			('win_gravity', c_int),
			('backing_store', c_int),
			('backing_planes', c_ulong),
			('backing_pixel', c_ulong),
			('save_under', c_int),
			('colormap', Colormap),
			('map_installed', c_int),
			('map_state', c_int),
			('all_event_masks', c_long),
			('your_event_mask', c_long),
			('do_not_propagate_mask', c_long),
			('override_redirect', c_int),
			('screen', POINTER(Screen)),
			]

class _ErrorHandler(object):
	def __init__(self):
		self.lastError = Success
		self.pErrorHandler = CFUNCTYPE(c_int, POINTER(XDisplay), POINTER(XErrorEvent))(self.HandleXError)
		libx11.XSetErrorHandler(self.pErrorHandler)
	def HandleXError(self, display, pXErrorEvent):
		self.lastError = pXErrorEvent[0].error_code
		return 0
	def GetLastError(self):
		"""returns and clears last error
		@return: (int) error code"""
		lastError = self.lastError
		self.lastError = Success
		return lastError
_ErrorHandler = _ErrorHandler()
GetLastError = _ErrorHandler.GetLastError

#************************************************************************************
# helpers
#************************************************************************************
def get_window_application(dsp, handle):
	application = ''
	classHint = XClassHint()
	if libx11.XGetClassHint(dsp, handle, byref(classHint)):
		application = classHint.res_name[:]
		# docs claim each string in XClassHint has to be freed individually, so here e go..
		addr = addressof(classHint) + XClassHint.res_name.offset
		libx11.XFree(c_char_p.from_address(addr))
		addr = addressof(classHint) + XClassHint.res_class.offset
		libx11.XFree(c_char_p.from_address(addr))
	return application

def get_window_geometry(dsp, handle):
	rootWindow = XWindow()
	x = c_int()
	y = c_int()
	w = c_uint()
	h = c_uint()
	borderW = c_uint()
	bitsPerPixel = c_uint()
	libx11.XGetGeometry(
				dsp,
				handle,
				byref(rootWindow),
				byref(x),
				byref(y),
				byref(w),
				byref(h),
				byref(borderW),
				byref(bitsPerPixel)
				)
	# translate coordinates
	child = XWindow()
	xDst = c_int()
	yDst = c_int()
	libx11.XTranslateCoordinates(dsp, handle, rootWindow, 0, 0, byref(xDst), byref(yDst), byref(child))
	return (xDst.value, yDst.value, w.value, h.value)

def get_window_title(dsp, handle):
	title = ''
	p = pointer(c_char())
	if libx11.XFetchName(dsp, handle, byref(p)):
		try:
			#TODO: found no way to decode the string to unicode. as expected german umlaut fails :-(
			#title = unicode(string_at(p).decode('utf-8'))
			title = string_at(p)
		finally:
			libx11.XFree(p)
	return title

def get_window_is_visible(dsp, handle):
	isVisible = False
	windowAttributes = XWindowAttributes()
	if libx11.XGetWindowAttributes(dsp, handle, byref(windowAttributes)):
		isVisible = windowAttributes.map_state == IsViewable
	return isVisible

def list_windows(dsp, window):
	windows = []
	root = XWindow()
	parent = XWindow()
	pChildren = pointer(XWindow())
	nChildren = c_uint()
	if libx11.XQueryTree(dsp, window.handle, byref(root), byref(parent), byref(pChildren), byref(nChildren)):
		if pChildren:
			try:
				arr = (XWindow * nChildren.value)()
				memmove(arr, pChildren, sizeof(arr))
			finally:
				libx11.XFree(pChildren)
			for handle in arr:
				childWindow = WindowManagerBase.Window(
						window,
						handle,
						get_window_title(dsp, handle),
						get_window_application(dsp, handle),
						WindowManagerBase.Rectangle(*get_window_geometry(dsp, handle)),
						get_window_is_visible(dsp, handle),
						)
				windows.append(childWindow)
	return windows

#NOTE: x11 has no real notion of toplevel so we have to go over the whole tree here.
# to keep things reasonable we filter out windows that have no name.
#NOTE: we may have to XGrabServer() XUngrabServer() here
def window_list():
	"""returns a list of all windows currently open
	@note: list should always start at the root window (the desktop)
	@note: the list should be sorted in stacking oder. root first, topmost window last
	"""
	def walker(dsp, window):
		yield window
		for x in list_windows(dsp, window):
			for y in walker(dsp, x):
				yield y

	dsp = libx11.XOpenDisplay('')
	try:
		handle = libx11.XDefaultRootWindow(dsp)
		window = WindowManagerBase.Window(
				None,
				handle,
				get_window_title(dsp, handle),
				get_window_application(dsp, handle),
				WindowManagerBase.Rectangle(*get_window_geometry(dsp, handle)),
				get_window_is_visible(dsp, handle),
				)
		#windows = [window for window in walker(dsp, window) if window.title]
		windows = [window for window in walker(dsp, window)]
	finally:
		libx11.XCloseDisplay(dsp)
	return windows

#************************************************************************************
# window manager implementation
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

