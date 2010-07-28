
import TableCrabConfig
from PyQt4 import QtCore, QtGui

import TableCrabGuiHelp

#**********************************************************************************************
#
#**********************************************************************************************

#NOTE: we have to hard code hotkeys reserved for dialog box and comboBox keyboard handling 
Hotkeys = ('', TableCrabConfig.MouseWheelUp, TableCrabConfig.MouseWheelDown, '<ENTER>',  '<ESCAPE>','<DOWN>', '<UP>')
ValueNone = 'None'
	
class HotkeyComboBox(QtGui.QComboBox):
	def __init__(self, hotkey, parent=None):
		QtGui.QComboBox.__init__(self, parent=None)
		self.addItems(Hotkeys)
		if hotkey in Hotkeys[1:]:
			self.setCurrentIndex(Hotkeys.index(hotkey))
		else:
			self.setItemText(0, hotkey)
		TableCrabConfig.signalConnect(TableCrabConfig.keyboardHook, self, 'keyPressed(QString)', self.onKeyboardHookKeyPressed)
	def onKeyboardHookKeyPressed(self, hotkey):
		#print hotkey
		if self.hasFocus():
			if hotkey not in Hotkeys:
				if self.currentIndex() == 0:
					self.setItemText(0, hotkey)
	

class ActionCheckEditor(QtGui.QDialog):
	def __init__(self, actionItem, parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.actionItem = actionItem
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'rejected()', self.reject)
		
		self.labelName = QtGui.QLabel('Action:', self)
		self.editName = QtGui.QLineEdit(self)
		self.editName.setText(actionItem.name)
		self.editName.setEnabled(False)
		
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.comboHotkey = HotkeyComboBox(self.actionItem.hotkey, parent=self)
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setText(actionItem.hotkeyName)
			
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
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.actionItem.itemName(), parent=self)
	
	def accept(self):
		self.actionItem.name = self.editName.text()
		self.actionItem.hotkey = self.comboHotkey.currentText()
		self.actionItem.hotkeyName = self.editHotkeyName.text()
		QtGui.QDialog.accept(self)
	def suggestName(self):
		return self.actionItem.itemName() 
	
class ActionAlterBetAmountEditor(QtGui.QDialog):
	def __init__(self, actionItem, parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.actionItem = actionItem
		
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'rejected()', self.reject)
		
		self.labelName = QtGui.QLabel('Action:', self)
		self.editName = QtGui.QLineEdit(self)
		self.editName.setText(actionItem.name)
		self.editName.setEnabled(False)
		
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.comboHotkey = HotkeyComboBox(self.actionItem.hotkey, parent=self)
		
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setText(actionItem.hotkeyName)
	
		self.labelBaseValue = QtGui.QLabel('BaseValue:', self)
		self.comboBaseValue = TableCrabConfig.ComboBox(choices=self.actionItem.BaseValues, default=self.actionItem.baseValue, parent=self)
		TableCrabConfig.signalConnect(self.comboBaseValue, self, 'currentIndexChanged(int)', self.onSuggestDisplayName)
		
		self.labelMultiplier = QtGui.QLabel('Multiplier:', self)
		self.spinMultiplier = TableCrabConfig.DoubleSpinBox(minimum=-9999.99, maximum=9999.99, default=self.actionItem.multiplier, step=0.1, precision=1, parent=self)
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
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.actionItem.itemName(), parent=self)
	
	def accept(self):
		self.actionItem.name = self.editName.text()
		self.actionItem.hotkey = self.comboHotkey.currentText()
		self.actionItem.hotkeyName = self.editHotkeyName.text()
		self.actionItem.baseValue = self.comboBaseValue.currentText()
		self.actionItem.multiplier = self.spinMultiplier.value()
		QtGui.QDialog.accept(self)
		
	def onSuggestDisplayName(self, *args):
		baseValue = self.comboBaseValue.currentText()
		multiplier = self.spinMultiplier.value()
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
				text = 'Multiply Bet Amount By %s' % multiplier
			elif multiplier < 0 and multiplierIsInt:
				text = 'Divide Bet Amount By %d' % abs(multiplier)
			else:
				text = 'Divide Bet Amount By %.1f' % abs(multiplier)
		else:
			raise ValueError('can not handle actionItem.basevalue: %s' % baseValue) 	
		
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
	def __init__(self, actionItem, parent=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.actionItem = actionItem
		if actionItem.hotkeyName:
			self.setText(0, self.actionItem.hotkeyName)
		else:
			self.setText(0, self.actionItem.hotkey)
		self.setText(1, self.actionItem.name)
		TableCrabConfig.signalConnect(self.actionItem, self.actionItem, 'attributeValueChanged(QString)', self.onActionAttributeValueChanged)
		TableCrabConfig.signalConnect(self.actionItem, self.actionItem, 'itemMovedUp(QObject*, int)', self.onActionMovedUp)
		TableCrabConfig.signalConnect(self.actionItem, self.actionItem, 'itemMovedDown(QObject*, int)', self.onActionMovedDown)
		TableCrabConfig.signalConnect(self.actionItem, self.actionItem, 'itemRemoved(QObject*)', self.onActionRemoved)
	def onActionMovedUp(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
	def onActionMovedDown(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
	def onActionRemoved(self, action):
		treeWidget = self.treeWidget()
		self.actionItem = None
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
	def onActionAttributeValueChanged(self, attrName):
		if attrName == 'hotkey':
			if not self.actionItem.hotkeyName:
				self.setText(0, self.actionItem.hotkey)
		elif attrName == 'hotkeyName':
			if self.actionItem.hotkeyName:
				self.setText(0, self.actionItem.hotkeyName)
			else:
				self.setText(0, self.actionItem.hotkey)
		elif attrName == 'name':
			self.setText(1, self.actionItem.name)
		

class ActionItemTreeWidget(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		TableCrabConfig.signalConnect(self, self, 'itemDoubleClicked(QTreeWidgetItem*, int)', self.editItem)
		TableCrabConfig.signalConnect(TableCrabConfig.actionItemManager, self, 'itemRead(QObject*)', self.onActiontItemManagerItemRead)
		
		self.setColumnCount(2)
		self.setRootIsDecorated(False)
		self.header().setVisible(False)
		self.header().setResizeMode (0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode (1, QtGui.QHeaderView.ResizeToContents)
		#self.setAlternatingRowColors(True)
		
	def keyReleaseEvent(self, event):
		#TODO: for some reason the first enter when the widget is created is not accepted
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			event.accept()
			item = self.currentItem()
			if item is not None:
				self.editItem(item)
			return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)
	def onActiontItemManagerItemRead(self, actionItem):
		item = ActionItemTreeWidgetItem(actionItem, parent=self)
		self.addTopLevelItem(item)
	def onActionItemAdded(self, actionItem):
		item = ActionItemTreeWidgetItem(actionItem, parent=self)
		self.addTopLevelItem(item)
		self.setCurrentItem(item)
	def editItem(self, item):
		editor = EditorMapping[item.actionItem.__class__]
		dlg =editor(item.actionItem, parent=self)
		dlg.setWindowTitle('Edit Hotkey (%s)' % item.actionItem.itemName())
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHotkeyEditor/Geometry', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/DialogHotkeyEditor/Geometry', dlg.saveGeometry() )
		if result ==dlg.Accepted:
			TableCrabConfig.actionItemManager.dump()
		
	def createActionItem(self, actionItemProto):
		actionItem = actionItemProto()
		editor = EditorMapping[actionItemProto]
		#actionItem.name = editor.suggestDisplayName(actionItem)
		dlg = editor(actionItem, parent=self)
		dlg.setWindowTitle('Create Hotkey (%s)' % actionItem.itemName())
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHotkeyEditor/Geometry', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/DialogHotkeyEditor/Geometry', dlg.saveGeometry() )
		if result == QtGui.QDialog.Accepted:
			TableCrabConfig.signalConnect(actionItem, self, 'itemAdded(QObject*)', self.onActionItemAdded)
			if not actionItem.name:
				actionItem.name = editor.suggestDisplayName(actionItem)
			TableCrabConfig.actionItemManager.addItem(actionItem)
	
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
		TableCrabConfig.actionItemManager.moveItemUp(item.actionItem)
	
	def onButtonDownClicked(self, checked):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.buttonDown.setEnabled(False)
			return
		TableCrabConfig.actionItemManager.moveItemDown(item.actionItem)
	
	def onButtonRemoveClicked(self, checked):
		item = self.actionItemTreeWidget.currentItem()
		if item is None:
			self.buttonRemove.setEnabled(False)
			return
		TableCrabConfig.actionItemManager.removeItem(item.actionItem)
		
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
			actionItem = None
		elif item.parent() is None:
			actionItem = item.actionItem
		else:
			actionItem = item.parent().actionItem
		if actionItem is None:
			self.buttonUp.setEnabled(False)
			self.buttonDown.setEnabled(False)
			self.buttonRemove.setEnabled(False)
			self.buttonEdit.setEnabled(False)
		else:
			self.buttonUp.setEnabled(TableCrabConfig.actionItemManager.canMoveItemUp(actionItem) )
			self.buttonDown.setEnabled(TableCrabConfig.actionItemManager.canMoveItemDown(actionItem) )
			self.buttonRemove.setEnabled(True)
			self.buttonEdit.setEnabled(True)
			
	def onActionNewTriggered(self, checked):
		self.actionItemTreeWidget.createActionItem(self.sender().actionItemProto)
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkeys', parent=self)
		
#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	g = TableCrabConfig.MainWindow()
	g.setCentralWidget(FrameHotkeys(g))
	g.start()
	
	
