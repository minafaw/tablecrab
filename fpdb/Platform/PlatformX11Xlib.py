"""x11 specific methods via xlib
"""

#TODO: this is just a boilerplate implementation so far. evil things may happen in here!!!

from ctypes import *

__all__ = ['WindowManager', ]

#************************************************************************************
# Xlib stuff
#************************************************************************************
#NOTE: CDLL() raises OSError when library is not present
libx11 = CDLL('libX11.so')

XID = c_ulong
XWindow = c_ulong

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
	_pack_ = 1
	_fields_ = [
			('res_name', c_char_p),
			('res_class', c_char_p),
			]

class _ErrorHandler(object):
	def __init__(self):
		self.lastError = None
		self.pErrorHandler = CFUNCTYPE(c_int, POINTER(XDisplay), POINTER(XErrorEvent))(self.HandleXError)
		libx11.XSetErrorHandler(self.pErrorHandler)
	def HandleXError(self, display, pXErrorEvent):
		#if pXErrorEvent:		# not quite clear from docs if a NULL pointer can be passed
		p = create_string_buffer(1024)
		libx11.XGetErrorText(display, pXErrorEvent[0].error_code, p, sizeof(p))
		self.lastError = p.value
		return 0
	def GetLastError(self):
		"""returns and clears last error"""
		lastError = self.lastError
		self.lastError = None
		return lastError
_ErrorHandler = _ErrorHandler()
GetLastError = _ErrorHandler.GetLastError

#************************************************************************************
#
#************************************************************************************
def init_window(dsp, handle):

	# get window title
	p = pointer(c_char())
	if not libx11.XFetchName(dsp, handle, byref(p)):
		title = ''
	else:
		#TODO: found no way to decode the string to unicode. as expected german umlaut fails :-(
		#title = unicode(string_at(p).decode('utf-8'))
		title = string_at(p)
		try:
			pass
		finally:
			libx11.XFree(p)

	# get application that created the window
	#TODO: according to docs we have to free the strings individually using XFree().
	# no idea how.. every attempt so far segfaulted
	classHint = XClassHint()
	if libx11.XGetClassHint(dsp, handle, byref(classHint)):
		application = classHint.res_name
	else:
		application = ''

	# get geometry
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
	geometry = (xDst.value, yDst.value, w.value, h.value)

	# finally
	return Window(handle, title, application, geometry)

def list_windows(dsp, window):
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
			return [init_window(dsp, i) for i in arr]
	return []

#NOTE: x11 has no real notion of toplevel so we have to go over the whole tree here.
# to keep things reasonable we filter out windows that have no name.
def toplevel_windows():
	def walker(dsp, window):
		yield window
		for i in list_windows(dsp, window):
			for x in walker(dsp, i):
				yield x

	dsp = libx11.XOpenDisplay('')
	try:
		window = init_window(dsp, libx11.XDefaultRootWindow(dsp))
		windows = [i for i in walker(dsp, window) if i.title]
	finally:
		libx11.XCloseDisplay(dsp)
	if GetLastError():
		return ()
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


#for window in toplevel_windows():
#	print window.title, window.application, window.geometry

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
