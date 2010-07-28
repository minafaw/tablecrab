
import TableCrabConfig
from PyQt4 import QtCore, QtGui

import TableCrabGuiHelp

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
	def __init__(self, widgetItem, parent=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.widgetItem = widgetItem
		self.attrName = 'name'
		self.setText(0, self.widgetItem.name)
		self.setFirstColumnSpanned(True)
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
		self.setIcon(0, QtGui.QIcon(TableCrabConfig.Pixmaps.stars()) )
		font = self.font(0)
		font.setBold(True)
		self.setFont(0, font)
		if widgetItem.itemIsExpanded:
			self.setExpanded(True)
		self.myChildren = {
				'itemName': ChildItem('itemName', 'Window:', self.widgetItem.itemName(), parent=self),
				'size': ChildItem('size', 'Size:', TableCrabConfig.sizeToString(self.widgetItem.size), parent=self),
				'buttonCheck': ChildItem('buttonCheck', 'ButtonCheck:', TableCrabConfig.pointToString(self.widgetItem.buttonCheck), parent=self),
				'buttonFold': ChildItem('buttonFold', 'ButtonFold:', TableCrabConfig.pointToString(self.widgetItem.buttonFold), parent=self),
				'buttonRaise': ChildItem('buttonRaise', 'ButtonRaise:', TableCrabConfig.pointToString(self.widgetItem.buttonRaise), parent=self),
				'checkboxFold': ChildItem('checkboxFold', 'CheckboxFold:', TableCrabConfig.pointToString(self.widgetItem.checkboxFold), parent=self),
				'instantHandHistory': ChildItem('instantHandHistory', 'InstantHandHistory:', TableCrabConfig.pointToString(self.widgetItem.instantHandHistory), parent=self),
				'replayer': ChildItem('replayer', 'Replayer:', TableCrabConfig.pointToString(self.widgetItem.replayer), parent=self),
				}
		
		TableCrabConfig.signalConnect(None, self.widgetItem, 'widgetScreenshotSet(int, int)', self.onWidgetScreenshotSet)
		TableCrabConfig.signalConnect(self.widgetItem, self.widgetItem, 'attributeValueChanged(QString)', self.onWidgetItemAttributeValueChanged)
		TableCrabConfig.signalConnect(self.widgetItem, self.widgetItem, 'itemMovedUp(QObject*, int)', self.onWidgetItemMovedUp)
		TableCrabConfig.signalConnect(self.widgetItem, self.widgetItem, 'itemMovedDown(QObject*, int)', self.onWidgetItemMovedDown)
		TableCrabConfig.signalConnect(self.widgetItem, self.widgetItem, 'itemRemoved(QObject*)', self.onWidgetItemRemoved)
		
		#TODO: bit of a hack here to disable child items initially
		self.onWidgetScreenshotSet(-9, -9)
		
	
	def childItem(self, attrName):
		for index in xrange(self.childCount()):
			child = self.child(index)
			attr = child.data(0, QtCore.Qt.UserRole).toString()
			if attr == attrName:
				return child
		raise valueError('nosuch child: %s' % attrName)
		
	def onWidgetItemMovedUp(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
		self.setExpanded(True)
	def onWidgetItemMovedDown(self, action, index):
		treeWidget = self.treeWidget()
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
		treeWidget.insertTopLevelItem(index, self)
		treeWidget.setCurrentItem(self)
		self.setExpanded(True)
	def onWidgetItemRemoved(self, action):
		treeWidget = self.treeWidget()
		self.widgetItem = None
		treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(self))
	def onWidgetItemAttributeValueChanged(self, attrName):
		attrName = str(attrName)	#NOTE: we can not pass python strings, so we have to type convert here
		if attrName == 'name':
			self.setText(0, self.widgetItem.name)
		elif attrName == 'itemName':
			child = self.myChildren[attrName]
			child.setText(1,self.widgetItem.itemName() )
		elif attrName == 'size':
			child = self.myChildren[attrName]
			child.setText(1, TableCrabConfig.sizeToString(self.widgetItem.size))
		elif attrName == 'itemIsExpanded':
			pass
		else:
			child = self.myChildren[attrName]
			child.setText(1, TableCrabConfig.pointToString( getattr(self.widgetItem, attrName) ) )
	def onWidgetScreenshotSet(self, w, h):
		hasScreenshot = w > -1 and  h > -1
		size = (w, h)
		mySize = (self.widgetItem.size.width(), self.widgetItem.size.height())
		sizeNone = (-1, -1)
		for child in self.myChildren.values():
			if not hasScreenshot:
				child.setDisabled(True)
			elif mySize == size:
				child.setDisabled(False)
			elif mySize == sizeNone:
				child.setDisabled(False)
			else:
				child.setDisabled(True)
	

class WidgetItemTreeWidget(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		##self.setAlternatingRowColors(True)
		self.setColumnCount(2)
		self.setExpandsOnDoubleClick(False)
		self.setRootIsDecorated(False)
		self.header().setVisible(False)
		self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
			
		#NOTE: we have to connect after adding the initial tables cos QTreeWidget informs us about every* itemChange
		TableCrabConfig.signalConnect(TableCrabConfig.widgetItemManager, self, 'itemRead(QObject*)', self.onWidgetItemManagerItemRead)
		TableCrabConfig.signalConnect(self, self, 'itemChanged(QTreeWidgetItem*, int)', self.onTreeItemChanged)
		TableCrabConfig.signalConnect(self, self, 'itemDoubleClicked(QListWidgetItem*)',self.editItem)
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
	def onWidgetItemAdded(self, widgetItem):
		item = TablePokerStarsTreeWidgetItem(widgetItem, parent=self)
		self.addTopLevelItem(item)
		self.setCurrentItem(item)
	def onTreeItemChanged(self, item, column):
		if item.attrName == 'name':
			if item.text(0) != item.widgetItem.name:	#NOTE: special handling for in-place editing
				item.widgetItem.name = item.text(0)
		TableCrabConfig.widgetItemManager.dump()
	def onWidgetItemManagerItemRead(self, widgetItem):
		item = TablePokerStarsTreeWidgetItem(widgetItem, parent=self)
		self.addTopLevelItem(item)
	def onItemExpanded(self, item):
		item.widgetItem.itemIsExpanded = True
		TableCrabConfig.widgetItemManager.dump()
	def onItemCollapsed(self, item):
		item.widgetItem.itemIsExpanded = False
		TableCrabConfig.widgetItemManager.dump()	
	def createWidgetItem(self, widgetItemProto):
		widgetItem = widgetItemProto(name=widgetItemProto.itemName())
		TableCrabConfig.signalConnect(widgetItem, self, 'itemAdded(QObject*)', self.onWidgetItemAdded)
		TableCrabConfig.widgetItemManager.addItem(widgetItem)
	

class FrameWidgetItems(QtGui.QFrame):
	
	class ActionNewWidgetItem(QtGui.QAction):
		def __init__(self, widgetItemProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.widgetItemProto = widgetItemProto
			self.setText(self.widgetItemProto.itemName())
			
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.widgetItemTreeWidget = WidgetItemTreeWidget(self)
		self.buttonUp = QtGui.QPushButton('Up', self)
		self.buttonDown = QtGui.QPushButton('Down', self)
		self.buttonNew = QtGui.QPushButton('New', self)
		self.buttonRemove = QtGui.QPushButton('Remove', self)
		self.menuNewWidgetItem = QtGui.QMenu(self)
		
		#
		for widgetItemProto in TableCrabConfig.WidgetItems:
			widgetItem = self.ActionNewWidgetItem(widgetItemProto, parent=self)
			TableCrabConfig.signalConnect(widgetItem, self, 'triggered(bool)', self.onWidgetItemNewTriggered)
			self.menuNewWidgetItem.addAction(widgetItem)
		self.buttonNew.setMenu(self.menuNewWidgetItem)
			
		#
		TableCrabConfig.signalConnect(None, self, 'widgetScreenshotDoubleClicked(QSize*, QPoint*)', self.onWidgetScreenshotDoubleClicked)
		TableCrabConfig.signalConnect(self.widgetItemTreeWidget, self, 'itemSelectionChanged()', self.onTreeItemSelectionChanged)
		TableCrabConfig.signalConnect(self.buttonUp, self, 'clicked(bool)', self.onButtonUpClicked)
		TableCrabConfig.signalConnect(self.buttonDown, self, 'clicked(bool)', self.onButtonDownClicked)
		self.buttonNew.setEnabled(TableCrabConfig.widgetItemManager.canAddItem() )
		TableCrabConfig.signalConnect(self.buttonRemove, self, 'clicked(bool)', self.onButtonRemoveClicked)
		
		self._adjustButtons()
		self.layout()
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.widgetItemTreeWidget, 0, 0, 1, 2)
		box.addWidget(self.buttonNew, 1, 0)
		box.addWidget(self.buttonRemove, 2, 0)
		box.addWidget(self.buttonUp, 1, 1)
		box.addWidget(self.buttonDown, 2, 1)
	
	def onWidgetScreenshotDoubleClicked(self, size, point):
		item = self.widgetItemTreeWidget.currentItem()
		if item is None:
			return False
		widgetItem= item.widgetItem if item.parent() is None else item.parent().widgetItem
		if type(getattr(widgetItem, item.attrName)) != QtCore.QPoint:
			return False
		if widgetItem.size.isEmpty():
			widgetItem.size = size
		elif widgetItem.size != size:
			return False
		setattr(widgetItem, item.attrName, point)
		return True
		
	def onButtonUpClicked(self, checked):
		item = self.widgetItemTreeWidget.currentItem()
		if item is None:
			self.buttonUp.setEnabled(False)
			return
		widgetItem= item.widgetItem if item.parent() is None else item.parent().widgetItem
		TableCrabConfig.widgetItemManager.moveItemUp(widgetItem)
	
	def onButtonDownClicked(self, checked):
		item = self.widgetItemTreeWidget.currentItem()
		if item is None:
			self.buttonDown.setEnabled(False)
			return
		widgetItem= item.widgetItem if item.parent() is None else item.parent().widgetItem
		TableCrabConfig.widgetItemManager.moveItemDown(widgetItem)
	
	def onButtonRemoveClicked(self, checked):
		item = self.widgetItemTreeWidget.currentItem()
		if item is None:
			self.buttonRemove.setEnabled(False)
			return
		widgetItem= item.widgetItem if item.parent() is None else item.parent().widgetItem
		TableCrabConfig.widgetItemManager.removeItem(widgetItem)
		
	def onTreeItemSelectionChanged(self):
		self._adjustButtons()
	
	def _adjustButtons(self):
		item = self.widgetItemTreeWidget.currentItem()
		if item is None:
			widgetItem = None
		elif item.parent() is None:
			widgetItem = item.widgetItem
		else:
			widgetItem = item.parent().widgetItem
		if widgetItem is None:
			self.buttonUp.setEnabled(False)
			self.buttonDown.setEnabled(False)
			self.buttonRemove.setEnabled(False)
		else:
			self.buttonUp.setEnabled(TableCrabConfig.widgetItemManager.canMoveItemUp(widgetItem) )
			self.buttonDown.setEnabled(TableCrabConfig.widgetItemManager.canMoveItemDown(widgetItem) )
			self.buttonRemove.setEnabled(True)
		
	def onWidgetItemNewTriggered(self, checked):
		self.widgetItemTreeWidget.createWidgetItem(self.sender().widgetItemProto)
		
		
class FrameTablesScreenshot(QtGui.QFrame):
	
	class MyLabel(QtGui.QLabel):
		def mouseDoubleClickEvent(self, event):
			if event.button() == QtCore.Qt.LeftButton:
				#TODO: check if the point is client cordinates of the label
				px = self.pixmap()
				if px is not None:
					TableCrabConfig.signalEmit(None, 'widgetScreenshotDoubleClicked(QSize*, QPoint*)', px.size(), event.pos())
				return QtGui.QLabel.mouseDoubleClickEvent(self, event)
	
	
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.scrollArea = QtGui.QScrollArea(self)
		self.label = self.MyLabel('Screenshot')
		self.buttonOpen = QtGui.QPushButton('Open..', self)
		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonInfo = QtGui.QPushButton('Info..', self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonOpen, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonInfo, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)	
			
		self.lastInfo = None
		
		TableCrabConfig.signalConnect(None, self, 'windowScreenshot(int, QPixmap*)', self.onWindowScreenshot)
		self.buttonSave.setEnabled(False)
		TableCrabConfig.signalConnect(self.buttonOpen, self, 'clicked(bool)', self.onButtonOpenClicked)
		TableCrabConfig.signalConnect(self.buttonSave, self, 'clicked(bool)', self.onButtonSaveClicked)
		TableCrabConfig.signalConnect(self.buttonInfo, self, 'clicked(bool)', self.onButtonInfoClicked)
		self.buttonInfo.setEnabled(False)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
				
		self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.scrollArea.setWidget(self.label)
		self.layout()
		
	def onWindowScreenshot(self, hwnd, pixmap):
		# make shure to not take screenshot of self
		selfHwnd = int(self.effectiveWinId())	# NOTE: effectiveWinId() returns <sip.voidptr>
		selfParent = TableCrabConfig.windowGetTopLevelParent(selfHwnd)
		otherParent = TableCrabConfig.windowGetTopLevelParent(hwnd)
		if selfParent == otherParent:
			return
		self.label.setPixmap(pixmap)
		self.buttonSave.setEnabled(True)
		self.gatherWindowInfo(hwnd)		
		self.buttonInfo.setEnabled(True)
		# emit global signal
		w, h = pixmap.width(), pixmap.height()
		TableCrabConfig.signalEmit(None, 'widgetScreenshotSet(int, int)', w, h)
		
		
	def 	gatherWindowInfo(self, hwnd):
		def windowInfo(hwnd, level=0):
			title = TableCrabConfig.windowGetText(hwnd).replace('\r', '')
			if '\n' in title: title = title.split('\n', 1)[0]
			className = TableCrabConfig.windowGetClassName(hwnd)
			buttons = sorted( TableCrabConfig.windowGetButtons(hwnd).keys() )
			if not buttons:
				buttons = ''
			elif len(buttons) == 1:
				buttons = "'%s'" % buttons[0]
			else:
				buttons = "'%s'" % ', '.join(["'%s'" % i for i in buttons] )
			isVisible = TableCrabConfig.windowIsVisible(hwnd)
			isEnabled = TableCrabConfig.windowIsEnabled(hwnd)
			
			indent = '\x20\x20\x20\x20' *level
			p = ''
			p += '%sTitle: %s\n' % (indent, title)
			p += '%sClassName: %s\n' % (indent, className)
			p += '%sButtons: %s\n' % (indent, buttons)
			p += '%sVisible: %s\n' % (indent, isVisible)
			p += '%sEnabled: %s\n' % (indent, isEnabled)
			p += '%sHwnd: %s\n' % (indent, hwnd)
			return p
			
		self.lastInfo = ''
		self.lastInfo += '-----------------------------------------------------------------\n'
		self.lastInfo += 'Current Window\n'
		self.lastInfo += '-----------------------------------------------------------------\n'
		self.lastInfo += windowInfo(hwnd)
		
		self.lastInfo += '-----------------------------------------------------------------\n'
		self.lastInfo += 'Window Details\n'
		self.lastInfo += '-----------------------------------------------------------------\n'
		for level, hwnd in TableCrabConfig.windowWalkChildren(hwnd, report=True):
			 self.lastInfo += windowInfo(hwnd, level=level)
			
		hwndParent = TableCrabConfig.windowGetTopLevelParent(hwnd)
		if hwndParent == hwnd: return
			
		self.lastInfo += '-----------------------------------------------------------------\n'
		self.lastInfo += 'Window Hirarchy\n'
		self.lastInfo += '-----------------------------------------------------------------\n'
		for level, hwnd in TableCrabConfig.windowWalkChildren(hwndParent, report=True):
			 self.lastInfo += windowInfo(hwnd, level=level)
		
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.scrollArea, 0, 0)
		box.addWidget(self.buttonBox, 1, 0)
		
	def onButtonOpenClicked(self, checked):
		dlg = QtGui.QFileDialog(self)
		imageFormats = [QtCore.QString(i).toLower() for i in  QtGui.QImageReader.supportedImageFormats()]
		dlg.setFileMode(dlg.AnyFile)
		dlg.setWindowTitle('Open Screenshot..')
		dlg.setAcceptMode(dlg.AcceptOpen)
		filters = QtCore.QStringList()
		filters << 'Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats])
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue(  'Gui/Screenshot/DialogOpenState', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogOpenState', dlg.saveState() )
		if result != dlg.Accepted:
			return
			
		fileName = dlg.selectedFiles()[0]
		pixmap = QtGui.QPixmap()
		if not pixmap.load(fileName):
			TableCrabConfig.MsgWarning(self, 'Could not open screenshot')
			return
		self.label.setPixmap(pixmap)
		self.buttonSave.setEnabled(True)
		
	def onButtonSaveClicked(self, checked):
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
		for tmp_format in imageFormats:
			if tmp_format == format:
				break
		else:
			format = 'png'
		if not self.label.pixmap().save(fileName, format):
			TableCrabConfig.MsgWarning(self, 'Could Not Save Screenshot')
		
	def onButtonInfoClicked(self, checked):
		if self.lastInfo is None:
			self.buttonInfo.setEnabled(False)
			return
		dlg = DialgScreenshotInfo(self.lastInfo, parent=self)
		dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', QtCore.QByteArray()).toByteArray() )
		dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', dlg.saveGeometry() )
	
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('widgets', parent=self)

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
		

class FrameWidgets(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self.frameWidgetItems = FrameWidgetItems(parent=self)
		self.frameTablesScreenshot = FrameTablesScreenshot(parent=self)
		
		self.splitter.addWidget(self.frameWidgetItems)
		self.splitter.addWidget(self.frameTablesScreenshot)
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Widgets/SplitterState', QtCore.QByteArray()).toByteArray() )
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
		
		self.layout()
	def layout(self):
		hbox = TableCrabConfig.HBox(self)
		hbox.addWidget(self.splitter)
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Widgets/SplitterState', self.splitter.saveState())

#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	g = TableCrabConfig.MainWindow()
	g.setCentralWidget(FrameWidgets(g))
	g.start()
	
	
	