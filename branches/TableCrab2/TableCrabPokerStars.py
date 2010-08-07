
#TODO: give feedback when closing dialog boxes
#TODO: we may need to define a PointNone where our mouse cursor is set to when restoring table focus

import TableCrabConfig
import TableCrabWin32
import TableCrabHotkeys
import TableCrabTemplates

import re, time

from PyQt4 import QtCore
#***************************************************************************************************
#
#***************************************************************************************************
class ActionHandler(QtCore.QObject):
	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)
		
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
		template = self.tableTemplate(hwnd)
		if template is not None:
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', template.name)
			return True
		return False
	
	def handleWindowLostForeground(self, hwnd):
		return False
	
	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		template = self.tableTemplate(hwnd)
		if template is None:
			return False
		if not self.tableHotkeysEnabled(hwnd):
			return False
		if not inputEvent.keyIsDown:
			inputEvent.accept = True
			return True
			
		actionID = hotkey.id()
			
		if actionID == TableCrabHotkeys.HotkeyCheck.id():
			self.tableHandleCheck(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True
		elif actionID == TableCrabHotkeys.HotkeyFold.id():
			self.tableHandleFold(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True		
		elif actionID == TableCrabHotkeys.HotkeyRaise.id():
			self.tableHandleRaise(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionID == TableCrabHotkeys.HotkeyAll_In.id():
			self.tableHandleAll_In(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionID == TableCrabHotkeys.HotkeyHilightBetAmount.id():
			self.tableHandleHilightBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True
		elif actionID == TableCrabHotkeys.HotkeyAddToBetAmount.id():
			self.tableHandleAddToBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionID == TableCrabHotkeys.HotkeySubtractFromBetAmount.id():
			self.tableHandleSubtractFromBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionID == TableCrabHotkeys.HotkeyMultiplyBetAmount.id():
			self.tableHandleMultiplyBetAmount(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True	
		elif actionID == TableCrabHotkeys.HotkeyReplayer.id():
			self.tableHandleReplayer(hotkey, template, hwnd, inputEvent)
			inputEvent.accept = True
			return True
		elif actionID == TableCrabHotkeys.HotkeyInstantHandHistory.id():
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
		
	def tableTemplate(self, hwnd):
		if self.isTable(hwnd):
			rect = TableCrabWin32.windowGetClientRect(hwnd)
			for template in TableCrabConfig.templateManager:
				if template.id() == TableCrabTemplates.TemplatePokerStarsTable.id():
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
			if point == TableCrabConfig.PointNone: 
				TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- Point ButtonCheck Not set -' % template.name)
				return
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		else:
			point = template.checkboxCheckFold
			if point == TableCrabConfig.PointNone: 
				TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- CheckboxCheckFold Not set -' % template.name)
				return
			# looks like we have to double click here
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool():
			#NOTE: the SendInput() is always off a few pixels so we use mouseSetPos() instead
			##mi.move(pointCurrent, hwnd=None).send()
			TableCrabWin32.mouseSetPos(pointCurrent)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
		
	def tableHandleFold(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		pointCurrent = TableCrabWin32.mouseGetPos()
		if data['betAmountBoxIsVisible']:
			point = template.buttonFold
			if point == TableCrabConfig.PointNone: 
				TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- Point ButtonFold Not set -' % template.name)
				return
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		else:
			point = template.checkboxFold
			if point == TableCrabConfig.PointNone: 
				TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- Point CheckboxFold Not set -' % template.name)
				return
			mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).send()
			# looks like we have to double click here
			mi.leftClick(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool():
			#NOTE: the SendInput() is always off a few pixels so we use mouseSetPos() instead
			##mi.move(pointCurrent, hwnd=None).send()
			TableCrabWin32.mouseSetPos(pointCurrent)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
		
	def tableHandleRaise(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		#NOTE: betAmountBox may not be visible when a player is all-in
		##if not data['betAmountBoxIsVisible']: return
		point = template.buttonRaise
		if point == TableCrabConfig.PointNone: 
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- Point Buttonraise Not set -' % template.name)
			return
		pointCurrent = TableCrabWin32.mouseGetPos()
		mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool():
			#NOTE: the SendInput() is always off a few pixels so we use mouseSetPos() instead
			##mi.move(pointCurrent, hwnd=None).send()
			TableCrabWin32.mouseSetPos(pointCurrent)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
		
	#NOTE: there is another way to handle all-in. no reliable one but could be a fallback. looks like bet amount box accepts
	# values up to some hard coded PS wide maximum. if this maximum is exceeded the bet box resets to 0.
	# played a bit around with this:
	# 20.000.000 ok
	# 21.000.000 ok
	# 24.000.000 reset
	# funny enough you can enter up to 9 digits into the box when the maximum is actually located somewhere in the 8 digits region.
	# either a bug or feature that is. 
	def tableHandleAll_In(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		pointStart = template.betSliderStart
		if pointStart == TableCrabConfig.PointNone: 
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- Point BetSliderStart Not set -' % template.name)
			return
		pointEnd = template.betSliderEnd
		if pointEnd == TableCrabConfig.PointNone: 
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s - Point BetSliderEnd Not set -' % template.name)
			return
		pointCurrent = TableCrabWin32.mouseGetPos()
		mi = TableCrabWin32.MouseInput().move(pointStart, hwnd=hwnd).send()
		mi.leftDown(pointStart, hwnd=hwnd).move(pointEnd, hwnd=hwnd).leftUp(pointEnd, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool():
			#NOTE: the SendInput() is always off a few pixels so we use mouseSetPos() instead
			##mi.move(pointCurrent, hwnd=None).send()
			TableCrabWin32.mouseSetPos(pointCurrent)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
		
	def tableHandleAddToBetAmount(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == 'BigBlind':
			newBetAmount = data['betAmount'] + (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue == 'SmallBlind':
			newBetAmount = data['betAmount'] + (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		newBetAmount = round(newBetAmount, 2)
		if int(newBetAmount) == newBetAmount:
			newBetAmount = int(newBetAmount)
		newBetAmount = str(newBetAmount)
		TableCrabWin32.windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
			
	def tableHandleSubtractFromBetAmount(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == 'BigBlind':
			newBetAmount = data['betAmount'] - (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue == 'SmallBlind':
			newBetAmount = data['betAmount'] - (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		newBetAmount = round(newBetAmount, 2)
		if int(newBetAmount) == newBetAmount:
			newBetAmount = int(newBetAmount)
		newBetAmount = str( 0 if newBetAmount < 0 else newBetAmount )
		TableCrabWin32.windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
	
	def tableHandleMultiplyBetAmount(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetAmountBox']: return
		if not data['betAmountBoxIsVisible']: return
		if data['betAmount'] is None: return
		if inputEvent.steps == 0: return
		newBetAmount = data['betAmount'] * hotkey.multiplier() * inputEvent.steps
		newBetAmount = round(newBetAmount, 2)
		if int(newBetAmount) == newBetAmount:
			newBetAmount = int(newBetAmount)
		newBetAmount = str(newBetAmount)
		TableCrabWin32.windowSetText(data['hwndBetAmountBox'], text=newBetAmount)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
		
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
		if TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool():
			#NOTE: the SendInput() is always off a few pixels so we use mouseSetPos() instead
			##mi.move(pointCurrent, hwnd=None).send()
			TableCrabWin32.mouseSetPos(pointCurrent)
		TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
		
	def _tableClickRestoreFocus(self, hwnd, point, template):
		pointCurrent = TableCrabWin32.mouseGetPos()
		# click point
		mi = TableCrabWin32.MouseInput().move(point, hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		# replayer gains focus, so we have to wait a bit and send another click to reactivate the table. 
		#TODO: for some reason (linux/wine?) table regain focus but is not activated when the replayer is opend for the first time
		#TODO: make this point user adjustable?
		mi.move(QtCore.QPoint(1, 1), hwnd=hwnd).leftClick(point, hwnd=hwnd).send()
		if TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool():
			#NOTE: the SendInput() is always off a few pixels so we use mouseSetPos() instead
			##mi.move(pointCurrent, hwnd=None).send()
			TableCrabWin32.mouseSetPos(pointCurrent)
			
		
	def tableHandleReplayer(self, hotkey, template, hwnd, inputEvent):
		point = template.replayer
		if point == TableCrabConfig.PointNone: 
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- Point Replayer Not set -' % template.name)
		else:
			self._tableClickRestoreFocus(hwnd, template.replayer, template)
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))
		
	def tableHandleInstantHandHistory(self, hotkey, template, hwnd, inputEvent):
		point = template.instantHandHistory
		if point == TableCrabConfig.PointNone: 
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: -- Point InstantHandHistory Not set -' % template.name)
		else:
			self._tableClickRestoreFocus(hwnd, template.instantHandHistory, template)
			TableCrabConfig.signalEmit(None, 'feedbackMessage(QString)', '%s: %s' % (template.name, hotkey.action() ))


