
#TODO: we may need to expose a PointNone in our table template where our mouse cursor is set to when restoring table focus
#TODO: for some reason ButtonCheck and ButtonRaise are not working as expected postflop (preflop is ok). we have to trigger
#				hotkey two times (always, sometimes?) to get the desired effect. double clicking right now ..have to experiment.
#TODO: move mouse to active table is not implemented. we'll see.

import TableCrabConfig
import TableCrabWin32
import TableCrabHotkeys
import TableCrabTemplates
from TableCrabLib.gocr import gocr

import re, time

from PyQt4 import QtCore, QtGui

#***************************************************************************************************
#
#***************************************************************************************************
class EventHandler(QtCore.QObject):

	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)

		self._pokerStarsLoginBox = None


	def handleWindowCreated(self, hwnd):

		if self.isPopupNews(hwnd):
			if TableCrabConfig.settingsValue('PokerStars/AutoClosePopupNews', False).toBool():
				TableCrabWin32.windowClose(hwnd)
				TableCrabConfig.globalObject.feedbackMessage.emit('Closed Popup News')
			return True

		elif self.isTourneyRegistrationMessageBox(hwnd):
			if TableCrabConfig.settingsValue('PokerStars/AutoCloseTourneyRegistrationBoxes', False).toBool():
				buttons = TableCrabWin32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				##windowClose(hwnd)
				TableCrabWin32.windowClickButton(buttons['OK'])
				TableCrabConfig.globalObject.feedbackMessage.emit('Closed Tourney Registration Message Box')
			return True

		elif self.isTableMessageBox(hwnd):
			if TableCrabConfig.settingsValue('PokerStars/AutoCloseTableMessageBoxes', False).toBool():
				buttons = TableCrabWin32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				TableCrabWin32.windowClickButton(buttons['OK'])
				TableCrabConfig.globalObject.feedbackMessage.emit('Closed Table Message Box')
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
								TableCrabConfig.globalObject.feedbackMessage.emit('Closed Log In Box')
				return True

		return False

	def handleWindowDestroyed(self, hwnd):
		return False

	def handleWindowGainedForeground(self, hwnd):
		template = self.tableTemplate(hwnd)
		if template is not None:
			TableCrabConfig.globalObject.feedbackMessage.emit(template.name)
			if TableCrabConfig.settingsValue('PokerStars/MoveMouseToActiveTable', False).toBool():
				if not TableCrabWin32.mouseButtonsDown():
					point = template.emptySpace
					point = TableCrabWin32.windowClientPointToScreenPoint(hwnd, point)
					TableCrabWin32.mouseSetPos(point)
			return True
		return False

	def handleWindowLostForeground(self, hwnd):
		return False

	def handleInputEvent(self, hwnd, hotkey, inputEvent):

		if self.isTable(hwnd):
			if not self.tableHotkeysEnabled(hwnd):
				return False

			hotkeyID = hotkey.id()

			if hotkeyID == TableCrabHotkeys.HotkeyTableSizeNext.id():
				if inputEvent.keyIsDown:
					#  find next table template that is not of current tables size
					size = TableCrabWin32.windowGetClientRect(hwnd).size()
					template = None
					pickNext = False
					for i, tmp_template in enumerate(TableCrabConfig.templateManager):
						if tmp_template.id() == TableCrabTemplates.TemplatePokerStarsTable.id():
							if tmp_template.size	== TableCrabConfig.SizeNone:
								continue
							if pickNext:
								template = tmp_template
								break
							if template is None:
								template = tmp_template
							if tmp_template.size == size:
								pickNext = True
					# resize table to next templates size
					if template is not None:
						#NOTE: on wine tables do not get redrawn on resize [ http://bugs.winehq.org/show_bug.cgi?id=5941 ].
						# 	for some reson sending F5 via KeyboardInput has no effect whatsoever, so we tell TableCrabWin32
						# to wrap resizing into enter- exitsizemove messages. tested on winXP aswell - works nicely
						TableCrabWin32.windowSetClientSize(hwnd, template.size, sendSizeMove=True)
				inputEvent.accept = True
				return True

			template = self.tableTemplate(hwnd)
			if template is None:
				return False

			if hotkeyID == TableCrabHotkeys.HotkeyCheck.id():
				if inputEvent.keyIsDown:
					self.tableHandleCheck(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyFold.id():
				if inputEvent.keyIsDown:
					self.tableHandleFold(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyRaise.id():
				if inputEvent.keyIsDown:
					self.tableHandleRaise(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyAll_In.id():
				if inputEvent.keyIsDown:
					self.tableHandleAll_In(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyHilightBet.id():
				if inputEvent.keyIsDown:
					self.tableHandleHilightBet(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyAddToBet.id():
				if inputEvent.keyIsDown:
					self.tableHandleAddToBet(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeySubtractFromBet.id():
				if inputEvent.keyIsDown:
					self.tableHandleSubtractFromBet(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyMultiplyBet.id():
				if inputEvent.keyIsDown:
					self.tableHandleMultiplyBet(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyBetPot.id():
				if inputEvent.keyIsDown:
					self.tableHandleBetPot(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyReplayer.id():
				if inputEvent.keyIsDown:
					self.tableHandleReplayer(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True
			elif hotkeyID == TableCrabHotkeys.HotkeyInstantHandHistory.id():
				if inputEvent.keyIsDown:
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
		if not TableCrabWin32.windowGetText(hwnd, maxSize=len(self.TitleLobby)).startswith(self.TitleLobby): return False
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
		if not TableCrabWin32.windowGetText(hwnd, maxSize=len(self.TitleNews)) == self.TitleNews: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	TitleTourneyRegistrationMessageBox = 'Tournament Registration'
	ClassTourneyRegistrationMessageBox = '#32770'
	def isTourneyRegistrationMessageBox(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassTourneyRegistrationMessageBox: return False
		if not TableCrabWin32.windowGetText(hwnd, maxSize=len(self.TitleTourneyRegistrationMessageBox)) == self.TitleTourneyRegistrationMessageBox: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	TitleTableMessageBox = 'PokerStars'
	ClassTableMessageBox = '#32770'
	def isTableMessageBox(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassTableMessageBox: return False
		if not TableCrabWin32.windowGetText(hwnd, maxSize=len(self.TitleTableMessageBox)) == self.TitleTableMessageBox: return False
		hwndParent = TableCrabWin32.windowGetParent(hwnd)
		if not self.isTable(hwndParent): return False
		return True

	TitleLogIn = 'Log In'
	ClassLogIn = '#32770'
	def isLogIn(self, hwnd):
		if not TableCrabWin32.windowGetClassName(hwnd) == self.ClassLogIn: return False
		if not TableCrabWin32.windowGetText(hwnd, maxSize=len(self.TitleLogIn)) == self.TitleLogIn: return False
		hwndParent = TableCrabWin32.windowGetParent(hwnd)
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	def tableTemplate(self, hwnd):
		if self.isTable(hwnd):
			rect = TableCrabWin32.windowGetClientRect(hwnd)
			for template in TableCrabConfig.templateManager:
				if template.id() == TableCrabTemplates.TemplatePokerStarsTable.id():
					if template.size == rect.size():
						return template
		return None

	#TODO: are there tables where BB/SB is not present in caption? closed tourneys ...?
	PatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	ClassTableBetBox = 'PokerStarsSliderEditorClass'
	def tableReadData(self, hwnd):
		data = {}
		text = TableCrabWin32.windowGetText(hwnd, maxSize=TableCrabConfig.MaxWindowText )
		if not text: return data
		match = self.PatAmountSB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['smallBlind'] = float(match.group(1))
		match = self.PatAmountBB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['bigBlind'] = float(match.group(1))
		hwndBetBox = TableCrabWin32.windowFindChild(hwnd, self.ClassTableBetBox)
		data['hwndBetBox'] =  hwndBetBox
		data['betBoxIsVisible'] = TableCrabWin32.windowIsVisible(hwndBetBox) if hwndBetBox else False
		data['bet'] = None
		if data['hwndBetBox']:
			p = TableCrabWin32.windowGetText(hwndBetBox, maxSize=TableCrabConfig.MaxPokerStarsBetBoxText)
			try:
				data['bet'] = float(p)
			except ValueError: pass
		return data

	#TODO: fo some reason hotkeys are stillenabled when mouse is over notes editor with editor not having focus
	ClassChatEditor = 'PokerStarsChatEditorClass'
	ClassNoteEditor = 'PokerStarsNoteEditorClass'
	ClassInfoBox = 'PokerStarsInfoClass'
	#NOTE: "Edit" is actually a child widget of 'PokerStarsNoteSelectorClass', so we could add more tests in code below if required
	ClassNoteEditorBox = 'Edit'
	def tableHotkeysEnabled(self, hwnd):
		point = TableCrabWin32.mouseGetPos()
		hwndUnderMouse = TableCrabWin32.windowFromPoint(point)
		className = TableCrabWin32.windowGetClassName(hwndUnderMouse)
		if className in (self.ClassNoteEditor, self.ClassChatEditor, self.ClassNoteEditorBox, self.ClassInfoBox):
			return False
		return True

	def tableHandleCheck(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if data['hwndBetBox'] and data['betBoxIsVisible']:
			point = template.buttonCheck
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point ButtonCheck Not Set -' % template.name)
				return
		# we always allow checkboxcCheckFold ..stars may show this box when we are newly seated at a table without having the
		# bet amount box created yet
		else:
			point = template.checkboxCheckFold
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- CheckboxCheckFold Not Set -' % template.name)
				return
		#NOTE: we always double click. seems to work more reliably
		TableCrabWin32.mouseInputLeftClickDouble(
				point,
				hwnd=hwnd,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleFold(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if data['hwndBetBox'] and data['betBoxIsVisible']:
			point =  template.buttonFold
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point ButtonFold Not Set -' % template.name)
				return
		# we always allow checkboxFold ..stars may show this box when we are newly seated at a table without having the
		# bet amount box created yet
		else:
			point = template.checkboxFold
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- CheckboxFold Not Set -' % template.name)
				return
		#NOTE: we always double click. seems to work more reliably
		TableCrabWin32.mouseInputLeftClickDouble(
				point,
				hwnd=hwnd,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleRaise(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		#NOTE: BetBox may not be visible when a player is all-in
		##if not data['betBoxIsVisible']: return
		if  template.buttonRaise == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point Buttonraise Not Set -' % template.name)
			return
		#NOTE: we always double click. seems to work more reliably
		TableCrabWin32.mouseInputLeftClickDouble(
				template.buttonRaise,
				hwnd=hwnd,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

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
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if template.betSliderStart == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point BetSliderStart Not Set -' % template.name)
			return
		if template.betSliderEnd == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point BetSliderEnd Not Set -' % template.name)
			return
		TableCrabWin32.mouseInputMouseDrag(
				template.betSliderStart,
				template.betSliderEnd,
				hwnd=hwnd,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleAddToBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == 'BigBlind':
			newBet = data['bet'] + (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue == 'SmallBlind':
			newBet = data['bet'] + (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		newBet = round(newBet, 2)
		if int(newBet) == newBet:
			newBet = int(newBet)
		newBet = str(newBet)
		#NOTE: the box gets mesed up when unicode is thrown at it
		TableCrabWin32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newbet))

	def tableHandleSubtractFromBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == 'BigBlind':
			newBet = data['bet'] - (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue == 'SmallBlind':
			newBet = data['bet'] - (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		newBet = round(newBet, 2)
		if int(newBet) == newBet:
			newBet = int(newBet)
		newBet = str( 0 if newBet < 0 else newBet )
		#NOTE: the box gets mesed up when unicode is thrown at it
		TableCrabWin32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def tableHandleMultiplyBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		newBet = data['bet'] * hotkey.multiplier() * inputEvent.steps
		newBet = round(newBet, 2)
		if int(newBet) == newBet:
			newBet = int(newBet)
		newBet = str(newBet)
		#NOTE: the box gets mesed up when unicode is thrown at it
		TableCrabWin32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def _tableGetPotAmount(self, buff):
		# scan image
		#TODO: grayLevel threshold.
		# 1) no real idea what it does. i guess it is a threshold in range(grayLevelMin, graylevelmax)
		# 2) we may have to make this user adjustable per template. nasty.
		result, err = gocr.scanImage(
				string=buff,
				chars='0-9.,',
				dustSize=0,
				#grayLevel=200
				)
		#NOTE: we track this case because gocr dumps warnings (other minor messages) to stderr as well
		if err and result:
			TableCrabConfig.logger.critical('gocr error - %s' % err)
		if not result:
			try:
				raise ValueError(err)
			except:
				TableCrabConfig.handleException(data='gocr - could not scan image')
			return None, 'could not scan pot'

		# clean gocr output from garbage
		num = result.replace('\x20', '').replace('\n', '').replace('\r', '')
		# buff should be very rough bounds of pot rect so remove trailing clutter.
		# we just hope* gocr does not recognize borders or stuff on the background as chars
		num = num.rstrip('_').rstrip('.').rstrip(',')

		#NOTE:
		# 1. assertion: pot rect contains at least the 'T' of 'POT' so we always get an unknown char preceeding number
		# 2. assertion: gocr does not recognize any chars following our number
		if '_' not in num:
			return None, 'could not scan pot'

		# 'i' should be either '$' or some other currency symbol or the 'T' from 'POT'
		i = num.rindex('_')
		num = num[i +1:]

		# try to reconstruct number
		# get rid of commas
		num = num.replace(',', '.')
		num = num.split('.')
		# check if pot is float
		if len(num) > 1:
			if len(num[-1]) == 2:
				num = ''.join(num[:-1]) + '.' + num[-1]
			else:
				num = ''.join(num)
		else:
			num = num[0]
		try:
			num = float(num)
		except ValueError:
			TableCrabConfig.handleException(data='gocr - invalid number: "%s"' % result)
			return None, 'could not scan pot'
		return num, None

	def tableHandleBetPot(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return

		if template.potTopLeft == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point Pot Top Left Not Set -' % template.name)
			return
		if template.potBottomRight == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point Pot Bottom Right Not Set -' % template.name)
			return

		# grab pot rect
		pixmap = QtGui.QPixmap.grabWindow(hwnd,
					template.potTopLeft.x(),
					template.potTopLeft.y(),
					template.potBottomRight.x() - template.potTopLeft.x(),
					template.potBottomRight.y() - template.potTopLeft.y(),
					)
		buff = gocr.imageToString(pixmap, 'PGM')	# looks like PGM works quite well here
		num, err = self._tableGetPotAmount(buff)
		if not num:
			# try again with inverted pixels.
			#TODO: more like praying gocr will do the right thing now. have to test this
			image = QtGui.QImage(buff, pixmap.width(), pixmap.height(), QtGui.QImage.Format_Indexed8)
			image.invertPixels()
			buff = gocr.imageToString(image, 'PGM')
			num, err = self._tableGetPotAmount(buff)
			if not num:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: Error - %s ' % (hotkey.action(), err) )
				return

		newBet = num + num * hotkey.multiplier()
		if int(newBet) == newBet:
			newBet = int(newBet)
		newBet = str(newBet)
		TableCrabWin32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet) )

	def tableHandleHilightBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		hwndBetBox = data['hwndBetBox']
		if not hwndBetBox: return
		if not data['betBoxIsVisible']: return
		point = QtCore.QPoint(2, 2)
		TableCrabWin32.mouseInputLeftClickDouble(
				point,
				hwnd=hwndBetBox,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def _tableClickRestoreFocus(self, hwnd, point, template):
		#NOTE: we always double click. not realy necessary here
		TableCrabWin32.mouseInputLeftClickDouble(
				point,
				hwnd=hwnd,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)
		# replayer gains focus, so we have to wait a bit and send another click to reactivate the table.
		#TODO: for some reason (linux/wine?) table regain focus but is not activated when the replayer is opend for the first time
		TableCrabWin32.mouseInputLeftClickDouble(
				template.emptySpace,
				hwnd=hwnd,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)

	def tableHandleReplayer(self, hotkey, template, hwnd, inputEvent):
		point = template.replayer
		if point == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point Replayer Not Set -' % template.name)
		else:
			self._tableClickRestoreFocus(hwnd, template.replayer, template)
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleInstantHandHistory(self, hotkey, template, hwnd, inputEvent):
		point = template.instantHandHistory
		if point == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point InstantHandHistory Not Set -' % template.name)
		else:
			self._tableClickRestoreFocus(hwnd, template.instantHandHistory, template)
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))


