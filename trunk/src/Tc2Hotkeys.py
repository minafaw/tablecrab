
#TODO: restore last selected hokey on restart? would require an attr "itemIsSelected", downside
#				we'd have to dump the whole tree on every curent item change.


import Tc2Config
import Tc2GuiHelp

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
		self.hotkeyBox = Tc2Config.HotkeyBox(key=self.hotkey.key(), parent=self)
		self.hotkeyBox.setToolTip('Hotkey (Alt+K)')
		self.labelHotkey.setBuddy(self.hotkeyBox)

		self.labelHotkeyName = QtGui.QLabel('HotkeyN&ame:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
		self.editHotkeyName.setToolTip('Edit shortcut name (Alt+A)')
		self.labelHotkeyName.setBuddy(self.editHotkeyName)
		self.editHotkeyName.setText(self.hotkey.hotkeyName()  )

		self.comboBaseValue = QtGui.QComboBox(self)
		self.labelBaseValue = QtGui.QLabel('&BaseValue:', self)
		if self.hotkey.HasBaseValue:
			self.comboBaseValue.addItems(self.hotkey.BaseValues)
			self.comboBaseValue.setCurrentIndex( self.comboBaseValue.findText(self.hotkey.baseValue(), QtCore.Qt.MatchExactly) )
			self.comboBaseValue.setToolTip('Base value (Atl+B)')
			self.labelBaseValue.setBuddy(self.comboBaseValue)
			self.comboBaseValue.currentIndexChanged.connect(self.setNewActionName)
		else:
			self.comboBaseValue.setVisible(False)
			self.labelBaseValue.setVisible(False)

		self.spinMultiplier = QtGui.QDoubleSpinBox(self)
		self.labelMultiplier = QtGui.QLabel('&Multiplier:', self)
		if self.hotkey.HasMultiplier:
			self.spinMultiplier.setRange(self.hotkey.MultiplierMin, self.hotkey.MultiplierMax)
			self.spinMultiplier.setSingleStep(10**-self.hotkey.MultiplierPrecision)
			self.spinMultiplier.setDecimals(self.hotkey.MultiplierPrecision)
			self.spinMultiplier.setValue(self.hotkey.multiplier() )
			self.spinMultiplier.setToolTip('Multiplier (Alt+M)')
			self.labelMultiplier.setBuddy(self.spinMultiplier)
			self.spinMultiplier.valueChanged.connect(self.setNewActionName)
		else:
			self.spinMultiplier.setVisible(False)
			self.labelMultiplier.setVisible(False)

		if self.settingsKey is not None:
			self.restoreGeometry( Tc2Config.settingsValue(self.settingsKey, QtCore.QByteArray()).toByteArray() )

	def layout(self):
		grid = Tc2Config.GridBox(self)
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
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=2)
		grid.row()
		grid.col(self.buttonBox, colspan=2)

		# adjust tab order
		Tc2Config.setTabOrder(
				self,
				self.buttonBox,
				self.hotkeyBox,
				self.editHotkeyName,
				self.comboBaseValue,
				self.spinMultiplier,
				)

	def hideEvent(self, event):
		if self.settingsKey is not None:
			Tc2Config.settingsSetValue(self.settingsKey, self.saveGeometry() )
		return QtGui.QDialog.hideEvent(self, event)

	def exec_(self):
		self.layout()
		if self.settingsKey is not None:
			self.restoreGeometry( Tc2Config.settingsValue(self.settingsKey, QtCore.QByteArray()).toByteArray() )
		return QtGui.QDialog.exec_(self)

	def accept(self):
		self.hotkey.setKey(self.hotkeyBox.key() )
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
		Tc2GuiHelp.dialogHelp('hotkey%s' % self.hotkey.id(), parent=self)


class HotkeyBase(QtGui.QTreeWidgetItem):

	HasMultiplier = False
	MultiplierMax = 0
	MultiplierMin = 0
	MultiplierDefault = 0
	MultiplierPrecision = 0

	HasBaseValue = False
	BaseValues = []
	BaseValueDefault = None

	def __init__(self, parent=None, key='', hotkeyName='', multiplier=None, baseValue=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self._key = key
		self._hotkeyName = hotkeyName
		self._multiplier = self.MultiplierDefault if multiplier is None else multiplier
		self._baseValue = self.BaseValueDefault if baseValue is None else baseValue
		self.setText(0, self.action() )
		self.setText(1, self.hotkeyName() if self.hotkeyName() else self.key())

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
	def key(self):
		return self._key
	def setKey(self, key):
		self._key = key
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
	def fromConfig(klass, settingsKey):
		id = None
		key = ''
		hotkeyName = ''
		baseValue = None
		multiplier = None

		id = Tc2Config.settingsValue( (settingsKey, 'ID'), '').toString()
		if id != klass.id():
			return None
		#TODO: rename to "Key"
		key = Tc2Config.settingsValue( (settingsKey, 'Hotkey'), Tc2Config.KeyNone).toString()
		if key == Tc2Config.KeyNone:
			return None
		hotkeyName = Tc2Config.settingsValue( (settingsKey, 'HotkeyName'), '').toString()
		if klass.HasMultiplier:
			multiplier, ok = Tc2Config.settingsValue( (settingsKey, 'Multiplier'), -1.0).toDouble()
			if not ok:
				return None
			if multiplier > klass.MultiplierMax or multiplier < klass.MultiplierMin:
				return None
		if klass.HasBaseValue:
			baseValue = Tc2Config.settingsValue( (settingsKey, 'BaseValue'), '').toString()
			if baseValue not in klass.BaseValues:
				return None
		return klass(key=key, hotkeyName=hotkeyName, baseValue=baseValue, multiplier=multiplier)

	def toConfig(self, settingsKey):
		Tc2Config.settingsSetValue( (settingsKey, 'ID'), self.id() )
		#TODO: rename to "Key"
		Tc2Config.settingsSetValue((settingsKey, 'Hotkey'), self.key() )
		Tc2Config.settingsSetValue( (settingsKey, 'HotkeyName'), self.hotkeyName() )
		if self.HasMultiplier:
			Tc2Config.settingsSetValue( (settingsKey, 'Multiplier'), self.multiplier())
		if self.HasBaseValue:
			Tc2Config.settingsSetValue( (settingsKey, 'BaseValue'), self.baseValue())
		return True

	def createEditor(self, parent=None, settingsKey=None, isEdit=True):
		other = self.__class__(key=self.key(), hotkeyName=self.hotkeyName(), baseValue=self.baseValue(), multiplier=self.multiplier())
		dlg = HotkeyEditor(other, parent=parent, settingsKey=settingsKey, isEdit=isEdit)
		result = None
		if dlg.exec_() == dlg.Accepted:
			self.setKey(other.key())
			self.setHotkeyName(other.hotkeyName())
			self.setBaseValue(other.baseValue())
			self.setMultiplier(other.multiplier())
			self.setText(0, self.action() )
			self.setText(1, self.hotkeyName() if self.hotkeyName() else self.key())
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
	BaseValues = (Tc2Config.BigBlind, Tc2Config.SmallBlind)
	BaseValueDefault = Tc2Config.BigBlind
	@classmethod
	def id(klass): return 'MultiplyBlind'
	@classmethod
	def menuName(klass): return 'Multiply blind'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+B')
	def action(self):
		if self.baseValue() == Tc2Config.BigBlind:
			baseValue = 'big'
		elif self.baseValue() == Tc2Config.SmallBlind:
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
	BaseValues = (Tc2Config.BigBlind, Tc2Config.SmallBlind)
	BaseValueDefault = Tc2Config.BigBlind
	@classmethod
	def id(klass): return 'AddToBet'
	@classmethod
	def menuName(klass): return 'Add to bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+A')
	def action(self):
		if self.multiplier() == 1:
			baseValue = 'big blind' if self.baseValue() == Tc2Config.BigBlind else 'small blind'
			multiplier = 1
		elif int(self.multiplier()) == self.multiplier():
			baseValue = 'big blinds' if self.baseValue() == Tc2Config.BigBlind else 'small blinds'
			multiplier = int(self.multiplier())
		else:
			baseValue = 'big blinds' if self.baseValue() == Tc2Config.BigBlind else 'small blinds'
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
	BaseValues = (Tc2Config.BigBlind, Tc2Config.SmallBlind)
	BaseValueDefault = Tc2Config.BigBlind
	@classmethod
	def id(klass): return 'SubtractFromBet'
	@classmethod
	def menuName(klass): return 'Subtract from bet'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+S')
	def action(self):
		if self.multiplier() == 1:
			baseValue = 'big blind' if self.baseValue() == Tc2Config.BigBlind else 'small blind'
			multiplier = 1
		elif int(self.multiplier()) == self.multiplier():
			baseValue = 'big blinds' if self.baseValue() == Tc2Config.BigBlind else 'small blinds'
			multiplier = int(self.multiplier())
		else:
			baseValue = 'big blinds' if self.baseValue() == Tc2Config.BigBlind else 'small blinds'
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


