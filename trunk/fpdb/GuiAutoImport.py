#TODO:
# - default button in DlgEditDirectory?
# - gtk.Entries need undo/redo
# - comb over layout
# - how to save / restore settings?
# - add controls for: ImportTimeout, start/stop import, Logging
# - add support for directory status feedback (invalid directory, currently monitoring, whatevs)
# - signal start/stop import, passing a list of directories on start import
# - keyboard shortcuts / tooltips
# - button 'start/stop import' should be enabled/disabled acc to if directories are in list

#OPEN QUESTIONS:
# - what to do when a user edits the list while import is running? we can not know when
#   editing is done to restart importing with the new credentials. so maybe we should
#   tell the user that changes only take effect after restarting import? maybe set status
#   to 'Pending' or 'New'?
# - how to handle default directories? would be nice to have a list somewhere for the user
#   to pick from. 
# - how to present settings like 'ImportTimeout'? does not really belong into the gui
#   ..more like a separate dialog. i guess not doable untill fpdb gets a reall settings
#   gui.
# - uniqueness of directories in the list. not shure if should check for it. exsample:
#   multi user setup with one shared config. to directories '~/dir' and 'home/user/dir'
#   can point to the same directory for one user and to two different once for another.
#   similar for making shure dirctories exist. i don't think we should do this. examle: 
#   user starts gui and then mounts drive where directory exists.
#       i guess we have to accept user input unconditionally and let other components
#    find out at runtime which directories they can deal with.

#import L10n
#TODO: just a placeholder so far
_ = lambda text: text
import pygtk
pygtk.require('2.0')
import gtk
import gobject
#************************************************************************************
#
#************************************************************************************
#TODO: move class to some general purpose module
class BoxDirectorySelector(gtk.HBox):
	__gsignals__ = {
		'directory-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,	(gobject.TYPE_STRING,)),
		'value-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
		}
	
	def __init__(self, *args, **kws):
		gtk.HBox.__init__(self, *args, **kws)
		self.button = gtk.Button()
		self.button.connect("clicked", self.on_button_select_directory_clicked)
		self.edit = gtk.Entry()
		self.edit.connect('changed', self.on_edit_changed)
			
	def get_directory(self):
		return self.edit.get_text()
	
	def init_layout(self):
		self.pack_start(self.edit, expand=True)
		self.pack_start(self.button, expand=False)
		self.show_all()
	
	def retranslate(self):
		self.button.set_label(_('...'))
			
	def set_directory(self, directory):
		self.edit.set_text(directory)
			
	def on_button_select_directory_clicked(self, button):
		dlg = gtk.FileChooserDialog(
					title='foo',
				action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
				buttons=(
					gtk.STOCK_CANCEL,
					gtk.RESPONSE_CANCEL,
					gtk.STOCK_OPEN,
					gtk.RESPONSE_OK
					)
				)
		dlg.set_destroy_with_parent(True)
		dlg.set_filename(self.get_directory())
		result = dlg.run()
		directory = dlg.get_filename()
		dlg.destroy()
		if result == gtk.RESPONSE_OK:
			self.set_directory(directory)
			self.emit('directory_selected', directory)
			
	def on_edit_changed(self, edit):
		self.emit('value-changed', edit.get_text())
		
#************************************************************************************
#
#************************************************************************************
#TODO: move class to some general purpose module
class WidgetLogView(gtk.ScrolledWindow):
	def __init__(self, maxLines=1000, modeAppend=True):
		gtk.ScrolledWindow.__init__(self)
		self._edit = gtk.TextView()
		self._maxLines = maxLines
		self._modeAppend = modeAppend
		self._edit.set_editable(False)
		self.add(self._edit)
		
	def get_max_lines(self):
		return self._maxLines
		
	def set_max_lines(self, n):
		self._maxLines = n
		
	def log(self, msg):
		if self._modeAppend:
			self.log_append(msg)
		else:
			self.log_prepend(msg)
		
	def log_prepend(self, msg):
		p = self._edit.get_buffer()
		start = p.get_start_iter()
		p.insert(start, msg)
		self.trunc_lines_prepend()
		self._edit.scroll_to_iter(p.get_start_iter(), 0.0)
		
	def trunc_lines_prepend(self):
		p = self._edit.get_buffer()
		nLines = p.get_line_count()
		while nLines >= 0:
			if nLines <= self._maxLines:
				break
			else:
				end = p.get_end_iter()
				start = p.get_end_iter()
				start.backward_line()
				p.delete(start, end)
			nLines = p.get_line_count()
		
	def log_append(self, msg):
		p = self._edit.get_buffer()
		start,end = p.get_bounds()
		p.insert(end, msg)
		self.trunc_lines_append()
		self._edit.scroll_to_iter(p.get_end_iter(), 0.0)
		
	def trunc_lines_append(self):
		p = self._edit.get_buffer()
		nLines = p.get_line_count()
		while nLines >= 0:
			if nLines <= self._maxLines:
				break
			else:
				start = p.get_start_iter()
				end = p.get_start_iter()
				end.forward_line()
				p.delete(start, end)
			nLines = p.get_line_count()
		 
#************************************************************************************
#
#************************************************************************************		
class DirectoryListModel(gtk.ListStore):
	#TODO: not shure if runtime translation works like this
	COLUMNS = (
			('directoryName', str, _('Name')),
			('directoryStatus', str, _('Status')),
			('directory', str, _('Directory')),
			)
	def __init__(self, treeView):
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
				
	def get_column_index(self, colName):
		return self._columns[colName]
		
	def get_value(self, row, colName):
		return self[row][self._columns[colName]]
	
	def retranslate(self):
		for i, column in enumerate(self._treeView.get_columns()):
			column.set_title(_(self.COLUMNS[i][2]))
	
	def set_value(self, row, colName, value):
		self[row][self._columns[colName]] = value
		
	def get_row_count(self):
		return self.iter_n_children(None)
		
	def append_row(self, **kws):
		columns = []
		#NOTE: we have to initialize all columns, otherwise gtk returns None as cell value 
		for i, (name, _, _) in enumerate(self.COLUMNS):
			value = kws.get(name, '')
			columns.append(i)
			columns.append(value)
		self.set(self.append(), *columns)
			
#************************************************************************************
#
#************************************************************************************
class DlgEditDirectory(gtk.Dialog):
		
	def __init__(self, modeNew=True, directoryName='', directory='', defaultDirectories=None):
		if modeNew: 
			title = _('Add directory..')
		else:
			title = _('Edit directory..')
		gtk.Dialog.__init__(
				self, 
				title=title,
				flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				buttons=(
					gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
					gtk.STOCK_OK, gtk.RESPONSE_OK
					),
				)
		self.labelName = gtk.Label(_('Name:'))
		self.editName = gtk.Entry()
		self.labelDirectory = gtk.Label(_('Directory:'))
		
		self.directorySelector = BoxDirectorySelector()
		self.directorySelector.retranslate()
		self.directorySelector.set_directory(directory)
		if modeNew and not directoryName:
			directoryName = _('New directory')
		self.editName.set_text(directoryName)
				
		self.defaultDirectories = defaultDirectories
		self.labelDefaults = None
		self.comboDefaults = None
		if self.defaultDirectories is not None:
			self.labelDefaults = gtk.Label(_('Defaults:'))
			self.comboDefaults = gtk.combo_box_new_text()
			for directoryName, directory in self.defaultDirectories:
				self.comboDefaults.append_text(directoryName)
			self.comboDefaults.connect('changed', self.on_combo_defaults_changed)
				
		self.init_layout()
						
	def init_layout(self):
		box1 = gtk.VBox()
		box1.pack_start(self.labelName)
		box1.pack_start(self.labelDirectory)
		if self.labelDefaults is not None:
			box1.pack_start(self.labelDefaults)
		
		
		box2 = gtk.HBox()
		box2.pack_start(self.directorySelector.edit, expand=True)
		box2.pack_start(self.directorySelector.button, expand=False)
		
		box3 = gtk.VBox()
		box3.pack_start(self.editName)
		box3.pack_start(box2)
		if self.comboDefaults is not None:
			box3.pack_start(self.comboDefaults)
			
		box4 = gtk.HBox()
		box4.pack_start(box1, expand=False)
		box4.pack_start(box3)
			
		self.vbox.pack_start(box4, expand=False)
		self.vbox.pack_start(gtk.VBox())
			
		self.show_all()
		
	def get_directory(self):
		return self.directorySelector.get_directory()
	
	def get_directory_name(self):
		return self.editName.get_text()
		
	def on_combo_defaults_changed(self, combo):
		directoryName, directory = self.defaultDirectories[combo.get_active()]
		self.editName.set_text(directoryName)
		self.directorySelector.set_directory(directory)
		
#************************************************************************************
#
#************************************************************************************
class BoxAutoImport(gtk.VBox):
		
	__gsignals__ = {
		'start-import': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'stop-import': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'directories-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'auto-start-import-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'import-timeout-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'splitter-position-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		}
	
	
	def __init__(self,):
		gtk.VBox.__init__(self)
				
		self.defaultDirectories = None
		
		self.splitter = gtk.VPaned()
		self.splitter.connect('size-allocate', self.on_splitter_size_allocate)
		
		# setup directory list
		self.directoryList = gtk.TreeView()
		self.directoryList.connect('cursor-changed', self.on_diretory_list_cursor_changed)
		self.directoryList.connect('row-activated', self.on_directory_list_row_activated)
		
		self.directoryList.set_grid_lines(True)
		self.directoryList.set_enable_search(False)
		self.directoryModel = DirectoryListModel(self.directoryList)
												
		# setup scrolling for directory list
		self.directoryListScroll = gtk.ScrolledWindow()
		self.directoryListScroll.add(self.directoryList)
					
		self.buttonNew = gtk.Button()
		self.buttonNew.connect("clicked", self.on_button_new_clicked)
		self.buttonEdit = gtk.Button()
		self.buttonEdit.connect("clicked", self.on_button_edit_clicked)
		self.buttonUp = gtk.Button()
		self.buttonUp.connect("clicked", self.on_button_up_clicked)
		self.buttonDown = gtk.Button()
		self.buttonDown.connect("clicked", self.on_button_down_clicked)
		self.buttonRemove = gtk.Button()
		self.buttonRemove.connect("clicked", self.on_button_remove_clicked)
			
		self.checkAutoStartImport = gtk.CheckButton()
		self.checkAutoStartImport.connect('toggled', self.on_check_auto_start_import_toggled)
		self.labelImportTimeout = gtk.Label()
		self.spinImportTimeout = gtk.SpinButton()
		self.spinImportTimeout.connect('value-changed', self.on_spin_import_timeout_value_changed)
			
		self.logView = WidgetLogView(maxLines=9, modeAppend=False)
		
		self.buttonImport = gtk.ToggleButton()
		self.buttonImport.connect("clicked", self.on_button_import_clicked)
				
		self.adjust_directory_list_widgets()
			
	def adjust_directory_list_widgets(self):
		editEnabled = self.directoryList.get_sensitive()
		selection = self.directoryList.get_selection()
		model, selected = selection.get_selected()
		nRows = self.directoryModel.get_row_count()
		hasSelection = selected is not None
		canMoveUp = False
		canMoveDown = False
		if hasSelection:
			path = model.get_path(selected)
			iRow = path[0]
			canMoveUp = iRow > 0
			canMoveDown = iRow < (nRows -1)
		self.buttonNew.set_sensitive(editEnabled)
		self.buttonEdit.set_sensitive(hasSelection and editEnabled)
		self.buttonUp.set_sensitive(canMoveUp and editEnabled)
		self.buttonDown.set_sensitive(canMoveDown and editEnabled)
		self.buttonRemove.set_sensitive(hasSelection and editEnabled)
		
		self.logView.set_sensitive(not editEnabled)
		self.buttonImport.set_sensitive(bool(nRows))
		if self.buttonImport.get_active() and not bool(nRows):
			self.buttonImport.set_active(False)
			
	def retranslate(self):
		self.directoryModel.retranslate()
		self.buttonNew.set_label(_('New'))
		self.buttonEdit.set_label(_('Edit'))
		self.buttonUp.set_label(_('Up'))
		self.buttonDown.set_label(_('Down'))
		self.buttonRemove.set_label(_('Remove'))
		self.checkAutoStartImport.set_label(_('Autostart import'))
		self.labelImportTimeout.set_text(_('Import timeout:'))
		if self.buttonImport.get_active():
			self.buttonImport.set_label(_('Stop import'))
		else:
			self.buttonImport.set_label(_('Start import'))
		
	def init_layout(self):
		self.pack_start(self.splitter)
						
		box1 = gtk.VBox()
		self.splitter.add(box1)
		box2 = gtk.HBox()
		box1.pack_start(self.directoryListScroll)
		box1.pack_start(box2, expand=False)
		
		box2.pack_start(self.buttonNew)
		box2.pack_start(self.buttonEdit)
		box2.pack_start(self.buttonUp)
		box2.pack_start(self.buttonDown)
		box2.pack_start(self.buttonRemove)
						
		box1 = gtk.VBox()
		self.splitter.add(box1)
		box1.pack_start(self.logView, expand=True)
		
		box2 = gtk.HBox()
		box1.pack_start(box2, expand=False)
		
		box3 = gtk.VBox()
		box2.pack_start(box3)
		box3.pack_start(self.checkAutoStartImport)
		
		box2.pack_start(gtk.VSeparator())
				
		box3 = gtk.VBox()
		box2.pack_start(box3)
		box4 = gtk.HBox()
		box3.pack_start(box4)
		box4.pack_start(self.labelImportTimeout, expand=False)
		box4.pack_start(self.spinImportTimeout)
		
		box1.pack_start(self.buttonImport, expand=False)
			
		self.show_all()
		
	def log(self, msg):
		self.logView.log(msg)
		
	def on_button_import_clicked(self, button):
		if button.get_active():
			button.set_label(_('Stop import'))
			self.directoryList.set_sensitive(False)
			self.emit('start-import')
		else:
			button.set_label(_('Start import'))
			self.directoryList.set_sensitive(True)
			self.emit('stop-import')
		self.adjust_directory_list_widgets()
		
		
	def on_button_new_clicked(self, button):
		dlg = DlgEditDirectory(modeNew=True, defaultDirectories=self.defaultDirectories,)
		result = dlg.run()
		directoryName = dlg.get_directory_name()
		directory =  dlg.get_directory()
		dlg.destroy()
		if result == gtk.RESPONSE_OK:
			self.directoryModel.append_row(directoryName=directoryName, directory=directory)
			# scroll to row + activate row
			selection = self.directoryList.get_selection()
			nRows = self.directoryModel.get_row_count()
			treeIter = self.directoryModel.get_iter(nRows-1)
			selection.select_iter(treeIter)
			self.directoryList.scroll_to_cell(self.directoryModel.get_path(treeIter))
			# finally
			self.adjust_directory_list_widgets()
			self.emit('directories-changed')
					
	def on_button_edit_clicked(self, button):
		selection = self.directoryList.get_selection()
		model, selected = selection.get_selected()
		hasSelection = selected is not None
		if hasSelection:
			path = model.get_path(selected)
			iRow = path[0]
			treeIter = model.get_iter(iRow)
			directoryName = model.get_value(treeIter, 'directoryName')
			directory = model.get_value(treeIter, 'directory')
			dlg = DlgEditDirectory(
					modeNew=False, 
					directoryName=directoryName, 
					directory=directory,
					defaultDirectories=self.defaultDirectories,
					)
			result = dlg.run()
			directoryName = dlg.get_directory_name()
			directory =  dlg.get_directory()
			dlg.destroy()
			if result == gtk.RESPONSE_OK:
				model.set_value(iRow, 'directoryName', directoryName)
				model.set_value(iRow, 'directory', directory)
				self.emit('directories-changed')
		
	def on_button_up_clicked(self, button):
		selection = self.directoryList.get_selection()
		model, selected = selection.get_selected()
		hasSelection = selected is not None
		if hasSelection:
			path = model.get_path(selected)
			iRow = path[0]
			iRowNext = iRow -1
			self.directoryModel.swap(model.get_iter(iRow), model.get_iter(iRowNext))
			self.adjust_directory_list_widgets()
			self.emit('directories-changed')
		
	def on_button_down_clicked(self, button):
		selection = self.directoryList.get_selection()
		model, selected = selection.get_selected()
		hasSelection = selected is not None
		if hasSelection:
			path = model.get_path(selected)
			iRow = path[0]
			iRowNext = iRow +1
			self.directoryModel.swap(model.get_iter(iRow), model.get_iter(iRowNext))
			self.adjust_directory_list_widgets()
			self.emit('directories-changed')
		
	def on_button_remove_clicked(self, button):
		selection = self.directoryList.get_selection()
		model, selected = selection.get_selected()
		hasSelection = selected is not None
		if hasSelection:
			path = model.get_path(selected)
			iRow = path[0]
			self.directoryModel.remove(model.get_iter(iRow))
			# restore selection if possible
			if model.get_row_count():
				iRowNext = iRow -1
				if iRowNext < 0:
					iRowNext = iRow
				selection.select_path(iRowNext)
			self.adjust_directory_list_widgets()
			self.emit('directories-changed')
			
	def on_check_auto_start_import_toggled(self, checkBox):
		self.emit('auto-start-import-changed')
	
	def on_diretory_list_cursor_changed(self, directoryList):
		self.adjust_directory_list_widgets()
		
	def on_directory_list_row_activated(self, *args):
		self.on_button_edit_clicked(self.buttonEdit)
		
	def on_spin_import_timeout_value_changed(self, spinBox):
		self.emit('import-timeout-changed')
		
	def get_directories(self):
		pass
	
	def set_directories(self, directories):
		pass
		
	def set_default_directories(self, directories):
		self.defaultDirectories = directories
		
	def get_splitter_pos(self):
		return self.splitter.get_position()
		
	def set_splitter_pos(self, pos):
		self.splitter.set_position(pos)
		
	def get_auto_start_import(self):
		pass
		
	def set_auto_start_import(self, flag):
		pass
		
	def set_import_timeout(self, value):
		pass
		
	def get_import_timeout(self):
		pass
		
	def set_directory_status(self, ):
		pass
		
	def on_splitter_size_allocate(self, splitter, allocation):
		self.emit('splitter-position-changed')
		
		
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':	
	
	class MyHandler(object):
		def __init__(self, boxAutoImport):
			self.boxAutoImport = boxAutoImport
			self.boxAutoImport.connect('start-import', self.on_start_import)
			self.boxAutoImport.connect('stop-import', self.on_stop_import)
			
		def on_start_import(self, boxAutoImport):
			boxAutoImport.log('start import\n')
		
		def on_stop_import(self, boxAutoImport):
			boxAutoImport.log('stop import\n')
			
	boxAutoImport = BoxAutoImport()
	handler = MyHandler(boxAutoImport)
	boxAutoImport.init_layout()
	boxAutoImport.retranslate()
	boxAutoImport.set_default_directories((('foo', '/foo'), ('bar', '/bar')))
	
	m = gtk.Window()
	m.connect('destroy', gtk.main_quit)
	m.add(boxAutoImport)
	m.show()
	gtk.main()


