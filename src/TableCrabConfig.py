
#TODO: we have to find a way to limit text length in QPlainTextEdit


#************************************************************************************
# consts
#************************************************************************************
ApplicationName = 'TableCrab2'
Version = '0.1.0'
ReleaseName = '%s-%s' % (ApplicationName, Version)
Author = 'JuergenUrner'
ErrorLogName = ApplicationName + '-Error.log'


MaxHotkeys = 64
MaxTemplates = 64
MaxName = 32		# arbitrary, maximum number of chars allowed in user supplied names
								# for now we hard code it here. would require some efford for status bar
								#to get it dynamically truncated
								# ++ we need to set some limit to template name editing

WindowHookTimeout = 0.2
HandGrabberTimeout = 0.4
MouseMonitorTimeout = 0.5
StatusBarMessageTimeout = 3
MaxHandGrabberPrefix = 16	# + postfix
MaxHandStyleSheet = 9000

#TODO: implement these
# let QWebKit deal with it
##MaxHandHtml = 0
# no idea about this one
##MaxScreenshotSize = 0

Ellipsis = '..'
MaxWindowText = 512		# maximum number of chars we retrieve as text / title from other windows
MaxHandHistoryText = 16384
MaxPokerStarsBetBoxText = 16	# maximum number of chars to retrieve from PS bet amount box

#****************************************************************************************
# setup minimal stuff to get at least some information in case something goes wrong
#
# every module should add this module as the very first import
#
#NOTE: if an exception occurs an error.log will be placed in the current directory. good or not?
#***************************************************************************************
import sys, os, traceback, logging, platform
from logging import handlers
logger = logging.getLogger(ApplicationName)
logger.addHandler(handlers.RotatingFileHandler(
		os.path.join(os.getcwd(), ErrorLogName),
		mode='a',
		maxBytes=32000,
		backupCount=0,
		))

def _excepthook(type, value, tb,
			sys=sys,
			traceback=traceback,
			logger=logger,
			releaseName=ReleaseName,
			platform=platform,
			suppressException=False,
			data=None,
			):
	# as failsave as possible
	p = ''
	p += 'TableCrab: %s\n' % releaseName
	p += 'Platform: %s %s\n' % (platform.system(), platform.release() )
	p += 'PythonVersion: %s\n' % sys.version.split()[0]
	try:
		from PyQt4.QtCore import qVersion, PYQT_VERSION_STR
		p += 'QtVersion: %s\n' % qVersion()
		p += 'PyQtVersion: %s\n' % PYQT_VERSION_STR
	except Exception,d:
		print '%s: %s' % (releaseName, d)
		p += 'QtVersion: Unknown\n'
		p += 'PyQtVersion: Unknown\n'
	try:
		import sipconfig
		p += 'SipVersion: %s\n' % sipconfig.Configuration().sip_version_str
	except  Exception,d:
		print '%s: %s' % (releaseName, d)
		p += 'SipVersion: Unknown\n'
	p += ''.join(traceback.format_exception(type, value, tb))
	if data is not None:
		try:
			p += data
		except Exception, d:
			print '%s: %s' % (releaseName, d)
	try:
		globalObject.feedbackException.emit(p)
	except Exception, d:
		print '%s: %s' % (releaseName, d)
	try:	# try to log
		logger.critical(p)
	except Exception, d:
		print '%s: %s' % (releaseName, d)
	if not suppressException:
		raise type(value)
sys.excepthook = _excepthook


def handleException(data=None):
	'''handles an exception without raising it
	@param data:(str) additional data topass along with the exception
	'''
	type, value, tb = sys.exc_info()
	_excepthook(type, value, tb, suppressException=True, data=data)

#************************************************************************************
#
#************************************************************************************
import posixpath, thread, atexit, inspect
from PyQt4 import QtCore, QtGui, QtWebKit

import TableCrabWin32
from TableCrabRes import Pixmaps, HtmlPages, StyleSheets

# explicitely set locale to US
QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates) )

# grab settings from commandline if possible
class Settings:
	qSettings = QtCore.QSettings(Author, ApplicationName)

#***********************************************************************************
# enshure we run a single application instance only
#***********************************************************************************
class SingleApplication(object):
	def __init__(self):
		self.hMutex = TableCrabWin32.kernel32.CreateMutexA(None, 1, 'Local\\73524668475460800279396959888864133024')
		atexit.register(self.close)
		if TableCrabWin32.GetLastError() == TableCrabWin32.ERROR_INVALID_HANDLE:
			#TODO: we could try to find the app holding the mutex (hopefuly us up and alive) and activate it
			# gut feeling it is be better to raise and log here. so we get at least some information in case someone blocks our mutex
			##sys.exit(1)
			raise RuntimeError('%s is already running' % ApplicationName)
	def close(self, closeFunc=TableCrabWin32.kernel32.CloseHandle):	# need to hold reference to CloseHandle here. we get garbage collected otherwise
		if self.hMutex is not None:
			closeFunc(self.hMutex)
			self.hMutex = None

#***********************************************************************************
# global QSettings
#***********************************************************************************
def settingsKeyJoin(*keys):
	keys = [(str(key) if isinstance(key, QtCore.QString) else key) for key in keys]
	return QtCore.QString( posixpath.join(*keys) )

def setSettings(settings):
	Settings.qSettings = settings
	globalObject.init.emit()

def settings():
	return Settings.qSettings
def settingsValue(key, default):
	if isinstance(key, tuple):
		key = settingsKeyJoin(*key)
	return Settings.qSettings.value(key, default)
def settingsSetValue(key, value):
	if isinstance(key, tuple):
		key = settingsKeyJoin(*key)
	Settings.qSettings.setValue(key, QtCore.QVariant(value) )
def settingsRemoveKey(key):
	if isinstance(key, tuple):
		key = settingsKeyJoin(*key)
	#TODO: for some reason QSettings.contains(key) always return false here even if the key exists
	##print key, qSettings.contains(key)
	#if qSettings.contains(key):
	Settings.qSettings.remove(key)

#***********************************************************************************
# global singal handling and messages
#***********************************************************************************
class _GlobalObject(QtCore.QObject):

	# global signals
	init = QtCore.pyqtSignal()
	closeEvent = QtCore.pyqtSignal(QtCore.QEvent)

	#TODO: overload to accept QObject aswell
	feedback =  QtCore.pyqtSignal(QtGui.QWidget, QtCore.QString)
	feedbackMessage =  QtCore.pyqtSignal(QtCore.QString)
	feedbackException =  QtCore.pyqtSignal(QtCore.QString)

	settingAlternatingRowColorsChanged = QtCore.pyqtSignal(bool)
	settingChildItemIndicatorsChanged = QtCore.pyqtSignal(bool)

	# new screenshot created (hwnd, pixmap)
	widgetScreenshot = QtCore.pyqtSignal(int, QtGui.QPixmap)
	# a screenshot has been double clicked in the screenshot widget
	widgetScreenshotDoubleClicked = QtCore.pyqtSignal(QtGui.QPixmap, QtCore.QPoint)
	# query screenshot widget for screenshot --> signal widgetScreenshotSet()
	widgetScreenshotQuery = QtCore.pyqtSignal()
	# a sceenshot has been set to screenshot widget. a null pixmap is passed if no screenshot has been set
	widgetScreenshotSet = QtCore.pyqtSignal(QtGui.QPixmap)

globalObject = _GlobalObject()

#***********************************************************************************
# types
#***********************************************************************************
PointNone = QtCore.QPoint(-1, -1)
def newPointNone():
	return QtCore.QPoint(PointNone.x(), PointNone.y() )
SizeNone = QtCore.QSize(-1, -1)
def newSizeNone():
	return QtCore.QSize(SizeNone.width(), SizeNone.height() )

HotkeyNone = 'None'

#***********************************************************************************
# persistent items
#***********************************************************************************
#NOTE: on every change in templates and hotkeys we dum the whole TreeWidget to settings.
# easy but brutal. no idea if it is worth the trouble to implement a more sensible mechanism.
#NOTE: if something goes wrong after settingsRemoveKey() we are doomed
def dumpPersistentItems(settigsKey, items):
		settingsRemoveKey(settigsKey)
		slot = 0
		for item in items:
			key = settingsKeyJoin(settigsKey, str(slot) )
			if item.toConfig(key):
				slot += 1

def readPersistentItems(settingsKey, maxItems=0, itemProtos=None):
	itemProtos = () if itemProtos is None else itemProtos
	newItems = []
	for slot in xrange(maxItems):
		key = settingsKeyJoin(settingsKey, str(slot) )
		for itemProto in itemProtos:
			newItem = itemProto.fromConfig(key)
			if newItem is not None:
				newItems.append( (slot, newItem) )
				break
	lastSlot = -1
	forceDump = False
	items = []
	for slot, item in sorted(newItems):
		if not forceDump:
			forceDump = slot != lastSlot +1
		lastSlot = slot
		items.append(item)
	if forceDump:
		dumpPersistentItems(settingsKey, items)
	return items

#***********************************************************************************
# global objects
#***********************************************************************************
windowHook = TableCrabWin32.WindowHook(parent=None, timeout=WindowHookTimeout)
mouseHook = TableCrabWin32.MouseHook(parent=None)
keyboardHook = TableCrabWin32.KeyboardHook(parent=None)
#TODO: ..both below only get set if and when the according widgets are created
hotkeyManager = None
templateManager = None

#***********************************************************************************
# Qt widgets
#***********************************************************************************
class Action(QtGui.QAction):
	def __init__(self,
				parent=None,
				text='',
				menu=None,
				icon=None,
				slot=None,
				isEnabled=True,
				toolTip=None,
				autoRepeat=True,
				shortcut=None,
				userData=None,
				):
		self.userData = userData
		if icon is not None:
			QtGui.QAction.__init__(self, icon, text, parent)
		else:
			QtGui.QAction.__init__(self, parent)
		self.setText(text)
		self.setMenu(menu)
		if slot is not None and parent is not None: self.triggered.connect(slot)
		self.setEnabled(isEnabled)
		if toolTip is not None: self.setToolTip(toolTip)
		self.setAutoRepeat(autoRepeat)
		if shortcut is not None:
			if isinstance(shortcut, QtGui.QKeySequence.StandardKey):
				self.setShortcut(shortcut)
			else:
				self.setShortcut(QtGui.QKeySequence(shortcut) )

class WebViewToolBar(QtGui.QToolBar):
	ZoomIncrement = 0.1
	MaxZoom = 7
	MinZoom = 0.5
	def __init__(self, webView, settingsKeyZoomFactor=None, settingsKeyZoomIncrement=None):
		QtGui.QToolBar.__init__(self, webView)
		self.webView = webView
		self.settingsKeyZoomFactor = settingsKeyZoomFactor
		self.settingsKeyZoomIncrement = settingsKeyZoomIncrement

		globalObject.init.connect(self.onInit)

		back = self.webView.pageAction(QtWebKit.QWebPage.Back)
		back.setShortcut(QtGui.QKeySequence.Back)
		back.setToolTip('Back (Alt+-)')
		self.addAction(back)
		forward = self.webView.pageAction(QtWebKit.QWebPage.Forward)
		forward.setToolTip('Forward (Alt++)')
		forward.setShortcut(QtGui.QKeySequence.Forward)
		self.addAction(forward)

		self.actionZoomIn = Action(
				parent=self,
				text='ZoomIn (Ctrl++)',
				icon=QtGui.QIcon(Pixmaps.magnifierPlus() ),
				autoRepeat=True,
				shortcut=QtGui.QKeySequence.ZoomIn,
				slot=self.onActionZoomInTriggered,
				)
		self.addAction(self.actionZoomIn)

		self.actionZoomOut = Action(
				parent=self,
				text='ZoomOut (Ctrl+-)',
				icon=QtGui.QIcon(Pixmaps.magnifierMinus() ),
				autoRepeat=True,
				shortcut=QtGui.QKeySequence.ZoomOut,
				slot=self.onActionZoomOutTriggered,
				)
		self.addAction(self.actionZoomOut)

	def onInit(self):
		if self.settingsKeyZoomFactor is not None:
			self.webView.setZoomFactor( settingsValue(self.settingsKeyZoomFactor, self.webView.zoomFactor() ).toDouble()[0] )
		self.adjustActions()

	def _zoomIncrement(self):
		if self.settingsKeyZoomIncrement is not None:
			return settingsValue(self.settingsKeyZoomIncrement, self.ZoomIncrement).toDouble()[0]
		return self.ZoomIncrement

	def adjustActions(self):
		self.actionZoomIn.setEnabled(self.webView.zoomFactor() + self._zoomIncrement() < self.MaxZoom)
		self.actionZoomOut.setEnabled(self.webView.zoomFactor() -  + self._zoomIncrement() > self.MinZoom)

	def onActionZoomInTriggered(self):
		zoomIncrement = self._zoomIncrement()
		zoom = self.webView.zoomFactor() + zoomIncrement
		if zoom <= self.MaxZoom:
			self.webView.setZoomFactor(zoom)
			if self.settingsKeyZoomFactor is not None:
				settingsSetValue(self.settingsKeyZoomFactor, self.webView.zoomFactor())
		self.adjustActions()

	def onActionZoomOutTriggered(self):
		zoomIncrement = self._zoomIncrement()
		zoom = self.webView.zoomFactor() - zoomIncrement
		if zoom >= self.MinZoom:
			self.webView.setZoomFactor(zoom)
			if self.settingsKeyZoomFactor is not None:
				settingsSetValue(self.settingsKeyZoomFactor, self.webView.zoomFactor())
		self.adjustActions()


class LineEdit(QtGui.QLineEdit):
	def __init__(self, default='', settingsKey=None, maxLength=-1, parent=None):
		QtGui.QLineEdit.__init__(self, parent)
		self._settingsKey = settingsKey
		self._default = default
		if maxLength > -1:
			self.setMaxLength(maxLength)
		self.editingFinished.connect(self.onValueChanged)
		globalObject.init.connect(self.onInit)

	def onInit(self):
		if self._settingsKey is not None:
			self.setText( settingsValue(self._settingsKey, self._default).toString() )
		else:
			self.setText(self._default)

	def onValueChanged(self):
		if self._settingsKey is not None: settingsSetValue(self._settingsKey, self.text())


class PlainTextEdit(QtGui.QPlainTextEdit):

	maxCharsExceeded = QtCore.pyqtSignal(bool)

	def __init__(self, default='', settingsKey=None, parent=None, maxChars=-1):
		QtGui.QPlainTextEdit.__init__(self, parent)
		self._settingsKey = settingsKey
		self._maxChars = maxChars
		self._lastText = default
		self._default = default
		if self._maxChars >= 0 and len(default) > self._maxChars:
			raise ValueError('maxChars exceeded')
		self.textChanged.connect(self.onValueChanged)
		globalObject.init.connect(self.onInit)

	def onInit(self):
		if self._settingsKey is not None:
			self.setPlainText( settingsValue(self._settingsKey, self._default).toString() )
		else:
			self.setPlainText(self._default)

	#TODO: cheap implementation of mxText. we have to find a better way to do so
	def onValueChanged(self):
		if self._maxChars >= 0:
			if self.toPlainText().length() > self._maxChars:
				self.maxCharsExceeded.emit(True)
				return
			else:
				self.maxCharsExceeded.emit(False)
		if self._settingsKey is not None: settingsSetValue(self._settingsKey, self.toPlainText())


class DoubleSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, default=1.0, minimum=0.0, maximum=99.99, step=1.0, precision=2, settingsKey=None, parent=None):
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self._settingsKey = settingsKey
		self._default = default
		self.setRange(minimum, maximum)
		self.setSingleStep(step)
		self.setDecimals(precision)
		self.valueChanged.connect(self.onValueChanged)
		globalObject.init.connect(self.onInit)

	def onInit(self):
		if self._settingsKey is not None:
			self.setValue(  settingsValue(self._settingsKey, self._default).toDouble()[0] )
		else:
			self.setValue(self._default)

	def onValueChanged(self):
		if self._settingsKey is not None: settingsSetValue(self._settingsKey, self.value())

class SpinBox(QtGui.QSpinBox):
	def __init__(self, default=1, minimum=0, maximum=99, settingsKey=None, parent=None):
		QtGui.QSpinBox.__init__(self, parent)
		self._settingsKey = settingsKey
		self._default = default
		self.setRange(minimum, maximum)
		self.valueChanged.connect(self.onValueChanged)
		globalObject.init.connect(self.onInit)

	def onInit(self):
		if self._settingsKey is not None:
			self.setValue(  settingsValue(self._settingsKey, self._default).toInt()[0] )
		else:
			self.setValue(self._default)

	def onValueChanged(self):
		if self._settingsKey is not None: settingsSetValue(self._settingsKey, self.value())

class CheckBox(QtGui.QCheckBox):
	def __init__(self, text, default=False, settingsKey=None, parent=None):
		QtGui.QCheckBox.__init__(self, text, parent)
		self._settingsKey = settingsKey
		self._default = default
		self.stateChanged.connect(self.onStateChanged)
		globalObject.init.connect(self.onInit)

	def onInit(self):
		if self._settingsKey is not None:
			self.setCheckState(  QtCore.Qt.Checked if settingsValue(self._settingsKey, self._default).toBool() else QtCore.Qt.Unchecked )
		else:
			self.setCheckState(  QtCore.Qt.Checked if self._default else QtCore.Qt.Unchecked )

	def onStateChanged(self):
		if self._settingsKey is not None: settingsSetValue(self._settingsKey, self.checkState() == QtCore.Qt.Checked)

class ComboBox(QtGui.QComboBox):
	def __init__(self, choices, default='', failsave=False, settingsKey=None, parent=None):
		QtGui.QComboBox.__init__(self, parent)
		self.addItems(choices)
		self._settingsKey = settingsKey
		self._default = default
		self.failsave = failsave
		self.choices = choices
		self.currentIndexChanged.connect(self.onCurrentIndexChanged)
		globalObject.init.connect(self.onInit)

	def onInit(self):
		if self._settingsKey is not None:
			value = settingsValue(self._settingsKey, self._default).toString()
		else:
			value = self._default
		if value in self.choices:
			self.setCurrentIndex(self.choices.index(value))
		elif self.failsave:
				pass
		else:
			self.setCurrentIndex(self.choices.index(value))

	def onCurrentIndexChanged(self, index):
		if self._settingsKey is not None: settingsSetValue(self._settingsKey, self.itemText(index))

contentsMargins = QtCore.QMargins(2, 2, 2, 2)
class VBox(QtGui.QVBoxLayout):
	def __init__(self, *args):
		QtGui.QVBoxLayout.__init__(self, *args)
		self.setContentsMargins(contentsMargins)

class HBox(QtGui.QHBoxLayout):
	def __init__(self, *args):
		QtGui.QHBoxLayout.__init__(self, *args)
		self.setContentsMargins(contentsMargins)

class GridBox(QtGui.QGridLayout):
	def __init__(self, *args):
		QtGui.QGridLayout.__init__(self, *args)
		self.setContentsMargins(contentsMargins)
	def addFields(self, *fields):
		row = self.rowCount()
		for items in fields:
			for col, item in enumerate(items):
				if isinstance(item, QtGui.QWidget):
					self.addWidget(item, row, col)
				else:
					self.addLayout(item, row, col)
			row += 1

class HLine(QtGui.QFrame):
	def __init__(self, *args):
		QtGui.QFrame.__init__(self, *args)
		self.setFrameStyle(self.HLine | self.Sunken)
class HStretch(HBox):
	def __init__(self, *args):
		HBox.__init__(self, *args)
		self.addStretch(999)
class VStretch(VBox):
	def __init__(self, *args):
		VBox.__init__(self, *args)
		self.addStretch(999)

#NOTE: kind of a guess ..PyQt4 single shot timers are segfaulting from time to time.
class Timer(QtCore.QTimer):
	def __init__(self, parent=None, singleShot=False, interval=0, slot=None, userData=None):
		QtCore.QTimer.__init__(self, parent)
		self.setSingleShot(singleShot)
		self.setInterval(interval)
		if slot is not None:
			self.timeout.connect(slot)
		self.userData = userData

#TODO: we have to ignore <TAB> cos it tabs away from the hotkey box
class HotkeyBox(QtGui.QComboBox):
	#NOTE: bit of a hack this combo
	# x) pretty much disbled all standart keybindings for the combo. except ESCAPE and SPACE (ESCAPE
	#     mut be handled internally cos it is working without our help)
	# x) we added a space to each displayName to trrick the combo popup search feature
	Hotkeys = (		# hotkey --> displayName
				('', '<Type Keys Your Keyboard>'),
				('<Escape>', ' Escape'),
				('<Space>', ' Space'),
				('<Tab>', ' Tab'),
				(TableCrabWin32.MouseWheelUp, ' MouseWheelUp'),
				(TableCrabWin32.MouseWheelDown, ' MouseWheelDown'),
			)
	def __init__(self, hotkey=None, parent=None):
		QtGui.QComboBox.__init__(self, parent=None)
		self._counter = 0
		self.addItems( [i[1] for i in self.Hotkeys] )
		for i, (tmpHotkey, _) in enumerate(self.Hotkeys):
			if hotkey == tmpHotkey:
				self.setCurrentIndex(i)
				break
		else:
			if hotkey is not None:
				self.setItemText(0, hotkey)
		keyboardHook.inputEvent.connect(self.onInputEvent)

	#TODO: works for now, but have to rework this. we open popup if the user clicks the combo twice
	def focusInEvent(self, event):
		self._counter = 1
		return QtGui.QComboBox.focusInEvent(self, event)

	def mousePressEvent(self, event):
		if self._counter > 0:
			self._counter -= 1
		else:
			return QtGui.QComboBox.mousePressEvent(self, event)

	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Space and not event.modifiers():
			QtGui.QComboBox.keyPressEvent(self, event)
	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Space and not event.modifiers():
			QtGui.QComboBox.keyPressEvent(self, event)
	def onInputEvent(self, inputEvent):
		if not inputEvent.keyIsDown: return
		if self.hasFocus():
			if self.currentIndex() == 0:
				for (myKey, _) in self.Hotkeys:
					if inputEvent.key == myKey:
						break
				else:
					self.setItemText(0, inputEvent.key)
	def hotkey(self):
		text = self.currentText()
		for key, displayName in self.Hotkeys:
			if text == displayName:
				return key
		return text

class TreeWidgetItemIterator(QtGui.QTreeWidgetItemIterator):
	def __init__(self, *args):
		QtGui.QTreeWidgetItemIterator.__init__(self, *args)
	def __iter__(self):
		while True:
			self.__iadd__(1)
			value = self.value()
			if value:
				yield value
			else:
				break
		raise StopIteration

def msgWarning(parent, msg):
	QtGui.QMessageBox.critical(parent, ApplicationName, msg)

def msgCritical(parent, msg):
	QtGui.QMessageBox.critical(parent, ApplicationName, msg)

def dlgOpenSaveFile(
			parent=None,
			openFile=True,
			title='',
			fileFilters=None,
			settingsKey=None,
			):
	pass

	dlg = QtGui.QFileDialog(parent)
	dlg.setAcceptMode(dlg.AcceptOpen if openFile else dlg.AcceptSave)
	dlg.setWindowTitle(title)
	if fileFilters:
		p = QtCore.QStringList()
		for i in fileFilters:
			p << i
		dlg.setNameFilters(p)
	if not openFile:
		dlg.setConfirmOverwrite(True)
	if settingsKey is not None:
		dlg.restoreState( settingsValue(settingsKey, QtCore.QByteArray()).toByteArray() )


	result = dlg.exec_()
	if settingsKey is not None:
		settingsSetValue(settingsKey, dlg.saveState() )
	if result == dlg.Accepted:
		return dlg.selectedFiles()[0]
	return None

#***********************************************************************************
# type converters
#***********************************************************************************
def pointToString(qPoint):
	if qPoint.x() < 0 or qPoint.y() < 0:
		return 'None'
	return '%s,%s' % (qPoint.x(), qPoint.y())

def sizeToString(qSize):
	if qSize.isEmpty():
		return 'None'
	return '%sx%s' % (qSize.width(), qSize.height())

def pointInSize(size, point):
	if not size.isValid():
		return False
	if point.y() >= 0 and point.y() >= 0:
		if point.x() <= size.width() and point.y() <= size.height():
			return True
	return False

def widgetScreenshot(hwnd):
	pixmap = QtGui.QPixmap.grabWindow(hwnd, 0, 0, -1,-1)
	globalObject.widgetScreenshot.emit(hwnd, pixmap)

def uniqueName(name, names):
	i = 0
	newName = name
	while newName in names:
		i += 1
		newName = name + ' (%s)' % i
	return newName

def cleanException(exception):
	p = QtCore.QString()
	for line in exception.split('\n'):
		if line.startsWith('  File "'):
			start = line.indexOf('"') +1
			if start < 0:	continue
			stop = line.lastIndexOf('"')
			if stop < 0: continue
			fileName = line[start:stop]
			fileInfo = QtCore.QFileInfo(fileName)
			line = QtCore.QString('%1%2%3').arg(line[:start]).arg(fileInfo.fileName()).arg(line[stop:])
		p += line
		p += '\n'
	return p

def truncateString(string, maxChars):
	isQString = isinstance(string, QtCore.QString)
	if maxChars > -1 and len(string) > maxChars:
		if maxChars <= len(Ellipsis):
			return QtCore.QString(Ellipsis[:maxChars])
		else:
			return string[:maxChars - len(Ellipsis)] + Ellipsis
	return string

def dialogTitle(title):
	return '%s - %s' % (ApplicationName, title)

def printStack():
	for frame, filename, line_num, func, source_code, source_index in inspect.stack()[1:]:
		print '%s, line %d\n  -> %s' % (filename, line_num, source_code[source_index].strip())

#NOTE: we format numbers by hand because we need US formatting and on some oses locale.setlocale(locale.LC_ALL, 'en_US') fails
def formatNum(num, precission=2):
	"""formats a number
	@param num: (int, float) number to format
	@param precission: (int) floating point precission
	@return: (str)
	"""
	num = round(num, precission)
	num = str(num)
	head, sep, tail = num.partition('.')
	if not tail:
		tail = '0'*precission
	groups = []
	for i in xrange(len(head), 0, -3):
		start = i -3 if i -3 > 0 else 0
		group = head[start:i]
		groups.insert(0, group)
	head = ','.join(groups)
	if tail:
		tail = float('0.' + tail)
		tail = '%.*f' % (precission, tail)
		tail = tail[1:]
	return head + tail










