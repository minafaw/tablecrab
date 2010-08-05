
import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
	
#TODO: we have to ignore <TAB> cos it tabs away from the hotkey box
class HotkeyBox(QtGui.QComboBox):
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
		TableCrabConfig.signalConnect(TableCrabConfig.keyboardHook, self, 'inputEvent(QObject*)', self.onInputEvent)
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Space and not event.modifiers():
			QtGui.QComboBox.keyPressEvent(self, event)
	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Space and not event.modifiers():
			QtGui.QComboBox.keyPressEvent(self, event)
	def onInputEvent(self, inputEvent):
		if not inputEvent.keyIsDown: return
		if self.hasFocus():
			if self.currentIndex() == 0:
				for (myKey, _) in self.Hotkeys:
					if inputEvent.key == myKey:
						break
				else:
					self.setItemText(0, inputEvent.key)
	def hotkey(self):
		text = self.currentText()
		for key, displayName in self.Hotkeys:
			if text == displayName:
				return key
		return text

class HotkeyEditorBase(QtGui.QDialog):
	def __init__(self, hotkey, parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.hotkey = hotkey
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'rejected()', self.reject)
		self.grid = TableCrabConfig.GridBox(self)
	def layout(self):
		self.grid.setRowStretch(97, 99)
		self.grid.addWidget(TableCrabConfig.HLine(self),98, 0, 1, 3)
		self.grid.addWidget(self.buttonBox, 99, 0, 1, 3)
	
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.hotkey.itemName(), parent=self)		
		

class HotkeyCheckEditor(HotkeyEditorBase):
	def __init__(self, hotkey, parent=None):
		HotkeyEditorBase.__init__(self, hotkey, parent=parent)
		
		self.labelName = QtGui.QLabel('Action:', self)
		self.editName = QtGui.QLineEdit(self)
		self.editName.setEnabled(False)
		
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.hotkeyBox = HotkeyBox(hotkey=self.hotkey.hotkey, parent=self)
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setText(hotkey.hotkeyName)
		self.editName.setText(self.suggestName())
		self.layout()
		
	def layout(self):
		self.grid.addFields(
				(self.labelName, self.editName),
				(self.labelHotkey, self.hotkeyBox),
				(self.labelHotkeyName, self.editHotkeyName),
				)
		HotkeyEditorBase.layout(self)
		
	def accept(self):
		TableCrabConfig.hotkeyManager.setItemAttrs(self.hotkey, {
				'hotkey': self.editName.text(),
				'hotkey': self.hotkeyBox.hotkey(),
				'hotkeyName': self.editHotkeyName.text(),
				})
		QtGui.QDialog.accept(self)
	def suggestName(self):
		return self.hotkey.itemName() 
	

class HotkeyAddToBetAmountEditor(HotkeyEditorBase):
	def __init__(self, hotkey, parent=None):
		HotkeyEditorBase.__init__(self, hotkey, parent=parent)
		
		self.labelName = QtGui.QLabel('Action:', self)
		self.editName = QtGui.QLineEdit(self)
		self.editName.setEnabled(False)
		
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.hotkeyBox = HotkeyBox(hotkey=self.hotkey.hotkey, parent=self)
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setText(hotkey.hotkeyName)
		
		self.labelBasevalue = QtGui.QLabel('BaseValue:', self)
		self.comboBaseValue = TableCrabConfig.ComboBox(choices=hotkey.BaseValues, default=hotkey.baseValue, parent=self)
		TableCrabConfig.signalConnect(self.comboBaseValue, self, 'currentIndexChanged(int)', self.suggestName)
		
		self.labelMultiplier = QtGui.QLabel('multiplier:', self)
		self.spinMultiplier = TableCrabConfig.DoubleSpinBox(
				default=hotkey.multiplier, 
				minimum=hotkey.MultiplierMin, 
				maximum=hotkey.MultiplierMax, 
				step=0.1, 
				precision=1,
				parent=self,
				)
		TableCrabConfig.signalConnect(self.spinMultiplier, self, 'valueChanged(double)', self.suggestName)
		self.suggestName()
		self.layout()
	def layout(self):
		self.grid.addFields(
				(self.labelName, self.editName),
				(self.labelHotkey, self.hotkeyBox),
				(self.labelHotkeyName, self.editHotkeyName),
				(self.labelBasevalue, self.comboBaseValue),
				(self.labelMultiplier, self.spinMultiplier),
				)
		HotkeyEditorBase.layout(self)
			
	def accept(self):
		TableCrabConfig.hotkeyManager.setItemAttrs(self.hotkey, {
				'hotkey': self.editName.text(),
				'hotkey': self.hotkeyBox.hotkey(),
				'hotkeyName': self.editHotkeyName.text(),
				'basevalue': self.comboBaseValue.currentText(),
				'multiplier': self.spinMultiplier.value(),
				})
		QtGui.QDialog.accept(self)
	
	def suggestName(self, *args):
		baseValue = self.comboBaseValue.currentText()
		multiplier = round(self.spinMultiplier.value(), 1)
		if multiplier == 1:
			baseValue = 'big blind' if baseValue == 'BigBlind' else 'small blind'
			multiplier = 1
		elif int(multiplier) == multiplier:
			baseValue = 'big blinds' if baseValue == 'BigBlind' else 'small blinds'
			multiplier = int(multiplier)
		else:
			baseValue = 'big blinds' if baseValue == 'BigBlind' else 'small blinds'
		if self.hotkey.itemName() == TableCrabConfig.HotkeyAddToBetAmount.itemName():
			text = 'Add %s %s' % (multiplier, baseValue)
		else:
			text = 'Subtract %s %s' % (multiplier, baseValue)
		self.editName.setText(text)
		

class HotkeyMultiplyBetAmountEditor(HotkeyEditorBase):
	def __init__(self, hotkey, parent=None):
		HotkeyEditorBase.__init__(self, hotkey, parent=parent)
				
		self.labelName = QtGui.QLabel('Action:', self)
		self.editName = QtGui.QLineEdit(self)
		self.editName.setEnabled(False)
		
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.hotkeyBox = HotkeyBox(hotkey=self.hotkey.hotkey, parent=self)
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setText(hotkey.hotkeyName)
		
		self.labelMultiplier = QtGui.QLabel('multiplier:', self)
		self.spinMultiplier = TableCrabConfig.DoubleSpinBox(
				default=hotkey.multiplier, 
				minimum=hotkey.MultiplierMin, 
				maximum=hotkey.MultiplierMax, 
				step=0.1, 
				precision=1,
				parent=self,
				)
		TableCrabConfig.signalConnect(self.spinMultiplier, self, 'valueChanged(double)', self.suggestName)
			
		self.suggestName()
		self.layout()
		
	def layout(self):
		self.grid.addFields(
				(self.labelName, self.editName),
				(self.labelHotkey, self.hotkeyBox),
				(self.labelHotkeyName, self.editHotkeyName),
				(self.labelMultiplier, self.spinMultiplier),
				)
		HotkeyEditorBase.layout(self)
		
	def accept(self):
		TableCrabConfig.hotkeyManager.setItemAttrs(self.hotkey, {
				'hotkey': self.editName.text(),
				'hotkey': self.hotkeyBox.hotkey(),
				'hotkeyName': self.editHotkeyName.text(),
				'multiplier': self.spinMultiplier.value(),
				})
		QtGui.QDialog.accept(self)
	
	def suggestName(self):
		multiplier = round(self.spinMultiplier.value(), 1)
		if int(multiplier) == multiplier:
			text = 'Multiply Bet Amount By %s' % int(multiplier)
		else:
			text = 'Multiply Bet Amount By %s' % multiplier
		self.editName.setText(text)


#NOTE: we want tp present the user logical order not sort order, so keep it as a tuple
Editors = (
		(TableCrabConfig.HotkeyCheck, HotkeyCheckEditor),
		(TableCrabConfig.HotkeyFold, HotkeyCheckEditor),
		(TableCrabConfig.HotkeyRaise, HotkeyCheckEditor),
		(TableCrabConfig.HotkeyAllIn, HotkeyCheckEditor),
		(TableCrabConfig.HotkeyAddToBetAmount, HotkeyAddToBetAmountEditor),
		(TableCrabConfig.HotkeySubtractFromBetAmount, HotkeyAddToBetAmountEditor),
		(TableCrabConfig.HotkeyMultiplyBetAmount, HotkeyMultiplyBetAmountEditor),
		(TableCrabConfig.HotkeyHilightBetAmount, HotkeyCheckEditor),
		(TableCrabConfig.HotkeyReplayer, HotkeyCheckEditor),
		(TableCrabConfig.HotkeyInstantHandHistory, HotkeyCheckEditor),
		(TableCrabConfig.HotkeyScreenshot, HotkeyCheckEditor),
		)
EditorMapping = dict(Editors)


class HotkeyWidgetItem(QtGui.QTreeWidgetItem):
	def __init__(self, hotkey, parent=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.hotkey = hotkey
		self.updateAction()
	def updateAction(self):
		self.setText(0, self.hotkey.hotkey)
		if self.hotkey.hotkeyName:
			self.setText(1, self.hotkey.hotkeyName)
		else:
			self.setText(1, self.hotkey.hotkey)
		

class HotkeyWidget(QtGui.QTreeWidget):
	
	class ActionNewHotkey(QtGui.QAction):
		def __init__(self, hotkeyProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.hotkeyProto = hotkeyProto
			self.setText(self.hotkeyProto.itemName())
			TableCrabConfig.signalConnect(self, self, 'triggered(bool)', self.onTriggered)
		def onTriggered(self):
			self.parent().createHotkey(self.hotkeyProto)
			
	
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		
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
		for actionItemProto, _ in Editors:
			hotkey = self.ActionNewHotkey(actionItemProto, parent=self)
			menu.addAction(hotkey)
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
			
		# connect to global signals
		TableCrabConfig.signalsConnect(None, self, 
				('settingAlternatingRowColorsChanged(bool)', self.onSettingAlternatingRowColorsChanged),
				)
		
		# connect to TreeWidgret signals
		TableCrabConfig.signalsConnect(self, self, 
				('itemDoubleClicked(QTreeWidgetItem*, int)', self.onItemDoubleClicked),
				('itemSelectionChanged()', self.adjustActions),
				)
		
		# connect to HotkeyManager signals
		TableCrabConfig.signalsConnect(TableCrabConfig.hotkeyManager, self, 
				('itemAdded(QObject*)', self.onHotkeyAdded),
				('itemMovedUp(QObject*, int)', self.onHotkeyMovedUp),
				('itemMovedDown(QObject*, int)', self.onHotkeyMovedDown),
				('itemRemoved(QObject*)', self.onHotkeyRemoved),
				)
				
		self.adjustActions()
				
	def actions(self): return self._actions
		
	def adjustActions(self):
		item = self.currentItem()
		if item is None:
			hotkey = None
		elif item.parent() is None:
			hotkey = item.hotkey
		else:
			hotkey = item.parent().hotkey
		if hotkey is None:
			self.actionUp.setEnabled(False)
			self.actionDown.setEnabled(False)
			self.actionRemove.setEnabled(False)
			self.actionEdit.setEnabled(False)
		else:
			self.actionUp.setEnabled(TableCrabConfig.hotkeyManager.canMoveItemUp(hotkey) )
			self.actionDown.setEnabled(TableCrabConfig.hotkeyManager.canMoveItemDown(hotkey) )
			self.actionRemove.setEnabled(True)
			self.actionEdit.setEnabled(True)
	
	def keyReleaseEvent(self, event):
		#TODO: for some reason the first enter when the widget is created is not accepted
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			event.accept()
			item = self.currentItem()
			if item is not None:
				self.editHotkey(item.hotkey)
			return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)
	
	def onItemDoubleClicked(self, item):
		self.editHotkey(item.hotkey)
	
	def onSettingAlternatingRowColorsChanged(self, flag):
		self.setAlternatingRowColors(flag)
		
	def editHotkey(self, hotkey=None):
		if hotkey is None:
			item = self.currentItem()
			if item is None:
				self.actionEdit.setEnabled(False)
				return
			hotkey = item.hotkey
		editor = EditorMapping[hotkey.__class__]
		dlg =editor(hotkey, parent=self)
		dlg.setWindowTitle('Edit Hotkey (%s)' % hotkey.itemName())
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHotkeyEditor/Geometry', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/DialogHotkeyEditor/Geometry', dlg.saveGeometry() )
		if result ==dlg.Accepted:
			item.userData().updateAction()
		
	def createHotkey(self, hotkeyProto):
		hotkey = hotkeyProto()
		editor = EditorMapping[hotkeyProto]
		dlg = editor(hotkey, parent=self)
		dlg.setWindowTitle('Create Hotkey (%s)' % hotkey.itemName())
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHotkeyEditor/Geometry', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/DialogHotkeyEditor/Geometry', dlg.saveGeometry() )
		if result == QtGui.QDialog.Accepted:
			TableCrabConfig.hotkeyManager.addItem(hotkey)
	
	def onHotkeyAdded(self, hotkey):
		item = HotkeyWidgetItem(hotkey, parent=self)
		hotkey.setUserData(item)
		self.addTopLevelItem(item)
		if TableCrabConfig.hotkeyManager.readFinished():
			self.setCurrentItem(item)
	
	def moveHotkeyUp(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			return
		TableCrabConfig.hotkeyManager.moveItemUp(item.hotkey)
	
	def onHotkeyMovedUp(self, hotkey, index):
		item = hotkey.userData()
		self.takeTopLevelItem(self.indexOfTopLevelItem(item) )
		self.insertTopLevelItem(index, item)
		self.setCurrentItem(item)

	def moveHotkeyDown(self):
		item = self.currentItem()
		if item is None:
			self.actionDown.setEnabled(False)
			return
		TableCrabConfig.hotkeyManager.moveItemDown(item.hotkey)
	
	def onHotkeyMovedDown(self, hotkey, index):
		item = hotkey.userData()
		self.takeTopLevelItem(self.indexOfTopLevelItem(item) )
		self.insertTopLevelItem(index, item)
		self.setCurrentItem(item)

	def removeHotkey(self):
		item = self.currentItem()
		if item is None:
			self.actionRemove.setEnabled(False)
			return
		TableCrabConfig.hotkeyManager.removeItem(item.hotkey)
	
	def onHotkeyRemoved(self, hotkey):
		item = hotkey.userData()
		self.hotkey = None
		self.takeTopLevelItem(self.indexOfTopLevelItem(item) )
		item.hotkey = None
		


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
	
	
