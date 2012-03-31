#TODO:
# - default button in DlgEditDirectory?
# - gtk.Entries need undo/redo
# - make shure directories are unique in the list
# - comb over layout
# - how to save / restore settings?
# - add controls for: ImportTimeout, start/stop import, Logging
# - add support for directory status feedback (invalid directory, currently monitoring, whatevs)
# - signal start/stop import, passing a list of directories on start import
# - keyboard shortcuts / tooltips
# - button 'start/stop import' should be enabled/disabled acc to if directories are in list

#QUESTIONS:
# - what to do when a user edits the list while import is running? we can not know when
#   editing is done to restart importing with the new credentials. so maybe we should
#   tell the user that changes only take effect after restarting import? maybe set status
#   to 'Pending' or 'New'?
# - how to handle default directories? would be nice to have a list somewhere for the user
#   to pick from. 
# - how to present settings like 'ImportTimeout'? does not really belong into the gui
#   ..more like a separate dialog. i guess not doable untill fpdb gets a reall settings
#   gui.

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
	'directory-selected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,	(gobject.TYPE_STRING,)),
	'value-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
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
		
	def __init__(self, modeNew=True, directoryName='', directory=''):
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
		
		if modeNew and not directoryName:
			directoryName = _('New diretory')
		self.editName.set_text(directoryName)
		self.directorySelector.set_directory(directory)
		self.init_layout()
						
	def init_layout(self):
		box1 = gtk.VBox()
		box1.pack_start(self.labelName)
		box1.pack_start(self.labelDirectory)
		
		box2 = gtk.HBox()
		box2.pack_start(self.directorySelector.edit, expand=True)
		box2.pack_start(self.directorySelector.button, expand=False)
		
		box3 = gtk.VBox()
		box3.pack_start(self.editName)
		box3.pack_start(box2)
			
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
		
#************************************************************************************
#
#************************************************************************************
class BoxAutoImport(gtk.VBox):
		
	def __init__(self,):
		gtk.VBox.__init__(self)
				
		self.splitter = gtk.VPaned()
		
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
			
		self.logView = WidgetLogView(maxLines=9, modeAppend=False)
		
		self.buttonAutoImport = gtk.ToggleButton()
		self.buttonAutoImport.connect("clicked", self.on_button_auto_import_clicked)
				
		self.adjust_directory_list_widgets()
			
	def adjust_directory_list_widgets(self):
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
		self.buttonEdit.set_sensitive(hasSelection)
		self.buttonUp.set_sensitive(canMoveUp)
		self.buttonDown.set_sensitive(canMoveDown)
		self.buttonRemove.set_sensitive(hasSelection)
		
	def retranslate(self):
		self.directoryModel.retranslate()
		self.buttonNew.set_label(_('New'))
		self.buttonEdit.set_label(_('Edit'))
		self.buttonUp.set_label(_('Up'))
		self.buttonDown.set_label(_('Down'))
		self.buttonRemove.set_label(_('Remove'))
		if self.buttonAutoImport.get_active():
			self.buttonAutoImport.set_label(_('Stop import'))
		else:
			self.buttonAutoImport.set_label(_('Start import'))
		
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
		box1.pack_start(self.buttonAutoImport, expand=False)
			
		self.show_all()
				
	N = 0
	def on_button_auto_import_clicked(self, button):
		if button.get_active():
			button.set_label(_('Stop import'))
		else:
			button.set_label(_('Start import'))
			
		self.N += 1
		self.logView.log('message number: %s\n' % self.N)
		
	
	def on_button_new_clicked(self, button):
		dlg = DlgEditDirectory(modeNew=True)
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
			dlg = DlgEditDirectory(modeNew=False, directoryName=directoryName, directory=directory)
			result = dlg.run()
			directoryName = dlg.get_directory_name()
			directory =  dlg.get_directory()
			dlg.destroy()
			if result == gtk.RESPONSE_OK:
				model.set_value(iRow, 'directoryName', directoryName)
				model.set_value(iRow, 'directory', directory)
		
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
			
	def on_diretory_list_cursor_changed(self, directoryList):
		self.adjust_directory_list_widgets()
		
	def on_directory_list_row_activated(self, *args):
		self.on_button_edit_clicked(self.buttonEdit)
		
		
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':	
	w = BoxAutoImport()
	w.init_layout()
	w.retranslate()
	m = gtk.Window()
	m.connect('destroy', gtk.main_quit)
	m.add(w)
	m.show()
	gtk.main()


