
import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
	
#TODO: we have to ignore <TAB> cos it tabs away from the hotkey box
class HotkeyWidget(QtGui.QComboBox):
	#NOTE: bit of a hack this combo
	# x) pretty much disbled all standart keybindings for the combo. except ESCAPE and SPACE (ESCAPE
	#     mut be handled internally cos it is working without our help)
	# x) we added a space to each displayName to trrick the combo popup search feature
	Hotkeys = (		# hotkey --> displayName
				('', '<Enter Hotkey>'),
				('<ESCAPE>', ' ESCAPE'),
				('<SPACE>', ' SPACE'),
				('<TAB>', ' TAB'),
				(TableCrabWin32.MouseWheelUp, ' MouseWheelUp'),
				(TableCrabWin32.MouseWheelDown, ' MouseWheelDown'),
			)
	def __init__(self, hotkey=None, parent=None):
		QtGui.QComboBox.__init__(self, parent=None)
		self.addItems( [i[1] for i in self.Hotkeys] )
		for i, (tmpHotkey, _) in enumerate(self.Hotkeys):
			if hotkey == tmpHotkey:
				self.setCurrentIndex(i)
				break
		else:
			if hotkey is not None:
				self.setItemText(0, hotkey)
		TableCrabConfig.signalConnect(TableCrabConfig.keyboardHook, self, 'keyPressed(QString)', self.onKeyboardHookKeyPressed)
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Space and not event.modifiers():
			QtGui.QComboBox.keyPressEvent(self, event)
	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Space and not event.modifiers():
			QtGui.QComboBox.keyPressEvent(self, event)
	def onKeyboardHookKeyPressed(self, key):
		if not key: return
		if self.hasFocus():
			if self.currentIndex() == 0:
				for (myKey, _) in self.Hotkeys:
					if key == myKey:
						break
				else:
					self.setItemText(0, key)
	def hotkey(self):
		text = self.currentText()
		for key, displayName in self.Hotkeys:
			if text == displayName:
				return key
		return text

class ActionCheckEditor(QtGui.QDialog):
	def __init__(self, persistentItem, parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.persistentItem = persistentItem
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'rejected()', self.reject)
				
		self.labelName = QtGui.QLabel('Action:', self)
		self.editName = QtGui.QLineEdit(self)
		self.editName.setText(persistentItem.name)
		self.editName.setEnabled(False)
		
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.hotkeyWidget = HotkeyWidget(hotkey=self.persistentItem.hotkey, parent=self)
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setText(persistentItem.hotkeyName)
			
		self.editName.setText( self.suggestName())
		self.layout()
		
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		
		grid.addWidget(self.labelName, 0, 0)
		grid.addWidget(self.editName, 0, 1)
			
		grid.addWidget(self.labelHotkey, 1, 0)
		grid.addWidget(self.hotkeyWidget, 1, 1)
		
		grid.addWidget(self.labelHotkeyName, 2, 0)
		grid.addWidget(self.editHotkeyName, 2, 1)
			
		grid.setRowStretch(97, 99)
		grid.addWidget(TableCrabConfig.HLine(self),98, 0, 1, 3)
		grid.addWidget(self.buttonBox, 99, 0, 1, 3)	
	
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.persistentItem.itemName(), parent=self)
	
	def accept(self):
		TableCrabConfig.actionManager.setItemAttrs(self.persistentItem, {
				'name': self.editName.text(),
				'hotkey': self.hotkeyWidget.hotkey(),
				'hotkeyName': self.editHotkeyName.text(),
				})
		QtGui.QDialog.accept(self)
	def suggestName(self):
		return self.persistentItem.itemName() 
	
class ActionAlterBetAmountEditor(QtGui.QDialog):
	def __init__(self, persistentItem, parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.persistentItem = persistentItem
		
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'rejected()', self.reject)
		
		self.labelName = QtGui.QLabel('Action:', self)
		self.editName = QtGui.QLineEdit(self)
		self.editName.setText(persistentItem.name)
		self.editName.setEnabled(False)
		
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.hotkeyWidget = HotkeyWidget(hotkey=self.persistentItem.hotkey, parent=self)
		
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setText(persistentItem.hotkeyName)
	
		self.labelBaseValue = QtGui.QLabel('BaseValue:', self)
		self.comboBaseValue = TableCrabConfig.ComboBox(choices=self.persistentItem.BaseValues, default=self.persistentItem.baseValue, parent=self)
		TableCrabConfig.signalConnect(self.comboBaseValue, self, 'currentIndexChanged(int)', self.onSuggestDisplayName)
		
		self.labelMultiplier = QtGui.QLabel('Multiplier:', self)
		self.spinMultiplier = TableCrabConfig.DoubleSpinBox(minimum=-9999.99, maximum=9999.99, default=self.persistentItem.multiplier, step=0.1, precision=1, parent=self)
		TableCrabConfig.signalConnect(self.spinMultiplier, self, 'valueChanged(double)', self.onSuggestDisplayName)
		self.onSuggestDisplayName()
		self.layout()
		
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		
		grid.addWidget(self.labelName, 0, 0)
		grid.addWidget(self.editName, 0, 1)
			
		grid.addWidget(self.labelHotkey, 1, 0)
		grid.addWidget(self.hotkeyWidget, 1, 1)
		
		grid.addWidget(self.labelHotkeyName, 2, 0)
		grid.addWidget(self.editHotkeyName, 2, 1)
			
		grid.addWidget(self.labelBaseValue, 3, 0)
		grid.addWidget(self.comboBaseValue, 3, 1)
		
		grid.addWidget(self.labelMultiplier, 4, 0)
		grid.addWidget(self.spinMultiplier, 4, 1)
		
		grid.setRowStretch(97, 99)
		grid.addWidget(TableCrabConfig.HLine(self),98, 0, 1, 3)
		grid.addWidget(self.buttonBox, 99, 0, 1, 3)	
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.persistentItem.itemName(), parent=self)
	
	def accept(self):
		TableCrabConfig.actionManager.setItemAttrs(self.persistentItem, {
				'name': self.editName.text(),
				'hotkey': self.hotkeyWidget.hotkey(),
				'hotkeyName': self.editHotkeyName.text(),
				'baseValue': self.comboBaseValue.currentText(),
				'multiplier': self.spinMultiplier.value(),
				})
		QtGui.QDialog.accept(self)
		
	def onSuggestDisplayName(self, *args):
		baseValue = self.comboBaseValue.currentText()
		multiplier = self.spinMultiplier.value()
		#TODO: this is not always true for 0. we'd have to use decimal i guess 
		multiplierIsInt = int(multiplier) == multiplier
				
		if baseValue == 'BigBlind':
			if multiplier == 1:
				text = 'Add 1 Big Blind To Bet Amount'
			elif multiplier == -1:
				text =  'Subtract 1 Big Blind from Bet Amount'
			elif multiplier >= 0 and multiplierIsInt:
				text = 'Add %d Big Blinds To Bet Amount' % multiplier
			elif multiplier >= 0 and not multiplierIsInt:
				text = 'Add %.1f Big Blinds To Bet Amount' % multiplier
			elif multiplier < 0 and multiplierIsInt:
				text = 'Subtract %d Big Blinds From Bet Amount' % abs(multiplier)
			else:
				text = 'Subtract %.1f Big Blinds From Bet Amount' % abs(multiplier)
		
		elif baseValue == 'SmallBlind':
			if multiplier == 1:
				text = 'Add 1 Small Blind To Bet Amount'
			elif multiplier == -1:
				text =  'Subtract 1 Small Blind from Bet Amount'
			elif multiplier >= 0 and multiplierIsInt:
				text = 'Add %d Small Blinds To Bet Amount' % multiplier
			elif multiplier >= 0 and not multiplierIsInt:
				text = 'Add %.1f Small Blinds To Bet Amount' % multiplier
			elif multiplier < 0 and multiplierIsInt:
				text = 'Subtract %d Small Blinds From Bet Amount' % abs(multiplier)
			else:
				text = 'Subtract %.1f Small Blinds From Bet Amount' % abs(multiplier)
			
		elif baseValue == 'CurrentBet':
			if multiplier >= 0 and multiplierIsInt:
				text = 'Multiply Bet Amount By %d' % multiplier
			elif multiplier >= 0 and not multiplierIsInt:	
				text = 'Multiply Bet Amount By %.1f' % multiplier
			elif multiplier < 0 and multiplierIsInt:
				text = 'Divide Bet Amount By %d' % abs(multiplier)
			else:
				text = 'Divide Bet Amount By %.1f' % abs(multiplier)
		else:
			raise ValueError('can not handle persistentItem.basevalue: %s' % baseValue) 	
		
		self.editName.setText(text)

#NOTE: we want tp present the user logical order not sort order, so keep it as a tuple
Editors = (
		(TableCrabConfig.ActionCheck, ActionCheckEditor),
		(TableCrabConfig.ActionFold, ActionCheckEditor),
		(TableCrabConfig.ActionRaise, ActionCheckEditor),
		(TableCrabConfig.ActionAllIn, ActionCheckEditor),
		(TableCrabConfig.ActionAlterBetAmount, ActionAlterBetAmountEditor),
		(TableCrabConfig.ActionHilightBetAmount, ActionCheckEditor),
		(TableCrabConfig.ActionReplayer, ActionCheckEditor),
		(TableCrabConfig.ActionInstantHandHistory, ActionCheckEditor),
		(TableCrabConfig.ActionScreenshot, ActionCheckEditor),
		)
EditorMapping = dict(Editors)

class ActionItemTreeWidgetItem(QtGui.QTreeWidgetItem):
	def __init__(self, persistentItem, parent=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.persistentItem = persistentItem
		self.setText(0, self.persistentItem.name)
		if persistentItem.hotkeyName:
			self.setText(1, self.persistentItem.hotkeyName)
		else:
			self.setText(1, self.persistentItem.hotkey)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemAttrChanged(QObject*, QString)', self.onPersistentItemAttrChanged)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemMovedUp(QObject*, int)', self.onPersistentItemMovedUp)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemMovedDown(QObject*, int)', self.onPersistentItemMovedDown)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemRemoved(QObject*)', self.onPersistentItemRemoved)
	def onPersistentItemMovedUp(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
	def onPersistentItemMovedDown(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
	def onPersistentItemRemoved(self, action):
		treeWidget = self.treeWidget()
		self.persistentItem = None
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
	def onPersistentItemAttrChanged(self, persistentItem, attrName):
		if attrName == 'hotkey':
			if not self.persistentItem.hotkeyName:
				self.setText(1, self.persistentItem.hotkey)
		elif attrName == 'hotkeyName':
			if self.persistentItem.hotkeyName:
				self.setText(1, self.persistentItem.hotkeyName)
			else:
				self.setText(1, self.persistentItem.hotkey)
		elif attrName == 'name':
			self.setText(0, self.persistentItem.name)
		

class ActionItemTreeWidget(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		TableCrabConfig.signalConnect(self, self, 'itemDoubleClicked(QTreeWidgetItem*, int)', self.editItem)
		TableCrabConfig.signalConnect(TableCrabConfig.actionManager, self, 'itemRead(QObject*)', self.onPersistentItemManagerItemRead)
		
		self.setColumnCount(2)
		self.setRootIsDecorated(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode (0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode (1, QtGui.QHeaderView.ResizeToContents)
		self.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		TableCrabConfig.signalConnect(None, self, 'settingAlternatingRowColorsChanged(bool)', self.onSettingAlternatingRowColorsChanged)
		
		
	def keyReleaseEvent(self, event):
		#TODO: for some reason the first enter when the widget is created is not accepted
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			event.accept()
			item = self.currentItem()
			if item is not None:
				self.editItem(item)
			return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)
	def onPersistentItemManagerItemRead(self, persistentItem):
		item = ActionItemTreeWidgetItem(persistentItem, parent=self)
		self.addTopLevelItem(item)
	def onPersistentItemAdded(self, persistentItem):
		item = ActionItemTreeWidgetItem(persistentItem, parent=self)
		self.addTopLevelItem(item)
		self.setCurrentItem(item)
	
	def onSettingAlternatingRowColorsChanged(self, flag):
		self.setAlternatingRowColors(flag)
		
	def editItem(self, item):
		editor = EditorMapping[item.persistentItem.__class__]
		dlg =editor(item.persistentItem, parent=self)
		dlg.setWindowTitle('Edit Hotkey (%s)' % item.persistentItem.itemName())
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHotkeyEditor/Geometry', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/DialogHotkeyEditor/Geometry', dlg.saveGeometry() )
		if result ==dlg.Accepted:
			TableCrabConfig.actionManager.dump()
		
	def createPersistentItem(self, actionItemProto):
		persistentItem = actionItemProto()
		editor = EditorMapping[actionItemProto]
		#persistentItem.name = editor.suggestDisplayName(persistentItem)
		dlg = editor(persistentItem, parent=self)
		dlg.setWindowTitle('Create Hotkey (%s)' % persistentItem.itemName())
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHotkeyEditor/Geometry', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/DialogHotkeyEditor/Geometry', dlg.saveGeometry() )
		if result == QtGui.QDialog.Accepted:
			TableCrabConfig.signalConnect(persistentItem, self, 'itemAdded(QObject*)', self.onPersistentItemAdded)
			TableCrabConfig.actionManager.addItem(persistentItem)
	
class FrameHotkeys(QtGui.QFrame):
	
	class ActionNewHotkey(QtGui.QAction):
		def __init__(self, actionItemProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.actionItemProto = actionItemProto
			self.setText(self.actionItemProto.itemName())
			
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
			
		self.actionItemTreeWidget = ActionItemTreeWidget(self)
		TableCrabConfig.signalConnect(self.actionItemTreeWidget, self, 'itemSelectionChanged()', self.onTreeItemSelectionChanged)
			
		self.toolBar = QtGui.QToolBar(self)
		
		menu = QtGui.QMenu(self)
		for actionItemProto, _ in Editors:
			action = self.ActionNewHotkey(actionItemProto, parent=self)
			TableCrabConfig.signalConnect(action, self, 'triggered(bool)', self.onActionNewTriggered)
			menu.addAction(action)
		self.actionNew = TableCrabConfig.TableCrabAction(
				parent=self,
				text='New',
				toolTip='Create a new hotkey',
				menu=menu,
				)
		self.toolBar.addAction(self.actionNew)
		
		self.actionEdit = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Edit..',
				toolTip='Edit hotkey',
				slot=self.onActionEditTriggered,
				)
		self.toolBar.addAction(self.actionEdit)
		
		self.actionUp = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Up',
				toolTip='Move hotkey up',
				slot=self.onActionUpTriggered,
				)
		self.toolBar.addAction(self.actionUp)
		
		self.actionDown = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Down',
				toolTip='Move hotkey down',
				slot=self.onActionDownTriggered,
				)
		self.toolBar.addAction(self.actionDown)
		
		self.actionRemove = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Remove',
				toolTip='Remove hotkey',
				slot=self.onActionRemoveTriggered,
				)
		self.toolBar.addAction(self.actionRemove)
		
		self.actionHelp = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Help',
				slot=self.onActionHelpTriggered,
				)
		self.toolBar.addAction(self.actionHelp)
				
		self.adjustActions()
		self.layout()
		
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.toolBar, 0, 0)
		grid.addWidget(self.actionItemTreeWidget, 1, 0)
			
	def adjustActions(self):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			persistentItem = None
		elif item.parent() is None:
			persistentItem = item.persistentItem
		else:
			persistentItem = item.parent().persistentItem
		if persistentItem is None:
			self.actionUp.setEnabled(False)
			self.actionDown.setEnabled(False)
			self.actionRemove.setEnabled(False)
			self.actionEdit.setEnabled(False)
		else:
			self.actionUp.setEnabled(TableCrabConfig.actionManager.canMoveItemUp(persistentItem) )
			self.actionDown.setEnabled(TableCrabConfig.actionManager.canMoveItemDown(persistentItem) )
			self.actionRemove.setEnabled(True)
			self.actionEdit.setEnabled(True)
	
	def onActionUpTriggered(self):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			return
		TableCrabConfig.actionManager.moveItemUp(item.persistentItem)
	
	def onActionDownTriggered(self):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.actionDown.setEnabled(False)
			return
		TableCrabConfig.actionManager.moveItemDown(item.persistentItem)
	
	def onActionRemoveTriggered(self):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.actionRemove.setEnabled(False)
			return
		TableCrabConfig.actionManager.removeItem(item.persistentItem)
		
	def onActionEditTriggered(self):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.actionEdit.setEnabled(False)
			return
		self.actionItemTreeWidget.editItem(item)
		
	def onTreeItemSelectionChanged(self):
		self.adjustActions()
	
	def onActionNewTriggered(self, checked):
		self.actionItemTreeWidget.createPersistentItem(self.sender().actionItemProto)
		
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
	
	
