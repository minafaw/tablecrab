
#****************************************************************************************
# setup minimal stuff to get at least some information in case something goes wrong
#
# every module should add this module as the very first import
#
#NOTE: if an exception occurs an error.log will be placed in the current directory. good or not?
#***************************************************************************************
import sys, os, traceback, logging
from logging import handlers

TableCrabApplicationName = 'TableCrab2'
TableCrabVersion = '0.1.0'
TableCrabReleaseName = '%s-%s' % (TableCrabApplicationName, TableCrabVersion)
TableCrabAuthor = 'JuergenUrner'
TableCrabErrorLogName = TableCrabApplicationName + '-Error.log'

logger = logging.getLogger(TableCrabApplicationName)
logger.addHandler(handlers.RotatingFileHandler(
		os.path.join(os.getcwd(), TableCrabErrorLogName),
		mode='a',
		maxBytes=32000,
		backupCount=0,
		))
def _excepthook(type, value, tb):
	# as failsave as possible
	p = ''
	p += 'TableCrab: %s\n' % TableCrabReleaseName
	p += 'Platform: %s\n' % sys.platform
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
import posixpath, thread, time, re, atexit
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
	_qSettings = QtCore.QSettings(TableCrabAuthor, TableCrabApplicationName)

#***********************************************************************************
# enshure we run a single application instance only
#***********************************************************************************
class _SingleApp(object):
	def __init__(self):
		self.hMutex = TableCrabWin32.kernel32.CreateMutexA(None, 1, 'Local\\73524668475460800279396959888864133024')
		atexit.register(self.close)
		if TableCrabWin32.GetLastError() == TableCrabWin32.ERROR_INVALID_HANDLE:
			#TODO: we could try to find the app holding the mutex (hopefuly TableCrab) and activate it 
			# gut feeling it is be better to raise and log here, so we get at least some information in case someone blocks our mutex
			##sys.exit(1)
			raise RuntimeError('TableCrab is already running')
	def close(self, closeFunc=TableCrabWin32.kernel32.CloseHandle):	# need to hold reference to CloseHandle here. we get garbage collected otherwise
		closeFunc(self.hMutex)
_singleApp = _SingleApp()

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
	return _qSettings.value( settingsKeyJoin(configKey, key), default)
def settingsSetValue(key, value):
	_qSettings.setValue( settingsKeyJoin(configKey, key), QtCore.QVariant(value) )
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

#***********************************************************************************
# 
#***********************************************************************************
SiteNamePokerStars = 'PokerStars'

#***********************************************************************************
# types
#***********************************************************************************
pointNone = QtCore.QPoint()
sizeNone = QtCore.QSize()

class CallableString(QtCore.QString):
	def __call__(self):
		return self.__class__(self)
	
class CallableFloat(float):
	def __call__(self):
		return self
class CallableBool(object):
	def __init__(self, value):
		self.value = value
	def __call__(self):
		return self.value
	
ValueNone = 'None'

#***********************************************************************************
# persistent items
#***********************************************************************************

import inspect
class PersistentItemManager(QtCore.QObject):
	#NOTE: we can not use __metaclass__ along with QObject. so we have to track actions by hand
	def __init__(self, parent=None, key=None, maxItems=0,itemProtos=None):
		QtCore.QObject.__init__(self, parent)
		self._items = []
		self.maxItems = maxItems
		self.key = key
		self.itemProtos= [] if itemProtos is None else itemProtos
		self._readFinished = False
	def read(self):
		# read items
		if self._readFinished:
			raise ValueError('you can read items only once')
		self._items = []
		if self.key is not None:
			newItems = []
			for slot in xrange(self.maxItems):
				key = settingsKeyJoin(self.key, str(slot) )
				for itemProto in self.itemProtos:
					newItem = itemProto.fromConfig(key)
					if newItem is not None:
						newItems.append( (slot, newItem) )
			for _, item in sorted(newItems):
				self._items.append(item)
				signalEmit(self, 'itemRead(QObject*)', item)
			self.dump()
			self._readFinished = True
			signalEmit(self, 'readFinished()')
	def dump(self):
		settingsRemoveKey(self.key)
		slot = 0
		for item in self._items:
			key = settingsKeyJoin(self.key, str(slot) )
			if item.toConfig(key):
				slot += 1
	def __len__(self): return len(self._items)
	def __iter__(self):
		return iter(self._items)
	def index(self, item):
		return self._items.index(item)
	def canAddItem(self):
		return len(self) < self.maxItems
	def addItem(self, item):
		self._items.append(item)
		if self.key is not None:
			self.dump()
		signalEmit(item,'itemAdded(QObject*)', item)
	def removeItem(self, item):
		self._items.remove(item)
		if self.key is not None:
			self.dump()
		signalEmit(item, 'itemRemoved(QObject*)', item)
	def canMoveItemUp(self, item):
		return self.index(item) > 0
	def canMoveItemDown(self, item):
		return self.index(item) < len(self._items) -1
	def moveItemUp(self, item):
		if not self.canMoveItemUp(item):
			raise valueError('can not move item up')
		index = self.index(item)
		self._items.remove(item)
		self._items.insert(index-1, item)
		if self.key is not None:
			self.dump()
		signalEmit(item, 'itemMovedUp(QObject*, int)', item, index -1)
	def moveItemDown(self, item):
		if not self.canMoveItemDown(item):
			raise valueError('can not move item up')
		index = self.index(item)
		self._items.remove(item)
		self._items.insert(index+1, item)
		if self.key is not None:
			self.dump()
		signalEmit(item, 'itemMovedDown(QObject*, int)', item, index +1)
	def readFinished(self):
		return self._readFinished
	def setItemAttr(self, item, name, value):
		setattr(item, name, value)
		signalEmit(item, 'itemAttrChanged(QObject*, QString)', item, name)
		if self.key is not None:
			self.dump()
	def setItemAttrs(self, item, values):
		for name, value in values.items():
			setattr(item, name, value)
			signalEmit(item, 'itemAttrChanged(QObject*, QString)', item, name)
		if self.key is not None:
			self.dump()


class PersistentItem(QtCore.QObject):
	Attrs = (	# (name, valueType) ..if a kw is None an instance of valuetype is set as default
			)
	def __init__(self, 
			parent=None,
			**kws 
			):
		QtCore.QObject.__init__(self, parent)
		for name, valueType in self.Attrs:
			value = kws.get(name, None)
			if value is None:
				value= valueType()
			setattr(self, name, value)
	def iterAttrs(self):
		for name, _ in self.Attrs:
			yield name, getattr(self, name)

class ActionCheck(PersistentItem):
	Attrs = (
			('name', QtCore.QString),
			('hotkey', QtCore.QString),
			('hotkeyName', QtCore.QString),
			)
	@classmethod
	def itemName(klass):
		return 'Check'
	@classmethod
	def fromConfig(klass, key):
		itemName = settingsValue( settingsKeyJoin(key, 'ItemName'), '').toString()
		if itemName != klass.itemName(): return None
		hotkey = settingsValue( settingsKeyJoin(key, 'Hotkey'), ValueNone).toString()
		if hotkey == ValueNone: return None
		name = settingsValue( settingsKeyJoin(key, 'Name'), '').toString()
		hotkeyName = settingsValue( settingsKeyJoin(key, 'HotkeyName'), '').toString()
		return klass(name=name, hotkey=hotkey, hotkeyName=hotkeyName)
	def toConfig(self, key):
		settingsSetValue( settingsKeyJoin(key, 'ItemName'), self.itemName() )
		settingsSetValue( settingsKeyJoin(key, 'Name'), self.name )
		settingsSetValue( settingsKeyJoin(key, 'Hotkey'), self.hotkey )
		settingsSetValue( settingsKeyJoin(key, 'HotkeyName'), self.hotkeyName)
		return True

class ActionFold(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Fold'

class ActionRaise(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Raise'

class ActionScreenshot(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Screenshot'
		
class ActionHilightBetAmount(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'HilightBetAmount'

class ActionReplayer(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'Replayer'

class ActionInstantHandHistory(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'InstantHandHistory'

class ActionAllIn(ActionCheck):
	@classmethod
	def itemName(klass):
		return 'All-In'


class ActionAlterBetAmount(PersistentItem):
	BaseValues = ('BigBlind', 'SmallBlind', 'CurrentBet')
	Attrs = (
			('name', QtCore.QString),
			('hotkey', QtCore.QString),
			('hotkeyName', QtCore.QString),
			('baseValue', CallableString('BigBlind') ),
			('multiplier', CallableFloat(1.0)),
			)
	@classmethod
	def itemName(klass):
		return 'AlterBetAmount'
	@classmethod
	def fromConfig(klass, key):
		itemName = settingsValue( settingsKeyJoin(key, 'ItemName'), ValueNone).toString()
		if itemName != klass.itemName(): return None
		hotkey = settingsValue( settingsKeyJoin(key, 'Hotkey'), ValueNone).toString()
		if hotkey == ValueNone: return None
		hotkeyName = settingsValue( settingsKeyJoin(key, 'HotkeyName'), '').toString()
		baseValue = settingsValue( settingsKeyJoin(key, 'BaseValue'), ValueNone).toString()
		if baseValue not in klass.BaseValues: return None
		multiplier, ok = settingsValue( settingsKeyJoin(key, 'Multiplier'), 1.0).toDouble()
		if not ok: return None
		name = settingsValue( settingsKeyJoin(key, 'Name'), ValueNone).toString()
		return klass(name=name, hotkey=hotkey, hotkeyName=hotkeyName, baseValue = baseValue, multiplier=multiplier)
	def toConfig(self, key):
		settingsSetValue( settingsKeyJoin(key, 'ItemName'), self.itemName() )
		settingsSetValue( settingsKeyJoin(key, 'Name'), self.name)
		settingsSetValue( settingsKeyJoin(key, 'HotkeyName'), self.hotkeyName)
		settingsSetValue( settingsKeyJoin(key, 'Hotkey'), self.hotkey)
		settingsSetValue( settingsKeyJoin(key, 'BaseValue'), self.baseValue)
		settingsSetValue( settingsKeyJoin(key, 'Multiplier'), self.multiplier)
		return  True

#NOTE: we can not use __metaclass__ along with QObject ..so we have to keep track by hand
Actions = (
		ActionCheck,
		ActionFold,
		ActionRaise,
		ActionAlterBetAmount,
		ActionHilightBetAmount,
		ActionScreenshot,
		ActionAllIn,
		ActionReplayer,
		ActionInstantHandHistory,
		)

MaxActions = 64
class _ActionItemManager(PersistentItemManager):
	def __init__(self, parent=None):
		PersistentItemManager.__init__(self, parent=parent, key='Hotkeys', maxItems=MaxActions, itemProtos=Actions)
		
actionItemManager = _ActionItemManager()


class SetupWidgetItemTablePokerStars(PersistentItem):
	Attrs = (		# name--> valueType
			('name', QtCore.QString),
			('size', QtCore.QSize), 
			('buttonCheck', QtCore.QPoint),
			('buttonFold', QtCore.QPoint),
			('buttonRaise', QtCore.QPoint),
			('checkboxFold', QtCore.QPoint),
			('checkboxCheckFold', QtCore.QPoint),
			('betSliderStart', QtCore.QPoint),
			('betSliderEnd', QtCore.QPoint),
			('instantHandHistory', QtCore.QPoint),
			('replayer', QtCore.QPoint),
			('itemIsExpanded', CallableBool(False)),
			)
	@classmethod
	def itemName(klass):
		return 'PokerStarsTable'
	@classmethod
	def fromConfig(klass, key):
		itemName = settingsValue( settingsKeyJoin(key, 'ItemName'), ValueNone).toString()
		if itemName != klass.itemName(): return None
		name = settingsValue(settingsKeyJoin(key, 'Name'), 'None').toString()
		size = settingsValue(settingsKeyJoin(key, 'Size'), sizeNone).toSize()
		buttonCheck = settingsValue(settingsKeyJoin(key, 'ButtonCheck'), pointNone).toPoint()
		buttonFold = settingsValue(settingsKeyJoin(key, 'ButtonFold'), pointNone).toPoint()
		buttonRaise = settingsValue(settingsKeyJoin(key, 'ButtonRaise'), pointNone).toPoint()
		instantHandHistory = settingsValue(settingsKeyJoin(key, 'InstantHandHistory'), pointNone).toPoint()
		replayer = settingsValue(settingsKeyJoin(key, 'Replayer'), pointNone).toPoint()
		checkboxFold = settingsValue(settingsKeyJoin(key, 'CheckboxFold'), pointNone).toPoint()
		checkboxCheckFold = settingsValue(settingsKeyJoin(key, 'CheckboxCheckFold'), pointNone).toPoint()
		betSliderStart = settingsValue(settingsKeyJoin(key, 'BetSliderStart'), pointNone).toPoint()
		betSliderEnd = settingsValue(settingsKeyJoin(key, 'BetSliderEnd'), pointNone).toPoint()
		itemIsExpanded = settingsValue(settingsKeyJoin(key, 'ItemIsExpanded'), False).toBool()
		return klass(name=name, size=size, buttonCheck=buttonCheck, 
				buttonFold=buttonFold, buttonRaise=buttonRaise, replayer=replayer, instantHandHistory=instantHandHistory, 
				checkboxFold=checkboxFold, checkboxCheckFold=checkboxCheckFold, itemIsExpanded=itemIsExpanded,
				betSliderStart=betSliderStart, betSliderEnd=betSliderEnd)
	def toConfig(self, key):
		settingsSetValue( settingsKeyJoin(key, 'ItemName'), self.itemName() )
		settingsSetValue(settingsKeyJoin(key, 'Name'), self.name)
		settingsSetValue(settingsKeyJoin(key, 'Size'), self.size)
		settingsSetValue(settingsKeyJoin(key, 'ButtonCheck'), self.buttonCheck)
		settingsSetValue(settingsKeyJoin(key, 'ButtonFold'), self.buttonFold)
		settingsSetValue(settingsKeyJoin(key, 'ButtonRaise'), self.buttonRaise)
		settingsSetValue(settingsKeyJoin(key, 'CheckboxFold'), self.checkboxFold)
		settingsSetValue(settingsKeyJoin(key, 'CheckboxCheckFold'), self.checkboxCheckFold)
		settingsSetValue(settingsKeyJoin(key, 'BetSliderStart'), self.betSliderStart)
		settingsSetValue(settingsKeyJoin(key, 'BetSliderEnd'), self.betSliderEnd)
		settingsSetValue(settingsKeyJoin(key, 'Replayer'), self.replayer)
		settingsSetValue(settingsKeyJoin(key, 'InstantHandHistory'), self.instantHandHistory)
		settingsSetValue(settingsKeyJoin(key, 'ItemIsExpanded'), self.itemIsExpanded)
		return True

SetupWidgetItems = (
		SetupWidgetItemTablePokerStars,
		)
MaxSetupWidgetItems = 64
class _SetupWidgetItemManager(PersistentItemManager):
	def __init__(self, parent=None):
		PersistentItemManager.__init__(self, parent=parent, key='Setup/Widgets', maxItems=MaxSetupWidgetItems, itemProtos=SetupWidgetItems)
		
setupWidgetItemManager = _SetupWidgetItemManager()

#***********************************************************************************
# 
#***********************************************************************************
class _SiteManager(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		self._pokerStarsLoginBox = None
	
	def setWindowHook(self, windowHook):
		signalConnect(windowHook, self, 'windowCreated(int)', self.onWindowCreated)
		signalConnect(windowHook, self, 'windowDestroyed(int)', self.onWindowDestroyed)
		signalConnect(windowHook, self, 'windowGainedForeground(int)', self.onWindowGainedForeground)
	
	def onWindowDestroyed(self, hwnd):
		##print 'destroyed: ', hwnd, "'%s'" % windowGetClassName(hwnd), "'%s'" %  windowGetText(hwnd)
		if hwnd == self._pokerStarsLoginBox:
			self._pokerStarsLoginBox = None
		
	def onWindowGainedForeground(self, hwnd):
		##print 'gainedForeground: ', hwnd, "'%s'" % windowGetClassName(hwnd), "'%s'" %  windowGetText(hwnd)
		pass
		
	def onWindowCreated(self, hwnd):
		##print 'created: ',  hwnd, "'%s'" % windowGetClassName(hwnd), "'%s'" %  windowGetText(hwnd)
		
		if self.windowIsPokerStarsPopupNews(hwnd):
			if settingsValue('PokerStars/AutoClosePopupNews', False).toBool():
				TableCrabWin32.windowClose(hwnd)
		
		elif self.windowIsPokerStarsTourneyRegistrationMessageBox(hwnd):
			if settingsValue('PokerStars/AutoCloseTourneyRegistrationBoxes', False).toBool():
				buttons = TableCrabWin32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				##windowClose(hwnd)
				TableCrabWin32.windowClickButton(buttons['OK'])
		
		elif self.windowIsPokerStarsTableMessageBox(hwnd):
			if settingsValue('PokerStars/AutoCloseTableMessageBoxes', False).toBool():
				buttons = TableCrabWin32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				TableCrabWin32.windowClickButton(buttons['OK'])
		
		elif self.windowIsPokerStarsLogIn(hwnd):
			if self._pokerStarsLoginBox is None: 
				self._pokerStarsLoginBox = hwnd
				if settingsValue('PokerStars/AutoCloseLogin', False).toBool():
					buttons = TableCrabWin32.windowGetButtons(hwnd)
					if sorted(buttons) == ['', 'Cancel', 'Create New Account...', 'Forgot User ID / Password...', 'OK']:
						if TableCrabWin32.windowCheckboxIsChecked(buttons['']):
							if TableCrabWin32.windowIsEnabled(buttons['OK']):
								TableCrabWin32.windowClickButton(buttons['OK'])
		
	def handleInput(self, input, keydown=None, nSteps=None):
		hwnd = TableCrabWin32.windowForeground()
		if not hwnd:
			return False
			
		# swallow key release events we handle
		if keydown is False:
			for actionItem in actionItemManager:
				if not actionItem.hotkey: continue
				if not actionItem.hotkey == input: continue
				if self.windowIsPokerStarsTable(hwnd):
					widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)
					if widgetItem is not None:
						return True
				return False
			
		for actionItem in actionItemManager:
			if not actionItem.hotkey: continue
			if not actionItem.hotkey == input: continue
			actionName = actionItem.itemName()
				
			if actionName == ActionScreenshot.itemName():
				widgetScreenshot(hwnd)
				return True
				
			# handle PokerStarsTable
			if self.windowIsPokerStarsTable(hwnd):
				widgetItem = self.pokerStarsGetTableWidgetItem(hwnd)
				if widgetItem is None:
					return False
				
				if actionName == ActionCheck.itemName():
					self.pokerStarsTableHandleCheck(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True
				elif actionName == ActionFold.itemName():
					self.pokerStarsTableHandleFold(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True		
				elif actionName == ActionRaise.itemName():
					self.pokerStarsTableHandleRaise(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True	
				elif actionName == ActionAllIn.itemName():
					self.pokerStarsTableHandleAllIn(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True	
				elif actionName == ActionAlterBetAmount.itemName():
					self.pokerStarsTableHandleAlterBetAmount(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True	
				elif actionName == ActionHilightBetAmount.itemName():
					self.pokerStarsTableHandleHilightBetAmount(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True
				elif actionName == ActionReplayer.itemName():
					self.pokerStarsTableHandleReplayer(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True
				elif actionName == ActionInstantHandHistory.itemName():
					self.pokerStarsTableHandleInstantHandHistory(actionItem, widgetItem, hwnd, nSteps=nSteps)
					return True
			
		return False
		
	# PokerStars	
	#-----------------------------------------------------------------------------------------
	def pokerStarsGetTableWidgetItem(self, hwnd):
		rect = TableCrabWin32.windowGetClientRect(hwnd)
		for persistentItem in setupWidgetItemManager:
			if persistentItem.itemName() == 'PokerStarsTable':
				if persistentItem.size == rect.size():
					return persistentItem
		return None

	
	PokerStarsPatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PokerStarsPatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	PokerStarsClassTableBetAmountBox = 'PokerStarsSliderEditorClass'
	def pokerStarsTableReadData(self, hwnd):
		data = {}
		text = TableCrabWin32.windowGetText(hwnd)
		if not text: return data
		match = self.PokerStarsPatAmountSB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['smallBlind'] = float(match.group(1))
		match = self.PokerStarsPatAmountBB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['bigBlind'] = float(match.group(1))
		hwndBetAmountBox = TableCrabWin32.windowFindChild(hwnd, self.PokerStarsClassTableBetAmountBox)
		data['hwndBetAmountBox'] =  hwndBetAmountBox
		data['betAmountBoxIsVisible'] = TableCrabWin32.windowIsVisible(hwndBetAmountBox )
		data['betAmount'] = None
		if data['hwndBetAmountBox']:
			p = TableCrabWin32.windowGetText(hwndBetAmountBox)
			try:
				data['betAmount'] = float(p)
			except ValueError: pass
		return data
		
	def pokerStarsTableHandleCheck(self, actionItem, widgetItem, hwnd, nSteps=None):
		data = self.pokerStarsTableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if data['betAmountBoxIsVisible']:
			point = widgetItem.buttonCheck
		else:
			point = widgetItem.checkboxCheckFold
		if not point.isNull():
			point = TableCrabWin32.windowClientPointToScreenPoint(hwnd, point)
			TableCrabWin32.mouseClickLeft(point)
		
	def pokerStarsTableHandleFold(self, actionItem, widgetItem, hwnd, nSteps=None):
		data = self.pokerStarsTableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if data['betAmountBoxIsVisible']:
			point = widgetItem.buttonFold
		else:
			point = widgetItem.checkboxFold
		if not point.isNull():
			point = TableCrabWin32.windowClientPointToScreenPoint(hwnd, point)
			TableCrabWin32.mouseClickLeft(point)
			
	
	def pokerStarsTableHandleRaise(self, actionItem, widgetItem, hwnd, nSteps=None):
		data = self.pokerStarsTableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		point = widgetItem.buttonRaise
		if not point.isNull():
			point = TableCrabWin32.windowClientPointToScreenPoint(hwnd, point)
			TableCrabWin32.mouseClickLeft(point)
	
	def pokerStarsTableHandleAllIn(self, actionItem, widgetItem, hwnd, nSteps=None):
		data = self.pokerStarsTableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if widgetItem.betSliderStart.isNull(): return
		if widgetItem.betSliderEnd.isNull(): return
		pointStart = TableCrabWin32.windowClientPointToScreenPoint(hwnd, widgetItem.betSliderStart)
		#TableCrabWin32.mouseClickLeft(pointStart)
		pointEnd = TableCrabWin32.windowClientPointToScreenPoint(hwnd, widgetItem.betSliderEnd)
		TableCrabWin32.mouseDragLeft(pointStart, pointEnd)
		
	def pokerStarsTableHandleAlterBetAmount(self, actionItem, widgetItem, hwnd, nSteps=None):
		data = self.pokerStarsTableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		
		if nSteps == 0: return
		nSteps = 1 if nSteps is None else abs(nSteps)	
		
		if actionItem.baseValue == 'BigBlind':
			baseValue = data['bigBlind']
		elif actionItem.baseValue == 'SmallBlind':
			baseValue = data['smallBlind']
		elif	actionItem.baseValue == 'CurrentBet':
			baseValue = data['betAmount']
		else: raise ValueError('unknown baseVale: %s' %actionItem.baseVale)
			
		newBetAmount = round(data['betAmount'] + (baseValue * actionItem.multiplier * nSteps), 2)
		print newBetAmount, int(newBetAmount)
		if int(newBetAmount) == newBetAmount:
			newBetAmount = int(newBetAmount)
		newBetAmount = str( 0 if newBetAmount < 0 else newBetAmount )
		TableCrabWin32.windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		
	def pokerStarsTableHandleHilightBetAmount(self, actionItem, widgetItem, hwnd, nSteps=None):
		data = self.pokerStarsTableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		point = TableCrabWin32.windowClientPointToScreenPoint(data['hwndBetAmountBox'], QtCore.QPoint(0, 0) )
		TableCrabWin32.mouseClickLeftDouble(point)	#TODO: maybe we need to add a bit of an offset
		
	#NOTE: as a hack we click (0, 0) to reactivate the window cos the dialogs are set to the foreground 
	# and on linux/wine SetForegroundWindow() does not work. 
	def pokerStarsTableHandleReplayer(self, actionItem, widgetItem, hwnd, nSteps=None):
		point = widgetItem.replayer
		if not point.isNull():
			point = TableCrabWin32.windowClientPointToScreenPoint(hwnd, point)
			TableCrabWin32.mouseClickLeft(point)
			# click neutral point to reactivate the table
			point2 = TableCrabWin32.windowClientPointToScreenPoint(hwnd, QtCore.QPoint(0, 0) )
			TableCrabWin32.mouseClickLeft(point2)
			# move mouse back to its former position
			TableCrabWin32.mouseSetPos(point)
		
	def pokerStarsTableHandleInstantHandHistory(self, actionItem, widgetItem, hwnd, nSteps=None):
		point = widgetItem.instantHandHistory
		if not point.isNull():
			point = TableCrabWin32.windowClientPointToScreenPoint(hwnd, point)
			TableCrabWin32.mouseClickLeft(point)
			# click neutral point to reactivate the table
			point2 = TableCrabWin32.windowClientPointToScreenPoint(hwnd, QtCore.QPoint(0, 0) )
			TableCrabWin32.mouseClickLeft(point2)
			# move mouse back to its former position
			TableCrabWin32.mouseSetPos(point)
		
	#NOTE: not easy to determine if a window is a PokerStarswindow. i don't feel like messing around with psapi.dll to get the exefilename.
	# so ..i use a hack. we identify a window as being a stars window if it (or one of its parents) contains a widget classname.startswith('PokerStars')
	# nasty and errorprone, but the most reasonalbe i could come up with now
	def windowHasPokerStarsWidgets(self, hwnd):
		for hwnd in TableCrabWin32.windowChildren(hwnd):
			if TableCrabWin32.windowGetClassName(hwnd).startswith('PokerStars'):	return True
		return False
	
	def windowIsPokerStarsWindow(self, hwnd):
		while hwnd:
			if self.windowHasPokerStarsWidgets(hwnd): return True
			hwnd = TableCrabWin32.windowGetParent(hwnd)
		return False	
	
	PokerStarsTitleLobby = 'PokerStars Lobby'
	PokerStarsClassLobby = '#32770'	# duh, stars. main windows should never be dialogs
	def windowIsPokerStarsLobby(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.PokerStarsClassLobby: return False
		if not TableCrabWin32.windowGetText(hwnd).startswith(self.PokerStarsTitleLobby): return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True
		
	PokerStarsClassTable = 'PokerStarsTableFrameClass'
	def windowIsPokerStarsTable(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.PokerStarsClassTable: return False
		return True	

	PokerStarsClassInstantHandHistory = '#32770'
	PokerStarsTitleInstantHandHistory = 'Instant Hand History'
	def windowIsPokerStarsInstantHandHistory(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.PokerStarsClassInstantHandHistory: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.PokerStarsTitleInstantHandHistory: return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True
		
	PokerStarsClassNews = '#32770'
	PokerStarsTitleNews = 'News'
	def windowIsPokerStarsPopupNews(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.PokerStarsClassNews: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.PokerStarsTitleNews: return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True
		
	PokerStarsTitleTourneyRegistrationMessageBox = 'Tournament Registration'
	PokerStarsClassTourneyRegistrationMessageBox = '#32770'
	def windowIsPokerStarsTourneyRegistrationMessageBox(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.PokerStarsClassTourneyRegistrationMessageBox: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.PokerStarsTitleTourneyRegistrationMessageBox: return False
		if not self.windowIsPokerStarsWindow(hwnd): return False
		return True

	PokerStarsTitleTableMessageBox = 'Tournament Registration'
	PokerStarsClassTableMessageBox = '#32770'
	def windowIsPokerStarsTableMessageBox(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.PokerStarsClassTableMessageBox: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.PokerStarsTitleTableMessageBox: return False
		hwndParent = TableCrabWin32.windowGetParent(hwnd)
		if not self.windowIsPokerStarsTable(hwndParent): return False
		return True
		
	PokerStarsTitleLogIn = 'Log In'
	PokerStarsClassLogIn = '#32770'
	def windowIsPokerStarsLogIn(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.PokerStarsClassLogIn: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.PokerStarsTitleLogIn: return False
		hwndParent = TableCrabWin32.windowGetParent(hwnd)
		if not self.windowIsPokerStarsLobby(hwndParent): return False
		return True

# init siteManager and global hooks
siteManager = _SiteManager()
windowHook = TableCrabWin32.WindowHook(parent=siteManager)
mouseHook = TableCrabWin32.MouseHook(parent=siteManager, eventHandler=siteManager)
keyboardHook = TableCrabWin32.KeyboardHook(parent=siteManager, eventHandler=siteManager)
siteManager.setWindowHook(windowHook)

#***********************************************************************************
# Qt widgets
#***********************************************************************************
class TableCrabAction(QtGui.QAction):
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
			
		
		
class TableCrabWebViewToolBar(QtGui.QToolBar):
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
		
		self.actionZoomIn = TableCrabAction(
				parent=self,
				text='Zoom+',
				icon=QtGui.QIcon(Pixmaps.magnifierPlus() ),
				autoRepeat=True,
				shortcut=QtGui.QKeySequence.ZoomIn,
				slot=self.onActionZoomInTriggered,
				)
		self.addAction(self.actionZoomIn)
		
		self.actionZoomOut = TableCrabAction(
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
			
	
#TODO: rename to TableCrab...
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

def MsgWarning(parent, msg):
	QtGui.QMessageBox.critical(parent, TableCrabApplicationName, msg)

def MsgCritical(parent, msg):
	QtGui.QMessageBox.critical(parent, TableCrabApplicationName, msg)

#***********************************************************************************
# type converters
#***********************************************************************************
def pointToString(qPoint):
	if qPoint.x() <= 0 or qPoint.y() < 0:
		return 'None'
	return '%s,%s' % (qPoint.x(), qPoint.y())

def sizeToString(qSize):
	if qSize.isEmpty():
		return 'None'
	return '%sx%s' % (qSize.width(), qSize.height())

def isClientPoint(point):
	return point.x() >= 0 and point.y() >= 0
	

def widgetScreenshot(hwnd):
	pixmap = QtGui.QPixmap.grabWindow(hwnd, 0, 0, -1,-1)
	signalEmit(None, 'widgetScreenshot(int, QPixmap*)', hwnd, pixmap)

#***********************************************************************************
# global Application and ainWindow object
#***********************************************************************************

class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.setWindowTitle(TableCrabReleaseName)
		self.setWindowIcon( QtGui.QIcon(Pixmaps.tableCrab()) )
		font = QtGui.QFont()
		if font.fromString(settingsValue('Gui/Font', '').toString() ):
			QtGui.qApp.setFont(font)
		self.restoreGeometry( settingsValue('Gui/Geometry', QtCore.QByteArray()).toByteArray() )
	def show(self):
		style = settingsValue('Gui/Style', '').toString()
		QtGui.qApp.setStyle(QtGui.QStyleFactory.create(style))
		QtGui.QMainWindow.show(self)
		mouseHook.start()
		keyboardHook.start()
		windowHook.start()
		actionItemManager.read()
		setupWidgetItemManager.read()
	def closeEvent(self, event):
		signalEmit(None, 'closeEvent(QEvent*)', event)
		mouseHook.stop()
		keyboardHook.stop()
		windowHook.stop()
		settingsSetValue('Gui/Geometry', self.saveGeometry() )
		return QtGui.QMainWindow.closeEvent(self, event)
	def start(self):
		self.show()
		application.exec_()
	
application = QtGui.QApplication(sys.argv)


#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': MainWindow().start()
	
	
	




