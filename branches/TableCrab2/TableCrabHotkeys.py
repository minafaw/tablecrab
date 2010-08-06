
import TableCrabConfig
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui
#**********************************************************************************************
#
#**********************************************************************************************

Hotkeys = []
MaxHotkeys = 64


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
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'rejected()', self.reject)
		
		self.labelAction = QtGui.QLabel('Action:', self)
		self.editAction = QtGui.QLineEdit(self)
		self.editAction.setText(self.hotkey.action())
		self.editAction.setEnabled(False)
		self.labelHotkey = QtGui.QLabel('Hotkey:', self)
		self.hotkeyBox = TableCrabConfig.HotkeyBox(hotkey=self.hotkey.hotkey(), parent=self)
		self.labelHotkeyName = QtGui.QLabel('HotkeyName:', self)
		self.editHotkeyName = QtGui.QLineEdit(self)
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
	
	def closeEvent(self, event):
		if self.settingsKey is not None: 
			TableCrabConfig.settingsSetValue(self.settingsKey, self.saveGeometry() )
	
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
		self.labelMultiplier = QtGui.QLabel('multiplier:', self)
		self.spinMultiplier = TableCrabConfig.DoubleSpinBox(
				default=self.hotkey.multiplier(), 
				minimum=self.hotkey.MultiplierMin, 
				maximum=self.hotkey.MultiplierMax, 
				step=0.1, 
				precision=1,
				parent=self,
				)
		TableCrabConfig.signalConnect(self.spinMultiplier, self, 'valueChanged(double)', self.setNewActionName)
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
		self.labelBasevalue = QtGui.QLabel('BaseValue:', self)
		self.comboBaseValue = TableCrabConfig.ComboBox(choices=self.hotkey.BaseValues, default=self.hotkey.baseValue(), parent=self)
		TableCrabConfig.signalConnect(self.comboBaseValue, self, 'currentIndexChanged(int)', self.setNewActionName)
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

class HotkeyCall(HotkeyCheck):
	@classmethod
	def id(klass): return 'Call'
	@classmethod
	def menuName(klass): return 'Call'
Hotkeys.append(HotkeyCall)

class HotkeyFold(HotkeyCheck):
	@classmethod
	def id(klass): return 'Fold'
	@classmethod
	def menuName(klass): return 'Fold'
Hotkeys.append(HotkeyFold)

class HotkeyRaise(HotkeyCheck):
	@classmethod
	def id(klass): return 'Raise'
	@classmethod
	def menuName(klass): return 'Raise'
Hotkeys.append(HotkeyRaise)

class HotkeyAll_In(HotkeyCheck):
	@classmethod
	def id(klass): return 'All_In'
	@classmethod
	def menuName(klass): return 'All-In'
Hotkeys.append(HotkeyAll_In)

class HotkeyHilightBetAmount(HotkeyCheck):
	@classmethod
	def id(klass): return 'HilightBetAmount'
	@classmethod
	def menuName(klass): return 'Hilight Bet Amount'
Hotkeys.append(HotkeyHilightBetAmount)

class HotkeyReplayer(HotkeyCheck):
	@classmethod
	def id(klass): return 'Replayer'
	@classmethod
	def menuName(klass): return 'Replayer'
Hotkeys.append(HotkeyReplayer)

class HotkeyInstantHandHistory(HotkeyCheck):
	@classmethod
	def id(klass): return 'InstantHandHistory'
	@classmethod
	def menuName(klass): return 'Instant hand history'
Hotkeys.append(HotkeyInstantHandHistory)

class HotkeyScreenshot(HotkeyCheck):
	@classmethod
	def id(klass): return 'Screenshot'
	@classmethod
	def menuName(klass): return 'Screenshot'
Hotkeys.append(HotkeyScreenshot)


class HotkeyMultiplyBetAmount(HotkeyCheck):
	MultiplierMax = 99.0
	MultiplierMin = 1.0
	MultiplierDefault = 1.0
	@classmethod
	def id(klass): return 'MultiplyBetAmount'
	@classmethod
	def menuName(klass): return 'Multiply bet amount'
	def __init__(self, parent=None, hotkey='', hotkeyName='', multiplier=1.0):
		self._multiplier = multiplier
		HotkeyCheck.__init__(self, parent=None, hotkey='', hotkeyName='')
	def update(self, other):
		self._multiplier = other.multiplier()
		HotkeyCheck.update(self, other)
	def multiplier(self): return self._multiplier
	def setMultiplier(self, multiplier): self._multiplier = round(multiplier, 1)
	def action(self):
		if int(self._multiplier) == self._multiplier:
			text = 'Multiply Bet Amount By %s' % int(self._multiplier)
		else:
			text = 'Multiply Bet Amount By %s' % self._multiplier
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
		attrs = klass.attrsFromConfig(key, klass.id() )
		if attrs is not None:
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

Hotkeys.append(HotkeyMultiplyBetAmount)
	
class HotkeyAddToBetAmount(HotkeyMultiplyBetAmount):
	BaseValues = ('BigBlind', 'SmallBlind')
	def __init__(self, parent=None, hotkey='', hotkeyName='', multiplier=1.0,baseValue='BigBlind'):
		self._baseValue = baseValue
		HotkeyMultiplyBetAmount.__init__(self, parent=None, hotkey='', hotkeyName='', multiplier=1.0)
	def update(self, other):
		self._baseValue = other.baseValue()
		HotkeyMultiplyBetAmount.update(self, other)
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
		return 'Add %s %s' % (multiplier, baseValue)
	def baseValue(self): return self._baseValue
	def setBaseValue(self, baseValue): self._baseValue = baseValue
	@classmethod
	def id(klass): return 'AddToBetAmount'
	@classmethod
	def menuName(klass): return 'Add to bet amount'
	@classmethod
	def attrsFromConfig(klass, key, klassID):
		attrs = HotkeyMultiplyBetAmount.attrsFromConfig(key, klassID)
		if attrs is not None:
			baseValue = TableCrabConfig.settingsValue( (key, 'BaseValue'), '').toString()
			if baseValue not in klass.BaseValues: return None
			attrs['baseValue'] = baseValue
			return attrs
	@classmethod
	def fromConfig(klass, key):
		attrs = klass.attrsFromConfig(key, klass.id() )
		if attrs is not None:
			return klass(**attrs)
	def toConfig(self, key):
		HotkeyMultiplyBetAmount.toConfig(self, key)
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

Hotkeys.append(HotkeyAddToBetAmount)

class HotkeySubtractFromBetAmount(HotkeyAddToBetAmount):
	@classmethod
	def id(klass): return 'SubtractFromBetAmount'
	@classmethod
	def menuName(klass): return 'Subtract from bet amount'
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
		return 'Subtract %s %s' % (multiplier, baseValue)
		
Hotkeys.append(HotkeySubtractFromBetAmount)
	
	
