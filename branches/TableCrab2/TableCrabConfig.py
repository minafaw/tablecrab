
#****************************************************************************************
# setup minimal stuff to get at least some information in case something goes wrong
#
# every module should add this module as the very first import
#
#NOTE: if an exception occurs an error.log will be placed in the current directory. good or not?
#***************************************************************************************
import sys, os, traceback, logging, platform
from logging import handlers

ApplicationName = 'TableCrab2'
Version = '0.1.0'
ReleaseName = '%s-%s' % (ApplicationName, Version)
Author = 'JuergenUrner'
ErrorLogName = ApplicationName + '-Error.log'

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
			):
	# as failsave as possible
	p = ''
	p += ': %s\n' % releaseName
	p += 'Platform: %s %s\n' % (platform.system(), platform.release() )
	p += 'PythonVersion: %s\n' % sys.version.split()[0]
	try:
		from PyQt4.QtCore import qVersion, PYQT_VERSION_STR
		p += 'QtVersion: %s\n' % qVersion()
		p += 'PyQtVersion: %s\n' % PYQT_VERSION_STR
	except:
		p += 'QtVersion: Unknown\n'
		p += 'PyQtVersion: Unknown\n'
	try:
		import sipconfig
		p += 'SipVersion: %s\n' % sipconfig.Configuration().sip_version_str
	except:
		p += 'SipVersion: Unknown\n'
	try:
		signalEmit(None, 'feedbackException()')
	except: pass
	p += ''.join(traceback.format_exception(type, value, tb))
	try:	# try to log
		logger.critical(p)
	except:	# no success ..write to console
		print p
	
	raise type(value)
sys.excepthook = _excepthook

#************************************************************************************
#
#************************************************************************************
import posixpath, thread, atexit
from PyQt4 import QtCore, QtGui, QtWebKit

import TableCrabWin32
from TableCrabRes import Pixmaps, HtmlPages, StyleSheets

# grab settings from commandline if possible
_qSettings = None
if '--config' in sys.argv:
	i = sys.argv.index('--config')
	del sys.argv[i]
	try:
		fileName = sys.argv[i]
	except IndexError: pass
	else:
		if os.path.isfile(fileName) or os.path.islink(fileName):
			del sys.argv[i]
			_qSettings = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
if _qSettings is None:
	_qSettings = QtCore.QSettings(Author, ApplicationName)

#***********************************************************************************
# enshure we run a single application instance only
#***********************************************************************************
class SingleApplication(object):
	def __init__(self):
		self.hMutex = TableCrabWin32.kernel32.CreateMutexA(None, 1, 'Local\\73524668475460800279396959888864133024')
		atexit.register(self.close)
		if TableCrabWin32.GetLastError() == TableCrabWin32.ERROR_INVALID_HANDLE:
			#TODO: we could try to find the app holding the mutex (hopefuly ) and activate it 
			# gut feeling it is be better to raise and log here, so we get at least some information in case someone blocks our mutex
			##sys.exit(1)
			raise RuntimeError(' is already running')
	def close(self, closeFunc=TableCrabWin32.kernel32.CloseHandle):	# need to hold reference to CloseHandle here. we get garbage collected otherwise
		closeFunc(self.hMutex)

#***********************************************************************************
# global QSettings
#***********************************************************************************
configKey = ''		# for testing. set this to save settings to a different key
def settingsKeyJoin(*keys):
	keys = [(str(key) if isinstance(key, QtCore.QString) else key) for key in keys]
	return QtCore.QString( posixpath.join(*keys) )

def settings():
	return _qSettings
def settingsValue(key, default):
	if isinstance(key, tuple):
		key = settingsKeyJoin(configKey, *key)
	else:
		key = settingsKeyJoin(configKey, key)
	return _qSettings.value(key, default)
def settingsSetValue(key, value):
	if isinstance(key, tuple):
		key = settingsKeyJoin(configKey, *key)
	else:
		key = settingsKeyJoin(configKey, key)
	_qSettings.setValue(key, QtCore.QVariant(value) )
def settingsRemoveKey(key):
	key = settingsKeyJoin(configKey, key)
	#TODO: for some reason QSettings.contains(key) always return false here even if the key exists 
	##print key, _qSettings.contains(key)
	#if _qSettings.contains(key):
	_qSettings.remove(key)
	
#***********************************************************************************
# global singal handling and messages
#***********************************************************************************
# global signal  'closeEvent(QEvent*)'
# global signal 'feedbackCurentObject(QString)'
# global signal 'feedbackCurentObjectData(QString)'
# global signal 'feedbackMessage(QString)'
# global signal 'feedbackException()'
# global signal 'widgetScreenshot(int, QPixmap*)'
# global signal 'widgetScreenshotSet(QPixmap*)'
# global signal 'widgetScreenshotDoubleClicked(QPixmap*, QPoint*)'
# global signal 'widgetScreenshotQuery()'
# global signal 'settingAlternatingRowColorsChanged(bool)'
# global signal 'settingChildItemIndicatorsChanged(bool)'
#
_qObject = QtCore.QObject()
def signalEmit(sender, signal, *params):
	if sender is None: _qObject.emit(QtCore.SIGNAL(signal), *params)
	else: sender.emit(QtCore.SIGNAL(signal), *params)
def signalConnect(sender, receiver, signal, slot):
	if sender is None: receiver.connect(_qObject, QtCore.SIGNAL(signal), slot)
	else: receiver.connect(sender, QtCore.SIGNAL(signal), slot)

def signalsConnect(sender, receiver, *signals):
	for signal, slot in signals:
		signalConnect(sender, receiver, signal, slot)

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
		dumpPersistentItems(settignsKey, items)
	return items
	
#***********************************************************************************
# global objects
#***********************************************************************************
windowHook = TableCrabWin32.WindowHook(parent=None)
mouseHook = TableCrabWin32.MouseHook(parent=None)
keyboardHook = TableCrabWin32.KeyboardHook(parent=None)
#TODO: not with about this ..both only get set if and when the according widgets are created
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
				):
		if icon is not None:
			QtGui.QAction.__init__(self, icon, text, parent)
		else:
			QtGui.QAction.__init__(self, parent)
		self.setText(text)
		self.setMenu(menu)
		if slot is not None and parent is not None: parent.connect(self, QtCore.SIGNAL('triggered(bool)'), slot)
		self.setEnabled(isEnabled)
		if toolTip is not None: self.setToolTip(toolTip)
		self.setAutoRepeat(autoRepeat)
		if shortcut is not None:
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
		
		if self.settingsKeyZoomFactor is not None:
			self.webView.setZoomFactor( settingsValue(settingsKeyZoomFactor, self.webView.zoomFactor() ).toDouble()[0] )
		
		self.addAction( self.webView.pageAction(QtWebKit.QWebPage.Back) )
		self.addAction( self.webView.pageAction(QtWebKit.QWebPage.Forward) )
		
		self.actionZoomIn = Action(
				parent=self,
				text='Zoom+',
				icon=QtGui.QIcon(Pixmaps.magnifierPlus() ),
				autoRepeat=True,
				shortcut=QtGui.QKeySequence.ZoomIn,
				slot=self.onActionZoomInTriggered,
				)
		self.addAction(self.actionZoomIn)
		
		self.actionZoomOut = Action(
				parent=self,
				text='Zoom-',
				icon=QtGui.QIcon(Pixmaps.magnifierMinus() ),
				autoRepeat=True,
				shortcut=QtGui.QKeySequence.ZoomOut,
				slot=self.onActionZoomOutTriggered,
				)
		self.addAction(self.actionZoomOut)
		
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
	def __init__(self, default='', settingsKey=None, parent=None):
		QtGui.QLineEdit.__init__(self, parent)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			self.setText(default)
		else:
			self.setText( settingsValue(self.settingsKey, default).toString() )
			self.connect(self, QtCore.SIGNAL('editingFinished()'), self.onValueChanged)
	def onValueChanged(self):
			if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.text())

class PlainTextEdit(QtGui.QPlainTextEdit):
	def __init__(self, default='', settingsKey=None, parent=None):
		QtGui.QPlainTextEdit.__init__(self, parent)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			self.setPlainText(default)
		else:
			self.setPlainText( settingsValue(self.settingsKey, default).toString() )
			self.connect(self, QtCore.SIGNAL('textChanged()'), self.onValueChanged)
	def onValueChanged(self):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.toPlainText())

class DoubleSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, default=1.0, minimum=0.0, maximum=99.99, step=1.0, precision=2, settingsKey=None, parent=None):
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self.settingsKey = settingsKey
		self.setRange(minimum, maximum)
		self.setSingleStep(step)
		self.setDecimals(precision)
		if self.settingsKey is None:
			self.setValue(default)
		else:
			self.setValue(  settingsValue(self.settingsKey, default).toDouble()[0] )
			self.connect(self, QtCore.SIGNAL('valueChanged(double)'), self.onValueChanged)
	def onValueChanged(self):
			if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.value())
				
class SpinBox(QtGui.QSpinBox):
	def __init__(self, default=1, minimum=0, maximum=99, settingsKey=None, parent=None):
		QtGui.QSpinBox.__init__(self, parent)
		self.settingsKey = settingsKey
		self.setRange(minimum, maximum)
		if self.settingsKey is None:
			self.setValue(default)
		else:
			self.setValue(  settingsValue(self.settingsKey, default).toInt()[0] )
			self.connect(self, QtCore.SIGNAL('valueChanged(int)'), self.onValueChanged)
	def onValueChanged(self):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.value())

class CheckBox(QtGui.QCheckBox):
	def __init__(self, text, default=False, settingsKey=None, parent=None):
		QtGui.QCheckBox.__init__(self, text, parent)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			self.setCheckState(  QtCore.Qt.Checked if default else QtCore.Qt.Unchecked )
		else:
			self.setCheckState(  QtCore.Qt.Checked if settingsValue(self.settingsKey, default).toBool() else QtCore.Qt.Unchecked )
			self.connect(self, QtCore.SIGNAL('stateChanged(int)'), self.onStateChanged)
	def onStateChanged(self):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, self.checkState() == QtCore.Qt.Checked)

class ComboBox(QtGui.QComboBox):
	def __init__(self, choices, default='', failsave=False, settingsKey=None, parent=None):
		QtGui.QComboBox.__init__(self, parent)
		self.addItems(choices)
		self.settingsKey = settingsKey
		if self.settingsKey is None:
			value = default
		else:
			value = settingsValue(self.settingsKey, default).toString()
			self.connect(self, QtCore.SIGNAL('currentIndexChanged(QString)'), self.onCurrentIndexChanged)
		if failsave:
			if value in choices:
				self.setCurrentIndex(choices.index(value))
		else:
			self.setCurrentIndex(choices.index(value))
	def 	onCurrentIndexChanged(self, qString):
		if self.settingsKey is not None: settingsSetValue(self.settingsKey, qString)

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

#TODO: we have to ignore <TAB> cos it tabs away from the hotkey box
class HotkeyBox(QtGui.QComboBox):
	#NOTE: bit of a hack this combo
	# x) pretty much disbled all standart keybindings for the combo. except ESCAPE and SPACE (ESCAPE
	#     mut be handled internally cos it is working without our help)
	# x) we added a space to each displayName to trrick the combo popup search feature
	Hotkeys = (		# hotkey --> displayName
				('', '<Type On Your Keyboard>'),
				('<ESCAPE>', ' ESCAPE'),
				('<SPACE>', ' SPACE'),
				('<TAB>', ' TAB'),
				(TableCrabWin32.MouseWheelUp, ' MouseWheelUp'),
				(TableCrabWin32.MouseWheelDown, ' MouseWheelDown'),
			)
	def __init__(self, hotkey=None, parent=None):
		QtGui.QComboBox.__init__(self, parent=None)
		self.addItems( [i[1] for i in self.Hotkeys] )
		for i, (tmpHotkey, _) in enumerate(self.Hotkeys):
			if hotkey == tmpHotkey:
				self.setCurrentIndex(i)
				break
		else:
			if hotkey is not None:
				self.setItemText(0, hotkey)
		signalConnect(keyboardHook, self, 'inputEvent(QObject*)', self.onInputEvent)
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
	signalEmit(None, 'widgetScreenshot(int, QPixmap*)', hwnd, pixmap)

#***********************************************************************************
# global Application object
#***********************************************************************************
application = QtGui.QApplication(sys.argv)

#***********************************************************************************
#
#***********************************************************************************

	
	




