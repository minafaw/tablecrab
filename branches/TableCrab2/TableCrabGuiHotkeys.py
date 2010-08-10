
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
			self.triggered.connect(self.onTriggered)
		def onTriggered(self):
			self.parent().createHotkey(self.hotkeyProto)
		
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		
		TableCrabConfig.hotkeyManager = self
			
		# setup treeWidget
		self.setColumnCount(2)
		self.setRootIsDecorated(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode (0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode (1, QtGui.QHeaderView.ResizeToContents)
		self.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		
		# setup actions
		self._actions = []
		
		menu = QtGui.QMenu(self)
		for hotkeyProto in TableCrabHotkeys.Hotkeys:
			menu.addAction(self.ActionNewHotkey(hotkeyProto, parent=self) )
		self.actionNew = TableCrabConfig.Action(
				parent=self,
				text='New',
				toolTip='Create a new hotkey',
				menu=menu,
				)
		self._actions.append(self.actionNew)
		self.actionEdit = TableCrabConfig.Action(
				parent=self,
				text='Edit..',
				toolTip='Edit hotkey',
				slot=self.editHotkey,
				)
		self._actions.append(self.actionEdit)
		self.actionUp = TableCrabConfig.Action(
				parent=self,
				text='Up',
				toolTip='Move hotkey up',
				slot=self.moveHotkeyUp,
				)
		self._actions.append(self.actionUp)
		self.actionDown = TableCrabConfig.Action(
				parent=self,
				text='Down',
				toolTip='Move hotkey down',
				slot=self.moveHotkeyDown,
				)
		self._actions.append(self.actionDown)
		self.actionRemove = TableCrabConfig.Action(
				parent=self,
				text='Remove',
				toolTip='Remove hotkey',
				slot=self.removeHotkey,
				)
		self._actions.append(self.actionRemove)
			
		# connect signals
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSetAlternatingRowColors),
		self.itemDoubleClicked.connect(self.onHotkeyDoubleClicked)
		self.itemSelectionChanged.connect(self.adjustActions)
		
		self.adjustActions()
		
	def __iter__(self):
		for i in xrange(self.topLevelItemCount()):
			yield self.topLevelItem(i)
		
	def onSetAlternatingRowColors(self, flag):
		self.setAlternatingRowColors(flag)
	
	def keyReleaseEvent(self, event):
		#TODO: for some reason the first enter when the widget is created is not accepted
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			event.accept()
			hotkey = self.currentItem()
			if hotkey is not None:
				self.editHotkey()
			return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)
	
	def actions(self): return self._actions
		
	def adjustActions(self):
		hotkey = self.currentItem()
		self.actionNew.setEnabled(self.topLevelItemCount() < TableCrabConfig.MaxHotkeys)
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
	
	def canMoveHotkeyDown(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(hotkey) < self.topLevelItemCount() -1
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
		hotkey = hotkey.createEditor(parent=self, settingsKey='Gui/DialogHotkeyEditor/Geometry', isEdit=False)
		if hotkey is not None:
			self.addTopLevelItem(hotkey)
			self.setCurrentItem(hotkey)
			self.dump()
	
	def dump(self):
		TableCrabConfig.dumpPersistentItems('Hotkeys', [hotkey for hotkey in self])
	
	def editHotkey(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionEdit.setEnabled(False)
			return
		hotkey = hotkey.createEditor(parent=self, settingsKey='Gui/DialogHotkeyEditor/Geometry', isEdit=True)
		if hotkey is not None:
			self.dump()
		
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
	
	def read(self):
		hotkey = None
		for hotkey in TableCrabConfig.readPersistentItems('Hotkeys', maxItems=TableCrabConfig.MaxHotkeys, itemProtos=TableCrabHotkeys.Hotkeys):
			self.addTopLevelItem(hotkey)
		# set at least one hotkey as default
		if hotkey is None:
			hotkey = TableCrabHotkeys.HotkeyScreenshot(hotkey='<F1+LeftControl>')
			self.addTopLevelItem(hotkey)
		
	def removeHotkey(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionRemove.setEnabled(False)
			return
		self.takeTopLevelItem(self.indexOfTopLevelItem(hotkey) )
		self.dump()
		
	def onHotkeyDoubleClicked(self, hotkey):
		self.editHotkey()
	

class FrameHotkeys(QtGui.QFrame):
			
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.HotkeyWidget = HotkeyWidget(self)
		self.toolBar = QtGui.QToolBar(self)
		for action in self.HotkeyWidget.actions():
			self.toolBar.addAction(action)
		self.actionHelp = TableCrabConfig.Action(
				parent=self,
				text='Help',
				slot=self.onActionHelpTriggered,
				)
		self.toolBar.addAction(self.actionHelp)
		self.layout()
		
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.toolBar, 0, 0)
		grid.addWidget(self.HotkeyWidget, 1, 0)
	
	def onActionHelpTriggered(self):
		TableCrabGuiHelp.dialogHelp('hotkeys', parent=self)
		
#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	import TableCrabMainWindow
	g = TableCrabMainWindow.MainWindow()
	g.setCentralWidget(FrameHotkeys(g))
	g.start()
	
	
