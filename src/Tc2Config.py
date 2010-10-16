
#TODO: we have to find a way to limit text length in QPlainTextEdit


#************************************************************************************
# project consts
#************************************************************************************
ApplicationName = 'TableCrab2'
Version = '0.4.0'
ReleaseName = '%s-%s' % (ApplicationName, Version)
Author = 'JuergenUrner'
ErrorLogName = ApplicationName + '-Error.log'

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
	p += 'Application: %s\n' % releaseName
	p += 'Platform: %s %s\n' % (platform.system(), platform.release() )
	p += 'PythonVersion: %s\n' % sys.version.split()[0]
	try:
		from PyQt4.QtCore import qVersion, PYQT_VERSION_STR
		p += 'QtVersion: %s\n' % qVersion()
		p += 'PyQtVersion: %s\n' % PYQT_VERSION_STR
	except Exception,d:
		print '>>%s: %s' % (releaseName, d)
		p += 'QtVersion: Unknown\n'
		p += 'PyQtVersion: Unknown\n'
	try:
		import sipconfig
		p += 'SipVersion: %s\n' % sipconfig.Configuration().sip_version_str
	except  Exception,d:
		print '>>%s: %s' % (releaseName, d)
		p += 'SipVersion: Unknown\n'
	try:
		from PyQt4 import QtWebKit
		p += 'WebKitVersion: %s\n' % QtWebKit.qWebKitVersion()
	except:
		p += 'WebKitVersion: Unknown\n'
	p += ''.join(traceback.format_exception(type, value, tb))
	if data is not None:
		try:
			p += data
		except Exception, d:
			print '>>%s: %s' % (releaseName, d)
	try:
		globalObject.feedbackException.emit(p)
	except Exception, d:
		print '>>%s: %s' % (releaseName, d)
	try:	# try to log
		logger.critical(p)
	except Exception, d:
		print '>>%s: %s' % (releaseName, d)
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
import posixpath, thread, inspect
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork

import Tc2Win32
from Tc2Res import Pixmaps, HtmlPages, StyleSheets

#************************************************************************************
# consts
#************************************************************************************
# explicitely set locale to US
QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates) )
locale = QtCore.QLocale()


SingleApplicationMagicString = '73524668475460800279396959888864133024'
SingleApplicationScopeDefault = Tc2Win32.SingleApplication.ScopeSession

MaxHotkeys = 64
MaxTemplates = 64
MaxName = 32		# arbitrary, maximum number of chars allowed in user supplied names
								# for now we hard code it here. would require some efford for status bar
								#to get it dynamically truncated
								# ++ we need to set some limit to template name editing

WindowHookTimeout = 0.2
HandGrabberTimeout = 0.4
StatusBarMessageTimeout = 3
MaxHandGrabberPrefix = 16	# + postfix
MaxHandStyleSheet = 9000

#TODO: implement consts
# let QWebKit deal with it
##MaxHandHtml = 0
# no idea about this one
##MaxScreenshotSize = 0

Ellipsis = '..'
MaxWindowText = 512		# maximum number of chars we retrieve as text / title from other windows
MaxHandHistoryText = 16384
MaxPokerStarsBetBoxText = 16	# maximum number of chars to retrieve from PS bet amount box


SmallBlind = 'SmallBlind'
BigBlind = 'BigBlind'

RoundBetsNoRounding = 'NoRounding'
RoundBetsBigBlind = BigBlind
RoundBetsSmallBlind = SmallBlind
RoundBetsDefault = RoundBetsNoRounding
RoundBets = (RoundBetsNoRounding, RoundBetsBigBlind, RoundBetsSmallBlind)

HelpTopics = [
		('index', 'TableCrab'), [
			('setup', 'Setup'), [
				('screenshotInfo', 'Screenshot Info Dialog'),
				],
			('hotkeys', 'Hotkeys'), [
				('hotkeyCheck', 'Check'),
				('hotkeyFold', 'Fold'),
				('hotkeyRaise', 'Raise'),
				('hotkeyAll_In', 'All-in'),
				('hotkeyHilightBet', 'Hilight Bet'),
				('hotkeyBetPot', 'Bet Pot'),
				('hotkeyMultiplyBlind', 'Multiply Blind'),
				('hotkeyMultiplyBet', 'Multiply Bet'),
				('hotkeyAddToBet', 'Add To Bet'),
				('hotkeySubtractFromBet', 'Subtract From Bet'),
				('hotkeyReplayer', 'Replayer'),
				('hotkeyInstantHandHistory', 'Instant Hand History'),
				('hotkeyScreenshot', 'Screenshot'),
				('hotkeyTableSizeNext', 'Table Size Next'),
				],
			('handViewer', 'Hand Viewer'),
			('settings', 'Settings'), [
				('settingsGlobal', 'Global'),
				('settingsPokerStars', 'PokerStars'),
				('settingsHandViewer', 'Hand Viewer'),
				('settingsHandViewerStyleSheet', 'Hand Viewer Style Sheet'),
				],
			],
		('versionHistory', 'Version History'),
		]

#***********************************************************************************
# global QSettings
#***********************************************************************************
#TODO: what to do with deprecated settings keys?
# deprecated: Gui/WebView/ZoomIncrement
# needs rename: Hotkeys/$Slot$/Hotkey --> Hotkeys/$Slot$/Key
# needs rename: Gui/Settings/HandStyleSheet/DialogOpen/State --> Gui/Settings/HandViewerStyleSheet/DialogOpen/State
# needs rename: Gui/Settings/HandStyleSheet/DialogSave/State --> Gui/Settings/HandViewerStyleSheet/DialogSave/State
# needs rename: Gui/Hand/DialogOpen/State --> Gui/HandViewer/DialogOpen/State
# needs rename: Gui/Hand/DialogSave/State --> Gui/HandViewer/DialogSave/State
# needs rename: Gui/Hand/ZoomFactor --> Gui/HandViewer/ZoomFactor

class Settings:
	qSettings = QtCore.QSettings(Author, ApplicationName)

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

	#TODO: overload signal to accept QObject as well
	feedback =  QtCore.pyqtSignal(QtGui.QWidget, QtCore.QString)
	feedbackMessage =  QtCore.pyqtSignal(QtCore.QString)
	feedbackException =  QtCore.pyqtSignal(QtCore.QString)
	clearException = QtCore.pyqtSignal()

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
# other global objects
#***********************************************************************************
windowHook = Tc2Win32.WindowHook(parent=None, timeout=WindowHookTimeout)
mouseHook = Tc2Win32.MouseHook(parent=None)
keyboardHook = Tc2Win32.KeyboardHook(parent=None)
#TODO: how to make hotkeyManager and templateManager globally available?
# currenly each of them assigns itsself here on init()
hotkeyManager = None
templateManager = None

#***********************************************************************************
# types
#***********************************************************************************
PointNone = QtCore.QPoint(-1, -1)
def newPointNone():
	return QtCore.QPoint(PointNone.x(), PointNone.y() )
SizeNone = QtCore.QSize(-1, -1)
def newSizeNone():
	return QtCore.QSize(SizeNone.width(), SizeNone.height() )

KeyNone = 'None'

#***********************************************************************************
# methods
#***********************************************************************************
#NOTE: on every change in templates and hotkeys we dum the whole TreeWidget to settings.
# easy but brutal. no idea if it is worth the trouble to implement a more sensible mechanism.
#NOTE: if something goes wrong after settingsRemoveKey() we are doomed
def dumpPersistentItems(settigsKey, items):
	settingsRemoveKey(settigsKey)
	slot = 0
	for item in items:
		mySettingsKey = settingsKeyJoin(settigsKey, str(slot) )
		if item.toConfig(mySettingsKey):
			slot += 1

def readPersistentItems(settingsKey, maxItems=0, itemProtos=None):
	itemProtos = () if itemProtos is None else itemProtos
	newItems = []
	for slot in xrange(maxItems):
		mySettingsKey = settingsKeyJoin(settingsKey, str(slot) )
		for itemProto in itemProtos:
			newItem = itemProto.fromConfig(mySettingsKey)
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

def readWriteImageFormats():
	'''returns a list of image formats we can read AND write'''
	fmts = []
	write = [str(i) for i in QtGui.QImageWriter.supportedImageFormats()]
	read = [str(i) for i in QtGui.QImageReader.supportedImageFormats()]
	for fmt in write:
		if fmt == 'ico': continue
		if fmt in read:
			fmts.append(fmt.lower())
	return fmts

def formatedBet(bet, blinds=None):
	'''fromats and adjusts bet size to user settings
	@param bet: (int, float) bet size to format
	@param blinds: (tuple) smallBlind, bigBlind
	@return: (str) new bet size
	'''
	if bet < 0:
		return '0'
	bet = round(bet, 2)
	if blinds is not None:
		roundTo = settingsValue('Settings/RoundBets', '')
		if roundTo in (RoundBetsBigBlind, RoundBetsSmallBlind):
			blind = blinds[1] if roundTo == RoundBetsBigBlind else blinds[0]
			bet = bet * 100
			blind = blind * 100
			d, r = divmod(bet, blind)
			bet = d * blind
			if float(r)/blind >= 0.5:
				bet += blind
			bet = round(bet / 100, 2)
	print bet == int(bet)
	if int(bet) == bet:
		bet = int(bet)
	return str(bet)

def setTabOrder(parent, *widgets):
	for i, widget in enumerate(widgets):
		if i +1 < len(widgets):
			parent.setTabOrder(widget, widgets[i+1])

def walkHelpTopics():
	def walker(item, level=0):
		if not isinstance(item, list):
			yield level -1, item
		else:
			for child in item:
				for x in walker(child, level=level +1):
					yield x
	return walker(HelpTopics)

#***********************************************************************************
# some Qt wrappers to make live easier
#***********************************************************************************
class WebViewToolBar(QtGui.QToolBar):
	ZoomStepsDefault = 10
	ZoomStepsMax = 40
	ZoomStepsMin = 1
	ZoomMin = 0.5
	ZoomMax = 7
	def __init__(self, webView, settingsKeyZoomFactor=None, settingsKeyZoomSteps=None):
		QtGui.QToolBar.__init__(self, webView)
		self.webView = webView
		self.settingsKeyZoomFactor = settingsKeyZoomFactor
		self.settingsKeyZoomSteps = settingsKeyZoomSteps

		globalObject.init.connect(self.onInit)

		self.actionBack = self.webView.pageAction(QtWebKit.QWebPage.Back)
		self.actionBack.setShortcut(QtGui.QKeySequence.Back)
		self.actionBack.setToolTip('Back (Alt+-)')
		self.addAction(self.actionBack)
		self.actionForward = self.webView.pageAction(QtWebKit.QWebPage.Forward)
		self.actionForward.setToolTip('Forward (Alt++)')
		self.actionForward.setShortcut(QtGui.QKeySequence.Forward)
		self.addAction(self.actionForward)

		self.actionZoomIn = QtGui.QAction(self)
		self.actionZoomIn.setText('ZoomIn (Ctrl++)')
		self.actionZoomIn.setIcon(QtGui.QIcon(Pixmaps.magnifierPlus() ) )
		self.actionZoomIn.setShortcut(QtGui.QKeySequence.ZoomIn)
		self.actionZoomIn.setAutoRepeat(True)
		self.actionZoomIn.triggered.connect(self.zoomIn)
		self.addAction(self.actionZoomIn)

		self.actionZoomOut = QtGui.QAction(self)
		self.actionZoomOut.setText('ZoomIn (Ctrl+-)')
		self.actionZoomOut.setIcon(QtGui.QIcon(Pixmaps.magnifierPlus() ) )
		self.actionZoomOut.setShortcut(QtGui.QKeySequence.ZoomOut)
		self.actionZoomOut.setAutoRepeat(True)
		self.actionZoomOut.triggered.connect(self.zoomOut)
		self.addAction(self.actionZoomOut)

	def onInit(self):
		if self.settingsKeyZoomFactor is not None:
			factor = settingsValue(self.settingsKeyZoomFactor, 1).toDouble()[0]
			self.webView.setZoomFactor(factor)
		self.adjustActions()

	def _zoomSteps(self):
		if self.settingsKeyZoomSteps is not None:
			steps = settingsValue(self.settingsKeyZoomSteps, self.ZoomStepsDefault).toInt()[0]
			if steps > self.ZoomStepsMax:
				steps = self.ZoomStepsDefault
			elif steps < 1:
				stape = 1
		else:
			steps = self.ZoomSteps
		return steps

	def _nextZoom(self, zoomIn=True):
		factor = self.webView.zoomFactor()
		steps = self._zoomSteps()
		if zoomIn:
			factor += self.ZoomMax / float(steps)
			factor = min(factor, self.ZoomMax)
		else:
			factor -= self.ZoomMax / float(steps)
			factor = max(factor, self.ZoomMin)
		self.webView.setZoomFactor(factor)
		if self.settingsKeyZoomFactor is not None:
			settingsSetValue(self.settingsKeyZoomFactor, factor)
		self.adjustActions()

	def zoomIn(self):
		self._nextZoom(zoomIn=True)

	def zoomOut(self):
		self._nextZoom(zoomIn=False)

	def adjustActions(self):
		self.actionZoomIn.setEnabled(self.webView.zoomFactor() < self.ZoomMax)
		self.actionZoomOut.setEnabled( self.webView.zoomFactor() > self.ZoomMin)


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

	class Grid(object):
		def __init__(self):
			self._items = [[]]
			self._currentRow = 0
		def pprint(self):
			for row in self._items:
				print ''.join(['x' if item else 'o' for item in row])
		def newRow(self):
			self._currentRow += 1
			if self._currentRow +1 > len(self._items):
				self._items.append([False]*len(self._items[self._currentRow -1]))
		def newColumn(self, w, h):
			row = self._items[self._currentRow]
			row = [(item, i) for (i, item) in enumerate(row)]
			row.sort()
			slot = len(row)
			if row and not row[0][0]:
				slot = row[0][1]
			# pad rows if nrcessary
			if len(self._items) <= self._currentRow + h:
				pad = self._currentRow + h - len(self._items)
				for i in range(pad):
					self._items.append([False]*len(row))
			# pad columns if necessary
			for row in self._items:
				if len(row) < slot + w:
					pad = slot + w - len(row)
					row.extend([False]*pad)
			# expand item
			currentRow = self._currentRow
			for y in xrange(0, h):
				row = self._items[currentRow]
				slot + w
				for x in xrange(slot, slot + w):
					row[x] = True
				currentRow += 1
			return [slot, self._currentRow, w, h]

	def __init__(self, *args):
		QtGui.QGridLayout.__init__(self, *args)
		self.setContentsMargins(contentsMargins)
		self._grid = self.Grid()
	def row(self):
		self._grid.newRow()
	#TODO: GridBox.col() can not handle right to left rowspaning columns
	def col(self, widget, colspan=1, rowspan=1, debug=False):
		if rowspan < 1: raise ValueError('rowspan must be > 0')
		if colspan < 1: raise ValueError('colspan must be > 0')
		x, y, w, h = self._grid.newColumn(colspan, rowspan)
		if debug:
			print x, y, w, h
		if isinstance(widget, QtGui.QWidget):
			method = self.addWidget
		elif isinstance(widget, QtGui.QLayout):
			method = self.addLayout
		else:
			raise ValueError('widget must be QWidget or QLayout')
		method(widget, y, x, h, w)
		return self

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

class HotkeyBox(QtGui.QComboBox):
	#NOTE: bit of a hack this combo
	# x) pretty much disbled all standart keybindings for the combo. except ESCAPE and SPACE (ESCAPE
	#     mut be handled internally cos it is working without our help)
	# x) we added a space to each displayName to trrick the combo popup search feature
	Keys = (		# hotkey --> displayName
				('', '<Type Keys Your Keyboard>'),
				('<Escape>', ' Escape'),
				('<Space>', ' Space'),
				('<Tab>', ' Tab'),
				(Tc2Win32.MouseWheelUp, ' MouseWheelUp'),
				(Tc2Win32.MouseWheelDown, ' MouseWheelDown'),
			)
	def __init__(self, key=None, parent=None):
		QtGui.QComboBox.__init__(self, parent=None)
		self._counter = 0
		self.addItems( [i[1] for i in self.Keys] )
		for i, (tmpKey, _) in enumerate(self.Keys):
			if key == tmpKey:
				self.setCurrentIndex(i)
				break
		else:
			if key is not None:
				self.setItemText(0, key)
		keyboardHook.inputEvent.connect(self.onInputEvent)

	#TODO: open HotkeyBox popup when the user clicks the combo twice. good or not?
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
				for (myKey, _) in self.Keys:
					if inputEvent.key == myKey:
						break
				else:
					self.setItemText(0, inputEvent.key)
	def key(self):
		text = self.currentText()
		for key, displayName in self.Keys:
			if text == displayName:
				#NOTE: we have to make shure to return QString here. QString hashes differenty than str
				return QtCore.QString(key)
		return text

class TreeWidgetItemIterator(QtGui.QTreeWidgetItemIterator):
	def __init__(self, *args):
		QtGui.QTreeWidgetItemIterator.__init__(self, *args)
	def __iter__(self):
		while True:
			value = self.value()
			if value:
				yield value
			else:
				break
			self.__iadd__(1)
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
			defaultSuffix=None,
			):
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
	if defaultSuffix is not None:
		dlg.setDefaultSuffix(defaultSuffix)
	if settingsKey is not None:
		dlg.restoreState( settingsValue(settingsKey, QtCore.QByteArray()).toByteArray() )
	result = dlg.exec_()
	if settingsKey is not None:
		settingsSetValue(settingsKey, dlg.saveState() )
	if result == dlg.Accepted:
		return dlg.selectedFiles()[0]
	return None


#************************************************************************************
# customized network access manager so we can serve raw data from anywhere
#
#************************************************************************************
class RawNetworkReply(QtNetwork.QNetworkReply):
	# this thingy will hand out everything you throw at it via setData()
	def __init__(self, parent=None):
		QtNetwork.QNetworkReply.__init__(self, parent)
		self._data = None
		self._dataPos = 0
		QtCore.QTimer.singleShot(0, self, QtCore.SIGNAL("readyRead()"))
		self.open(self.ReadOnly | self.Unbuffered)
	def abort(self):	pass
	def bytesAvailable(self):
		if self._data is None:
			return 0
		return len(self._data)
	def isSequential(self): return True
	def readData(self, maxSize):
		if self._data is None or self._dataPos >= len(self._data) -1:
			self.finished.emit()
			arr = QtCore.QByteArray()
			arr += ''
			return arr.data()
		stop = self._dataPos + maxSize
		if stop > len(self._data):
			stop = len(self._data) -1
		data = self._data[self._dataPos:stop]
		self._dataPos = stop
		if self._dataPos >= len(self._data) -1:
			self.finished.emit()
		arr = QtCore.QByteArray()
		arr += data
		return arr.data()
	def setData(self, data, mimeType):
		self.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant(mimeType))
		self._data = data
	def hasData(self):
		return self._data is not None

# usage:
# 1) connect to signal getData()
# 2) this thing will throw a networkReply at your slot
# 3) dump data to the reply via networkReply.setData(data, mimeType)
#     not setting data or setting data to None will serve whatever QWebKit serves as default
#NOTE: QNetworkAccessManager is quite a bitch. slightest err will segfault
class RawNetworkAccessManager(QtNetwork.QNetworkAccessManager):

	getData =  QtCore.pyqtSignal(RawNetworkReply)

	def __init__(self, oldManager, parent=None):
		QtNetwork.QNetworkAccessManager.__init__(self, parent)
		self.oldManager = oldManager
		self.setCache(oldManager.cache())
		self.setCookieJar(oldManager.cookieJar())
		self.setProxy(oldManager.proxy())
		self.setProxyFactory(oldManager.proxyFactory())

	def createRequest(self, operation, request, data):
		#NOTE: from previous versions of Qt i found we can not keep the url bcause Qt nulls it on return
		url = QtCore.QUrl(request.url())
		if operation == self.GetOperation:
			networkReply = RawNetworkReply(parent=self)
			networkReply.setUrl(url)
			self.getData.emit(networkReply)
			if networkReply.hasData():
				return networkReply
		return QtNetwork.QNetworkAccessManager.createRequest(self, operation, request, data)




