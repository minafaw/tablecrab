"""x11 specific methods via xlib
"""

#TODO: this is just a boilerplate implementation so far. evil things may happen in here!!!

from ctypes import *

__all__ = ['toplevel_windows', ]
#************************************************************************************
# xlib consts
#************************************************************************************
#NOTE: CDLL() raises OSError when library is not present
libx11 = CDLL('libX11.so')

Success = 0
MAX_PROPERTY_VALUE_LEN = 4096
PROPFMT_NONE = 0	# felt free to define this
PROPFMT_CHAR_ARRAY = 8
PROPFMT_SHORT_ARRAY = 16
PROPFMT_LONG_ARRAY = 32

Atom = c_ulong
XID = c_ulong
Window = c_ulong
XA_STRING = Atom(31)

class Display(Structure):
    _fields_ = []

class XErrorEvent(Structure):
    _fields_ = [
		('type', c_int),
		('display', POINTER(Display)),
		('resourceid', XID),
		('serial', c_ulong),
		('error_code', c_ubyte),
		('request_code', c_ubyte),
		('minor_code', c_ubyte),
		]

class _ErrorHandler(object):

	def __init__(self):
		self.lastError = None
		self.pErrorHandler = CFUNCTYPE(c_int, POINTER(Display), POINTER(XErrorEvent))(self.HandleXError)
		libx11.XSetErrorHandler(self.pErrorHandler)

	def HandleXError(self, display, pXErrorEvent):
		#if pXErrorEvent:		# not quite clear from docs if a NULL pointer can be passed
		p = create_string_buffer(1024)
		libx11.XGetErrorText(display, pXErrorEvent[0].error_code, p, sizeof(p))
		self.lastError = p.value
		return 0

	def HasLastError(self):
		return self.lastError != None

	def GetLastError(self):
		"""returns and clears last error"""
		lastError = self.lastError
		self.lastError = None
		return lastError
_ErrorHandler = _ErrorHandler()
GetLastError = _ErrorHandler.GetLastError
HasLastError = _ErrorHandler.HasLastError

#************************************************************************************
# platform implementation
#************************************************************************************
class PlatformWindow(object):
	def __init__(self, handle):
		self.handle = handle

	def __eq__(self, other): return self.handle == other.handle
	def __ne__(self, other): return not self.__eq__(other)

	def get_title(self):
		return get_property(self.handle, XA_STRING, "WM_NAME")

	def get_geometry(self):
		rootWindow = Window()
		x = c_int()
		y = c_int()
		w = c_uint()
		h = c_uint()
		borderW = c_uint()
		bitsPerPixel = c_uint()
		dsp = libx11.XOpenDisplay('')
		try:
			libx11.XGetGeometry(
					dsp,
					self.handle,
					byref(rootWindow),
					byref(x),
					byref(y),
					byref(w),
					byref(h),
					byref(borderW),
					byref(bitsPerPixel)
					)
		finally:
			libx11.XCloseDisplay(dsp)
		if GetLastError():
			return (0, 0, 0, 0)
		return (x.value, y.value, w.value, h.value)


# XGetWindowProperty in all its glory..
def get_property(xid, propType, propName):

	result = None
	dsp = libx11.XOpenDisplay('')
	try:
		atomPropName = libx11.XInternAtom(dsp, propName, False)
		bytesAfter = c_ulong()
		fmtReturned = c_int()
		nItems = c_ulong()
		pReturn = pointer(c_ubyte())
		typeReturned = Atom()
		# usual two step query process here. first query with no format, check
		# what format the method returns, query again with format returned
		try:
			result = libx11.XGetWindowProperty(
					dsp,
					xid,
					atomPropName,
					0,
					MAX_PROPERTY_VALUE_LEN / 4,
					False,
					propType,
					byref(typeReturned),
					byref(fmtReturned),
					byref(nItems),
					byref(bytesAfter),
					byref(pReturn)
				)
			if result != Success:
				return None
		finally:
			libx11.XFree(pReturn)
		if fmtReturned.value == PROPFMT_NONE:
			return None
		result = libx11.XGetWindowProperty(
				dsp,
				xid,
				atomPropName,
				0,
				MAX_PROPERTY_VALUE_LEN / 4,
				False,
				typeReturned,
				#propType,
				byref(typeReturned),
				byref(fmtReturned),
				byref(nItems),
				byref(bytesAfter),
				byref(pReturn)
				)
		#
		try:
			# errorcheck
			if result != Success:
				return None
			## may actually differ
			#if typeReturned.value!= propType.value:
			#	raise ValueError('Invalid property type: %s' % propName)
			if bytesAfter.value:
				raise ValueError('Not all bytes of property requested')

			# retrieve actual data for the returned type
			if fmtReturned.value == PROPFMT_CHAR_ARRAY:
				p = create_string_buffer(nItems.value)
				memmove(p, pReturn, sizeof(p))
				result = p.value
			elif fmtReturned.value == PROPFMT_SHORT_ARRAY:
				arr = (c_short * nItems.value)()
				memmove(arr, pReturn, sizeof(arr))
				result = [i for i in arr]
			elif fmtReturned.value == PROPFMT_LONG_ARRAY:
				arr = (c_long * nItems.value)()
				memmove(arr, pReturn, sizeof(arr))
				result = [i for i in arr]
			else:
				raise ValueError('Unknown proprty format')
		finally:
			libx11.XFree(pReturn)
	finally:
		libx11.XCloseDisplay(dsp)

	return result


def list_windows(dsp, window):
	rootWindow = Window()
	parentWindow = Window()
	pChildren = pointer(Window())
	nChildren = c_uint()
	try:
		libx11.XQueryTree(
				dsp,
				window.handle,
				byref(rootWindow),
				byref(parentWindow),
				byref(pChildren),
				byref(nChildren)
				)
		arr = (Window * nChildren.value)()
		memmove(arr, pChildren, sizeof(arr))
	finally:
		libx11.XFree(pChildren)
	return [PlatformWindow(i) for i in arr]

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
		window = PlatformWindow(libx11.XDefaultRootWindow(dsp))
		windows = [i for i in walker(dsp, window) if i.get_title() is not None]
	finally:
		libx11.XCloseDisplay(dsp)
	if GetLastError():
		return ()
	return windows

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	for window in toplevel_windows():
		print 'window: "%s" %s' % (window.get_title(), window.get_geometry())
