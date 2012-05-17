
import Tc2Config
import Tc2Win32
import Tc2GuiHelp
import Tc2ConfigHotkeys

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
class HotkeyWidget(QtGui.QTreeWidget):

	SettingsKeyBase = 'Gui'
	SettingsKeyHotkeyEditorGeometry =SettingsKeyBase + '/DialogHotkeyEditor/Geometry'
	SettingsKeyHotkeys = 'Hotkeys'

	settingHotkeyEditorGeometry = Tc2Config.settings2.ByteArray(
			'Gui/DialogHotkeyEditor/Geometry',
			defaultValue=QtCore.QByteArray()
			)

	settingsHotkeys = []
	for i in xrange(Tc2Config.MaxHotkeys):
		settingsHotkeys.append({
			'id': Tc2Config.settings2.UnicodeString(
					'Hotkeys/%03i-Id' % i,
					defaultValue=''
					),
			'key': Tc2Config.settings2.UnicodeString(
					'Hotkeys/%03i-Key' % i,
					defaultValue=''
					),
			'hotkeyName': Tc2Config.settings2.UnicodeString(
					'Hotkeys/%03i-HotkeyName' % i,
					defaultValue=''
					),
			'multiplier': Tc2Config.settings2.Float(
					'Hotkeys/%03i-Multiplier' % i,
					defaultValue=Tc2ConfigHotkeys.MultiplierDefault,
					minValue=Tc2ConfigHotkeys.MultiplierMin,
					maxValue=Tc2ConfigHotkeys.MultiplierMax,
					),
			'baseValue': Tc2Config.settings2.ChooseString(
					'Hotkeys/%03i-BaseValue' % i,
					defaultValue=Tc2ConfigHotkeys.BaseValueDefault,
					choices=Tc2ConfigHotkeys.BaseValues
					),
			})

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
		Tc2Config.globalObject.objectCreatedHotkeyManager.emit(self)

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
		for hotkeyProto in Tc2ConfigHotkeys.Hotkeys:
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
		Tc2Config.globalObject.guiInited.connect(self.onGuiInited)
		self.itemDoubleClicked.connect(self.onHotkeyDoubleClicked)
		self.itemSelectionChanged.connect(self.adjustActions)
		Tc2Config.settings2['Gui/AlternatingRowColors'].changed.connect(
				lambda setting:self.setAlternatingRowColors(setting.value())
				)

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
		self.actionNew.setEnabled(len(self) < Tc2Config.MaxHotkeys)
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
		# find free slot
		data = None
		for data in self.settingsHotkeys:
			if not data['id'].value():
				break
		else:
			raise valueError('no free slot found!')
		hotkey = hotkeyProto(userData=data)
		hotkey = hotkey.createEditor(
				parent=self,
				settingGeometry=self.settingHotkeyEditorGeometry,
				isEdit=False
				)
		if hotkey is not None:
			for attr, setting in data.items():
				setting.setValue(getattr(hotkey, attr)())
			self.addTopLevelItem(hotkey)
			self.setCurrentItem(hotkey)
			self.adjustHotkeys()

	def editHotkey(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionEdit.setEnabled(False)
			return
		hotkey = hotkey.createEditor(
				parent=self,
				settingGeometry=self.settingHotkeyEditorGeometry,
				isEdit=True
				)
		if hotkey is not None:
			data = hotkey.userData()
			data = hotkey.userData()
			for attr, setting in data.items():
				setting.setValue(getattr(hotkey, attr)())
			self.adjustHotkeys()

	def moveHotkeyDown(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionDown.setEnabled(False)
			return
		# move tree item
		i = self.indexOfTopLevelItem(hotkey)
		hotkeyOther = self.topLevelItem(i+1)
		self.takeTopLevelItem(i)
		self.insertTopLevelItem(i+1, hotkey)
		# move settings
		data = hotkey.userData()
		dataOther = hotkeyOther.userData()
		hotkeyOther.setUserData(data)
		hotkey.setUserData(dataOther)
		for attr, setting in dataOther.items():
			setting.setValue(getattr(hotkey, attr)())
		for attr, setting in data.items():
			setting.setValue(getattr(hotkeyOther, attr)())
		# finally
		self.setCurrentItem(hotkey)

	def moveHotkeyUp(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionUp.setEnabled(False)
			return
		# move tree item
		i = self.indexOfTopLevelItem(hotkey)
		hotkeyOther = self.topLevelItem(i-1)
		self.takeTopLevelItem(i)
		self.insertTopLevelItem(i-1, hotkey)
		# move settings
		data = hotkey.userData()
		dataOther = hotkeyOther.userData()
		hotkeyOther.setUserData(data)
		hotkey.setUserData(dataOther)
		for attr, setting in dataOther.items():
			setting.setValue(getattr(hotkey, attr)())
		for attr, setting in data.items():
			setting.setValue(getattr(hotkeyOther, attr)())
		# finally
		self.setCurrentItem(hotkey)

	def removeHotkey(self):
		hotkey = self.currentItem()
		if hotkey is None:
			self.actionRemove.setEnabled(False)
			return
		self.takeTopLevelItem(self.indexOfTopLevelItem(hotkey) )
		data = hotkey.userData()
		for attr, setting in data.items():
			data[attr].resetValue()
		self.dumpItems()
		self.adjustHotkeys()

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onHotkeyDoubleClicked(self, hotkey):
		self.editHotkey()

	def dumpItems(self):
		nItems = self.topLevelItemCount()
		for i, data in enumerate(self.settingsHotkeys):
			if i < nItems:
				hotkey = self.topLevelItem(i)
				dataOld = hotkey.userData()
				for attr, setting in dataOld.items():
					data[attr].setValue(setting.value())
				hotkey.setUserData(data)
			else:
				for attr, setting in data.items():
					data[attr].resetValue()

	def onGuiInited(self):
		self.setUpdatesEnabled(False)
		self.clear()

		#NOTE: we run into fragementation problems here if the user edits settings by hand.
		# so we have to defrag hotkeys if necessary
		nSlots = 0
		hotkeyKlasses = dict([(hotkeyKlass.id(), hotkeyKlass) for hotkeyKlass in Tc2ConfigHotkeys.Hotkeys])
		for iSlot, data in enumerate(self.settingsHotkeys):
			hotkeyKlass = hotkeyKlasses.get(data['id'].value(), None)
			if hotkeyKlass is not None:
				nSlots = iSlot +1
				tmpData = data.copy()
				del tmpData['id']
				kws = dict([(attr, setting.value()) for (attr, setting) in tmpData.items()])
				kws['userData'] = data
				hotkey = hotkeyKlass(**kws)
				self.addTopLevelItem(hotkey)

		# clean up if necessary
		nItems = self.topLevelItemCount()
		if nSlots != nItems:
			self.dumpItems()

		# make shure there is at least one hotkey present
		if not nItems and self.settingsHotkeys:
			data = self.settingsHotkeys[0]
			hotkey = Tc2ConfigHotkeys.HotkeyScreenshot(key='<F1+LeftControl>', userData=data)
			for attr, setting in data.items():
				setting.setValue(getattr(hotkey, attr)())
			self.addTopLevelItem(hotkey)

		self.setUpdatesEnabled(True)
		self.adjustHotkeys()
		self.adjustActions()

#**********************************************************************************************
#
#**********************************************************************************************
class FrameHotkeys(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.grid = Tc2Config.GridBox(self)

		self.hotkeyWidget = HotkeyWidget(self)
		self.toolBar = QtGui.QToolBar(self)
		for action in self.hotkeyWidget.actions():
			self.toolBar.addAction(action)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self.toolBar.addAction(self.actionHelp)

		# connect global signals
		Tc2Config.settings2['Gui/ToolBar/Position'].changed.connect(
				lambda setting: self.layout(setting.value())
				)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def layout(self, toolBarPosition):
		grid = self.grid
		self.grid.clear()
		if toolBarPosition == Tc2Config.ToolBarPositionTop:
			grid.col(self.toolBar)
			grid.row()
		grid.col(self.hotkeyWidget)
		if toolBarPosition == Tc2Config.ToolBarPositionBottom:
			grid.row()
			grid.col(self.toolBar)


	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self):
		Tc2GuiHelp.dialogHelp('hotkeys', parent=self)



