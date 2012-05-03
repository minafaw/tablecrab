"""proove of concept and test bed implementation for a HUD. not tooo much to see here,
just two small buttons that get attatched to PokerStars lobby at (0, 0) of its client
ara.
"""

import pygtk
import gtk
import gobject

import WindowManager

#************************************************************************************
#
#************************************************************************************
#NOTE: focus handling. window we are attatched to has focus, our HUD gests clicked
# - x11: window keeps focus
# - wayland: ?
# - wine: window loses focus, HudManager gets it and get put to the foreground
# - native windows: ?
# - mac: ?
# + should be os/wm specific which window in the focus chain receives focus next
# + on win32 we would intercept WM_SETFOCUS and put focus back to prev window by hand
# + on wine we are 1) dealing with wine as window manager and 2) with the linux distos
#   window manager. things could work as expected if we had access to both from within
#   wine. obv there is no way to do so. so ..focus handling could be made to work on native
#   windows and on linux but not on wine. i think this could be ok along with some
#   explanatory words for the user.

#
#NOTE: gtk.gdk.window_foreign_new() from invalid xid/hwnd/whatevs
# - x11: returns None
# - wayland: ?
# - wine: returns a gdk.Window to hapily segfault on subsequent calls
# - native windows: ?
# - mac: ?
# + imo gtk.gdk.window_foreign_new() is not intended to be used with windows not belonging
#   to the current process. "foreign" relates to "foreign to gtk" not to "foreign to the process".
#   so i'd consider the method unusable for the purpose. our window manager(s) should
#   handle all things necessary for us according to means the platform provides. our task
#   is to implement things in a failsave way, which should be doable on x11 and native
#   windows. no idea about mac and wayland though.

class Hud(gtk.Window):
	def __init__(self, platformWindow):
		gtk.Window.__init__(self)

		self.set_title('Hud')
		self.set_decorated(0)
		self.set_focus(None)
		self.set_focus_on_map(False)
		self.set_accept_focus(False)
		self.set_skip_pager_hint(True)
		self.set_skip_taskbar_hint(True)

		# init hud for window
		#NOTE: have to realize() window first, otherwise window has no handle
		#NOTE: have to set stransient before showing the window, otherwise it won't work
		self.realize()
		gdkWindow = gtk.gdk.window_foreign_new(platformWindow.handle)
		self.get_window().set_transient_for(gdkWindow)

		self.button1 = gtk.Button('+')
		self.button2 = gtk.Button('Resize')

		box = gtk.HBox()
		self.add(box)
		box.pack_start(self.button1, expand=False)
		box.pack_start(self.button2, expand=False)

		self.show_all()
		#self.show()

		print bool(gtk.gdk.window_foreign_new(1234567))

	def handle_window_geometry_changed(self, platformWindow):
		self.move(platformWindow.geometry.x, platformWindow.geometry.y)

	def handle_window_destroyed(self, platformWindow):
		self.destroy()


class HudManager(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self)
		self.set_title('HudManager')

		self.huds = {}
		self.windowManager = WindowManager.WindowManager()

		gobject.timeout_add(500, self.on_window_manager_timeout)

	def on_window_manager_timeout(self):
		"""event dispatcher for our HUDs"""

		for event, param in self.windowManager.next():

			#TODO: something goes wrong when the lobby pops up with the "connecting.."
			# dialog. seems like we get no message that the lobby has been created
			if event == self.windowManager.EVENT_WINDOW_CREATED:
				platformWindow = param
				if platformWindow.application == 'PokerStars.exe' and platformWindow.title == 'PokerStars Lobby':
					self.huds[platformWindow.handle] = Hud(platformWindow)

			elif event == self.windowManager.EVENT_WINDOW_GEOMETRY_CHANGED:
				platformWindow = param
				hud = self.huds.get(platformWindow.handle, None)
				if hud is not None:
					hud.handle_window_geometry_changed(platformWindow)

			elif event == self.windowManager.EVENT_WINDOW_DESTROYED:
				platformWindow = param
				hud = self.huds.get(platformWindow.handle, None)
				if hud is not None:
					hud.handle_window_destroyed(platformWindow)
					del self.huds[platformWindow.handle]

		return True

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	m = HudManager()
	m.connect('destroy', gtk.main_quit)
	m.show()
	gtk.main()
