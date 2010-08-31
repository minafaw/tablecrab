
#TODO: messy code ..clean up
#TODO: check for conflicting hotkeys? currently we trigger the first matching, that's all
#TODO: restore last selected hokey on restart? would rewuire an attr "itemIsSelected", downside
#				we'd have to dump the whole tree on every curent item change.


import TableCrabConfig
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui
#**********************************************************************************************
#
#**********************************************************************************************

Hotkeys = []


class HotkeyEditor(QtGui.QDialog):
	def __init__(self, hotkey, parent=None, settingsKey=None, isEdit=True):
		QtGui.QDialog.__init__(self,parent)
		if isEdit:
			self.setWindowTitle('Edit hotkey: %s' % hotkey.menuName() )
		else:
			self.setWindowTitle('Create hotkey: %s' % hotkey.menuName() )

		self.hotkey = hotkey
		self.settingsKey = settingsKey
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.setShortcut(QtGui.QKeySequence('F1'))
		self.buttonHelp.clicked.connect(self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.labelAction = QtGui.QLabel('Action:', self)
		self.editAction = QtGui.QLineEdit(self)
		self.editAction.setText(self.hotkey.action())
		self.editAction.setEnabled(False)

		self.labelHotkey = QtGui.QLabel('Hot&key:', self)
		self.hotkeyBox = TableCrabConfig.HotkeyBox(hotkey=self.hotkey.hotkey(), parent=self)
		self.hotkeyBox.setToolTip('Hotkey (Alt+K)')
		self.labelHotkey.setBuddy(self.hotkeyBox)

		self.labelHotkeyName = QtGui.QLabel('HotkeyN&ame:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setToolTip('Edit shortcut name (Alt+A)')
		self.labelHotkeyName.setBuddy(self.editHotkeyName)
		self.editHotkeyName.setText(self.hotkey.hotkeyName()  )

		self.grid = TableCrabConfig.GridBox(self)
		self.fields = [
				(self.labelAction, self.editAction),
				(self.labelHotkey, self.hotkeyBox),
				(self.labelHotkeyName, self.editHotkeyName),
				]

	def layout(self):
		self.grid.addFields(*self.fields)
		self.grid.setRowStretch(97, 99)
		self.grid.addWidget(TableCrabConfig.HLine(self),98, 0, 1, 3)
		self.grid.addWidget(self.buttonBox, 99, 0, 1, 3)
		tabOrder = [self.buttonBox, ]
		for _, w in self.fields:
			tabOrder.append(w)
			if len(tabOrder) == 3:
				tabOrder.pop(0)
			self.setTabOrder(*tabOrder)

	def hideEvent(self, event):
		if self.settingsKey is not None:
			TableCrabConfig.settingsSetValue(self.settingsKey, self.saveGeometry() )
		return QtGui.QDialog.hideEvent(self, event)

	def exec_(self):
		self.layout()
		if self.settingsKey is not None:
			self.restoreGeometry( TableCrabConfig.settingsValue(self.settingsKey, QtCore.QByteArray()).toByteArray() )
		return QtGui.QDialog.exec_(self)

	def accept(self):
		self.hotkey.setHotkey(self.hotkeyBox.hotkey() )
		self.hotkey.setHotkeyName(self.editHotkeyName.text() )
		QtGui.QDialog.accept(self)

	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.hotkey.id(), parent=self)


class HotkeyEditorWithMultiplier(HotkeyEditor):
	def __init__(self, *args, **kws):
		HotkeyEditor.__init__(self, *args,**kws)
		self.labelMultiplier = QtGui.QLabel('&Multiplier:', self)
		self.spinMultiplier = TableCrabConfig.DoubleSpinBox(
				default=self.hotkey.multiplier(),
				minimum=self.hotkey.MultiplierMin,
				maximum=self.hotkey.MultiplierMax,
				step=0.1,
				precision=1,
				parent=self,
				)
		self.spinMultiplier.setToolTip('Multiplier (Alt+M)')
		self.labelMultiplier.setBuddy(self.spinMultiplier)

		self.spinMultiplier.valueChanged.connect(self.setNewActionName)
		self.fields.extend((
				(self.labelMultiplier, self.spinMultiplier),
				))

	def setNewActionName(self,*args):
		self.hotkey.setMultiplier(self.spinMultiplier.value() )
		self.editAction.setText(self.hotkey.action() )

	def accept(self):
		self.hotkey.setMultiplier(self.spinMultiplier.value() )
		return HotkeyEditor.accept(self)


class HotkeyEditorWithMultiplierAndBaseValue(HotkeyEditorWithMultiplier):
	def __init__(self, *args, **kws):
		HotkeyEditorWithMultiplier.__init__(self, *args,**kws)
		self.labelBasevalue = QtGui.QLabel('&BaseValue:', self)
		self.comboBaseValue = TableCrabConfig.ComboBox(choices=self.hotkey.BaseValues, default=self.hotkey.baseValue(), parent=self)
		self.comboBaseValue.currentIndexChanged.connect(self.setNewActionName)
		self.comboBaseValue.setToolTip('Base value (Atl+B)')
		self.labelBasevalue.setBuddy(self.comboBaseValue)


		self.fields.insert(-1,
				(self.labelBasevalue, self.comboBaseValue),
				)
	def setNewActionName(self,*args):
		self.hotkey.setBaseValue(self.comboBaseValue.currentText() )
		HotkeyEditorWithMultiplier.setNewActionName(self,*args)

	def accept(self):
		self.hotkey.setBaseValue(self.comboBaseValue.currentText() )
		return HotkeyEditor.accept(self)




class HotkeyCheck(QtGui.QTreeWidgetItem):
	def __init__(self, parent=None, hotkey='', hotkeyName=''):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self._hotkey = hotkey
		self._hotkeyName = hotkeyName
		self.update(self)
	def update(self, other):
		self._hotkey = other.hotkey()
		self._hotkeyName = other.hotkeyName()
		self.setText(0, self.action() )
		self.setText(1, self._hotkeyName if self._hotkeyName else self._hotkey)
	@classmethod
	def id(klass): return 'Check'
	@classmethod
	def menuName(klass): return 'Check'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+C')
	def action(self): return self.menuName()
	def hotkey(self): return self._hotkey
	def setHotkey(self, hotkey): self._hotkey = hotkey
	def hotkeyName(self): return self._hotkeyName
	def setHotkeyName(self, hotkeyName): self._hotkeyName = hotkeyName
	@classmethod
	def attrsFromConfig(klass, key, klassID):
		id = TableCrabConfig.settingsValue( (key, 'ID'), '').toString()
		if id != klassID: return None
		hotkey = TableCrabConfig.settingsValue( (key, 'Hotkey'), TableCrabConfig.HotkeyNone).toString()
		if hotkey == TableCrabConfig.HotkeyNone: return None
		hotkeyName = TableCrabConfig.settingsValue( (key, 'HotkeyName'), '').toString()
		return {'hotkey': hotkey, 'hotkeyName': hotkeyName}
	@classmethod
	def fromConfig(klass, key):
		attrs = klass.attrsFromConfig(key, klass.id() )
		if attrs is not None:
			return klass(**attrs)
	def toConfig(self, key):
		TableCrabConfig.settingsSetValue( (key, 'ID'), self.id() )
		TableCrabConfig.settingsSetValue((key, 'Hotkey'), self.hotkey() )
		TableCrabConfig.settingsSetValue( (key, 'HotkeyName'), self.hotkeyName() )
		return True
	def createEditor(self, parent=None, settingsKey=None, isEdit=True):
		other = self.__class__()
		other.update(self)
		dlg = HotkeyEditor(other, parent=parent, settingsKey=settingsKey, isEdit=isEdit)
		result = None
		if dlg.exec_() == dlg.Accepted:
			self.update(other)
			return self

Hotkeys.append(HotkeyCheck)

class HotkeyFold(HotkeyCheck):
	@classmethod
	def id(klass): return 'Fold'
	@classmethod
	def menuName(klass): return 'Fold'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+F')
Hotkeys.append(HotkeyFold)

class HotkeyRaise(HotkeyCheck):
	@classmethod
	def id(klass): return 'Raise'
	@classmethod
	def menuName(klass): return 'Raise'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+R')
Hotkeys.append(HotkeyRaise)

class HotkeyAll_In(HotkeyCheck):
	@classmethod
	def id(klass): return 'All_In'
	@classmethod
	def menuName(klass): return 'All-In'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+L')
Hotkeys.append(HotkeyAll_In)

class HotkeyHilightBet(HotkeyCheck):
	@classmethod
	def id(klass): return 'HilightBet'
	@classmethod
	def menuName(klass): return 'Hilight bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+I')
Hotkeys.append(HotkeyHilightBet)

class HotkeyMultiplyBet(HotkeyCheck):
	MultiplierMax = 99.0
	MultiplierMin = 1.0
	MultiplierDefault = 1.0
	@classmethod
	def id(klass): return 'MultiplyBet'
	@classmethod
	def menuName(klass): return 'Multiply bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+M')
	def __init__(self, parent=None, hotkey='', hotkeyName='', multiplier=1.0):
		self._multiplier = multiplier
		HotkeyCheck.__init__(self, parent=parent, hotkey=hotkey, hotkeyName=hotkeyName)
	def update(self, other):
		self._multiplier = other.multiplier()
		HotkeyCheck.update(self, other)
	def multiplier(self): return self._multiplier
	def setMultiplier(self, multiplier): self._multiplier = round(multiplier, 1)
	def action(self):
		if int(self._multiplier) == self._multiplier:
			text = 'Multiply bet by %s' % int(self._multiplier)
		else:
			text = 'Multiply bet by %s' % self._multiplier
		return text
	@classmethod
	def attrsFromConfig(klass, key, klassID):
		attrs = HotkeyCheck.attrsFromConfig(key, klassID)
		if attrs is not None:
			multiplier, ok = TableCrabConfig.settingsValue( (key, 'Multiplier'), -1.0).toDouble()
			if not ok: return None
			if multiplier > klass.MultiplierMax or multiplier < klass.MultiplierMin: return None
			attrs['multiplier'] = multiplier
			return attrs
	@classmethod
	def fromConfig(klass, key):
		attrs = HotkeyCheck.attrsFromConfig(key, klass.id() )
		if attrs is not None:
			myAttrs = klass.attrsFromConfig(key, klass.id() )
			if myAttrs is not None:
				attrs.update(myAttrs)
				return klass(**attrs)
	def toConfig(self, key):
		HotkeyCheck.toConfig(self, key)
		TableCrabConfig.settingsSetValue( (key, 'Multiplier'), self._multiplier)
		return True
	def createEditor(self, parent=None, settingsKey=None, isEdit=True):
		other = self.__class__()
		other.update(self)
		dlg = HotkeyEditorWithMultiplier(other, parent=parent, settingsKey=settingsKey, isEdit=isEdit)
		result = None
		if dlg.exec_() == dlg.Accepted:
			self.update(other)
			return self

Hotkeys.append(HotkeyMultiplyBet)


class HotkeyBetPot(HotkeyMultiplyBet):
	@classmethod
	def id(klass): return 'BetPot'
	@classmethod
	def menuName(klass): return 'Bet pot'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+T')
	def action(self):
		if int(self._multiplier) == self._multiplier:
			text = 'Bet %s x pot' % int(self._multiplier)
		else:
			text = 'Bet %s x pot' % self._multiplier
		return text

Hotkeys.append(HotkeyBetPot)

class HotkeyAddToBet(HotkeyMultiplyBet):
	BaseValues = ('BigBlind', 'SmallBlind')
	def __init__(self, parent=None, hotkey='', hotkeyName='', multiplier=1.0,baseValue='BigBlind'):
		self._baseValue = baseValue
		HotkeyMultiplyBet.__init__(self, parent=parent, hotkey=hotkey, hotkeyName=hotkeyName, multiplier=multiplier)
	def update(self, other):
		self._baseValue = other.baseValue()
		HotkeyMultiplyBet.update(self, other)
	def action(self):
		if self._multiplier == 1:
			baseValue = 'big blind' if self._baseValue == 'BigBlind' else 'small blind'
			multiplier = 1
		elif int(self._multiplier) == self._multiplier:
			baseValue = 'big blinds' if self._baseValue == 'BigBlind' else 'small blinds'
			multiplier = int(self._multiplier)
		else:
			baseValue = 'big blinds' if self._baseValue == 'BigBlind' else 'small blinds'
			multiplier = self._multiplier
		return 'Add %s %s to bet' % (multiplier, baseValue)
	def baseValue(self): return self._baseValue
	def setBaseValue(self, baseValue): self._baseValue = baseValue
	@classmethod
	def id(klass): return 'AddToBet'
	@classmethod
	def menuName(klass): return 'Add to bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+A')
	@classmethod
	def attrsFromConfig(klass, key, klassID):
		attrs = HotkeyMultiplyBet.attrsFromConfig(key, klassID)
		if attrs is not None:
			baseValue = TableCrabConfig.settingsValue( (key, 'BaseValue'), '').toString()
			if baseValue not in klass.BaseValues: return None
			attrs['baseValue'] = baseValue
			return attrs
	@classmethod
	def fromConfig(klass, key):
		attrs = HotkeyMultiplyBet.attrsFromConfig(key, klass.id() )
		if attrs is not None:
			myAttrs = klass.attrsFromConfig(key, klass.id() )
			if myAttrs is not None:
				attrs.update(myAttrs)
				return klass(**attrs)
	def toConfig(self, key):
		HotkeyMultiplyBet.toConfig(self, key)
		TableCrabConfig.settingsSetValue( (key, 'BaseValue'), self._baseValue)
		return True
	def createEditor(self, parent=None, settingsKey=None, isEdit=True):
		other = self.__class__()
		other.update(self)
		dlg = HotkeyEditorWithMultiplierAndBaseValue(other, parent=parent, settingsKey=settingsKey, isEdit=isEdit)
		result = None
		if dlg.exec_() == dlg.Accepted:
			self.update(other)
			return self

Hotkeys.append(HotkeyAddToBet)

class HotkeySubtractFromBet(HotkeyAddToBet):
	@classmethod
	def id(klass): return 'SubtractFromBet'
	@classmethod
	def menuName(klass): return 'Subtract from bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+S')
	def action(self):
		if self._multiplier == 1:
			baseValue = 'big blind' if self._baseValue == 'BigBlind' else 'small blind'
			multiplier = 1
		elif int(self._multiplier) == self._multiplier:
			baseValue = 'big blinds' if self._baseValue == 'BigBlind' else 'small blinds'
			multiplier = int(self._multiplier)
		else:
			baseValue = 'big blinds' if self._baseValue == 'BigBlind' else 'small blinds'
			multiplier = self._multiplier
		return 'Subtract %s %s from bet' % (multiplier, baseValue)

Hotkeys.append(HotkeySubtractFromBet)

class HotkeyReplayer(HotkeyCheck):
	@classmethod
	def id(klass): return 'Replayer'
	@classmethod
	def menuName(klass): return 'Replayer'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+P')
Hotkeys.append(HotkeyReplayer)

class HotkeyInstantHandHistory(HotkeyCheck):
	@classmethod
	def id(klass): return 'InstantHandHistory'
	@classmethod
	def menuName(klass): return 'Instant hand history'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+H')
Hotkeys.append(HotkeyInstantHandHistory)

class HotkeyScreenshot(HotkeyCheck):
	@classmethod
	def id(klass): return 'Screenshot'
	@classmethod
	def menuName(klass): return 'Screenshot'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+O')
Hotkeys.append(HotkeyScreenshot)

class HotkeyTableSizeNext(HotkeyCheck):
	@classmethod
	def id(klass): return 'TableSizeNext'
	@classmethod
	def menuName(klass): return 'Table Size Next'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+X')
Hotkeys.append(HotkeyTableSizeNext)


