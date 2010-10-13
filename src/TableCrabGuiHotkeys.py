
#TODO: would be nice to have some information on how many hotkeys are left until hitting MaxHotkeys

import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp
import TableCrabHotkeys

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
class HotkeyWidget(QtGui.QTreeWidget):

	class ActionNewHotkey(QtGui.QAction):
		def __init__(self, hotkeyProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.hotkeyProto = hotkeyProto
			self.setText(self.hotkeyProto.menuName())
			self.setShortcut(self.hotkeyProto.shortcut() )
			self.triggered.connect(self.onTriggered)
		def onTriggered(self):
			self.parent().createHotkey(self.hotkeyProto)

	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)

		#TODO: find a better way to set hotkey manager as global
		TableCrabConfig.hotkeyManager = self

		# setup treeWidget
		self.setUniformRowHeights(True)
		self.setColumnCount(3)
		self.setRootIsDecorated(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)

		# setup actions
		self._actions = []

		menu = QtGui.QMenu(self)
		for hotkeyProto in TableCrabHotkeys.Hotkeys:
			menu.addAction(self.ActionNewHotkey(hotkeyProto, parent=self) )

		self.actionNew = QtGui.QAction(self)
		self.actionNew.setText('New')
		self.actionNew.setToolTip('Create a new hotkey')
		self.actionNew.setMenu(menu)
		self._actions.append(self.actionNew)

		self.actionEdit = QtGui.QAction(self)
		self.actionEdit.setText('Edit..')
		self.actionEdit.setToolTip('Edit hotkey (Alt+E)')
		self.actionEdit.setShortcut(QtGui.QKeySequence('Alt+E') )
		self.actionEdit.triggered.connect(self.editHotkey)
		self._actions.append(self.actionEdit)

		self.actionUp = QtGui.QAction(self)
		self.actionUp.setText('Up')
		self.actionUp.setToolTip('Move hotkey up (Alt+Up)')
		self.actionUp.setShortcut(QtGui.QKeySequence('Alt+Up') )
		self.actionUp.triggered.connect(self.moveHotkeyUp)
		self._actions.append(self.actionUp)

		self.actionDown = QtGui.QAction(self)
		self.actionDown.setText('Down')
		self.actionDown.setToolTip('Move hotkey down (Alt+Down)')
		self.actionDown.setShortcut(QtGui.QKeySequence('Alt+Down') )
		self.actionDown.triggered.connect(self.moveHotkeyDown)
		self._actions.append(self.actionDown)

		self.actionRemove = QtGui.QAction(self)
		self.actionRemove.setText('Remove')
		self.actionRemove.setToolTip('Remove hotkey (Alt+Del)')
		self.actionRemove.setShortcut(QtGui.QKeySequence('Alt+Del') )
		self.actionRemove.triggered.connect(self.removeHotkey)
		self._actions.append(self.actionRemove)

		# connect signals
		TableCrabConfig.globalObject.init.connect(self.onInit)
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(
				self.onSetAlternatingRowColors
				)
		self.itemDoubleClicked.connect(self.onHotkeyDoubleClicked)
		self.itemSelectionChanged.connect(self.adjustActions)

	#----------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#---------------------------------------------------------------------------------------------------------------
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			event.accept()
			hotkey = self.currentItem()
			if hotkey is not None:
				self.editHotkey()
			return
		return QtGui.QTreeWidget.keyPressEvent(self, event)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def __iter__(self):
		for i in xrange(len(self) ):
			yield self.topLevelItem(i)

	def __len__(self):
		return self.topLevelItemCount()

	def actions(self): return self._actions

	def adjustActions(self):
		hotkey = self.currentItem()
		self.actionNew.setEnabled(len(self) < TableCrabConfig.MaxHotkeys)
		if hotkey is None:
			self.actionUp.setEnabled(False)
			self.actionDown.setEnabled(False)
			self.actionRemove.setEnabled(False)
			self.actionEdit.setEnabled(False)
		else:
			self.actionUp.setEnabled(self.canMoveHotkeyUp() )
			self.actionDown.setEnabled(self.canMoveHotkeyDown() )
			self.actionRemove.setEnabled(True)
			self.actionEdit.setEnabled(True)

	#TODO: there is a is a bug in Qt4.6.2. last items text(1) is never updated.
	#			[http://bugreports.qt.nokia.com/browse/QTBUG-4849]
	# looks like there is no way to workaround. tried removing / reinsterting items
	# but this runs into more bugs, resulting in loosing templates on certain occasions
	#
	# test is: open screenshot, create new item. this items flag is never set to '//Edit//'
	# move item up --> flag gets shown. guess its best to leave it as is and wait for Qt
	# fixing bugs.
	def adjustHotkeys(self):
		tmp_keys = {}
		for hotkey in self:
			if hotkey.key() not in tmp_keys:
				tmp_keys[hotkey.key()] = [hotkey]
			else:
				tmp_keys[hotkey.key()].append(hotkey)

		for _, hotkeys in tmp_keys.items():
			conflicts = [i for i in hotkeys if i.key()]
			for hotkey in hotkeys:
				flag = 'Conflict' if len(conflicts) > 1 else None
				if flag is None:
					hotkey.setText(2, '')
				else:
					hotkey.setText(2, '//%s//' % flag)

		self.setUpdatesEnabled(True)

	def canMoveHotkeyDown(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(hotkey) < len(self) -1
		return False

	def canMoveHotkeyUp(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(hotkey) > 0
		return False

	def createHotkey(self, hotkeyProto):
		hotkey = hotkeyProto()
		hotkey = hotkey.createEditor(
				parent=self,
				settingsKey='Gui/DialogHotkeyEditor/Geometry',
				isEdit=False
				)
		if hotkey is not None:
			self.addTopLevelItem(hotkey)
			self.setCurrentItem(hotkey)
			self.dump()
			self.adjustHotkeys()

	def dump(self):
		TableCrabConfig.dumpPersistentItems('Hotkeys', self)

	def editHotkey(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionEdit.setEnabled(False)
			return
		hotkey = hotkey.createEditor(
				parent=self,
				settingsKey='Gui/DialogHotkeyEditor/Geometry',
				isEdit=True
				)
		if hotkey is not None:
			self.dump()
			self.adjustHotkeys()

	def moveHotkeyDown(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionDown.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(hotkey)
		self.takeTopLevelItem(index)
		self.insertTopLevelItem(index +1, hotkey)
		self.setCurrentItem(hotkey)
		self.dump()

	def moveHotkeyUp(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionUp.setEnabled(False)
		else:
			index = self.indexOfTopLevelItem(hotkey)
			self.takeTopLevelItem(index)
			self.insertTopLevelItem(index -1, hotkey)
			self.setCurrentItem(hotkey)
			self.dump()

	def removeHotkey(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionRemove.setEnabled(False)
			return
		self.takeTopLevelItem(self.indexOfTopLevelItem(hotkey) )
		self.dump()
		self.adjustHotkeys()

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onHotkeyDoubleClicked(self, hotkey):
		self.editHotkey()

	def onInit(self):
		self.setUpdatesEnabled(False)

		self.setAlternatingRowColors(
				TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool()
				)
		self.clear()
		hotkey = None
		for hotkey in TableCrabConfig.readPersistentItems(
				'Hotkeys',
				maxItems=TableCrabConfig.MaxHotkeys,
				itemProtos=TableCrabHotkeys.Hotkeys
				):
			self.addTopLevelItem(hotkey)
		# set at least one hotkey as default
		if hotkey is None:
			hotkey = TableCrabHotkeys.HotkeyScreenshot(key='<F1+LeftControl>')
			self.addTopLevelItem(hotkey)
		self.setCurrentItem( self.topLevelItem(0) )

		self.setUpdatesEnabled(True)
		self.adjustHotkeys()
		self.adjustActions()

	def onSetAlternatingRowColors(self, flag):
		self.setAlternatingRowColors(flag)


#**********************************************************************************************
#
#**********************************************************************************************
class FrameHotkeys(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.HotkeyWidget = HotkeyWidget(self)
		self.toolBar = QtGui.QToolBar(self)
		for action in self.HotkeyWidget.actions():
			self.toolBar.addAction(action)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self.toolBar.addAction(self.actionHelp)
		self.layout()

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.HotkeyWidget)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self):
		TableCrabGuiHelp.dialogHelp('hotkeys', parent=self)



