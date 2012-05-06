"""proove of concept and test bed implementation for a HUD. not tooo much to see here,
just two small buttons that get attatched to PokerStars lobby at (0, 0) of its client
ara.
"""

import pygtk
import gtk
import gobject

import WindowManager

try:
	import L10n
	_ = L10n.get_translation()
except ImportError:
	_ = lambda text: text

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

#NOTE: application name
# - when PokerStars lobby is created with "connecting.." dialog we get no application name for it
#


class Hud(gtk.Window):

	def __init__(self, hudManager, wmWindow):
		gtk.Window.__init__(self)

		self.hudManager = hudManager
		self.wmWindow = wmWindow
		self.tableSizeIndex = -1

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

		#NOTE: on win32 window_foreign_new() if passed an invalid handle returns a
		# pointer instead of None and segfaults on subsequent calls so we don't use it
		##gdkWindow = gtk.gdk.window_foreign_new(wmWindow.handle)
		##self.get_window().set_transient_for(gdkWindow)
		#-----------
		#NOTE: win32 - PokerStars lobby crashes randomly when we attatch something to
		# it. they may be checking for dialogs, news flyers, whatevs being around and
		# hit our window in the process. they may do something with it they should not do
		# with windows from other processes.
		try:
			handle = self.window.xid
		except AttributeError:
			handle = self.window.handle
		wmWindow.attatch(handle)



		self.buttonAddTableSize = gtk.Button('+')
		self.buttonAddTableSize.connect("clicked", self.on_button_add_table_size_clicked)
		self.buttonResizeTable = gtk.Button('Resize')
		self.buttonResizeTable.connect("clicked", self.on_button_resize_table_clicked)

		#
		self.retranslate()
		self.init_layout()

	def init_layout(self):
		box = gtk.HBox()
		self.add(box)
		box.pack_start(self.buttonAddTableSize, expand=False)
		box.pack_start(self.buttonResizeTable, expand=False)
		self.show_all()

	def retranslate(self):
		self.buttonAddTableSize.set_tooltip_text(_('Add table size'))
		self.buttonResizeTable.set_tooltip_text(_('Resize table to next size'))

	def handle_window_geometry_changed(self, wmWindow):
		self.wmWindow = wmWindow
		self.move(wmWindow.clientRect.x, wmWindow.clientRect.y)

	def handle_window_destroyed(self, wmWindow):
		self.wmWindow = None
		self.destroy()

	def on_button_add_table_size_clicked(self, button):
		#TODO: we may have to update wmWindow here
		self.hudManager.add_table_size(None, self.wmWindow.clientRect.w, self.wmWindow.clientRect.h)

	def on_button_resize_table_clicked(self, button):
		sizes = self.hudManager.get_table_sizes()
		if sizes:
			lastSize = sizes[self.tableSizeIndex]
			self.tableSizeIndex = sizes.index(lastSize) +1
			if self.tableSizeIndex >= len(sizes):
				self.tableSizeIndex = 0
			size = sizes[self.tableSizeIndex]
			self.wmWindow.set_size(size[1], size[2])

class TableSizesModel(gtk.ListStore):
	"""(gtk.ListStore) directory list"""

	#TODO: not shure if runtime translation works like this
	COLUMNS = (
			('name', str, _('Name')),
			('size', str, _('Size')),
			)
	def __init__(self, treeView):
		"""constructor
		@param treeView: treeView to associate the list to
		"""

		self._treeView = treeView

		# init ListStore
		self._columns, columnTypes = {}, []
		for i, (name, type_, _) in enumerate(self.COLUMNS):
			self._columns[name] = i
			columnTypes.append(type_)
		gtk.ListStore.__init__(self, *columnTypes)

		# init TreeView
		for i, (_, _type, _) in enumerate(self.COLUMNS):
			column = gtk.TreeViewColumn()
			self._treeView.append_column(column)
			cell = gtk.CellRendererText()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', i)
		self._treeView.set_model(self)

	def append_row(self, **kws):
		"""appends a row to the list
		@param kws: columnName1=value, columnName2=value
		"""
		columns = []
		#NOTE: we have to initialize all columns, otherwise gtk returns None as cell value
		for i, (name, _, _) in enumerate(self.COLUMNS):
			value = kws.pop(name, '')
			columns.append(i)
			columns.append(value)
		self.set(self.append(), *columns)
		if kws:
			raise ValueError('no such column. %s' % kws.keys()[0])

	def get_column_index(self, colName):
		"""returns index af a column given its column name
		@param colName: (str) name of the column
		@return: (int)
		"""
		return self._columns[colName]

	def get_row_count(self):
		"""returns number of rows in the list
		@return: (int)
		"""
		return self.iter_n_children(None)

	def get_value(self, row, colName):
		"""returns value of a column
		@param row: row the column resides in
		@param colName: (str) name of the column
		"""
		return self[row][self._columns[colName]]

	def retranslate(self):
		for i, column in enumerate(self._treeView.get_columns()):
			column.set_title(_(self.COLUMNS[i][2]))

	def set_value(self, row, colName, value):
		"""sets the value of a column
		@param row: row the column resides in
		@param colName: (str) name of the column
		@param value: value to set
		"""
		self[row][self._columns[colName]] = value



class HudManager(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self)
		self.set_title('HudManager')

		self.huds = {}
		self.windowManager = WindowManager.WindowManager()

		self.tableSizesList = gtk.TreeView()
		self.tableSizesScroll = gtk.ScrolledWindow()
		self.tableSizesScroll.add(self.tableSizesList)
		self.tableSizesModel = TableSizesModel(self.tableSizesList)
		self.tableSizes = []

		#
		self.init_layout()
		self.retranslate()
		gobject.timeout_add(500, self.on_window_manager_timeout)

	def init_layout(self):
		self.add(self.tableSizesScroll)
		self.show_all()

	def retranslate(self):
		self.tableSizesModel.retranslate()

	def get_table_sizes(self):
		return self.tableSizes

	def add_table_size(self, name, w, h):
		size = '%sx%s' % (w, h)
		if name is None:
			name = ''
		self.tableSizes.append((name, w, h))
		self.tableSizesModel.append_row(name=name, size=size)

	def on_window_manager_timeout(self):
		"""event dispatcher for our HUDs"""

		for event, param in self.windowManager.next():

			#TODO: something goes wrong when the lobby pops up with the "connecting.."
			# dialog. seems like we get no message that the lobby has been created
			if event == self.windowManager.EVENT_WINDOW_CREATED:
				wmWindow = param
				if wmWindow.application == 'PokerStars.exe' and wmWindow.title == 'PokerStars Lobby':
					hud = Hud(self, wmWindow)
					self.huds[wmWindow.handle] = hud

			elif event == self.windowManager.EVENT_WINDOW_GEOMETRY_CHANGED:
				wmWindow = param
				hud = self.huds.get(wmWindow.handle, None)
				if hud is not None:
					hud.handle_window_geometry_changed(wmWindow)

			elif event == self.windowManager.EVENT_WINDOW_DESTROYED:
				wmWindow = param
				hud = self.huds.get(wmWindow.handle, None)
				if hud is not None:
					hud.handle_window_destroyed(wmWindow)
					del self.huds[wmWindow.handle]

		return True

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	m = HudManager()
	m.connect('destroy', gtk.main_quit)
	m.show()
	gtk.main()
