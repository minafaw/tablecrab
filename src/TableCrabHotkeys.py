
#TODO: restore last selected hokey on restart? would require an attr "itemIsSelected", downside
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
		QtGui.QDialog.__init__(self, parent)
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

		self.comboBaseValue = TableCrabConfig.ComboBox(choices=self.hotkey.BaseValues, default=self.hotkey.baseValue(), parent=self)
		self.comboBaseValue.setToolTip('Base value (Atl+B)')
		self.labelBaseValue = QtGui.QLabel('&BaseValue:', self)
		self.labelBaseValue.setBuddy(self.comboBaseValue)
		if self.hotkey.HasBaseValue:
			self.comboBaseValue.currentIndexChanged.connect(self.setNewActionName)
			self.comboBaseValue.onInit()
		else:
			self.comboBaseValue.setVisible(False)
			self.labelBaseValue.setVisible(False)

		self.spinMultiplier = TableCrabConfig.DoubleSpinBox(
				default=self.hotkey.multiplier(),
				minimum=self.hotkey.MultiplierMin,
				maximum=self.hotkey.MultiplierMax,
				step=10**-self.hotkey.MultiplierPrecision,
				precision=self.hotkey.MultiplierPrecision,
				parent=self,
				)
		self.spinMultiplier.setToolTip('Multiplier (Alt+M)')
		self.labelMultiplier = QtGui.QLabel('&Multiplier:', self)
		self.labelMultiplier.setBuddy(self.spinMultiplier)
		if self.hotkey.HasMultiplier:
			self.spinMultiplier.valueChanged.connect(self.setNewActionName)
			self.spinMultiplier.onInit()
		else:
			self.spinMultiplier.setVisible(False)
			self.labelMultiplier.setVisible(False)

		if self.settingsKey is not None:
			self.restoreGeometry( TableCrabConfig.settingsValue(self.settingsKey, QtCore.QByteArray()).toByteArray() )

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.labelAction).col(self.editAction)
		grid.row()
		grid.col(self.labelHotkey).col(self.hotkeyBox)
		grid.row()
		grid.col(self.labelHotkeyName).col(self.editHotkeyName)
		grid.row()
		grid.col(self.labelBaseValue).col(self.comboBaseValue)
		grid.row()
		grid.col(self.labelMultiplier).col(self.spinMultiplier)
		grid.row()
		grid.col(TableCrabConfig.VStretch())
		grid.row()
		grid.col(TableCrabConfig.HLine(self), colspan=2)
		grid.row()
		grid.col(self.buttonBox, colspan=2)

		# adjust tab order
		TableCrabConfig.setTabOrder(
				self,
				self.buttonBox,
				self.hotkeyBox,
				self.editHotkeyName,
				self.comboBaseValue,
				self.spinMultiplier,
				)

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
		if self.hotkey.HasBaseValue:
			self.hotkey.setBaseValue(self.comboBaseValue.currentText() )
		if self.hotkey.HasMultiplier:
			self.hotkey.setMultiplier(self.spinMultiplier.value() )
		QtGui.QDialog.accept(self)

	def setNewActionName(self,*args):
		if self.hotkey.HasMultiplier:
			self.hotkey.setMultiplier(self.spinMultiplier.value() )
		if self.hotkey.HasBaseValue:
			self.hotkey.setBaseValue(self.comboBaseValue.currentText() )
		self.editAction.setText(self.hotkey.action() )

	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hotkey%s' % self.hotkey.id(), parent=self)


class HotkeyBase(QtGui.QTreeWidgetItem):

	HasMultiplier = False
	MultiplierMax = 0
	MultiplierMin = 0
	MultiplierDefault = 0
	MultiplierPrecision = 0

	HasBaseValue = False
	BaseValues = []
	BaseValueDefault = None

	def __init__(self, parent=None, hotkey='', hotkeyName='', multiplier=None, baseValue=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self._hotkey = hotkey
		self._hotkeyName = hotkeyName
		self._multiplier = self.MultiplierDefault if multiplier is None else multiplier
		self._baseValue = self.BaseValueDefault if baseValue is None else baseValue
		self.setText(0, self.action() )
		self.setText(1, self.hotkeyName() if self.hotkeyName() else self.hotkey())

	@classmethod
	def id(klass):
		raise NotImplementedError()
	def menuName(klass):
		raise NotImplementedError()
	@classmethod
	def shortcut(klass):
		raise NotImplementedError()
	def action(self):
		return self.menuName()
	def hotkey(self):
		return self._hotkey
	def setHotkey(self, hotkey):
		self._hotkey = hotkey
	def hotkeyName(self):
		return self._hotkeyName
	def setHotkeyName(self, hotkeyName):
		self._hotkeyName = hotkeyName
	def multiplier(self):
		return self._multiplier
	def setMultiplier(self, multiplier):
		if self.HasMultiplier:
			self._multiplier = round(multiplier, self.MultiplierPrecision)
	def baseValue(self):
		return self._baseValue
	def setBaseValue(self, baseValue):
		if self.HasBaseValue:
			self._baseValue = baseValue

	@classmethod
	def fromConfig(klass, key):
		id = None
		hotkey = ''
		hotkeyName = ''
		baseValue = None
		multiplier = None

		id = TableCrabConfig.settingsValue( (key, 'ID'), '').toString()
		if id != klass.id():
			return None
		hotkey = TableCrabConfig.settingsValue( (key, 'Hotkey'), TableCrabConfig.HotkeyNone).toString()
		if hotkey == TableCrabConfig.HotkeyNone:
			return None
		hotkeyName = TableCrabConfig.settingsValue( (key, 'HotkeyName'), '').toString()
		if klass.HasMultiplier:
			multiplier, ok = TableCrabConfig.settingsValue( (key, 'Multiplier'), -1.0).toDouble()
			if not ok:
				return None
			if multiplier > klass.MultiplierMax or multiplier < klass.MultiplierMin:
				return None
		if klass.HasBaseValue:
			baseValue = TableCrabConfig.settingsValue( (key, 'BaseValue'), '').toString()
			if baseValue not in klass.BaseValues:
				return None
		return klass(hotkey=hotkey, hotkeyName=hotkeyName, baseValue=baseValue, multiplier=multiplier)

	def toConfig(self, key):
		TableCrabConfig.settingsSetValue( (key, 'ID'), self.id() )
		TableCrabConfig.settingsSetValue((key, 'Hotkey'), self.hotkey() )
		TableCrabConfig.settingsSetValue( (key, 'HotkeyName'), self.hotkeyName() )
		if self.HasMultiplier:
			TableCrabConfig.settingsSetValue( (key, 'Multiplier'), self.multiplier())
		if self.HasBaseValue:
			TableCrabConfig.settingsSetValue( (key, 'BaseValue'), self.baseValue())
		return True

	def createEditor(self, parent=None, settingsKey=None, isEdit=True):
		other = self.__class__(hotkey=self.hotkey(), hotkeyName=self.hotkeyName(), baseValue=self.baseValue(), multiplier=self.multiplier())
		dlg = HotkeyEditor(other, parent=parent, settingsKey=settingsKey, isEdit=isEdit)
		result = None
		if dlg.exec_() == dlg.Accepted:
			self.setHotkey(other.hotkey())
			self.setHotkeyName(other.hotkeyName())
			self.setBaseValue(other.baseValue())
			self.setMultiplier(other.multiplier())
			self.setText(0, self.action() )
			self.setText(1, self.hotkeyName() if self.hotkeyName() else self.hotkey())
			return self

#************************************************************************************
#
#************************************************************************************
class HotkeyCheck(HotkeyBase):
	@classmethod
	def id(klass): return 'Check'
	@classmethod
	def menuName(klass): return 'Check'
	@classmethod
	def shortcut(klass):	return QtGui.QKeySequence('Shift+C')
Hotkeys.append(HotkeyCheck)

class HotkeyFold(HotkeyBase):
	@classmethod
	def id(klass): return 'Fold'
	@classmethod
	def menuName(klass): return 'Fold'
	@classmethod
	def shortcut(klass):	return QtGui.QKeySequence('Shift+F')
Hotkeys.append(HotkeyFold)

class HotkeyRaise(HotkeyBase):
	@classmethod
	def id(klass): return 'Raise'
	@classmethod
	def menuName(klass): return 'Raise'
	@classmethod
	def shortcut(klass):	return QtGui.QKeySequence('Shift+R')
Hotkeys.append(HotkeyRaise)

class HotkeyAll_In(HotkeyBase):
	@classmethod
	def id(klass): return 'All_In'
	@classmethod
	def menuName(klass): return 'All-In'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+L')
Hotkeys.append(HotkeyAll_In)

class HotkeyHilightBet(HotkeyBase):
	@classmethod
	def id(klass): return 'HilightBet'
	@classmethod
	def menuName(klass): return 'Hilight bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+I')
Hotkeys.append(HotkeyHilightBet)

class HotkeyMultiplyBlind(HotkeyBase):
	HasMultiplier = True
	MultiplierMax = 99.0
	MultiplierMin = 1.0
	MultiplierDefault = 1.0
	MultiplierPrecision = 1
	HasBaseValue = True
	BaseValues = (TableCrabConfig.BigBlind, TableCrabConfig.SmallBlind)
	BaseValueDefault = TableCrabConfig.BigBlind
	@classmethod
	def id(klass): return 'MultiplyBlind'
	@classmethod
	def menuName(klass): return 'Multiply blind'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+B')
	def action(self):
		if self.baseValue() == TableCrabConfig.BigBlind:
			baseValue = 'big'
		elif elf.baseValue() == TableCrabConfig.SmallBlind:
			baseValue = 'small'
		else:
			raise ValueError('can not handle base value: %s' % self.baseValue())
		if int(self.multiplier()) == self.multiplier():
			text = 'Multiply %s blind by %s' % (baseValue, int(self.multiplier()))
		else:
			text = 'Multiply %s blind by %s' % (baseValue, self.multiplier())
		return text
Hotkeys.append(HotkeyMultiplyBlind)

class HotkeyMultiplyBet(HotkeyBase):
	HasMultiplier = True
	MultiplierMax = 99.0
	MultiplierMin = 1.0
	MultiplierDefault = 1.0
	MultiplierPrecision = 1
	@classmethod
	def id(klass): return 'MultiplyBet'
	@classmethod
	def menuName(klass): return 'Multiply bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+M')
	def action(self):
		if int(self.multiplier()) == self.multiplier():
			text = 'Multiply bet by %s' % int(self.multiplier())
		else:
			text = 'Multiply bet by %s' % self.multiplier()
		return text
Hotkeys.append(HotkeyMultiplyBet)

class HotkeyBetPot(HotkeyBase):
	HasMultiplier = True
	MultiplierMax = 99.0
	MultiplierMin = 0.1
	MultiplierDefault = 0.5
	MultiplierPrecision = 2
	@classmethod
	def id(klass): return 'BetPot'
	@classmethod
	def menuName(klass): return 'Bet pot'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+T')
	def action(self):
		if int(self.multiplier()) == self.multiplier():
			text = 'Bet %s pot' % int(self.multiplier())
		else:
			text = 'Bet %s pot' % self.multiplier()
		return text
Hotkeys.append(HotkeyBetPot)

class HotkeyAddToBet(HotkeyBase):
	HasMultiplier = True
	MultiplierMax = 99.0
	MultiplierMin = 1.0
	MultiplierDefault = 1.0
	MultiplierPrecision = 1
	HasBaseValue = True
	BaseValues = (TableCrabConfig.BigBlind, TableCrabConfig.SmallBlind)
	BaseValueDefault = TableCrabConfig.BigBlind
	@classmethod
	def id(klass): return 'AddToBet'
	@classmethod
	def menuName(klass): return 'Add to bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+A')
	def action(self):
		if self.multiplier() == 1:
			baseValue = 'big blind' if self.baseValue() == TableCrabConfig.BigBlind else 'small blind'
			multiplier = 1
		elif int(self.multiplier()) == self.multiplier():
			baseValue = 'big blinds' if self.baseValue() == TableCrabConfig.BigBlind else 'small blinds'
			multiplier = int(self.multiplier())
		else:
			baseValue = 'big blinds' if self.baseValue() == TableCrabConfig.BigBlind else 'small blinds'
			multiplier = self.multiplier()
		return 'Add %s %s to bet' % (multiplier, baseValue)
Hotkeys.append(HotkeyAddToBet)

class HotkeySubtractFromBet(HotkeyBase):
	HasMultiplier = True
	MultiplierMax = 99.0
	MultiplierMin = 1.0
	MultiplierDefault = 1.0
	MultiplierPrecision = 1
	HasBaseValue = True
	BaseValues = (TableCrabConfig.BigBlind, TableCrabConfig.SmallBlind)
	BaseValueDefault = TableCrabConfig.BigBlind
	@classmethod
	def id(klass): return 'SubtractFromBet'
	@classmethod
	def menuName(klass): return 'Subtract from bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+S')
	def action(self):
		if self.multiplier() == 1:
			baseValue = 'big blind' if self.baseValue() == TableCrabConfig.BigBlind else 'small blind'
			multiplier = 1
		elif int(self.multiplier()) == self.multiplier():
			baseValue = 'big blinds' if self.baseValue() == TableCrabConfig.BigBlind else 'small blinds'
			multiplier = int(self.multiplier())
		else:
			baseValue = 'big blinds' if self.baseValue() == TableCrabConfig.BigBlind else 'small blinds'
			multiplier = self.multiplier()
		return 'Subtract %s %s from bet' % (multiplier, baseValue)
Hotkeys.append(HotkeySubtractFromBet)

class HotkeyReplayer(HotkeyBase):
	@classmethod
	def id(klass): return 'Replayer'
	@classmethod
	def menuName(klass): return 'Replayer'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+P')
Hotkeys.append(HotkeyReplayer)

class HotkeyInstantHandHistory(HotkeyBase):
	@classmethod
	def id(klass): return 'InstantHandHistory'
	@classmethod
	def menuName(klass): return 'Instant hand history'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+H')
Hotkeys.append(HotkeyInstantHandHistory)

class HotkeyScreenshot(HotkeyBase):
	@classmethod
	def id(klass): return 'Screenshot'
	@classmethod
	def menuName(klass): return 'Screenshot'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+O')
Hotkeys.append(HotkeyScreenshot)

class HotkeyTableSizeNext(HotkeyBase):
	@classmethod
	def id(klass): return 'TableSizeNext'
	@classmethod
	def menuName(klass): return 'Table Size Next'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+X')
Hotkeys.append(HotkeyTableSizeNext)


