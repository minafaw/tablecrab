
import pygtk
import gtk
import gobject

#************************************************************************************
# helpers
#************************************************************************************
class DebugWidget(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)
		self.connect('destroy', gtk.main_quit)
		self.scroll = gtk.ScrolledWindow()
		self.add(self.scroll)
		self.edit = gtk.TextView()
		self.scroll.add(self.edit)
		self.setup()
		self.show_all()
		self.show()
	def log(self, msg):
		p = self.edit.get_buffer()
		start,end = p.get_bounds()
		p.insert(end, msg)
		self.edit.scroll_to_iter(p.get_end_iter(), 0.0)
	def setup(self):
		"""overwrite in derrived classes"""

#************************************************************************************
# public methods and classes
#************************************************************************************
class WindowManager(gtk.Object):
	__gsignals__ = {
			'window-created': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT, )),
			'window-destroyed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT, )),
			'window-size-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT, )),
			}

	def __init__(self):
		gtk.Object.__init__(self)
		self._gdkWindows = []
		self._isRunning = False

	def is_running(self):
		return self._isRunning

	def start(self, timeout=500):
		if self._isRunning:
			raise ValueError('window manager is already running')
		self._isRunning = True
		gobject.timeout_add(timeout, self.on_timeout)

	def stop(self):
		if not self._isRunning:
			raise ValueError('window manager is not running')
		self._isRunning = False

	def on_timeout(self):
		gdkWindows = gtk.gdk.window_get_toplevels()
		gdkWindowsAll = self._gdkWindows + [i for i in gdkWindows if i not in self._gdkWindows]
		for gdkWindow in gdkWindowsAll:
			if gdkWindow not in gdkWindows:
				self.emit('window-destroyed', gdkWindow)
				continue
			if gdkWindow not in self._gdkWindows:
				gdkWindow._myGeometryOld = None
				self.emit('window-created', gdkWindow)
			geometry = gdkWindow.get_geometry()
			if gdkWindow._myGeometryOld != geometry:
				gdkWindow._myGeometryOld = geometry
				self.emit('window-size-changed', gdkWindow)
		self._gdkWindows = gdkWindows
		return self._isRunning

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':

	def test_window_manager():
		class TestWindowManager(DebugWidget):
			def setup(self):
				self.wm = WindowManager()
				self.wm.connect('window-created', lambda wm, handle: self.log('window-created: %s\n' % handle))
				self.wm.connect('window-destroyed', lambda wm, handle: self.log('window-destroyed: %s\n' % handle))
				self.wm.connect('window-size-changed', lambda wm, handle: self.log('window-size-changed: %s\n' % handle))
				self.wm.start()
		TestWindowManager()

		gtk.main()
	test_window_manager()
