"""x11 specific methods via shell

@dependences: xwininfo
"""

import re, subprocess

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
# pattern to match output from xwininfo (warning: not generic, just good enough for our purposes)
PatXWinInfo = re.compile('''
		\s*
		(?P<handle>0x[\dabcdef]+)\s+
		\"(?P<title>.+)\"\:\s+
		\(
			\"(?P<application>.+?)\".*?
		\)\s+
		(?P<w>\d+)x
		(?P<h>\d+)+
		.+?\s
		\+(?P<x>\-?\d+)
		\+(?P<y>\-?\d+)
		''',
		re.X|re.I)

def toplevel_windows():
	"""returns a list of all toplevel windows
	@return: (list) L{Window}s
	@note: we ignore windows here that do not have a name (title)
	"""
	windows = []
	out, err = subprocess.Popen(
		'xwininfo -root -tree', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
	if err:
		raise ValueError(err)
	for line in out.split('\n'):
		if ' (has no name): ' in line:
			continue
		match = PatXWinInfo.match(line)
		if match:
			d = match.groupdict()
			handle = int(d['handle'], 16)
			x = int(d['x'])
			y = int(d['y'])
			w = int(d['w'])
			h = int(d['h'])
			window = Window(handle, unicode(d['title'].encode('utf-8')), d['application'], (x, y, w, h))
			windows.append(window)
	return windows

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
