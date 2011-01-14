
#TODO: we have to find a way to limit text length in QPlainTextEdit


#************************************************************************************
# project consts
#************************************************************************************
ApplicationName = 'TableCrab2'
Version = '0.6.6'
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
import posixpath, thread, inspect, random
from PyQt4 import QtCore, QtGui

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
MaxDisplayFileName = 32	# maximum number of chars displayed for file names

MaxProxyHostName = 1024
MaxProxyUserName = 2048
MaxProxyPassword = 2048

MinProxyPort = 0
MaxProxyPort = 99999
DefaultProxyPort = 80

MinFetchTimeout = 1.0
MaxFetchTimeout = 20.0
DefaultFetchTimeout = 4.0

WebViewZoomStepsDefault = 10
WebViewZoomStepsMax = 40
WebViewZoomStepsMin = 1
WebViewZoomMin = 0.5
WebViewZoomMax = 7

SmallBlind = 'SmallBlind'
BigBlind = 'BigBlind'

RoundBetsNoRounding = 'NoRounding'
RoundBetsBigBlind = BigBlind
RoundBetsSmallBlind = SmallBlind
RoundBetsDefault = RoundBetsNoRounding
RoundBets = (RoundBetsNoRounding, RoundBetsBigBlind, RoundBetsSmallBlind)

ToolBarPositionBottom = 'Bottom'
ToolBarPositionTop = 'Top'
ToolBarPositionDefault= ToolBarPositionTop
ToolBarPositions = (ToolBarPositionBottom, ToolBarPositionTop)

TabPositionBottom = 'Bottom'
TabPositionTop = 'Top'
TabPositionDefault= ToolBarPositionTop
TabPositions = (TabPositionBottom, TabPositionTop)

HandViewerSideBarPositionTop = 'Top'
HandViewerSideBarPositionBottom = 'Bottom'
HandViewerSideBarPositionLeft = 'Left'
HandViewerSideBarPositionRight = 'Right'
HandViewerSideBarPositionDefault = HandViewerSideBarPositionRight
HandViewerSideBarPositions = (
		HandViewerSideBarPositionTop,
		HandViewerSideBarPositionBottom,
		HandViewerSideBarPositionLeft,
		HandViewerSideBarPositionRight,
		)

HandViewerMaxPlayerNameMin = -1
HandViewerMaxPlayerNameMax = 999
HandViewerMaxPlayerNameDefault = -1

HoldemResourcesHandHistoryViewerRequestDelay = 0.2

DefaultClockSpeed = 1.0
DefaultClockIncrement = 1
DefaultClockPrecission = 1

CardProtectorAutoToggleDefault = False
CardProtectorAutoToggleTimeoutMin = 0.1
CardProtectorAutoToggleTimeoutMax = 20.0
CardProtectorAutoToggleTimeoutDefault = 3.0

HelpTopics = [
		('index', 'TableCrab'), [
			('versionHistory', 'Version History'),
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
				('hotkeyClick1', 'Click1'),
				('hotkeyClick2', 'Click2'),
				('hotkeyClick3', 'Click3'),
				('hotkeyClick4', 'Click4'),
				('hotkeyClick5', 'Click5'),
				('hotkeyCardProtector', 'Card Protector'),

				],
			('handViewer', 'Hand Viewer'),
			('help', 'Help'),
			('settings', 'Settings'), [
				('settingsGlobal', 'Global'),
				('settingsNetwork', 'Network'),
				('settingsPokerStars', 'PokerStars'),
				('settingsHandViewer', 'Hand Viewer'),
				('settingsHandViewerStyleSheet', 'Hand Viewer Style Sheet'),
				('settingsNashCalculationsStyleSheet', 'Nash Calculations Style Sheet'),
				('settingsCardProtector', 'Card Protector'),
				('settingsClock', 'Clock'),
				],

			('tools', 'Tools'), [
				('toolsFPPCalculator', 'FPP calculator'),
				('toolsHandHistoryViewer', 'Hand history viewer'),
				],
			('developement', 'Developement'), [
				('ocrEditor', 'Ocr Editor'),
				],
			('About', 'About'),
			],
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
# needs rename: typo in: 'PokerStarsHandGrabber/HandFornmatterHtmlTabular' --> should read "For[n]matter"

#TODO: we have to use this key at two places: 1) Gui 2) settingsGlobal
SettingsKeySingleApplicationScope ='Gui/SingleApplication/Scope'


class Settings:
	qSettings = QtCore.QSettings(Author, ApplicationName)

def settingsKeyJoin(*keys):
	keys = [(str(key) if isinstance(key, QtCore.QString) else key) for key in keys if key]
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

	# settings objects should initialize themselves in response to this signal
	initSettings = QtCore.pyqtSignal()
	# emitted when the all settings are up and alive. param is globalObject
	#NOTE: for dynamically created widgets you may have to call the respective slot
	initSettingsFinished = QtCore.pyqtSignal(QtCore.QObject)
	# emitted when the gui is up and alive. param is globalObject
	initGuiFinished = QtCore.pyqtSignal(QtCore.QObject)
	# emitted when the gui is about to close
	closeEvent = QtCore.pyqtSignal(QtCore.QEvent)

	# inform listeners about objects created
	objectCreatedMainWindow = QtCore.pyqtSignal(QtGui.QWidget)
	objectCreatedHotkeyManager = QtCore.pyqtSignal(QtGui.QWidget)
	objectCreatedTemplateManager = QtCore.pyqtSignal(QtGui.QWidget)
	objectCreatedSettingsGlobal = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSettingsNetwork = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSettingsPokerStars = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSettingsHandViewer = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSettingsHandViewerStyleSheet = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSettingsNashCalculationsStyleSheet = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSettingsClock = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSettingsCardProtector = QtCore.pyqtSignal(QtCore.QObject)
	objectCreatedSiteHandlerPokerStars = QtCore.pyqtSignal(QtCore.QObject)

	#TODO: overload signal to accept QObject as well
	feedback = QtCore.pyqtSignal(QtGui.QWidget, QtCore.QString)
	feedbackMessage = QtCore.pyqtSignal(QtCore.QString)
	feedbackException = QtCore.pyqtSignal(QtCore.QString)
	clearException = QtCore.pyqtSignal()

	# new screenshot created (hwnd, pixmap)
	widgetScreenshot = QtCore.pyqtSignal(int, QtGui.QPixmap)
	# a screenshot has been double clicked in the screenshot widget
	widgetScreenshotDoubleClicked = QtCore.pyqtSignal(QtGui.QPixmap, QtCore.QPoint)
	# query screenshot widget for screenshot --> signal widgetScreenshotSet()
	widgetScreenshotQuery = QtCore.pyqtSignal()
	# a sceenshot has been set to screenshot widget. a null pixmap is passed if no screenshot has been set
	widgetScreenshotSet = QtCore.pyqtSignal(QtGui.QPixmap)

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.mainWindow = self.objectCreatedMainWindow.connect(lambda obj, self=self: setattr(self, 'mainWindow', obj))
		self.windowHook = Tc2Win32.WindowHook(parent=self, timeout=WindowHookTimeout)
		self.mouseHook = Tc2Win32.MouseHook(parent=self)
		self.keyboardHook = Tc2Win32.KeyboardHook(parent=self)
		self.hotkeyManager = self.objectCreatedHotkeyManager.connect(lambda obj, self=self: setattr(self, 'hotkeyManager', obj))
		templateManager = self.objectCreatedTemplateManager.connect(lambda obj, self=self: setattr(self, 'templateManager', obj))
		self.settingsGlobal = self.objectCreatedSettingsGlobal.connect(lambda obj, self=self: setattr(self, 'settingsGlobal', obj))
		self.settingsNetwork = self.objectCreatedSettingsNetwork.connect(lambda obj, self=self: setattr(self, 'settingsNetwork', obj))
		self.settingsPokerStars = self.objectCreatedSettingsPokerStars.connect(lambda obj, self=self: setattr(self, 'settingsPokerStars', obj))
		self.settingsHandViewer = self.objectCreatedSettingsHandViewer.connect(lambda obj, self=self: setattr(self, 'settingsHandViewer', obj))
		self.settingsPHandViewerStyleSheet = self.objectCreatedSettingsHandViewerStyleSheet.connect(lambda obj, self=self: setattr(self, 'settingsHandViewerStyleSheet', obj))
		self.settingsNashCalculationsStyleSheet = self.objectCreatedSettingsNashCalculationsStyleSheet.connect(lambda obj, self=self: setattr(self, 'settingsNashCalculationsStyleSheet', obj))
		self.settingsClock = self.objectCreatedSettingsClock.connect(lambda obj, self=self: setattr(self, 'settingsClock', obj))
		self.settingsCardProtector = self.objectCreatedSettingsCardProtector.connect(lambda obj, self=self: setattr(self, 'settingsCardProtector', obj))
		self.siteHandlerPokerStars = self.objectCreatedSiteHandlerPokerStars.connect(lambda obj, self=self: setattr(self, 'siteHandlerPokerStars', obj))

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
	#NOTE: "pgm" works even though it is not listed
	if 'pgm' not in fmts:
		fmts.append('pgm')
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
		roundBets = globalObject.settingsGlobal.roundBets()
		if roundBets in (RoundBetsBigBlind, RoundBetsSmallBlind):
			blind = blinds[1] if roundBets == RoundBetsBigBlind else blinds[0]
			bet = bet * 100
			blind = blind * 100
			d, r = divmod(bet, blind)
			bet = d * blind
			if float(r)/blind >= 0.5:
				bet += blind
			bet = round(bet / 100, 2)
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
class ClockLabel(QtGui.QLabel):
	SpeedMin = 0.2
	SpeedMax = 5.0
	PrecissionMin = 1
	PrecissionMax = 5
	IncrementMin = 1
	IncrementMax = 100
	def __init__(self, parent=None, precission=PrecissionMin, increment=IncrementMin, speed=SpeedMin, randomMode=False):
		QtGui.QLabel.__init__(self, parent)
		self._precission = precission
		self. _increment = increment
		self._randomMode = randomMode
		self._value = 0
		self.setText(str(self._value).zfill(self._precission))
		self._timer = QtCore.QTimer(self)
		self._timer.setInterval(speed * 1000)
		self._timer.timeout.connect(self.tick)
		globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
	def onGlobalObjectInitSettingsFinished(self, globalObject):
		settings = globalObject.settingsClock
		self.setOn(settings.isOn())
		settings.isOnChanged.connect(self.setOn)
		self.setIncrement(settings.increment())
		settings.incrementChanged.connect(self.setIncrement)
		self.setPrecission(settings.precission())
		settings.precissionChanged.connect(self.setPrecission)
		self.setSpeed(settings.speed())
		settings.speedChanged.connect(self.setSpeed)
		self.setRandomMode(settings.randomMode())
		settings.randomModeChanged.connect(self.setRandomMode)
	def setIncrement(self, value):
		wasOn = self.setOn(False)
		self._increment = value
		if wasOn: self.setOn(True)
	def setPrecission(self, value):
		wasOn = self.setOn(False)
		self._precission = value
		if wasOn: self.setOn(True)
	def setSpeed(self, value):
		wasOn = self.setOn(False)
		self._timer.setInterval(value * 1000)
		if wasOn: self.setOn(True)
	def setRandomMode(self, flag):
		self._randomMode = flag
	def isOn(self):
		return self._timer.isActive()
	def setOn(self, flag):
		wasOn = self._timer.isActive()
		self._timer.start() if flag else self._timer.stop()
		return wasOn
	def tick(self):
		maxValue = 10**self._precission
		if self._randomMode:
			value = random.randint(1, maxValue)
			f = float(value) / self._increment
			self._value = int(self._increment * round(f, 0) )
		else:
			self._value += self._increment
		if self._value >= maxValue:
			self._value = 0
		self.setText(str(self._value).zfill(self._precission))


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
			return self._currentRow
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
		return self._grid.newRow()
	#TODO: GridBox.col() can not handle right to left rowspaning columns
	def col(self, widget, colspan=1, rowspan=1, align=None, debug=False):
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
		if align:
			method(widget, y, x, h, w, align)
		else:
			method(widget, y, x, h, w)
		return self
	def clear(self):
		while self.takeAt(0) is not None: pass
		self._grid = self.Grid()


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

		globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		globalObject.keyboardHook.inputEvent.connect(self.onInputEvent)

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


