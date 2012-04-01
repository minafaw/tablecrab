# -*- coding: utf-8 -*-

#************************************************************************************
#LICENCE: MIT License (MIT)
#
# Copyright (c) 2012 Jürgen Urner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# software and associated documentation files (the "Software"), to deal in the Software 
# without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, subject to the following 
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies 
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE 
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE 
# OR OTHER DEALINGS IN THE SOFTWARE.

#************************************************************************************
#VERSION HISTORY:
#
# <0.1>
# initial relase

#************************************************************************************
#TODO:
# - documentation
# - default button in DlgEditDirectory?
# - gtk.Entries need undo/redo
# - tooltips
# - bg/fg color of directory status
# - save/restore DlgEditDirectory geometry
# - when in edit more we can not scroll logViewer

#************************************************************************************
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
# - uniqueness of directories in the list. not shure if should check for it. exsample:
#   multi user setup with one shared config. to directories '~/dir' and 'home/user/dir'
#   can point to the same directory for one user and to two different once for another.
#   similar for making shure dirctories exist. i don't think we should do this. examle: 
#   user starts gui and then mounts drive where directory exists.
#       i guess we have to accept user input unconditionally and let other components
#    find out at runtime which directories they can deal with.

import pygtk
pygtk.require('2.0')
import gtk
import gobject
try:
    import L10n
    _ = L10n.get_translation()
except ImportError:
    _ = lambda text: text
#************************************************************************************
#
#************************************************************************************
__version__ = '0.1'

#************************************************************************************
#
#************************************************************************************
#TODO: move class to some general purpose module
class BoxDirectorySelector(gtk.HBox):
    """(gtk.HBox) user interface to let the user select a directory
    @signal directory-selected: triggered after the user has selected a directory via the
    'select directory' button
    @signal value-changed: triggered whenever the value of edit box the changes
    @cvar edit: directory edit box
    @cvar button: dircectory seletor button
    """
    __gsignals__ = {
        'directory-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,    (gobject.TYPE_STRING,)),
        'value-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        }
    
    def __init__(self):
        """constructor
        """
        gtk.HBox.__init__(self)
        self.button = gtk.Button()
        self.button.connect("clicked", self.on_button_select_directory_clicked)
        self.edit = gtk.Entry()
        self.edit.connect('changed', self.on_edit_changed)
            
    def get_directory(self):
        """returns the directory"""
        return self.edit.get_text()
    
    def init_layout(self):
        """initializes the layout for the user interface
        @note: make shure to call this method after intitializing the interface
        """
        self.pack_start(self.edit, expand=True)
        self.pack_start(self.button, expand=False)
        self.show_all()
    
    def retranslate(self):
        """retranslates the user interface.
        @note: make shure to call this method after intitializing the interface and
        on language changes.
        """
        self.button.set_label(_('...'))
            
    def set_directory(self, directory):
        """sets the contents of the edit box to the specified string
        qparam directory: (str)
        """
        self.edit.set_text(directory)
        
    def on_button_select_directory_clicked(self, button):
        """signal handler for the 'select directory' button"""
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
        """signal handler for the edit box"""
        self.emit('value-changed', edit.get_text())
        
#************************************************************************************
#
#************************************************************************************
#TODO: move class to some general purpose module
class WidgetLogView(gtk.ScrolledWindow):
    """(gtk.ScrolledWindow) logging widget with max lines support
    """
    
    def __init__(self, maxLines=1000, modeAppend=True):
        """constructor
        @param maxLines: (int) maximum number of lines allowed in the widget. 
        excess lines will get truncated.
        @param modeAppend: (bool) if True, new lines will be appended, if False they will 
        be prepended
        """
        gtk.ScrolledWindow.__init__(self)
        self._edit = gtk.TextView()
        self._maxLines = maxLines
        self._modeAppend = modeAppend
        self._edit.set_editable(False)
        self.add(self._edit)
        
    def _log_append(self, msg):
        """private method to unconditionally add a message to the bottom of the list. no truncation is dome 
        in the call
        @param msg: (str)
        """
        p = self._edit.get_buffer()
        start,end = p.get_bounds()
        p.insert(end, msg)
        self._trunc_lines()
        self._edit.scroll_to_iter(p.get_end_iter(), 0.0)
    
    def _log_prepend(self, msg):
        """private method to unconditionally add a message to the top of the list. no truncation is dome 
        in the call
        @param msg: (str)
        """
        p = self._edit.get_buffer()
        start = p.get_start_iter()
        p.insert(start, msg)
        self._trunc_lines()
        self._edit.scroll_to_iter(p.get_start_iter(), 0.0)
    
    def _trunc_lines(self):
        """private method to trauncate lines"""
        if self._modeAppend:
            self._trunc_lines__append()
        else:
            self._trunc_lines_prepend()
    
    def _trunc_lines_append(self):
        """truncates lines starting from the bottom of the list according to max lines
        """
        p = self._edit.get_buffer()
        nLines = p.get_line_count()
        while nLines > 0:
            if nLines <= self._maxLines +1:
                break
            start = p.get_start_iter()
            end = p.get_start_iter()
            end.forward_line()
            p.delete(start, end)
            nLines = p.get_line_count()
            
    def _trunc_lines_prepend(self):
        """truncates lines starting from the top of the list according to max lines
        """
        p = self._edit.get_buffer()
        nLines = p.get_line_count()
        while nLines > 0:
            if nLines <= self._maxLines +1:
                break
            end = p.get_end_iter()
            start = p.get_end_iter()
            start.backward_line()
            p.delete(start, end)
            nLines = p.get_line_count()
        
    def get_max_lines(self):
        """returns max lines allowed
        @return: (int)
        """
        return self._maxLines
    
    def log_message(self, msg):
        """logs a message
        @param msg: (str)
        """
        if self._modeAppend:
            self._log_append(msg)
        else:
            self._log_prepend(msg)
    
    def set_max_lines(self, n):
        """sets maximum number of lines allowed
        @param n: (int)
        """
        self._maxLines = n
        self._trunc_lines()

#************************************************************************************
#
#************************************************************************************        
class DirectoryListModel(gtk.ListStore):
    """(gtk.ListStore) directory list"""
    
    #TODO: not shure if runtime translation works like this
    COLUMNS = (
            ('directoryName', str, _('Name')),
            ('directoryStatus', str, _('Status')),
            ('directory', str, _('Directory')),
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
        
#************************************************************************************
#
#************************************************************************************
class DlgEditDirectory(gtk.Dialog):
    """(gtk.Dialog) to edit a directory
    """
        
    def __init__(self, modeNew=True, directoryName='', directory='', defaultDirectories=None):
        """constructor
        @param modeNed: (bool) if true dialog is started to edit a new directory, if False
        to edit an existing one.
        @param directoryName:(str) name of the directory
        @param directory: (str) directory path
        @param defaultDirectories: (list) of (directoryName, directory) tuples to pick from.
        if None the corrosponding controls will not be available.
        """
        if modeNew: 
            title = _('New directory..')
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
        
        self.editName = gtk.Entry()
        self.editName.set_tooltip_text(_('Name of the directory'))
        self.labelName = gtk.Label()
        if modeNew and not directoryName:
            directoryName = _('New directory')
        self.editName.set_text(directoryName)
        self.labelName.set_text_with_mnemonic(_('_Name:'))
        self.labelName.set_mnemonic_widget(self.editName)
            
        self.directorySelector = BoxDirectorySelector()
        self.directorySelector.retranslate()
        self.directorySelector.edit.set_tooltip_text(_('Location of the directory'))
        self.directorySelector.button.set_tooltip_text(_('Select a location'))
        self.directorySelector.set_directory(directory)
        self.labelDirectory = gtk.Label()
        self.labelDirectory.set_text_with_mnemonic(_('_Directory:'))
        self.labelDirectory.set_mnemonic_widget(self.directorySelector.edit)
                        
        self.defaultDirectories = defaultDirectories
        self.labelDefaults = None
        self.comboDefaults = None
        if self.defaultDirectories is not None:
            self.comboDefaults = gtk.combo_box_new_text()
            for directoryName, directory in self.defaultDirectories:
                self.comboDefaults.append_text(directoryName)
            self.comboDefaults.set_tooltip_text(_('Default locations'))
            self.comboDefaults.connect('changed', self.on_combo_defaults_changed)
            self.labelDefaults = gtk.Label()
            self.labelDefaults.set_text_with_mnemonic(_('De_faults:'))
        self.labelDefaults.set_mnemonic_widget(self.comboDefaults)
                        
        self.init_layout()
                        
    def get_directory(self):
        """returns the directoy
        @return: (str)
        """
        return self.directorySelector.get_directory()
    
    def get_directory_name(self):
        """returns the directoyName
        @return: (str)
        """
        return self.editName.get_text()
        
    def init_layout(self):
        """initializes the layout for the dialog"""
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
    
    def on_combo_defaults_changed(self, combo):
        """signal handler for the 'default directories' combobox"""
        directoryName, directory = self.defaultDirectories[combo.get_active()]
        self.editName.set_text(directoryName)
        self.directorySelector.set_directory(directory)
        
#************************************************************************************
#
#************************************************************************************
class BoxAutoImport(gtk.VBox):
    """(gtk.VBox) main user interface for auto import
    
    @signal start-import: triggerd when import should started
    @signal start-import: triggerd when import should be stoped
    @signal directories-changed: triggerd when the contents of the directory list have changed
    @signal auto-start-import-changed: triggerd when the 'auto start import' setting has changed
    @signal import-timeout-changed: triggerd when the 'import timeout' setting has changed
    @signal max_log_lines-changed: triggerd when the 'max log lines' setting has changed
    @signal splitter-position-changed: triggerd when the splitter postition has changed
    """
    __gsignals__ = {
        'start-import': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'stop-import': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'directories-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'auto-start-import-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'import-timeout-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'max-log-lines-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'splitter-position-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }
        
    MAX_LOG_LINES_DEFAULT = 1000
    MAX_LOG_LINES_MIN = 1
    MAX_LOG_LINES_MAX = 100000
    MAX_LOG_LINES_STEP = 1
    MAX_LOG_LINES_PAGE = 100
        
    IMPORT_TIMEOUT_DEFAULT = 1.0
    IMPORT_TIMEOUT_MIN = 0.1
    IMPORT_TIMEOUT_MAX = 100.0
    IMPORT_TIMEOUT_STEP = 0.1
    IMPORT_TIMEOUT_PAGE = 1.0
    
    def __init__(self):
        """constructor
        """
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
        
        self.spinImportTimeout = gtk.SpinButton(
                gtk.Adjustment(
                        value=self.IMPORT_TIMEOUT_DEFAULT, 
                        lower=self.IMPORT_TIMEOUT_MIN, 
                        upper=self.IMPORT_TIMEOUT_MAX, 
                        step_incr=self.IMPORT_TIMEOUT_STEP, 
                        page_incr=self.IMPORT_TIMEOUT_PAGE
                        ),
                climb_rate=0.1, 
                digits=1
                )
        self.spinImportTimeout.connect('value-changed', self.on_spin_import_timeout_value_changed)
        self.labelImportTimeout = gtk.Label()
        self.labelImportTimeout.set_mnemonic_widget(self.spinImportTimeout)
            
        self.spinMaxLogLines = gtk.SpinButton(
                gtk.Adjustment(
                        value=self.MAX_LOG_LINES_DEFAULT, 
                        lower=self.MAX_LOG_LINES_MIN, 
                        upper=self.MAX_LOG_LINES_MAX, 
                        step_incr=self.MAX_LOG_LINES_STEP,
                        page_incr=self.MAX_LOG_LINES_PAGE
                        ),
                climb_rate=1, 
                digits=0
                )
        self.spinMaxLogLines.connect('value-changed', self.on_spin_max_log_lines_value_changed)
        self.labelMaxLogLines = gtk.Label()
        self.labelMaxLogLines.set_mnemonic_widget(self.spinMaxLogLines)
        
        self.logView = WidgetLogView(maxLines=self.MAX_LOG_LINES_DEFAULT, modeAppend=False)
        
        self.buttonImport = gtk.ToggleButton()
        self.buttonImport.connect("clicked", self.on_button_import_clicked)
                
        self._adjust_widgets()
            
    def _adjust_widgets(self):
        """private mode to adjust widgets to edit mode / import mode"""
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
            
    def _set_edit_mode(self, flag):
        """private method to toggle edit mode / import mode
        @param flag: (bool)
        """
        self.directoryList.set_sensitive(flag)
        self._adjust_widgets()
    
    def get_auto_start_import(self):
        """cheks if 'auto start import setting is set
        @return: (bool)
        '"""
        return self.checkAutoImport.get_active()
    
    def get_directories(self):
        """retrieve diretories contained in the list        
        @return: (list) of (directoryName, directory) tuples
        @note: directories in the list are not guaranteed to exist and there may be
        multiple enties for the same directory. use L{set_directory_status} to give
        feedback to the user on problematic entries.
        """
        directories = []
        for i in range(self.directoryModel.get_row_count()):
            directories.append((
                    self.directoryModel.get_value(i, 'directoryName'),
                    self.directoryModel.get_value(i, 'directory')
                    ))
        return directories
                    
    def get_import_timeout(self):
        """returns current value of the 'import timeout' setting
        @return: (float)
        """
        return self.spinImportTimeout.get_value()
    
    def get_max_log_lines(self):
        """returns value of the 'max log lines' setting
        @param value: (int)
        """
        return self.spinMaxLogLines.get_value_as_int()
    
    def get_splitter_pos(self):
        """returns the current position of the slitter
        @return: (init) position
        """
        return self.splitter.get_position()
    
    def init_layout(self):
        """initializes the layout of the user interface
        @note: make shure to call this method after intitializing the user inteface
        """
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
            
        box1.pack_start(self.buttonImport, expand=False)
        
        box2 = gtk.HBox()
        box1.pack_start(box2, expand=False)
                
        box3 = gtk.VBox()
        box2.pack_start(box3)
        box3.pack_start(self.checkAutoStartImport)
        box3.pack_start(gtk.VBox())
        
        box2.pack_start(gtk.VSeparator())
                
        #TODO: layout is a bit messa here with labels + spinboxes
        box3 = gtk.VBox()
        box2.pack_start(box3)
        box4 = gtk.HBox()
        box3.pack_start(box4)
        box4.pack_start(self.labelImportTimeout, expand=False)
        box4.pack_start(self.spinImportTimeout)
                    
        box4 = gtk.HBox()
        box3.pack_start(box4)
        box4.pack_start(self.labelMaxLogLines, expand=False)
        box4.pack_start(self.spinMaxLogLines)
        
        self.show_all()
    
    def log_message(self, msg):
        """adds a message to the log message widget
        @param msg: (str) message to add
        @note: no newline is appended to the message. you have to take care of this yourself
        """
        self.logView.log_message(msg)
    
    def retranslate(self):
        """retranslates the user interface
        @note: make shure to call this method when initializing the user interface and
        on language changes.
        """
        self.directoryModel.retranslate()
        self.buttonNew.set_label(_('_New'))
        self.buttonNew.set_tooltip_text(_('Add a new directory to the list'))
        self.buttonEdit.set_label(_('_Edit'))
        self.buttonEdit.set_tooltip_text(_('Edit directory'))
        self.buttonUp.set_label(_('_Up'))
        self.buttonUp.set_tooltip_text(_('Move directory up'))
        self.buttonDown.set_label(_('_Down'))
        self.buttonDown.set_tooltip_text(_('Move directory down'))
        self.buttonRemove.set_label(_('_Remove'))
        self.buttonRemove.set_tooltip_text(_('Remove directory from the list'))
        #NOTE: mnemonics are not recognized for this checkbox. no idea why
        self.checkAutoStartImport.set_label('')
        self.checkAutoStartImport.child.set_text_with_mnemonic(_('Auto_start import'))
        self.checkAutoStartImport.set_tooltip_text(_('Automatically start import'))
        self.labelImportTimeout.set_text_with_mnemonic(_('Import _timeout:'))
        self.spinImportTimeout.set_tooltip_text(_('Timeout in between import attempts (in seconds)'))
        self.labelMaxLogLines.set_text_with_mnemonic(_('Max log lines:'))
        self.spinMaxLogLines.set_tooltip_text(_('Maximum number of lines in the log'))
        #NOTE: mnemonics are not recognized for this button. no idea why
        if self.buttonImport.get_active():
            self.buttonImport.set_label('')
            self.buttonImport.child.set_text_with_mnemonic(_('Stop _import'))
        else:
            self.buttonImport.set_label('')
            self.buttonImport.child.set_text_with_mnemonic(_('Start _import'))
        self.buttonImport.set_tooltip_text(_('Start/stop import'))
        
    def set_auto_start_import(self, flag):
        """sets the 'auto start import' setting
        @param flag: (bool) turns it on if True, off othewise
        @note: if flag is True, if import is not already running it is started in the call
        """
        self.checkAutoStartImport.set_active(flag)
        if flag and not self.buttonImport.get_active():
            self.buttonImport.set_active(True)
    
    def set_default_directories(self, directories):
        """sets default directories for the user to pick from
        @param directories: (list) of (directoryName, directory) tuples
        """
        self.defaultDirectories = directories
    
    def set_directories(self, directories):
        """sets a list of directories to the directoy list
        @param directories: (list) of (directoryName, directory) tuples
        """
        self.directoryModel.clear()
        for directoryName, directory in directories:
            self.directoryModel.append_row(directoryName=directoryName, directory=directory)
            
    def set_directory_status(self, i, status):
        """sets status associated to a directoy
        @param i: (int) index of the diretory to associate a status to
        @param status: (str) any string to reflect its status
        @return: always None
        @note: status is used to give feedback to to the user only. it has no meaning
        in the processing logic.
        """
        self.directoryModel.set_value(i, 'directoryStatus', status)
    
    def set_import_timeout(self, value):
        """sets value of the 'import timeout' setting
        @param value: (float)
        """
        self.spinImportTimeout.set_value(value)
        
    def set_max_log_lines(self, value):
        """sets value of the 'max log lines' setting
        @param value: (float)
        """
        self.spinMaxLogLines.set_value(value)
        
    def set_splitter_pos(self, pos):
        """adjusts the position of the splitter
        @param pos: (int)
        """
        self.splitter.set_position(pos)
        
    def on_button_down_clicked(self, button):
        """signal handler for the 'move directory down' button
        """
        selection = self.directoryList.get_selection()
        model, selected = selection.get_selected()
        hasSelection = selected is not None
        if hasSelection:
            path = model.get_path(selected)
            iRow = path[0]
            iRowNext = iRow +1
            self.directoryModel.swap(model.get_iter(iRow), model.get_iter(iRowNext))
            self._adjust_widgets()
            self.emit('directories-changed')
        
    def on_button_edit_clicked(self, button):
        """signal handler for the 'edit directory' button
        """
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
    
    def on_button_import_clicked(self, button):
        """signal handler for the 'import' button
        """
        if button.get_active():
            #NOTE: mnemonics are not recognized for this button. no idea why
            ##button.set_label(_('Stop _import'))
            self.buttonImport.set_label('')
            self.buttonImport.child.set_text_with_mnemonic(_('Stop _import')) 
            self._set_edit_mode(False)
            self.emit('start-import')
        else:
            #NOTE: mnemonics are not recognized for this button. no idea why
            ##button.set_label(_('Start import'))
            self.buttonImport.child.set_text_with_mnemonic(_('Start _import')) 
            self._set_edit_mode(True)
            self.emit('stop-import')
            
    def on_button_new_clicked(self, button):
        """signal handler for the 'new directory' button
        """
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
            self._adjust_widgets()
            self.emit('directories-changed')
    
    def on_button_remove_clicked(self, button):
        """signal handler for the 'remove directory' button
        """
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
            self._adjust_widgets()
            self.emit('directories-changed')
            
    def on_button_up_clicked(self, button):
        """signal handler for the 'move directory up' button
        """
        selection = self.directoryList.get_selection()
        model, selected = selection.get_selected()
        hasSelection = selected is not None
        if hasSelection:
            path = model.get_path(selected)
            iRow = path[0]
            iRowNext = iRow -1
            self.directoryModel.swap(model.get_iter(iRow), model.get_iter(iRowNext))
            self._adjust_widgets()
            self.emit('directories-changed')
            
    def on_check_auto_start_import_toggled(self, checkBox):
        """signal handler for the 'auto start import' checkbox
        """
        self.emit('auto-start-import-changed')
        
    def on_diretory_list_cursor_changed(self, directoryList):
        """signal handler for the directory list
        """
        self._adjust_widgets()
        
    def on_directory_list_row_activated(self, *args):
        """signal handler for the directory list
        """
        self.on_button_edit_clicked(self.buttonEdit)
        
    def on_spin_import_timeout_value_changed(self, spinBox):
        """signal handler for the 'import timeout' spinbox
        """
        self.emit('import-timeout-changed')
        
    def on_spin_max_log_lines_value_changed(self, spinBox):
        """signal handler for the 'max log lines' spinbox
        """
        self.logView.set_max_lines(spinBox.get_value_as_int())
        self.emit('max-log-lines-changed')
    
    def on_splitter_size_allocate(self, splitter, allocation):
        """signal handler for the splitter
        """
        self.emit('splitter-position-changed')
        
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':    
    
    # usage
    
    class MyHandler(object):
        def __init__(self, boxAutoImport):
            self.boxAutoImport = boxAutoImport
            self.boxAutoImport.connect('start-import', self.on_start_import)
            self.boxAutoImport.connect('stop-import', self.on_stop_import)
            self.boxAutoImport.connect('splitter-position-changed', self.on_splitter_position_changed)
            
        def on_start_import(self, boxAutoImport):
            boxAutoImport.log_message('start import\n')
        
        def on_stop_import(self, boxAutoImport):
            boxAutoImport.log_message('stop import\n')
            
        def on_splitter_position_changed(self, boxAutoImport):
            pos = boxAutoImport.get_splitter_pos()
            #TODO: save to config for later restore
            
            
    # create box. for this code sample we create a handler to captures some signals from the box
    boxAutoImport = BoxAutoImport()
    handler = MyHandler(boxAutoImport)
    
    # setup user interface of the box
    boxAutoImport.init_layout()
    boxAutoImport.retranslate()
        
    # init some settings of the box
    boxAutoImport.set_default_directories((('foo', '/foo'), ('bar', '/bar')))
    boxAutoImport.set_directories((('first', '/foo'), ('secund', '/bar')))
    ##boxAutoImport.set_auto_start_import(True)
    
    # do whatevs with directories and give feedback to the box
    directories = boxAutoImport.get_directories()
    boxAutoImport.set_directory_status(1, '*not found*')
    boxAutoImport.log_message('Hi there!\n')
    
    #
    m = gtk.Window()
    m.connect('destroy', gtk.main_quit)
    m.add(boxAutoImport)
    m.show()
    gtk.main()


