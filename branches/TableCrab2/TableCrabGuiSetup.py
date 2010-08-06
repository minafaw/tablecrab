 
import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp
import TableCrabTemplates

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
class TemplatesWidget(QtGui.QTreeWidget):
	
	class ActionNewTemplate(QtGui.QAction):
		def __init__(self, templateProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.templateProto = templateProto
			self.setText(self.templateProto.menuName() )
			TableCrabConfig.signalConnect(self, self, 'triggered(bool)', self.onTriggered)
		def onTriggered(self):
			self.parent().createTemplate(self.templateProto)
			
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		
		TableCrabConfig.templateManager = self
		
		self.setColumnCount(2)
		self.setExpandsOnDoubleClick(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
		self.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		self.setRootIsDecorated( TableCrabConfig.settingsValue('Gui/ChildItemIndicators', True).toBool() )
		
		self._templatesRead = False
		
		# setup actions
		self._actions = []
		
		menu = QtGui.QMenu(self)
		for templateProto in TableCrabTemplates.Templates:
			menu.addAction(self.ActionNewTemplate(templateProto, parent=self) )
		self.actionNew = TableCrabConfig.Action(
				parent=self,
				text='New',
				menu=menu,
				toolTip='Create a new template',
				)
		self._actions.append(self.actionNew)
		self.actionDown = TableCrabConfig.Action(
				parent=self,
				text='Down',
				toolTip='Move template down',
				slot=self.moveTemplateDown,
				)
		self._actions.append(self.actionDown)
		self.actionUp = TableCrabConfig.Action(
				parent=self,
				text='Up',
				toolTip='Move template up',
				slot=self.moveTemplateUp,
				)
		self._actions.append(self.actionUp)
		self.actionRemove = TableCrabConfig.Action(
				parent=self,
				text='Remove',
				toolTip='Remove template',
				slot=self.removeTemplate,
				)
		self._actions.append(self.actionRemove)
				
		# connect to global signals	
		TableCrabConfig.signalsConnect(None, self,
				('settingAlternatingRowColorsChanged(bool)', self.setAlternatingRowColors),
				('settingChildItemIndicatorsChanged(bool)', self.setRootIsDecorated),
				('widgetScreenshotSet(QPixmap*)', self.onWidgetScreenshotSet),
				('widgetScreenshotDoubleClicked(QPixmap*, QPoint*)', self.onWidgetScreenshotDoubleClicked),
				)
			
		# connect to TreeWidget signals
		TableCrabConfig.signalsConnect(self, self,
				('itemChanged(QTreeWidgetItem*, int)', self.onTreeItemChanged),
				('itemDoubleClicked(QTreeWidgetItem*)',self.editItem),
				('itemExpanded(QTreeWidgetItem*)',self.onItemExpanded),
				('itemCollapsed(QTreeWidgetItem*)',self.onItemCollapsed),
				('itemSelectionChanged()', self.adjustActions),
				)
		self.adjustActions()
		
	def read(self):
		for template in TableCrabConfig.readPersistentItems('Templates', maxItems=TableCrabTemplates.MaxTemplates, itemProtos=TableCrabTemplates.Templates):
			self.addTopLevelItem(template)
			template.setExpanded(template.itemIsExpanded)
		self._templatesRead = True
		TableCrabConfig.signalEmit(None, 'widgetScreenshotQuery()')
		
	def dump(self):
		TableCrabConfig.dumpPersistentItems('Templates', [template for template in self])
	
	def __iter__(self):
		for i in xrange(self.topLevelItemCount()):
			yield self.topLevelItem(i)
	
	def actions(self):
		return self._actions
	
	def adjustActions(self):
		self.actionNew.setEnabled(self.topLevelItemCount() < TableCrabTemplates.MaxTemplates)
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			self.actionDown.setEnabled(False)
			self.actionRemove.setEnabled(False)
		else:
			self.actionUp.setEnabled(self.canMoveTemplateUp() )
			self.actionDown.setEnabled(self.canMoveTemplateDown() )
			self.actionRemove.setEnabled(True)
		
	def onTreeItemChanged(self, item, column):
		if not self._templatesRead:
			return
		if item.toplevel().handleItemChanged(item):
			self.dump()
	
	def onItemExpanded(self, item):
		if not self._templatesRead:
			return
		if item.toplevel().handleItemExpanded(item):
			self.dump()
		
	def onItemCollapsed(self, item):
		if not self._templatesRead:
			return
		if item.toplevel().handleItemCollapsed(item):
			self.dump()
		
	def onWidgetScreenshotSet(self, pixmap):
		for template in self:
			template.handleScreenshotSet(pixmap)
		
	def onWidgetScreenshotDoubleClicked(self, pixmap, point):
		item = self.currentItem()
		if item is None:
			return False
		if item.toplevel().handleScreenshotDoubleClicked(item, pixmap, point):
			self.dump()
	
	def createTemplate(self, templateProto):
		template = templateProto()
		self.addTopLevelItem(template)
		self.setCurrentItem(template)
		template.setExpanded(True)
		self.dump()
		TableCrabConfig.signalEmit(None, 'widgetScreenshotQuery()')
		
	def canMoveTemplateUp(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(item.toplevel() ) > 0
		return False
		
	def moveTemplateUp(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(item.toplevel() )
		template = self.takeTopLevelItem(index)
		self.insertTopLevelItem(index -1, template)
		#NOTE: for some reason Qt collapses items on TakeItem()
		template.setExpanded(template.itemIsExpanded)
		self.setCurrentItem(template)
		self.dump()
		
	def canMoveTemplateDown(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(item.toplevel() ) < self.topLevelItemCount() -1
		return False
	
	def moveTemplateDown(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(item.toplevel() )
		template = self.takeTopLevelItem(index)
		self.insertTopLevelItem(index +1, template)
		#NOTE: for some reason Qt collapses items on TakeItem()
		template.setExpanded(template.itemIsExpanded)
		self.setCurrentItem(template)
		self.dump()
	
	def removeTemplate(self):
		item = self.currentItem()
		if item is None:
			self.actionRemove.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(item.toplevel() )
		self.takeTopLevelItem(index)
		self.dump()

	
class ScreenshotWidget(QtGui.QScrollArea):
	
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
		QtGui.QScrollArea.__init__(self, parent)
		
		self._lastInfo = None
		
		self.label = self.MyLabel('Screenshot')
		self.label.setScaledContents(True)
		self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		
		self.setBackgroundRole(QtGui.QPalette.Dark)
		self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.setWidget(self.label)		

		# setup actions
		self._actions = []
		
		self.actionOpen = TableCrabConfig.Action(
				parent=self,
				text='Open screenshot..',
				toolTip='Open a screenshot from file',
				slot=self.onActionOpenTriggered,
				)
		self._actions.append(self.actionOpen)
		
		self.actionSave = TableCrabConfig.Action(
				parent=self,
				text='Save screenshot..',
				toolTip='Save screenshot to file',
				slot=self.onActionSaveTriggered,
				)
		self._actions.append(self.actionSave)
		
		self.actionInfo = TableCrabConfig.Action(
				parent=self,
				text='Info..',
				toolTip='Detailed screenshot information',
				slot=self.onActionInfoTriggered,
				)
		self._actions.append(self.actionInfo)
			
		# connect global signals
		TableCrabConfig.signalsConnect(None, self, 
				('widgetScreenshotQuery()', self.onWidgetScreenshotQuery),
				('widgetScreenshot(int, QPixmap*)', self.onWidgetScreenshot),
				)
				
		self.adjustActions()
		
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
			
	def onActionOpenTriggered(self):
		imageFormats = [QtCore.QString(i).toLower() for i in  QtGui.QImageReader.supportedImageFormats()]
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Screenshot..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'), 
				settingsKey='Gui/Screenshot/DialogOpen/State',
				)
		if fileName is None:
			return
		pixmap = QtGui.QPixmap()
		if not pixmap.load(fileName):
			TableCrabConfig.msgWarning(self, 'Could not open screenshot')
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
		imageFormats = [QtCore.QString(i).toLower() for i in  QtGui.QImageWriter.supportedImageFormats()]
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Screenshot..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'), 
				settingsKey='Gui/Screenshot/DialogSave/State',
				)
		if fileName is None:
			return
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
			TableCrabConfig.msgWarning(self, 'Could Not Save Screenshot')
		
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
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Screenshot Info..',
				fileFilters=('TextFiles (*.txt)', 'All Files (*)'), 
				settingsKey='Gui/Screenshot/DialogScreenshotInfo/DialogSave/State',
				)
		if fileName is None:
			return
		# default to '.txt'
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not format:
			fileName = fileName + '.txt'
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.edit.toPlainText() )
		except Exception, d:
			TableCrabConfig.msgWarning(self, 'Could Not Save Screenshot Info\n\n%s' % d)
		finally: 
			if fp is not None: fp.close()
		
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('screenshotInfo', parent=self)
		

class FrameSetup(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self.templatesWidget = TemplatesWidget(parent=self)
		self.screenshotWidget =ScreenshotWidget(parent=self)
		
		self.splitter.addWidget(self.templatesWidget)
		self.splitter.addWidget(self.screenshotWidget)
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Setup/SplitterState', QtCore.QByteArray()).toByteArray() )
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
		
		self.toolBar = QtGui.QToolBar(self)
		for action in self.templatesWidget.actions():
			self.toolBar.addAction(action)
		self.toolBar.addSeparator()
		self.toolBar.addSeparator()
		for action in self.screenshotWidget.actions():
			self.toolBar.addAction(action)
		
		self.actionHelp = TableCrabConfig.Action(
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
	
	
	