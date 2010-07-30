
import TableCrabConfig
from PyQt4 import QtCore, QtGui

import TableCrabGuiHelp

#**********************************************************************************************
#
#**********************************************************************************************
	
class HotkeyComboBox(QtGui.QComboBox):
	#NOTE: we can not enter certain hotkeys into the box - mouse wheel and keys triggering widget actions
	Hotkeys = (		# hotkey --> displayName
				('', '<Enter Hotkey>'),
				('<DOWN>', 'DOWN'),
				('<ENTER>', 'ENTER'),
				('<ESCAPE>', 'ESCAPE'),
				('<UP>', 'UP'),
				(TableCrabConfig.MouseWheelUp, 'MouseWheelUp'),
				(TableCrabConfig.MouseWheelDown, 'MouseWheelDown'),
			)
	def __init__(self, hotkey, parent=None):
		QtGui.QComboBox.__init__(self, parent=None)
		self.addItems( [i[1] for i in self.Hotkeys] )
		##for i in self.Hotkeys: print i
		for i, (tmpHotkey, _) in enumerate(self.Hotkeys):
			if hotkey == tmpHotkey:
				self.setCurrentIndex(i)
				break
		else:
			self.setItemText(0, hotkey)
		TableCrabConfig.signalConnect(TableCrabConfig.keyboardHook, self, 'keyPressed(QString)', self.onKeyboardHookKeyPressed)
	def popup(self, *args):
		print 11111111111111111
	
	def onKeyboardHookKeyPressed(self, hotkey):
		if self.hasFocus():
			if hotkey not in Hotkeys:
				if self.currentIndex() == 0:
					self.setItemText(0, hotkey)
	def hotkey(self):
		text = self.currentText()
		for hotkey, displayName in self.Hotkeys:
			if text == displayName:
				return hotkey
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
		self.comboHotkey = HotkeyComboBox(self.persistentItem.hotkey, parent=self)
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
		grid.addWidget(self.comboHotkey, 1, 1)
		
		grid.addWidget(self.labelHotkeyName, 2, 0)
		grid.addWidget(self.editHotkeyName, 2, 1)
			
		grid.setRowStretch(97, 99)
		grid.addWidget(TableCrabConfig.HLine(self),98, 0, 1, 3)
		grid.addWidget(self.buttonBox, 99, 0, 1, 3)	
	
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.persistentItem.itemName(), parent=self)
	
	def accept(self):
		TableCrabConfig.actionItemManager.setItemAttrs(self.persistentItem, {
				'name': self.editName.text(),
				'hotkey': self.comboHotkey.hotkey(),
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
		self.comboHotkey = HotkeyComboBox(self.persistentItem.hotkey, parent=self)
		
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
		grid.addWidget(self.comboHotkey, 1, 1)
		
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
		TableCrabConfig.actionItemManager.setItemAttrs(self.persistentItem, {
				'name': self.editName.text(),
				'hotkey': self.comboHotkey.currentText(),
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
		if persistentItem.hotkeyName:
			self.setText(0, self.persistentItem.hotkeyName)
		else:
			self.setText(0, self.persistentItem.hotkey)
		self.setText(1, self.persistentItem.name)
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
				self.setText(0, self.persistentItem.hotkey)
		elif attrName == 'hotkeyName':
			if self.persistentItem.hotkeyName:
				self.setText(0, self.persistentItem.hotkeyName)
			else:
				self.setText(0, self.persistentItem.hotkey)
		elif attrName == 'name':
			self.setText(1, self.persistentItem.name)
		

class ActionItemTreeWidget(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		TableCrabConfig.signalConnect(self, self, 'itemDoubleClicked(QTreeWidgetItem*, int)', self.editItem)
		TableCrabConfig.signalConnect(TableCrabConfig.actionItemManager, self, 'itemRead(QObject*)', self.onPersistentItemManagerItemRead)
		
		self.setColumnCount(2)
		self.setRootIsDecorated(False)
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
			TableCrabConfig.actionItemManager.dump()
		
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
			TableCrabConfig.actionItemManager.addItem(persistentItem)
	
class FrameHotkeys(QtGui.QFrame):
	
	class ActionNewHotkey(QtGui.QAction):
		def __init__(self, actionItemProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.actionItemProto = actionItemProto
			self.setText(self.actionItemProto.itemName())
			
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
				
		self.actionItemTreeWidget = ActionItemTreeWidget(self)
			
		self.buttonNew = QtGui.QPushButton('New', self)
		self.buttonEdit = QtGui.QPushButton('Edit', self)
		self.buttonUp = QtGui.QPushButton('Up', self)
		self.buttonDown = QtGui.QPushButton('Down', self)
		self.buttonRemove = QtGui.QPushButton('Remove', self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.menuNewAction = QtGui.QMenu(self)
		
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonNew, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonEdit, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonUp, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonDown, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonRemove, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)	
			
		#
		for actionItemProto, _ in Editors:
			action = self.ActionNewHotkey(actionItemProto, parent=self)
			TableCrabConfig.signalConnect(action, self, 'triggered(bool)', self.onActionNewTriggered)
			self.menuNewAction.addAction(action)
		self.buttonNew.setMenu(self.menuNewAction)
			
		# init buttons
		TableCrabConfig.signalConnect(self.actionItemTreeWidget, self, 'itemSelectionChanged()', self.onTreeItemSelectionChanged)
		TableCrabConfig.signalConnect(self.buttonUp, self, 'clicked(bool)', self.onButtonUpClicked)
		self.buttonUp.setEnabled(False)
		TableCrabConfig.signalConnect(self.buttonDown, self, 'clicked(bool)', self.onButtonDownClicked)
		self.buttonDown.setEnabled(False)
		self.buttonNew.setEnabled(TableCrabConfig.actionItemManager.canAddItem() )
		TableCrabConfig.signalConnect(self.buttonRemove, self, 'clicked(bool)', self.onButtonRemoveClicked)
		self.buttonRemove.setEnabled(False)
		TableCrabConfig.signalConnect(self.buttonEdit, self, 'clicked(bool)', self.onButtonEditClicked)
		self.buttonEdit.setEnabled(False)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)

		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.actionItemTreeWidget, 0, 0)
		grid.addWidget(self.buttonBox, 1, 0)
		
		
	def onButtonUpClicked(self, checked):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.buttonUp.setEnabled(False)
			return
		TableCrabConfig.actionItemManager.moveItemUp(item.persistentItem)
	
	def onButtonDownClicked(self, checked):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.buttonDown.setEnabled(False)
			return
		TableCrabConfig.actionItemManager.moveItemDown(item.persistentItem)
	
	def onButtonRemoveClicked(self, checked):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.buttonRemove.setEnabled(False)
			return
		TableCrabConfig.actionItemManager.removeItem(item.persistentItem)
		
	def onButtonEditClicked(self, checked):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.buttonEdit.setEnabled(False)
			return
		self.actionItemTreeWidget.editItem(item)
		
	def onTreeItemSelectionChanged(self):
		self._adjustButtons()
	
	def _adjustButtons(self):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			persistentItem = None
		elif item.parent() is None:
			persistentItem = item.persistentItem
		else:
			persistentItem = item.parent().persistentItem
		if persistentItem is None:
			self.buttonUp.setEnabled(False)
			self.buttonDown.setEnabled(False)
			self.buttonRemove.setEnabled(False)
			self.buttonEdit.setEnabled(False)
		else:
			self.buttonUp.setEnabled(TableCrabConfig.actionItemManager.canMoveItemUp(persistentItem) )
			self.buttonDown.setEnabled(TableCrabConfig.actionItemManager.canMoveItemDown(persistentItem) )
			self.buttonRemove.setEnabled(True)
			self.buttonEdit.setEnabled(True)
			
	def onActionNewTriggered(self, checked):
		self.actionItemTreeWidget.createPersistentItem(self.sender().actionItemProto)
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkeys', parent=self)
		
#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	g = TableCrabConfig.MainWindow()
	g.setCentralWidget(FrameHotkeys(g))
	g.start()
	
	
