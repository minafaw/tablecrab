
import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************

class ChildItem(QtGui.QTreeWidgetItem):
	def __init__(self, attrName, text, value, parent=None):
		self.attrName = attrName
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.setText(0, text)
		self.setText(1, value)


class TablePokerStarsTreeWidgetItem(QtGui.QTreeWidgetItem):
	def __init__(self, persistentItem, parent=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.persistentItem = persistentItem
		self.attrName = 'name'
		self.setText(0, self.persistentItem.name)
		self.setFirstColumnSpanned(True)
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
		self.setIcon(0, QtGui.QIcon(TableCrabConfig.Pixmaps.stars()) )
		font = self.font(0)
		font.setBold(True)
		self.setFont(0, font)
		if self.persistentItem.itemIsExpanded:
			self.setExpanded(True)
		self.myChildren = {
				'itemName': ChildItem('itemName', 'Window:', self.persistentItem.itemName(), parent=self),
				'size': ChildItem('size', 'Size:', TableCrabConfig.sizeToString(self.persistentItem.size), parent=self),
				'buttonCheck': ChildItem('buttonCheck', 'ButtonCheck:', TableCrabConfig.pointToString(self.persistentItem.buttonCheck), parent=self),
				'buttonFold': ChildItem('buttonFold', 'ButtonFold:', TableCrabConfig.pointToString(self.persistentItem.buttonFold), parent=self),
				'buttonRaise': ChildItem('buttonRaise', 'ButtonRaise:', TableCrabConfig.pointToString(self.persistentItem.buttonRaise), parent=self),
				'checkboxFold': ChildItem('checkboxFold', 'CheckboxFold:', TableCrabConfig.pointToString(self.persistentItem.checkboxFold), parent=self),
				'checkboxCheckFold': ChildItem('checkboxCheckFold', 'CheckboxCheckFold:', TableCrabConfig.pointToString(self.persistentItem.checkboxCheckFold), parent=self),
				'betSliderStart': ChildItem('betSliderStart', 'BetSliderStart:', TableCrabConfig.pointToString(self.persistentItem.betSliderStart), parent=self),
				'betSliderEnd': ChildItem('betSliderEnd', 'BetSliderEnd:', TableCrabConfig.pointToString(self.persistentItem.betSliderEnd), parent=self),
				'instantHandHistory': ChildItem('instantHandHistory', 'InstantHandHistory:', TableCrabConfig.pointToString(self.persistentItem.instantHandHistory), parent=self),
				'replayer': ChildItem('replayer', 'Replayer:', TableCrabConfig.pointToString(self.persistentItem.replayer), parent=self),
				}
		self.myChildren['itemName'].setDisabled(True)
		
		TableCrabConfig.signalConnect(None, self.persistentItem, 'widgetScreenshotSet(QPixmap*)', self.onWidgetScreenshotSet)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemAttrChanged(QObject*, QString)', self.onPersistentItemAttrChanged)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemMovedUp(QObject*, int)', self.onPersistentItemMovedUp)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemMovedDown(QObject*, int)', self.onPersistentItemMovedDown)
		TableCrabConfig.signalConnect(self.persistentItem, self.persistentItem, 'itemRemoved(QObject*)', self.onPersistentItemRemoved)
		
		#TODO: bit of a hack here to disable child items initially
		TableCrabConfig.signalEmit(None, 'widgetScreenshotQuery()')
		
	def childItem(self, attrName):
		for index in xrange(self.childCount()):
			child = self.child(index)
			attr = child.data(0, QtCore.Qt.UserRole).toString()
			if attr == attrName:
				return child
		raise valueError('nosuch child: %s' % attrName)
		
	def onPersistentItemMovedUp(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
		self.setExpanded(True)
	def onPersistentItemMovedDown(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
		self.setExpanded(True)
	def onPersistentItemRemoved(self, action):
		treeWidget = self.treeWidget()
		self.persistentItem = None
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
	def onPersistentItemAttrChanged(self, persistentItem, attrName):
		attrName = str(attrName)	#NOTE: we can not pass python strings, so we have to type convert here
		if attrName == 'name':
			self.setText(0, self.persistentItem.name)
		elif attrName == 'itemName':
			child = self.myChildren[attrName]
			child.setText(1,self.persistentItem.itemName() )
		elif attrName == 'size':
			child = self.myChildren[attrName]
			if self.persistentItem.size.isEmpty():
				child.setText(1, 'None')
			else:
				child.setText(1, TableCrabConfig.sizeToString(self.persistentItem.size))
				child.setDisabled(True)
		elif attrName == 'itemIsExpanded':
			self.setExpanded(self.persistentItem.itemIsExpanded)
		else:
			child = self.myChildren[attrName]
			child.setText(1, TableCrabConfig.pointToString( getattr(self.persistentItem, attrName) ) )
	
	def onWidgetScreenshotSet(self, pixmap):
		for attrName, child in self.myChildren.items():
			if attrName == 'itemName': continue
			if attrName == 'size':
				child.setDisabled(True)
				continue
			if pixmap.isNull():
				child.setDisabled(True)
			elif self.persistentItem.size == pixmap.size():
				child.setDisabled(False)
			elif self.persistentItem.size.isEmpty():
				child.setDisabled(False)
			else:
				child.setDisabled(True)
	
class PersistentItemTreeWidget(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		##self.setAlternatingRowColors(True)
		self.setColumnCount(2)
		self.setExpandsOnDoubleClick(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
		self.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		TableCrabConfig.signalConnect(None, self, 'settingAlternatingRowColorsChanged(bool)', self.onSettingAlternatingRowColorsChanged)	
		self.setRootIsDecorated( TableCrabConfig.settingsValue('Gui/ChildItemIndicators', True).toBool() )
		TableCrabConfig.signalConnect(None, self, 'settingChildItemIndicatorsChanged(bool)', self.onSettingChildItemIndicatorsChanged)	
		
		#NOTE: we have to connect after adding the initial tables cos QTreeWidget informs us about every* itemChange
		TableCrabConfig.signalConnect(TableCrabConfig.templateManager, self, 'itemRead(QObject*)', self.onPersistentItemManagerItemRead)
		TableCrabConfig.signalConnect(self, self, 'itemChanged(QTreeWidgetItem*, int)', self.onTreeItemChanged)
		TableCrabConfig.signalConnect(self, self, 'itemDoubleClicked(QTreeWidgetItem*)',self.editItem)
		TableCrabConfig.signalConnect(self, self, 'itemExpanded(QTreeWidgetItem*)',self.onItemExpanded)
		TableCrabConfig.signalConnect(self, self, 'itemCollapsed(QTreeWidgetItem*)',self.onItemCollapsed)
	def keyReleaseEvent(self, event):
		#TODO: for some reason the first enter when the widget is created is not accepted
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			event.accept()
			item = self.currentItem()
			if item is not None:
				self.editItem(item)
			return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)
	def onPersistentItemAdded(self, persistentItem):
		item = TablePokerStarsTreeWidgetItem(persistentItem, parent=self)
		self.addTopLevelItem(item)
		self.setCurrentItem(item)
		TableCrabConfig.templateManager.setItemAttr(persistentItem, 'itemIsExpanded', True)
	def onTreeItemChanged(self, item, column):
		if not TableCrabConfig.templateManager.readFinished():
			return
		if item.attrName == 'name':
			if item.text(0) != item.persistentItem.name:	#NOTE: special handling for in-place editing
				TableCrabConfig.templateManager.setItemAttr(item.persistentItem, 'name', item.text(0))
	def onPersistentItemManagerItemRead(self, persistentItem):
		item = TablePokerStarsTreeWidgetItem(persistentItem, parent=self)
		self.addTopLevelItem(item)
	def onItemExpanded(self, item):
		if not TableCrabConfig.templateManager.readFinished():
			return
		TableCrabConfig.templateManager.setItemAttr(item.persistentItem, 'itemIsExpanded', True)
	def onItemCollapsed(self, item):
		if not TableCrabConfig.templateManager.readFinished():
			return
		TableCrabConfig.templateManager.setItemAttr(item.persistentItem, 'itemIsExpanded', False)
	def createPersistentItem(self, persistentItemProto):
		persistentItem = persistentItemProto(name=persistentItemProto.itemName())
		TableCrabConfig.signalConnect(persistentItem, self, 'itemAdded(QObject*)', self.onPersistentItemAdded)
		TableCrabConfig.templateManager.addItem(persistentItem)
	def onSettingAlternatingRowColorsChanged(self, flag):
		self.setAlternatingRowColors(flag)
	def onSettingChildItemIndicatorsChanged(self, flag):
		self.setRootIsDecorated(flag)

class FramePersistentItems(QtGui.QFrame):
	
	class ActionNewPersistentItem(QtGui.QAction):
		def __init__(self, persistentItemProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.persistentItemProto = persistentItemProto
			self.setText(self.persistentItemProto.itemName())
			
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self._actions = []
		self.persistentItemTreeWidget = PersistentItemTreeWidget(self)
		TableCrabConfig.signalConnect(None, self, 'widgetScreenshotDoubleClicked(QPixmap*, QPoint*)', self.onWidgetScreenshotDoubleClicked)
		TableCrabConfig.signalConnect(self.persistentItemTreeWidget, self, 'itemSelectionChanged()', self.onTreeItemSelectionChanged)
			
		menu = QtGui.QMenu(self)
		for persistentItemProto in TableCrabConfig.templateManager.itemProtos():
			persistentItem = self.ActionNewPersistentItem(persistentItemProto, parent=self)
			TableCrabConfig.signalConnect(persistentItem, self, 'triggered(bool)', self.onPersistentItemNewTriggered)
			menu.addAction(persistentItem)
		self.actionNew = TableCrabConfig.TableCrabAction(
				parent=self,
				text='New',
				menu=menu,
				toolTip='Create a new template',
				)
		self._actions.append(self.actionNew)
			
		self.actionUp = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Up',
				toolTip='Move template up',
				slot=self.onActionUpTriggered,
				)
		self._actions.append(self.actionUp)
		
		self.actionDown = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Down',
				toolTip='Move template down',
				slot=self.onActionDownTriggered,
				)
		self._actions.append(self.actionDown)
		
		self.actionRemove = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Remove',
				toolTip='Remove template',
				slot=self.onActionRemoveTriggered,
				)
		self._actions.append(self.actionRemove)
			
		self.adjustActions()
		self.layout()
	
	def adjustActions(self):
		self.actionNew.setEnabled(TableCrabConfig.templateManager.canAddItem() )
		item = self.persistentItemTreeWidget.currentItem()
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
		else:
			self.actionUp.setEnabled(TableCrabConfig.templateManager.canMoveItemUp(persistentItem) )
			self.actionDown.setEnabled(TableCrabConfig.templateManager.canMoveItemDown(persistentItem) )
			self.actionRemove.setEnabled(True)
	
	def actions(self):
		return self._actions
	
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.persistentItemTreeWidget, 0, 0)
			
	def onWidgetScreenshotDoubleClicked(self, pixmap, point):
		item = self.persistentItemTreeWidget.currentItem()
		if item is None:
			return False
		persistentItem= item.persistentItem if item.parent() is None else item.parent().persistentItem
		if type(getattr(persistentItem, item.attrName)) != QtCore.QPoint:
			return False
		if persistentItem.size.isEmpty():
			pass
		elif persistentItem.size != pixmap.size():
			return False
		TableCrabConfig.templateManager.setItemAttrs(persistentItem, {item.attrName: point, 'size': pixmap.size()})
		return True
		
	def onActionUpTriggered(self):
		item = self.persistentItemTreeWidget.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			return
		persistentItem= item.persistentItem if item.parent() is None else item.parent().persistentItem
		TableCrabConfig.templateManager.moveItemUp(persistentItem)
	
	def onActionDownTriggered(self):
		item = self.persistentItemTreeWidget.currentItem()
		if item is None:
			self.actionDown.setEnabled(False)
			return
		persistentItem = item.persistentItem if item.parent() is None else item.parent().persistentItem
		TableCrabConfig.templateManager.moveItemDown(persistentItem)
	
	def onActionRemoveTriggered(self):
		item = self.persistentItemTreeWidget.currentItem()
		if item is None:
			self.buttonRemove.setEnabled(False)
			return
		persistentItem= item.persistentItem if item.parent() is None else item.parent().persistentItem
		TableCrabConfig.templateManager.removeItem(persistentItem)
		
	def onTreeItemSelectionChanged(self):
		self.adjustActions()
		
	def onPersistentItemNewTriggered(self, checked):
		self.persistentItemTreeWidget.createPersistentItem(self.sender().persistentItemProto)
		
		
class FrameTablesScreenshot(QtGui.QFrame):
	
	class MyLabel(QtGui.QLabel):
		ScreenshotName = 'Screenshot'
		def __init__(self, *args):
			QtGui.QLabel.__init__(self, *args)
			self.setMouseTracking(True)
		def setScreenshot(self, pixmap=None):
			result = False
			self.setPixmap(pixmap)
			if pixmap is None:
				self.setScaledContents(True)
				self.setText(self.ScreenshotName)
				pixmap = QtGui.QPixmap()
			else:
				# manually set size of the label so we get the correct coordiantes of the mouse cursor
				self.setScaledContents(False)
				self.resize(pixmap.size())
				point = QtGui.QCursor.pos()
				point = self.mapFromGlobal(point)
				if point.x() < 0 or point.y() < 0:
					point = QtCore.QPoint()
				self._giveFeedback(pixmap,  point)
				result = True
			# emit global signal
			TableCrabConfig.signalEmit(None, 'widgetScreenshotSet(QPixmap*)', pixmap)
			return result
		def mouseDoubleClickEvent(self, event):
			if event.button() == QtCore.Qt.LeftButton:
				pixmap = self.pixmap()
				if pixmap is not None:
					TableCrabConfig.signalEmit(None, 'widgetScreenshotDoubleClicked(QPixmap*, QPoint*)', pixmap, event.pos())
		def mouseMoveEvent(self, event):
			pixmap = self.pixmap()
			if pixmap is not None:
				self._giveFeedback(pixmap, event.pos())
		def _giveFeedback(self, pixmap, point):
			p = 'Size %s Mouse %s' % (TableCrabConfig.sizeToString(pixmap.size()), TableCrabConfig.pointToString(point) )
			TableCrabConfig.signalEmit(None, 'feedbackCurrentObjectData(QString)', p )
		
		
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self._lastInfo = None
		
		self.label = self.MyLabel('Screenshot')
		self.label.setScaledContents(True)
		self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		
		self.scrollArea = QtGui.QScrollArea(self)
		self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
		self.scrollArea.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.scrollArea.setWidget(self.label)		
		
		self._actions = []
		
		self.actionOpen = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Open screenshot..',
				toolTip='Open a screenshot from file',
				slot=self.onActionOpenTriggered,
				)
		self._actions.append(self.actionOpen)
		
		self.actionSave = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Save screenshot..',
				toolTip='Save screenshot to file',
				slot=self.onActionSaveTriggered,
				)
		self._actions.append(self.actionSave)
		
		self.actionInfo = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Info..',
				toolTip='Detailed screenshot information',
				slot=self.onActionInfoTriggered,
				)
		self._actions.append(self.actionInfo)
			
		TableCrabConfig.signalConnect(None, self, 'widgetScreenshotQuery()', self.onWidgetScreenshotQuery)
		TableCrabConfig.signalConnect(None, self, 'widgetScreenshot(int, QPixmap*)', self.onWidgetScreenshot)
				
		self.adjustActions()
		self.layout()
		
	def actions(self):
		return self._actions
	
	def adjustActions(self):
		self.actionSave.setEnabled(self.label.pixmap() is not None)
		self.actionInfo.setEnabled(self._lastInfo is not None)
	
	def onWidgetScreenshotQuery(self):
		pixmap = self.label.pixmap()
		if pixmap is None:
			pixmap = QtGui.QPixmap()
		TableCrabConfig.signalEmit(None, 'widgetScreenshotSet(QPixmap*)', pixmap)
		
	def onWidgetScreenshot(self, hwnd, pixmap):
		# make shure to not take screenshot of self
		wid = self.effectiveWinId()	# NOTE: effectiveWinId() returns <sip.voidptr> and may be None
		if not wid:
			return
		selfHwnd = int(wid)
		selfParent = TableCrabWin32.windowGetTopLevelParent(selfHwnd)
		otherParent = TableCrabWin32.windowGetTopLevelParent(hwnd)
		if selfParent == otherParent:
			return
		self.gatherWindowInfo(hwnd)		
		self.setScreenshot(pixmap)
		self.adjustActions()
		
	def setScreenshot(self, pixmap=None, screenshotName='NewScreenshot'):
		self.label.setScreenshot(pixmap=pixmap)
		self.adjustActions()
		TableCrabConfig.signalEmit(None, 'feedbackCurrentObject(QString)', screenshotName)
		
	def 	gatherWindowInfo(self, hwnd):
		def windowInfo(hwnd, level=0):
			title = TableCrabWin32.windowGetText(hwnd).replace('\r', '')
			if '\n' in title: title = title.split('\n', 1)[0]
			className = TableCrabWin32.windowGetClassName(hwnd)
			buttons = sorted( TableCrabWin32.windowGetButtons(hwnd).keys() )
			size = TableCrabWin32.windowGetRect(hwnd).size()
			pos = TableCrabWin32.windowGetPos(hwnd)
			if not buttons:
				buttons = ''
			elif len(buttons) == 1:
				buttons = "'%s'" % buttons[0]
			else:
				buttons = "'%s'" % ', '.join(["'%s'" % i for i in buttons] )
			isVisible = TableCrabWin32.windowIsVisible(hwnd)
			isEnabled = TableCrabWin32.windowIsEnabled(hwnd)
			
			indent = '\x20\x20\x20\x20' *level
			p = ''
			p += '%sTitle: %s\n' % (indent, title)
			p += '%sClassName: %s\n' % (indent, className)
			p += '%sPos: %s,%s\n' % (indent, pos.x(), pos.y() )
			p += '%sSize: %sx%s\n' % (indent, size.width(), size.height() )
			p += '%sButtons: %s\n' % (indent, buttons)
			p += '%sVisible: %s\n' % (indent, isVisible)
			p += '%sEnabled: %s\n' % (indent, isEnabled)
			p += '%sHwnd: %s\n' % (indent, hwnd)
			return p
			
		self._lastInfo = ''
		self._lastInfo += '-----------------------------------------------------------------\n'
		self._lastInfo += 'Current Window\n'
		self._lastInfo += '-----------------------------------------------------------------\n'
		self._lastInfo += windowInfo(hwnd)
		
		self._lastInfo += '-----------------------------------------------------------------\n'
		self._lastInfo += 'Window Details\n'
		self._lastInfo += '-----------------------------------------------------------------\n'
		for level, hwnd in TableCrabWin32.windowWalkChildren(hwnd, report=True):
			 self._lastInfo += windowInfo(hwnd, level=level)
			
		hwndParent = TableCrabWin32.windowGetTopLevelParent(hwnd)
		if hwndParent == hwnd: return
			
		self._lastInfo += '-----------------------------------------------------------------\n'
		self._lastInfo += 'Window Hirarchy\n'
		self._lastInfo += '-----------------------------------------------------------------\n'
		for level, hwnd in TableCrabWin32.windowWalkChildren(hwndParent, report=True):
			 self._lastInfo += windowInfo(hwnd, level=level)
		
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.scrollArea, 0, 0)
			
	def onActionOpenTriggered(self):
		dlg = QtGui.QFileDialog(self)
		imageFormats = [QtCore.QString(i).toLower() for i in  QtGui.QImageReader.supportedImageFormats()]
		dlg.setFileMode(dlg.AnyFile)
		dlg.setWindowTitle('Open Screenshot..')
		dlg.setAcceptMode(dlg.AcceptOpen)
		filters = QtCore.QStringList()
		filters << 'Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats])
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue(  'Gui/Screenshot/DialogOpen/State', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogOpen/State', dlg.saveState() )
		if result != dlg.Accepted:
			return
			
		fileName = dlg.selectedFiles()[0]
		pixmap = QtGui.QPixmap()
		if not pixmap.load(fileName):
			TableCrabConfig.MsgWarning(self, 'Could not open screenshot')
			return
		
		fileInfo = QtCore.QFileInfo(fileName)
		screenshotName = fileInfo.baseName()
		self.setScreenshot(pixmap=pixmap, screenshotName=screenshotName)
		self._lastInfo = None
		self.adjustActions()
		
	def onActionSaveTriggered(self):
		if self.label.pixmap() is None:
			self.buttonSave.setEnabled(False)
			return
			
		dlg = QtGui.QFileDialog(self)
		dlg.setWindowTitle('Save Screenshot..')
		imageFormats = [QtCore.QString(i).toLower() for i in  QtGui.QImageWriter.supportedImageFormats()]
		dlg.setFileMode(dlg.AnyFile)
		dlg.setAcceptMode(dlg.AcceptSave)
		dlg.setConfirmOverwrite(True)
		filters = QtCore.QStringList()
		filters << 'Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats])
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue('Gui/Screenshot/DialogSave/State', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogSave/State', dlg.saveState() )
		if result != dlg.Accepted:
			return
			
		fileName = dlg.selectedFiles()[0]
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		# default save format to to "png"
		for tmp_format in imageFormats:
			if tmp_format == format:
				break
		else:
			fileName = fileName + '.png'
			format = 'png'
		if not self.label.pixmap().save(fileName, format):
			TableCrabConfig.MsgWarning(self, 'Could Not Save Screenshot')
		
	def onActionInfoTriggered(self):
		if self._lastInfo is None:
			self.actionInfo.setEnabled(False)
			return
		dlg = DialgScreenshotInfo(self._lastInfo, parent=self)
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', QtCore.QByteArray()).toByteArray() )
		dlg.show()
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', dlg.saveGeometry() )
	
	

class DialgScreenshotInfo(QtGui.QDialog):
	def __init__(self, info, parent=None):
		QtGui.QDialog. __init__(self, parent)
		self.edit = QtGui.QPlainTextEdit(self)
		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ApplyRole )
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		TableCrabConfig.signalConnect(self.buttonSave, self, 'clicked(bool)', self.onButtonSaveClicked)
		self.edit.setPlainText(info)
		self.layout()
		
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.edit, 0, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 1, 0)
		grid.addWidget(self.buttonBox, 2, 0)
	def onButtonSaveClicked(self, checked):
		dlg = QtGui.QFileDialog(self)
		dlg.setWindowTitle('Save Screenshot Info..')
		dlg.setFileMode(dlg.AnyFile)
		dlg.setAcceptMode(dlg.AcceptSave)
		dlg.setConfirmOverwrite(True)
		filters = QtCore.QStringList()
		filters << 'TextFiles (*.txt)'
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue('Gui/Screenshot/DialogScreenshotInfo/DialogSave/State', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogScreenshotInfo/DialogSave/State', dlg.saveState() )
		if result != dlg.Accepted:
			return
			
		fileName = dlg.selectedFiles()[0]
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.edit.toPlainText() )
		except Exception, d:
			TableCrabConfig.MsgWarning(self, 'Could Not Save Screenshot Info\n\n%s' % d)
		finally: 
			if fp is not None: fp.close()
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('screenshotInfo', parent=self)
		

class FrameSetup(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self.framePersistentItems = FramePersistentItems(parent=self)
		self.frameTablesScreenshot = FrameTablesScreenshot(parent=self)
		
		self.splitter.addWidget(self.framePersistentItems)
		self.splitter.addWidget(self.frameTablesScreenshot)
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Setup/SplitterState', QtCore.QByteArray()).toByteArray() )
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
		
		self.toolBar = QtGui.QToolBar(self)
		for action in self.framePersistentItems.actions():
			self.toolBar.addAction(action)
		self.toolBar.addSeparator()
		self.toolBar.addSeparator()
		for action in self.frameTablesScreenshot.actions():
			self.toolBar.addAction(action)
		
		self.actionHelp = TableCrabConfig.TableCrabAction(
				parent=self,
				text='Help',
				slot=self.onActionHelpTriggered,
				)
		self.toolBar.addAction(self.actionHelp)
		
		
		self.layout()
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.toolBar, 0, 0)
		box.addWidget(self.splitter, 1, 0)
		
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Setup/SplitterState', self.splitter.saveState())
	
	def onActionHelpTriggered(self):
		TableCrabGuiHelp.dialogHelp('setup', parent=self)

#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	import TableCrabMainWindow
	g = TableCrabMainWindow.MainWindow()
	g.setCentralWidget(FrameSetup(g))
	g.start()
	
	
	