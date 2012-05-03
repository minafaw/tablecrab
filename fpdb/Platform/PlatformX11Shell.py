# -*- coding: utf-8 -*-

"""x11 specific methods via shell

@dependences: xwininfo
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

import re, subprocess

__all__ = ['WindowManager', ]

#************************************************************************************
# helpers
#************************************************************************************
# check if X is running
#TODO: check if test if ok
out, err = subprocess.Popen(
		'ps -e | grep X', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
if not ' Xorg' in out:
	raise OSError('no X server running!')

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


def get_window_is_visible(handle):
	isVisible = False
	out, err = subprocess.Popen(
		'xwininfo -id %s' % handle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
		).communicate()
	if not err:
		for line in out.split('\n'):
			if 'Map State:' in line:
				isVisible = '\x20IsViewable' in line
	return isVisible

def window_list():
	"""returns a list of all windows currently open
	@note: list should always start at the root window (the desktop)
	@note: the list should be sorted in stacking oder. root first, topmost window last
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
			isVisible = get_window_is_visible(handle)
			window = Window(
					handle,
					unicode(d['title'].decode('utf-8')),
					d['application'],
					Rectangle(x, y, w, h),
					isVisible,
					)
			windows.append(window)
	return windows

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
class Rectangle(object):
	"""rectangle"""
	def __init__(self, x=0, y=0, w=0, h=0):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	@classmethod
	def new(klass, x=0, y=0, w=0, h=0):
		"""creates a new rectangle
		@return: (L{Rectangle})
		"""
		return klass(x, y, w, h)
	def __ne__(self, rect): return not self.__eq__(rect)
	def __eq__(self, rect):
		return (
			self.x == rect.x
			and self.w == rect.w
			and self.y == rect.y
			and self.h == rect.h
			)
	def is_empty(self):
		"""checks if the rectangle is empty
		@return: (bool)
		"""
		return self.w > 0 and self.h > 0
	def intersects(self, rect):
		"""checks if the rectangle has an intersection with another rectangle
		@return: (bool)
		"""
		return not (
			self.x > (rect.x+rect.w)
			or self.y > (rect.y+rect.h)
			or rect.x > (self.x+self.w)
			or rect.y > (self.y+self.h)
			)
	def to_tuple(self):
		"""converts the rectangle to a tuple"""
		return (self.x, self.y, self.w, self.h)

class Display(object):
	def __init__(self, windows):
		self._windows = windows

class Window(object):
	"""window implementation
	@ivar parent: (L{Window}) parent window or None
	@ivar application: (str) appllication that created the window
	@ivar geometry: (tuple) client area coordinates (x, y, w, h) relative to the screen
	@ivar handle: (int) platform dependend window handle
	@ivar title: (unicode) title of the window
	@ivar isVisible: (bool) True if the window is currently visible, False otherwise
	"""
	def __init__(self, parent, handle, title, application, geometry, isVisible):
		self.parent = parent
		self.application = application
		self.geometry = geometry
		self.handle = handle
		self.title = title
		self.isVisible = isVisible
	def __eq__(self, other):
		return self.handle == other.handle and self.application == other.application
	def __ne__(self, other): return not self.__eq__(other)

class WindowManager(object):
	"""window manager implementation

	run the manager as generator and process the events it returns on L{next}

	@cvar EVENT_DISPLAY_COMPOSITION: event generated on every hop. param: L{Display}
	@cvar EVENT_WINDOW_GEOMETRY_CHANGED: event generated when the geometry of a window has changed. param: L{Window}
	@cvar EVENT_WINDOW_TITLE_CHANGED: event generated when the title of a window has changed. param: L{Window}
	@cvar EVENT_WINDOW_VISIBILITY_CHANGED: event generated when the window becomes visible or gets hidden. param: L{Window}
	@cvar EVENT_WINDOW_DESTROYED: event generated when a window has been destroyed. param: L{Window}

	@note: L{Window}s passed in events are snapshots of windows not actual windows.
	they are meant for emidiate use. that is, the instances passed are never updated.
	instead	a new instance is passed on every event.
	"""
	EVENT_WINDOW_CREATED = 'window-created'
	EVENT_WINDOW_GEOMETRY_CHANGED = 'window-geometry-changed'
	EVENT_WINDOW_TITLE_CHANGED = 'window-title-changed'
	EVENT_WINDOW_VISIBILITY_CHANGED = 'window-visibility-changed'
	EVENT_WINDOW_DESTROYED = 'window-destroyed'
	EVENT_DISPLAY_COMPOSITION = 'display-composition'

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
		self._windows = window_list()
		for window in self._windows:
			if window in windowsOld:
				windowOld = windowsOld[windowsOld.index(window)]
				if window.geometry != windowOld.geometry:
					events.append((self.EVENT_WINDOW_GEOMETRY_CHANGED, window))
				if window.title != windowOld.title:
					events.append((self.EVENT_WINDOW_TITLE_CHANGED, window))
				if window.isVisible != windowOld.isVisible:
					events.append((self.EVENT_WINDOW_VISIBILITY_CHANGED, window))
			else:
				events.append((self.EVENT_WINDOW_CREATED, window))
				events.append((self.EVENT_WINDOW_GEOMETRY_CHANGED, window))
				events.append((self.EVENT_WINDOW_TITLE_CHANGED, window))
				events.append((self.EVENT_WINDOW_VISIBILITY_CHANGED, window))

		for window in windowsOld:
			if window not in self._windows:
				events.append((self.EVENT_WINDOW_DESTROYED, window))

		display =Display(self._windows[:])
		events.append((self.EVENT_DISPLAY_COMPOSITION, display))
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
				print '%s: 0x%x "%s" ("%s") %s visible=%s' % (
						event,
						window.handle,
						window.title,
						window.application,
						window.geometry.to_tuple(),
						window.isVisible,
						)
		time.sleep(0.5)
