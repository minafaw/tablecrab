""""""

#************************************************************************************
# window manager base implementation
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

class WindowManagerBase(object):
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
		self._windows = self.window_list()
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

	def window_list(self):
		"""returns list of L{Window}s currently open
		@note: overwrite in derrived classes
		@note: the list returned should be in window stacking order, starting with
		the lowest window in the hirarchy (root window or desktop)
		"""
		raise NotImplementedError()


