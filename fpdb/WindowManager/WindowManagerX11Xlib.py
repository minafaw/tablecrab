# -*- coding: utf-8 -*-

"""x11 specific methods via xlib

@dependency: libx11
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

#NOTE: CDLL() raises OSError when library is not present
libx11 = CDLL('libX11.so')
dsp = libx11.XOpenDisplay(None)
if not dsp:
	raise OSError('no X server running!')
libx11.XCloseDisplay(dsp)

#************************************************************************************
# window manager implementation
#************************************************************************************
class Window(WindowManagerBase.Window):
	def set_size(self, w, h):
		 set_window_size(self.handle, w, h)
	def attatch(self, child):
		return set_window_transient_for(self.handle, child)

class WindowManager(WindowManagerBase.WindowManagerBase):
	def window_list(self):
		return window_list()

#************************************************************************************
# Xlib
#************************************************************************************
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
def get_window_application(dsp, handle,
		XFree=libx11.XFree, XGetClassHint=libx11.XGetClassHint, XClassHint=XClassHint,
		addressof=addressof, c_char_p=c_char_p, byref=byref):
	classHint = XClassHint()
	if XGetClassHint(dsp, handle, byref(classHint)):
		application = classHint.res_name
		# docs claim each string in XClassHint has to be freed individually, so here e go..
		XFree(c_char_p.from_address(addressof(classHint) + XClassHint.res_name.offset))
		XFree(c_char_p.from_address(addressof(classHint) + XClassHint.res_class.offset))
		return application
	return ''

#TODO: check if child is a toplevel window
def set_window_transient_for(parent, child):
	dsp = libx11.XOpenDisplay('')
	try:
		libx11.XSetTransientForHint(dsp, child, parent)
	finally:
		libx11.XCloseDisplay(dsp)

def set_window_size(handle, w, h):
	dsp = libx11.XOpenDisplay('')
	try:
		libx11.XResizeWindow(dsp, handle, w, h)
	finally:
		libx11.XCloseDisplay(dsp)

def get_window_geometry(dsp, handle,
		XGetGeometry=libx11.XGetGeometry, XTranslateCoordinates=libx11.XTranslateCoordinates,
		byref=byref, c_uint=c_uint, c_int=c_int, XWindow=XWindow
		):
	rootWindow = XWindow()
	x = c_int()
	y = c_int()
	w = c_uint()
	h = c_uint()
	borderW = c_uint()
	bitsPerPixel = c_uint()
	XGetGeometry(
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
	XTranslateCoordinates(dsp, handle, rootWindow, 0, 0, byref(xDst), byref(yDst), byref(child))
	return (xDst.value, yDst.value, w.value, h.value)

def get_window_title(dsp, handle,
		XFetchName=libx11.XFetchName, byref=byref, c_char_p=c_char_p, string_at=string_at, XFree=libx11.XFree
		):
	p = c_char_p()
	if XFetchName(dsp, handle, byref(p)):
		try:
			#TODO: found no way to decode the string to unicode. as expected german umlaut fails :-(
			#title = unicode(string_at(p).decode('utf-8'))
			return p.value
		finally:
			XFree(p)
	return ''

def get_window_is_visible(dsp, handle,
		XGetWindowAttributes=libx11.XGetWindowAttributes, XWindowAttributes=XWindowAttributes,
		IsViewable=IsViewable, byref=byref):
	windowAttributes = XWindowAttributes()
	if XGetWindowAttributes(dsp, handle, byref(windowAttributes)):
		return windowAttributes.map_state == IsViewable
	return False

def list_windows(dsp, handle,
		XQueryTree=libx11.XQueryTree, XFree=libx11.XFree,  XWindow= XWindow, pointer=pointer,
		byref=byref, xrange=xrange,
		):
	root = XWindow()
	parent = XWindow()
	pChildren = pointer(XWindow())
	nChildren = c_uint()
	if XQueryTree(dsp, handle, byref(root), byref(parent), byref(pChildren), byref(nChildren)):
		if pChildren:
			try:
				return map(pChildren.__getitem__, xrange(nChildren.value))
			finally:
				XFree(pChildren)
	return []

#TODO: we may have to XGrabServer() XUngrabServer() here
def window_list(
		XDefaultRootWindow=libx11.XDefaultRootWindow, XOpenDisplay=libx11.XOpenDisplay, XCloseDisplay=libx11.XCloseDisplay,
		list_windows=list_windows, get_window_title=get_window_title, get_window_geometry=get_window_geometry,
		get_window_application=get_window_application, get_window_is_visible=get_window_is_visible,
		Window=Window, Rectangle=WindowManagerBase.Rectangle,

		):
	"""returns a list of all toplevel windows currently open
	@note: list should always start at the root window (the desktop)
	@note: the list should be sorted in stacking oder. root first, topmost window last
	"""
	dsp = XOpenDisplay('')
	try:
		handleRoot = XDefaultRootWindow(dsp)
		geometryRoot = get_window_geometry(dsp, handleRoot)
		windowRoot = Window(
				None,
				handleRoot,
				get_window_title(dsp, handleRoot),
				get_window_application(dsp, handleRoot),
				WindowManagerBase.Rectangle(*geometryRoot),
				Rectangle(*geometryRoot),
				get_window_is_visible(dsp, handleRoot),
				)
		windows = [windowRoot, ]
		#NOTE: looks like in x11 each window has an unnamed frame with first named child being
		# the actual window. i guess this is window manager specific, we will see..
		#NOTE: we take the handle of the actual window as handle for our window. this could
		# cause troubles. we have to either work on the parent for some calls or rework
		# attributes of our window to assign "handleFrame" and "handleWindow"
		for handleFrame in list_windows(dsp, handleRoot):
			title = get_window_title(dsp, handleFrame)
			if not title:
				windowFrame = None
				for handleWindow in list_windows(dsp, handleFrame):
					title = get_window_title(dsp, handleWindow)
					if title:
						windowFrame = Window(
								windowRoot,
								handleWindow,
								title,
								get_window_application(dsp, handleWindow),
								Rectangle(*get_window_geometry(dsp, handleFrame)),
								Rectangle(*get_window_geometry(dsp, handleWindow)),
								get_window_is_visible(dsp, handleFrame),	# have to take frame here (?)
								)
						break
				if windowFrame is not None:
					windows.append(windowFrame)
	finally:
		XCloseDisplay(dsp)
	return windows

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	# print all currently running toplevel windows
	wm = WindowManager()
	for event, param in wm.next():
		if event == wm.EVENT_WINDOW_CREATED:
			window = param
			print '0x%x title="%s" application="%s" frameRect=%s clientRect=%s isVisible=%s' % (
					window.handle,
					window.title,
					window.application,
					window.frameRect.to_tuple(),
					window.clientRect.to_tuple(),
					window.isVisible,
					)


