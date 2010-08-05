
import TableCrabConfig
import TableCrabWin32

import re, time

from PyQt4 import QtCore

#**********************************************************************************************
#
#**********************************************************************************************

class TemplateTablePokerStars(TableCrabConfig.PersistentItem):
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
			('itemIsExpanded', TableCrabConfig.CallableBool(False)),
			)
	@classmethod
	def itemName(klass):
		return 'PokerStarsTable'
	@classmethod
	def fromConfig(klass, key):
		itemName = TableCrabConfig.settingsValue( (key, 'ItemName'), '').toString()
		if itemName != klass.itemName(): return None
		name = TableCrabConfig.settingsValue( (key, 'Name'), 'None').toString()
		size = TableCrabConfig.settingsValue( (key, 'Size'), TableCrabConfig.SizeNone).toSize()
		if not size.isValid():
			size = TableCrabConfig.SizeNone
		buttonCheck = TableCrabConfig.settingsValue( (key, 'ButtonCheck'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, buttonCheck):
			buttonCheck = TableCrabConfig.PointNone
		buttonFold = TableCrabConfig.settingsValue( (key, 'ButtonFold'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, buttonFold):
			buttonFold = TableCrabConfig.PointNone
		buttonRaise = TableCrabConfig.settingsValue( (key, 'ButtonRaise'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, buttonRaise):
			buttonRaise = TableCrabConfig.PointNone
		instantHandHistory = TableCrabConfig.settingsValue( (key, 'InstantHandHistory'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, instantHandHistory):
			instantHandHistory = TableCrabConfig.PointNone
		replayer = TableCrabConfig.settingsValue( (key, 'Replayer'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, replayer):
			replayer = TableCrabConfig.PointNone
		checkboxFold = TableCrabConfig.settingsValue( (key, 'CheckboxFold'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, checkboxFold):
			checkboxFold = TableCrabConfig.PointNone
		checkboxCheckFold = TableCrabConfig.settingsValue( (key, 'CheckboxCheckFold'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, checkboxCheckFold):
			checkboxCheckFold = TableCrabConfig.PointNone
		betSliderStart = TableCrabConfig.settingsValue( (key, 'BetSliderStart'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, betSliderStart):
			betSliderStart = TableCrabConfig.PointNone
		betSliderEnd = TableCrabConfig.settingsValue( (key, 'BetSliderEnd'), TableCrabConfig.PointNone).toPoint()
		if not TableCrabConfig.pointInSize(size, betSliderEnd):
			betSliderEnd = TableCrabConfig.PointNone
		itemIsExpanded = TableCrabConfig.settingsValue( (key, 'ItemIsExpanded'), False).toBool()
		return klass(name=name, size=size, buttonCheck=buttonCheck, 
				buttonFold=buttonFold, buttonRaise=buttonRaise, replayer=replayer, instantHandHistory=instantHandHistory, 
				checkboxFold=checkboxFold, checkboxCheckFold=checkboxCheckFold, itemIsExpanded=itemIsExpanded,
				betSliderStart=betSliderStart, betSliderEnd=betSliderEnd)
	def toConfig(self, key):
		TableCrabConfig.settingsSetValue( (key, 'ItemName'), self.itemName() )
		TableCrabConfig.settingsSetValue( (key, 'Name'), self.name)
		TableCrabConfig.settingsSetValue( (key, 'Size'), self.size)
		TableCrabConfig.settingsSetValue( (key, 'ButtonCheck'), self.buttonCheck)
		TableCrabConfig.settingsSetValue( (key, 'ButtonFold'), self.buttonFold)
		TableCrabConfig.settingsSetValue( (key, 'ButtonRaise'), self.buttonRaise)
		TableCrabConfig.settingsSetValue( (key, 'CheckboxFold'), self.checkboxFold)
		TableCrabConfig.settingsSetValue( (key, 'CheckboxCheckFold'), self.checkboxCheckFold)
		TableCrabConfig.settingsSetValue( (key, 'BetSliderStart'), self.betSliderStart)
		TableCrabConfig.settingsSetValue( (key, 'BetSliderEnd'), self.betSliderEnd)
		TableCrabConfig.settingsSetValue( (key, 'Replayer'), self.replayer)
		TableCrabConfig.settingsSetValue( (key, 'InstantHandHistory'), self.instantHandHistory)
		TableCrabConfig.settingsSetValue( (key, 'ItemIsExpanded'), self.itemIsExpanded)
		return True
		

TableCrabConfig.templateManager.addItemProto(TemplateTablePokerStars)


#***************************************************************************************************
#
#***************************************************************************************************
#TODO: sometime ..maybe ..make user adjustable: 'Gui/RestoreMousePosition'
class ActionHandler(object):
	def __init__(self):
		self._pokerStarsLoginBox = None
			
	def handleWindowCreated(self, hwnd):
		if self.isPopupNews(hwnd):
			if TableCrabConfig.settingsValue('PokerStars/AutoClosePopupNews', False).toBool():
				TableCrabWin32.windowClose(hwnd)
			return True
		
		elif self.isTourneyRegistrationMessageBox(hwnd):
			if TableCrabConfig.settingsValue('PokerStars/AutoCloseTourneyRegistrationBoxes', False).toBool():
				buttons = TableCrabWin32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				##windowClose(hwnd)
				TableCrabWin32.windowClickButton(buttons['OK'])
			return True
		
		elif self.isTableMessageBox(hwnd):
			if TableCrabConfig.settingsValue('PokerStars/AutoCloseTableMessageBoxes', False).toBool():
				buttons = TableCrabWin32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				TableCrabWin32.windowClickButton(buttons['OK'])
			return True
		
		elif self.isLogIn(hwnd):
			if self._pokerStarsLoginBox is None: 
				self._pokerStarsLoginBox = hwnd
				if TableCrabConfig.settingsValue('PokerStars/AutoCloseLogin', False).toBool():
					buttons = TableCrabWin32.windowGetButtons(hwnd)
					if sorted(buttons) == ['', 'Cancel', 'Create New Account...', 'Forgot User ID / Password...', 'OK']:
						if TableCrabWin32.windowCheckboxIsChecked(buttons['']):
							if TableCrabWin32.windowIsEnabled(buttons['OK']):
								TableCrabWin32.windowClickButton(buttons['OK'])
				return True
			
		return False
	
	def handleWindowDestroyed(self, hwnd):
		return False
		
	def handleWindowGainedForeground(self, hwnd):
		template = self.tableTemplateItem(hwnd)
		if template is not None:
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', template.name)
			return True
		return False
	
	def handleWindowLostForeground(self, hwnd):
		return False
	
	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		template = self.tableTemplateItem(hwnd)
		if template is None:
			return False
		if not self.tableHotkeysEnabled(hwnd):
			return False
		if not inputEvent.keyIsDown:
			inputEvent.accept = True
			return True
			
		actionName = hotkey.itemName()
		
		if actionName == TableCrabConfig.HotkeyCheck.itemName():
			self.tableHandleCheck(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True
		elif actionName == TableCrabConfig.HotkeyFold.itemName():
			self.tableHandleFold(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True		
		elif actionName == TableCrabConfig.HotkeyRaise.itemName():
			self.tableHandleRaise(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionName == TableCrabConfig.HotkeyAllIn.itemName():
			self.tableHandleAllIn(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionName == TableCrabConfig.HotkeyHilightBetAmount.itemName():
			self.tableHandleHilightBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True
		elif actionName == TableCrabConfig.HotkeyAddToBetAmount.itemName():
			self.tableHandleAddToBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionName == TableCrabConfig.HotkeySubtractFromBetAmount.itemName():
			self.tableHandleSubtractFromBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionName == TableCrabConfig.HotkeyMultiplyBetAmount.itemName():
			self.tableHandleMultiplyBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionName == TableCrabConfig.HotkeyReplayer.itemName():
			self.tableHandleReplayer(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True
		elif actionName == TableCrabConfig.HotkeyInstantHandHistory.itemName():
			self.tableHandleInstantHandHistory(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True
			
		return False
		
	#NOTE: not easy to determine if a window is a PokerStarswindow. i don't feel like messing around with psapi.dll to get the exefilename.
	# so ..i use a hack. we identify a window as being a stars window if it (or one of its parents) contains a widget classname.startswith('PokerStars')
	# nasty and errorprone, but the most reasonalbe i could come up with now
	def hasPokerStarsWidgets(self, hwnd):
		for hwnd in TableCrabWin32.windowChildren(hwnd):
			if TableCrabWin32.windowGetClassName(hwnd).startswith('PokerStars'):	return True
		return False
	
	def isPokerStarsWindow(self, hwnd):
		while hwnd:
			if self.hasPokerStarsWidgets(hwnd): return True
			hwnd = TableCrabWin32.windowGetParent(hwnd)
		return False	
		
	TitleLobby = 'PokerStars Lobby'
	ClassLobby = '#32770'	# duh, stars. main windows should never be dialogs
	def isLobby(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassLobby: return False
		if not TableCrabWin32.windowGetText(hwnd).startswith(self.TitleLobby): return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True
		
	ClassTable = 'PokerStarsTableFrameClass'
	def isTable(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassTable: return False
		return True
		
	ClassInstantHandHistory = '#32770'
	TitleInstantHandHistory = 'Instant Hand History'
	def isInstantHandHistory(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassInstantHandHistory: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.TitleInstantHandHistory: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True
		
	ClassNews = '#32770'
	TitleNews = 'News'
	def isPopupNews(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassNews: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.TitleNews: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True
		
	TitleTourneyRegistrationMessageBox = 'Tournament Registration'
	ClassTourneyRegistrationMessageBox = '#32770'
	def isTourneyRegistrationMessageBox(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassTourneyRegistrationMessageBox: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.TitleTourneyRegistrationMessageBox: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True
		
	TitleTableMessageBox = 'Tournament Registration'
	ClassTableMessageBox = '#32770'
	def isTableMessageBox(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassTableMessageBox: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.TitleTableMessageBox: return False
		hwndParent = TableCrabWin32.windowGetParent(hwnd)
		if not self.isTable(hwndParent): return False
		return True
		
	TitleLogIn = 'Log In'
	ClassLogIn = '#32770'
	def isLogIn(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassLogIn: return False
		if not TableCrabWin32.windowGetText(hwnd) == self.TitleLogIn: return False
		hwndParent = TableCrabWin32.windowGetParent(hwnd)
		if not self.isLobby(hwndParent): return False
		return True
		
	def tableTemplateItem(self, hwnd):
		if self.isTable(hwnd):
			rect = TableCrabWin32.windowGetClientRect(hwnd)
			for template in TableCrabConfig.templateManager.items():
				if template.itemName() == 'PokerStarsTable':
					if template.size == rect.size():
						return template
		return None
		
	PatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	ClassTableBetAmountBox = 'PokerStarsSliderEditorClass'
	def tableReadData(self, hwnd):
		data = {}
		text = TableCrabWin32.windowGetText(hwnd)
		if not text: return data
		match = self.PatAmountSB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['smallBlind'] = float(match.group(1))
		match = self.PatAmountBB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['bigBlind'] = float(match.group(1))
		hwndBetAmountBox = TableCrabWin32.windowFindChild(hwnd, self.ClassTableBetAmountBox)
		data['hwndBetAmountBox'] =  hwndBetAmountBox
		data['betAmountBoxIsVisible'] = TableCrabWin32.windowIsVisible(hwndBetAmountBox )
		data['betAmount'] = None
		if data['hwndBetAmountBox']:
			p = TableCrabWin32.windowGetText(hwndBetAmountBox)
			try:
				data['betAmount'] = float(p)
			except ValueError: pass
		return data

	ClassChatEditor = 'PokerStarsChatEditorClass'
	ClassNoteEditor = 'PokerStarsNoteEditorClass'
	#NOTE: "Edit" is actually a child widget of 'PokerStarsNoteSelectorClass', so we could add more tests in code below if required
	ClassNoteEditorBox = 'Edit'
	def tableHotkeysEnabled(self, hwnd):
		point = TableCrabWin32.mouseGetPos()
		hwndUnderMouse = TableCrabWin32.windowFromPoint(point)
		className = TableCrabWin32.windowGetClassName(hwndUnderMouse)
		if className in (self.ClassNoteEditor, self.ClassChatEditor, self.ClassNoteEditorBox):
			return False
		return True	
		
	def tableHandleCheck(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		pointCurrent = TableCrabWin32.mouseGetPos()
		if data['betAmountBoxIsVisible']:
			point = template.buttonCheck
			if point == TableCrabConfig.PointNone: return
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		else:
			point = template.checkboxCheckFold
			if point == TableCrabConfig.PointNone: return
			# looks like we have to double click here
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('Gui/RestoreMousePosition', False).toBool():
			mi.move(pointCurrent, hwnd=None).send()
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
		
	def tableHandleFold(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		pointCurrent = TableCrabWin32.mouseGetPos()
		if data['betAmountBoxIsVisible']:
			point = template.buttonFold
			if point == TableCrabConfig.PointNone: return
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		else:
			point = template.checkboxFold
			if point == TableCrabConfig.PointNone: return
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).send()
			# looks like we have to double click here
			mi.leftClick(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('Gui/RestoreMousePosition', False).toBool():
			mi.move(pointCurrent, hwnd=None).send()
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
		
	def tableHandleRaise(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		#NOTE: betAmountBox may not be visible when a player is all-in
		##if not data['betAmountBoxIsVisible']: return
		point = template.buttonRaise
		if point == TableCrabConfig.PointNone: return
		pointCurrent = TableCrabWin32.mouseGetPos()
		mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('Gui/RestoreMousePosition', False).toBool():
			mi.move(pointCurrent, hwnd=None).send()
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
		
	#NOTE: there is another way to handle all-in. no reliable one but could be a fallback. looks like bet amount box accepts
	# values up to some hard coded PS wide maximum. if this maximum is exceeded the bet box resets to 0.
	# played a bit around with this:
	# 20.000.000 ok
	# 21.000.000 ok
	# 24.000.000 reset
	# funny enough you can enter up to 9 digits into the box when the maximum is actually located somewhere in the 8 digits region.
	# either a bug or feature that is. 
	def tableHandleAllIn(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		pointStart = template.betSliderStart
		if pointStart == TableCrabConfig.PointNone: return
		pointEnd = template.betSliderEnd
		if pointEnd == TableCrabConfig.PointNone: return
		pointCurrent = TableCrabWin32.mouseGetPos()
		mi = TableCrabWin32.MouseInput().move(pointStart, hwnd=hwnd).send()
		mi.leftDown(pointStart, hwnd=hwnd).move(pointEnd, hwnd=hwnd).leftUp(pointEnd, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('Gui/RestoreMousePosition', False).toBool():
			mi.move(pointCurrent, hwnd=None).send()
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
		
	def tableHandleAddToBetAmount(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		if nSteps == 0: return
		nSteps =  inputEvent.mouseSteps if inputEvent.mouseSteps else 1
		if hotkey.baseValue == 'BigBlind':
			newBetAmount = data['betAmount'] + (data['bigBlind'] * hotkey.multiplier * nSteps)
		elif hotkey.baseValue == 'SmallBlind':
			newBetAmount = data['betAmount'] + (data['smallBlind'] * hotkey.multiplier * nSteps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue)
		newBetAmount = round(newBetAmount, 2)
		if int(newBetAmount) == newBetAmount:
			newBetAmount = int(newBetAmount)
		newBetAmount = str(newBetAmount)
		TableCrabWin32.windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
			
	def tableHandleSubtractFromBetAmount(self, hotkey, template, hwnd, inputEvent):
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		if nSteps == 0: return
		nSteps =  inputEvent.mouseSteps if inputEvent.mouseSteps else 1
		if hotkey.baseValue == 'BigBlind':
			newBetAmount = data['betAmount'] - (data['bigBlind'] * hotkey.multiplier * nSteps)
		elif hotkey.baseValue == 'SmallBlind':
			newBetAmount = data['betAmount'] - (data['smallBlind'] * hotkey.multiplier * nSteps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue)
		newBetAmount = round(newBetAmount, 2)
		if int(newBetAmount) == newBetAmount:
			newBetAmount = int(newBetAmount)
		newBetAmount = str( 0 if newBetAmount < 0 else newBetAmount )
		TableCrabWin32.windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
	
	def tableHandleMultiplyBetAmount(self, hotkey, template, hwnd, inputEvent):
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		nSteps =  inputEvent.mouseSteps if inputEvent.mouseSteps else 1
		nSteps = 1 if nSteps is None else abs(nSteps)
		newBetAmount = data['betAmount'] * hotkey.multiplier * nSteps
		newBetAmount = round(newBetAmount, 2)
		if int(newBetAmount) == newBetAmount:
			newBetAmount = int(newBetAmount)
		newBetAmount = str(newBetAmount)
		TableCrabWin32.windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
		
	def tableHandleHilightBetAmount(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		hwndBetAmountBox = data['hwndBetAmountBox']
		if not hwndBetAmountBox: return
		if not data['betAmountBoxIsVisible']: return
			
		pointCurrent = TableCrabWin32.mouseGetPos()
		point = QtCore.QPoint(2, 2)
		mi = TableCrabWin32.MouseInput().move(point, hwnd=hwndBetAmountBox).send()
		mi.leftClick(point, hwnd=hwndBetAmountBox).leftClick(point, hwnd=hwndBetAmountBox).send()
		if TableCrabConfig.settingsValue('Gui/RestoreMousePosition', False).toBool():
			mi.move(pointCurrent, hwnd=None).send()
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
		
	def _tableClickRestoreFocus(self, hwnd, point):
		if point == TableCrabConfig.PointNone: return
		pointCurrent = TableCrabWin32.mouseGetPos()
		# click point
		mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		# replayer gains focus, so we have to wait a bit and send another click to reactivate the table. 
		#TODO: for some reason we never regain focus when the replayer is opend for the first time
		#TODO: maybe we have to make timeout user adjustable
		time.sleep(0.1)
		#TODO: maybe we have make this point user adjustable
		mi.move(QtCore.QPoint(1, 1), hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('Gui/RestoreMousePosition', False).toBool():
			#NOTE: the mouse will move around a bit for SndInput() being inacurate)
			mi.move(pointCurrent, hwnd=None).send()
		
	def tableHandleReplayer(self, hotkey, template, hwnd, inputEvent):
		self._tableClickRestoreFocus(hwnd, template.replayer)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))
		
	def tableHandleInstantHandHistory(self, hotkey, template, hwnd, inputEvent):
		self._tableClickRestoreFocus(hwnd, template.instantHandHistory)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name,  hotkey.hotkey))


