
#TODO: would be nice to have some information on how many templates are left until hitting MaxTemplates
#TODO: in wine we-1.2 can not resize windows belonging to other processes. this a bug in wine [ http://bugs.winehq.org/show_bug.cgi?id=23940 ]
#				user32.SetWindowPos() does not work for other processes. used to work in wine-1.1.41, stopped working in wine-1.1.42. as soon as SetWindowPos()
#				is working again we should kick out mouse tracking on other windows and add a hotkey to cycle through layouts and adapt the current windows
#				size acccording to the next matching templates size. CycleForward / CycleBackward maybe.
#TODO: i kind of dislike in-place editing of template names. an "Edit" button would be more consistent but a bit of overkill right now. then .again .screenshot
# 			open / save is taking away screenspace already. would have to find shorter names for these actions.
#TODO: check for multiple templates of the same size? currently we are using the first matching encountered that's all.
#TODO: restore last selected template on restart? would require an attr "itemIsSelected", downside we'd have to dump the whole tree on every curent
#				item change. so most likely a no.

import TableCrabConfig
import TableCrabWin32
import TableCrabGuiHelp
import TableCrabTemplates

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
class TemplatesWidget(QtGui.QTreeWidget):

	class MyDelegate(QtGui.QItemDelegate):
		editingFinished = QtCore.pyqtSignal()

		def __init__(self, parent=None):
			QtGui.QItemDelegate.__init__(self, parent)
		def createEditor(self, parent, option, index):
			ed = QtGui.QLineEdit(parent)
			ed.setMaxLength(TableCrabConfig.MaxName)
			ed.editingFinished.connect(self.onEditingFinished)
			return ed
		def onEditingFinished(self):
			self.editingFinished.emit()

	class ActionNewTemplate(QtGui.QAction):
		def __init__(self, templateProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.templateProto = templateProto
			self.setText(self.templateProto.menuName() )
			self, self.triggered.connect(self.onTriggered)
		def onTriggered(self):
			self.parent().createTemplate(self.templateProto)


	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)

		TableCrabConfig.templateManager = self

		# setup treeWidget
		self.setColumnCount(2)
		self.setExpandsOnDoubleClick(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
		self.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		self.setRootIsDecorated( TableCrabConfig.settingsValue('Gui/ChildItemIndicators', True).toBool() )

		self.myDelegate = self.MyDelegate(parent=self)
		self.setItemDelegate(self.myDelegate)

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

		# connect signals
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSetAlternatingRowColors)
		TableCrabConfig.globalObject.settingChildItemIndicatorsChanged.connect(self.onSetRootIsDecorated)
		TableCrabConfig.globalObject.widgetScreenshotSet.connect(self.onWidgetScreenshotSet)
		TableCrabConfig.globalObject.widgetScreenshotDoubleClicked.connect(self.onWidgetScreenshotDoubleClicked)

		# connect to TreeWidget signals
		self.itemDoubleClicked.connect(self.onEditItem)
		self.itemExpanded.connect(self.onItemExpanded)
		self.itemCollapsed.connect(self.onItemCollapsed)
		self.itemSelectionChanged.connect(self.adjustActions)

		# connect to ietm delegate signals
		self.myDelegate.editingFinished.connect(self.onTemplateEditingFinished)

		self.adjustActions()

	def onSetAlternatingRowColors(self, flag):
		self.setAlternatingRowColors(flag)

	def onSetRootIsDecorated(self, flag):
		self.setRootIsDecorated(flag)

	def onEditItem(self, item):
		self.editItem(item)

	def keyReleaseEvent(self, event):
		#TODO: for some reason the first enter when the widget is created is not accepted
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			event.accept()
			item = self.currentItem()
			if not item is None:
				if item.toplevel() is item:
						self.editItem(item)
			return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)

	def read(self):
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

	def dump(self):
		TableCrabConfig.dumpPersistentItems('Templates', self)

	def __iter__(self):
		for i in xrange(self.topLevelItemCount()):
			yield self.topLevelItem(i)

	def actions(self):
		return self._actions

	def adjustActions(self):
		self.actionNew.setEnabled(self.topLevelItemCount() < TableCrabConfig.MaxTemplates)
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			self.actionDown.setEnabled(False)
			self.actionRemove.setEnabled(False)
		else:
			self.actionUp.setEnabled(self.canMoveTemplateUp() )
			self.actionDown.setEnabled(self.canMoveTemplateDown() )
			self.actionRemove.setEnabled(True)

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

	def onItemCollapsed(self, item):
		if not self._templatesRead:
			return
		if item.toplevel().handleItemCollapsed(item):
			self.dump()

	def onTemplateEditingFinished(self):
		item = self.currentItem()
		if item is not None:
			if item.toplevel().handleEditingFinished(item):
				self.dump()

	def onItemExpanded(self, item):
		if not self._templatesRead:
			return
		if item.toplevel().handleItemExpanded(item):
			self.dump()

	def onWidgetScreenshotDoubleClicked(self, pixmap, point):
		item = self.currentItem()
		if item is None:
			return False
		if item.toplevel().handleScreenshotDoubleClicked(item, pixmap, point):
			self.dump()

	def onWidgetScreenshotSet(self, pixmap):
		for template in self:
			template.handleScreenshotSet(pixmap)


class ScreenshotWidget(QtGui.QScrollArea):

	widgetScreenshotInfo = QtCore.pyqtSignal(QtCore.QString)

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

		def onMouseLeave(self):
			pixmap = self.pixmap()
			if pixmap is not None and not pixmap.isNull():
				point = TableCrabConfig.newPointNone()
				self._giveFeedback(pixmap, point)

		def mouseMoveEvent(self, event):
			pixmap = self.pixmap()
			if pixmap is not None and not pixmap.isNull():
				self._giveFeedback(pixmap, event.pos())

		def _giveFeedback(self, pixmap, point):
			name = TableCrabConfig.truncateString(self._screenshotName, TableCrabConfig.MaxName)
			p = '%s -- Size: %s Mouse: %s' % (name, TableCrabConfig.sizeToString(pixmap.size()), TableCrabConfig.pointToString(point) )
			TableCrabConfig.globalObject.feedback.emit(self, p)

		def setScreenshot(self, pixmap=None, screenshotName=None):
			self._screenshotName = self.ScreenshotName if screenshotName is None else screenshotName
			result = False
			if pixmap is None:
				self.setScaledContents(True)
				self.setFrameShape(QtGui.QFrame.NoFrame)
				self.setText(self._screenshotName)
				pixmap = QtGui.QPixmap()
				TableCrabConfig.globalObject.widgetScreenshotSet.emit(pixmap)
				if self.isVisible():
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
				if self.isVisible():
					self._giveFeedback(pixmap,  point)
				result = True
			return result


	def __init__(self, parent=None):
		QtGui.QScrollArea.__init__(self, parent)

		self._lastScreenshotInfo = None

		self.label = self.ScreenshotLabel()
		self.label.setScreenshot(pixmap=None)
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
				toolTip='Display detailed screenshot information',
				slot=self.onActionInfoTriggered,
				)
		self._actions.append(self.actionInfo)

		# connect global signals
		TableCrabConfig.globalObject.widgetScreenshotQuery.connect(self.onWidgetScreenshotQuery)
		TableCrabConfig.globalObject.widgetScreenshot.connect(self.onWidgetScreenshot)

		self.adjustActions()

	def actions(self):
		return self._actions

	def adjustActions(self):
		self.actionSave.setEnabled(self.label.pixmap() is not None)
		self.actionInfo.setEnabled(self._lastScreenshotInfo is not None)

	def 	gatherWindowInfo(self, hwnd):
		def windowInfo(hwnd, level=0):
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

		self._lastScreenshotInfo = ''
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += 'Current Window\n'
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += windowInfo(hwnd)

		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += 'Window Hirarchy\n'
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		level = 0
		hwndParent = hwnd
		while hwndParent:
			self._lastScreenshotInfo += windowInfo(hwndParent, level=level)
			hwndParent = TableCrabWin32.windowGetParent(hwndParent)
			level += 1

		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += 'Window Details\n'
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		for level, hwnd in TableCrabWin32.windowWalkChildren(hwnd, report=True):
			 self._lastScreenshotInfo += windowInfo(hwnd, level=level)

	def screenshotInfo(self):
		return self._lastScreenshotInfo

	def setScreenshot(self, pixmap=None, screenshotName=None):
		self.label.setScreenshot(pixmap=pixmap, screenshotName=screenshotName)
		self.adjustActions()

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
		self.widgetScreenshotInfo.emit('')
		self._lastScreenshotInfo = None
		self.adjustActions()

	def onActionSaveTriggered(self):
		if self.label.pixmap() is None:
			self.actionSave.setEnabled(False)
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
		if self._lastScreenshotInfo is None:
			self.actionInfo.setEnabled(False)
			return
		dlg = DialgScreenshotInfo(self._lastScreenshotInfo, parent=self)
		dlg.show()

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
		self.widgetScreenshotInfo.emit(self._lastScreenshotInfo)
		self.setScreenshot(pixmap)
		self.adjustActions()

	def onWidgetScreenshotQuery(self):
		pixmap = self.label.pixmap()
		if pixmap is None:
			pixmap = QtGui.QPixmap()
		TableCrabConfig.globalObject.widgetScreenshotSet.emit(pixmap)


class DialgScreenshotInfo(QtGui.QDialog):
	def __init__(self, info, parent=None):
		QtGui.QDialog. __init__(self, parent)
		self.setWindowTitle(TableCrabConfig.dialogTitle('Screenshot Info') )

		self._lastScreenshotInfo = info

		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setPlainText(info)
		self.edit.setReadOnly(True)
		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.clicked.connect(self.onButtonHelpClicked)
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ApplyRole )
		self.buttonBox.accepted.connect(self.accept)
		self.buttonSave.clicked.connect(self.onButtonSaveClicked)

		#NOTE: we are modeless, so it is a good idea to add a refresh button
		parent.widgetScreenshotInfo.connect(self.onWidgetScreenshotInfo)
		self.buttonRefresh = QtGui.QPushButton('Refresh', self)
		self.buttonRefresh.clicked.connect(self.onButtonRefreshClicked)
		self.buttonBox.addButton(self.buttonRefresh, self.buttonBox.ActionRole)

		self.layout()
		self.restoreGeometry( TableCrabConfig.settingsValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', QtCore.QByteArray()).toByteArray() )

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.edit, 0, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 1, 0)
		grid.addWidget(self.buttonBox, 2, 0)

	def hideEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Screenshot/DialogScreenshotInfo/Geometry', self.saveGeometry() )
		QtGui.QDialog.hideEvent(self, event)

	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('screenshotInfo', parent=self)

	def onButtonRefreshClicked(self, checked):
		self.edit.setPlainText(self._lastScreenshotInfo)

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

	def onWidgetScreenshotInfo(self, info):
		self._lastScreenshotInfo = info
		self.buttonRefresh.setEnabled(bool(info))


class FrameSetup(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		# time to monitor mouse to give feedback on other windws
		self.mouseMonitorTimer = TableCrabConfig.Timer(parent=self, singleShot=False, interval=TableCrabConfig.MouseMonitorTimeout*1000, slot=self.onMouseMonitor)

		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self.templatesWidget = TemplatesWidget(parent=self)
		self.screenshotWidget =ScreenshotWidget(parent=self)

		self.splitter.addWidget(self.templatesWidget)
		self.splitter.addWidget(self.screenshotWidget)
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Setup/SplitterState', QtCore.QByteArray()).toByteArray() )
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)

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

	def hideEvent(self, event):
		self.mouseMonitorTimer.stop()
		return QtGui.QFrame.hideEvent(self, event)

	def showEvent(self, event):
		self.mouseMonitorTimer.start()
		return QtGui.QFrame.showEvent(self, event)

	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Setup/SplitterState', self.splitter.saveState())

	def onMouseMonitor(self):

		# find our main window hwnd
		wid = self.effectiveWinId()	# NOTE: effectiveWinId() returns <sip.voidptr> and may be None
		if not wid:
			return
		hwndSelf = int(wid)
		hwndSelf = TableCrabWin32.windowGetTopLevelParent(hwndSelf)

		# get toplevel window under mouse
		point = TableCrabWin32.mouseGetPos()
		hwndOther = TableCrabWin32.windowFromPoint(point)
		hwndOther = TableCrabWin32.windowGetTopLevelParent(hwndOther)
		if not hwndOther:
			return
		elif hwndOther == hwndSelf:
			return

		# found a window of another process ..give feedback
		if TableCrabWin32.windowGetTextLength(hwndOther) > TableCrabConfig.MaxWindowText:
			title = 'Window title too long'
		else:
			title = TableCrabWin32.windowGetText(hwndOther, maxSize=TableCrabConfig.MaxWindowText)
			if not title:
				return
		title = TableCrabConfig.truncateString(title, TableCrabConfig.MaxName)
		rect = TableCrabWin32.windowGetClientRect(hwndOther)
		size = TableCrabConfig.sizeToString(rect.size() )
		point = TableCrabWin32.windowScreenPointToClientPoint(hwndOther, point)
		point = TableCrabConfig.pointToString(point)
		TableCrabConfig.globalObject.feedback.emit(self, '%s -- Size: %s Mouse: %s' % (title, size, point) )

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


