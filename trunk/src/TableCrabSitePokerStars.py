
#TODO: for some reason ButtonCheck and ButtonRaise are not working as expected postflop (preflop is ok). we have to trigger
#				hotkey two times (always, sometimes?) to get the desired effect. double clicking right now ..have to experiment.

import TableCrabConfig
import TableCrabWin32
import TableCrabHotkeys
import TableCrabTemplates
from TableCrabLib.gocr import gocr

import re, time

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
	scanTrace += repr(gocrImage.toString())

	# determine gray level
	#TODO: not shure if i am interpreting grayLevel param correcly. works nicely for
	# regular pixmaps, but fails for inverted onse, having gocr reset to a default value
	#
	grayLevel = 90		# grayLevel in percent of maxGrayLevel. lower values smaller range of matching colors?
	dustSize = 0
	header = gocrImage.header()
	minGray = gocrImage.minGray()
	maxGray = gocrImage.maxGray()
	scanTrace += '>>detemined grayLevel: %s-%s' % (minGray, maxGray)
	absGray =  float(grayLevel) / 100 * (maxGray - minGray)
	absGray = int(round(minGray + absGray, 0))
	scanTrace += '>>set grayLevel: %s' % absGray

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
	scanTrace += '>>gocr result: %r' % result
	scanTrace += '>>gocr err: %s' % err
	if not result:
		return None, scanTrace
	elif result and err:
		scanTrace.gocrWarinings.append(err)

	# clean gocr output from garbage
	num = result.replace('\x20', '').replace('\n', '').replace('\r', '')
	scanTrace += '>>stripped string: %s' % num

	# right strip string up to last digit
	#NOTE: obv gocr may interpret borders and background as chars. funny enough
	# it even chars we opted out may apperar in result
	while num:
		char = num[-1]
		if char.isdigit(): break
		num = num[:-1]
	scanTrace += '>>right stripped string: %s' % num

	#NOTE:
	# 1. assertion: pot rect contains at least the 'T' of 'POT' so we always get an unknown char preceeding number
	# 2. assertion: gocr does not recognize any chars following our number
	if '_' not in num:
		scanTrace += '>>error - expected unknown char preceeding number'
		return None, scanTrace

	# 'i' should be either '$' or some other currency symbol or the 'T' from 'POT'
	i = num.rindex('_')
	num = num[i +1:]
	scanTrace += '>>left stripped string: %s' % num

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
	scanTrace += '>>formatted number: %s' % num
	try:
		num = float(num)
	except ValueError:
		scanTrace += '>>invalid float'
		return None, scanTrace
	return num, scanTrace

#TODO: how to handle worst case: we get an amount but amount is garbage? no way..
def potGetAmount(pixmap):
	scanTrace = ScanTrace()
	scanTrace += '>>scan pot -- original image: (%sx%s)' % (pixmap.width(), pixmap.height() )
	gocrImage = gocr.ImagePGM.fromQPixmap(pixmap)
	num, scanTrace = potAmountFromGocrImage(gocrImage, scanTrace=scanTrace)
	if num is None:
		# try again with inverted pixels.
		gocrImage2 = gocrImage.inverted()
		scanTrace += '>>scan pot -- inverted image'
		num, scanTrace = potAmountFromGocrImage(gocrImage2, scanTrace=scanTrace)
	return num, scanTrace


# for quick and dirty testing
def testPotAmount():
	buff = ''		# paste image here
	app = QtGui.QApplication([])
	gocrImage = gocr.ImagePGM(buff)
	header = gocrImage.header()
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
			point = template.points['ButtonCheck']
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point ButtonCheck Not Set -' % template.name)
				return
		# we always allow checkboxcCheckFold ..stars may show this box when we are newly seated at a table without having the
		# bet amount box created yet
		else:
			point = template.points['CheckboxCheckFold']
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point CheckboxCheckFold Not Set -' % template.name)
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
			point =  template.points['ButtonFold']
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point ButtonFold Not Set -' % template.name)
				return
		# we always allow checkboxFold ..stars may show this box when we are newly seated at a table without having the
		# bet amount box created yet
		else:
			point = template.points['CheckboxFold']
			if point == TableCrabConfig.PointNone:
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point CheckboxFold Not Set -' % template.name)
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
		if  template.points['ButtonRaise'] == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point ButtonRaise Not Set -' % template.name)
			return
		#NOTE: we always double click. seems to work more reliably
		TableCrabWin32.mouseInputLeftClickDouble(
				template.points['ButtonRaise'],
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
		pointSliderStart = template.points['BetSliderStart']
		pointSliderEnd = template.points['BetSliderEnd']
		if pointSliderStart == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point BetSliderStart Not Set -' % template.name)
			return
		if pointSliderEnd == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point BetSliderEnd Not Set -' % template.name)
			return
		TableCrabWin32.mouseInputMouseDrag(
				pointSliderStart,
				pointSliderEnd,
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
		if hotkey.baseValue() == TableCrabConfig.BigBlind:
			newBet = data['bet'] + (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue == TableCrabConfig.SmallBlind:
			newBet = data['bet'] + (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		#TODO: adjust bet to 'Settings/RoundBets' ? kind of contradictionary
		newBet = TableCrabConfig.formatedBet(newBet, blinds=None)
		#NOTE: the box gets mesed up when unicode is thrown at it
		TableCrabWin32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def tableHandleSubtractFromBet(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		if inputEvent.steps == 0: return
		if hotkey.baseValue() == TableCrabConfig.BigBlind:
			newBet = data['bet'] - (data['bigBlind'] * hotkey.multiplier() * inputEvent.steps)
		elif hotkey.baseValue == TableCrabConfig.SmallBlind:
			newBet = data['bet'] - (data['smallBlind'] * hotkey.multiplier() * inputEvent.steps)
		else:
			raise ValueError('can not handle base value: %s' % hotkey.baseValue() )
		#TODO: adjust bet to 'Settings/RoundBets' ? kind of contradictionary
		newBet = TableCrabConfig.formatedBet(newBet, blinds=None)
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
		newBet = TableCrabConfig.formatedBet(newBet, blinds=(data['smallBlind'], data['bigBlind']) )
		#NOTE: the box gets mesed up when unicode is thrown at it
		TableCrabWin32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		TableCrabConfig.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name, hotkey.action(), newBet))

	def tableHandleBetPot(self, hotkey, template, hwnd, inputEvent):
		data = self.tableReadData(hwnd)
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return

		pointTopLeft = template.points['PotTopLeft']
		pointBottomRight = template.points['PotBottomRight']
		if pointTopLeft == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point Pot Top Left Not Set -' % template.name)
			return
		if pointBottomRight == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point Pot Bottom Right Not Set -' % template.name)
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
		##num = None	# for testing, triggers exception
		if num is None:
			try:
				raise ValueError(scanTrace)
			except:
				TableCrabConfig.handleException()
				TableCrabConfig.globalObject.feedbackMessage.emit('%s: Error - Could not scan pot' % hotkey.action() )
				return

		newBet = round(num * hotkey.multiplier(), 2)
		newBet = TableCrabConfig.formatedBet(newBet, blinds=(data['smallBlind'], data['bigBlind']) )
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
				template.points['EmptySpace'],
				hwnd=hwnd,
				restoreCursor=TableCrabConfig.settingsValue('RestoreMousePosition', False).toBool(),
				)

	def tableHandleReplayer(self, hotkey, template, hwnd, inputEvent):
		point = template.points['Replayer']
		if point == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point Replayer Not Set -' % template.name)
		else:
			self._tableClickRestoreFocus(hwnd, point, template)
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))

	def tableHandleInstantHandHistory(self, hotkey, template, hwnd, inputEvent):
		point = template.points['InstantHandHistory']
		if point == TableCrabConfig.PointNone:
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: -- Point InstantHandHistory Not Set -' % template.name)
		else:
			self._tableClickRestoreFocus(hwnd, point, template)
			TableCrabConfig.globalObject.feedbackMessage.emit('%s: %s' % (template.name, hotkey.action() ))


