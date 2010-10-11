
#TODO: would be nice to have some information on how many templates are left until hitting MaxTemplates
#TODO: i kind of dislike in-place editing of template names. an "Edit" button would be more consistent but a bit of overkill right now. then .again .screenshot
# 			open / save is taking away screenspace already. would have to find shorter names for these actions.
#TODO: restore last selected template on restart?

import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp
import TableCrabTemplates

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
class DialgScreenshotInfo(QtGui.QDialog):
	def __init__(self, info, parent=None):
		QtGui.QDialog. __init__(self, parent)
		self.setWindowTitle(TableCrabConfig.dialogTitle('Screenshot Info') )

		self._lastScreenshotInfo = info

		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setPlainText(info)
		self.edit.setReadOnly(True)

		self.buttonRefresh = QtGui.QPushButton('Refresh', self)
		self.buttonRefresh.clicked.connect(self.onRefresh)
		self.buttonRefresh.setToolTip('Save info (Ctrl+R)')

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+R') )
		action.triggered.connect(self.onRefresh)
		self.addAction(action)

		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonSave.setToolTip('Save info (Ctrl+S)')
		self.buttonSave.clicked.connect(self.onSave)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+S') )
		action.triggered.connect(self.onSave)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		self.buttonBox.addButton(self.buttonRefresh, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ApplyRole )
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		self.buttonBox.accepted.connect(self.accept)

		parent.widgetScreenshotInfo.connect(self.onWidgetScreenshotInfo)

		self.layout()
		self.restoreGeometry( TableCrabConfig.settingsValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', QtCore.QByteArray()).toByteArray() )

	#----------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#---------------------------------------------------------------------------------------------------------------
	def hideEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', self.saveGeometry() )
		QtGui.QDialog.hideEvent(self, event)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.edit)
		grid.row()
		grid.col(TableCrabConfig.HLine(self))
		grid.row()
		grid.col(self.buttonBox)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('screenshotInfo', parent=self)

	def onRefresh(self, *args):
		self.edit.setPlainText(self._lastScreenshotInfo)

	def onSave(self, *args):
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

	def onWidgetScreenshotInfo(self, info):
		self._lastScreenshotInfo = info
		self.buttonRefresh.setEnabled(bool(info))

#**********************************************************************************************
#
#**********************************************************************************************
class TemplatesWidget(QtGui.QTreeWidget):

	class MyDelegate(QtGui.QStyledItemDelegate):
		editingFinished = QtCore.pyqtSignal()

		def __init__(self, parent=None):
			QtGui.QStyledItemDelegate.__init__(self, parent)

			#NOTE: bit of a hack here. hitting <return> on edit ends editing, triggers
			# editingFinished() and propagates the KeyEvent to the parent. this gets us
			# into trouble one of our edit triggers is <return>. parent hast to clear this
			# flag to not retrigger editing (!!) this hack is broken if Qt stops propagating
			# <return> to parent. indicator: <return> triggers editing one time and then stops
			# working as a trigger.
			self.edReturnPressed= False

		def createEditor(self, parent, option, index):
			ed = QtGui.QLineEdit(parent)
			ed.setMaxLength(TableCrabConfig.MaxName)
			ed.editingFinished.connect(self.onEditingFinished)
			ed.returnPressed.connect(self.onEdReturnPressed)
			return ed
		def onEditingFinished(self):
			self.editingFinished.emit()
		def onEdReturnPressed(self):
			self.edReturnPressed= True

	class ActionNewTemplate(QtGui.QAction):
		def __init__(self, templateProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.templateProto = templateProto
			self.setText(self.templateProto.menuName() )
			self.setShortcut(self.templateProto.shortcut() )
			self, self.triggered.connect(self.onTriggered)
		def onTriggered(self):
			self.parent().createTemplate(self.templateProto)


	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)

		#TODO: find a better way to set template manager as global
		TableCrabConfig.templateManager = self

		# setup treeWidget
		self.setUniformRowHeights(True)
		self.setColumnCount(2)
		self.setExpandsOnDoubleClick(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)

		self.myDelegate = self.MyDelegate(parent=self)
		self.setItemDelegate(self.myDelegate)

		self._templatesRead = False
		self._screenshotSize = None	#  QSize

		# setup actions
		self._actions = []

		menu = QtGui.QMenu(self)
		for templateProto in TableCrabTemplates.Templates:
			menu.addAction(self.ActionNewTemplate(templateProto, parent=self) )

		self.actionNew = QtGui.QAction(self)
		self.actionNew.setText('New')
		self.actionNew.setToolTip('Create a new template')
		self.actionNew.setMenu(menu)
		self._actions.append(self.actionNew)

		self.actionUp = QtGui.QAction(self)
		self.actionUp.setText('Up')
		self.actionUp.setToolTip('Move template up (Alt+Up)')
		self.actionUp.setShortcut(QtGui.QKeySequence('Alt+Up') )
		self.actionUp.triggered.connect(self.moveTemplateUp)
		self._actions.append(self.actionUp)

		self.actionDown = QtGui.QAction(self)
		self.actionDown.setText('Down')
		self.actionDown.setToolTip('Move template down (Alt+Down)')
		self.actionDown.setShortcut(QtGui.QKeySequence('Alt+Down') )
		self.actionDown.triggered.connect(self.moveTemplateDown)
		self._actions.append(self.actionDown)

		self.actionRemove = QtGui.QAction(self)
		self.actionRemove.setText('Remove')
		self.actionRemove.setToolTip('Remove template (Alt+Del)')
		self.actionRemove.setShortcut(QtGui.QKeySequence('Alt+Del') )
		self.actionRemove.triggered.connect(self.removeTemplate)
		self._actions.append(self.actionRemove)

		# connect signals
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSetAlternatingRowColors)
		TableCrabConfig.globalObject.settingChildItemIndicatorsChanged.connect(self.onSetRootIsDecorated)
		TableCrabConfig.globalObject.widgetScreenshotSet.connect(self.onWidgetScreenshotSet)
		TableCrabConfig.globalObject.widgetScreenshotDoubleClicked.connect(self.onWidgetScreenshotDoubleClicked)

		# connect to TreeWidget signals
		TableCrabConfig.globalObject.init.connect(self.onInit)
		self.itemDoubleClicked.connect(self.onEditItem)
		self.itemExpanded.connect(self.onItemExpanded)
		self.itemCollapsed.connect(self.onItemCollapsed)
		self.itemSelectionChanged.connect(self.adjustActions)

		# connect to ietm delegate signals
		self.myDelegate.editingFinished.connect(self.onTemplateEditingFinished)

		self.adjustActions()

	#----------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#---------------------------------------------------------------------------------------------------------------

	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			if self.myDelegate.edReturnPressed:
				self.myDelegate.edReturnPressed = False
			else:
				event.accept()
				item = self.currentItem()
				if item is not None:
					if item.toplevel() is item:
						self.editItem(item)
					return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def __iter__(self):
		for i in xrange(len(self)):
			yield self.topLevelItem(i)

	def __len__(self):
		return self.topLevelItemCount()

	def actions(self):
		return self._actions

	def adjustActions(self):
		self.actionNew.setEnabled(len(self) < TableCrabConfig.MaxTemplates)
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			self.actionDown.setEnabled(False)
			self.actionRemove.setEnabled(False)
		else:
			self.actionUp.setEnabled(self.canMoveTemplateUp() )
			self.actionDown.setEnabled(self.canMoveTemplateDown() )
			self.actionRemove.setEnabled(True)

	#TODO: there is a is a bug in Qt4.6.2. last items text(1) is never updated.
	#			[http://bugreports.qt.nokia.com/browse/QTBUG-4849]
	# looks like there is no way to workaround. tried removing / reinsterting items
	# but this runs into more bugs, resulting in loosing templates on certain occasions
	#
	# test is: open screenshot, create new item. this items flag is never set to '//Edit//'
	# move item up --> flag gets shown. guess its best to leave it as is and wait for Qt
	# fixing bugs.
	def adjustTemplates(self):
		self.setUpdatesEnabled(False)

		tmp_templates = {}
		for template in self:
			id = template.id()
			size = template.size
			templateType = '%s-%sx%s' % (id, template.size.width(), template.size.height())
			if templateType not in tmp_templates:
				tmp_templates[templateType] = [template]
			else:
				tmp_templates[templateType].append(template)

		for templateType, templates in tmp_templates.items():
			conflicts = [i for i in templates if i.size != TableCrabConfig.SizeNone]
			for template in templates:
				flag = 'Conflict' if len(conflicts) > 1 else None
				if flag is None:
					if self._screenshotSize == TableCrabConfig.SizeNone:
						pass
					elif template.size == TableCrabConfig.SizeNone:
						flag = 'Edit'
					elif template.size == self._screenshotSize:
						flag = 'Edit'
					else:
						pass
				if flag is None:
					template.setText(1, '')
				else:
					template.setText(1, '//%s//' % flag)

		self.setUpdatesEnabled(True)

	def canMoveTemplateUp(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(item.toplevel() ) > 0
		return False

	def canMoveTemplateDown(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(item.toplevel() ) < len(self) -1
		return False

	def createTemplate(self, templateProto):
		names = [i.name for i in self]
		name = templateProto.menuName()
		name = TableCrabConfig.uniqueName(name, names)
		template = templateProto(parent=self, name=name)
		self.addTopLevelItem(template)
		self.setCurrentItem(template)
		template.setExpanded(True)
		self.dump()
		TableCrabConfig.globalObject.widgetScreenshotQuery.emit()

	def dump(self):
		TableCrabConfig.dumpPersistentItems('Templates', self)

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

	def removeTemplate(self):
		item = self.currentItem()
		if item is None:
			self.actionRemove.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(item.toplevel() )
		self.takeTopLevelItem(index)
		self.dump()
		self.adjustTemplates()

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onEditItem(self, item):
		self.editItem(item)

	def onInit(self):
		self.setUpdatesEnabled(False)
		self.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		self.setRootIsDecorated( TableCrabConfig.settingsValue('Gui/ChildItemIndicators', True).toBool() )
		self.clear()
		template = None
		for template in TableCrabConfig.readPersistentItems('Templates', maxItems=TableCrabConfig.MaxTemplates, itemProtos=TableCrabTemplates.Templates):
			self.addTopLevelItem(template)
			template.setExpanded(template.itemIsExpanded)
		# set at least one template as default
		if template is None:
			template = TableCrabTemplates.TemplatePokerStarsTable()
			self.addTopLevelItem(template)
			template.setExpanded(True)
		self._templatesRead = True
		self.setCurrentItem( self.topLevelItem(0) )
		self.setUpdatesEnabled(True)
		TableCrabConfig.globalObject.widgetScreenshotQuery.emit()

	def onItemCollapsed(self, item):
		if not self._templatesRead:
			return
		if item.toplevel().handleItemCollapsed(item):
			self.dump()

	def onItemExpanded(self, item):
		if not self._templatesRead:
			return
		if item.toplevel().handleItemExpanded(item):
			self.dump()

	def onSetAlternatingRowColors(self, flag):
		self.setAlternatingRowColors(flag)

	def onSetRootIsDecorated(self, flag):
		self.setRootIsDecorated(flag)

	def onTemplateEditingFinished(self):
		item = self.currentItem()
		if item is not None:
			if item.toplevel().handleEditingFinished(item):
				self.dump()

	def onWidgetScreenshotDoubleClicked(self, pixmap, point):
		item = self.currentItem()
		if item is None:
			return False
		if item.toplevel().handleScreenshotDoubleClicked(item, pixmap, point):
			self.dump()
			self.adjustTemplates()

	def onWidgetScreenshotSet(self, pixmap):
		for template in self:
			template.handleScreenshotSet(pixmap)
		self._screenshotSize = TableCrabConfig.newSizeNone() if pixmap.isNull() else QtCore.QSize(pixmap.size())
		self.adjustTemplates()

#**********************************************************************************************
#
#**********************************************************************************************
class ScreenshotLabel(QtGui.QLabel):

	class MyEventFilter(QtCore.QObject):
		mouseLeave = QtCore.pyqtSignal()
		def eventFilter(self, obj, event):
			if event.type() == event.Leave:
				self.mouseLeave.emit()
			return QtCore.QObject.eventFilter(self, obj, event)

	ScreenshotName = 'Screenshot'
	def __init__(self, *args):
		QtGui.QLabel.__init__(self, *args)
		self.setMouseTracking(True)
		self._screenshotName = self.ScreenshotName
		self.eventFilter = self.MyEventFilter()
		self.installEventFilter(self.eventFilter)
		self.eventFilter.mouseLeave.connect(self.onMouseLeave)

	#--------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#--------------------------------------------------------------------------------------------------------------
	def mouseDoubleClickEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			pixmap = self.pixmap()
			if pixmap is not None and not pixmap.isNull():
				# holding sown Ctrl while double clicking rests the point
				if event.modifiers() & QtCore.Qt.ControlModifier:
					point = TableCrabConfig.newPointNone()
				else:
					point = QtCore.QPoint(event.pos())
				TableCrabConfig.globalObject.widgetScreenshotDoubleClicked.emit(pixmap, point)

	def mouseMoveEvent(self, event):
		pixmap = self.pixmap()
		if pixmap is not None and not pixmap.isNull():
			self._giveFeedback(pixmap, event.pos())

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def _giveFeedback(self, pixmap, point):
		name = TableCrabConfig.truncateString(self._screenshotName, TableCrabConfig.MaxName)
		p = '%s -- Size: %s Mouse: %s' % (name, TableCrabConfig.sizeToString(pixmap.size()), TableCrabConfig.pointToString(point) )
		TableCrabConfig.globalObject.feedback.emit(self, p)

	def setScreenshot(self, pixmap=None, screenshotName=None):
		self._screenshotName = self.ScreenshotName if screenshotName is None else screenshotName
		result = False
		if pixmap is None:
			self.setScaledContents(True)
			self.setText(self._screenshotName)
			self.resize(self.parent().size())		#TODO: no idea why but we need to resize here
			self.setFrameShape(QtGui.QFrame.NoFrame)
			pixmap = QtGui.QPixmap()
			TableCrabConfig.globalObject.widgetScreenshotSet.emit(pixmap)
			TableCrabConfig.globalObject.feedback.emit(self, '')
		else:
			# manually set size of the label so we get the correct coordiantes of the mouse cursor
			self.setPixmap(pixmap)
			self.setScaledContents(False)
			self.resize(pixmap.size())
			self.setFrameShape(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
			point = QtGui.QCursor.pos()
			point = self.mapFromGlobal(point)
			if point.x() < 0 or point.y() < 0:
				point = QtCore.QPoint()
			TableCrabConfig.globalObject.widgetScreenshotSet.emit(pixmap)
			self._giveFeedback(pixmap,  point)
			result = True
		return result

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onMouseLeave(self):
		pixmap = self.pixmap()
		if pixmap is not None and not pixmap.isNull():
			point = TableCrabConfig.newPointNone()
			self._giveFeedback(pixmap, point)


class ScreenshotWidget(QtGui.QScrollArea):

	widgetScreenshotInfo = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self, parent=None):
		QtGui.QScrollArea.__init__(self, parent)

		self._lastScreenshotInfo = None

		self.label = ScreenshotLabel(self)
		self.label.setScreenshot(pixmap=None)
		self.setBackgroundRole(QtGui.QPalette.Dark)
		self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.setWidget(self.label)

		# setup actions
		self._actions = []

		self.actionOpen = QtGui.QAction(self)
		self.actionOpen.setText('Open screenshot..')
		self.actionOpen.setToolTip('Open a screenshot from file (Alt+O)')
		self.actionOpen.setShortcut(QtGui.QKeySequence('Alt+O') )
		self.actionOpen.triggered.connect(self.onActionOpenTriggered)
		self._actions.append(self.actionOpen)

		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save screenshot..')
		self.actionSave.setToolTip('Save screenshot to file (Alt+S)')
		self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		self._actions.append(self.actionSave)

		self.actionInfo = QtGui.QAction(self)
		self.actionInfo.setText('Info..')
		self.actionInfo.setToolTip('Save screenshot to file (Alt+N)')
		self.actionInfo.setShortcut(QtGui.QKeySequence('Alt+N') )
		self.actionInfo.triggered.connect(self.onActionInfoTriggered)
		self._actions.append(self.actionInfo)

		# connect global signals
		TableCrabConfig.globalObject.widgetScreenshotQuery.connect(self.onWidgetScreenshotQuery)
		TableCrabConfig.globalObject.widgetScreenshot.connect(self.onWidgetScreenshot)

		self.adjustActions()

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def _windowInfo(self, hwnd, level=0):
		if TableCrabWin32.windowGetTextLength(hwnd) > TableCrabConfig.MaxWindowText:
			title = 'Window title too long'
		else:
			title = TableCrabWin32.windowGetText(hwnd, maxSize=TableCrabConfig.MaxWindowText).replace('\r', '')
		if '\n' in title: title = title.split('\n', 1)[0]
		className = TableCrabWin32.windowGetClassName(hwnd)
		buttons = sorted( TableCrabWin32.windowGetButtons(hwnd).keys() )
		size = TableCrabWin32.windowGetRect(hwnd).size()
		pos = TableCrabWin32.windowGetPos(hwnd)
		clientSize = TableCrabWin32.windowGetClientRect(hwnd).size()
		if not buttons:
			buttons = ''
		elif len(buttons) == 1:
			buttons = "'%s'" % buttons[0]
		else:
			buttons = "'%s'" % ', '.join(["'%s'" % i for i in buttons] )
		isVisible = TableCrabWin32.windowIsVisible(hwnd)
		isEnabled = TableCrabWin32.windowIsEnabled(hwnd)

		indent = '\x20\x20\x20\x20' *level
		p = '%s%s\n' % (indent, '/'*level)
		p += '%sTitle: %s\n' % (indent, title)
		p += '%sClassName: %s\n' % (indent, className)
		p += '%sPos: %s,%s\n' % (indent, pos.x(), pos.y() )
		p += '%sSize: %sx%s\n' % (indent, size.width(), size.height() )
		p += '%sClientSize: %sx%s\n' % (indent, clientSize.width(), clientSize.height() )
		p += '%sButtons: %s\n' % (indent, buttons)
		p += '%sVisible: %s\n' % (indent, isVisible)
		p += '%sEnabled: %s\n' % (indent, isEnabled)
		p += '%sHwnd: %s\n' % (indent, hwnd)
		return p

	def actions(self):
		return self._actions

	def adjustActions(self):
		self.actionSave.setEnabled(self.label.pixmap() is not None)
		self.actionInfo.setEnabled(self._lastScreenshotInfo is not None)

	def 	gatherWindowInfo(self, hwnd):
		self._lastScreenshotInfo = ''
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += 'Current Window\n'
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += self._windowInfo(hwnd)

		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += 'Window Hirarchy\n'
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		level = 0
		hwndParent = hwnd
		while hwndParent:
			self._lastScreenshotInfo += self._windowInfo(hwndParent, level=level)
			hwndParent = TableCrabWin32.windowGetParent(hwndParent)
			level += 1

		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += 'Window Details\n'
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		for level, hwnd in TableCrabWin32.windowWalkChildren(hwnd, report=True):
			 self._lastScreenshotInfo += self._windowInfo(hwnd, level=level)

	def setScreenshot(self, pixmap=None, screenshotName=None):
		self.label.setScreenshot(pixmap=pixmap, screenshotName=screenshotName)
		self.adjustActions()

	def screenshotInfo(self):
		return self._lastScreenshotInfo

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionOpenTriggered(self):
		imageFormats = TableCrabConfig.readWriteImageFormats()
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
		self.widgetScreenshotInfo.emit('')
		self._lastScreenshotInfo = None
		self.adjustActions()

	def onActionInfoTriggered(self):
		if self._lastScreenshotInfo is None:
			self.actionInfo.setEnabled(False)
			return
		dlg = DialgScreenshotInfo(self._lastScreenshotInfo, parent=self)
		dlg.show()

	def onActionSaveTriggered(self):
		if self.label.pixmap() is None:
			self.actionSave.setEnabled(False)
			return
		imageFormats = imageFormats = TableCrabConfig.readWriteImageFormats()
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Screenshot..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				defaultSuffix='png',
				settingsKey='Gui/Screenshot/DialogSave/State',
				)
		if fileName is None:
			return
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not self.label.pixmap().save(fileName, format):
			TableCrabConfig.msgWarning(self, 'Could Not Save Screenshot')

	def onWidgetScreenshot(self, hwnd, pixmap):
		self.gatherWindowInfo(hwnd)
		self.widgetScreenshotInfo.emit(self._lastScreenshotInfo)
		self.setScreenshot(pixmap)
		self.adjustActions()

	def onWidgetScreenshotQuery(self):
		pixmap = self.label.pixmap()
		if pixmap is None:
			pixmap = QtGui.QPixmap()
		TableCrabConfig.globalObject.widgetScreenshotSet.emit(pixmap)

#**********************************************************************************************
#
#**********************************************************************************************
class FrameSetup(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.templatesWidget = TemplatesWidget(parent=self)
		self.screenshotWidget =ScreenshotWidget(parent=self)

		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self.splitter.addWidget(self.templatesWidget)
		self.splitter.addWidget(self.screenshotWidget)

		self.toolBar = QtGui.QToolBar(self)
		for action in self.templatesWidget.actions():
			self.toolBar.addAction(action)
		self.toolBar.addSeparator()
		self.toolBar.addSeparator()
		for action in self.screenshotWidget.actions():
			self.toolBar.addAction(action)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self.toolBar.addAction(self.actionHelp)

		TableCrabConfig.globalObject.init.connect(self.onInit)
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)

		self.layout()

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.splitter)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self):
		TableCrabGuiHelp.dialogHelp('setup', parent=self)

	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Setup/SplitterState', self.splitter.saveState())

	def onInit(self):
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Setup/SplitterState', QtCore.QByteArray()).toByteArray() )

