
import Tc2Config
import Tc2Win32
import Tc2DialogScreenshotInfo

from PyQt4 import QtCore,QtGui

#************************************************************************************
#
#************************************************************************************
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
					point = Tc2Config.newPointNone()
				else:
					point = QtCore.QPoint(event.pos())
				Tc2Config.globalObject.widgetScreenshotDoubleClicked.emit(pixmap, point)

	def mouseMoveEvent(self, event):
		pixmap = self.pixmap()
		if pixmap is not None and not pixmap.isNull():
			self._giveFeedback(pixmap, event.pos())

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def _giveFeedback(self, pixmap, point):
		name = Tc2Config.truncateString(self._screenshotName, Tc2Config.MaxName)
		p = '%s -- Size: %s Mouse: %s' % (name, Tc2Config.sizeToString(pixmap.size()), Tc2Config.pointToString(point) )
		Tc2Config.globalObject.feedback.emit(self, p)

	def setScreenshot(self, pixmap=None, screenshotName=None):
		self._screenshotName = self.ScreenshotName if screenshotName is None else screenshotName
		result = False
		if pixmap is None:
			self.setScaledContents(True)
			self.setText(self._screenshotName)
			self.resize(self.parent().size())		#TODO: no idea why but we need to resize here
			self.setFrameShape(QtGui.QFrame.NoFrame)
			pixmap = QtGui.QPixmap()
			Tc2Config.globalObject.widgetScreenshotSet.emit(pixmap)
			Tc2Config.globalObject.feedback.emit(self, '')
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
			Tc2Config.globalObject.widgetScreenshotSet.emit(pixmap)
			self._giveFeedback(pixmap,  point)
			result = True
		return result

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onMouseLeave(self):
		pixmap = self.pixmap()
		if pixmap is not None and not pixmap.isNull():
			point = Tc2Config.newPointNone()
			self._giveFeedback(pixmap, point)


class ScreenshotWidget(QtGui.QScrollArea):

	widgetScreenshotInfo = QtCore.pyqtSignal(QtCore.QString)

	SettingsKeyBase = 'Gui/Screenshot'
	SettingsKeyDialogOpenState = SettingsKeyBase + '/DialogOpen/State'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'


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
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.widgetScreenshotQuery.connect(self.onWidgetScreenshotQuery)
		Tc2Config.globalObject.widgetScreenshot.connect(self.onWidgetScreenshot)

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def _windowInfo(self, hwnd, level=0):
		if Tc2Win32.windowGetTextLength(hwnd) > Tc2Config.MaxWindowText:
			title = 'Window title too long'
		else:
			title = Tc2Win32.windowGetText(hwnd, maxSize=Tc2Config.MaxWindowText).replace('\r', '')
		if '\n' in title: title = title.split('\n', 1)[0]
		className = Tc2Win32.windowGetClassName(hwnd)
		buttons = sorted( Tc2Win32.windowGetButtons(hwnd).keys() )
		size = Tc2Win32.windowGetRect(hwnd).size()
		pos = Tc2Win32.windowGetPos(hwnd)
		clientSize = Tc2Win32.windowGetClientRect(hwnd).size()
		if not buttons:
			buttons = ''
		elif len(buttons) == 1:
			buttons = "'%s'" % buttons[0]
		else:
			buttons = "'%s'" % ', '.join(["'%s'" % i for i in buttons] )
		isVisible = Tc2Win32.windowIsVisible(hwnd)
		isEnabled = Tc2Win32.windowIsEnabled(hwnd)

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
			hwndParent = Tc2Win32.windowGetParent(hwndParent)
			level += 1

		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		self._lastScreenshotInfo += 'Window Details\n'
		self._lastScreenshotInfo += '-----------------------------------------------------------------\n'
		for level, hwnd in Tc2Win32.windowWalkChildren(hwnd, report=True):
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
		imageFormats = Tc2Config.readWriteImageFormats()
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Screenshot..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				settingsKey=self.SettingsKeyDialogOpenState,
				)
		if fileName is None:
			return
		pixmap = QtGui.QPixmap()
		if not pixmap.load(fileName):
			Tc2Config.msgWarning(self, 'Could not open screenshot')
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
		dlg = Tc2DialogScreenshotInfo.DialgScreenshotInfo(self._lastScreenshotInfo, parent=self)
		dlg.show()

	def onActionSaveTriggered(self):
		if self.label.pixmap() is None:
			self.actionSave.setEnabled(False)
			return
		imageFormats = imageFormats = Tc2Config.readWriteImageFormats()
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Screenshot..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				defaultSuffix='png',
				settingsKey=self.SettingsKeyDialogSaveState,
				)
		if fileName is None:
			return
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not self.label.pixmap().save(fileName, format):
			Tc2Config.msgWarning(self, 'Could Not Save Screenshot')

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.adjustActions()

	def onWidgetScreenshot(self, hwnd, pixmap):
		self.gatherWindowInfo(hwnd)
		self.widgetScreenshotInfo.emit(self._lastScreenshotInfo)
		self.setScreenshot(pixmap)
		self.adjustActions()

	def onWidgetScreenshotQuery(self):
		pixmap = self.label.pixmap()
		if pixmap is None:
			pixmap = QtGui.QPixmap()
		Tc2Config.globalObject.widgetScreenshotSet.emit(pixmap)
