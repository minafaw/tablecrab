
#TODO: for some reason ButtonCheck and ButtonRaise are not working as expected postflop (preflop is ok). we have to trigger
#				hotkey two times (always, sometimes?) to get the desired effect. double clicking right now ..have to experiment.

import Tc2Config
import Tc2Win32
import Tc2ConfigHotkeys
import Tc2ConfigTemplates
from Tc2Lib.gocr import gocr

import re, time, base64

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************

class ScanTrace(object):
	def __init__(self):
		self.data = []
		self.gocrWarinings = []
	def __str__(self):
		return '\n'.join(self.data)
	def __add__(self, data):
		self.data.append(data)
		return self
	def __ladd__(self, data):
		self.__add__(data)
		return self
	def __radd__(self, data):
		self.__add__(data)
		return self

def potAmountFromGocrImage(gocrImage, scanTrace=None):
	if scanTrace is None:
		scanTrace = ScanTrace()

	# determine gray level
	#TODO: not shure if i am interpreting grayLevel param correcly. works nicely for
	# regular pixmaps, but fails for inverted onse, having gocr reset to a default value
	#
	grayLevel = 90		# grayLevel in percent of maxGrayLevel. lower values smaller range of matching colors?
	dustSize = 0
	header = gocrImage.header()
	minGray = gocrImage.minGray()
	maxGray = gocrImage.maxGray()
	scanTrace += 'detemined grayLevel: %s-%s' % (minGray, maxGray)
	absGray =  float(grayLevel) / 100 * (maxGray - minGray)
	absGray = int(round(minGray + absGray, 0))
	scanTrace += 'set grayLevel: %s' % absGray

	# scan image
	#TODO: grayLevel threshold.
	# 1) no real idea what it does. i guess it is a threshold in range(grayLevelMin, graylevelmax)
	# 2) we may have to make this user adjustable per template. nasty.
	result, err = gocr.scanImage(
			string=gocrImage.toString(),
			chars='0-9.,',
			dustSize=dustSize,
			grayLevel=absGray,
			)
	scanTrace += 'gocr result: %r' % result
	scanTrace += 'gocr err: %s' % err
	if not result:
		return None, scanTrace
	elif result and err:
		scanTrace.gocrWarinings.append(err)

	# clean gocr output from garbage
	num = result.replace('\x20', '').replace('\n', '').replace('\r', '')
	scanTrace += 'stripped string: %s' % num

	# right strip string up to last digit
	#NOTE: obv gocr may interpret borders and background as chars. funny enough
	# it even chars we opted out may apperar in result
	while num:
		char = num[-1]
		if char.isdigit(): break
		num = num[:-1]
	scanTrace += 'right stripped string: %s' % num

	#NOTE:
	# 1. assertion: pot rect contains at least the 'T' of 'POT' so we always get an unknown char preceeding number
	# 2. assertion: gocr does not recognize any chars following our number
	if '_' not in num:
		scanTrace += 'error - expected unknown char preceeding number'
		return None, scanTrace

	# 'i' should be either '$' or some other currency symbol or the 'T' from 'POT'
	i = num.rindex('_')
	num = num[i +1:]
	scanTrace += 'left stripped string: %s' % num

	# try to reconstruct number
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
	scanTrace += 'formatted number: %s' % num
	try:
		num = float(num)
	except ValueError:
		scanTrace += 'invalid float'
		return None, scanTrace
	return num, scanTrace

#TODO: how to handle worst case: we get an amount but amount is garbage? no way..
def potGetAmount(pixmap):
	scanTrace = ScanTrace()
	scanTrace += 'scan pot -- image: (%sx%s)' % (pixmap.width(), pixmap.height() )
	gocrImage = gocr.ImagePGM.fromQPixmap(pixmap)
	num, scanTrace = potAmountFromGocrImage(gocrImage, scanTrace=scanTrace)
	if num is None:
		# try again with inverted pixels
		scanTrace += 'scan pot -- inverted image'
		gocrImage2 = gocrImage.inverted()
		num, scanTrace = potAmountFromGocrImage(gocrImage2, scanTrace=scanTrace)
	if num is None:
		scanTrace.data.insert(0, 'Could not scan pot\n')
	scanTrace += '<image>%s</image>' % base64.b64encode(gocrImage.toString())
	return num, scanTrace


# for quick and dirty testing
def testPotAmount():
	buff = ''

	buff = base64.b64decode(buff)
	app = QtGui.QApplication([])
	gocrImage = gocr.ImagePGM(buff)
	pixmap = gocrImage.toQPixmap()
	num, scanTrace = potGetAmount(pixmap)
	print 'num:', num
	print 'scanTrace:', scanTrace
	import os
	pixmap.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test-potamount.pgm'), 'PGM', 100)

#testPotAmount()
#************************************************************************************
#
#************************************************************************************

class EventHandler(QtCore.QObject):

	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)

		self._pokerStarsLoginBox = None


	def handleWindowCreated(self, hwnd):

		if self.isPopupNews(hwnd):
			if Tc2Config.settingsValue('PokerStars/AutoClosePopupNews', False).toBool():
				Tc2Win32.windowClose(hwnd)
				Tc2Config.globalObject.feedbackMessage.emit('Closed Popup News')
			return True

		elif self.isTourneyRegistrationMessageBox(hwnd):
			if Tc2Config.settingsValue('PokerStars/AutoCloseTourneyRegistrationBoxes', False).toBool():
				buttons = Tc2Win32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				##windowClose(hwnd)
				Tc2Win32.windowClickButton(buttons['OK'])
				Tc2Config.globalObject.feedbackMessage.emit('Closed Tourney Registration Message Box')
			return True

		elif self.isTableMessageBox(hwnd):
			if Tc2Config.settingsValue('PokerStars/AutoCloseTableMessageBoxes', False).toBool():
				buttons = Tc2Win32.windowGetButtons(hwnd)
				if len(buttons) != 1: return
				if not 'OK' in buttons: return
				Tc2Win32.windowClickButton(buttons['OK'])
				Tc2Config.globalObject.feedbackMessage.emit('Closed Table Message Box')
			return True

		elif self.isLogIn(hwnd):
			if self._pokerStarsLoginBox is None:
				self._pokerStarsLoginBox = hwnd
				if Tc2Config.settingsValue('PokerStars/AutoCloseLogin', False).toBool():
					buttons = Tc2Win32.windowGetButtons(hwnd)
					if sorted(buttons) == ['', 'Cancel', 'Create New Account...', 'Forgot User ID / Password...', 'OK']:
						if Tc2Win32.windowCheckboxIsChecked(buttons['']):
							if Tc2Win32.windowIsEnabled(buttons['OK']):
								Tc2Win32.windowClickButton(buttons['OK'])
								Tc2Config.globalObject.feedbackMessage.emit('Closed Log In Box')
				return True

		return False

	def handleWindowDestroyed(self, hwnd):
		return False

	def handleWindowGainedForeground(self, hwnd):
		template = self.tableTemplate(hwnd)
		if template is not None:
			Tc2Config.globalObject.feedbackMessage.emit(template.name)
			if Tc2Config.settingsValue('PokerStars/MoveMouseToActiveTable', False).toBool():
				if not Tc2Win32.mouseButtonsDown():
					point = template.emptySpace
					point = Tc2Win32.windowClientPointToScreenPoint(hwnd, point)
					Tc2Win32.mouseSetPos(point)
			return True
		return False

	def handleWindowLostForeground(self, hwnd):
		return False

	def handleInputEvent(self, hwnd, hotkey, inputEvent):

		if self.isTable(hwnd):
			if not self.tableHotkeysEnabled(hwnd):
				return False

			hotkeyID = hotkey.id()

			if hotkeyID == Tc2ConfigHotkeys.HotkeyTableSizeNext.id():
				if inputEvent.keyIsDown:
					#  find next table template that is not of current tables size
					size = Tc2Win32.windowGetClientRect(hwnd).size()
					template = None
					pickNext = False
					for i, tmp_template in enumerate(Tc2Config.templateManager):
						if tmp_template.id() == Tc2ConfigTemplates.TemplatePokerStarsTable.id():
							if tmp_template.size	== Tc2Config.SizeNone:
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
						# 	for some reson sending F5 via KeyboardInput has no effect whatsoever, so we tell Tc2Win32
						# to wrap resizing into enter- exitsizemove messages. tested on winXP as well - works nicely
						Tc2Win32.windowSetClientSize(hwnd, template.size, sendSizeMove=True)
						Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (hotkey.menuName(), template.name) )
				inputEvent.accept = True
				return True

			#
			template = self.tableTemplate(hwnd)
			if template is None:
				return False

			handler = None
			if hotkeyID == Tc2ConfigHotkeys.HotkeyCheck.id():
				handler = self.tableHandleCheck
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyFold.id():
				handler = self.tableHandleFold
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyRaise.id():
				handler = self.tableHandleRaise
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyAll_In.id():
				handler = self.tableHandleAll_In
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyHilightBet.id():
				handler = self.tableHandleHilightBet
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyMultiplyBlind.id():
				handler = self.tableHandleMultiplyBlind
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyAddToBet.id():
				handler = self.tableHandleAddToBet
			elif hotkeyID == Tc2ConfigHotkeys.HotkeySubtractFromBet.id():
				handler = self.tableHandleSubtractFromBet
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyMultiplyBet.id():
				handler = self.tableHandleMultiplyBet
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyBetPot.id():
				handler = self.tableHandleBetPot
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyReplayer.id():
				handler = self.tableHandleReplayer
			elif hotkeyID == Tc2ConfigHotkeys.HotkeyInstantHandHistory.id():
				handler = self.tableHandleInstantHandHistory

			if handler is not None:
				if inputEvent.keyIsDown:
					handler(hotkey, template, hwnd, inputEvent)
				inputEvent.accept = True
				return True

		return False

	#NOTE: not easy to determine if a window is a PokerStarswindow. i don't feel like messing around with psapi.dll to get the exefilename.
	# so ..i use a hack. we identify a window as being a stars window if it (or one of its parents) contains a widget classname.startswith('PokerStars')
	# nasty and errorprone, but the most reasonalbe i could come up with now
	def hasPokerStarsWidgets(self, hwnd):
		for hwnd in Tc2Win32.windowChildren(hwnd):
			if Tc2Win32.windowGetClassName(hwnd).startswith('PokerStars'):	return True
		return False

	def isPokerStarsWindow(self, hwnd):
		while hwnd:
			if self.hasPokerStarsWidgets(hwnd): return True
			hwnd = Tc2Win32.windowGetParent(hwnd)
		return False

	TitleLobby = 'PokerStars Lobby'
	ClassLobby = '#32770'	# duh, stars. main windows should never be dialogs
	def isLobby(self, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != self.ClassLobby: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(self.TitleLobby)).startswith(self.TitleLobby): return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	ClassTable = 'PokerStarsTableFrameClass'
	def isTable(self, hwnd):
		if not Tc2Win32.windowGetClassName(hwnd) == self.ClassTable: return False
		return True

	ClassInstantHandHistory = '#32770'
	TitleInstantHandHistory = 'Instant Hand History'
	def isInstantHandHistory(self, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != self.ClassInstantHandHistory: return False
		if Tc2Win32.windowGetText(hwnd) != self.TitleInstantHandHistory: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	ClassNews = '#32770'
	TitleNews = 'News'
	def isPopupNews(self, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != self.ClassNews: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(self.TitleNews)) == self.TitleNews: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	TitleTourneyRegistrationMessageBox = 'Tournament Registration'
	ClassTourneyRegistrationMessageBox = '#32770'
	def isTourneyRegistrationMessageBox(self, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != self.ClassTourneyRegistrationMessageBox: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(self.TitleTourneyRegistrationMessageBox)) == self.TitleTourneyRegistrationMessageBox: return False
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	TitleTableMessageBox = 'PokerStars'
	ClassTableMessageBox = '#32770'
	def isTableMessageBox(self, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != self.ClassTableMessageBox: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(self.TitleTableMessageBox)) == self.TitleTableMessageBox: return False
		hwndParent = Tc2Win32.windowGetParent(hwnd)
		if not self.isTable(hwndParent): return False
		return True

	TitleLogIn = 'Log In'
	ClassLogIn = '#32770'
	def isLogIn(self, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != self.ClassLogIn: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(self.TitleLogIn)) == self.TitleLogIn: return False
		hwndParent = Tc2Win32.windowGetParent(hwnd)
		if not self.isPokerStarsWindow(hwnd): return False
		return True

	def tableTemplate(self, hwnd):
		if self.isTable(hwnd):
			rect = Tc2Win32.windowGetClientRect(hwnd)
			for template in Tc2Config.templateManager:
				if template.id() == Tc2ConfigTemplates.TemplatePokerStarsTable.id():
					if template.size == rect.size():
						return template
		return None

	#TODO: are there tables where BB/SB is not present in caption? closed tourneys ...?
	PatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	ClassTableBetBox = 'PokerStarsSliderEditorClass'
	def tableReadData(self, hwnd):
		data = {}
		text = Tc2Win32.windowGetText(hwnd, maxSize=Tc2Config.MaxWindowText )
		if not text: return data
		match = self.PatAmountSB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['smallBlind'] = float(match.group(1))
		match = self.PatAmountBB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['bigBlind'] = float(match.group(1))
		hwndBetBox = Tc2Win32.windowFindChild(hwnd, self.ClassTableBetBox)
		data['hwndBetBox'] =  hwndBetBox
		data['betBoxIsVisible'] = Tc2Win32.windowIsVisible(hwndBetBox) if hwndBetBox else False
		data['bet'] = None
		if data['hwndBetBox']:
			p = Tc2Win32.windowGetText(hwndBetBox, maxSize=Tc2Config.MaxPokerStarsBetBoxText)
			try:
				data['bet'] = float(p)
			except ValueError: pass
		return data

	#TODO: for some reason hotkeys are still enabled when mouse is over notes editor with editor not having focus.
	#    className we get in this case is "PokerStarsTableClass"
	ClassChat = 'PokerStarsChatClass'
	ClassChatEditor = 'PokerStarsChatEditorClass'
	ClassNoteEditor = 'PokerStarsNoteEditorClass'
	ClassInfoBox = 'PokerStarsInfoClass'
	#NOTE: "Edit" is actually a child widget of 'PokerStarsNoteSelectorClass', so we could add more tests in code below if required
	ClassNoteEditorBox = 'Edit'
	def tableHotkeysEnabled(self, hwnd):
		point = Tc2Win32.mouseGetPos()
		hwndUnderMouse = Tc2Win32.windowFromPoint(point)
		className = Tc2Win32.windowGetClassName(hwndUnderMouse)
		if className in (self.ClassChat, self.ClassNoteEditor, self.ClassChatEditor, self.ClassNoteEditorBox, self.ClassInfoBox):
			return False
		return True

	def tableGetPoint(self,pointName, template):
		point = template.points[pointName]
		if point == Tc2Config.PointNone:
			Tc2Config.globalObject.feedbackMessage.emit('%s: -- Point %s Not Set -' % (template.name,pointName) )
			return None
		return point

	def tableClickButton(self, hwnd, point, template, hotkey):
		#NOTE:
		# 1) checkboxes behave like tri state boxes when we send input. not when clicking them (weird)
		# 2) PostMessage(WM_LBUTTONDOWN,...) works for buttons but is not working for checkboxes
		# 3) SendInput() throws messages anonymously into the eent queue so we can not
		#    be shure the current foreground window is receiving the messages (race condition)
		# 4) there is no way we can check if our input triggered the desired effect
		# 5) we dont know when PS schows us buttons or checkboxes. bet box being
		#    visible gives us an indicator at times, but is useless for example if s.o. is all-in
		mi = Tc2Win32.MouseInput()
		mi.leftClick(point, hwnd=hwnd).send(restoreCursor=Tc2Config.settingsValue('RestoreMousePosition', False).toBool())
		# workaround to send double clicks. this handles checkboxes as expected but may trigger
		# accidental clicks on unrelated tables. we add an abitrary timeout to check if PS has thrown another
		# table to the foreground. no way to get this fail save, we have a race condition
		##time.sleep( min(0.05, Tc2Win32.mouseDoubleClickTime()) )
		##hwnd2 = Tc2Win32.windowForeground()
		##if hwnd == hwnd2:
		##	mi.leftClick(point, hwnd=hwnd).send(restoreCursor=Tc2Config.settingsValue('RestoreMousePosition', False).toBool())
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleCheck(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if data['hwndBetBox'] and data['betBoxIsVisible']:
			point = self.tableGetPoint('ButtonCheck', template)
			if point is None:
				return
		# we always allow checkboxcCheckFold ..stars may show this box when we are newly seated at a table without having the
		# bet amount box created yet
		else:
			point = self.tableGetPoint('CheckboxCheckFold', template)
			if point is None:
				return
		self.tableClickButton(hwnd, point, template, hotkey)

	#TODO: action fold relies on button fold being in the same spot as checkbox fold
	#          ..so we are a bit in trouble here, cos we rely on determining "can or can not bet"
	#          by checking if the bet box is visible or not for it being the only indicator
	#          available at the tables.
	#          background: "fold" is the only action that a) has a checkbox representation AND
	#          b) has a button that may be shown with bet box being invisible - e.g. case
	#          player goes all-in and we can only fold or call but not bet.
	#          bottom line: we have no means to tell if checkbox or button is shown at
	#          a given time without taking actual game state information into account.
	#
	#          braindump:
	#
	#              - determine visibility of checkbox or button by reading game state information.
	#                pretty nasty. think "full bet rule" as an example
	#
	#              - always cklick both - checkbox AND button - (in this order cos clicking
	#                checkbox never causes side effects like other table being put to the
	#                foreground). this would work under the assumption that a) no other object
	#                is present in location checkbox when checkbox is not visible AND no
	#                other object is present in location button if button is not visible AND
	#                location checkbox != location button (!!)
	#                bottom line: this would require to implement a user adjustable flag
	#                [x] My checkbox fold is not located at position button fold
	#
	#              - ..other ideas?
	#
	def tableHandleFold(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if data['hwndBetBox'] and data['betBoxIsVisible']:
			point = self.tableGetPoint('ButtonFold', template)
			if point is None:
				return
		# we always allow checkboxFold ..stars may show this box when we are newly seated at a table without having the
		# bet amount box created yet
		else:
			point = self.tableGetPoint('CheckboxFold', template)
			if point is None:
				return
		self.tableClickButton(hwnd, point, template, hotkey)

	def tableHandleRaise(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		#NOTE: BetBox may not be visible when a player is all-in
		##if not data['betBoxIsVisible']: return
		point = self.tableGetPoint('ButtonRaise', template)
		if point is None:
			return
		self.tableClickButton(hwnd, point, template, hotkey)

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
		pointSliderStart = self.tableGetPoint('BetSliderStart', template)
		if pointSliderStart is None:
			return
		pointSliderEnd = self.tableGetPoint('BetSliderEnd', template)
		if pointSliderEnd is None:
			return
		mi = Tc2Win32.MouseInput()
		mi.leftDrag(pointSliderStart, pointSliderEnd, hwnd=hwnd)
		mi.send(restoreCursor=Tc2Config.settingsValue('RestoreMousePosition', False).toBool())
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleMultiplyBlind(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == Tc2Config.BigBlind:
			newBet = data['bigBlind'] * hotkey.multiplier() * inputEvent.steps
		elif hotkey.baseValue() == Tc2Config.SmallBlind:
			newBet = data['smallBlind'] * hotkey.multiplier() * inputEvent.steps
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		#TODO: adjust bet to 'Settings/RoundBets' ? kind of contradictionary
		newBet = Tc2Config.formatedBet(newBet, blinds=None)
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def tableHandleAddToBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == Tc2Config.BigBlind:
			newBet = data['bet'] + (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue() == Tc2Config.SmallBlind:
			newBet = data['bet'] + (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		#TODO: adjust bet to 'Settings/RoundBets' ? kind of contradictionary
		newBet = Tc2Config.formatedBet(newBet, blinds=None)
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def tableHandleSubtractFromBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == Tc2Config.BigBlind:
			newBet = data['bet'] - (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue() == Tc2Config.SmallBlind:
			newBet = data['bet'] - (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		#TODO: adjust bet to 'Settings/RoundBets' ? kind of contradictionary
		newBet = Tc2Config.formatedBet(newBet, blinds=None)
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def tableHandleMultiplyBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		newBet = data['bet'] * hotkey.multiplier() * inputEvent.steps
		newBet = Tc2Config.formatedBet(newBet, blinds=(data['smallBlind'], data['bigBlind']) )
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def tableHandleBetPot(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return

		pointTopLeft = template.points['PotTopLeft']
		pointBottomRight = template.points['PotBottomRight']
		if pointTopLeft == Tc2Config.PointNone:
			Tc2Config.globalObject.feedbackMessage.emit('%s: -- Point Pot Top Left Not Set -' % template.name)
			return
		if pointBottomRight == Tc2Config.PointNone:
			Tc2Config.globalObject.feedbackMessage.emit('%s: -- Point Pot Bottom Right Not Set -' % template.name)
			return

		# grab pot rect
		pixmap = QtGui.QPixmap.grabWindow(hwnd,
					pointTopLeft.x(),
					pointTopLeft.y(),
					pointBottomRight.x() - pointTopLeft.x(),
					pointBottomRight.y() - pointTopLeft.y(),
					)
		num, scanTrace = potGetAmount(pixmap)
		#TODO: what to do with gocr warnings?
		#num = None	# for testing, triggers exception
		if num is None:
			try:
				raise ValueError(scanTrace)
			except:
				Tc2Config.handleException()
				Tc2Config.globalObject.feedbackMessage.emit('%s: Error - Could not scan pot' % hotkey.action() )
				return
		newBet = round(num * hotkey.multiplier(), 2)
		newBet = Tc2Config.formatedBet(newBet, blinds=(data['smallBlind'], data['bigBlind']) )
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet) )

	def tableHandleHilightBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		hwndBetBox = data['hwndBetBox']
		if not hwndBetBox: return
		if not data['betBoxIsVisible']: return
		point = QtCore.QPoint(2, 2)
		mi = Tc2Win32.MouseInput()
		mi.leftClickDouble(point, hwnd=hwndBetBox)
		mi.send(restoreCursor=Tc2Config.settingsValue('RestoreMousePosition', False).toBool())
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def _tableClickRestoreFocus(self, hwnd, point, template):
		#NOTE: we always double click. not realy necessary here
		mi = Tc2Win32.MouseInput()
		mi.leftClickDouble(point, hwnd=hwnd)
		mi.send(restoreCursor=False)
		# replayer gains focus, so we have to wait a bit and send another click to reactivate the table.
		#TODO: for some reason (linux/wine?) table regain focus but is not activated when the replayer is opend for the first time
		mi = Tc2Win32.MouseInput()
		mi.leftClickDouble(template.points['EmptySpace'], hwnd=hwnd)
		mi.send(restoreCursor=Tc2Config.settingsValue('RestoreMousePosition', False).toBool())

	def tableHandleReplayer(self, hotkey, template, hwnd, inputEvent):
		point = self.tableGetPoint('Replayer', template)
		if point is None:
			return
		self._tableClickRestoreFocus(hwnd, point, template)
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleInstantHandHistory(self, hotkey, template, hwnd, inputEvent):
		point = self.tableGetPoint('InstantHandHistory', template)
		if point is None:
			return
		self._tableClickRestoreFocus(hwnd, point, template)
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))


