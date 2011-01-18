
#NOTE: all windows we handle are not save from race conditions. we may accidently
# act on random windows. we could add additional checks emidiately before taking
# actions to minimize the risk.
#

import Tc2Config
import Tc2Win32
import Tc2ConfigHotkeys
import Tc2ConfigTemplates
import Tc2HandGrabberPokerStars
from Tc2Lib.gocr import gocr

import re, time, base64

from PyQt4 import QtCore, QtGui
#************************************************************************************
# PokerStars windows we handle
#************************************************************************************
WindowClasses = []

class WindowClassMeta(type):
	def __new__(klass, name, bases, kws):
		newKlass = type.__new__(klass, name, bases, kws)
		WindowClasses.append(newKlass)
		return newKlass

#NOTE: unhandled base window
class PokerStarsWindow(object):
	__metaclass__ = WindowClassMeta
	#NOTE: not easy to determine if a window is a PokerStarswindow. i don't feel like messing around with psapi.dll to get the exefilename.
	# so ..i use a hack. we identify a window as being a stars window if it (or one of its parents) contains a widget classname.startswith('PokerStars')
	# nasty and errorprone, but the most reasonalbe i could come up with now
	@classmethod
	def hasPokerStarsWidgets(klass, hwnd):
		for hwnd in Tc2Win32.windowChildren(hwnd):
			if Tc2Win32.windowGetClassName(hwnd).startswith('PokerStars'): return True
		return False
	@classmethod
	def matchesHwnd(klass, hwnd):
		while hwnd:
			if klass.hasPokerStarsWidgets(hwnd): return True
			hwnd = Tc2Win32.windowGetParent(hwnd)
		return False
	@classmethod
	def fromHwnd(klass, siteHandler, hwnd):
		return None
	def __init__(self, siteHandler, hwnd):
		self.siteHandler = siteHandler
		self.hwnd = hwnd
	def handleCreated(self):
		pass
	def handleDestroyed(self):
		pass
	def handleGainedForeground(self):
		pass
	def handleLostForeground(self):
		pass
	def handleInputEvent(self, hotkey, inputEvent):
		pass


class Lobby(PokerStarsWindow):
	WindowTitle = 'PokerStars Lobby'
	WindowClassName = '#32770'	# duh, stars. main windows should never be dialogs
	@classmethod
	def matchesHwnd(klass, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != self.WindowClassName: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(klass.WindowTitle)).startswith(klass.WindowTitle): return False
		if not PokerStarsWindow.matchesHwnd(hwnd): return False
		return True


class Table(PokerStarsWindow):
	WindowClassName = 'PokerStarsTableFrameClass'
	@classmethod
	def matchesHwnd(klass, hwnd):
		if not Tc2Win32.windowGetClassName(hwnd) == klass.WindowClassName: return False
		return True
	@classmethod
	def fromHwnd(klass, siteHandler, hwnd):
		if klass.matchesHwnd(hwnd):
			return klass(siteHandler, hwnd)
		return None

	def handleGainedForeground(self):
		template = self.template()
		if template is not None:
			Tc2Config.globalObject.feedbackMessage.emit(template.name() )
			if Tc2Config.globalObject.settingsPokerStars.moveMouseToActiveTable():
				if not Tc2Win32.mouseButtonsDown():
					point = Tc2Win32.mouseGetPos()
					rect = Tc2Win32.windowGetRect(self.hwnd)
					if not rect.contains(point):
						point = template.points['EmptySpace']
						point = Tc2Win32.windowClientPointToScreenPoint(self.hwnd, point)
						Tc2Win32.mouseSetPos(point)
			return True
		return False

	def handleInputEvent(self, hotkey, inputEvent):
		if not self.hotkeysEnabled():
			return

		hotkeyID = hotkey.id()

		if hotkeyID == Tc2ConfigHotkeys.HotkeyTableSizeNext.id():
			if inputEvent.keyIsDown:
				#  find next table template that is not of current tables size
				size = Tc2Win32.windowGetClientRect(self.hwnd).size()
				templates = []
				indexCurrent = None
				i = 0
				for template in Tc2Config.globalObject.templateManager:
					if template.id() != Tc2ConfigTemplates.TemplatePokerStarsTable.id():
						continue
					if not template.isEnabled():
						continue
					if template.size	== Tc2Config.SizeNone:
						continue
					if template.size == size:
						indexCurrent = i
					templates.append(template)
					i += 1
				if templates:
					if indexCurrent is None:
						indexCurrent = len(templates) -1
					indexNext = indexCurrent +1
					if indexNext >= len(templates):
						indexNext = 0
					template = templates[indexNext]
					#NOTE: on wine tables do not get redrawn on resize [ http://bugs.winehq.org/show_bug.cgi?id=5941 ].
					# 	for some reson sending F5 via KeyboardInput has no effect whatsoever, so we tell Tc2Win32
					# to wrap resizing into enter- exitsizemove messages. tested on winXP as well - works nicely
					Tc2Win32.windowSetClientSize(self.hwnd, template.size, sendSizeMove=True)
					Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (hotkey.menuName(), template.name() ) )
			inputEvent.accept = True
			return True

		#
		template = self.template()
		if template is None:
			return False

		handler = None
		if hotkeyID == Tc2ConfigHotkeys.HotkeyCheck.id():
			handler = self.handleCheck
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyFold.id():
			handler = self.handleFold
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyRaise.id():
			handler = self.handleRaise
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyAll_In.id():
			handler = self.handleAll_In
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyHilightBet.id():
			handler = self.handleHilightBet
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyMultiplyBlind.id():
			handler = self.handleMultiplyBlind
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyAddToBet.id():
			handler = self.handleAddToBet
		elif hotkeyID == Tc2ConfigHotkeys.HotkeySubtractFromBet.id():
			handler = self.handleSubtractFromBet
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyMultiplyBet.id():
			handler = self.handleMultiplyBet
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyBetPot.id():
			handler = self.handleBetPot
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyReplayer.id():
			handler = self.handleReplayer
		elif hotkeyID == Tc2ConfigHotkeys.HotkeyInstantHandHistory.id():
			handler = self.handleInstantHandHistory
		elif hotkeyID in (
					Tc2ConfigHotkeys.HotkeyClick1.id(),
					Tc2ConfigHotkeys.HotkeyClick2.id(),
					Tc2ConfigHotkeys.HotkeyClick3.id(),
					Tc2ConfigHotkeys.HotkeyClick4.id(),
					Tc2ConfigHotkeys.HotkeyClick5.id(),
					):
			handler = self.handleHotkeyClick

		if handler is not None:
			if inputEvent.keyIsDown:
				handler(hotkey, template, inputEvent)
			inputEvent.accept = True

	def template(self):
		rect = Tc2Win32.windowGetClientRect(self.hwnd)
		for template in Tc2Config.globalObject.templateManager:
			if not template.isEnabled(): continue
			if template.id() != Tc2ConfigTemplates.TemplatePokerStarsTable.id(): continue
			if template.size != rect.size(): continue
			return template
		return None

	#TODO: for some reason hotkeys are still enabled when mouse is over notes editor with editor not having focus.
	#    className we get in this case is "PokerStarsTableClass"
	ClassChat = 'PokerStarsChatClass'
	ClassChatEditor = 'PokerStarsChatEditorClass'
	ClassNoteEditor = 'PokerStarsNoteEditorClass'
	ClassInfoBox = 'PokerStarsInfoClass'
	#NOTE: "Edit" is actually a child widget of 'PokerStarsNoteSelectorClass', so we could add more tests in code below if required
	ClassNoteEditorBox = 'Edit'
	def hotkeysEnabled(self):
		point = Tc2Win32.mouseGetPos()
		hwndUnderMouse = Tc2Win32.windowFromPoint(point)
		className = Tc2Win32.windowGetClassName(hwndUnderMouse)
		if className in (self.ClassChat, self.ClassNoteEditor, self.ClassChatEditor, self.ClassNoteEditorBox, self.ClassInfoBox):
			return False
		return True

	#TODO: are there tables where BB/SB is not present in caption? closed tourneys ...?
	PatAmountSB = re.compile('.*(?: [^0-9\.]|\s)   ( (?: 0\.[0-9]{2})   |    (?: [0-9]+))/.*', re.X|re.I)
	PatAmountBB = re.compile('.*/[^0-9\.]?(   (?: 0\.[0-9]{2})   |    (?: [0-9]+)).*', re.X|re.I)
	ClassTableBetBox = 'PokerStarsSliderEditorClass'
	def readData(self):
		data = {}
		text = Tc2Win32.windowGetText(self.hwnd, maxSize=Tc2Config.MaxWindowText )
		if not text: return data
		match = self.PatAmountSB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['smallBlind'] = float(match.group(1))
		match = self.PatAmountBB.match(text)
		if match is None:
			raise ValueError('could not determine smallBlind: %r' % text)
		data['bigBlind'] = float(match.group(1))
		hwndBetBox = Tc2Win32.windowFindChild(self.hwnd, self.ClassTableBetBox)
		data['hwndBetBox'] =  hwndBetBox
		data['betBoxIsVisible'] = Tc2Win32.windowIsVisible(hwndBetBox) if hwndBetBox else False
		data['bet'] = None
		if data['hwndBetBox']:
			p = Tc2Win32.windowGetText(hwndBetBox, maxSize=Tc2Config.MaxPokerStarsBetBoxText)
			try:
				data['bet'] = float(p)
			except ValueError: pass
		return data

	def point(self,pointName, template):
		point = template.points[pointName]
		if point == Tc2Config.PointNone:
			Tc2Config.globalObject.feedbackMessage.emit('%s: -- Point %s Not Set -' % (template.name() ,pointName) )
			return None
		return point

	def clickButton(self, point, template, hotkey):
		#NOTE:
		# 1) checkboxes behave like tri state boxes when we send input. not when clicking them (weird)
		# 2) PostMessage(WM_LBUTTONDOWN,...) works for buttons but is not working for checkboxes
		# 3) SendInput() throws messages anonymously into the eent queue so we can not
		#    be shure the current foreground window is receiving the messages (race condition)
		# 4) there is no way we can check if our input triggered the desired effect
		# 5) we dont know when PS schows us buttons or checkboxes. bet box being
		#    visible gives us an indicator at times, but is useless for example if s.o. is all-in
		mi = Tc2Win32.MouseInput()
		mi.leftClick(point, hwnd=self.hwnd).send(restoreCursor=Tc2Config.globalObject.settingsGlobal.restoreMousePosition())
		# workaround to send double clicks. this handles checkboxes as expected but may trigger
		# accidental clicks on unrelated tables. we add an abitrary timeout to check if PS has thrown another
		# table to the foreground. no way to get this fail save, we have a race condition
		##time.sleep( min(0.05, Tc2Win32.mouseDoubleClickTime()) )
		##hwnd2 = Tc2Win32.windowForeground()
		##if hwnd == hwnd2:
		##	mi.leftClick(point, hwnd=hwnd).send(restoreCursor=self.settingsGlobal.Tc2Config.globalObject.settingsGlobal.())
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name() , hotkey.action() ))

	def handleCheck(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		point = self.point('ButtonCheck', template)
		if point is None:
			return
		self.clickButton(point, template, hotkey)

	def handleFold(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		point = self.point('ButtonFold', template)
		if point is None:
			return
		self.clickButton(point, template, hotkey)

	def handleRaise(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		point = self.point('ButtonRaise', template)
		if point is None:
			return
		self.clickButton(point, template, hotkey)

	def handleHotkeyClick(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		point = self.point(hotkey.id(), template)
		if point is None:
			return
		self.clickButton(point, template, hotkey)

	#NOTE: there is another way to handle all-in. no reliable one but could be a fallback. looks like bet amount box accepts
	# values up to some hard coded PS wide maximum. if this maximum is exceeded the bet box resets to 0.
	# played a bit around with this:
	# 20.000.000 ok
	# 21.000.000 ok
	# 24.000.000 reset
	# funny enough you can enter up to 9 digits into the box when the maximum is actually located somewhere in the 8 digits region.
	# either a bug or feature that is.
	def handleAll_In(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		point = self.point('BetSliderEnd', template)
		if point is None:
			return
		mi = Tc2Win32.MouseInput()
		mi.leftClick(point, hwnd=self.hwnd).send(restoreCursor=Tc2Config.globalObject.settingsGlobal.restoreMousePosition())
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name() , hotkey.action() ))

	def handleMultiplyBlind(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		newBet = hotkey.applyAction(inputEvent, blinds=(data['smallBlind'], data['bigBlind']) )
		if newBet is None:
			return
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name() , hotkey.action(), newBet))

	def handleAddToBet(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		newBet = hotkey.applyAction(inputEvent, blinds=(data['smallBlind'], data['bigBlind']), bet=data['bet'])
		if newBet is None:
			return
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name() , hotkey.action(), newBet))

	def handleSubtractFromBet(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		newBet = hotkey.applyAction(inputEvent, blinds=(data['smallBlind'], data['bigBlind']), bet=data['bet'])
		if newBet is None:
			return
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name() , hotkey.action(), newBet))

	def handleMultiplyBet(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return
		if data['bet'] is None: return
		newBet = hotkey.applyAction(inputEvent, blinds=(data['smallBlind'], data['bigBlind']), bet=data['bet'])
		if newBet is None:
			return
		#NOTE: the box gets mesed up when unicode is thrown at it
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name() , hotkey.action(), newBet))

	PatPot = re.compile(r'[_\s]*_0_\s*_?(?P<output>[0-9,\.]+)[_\s]*', re.X|re.U)
	def handleBetPot(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		if not data['hwndBetBox']: return
		if not data['betBoxIsVisible']: return

		pointTopLeft = template.points['PotTopLeft']
		pointBottomRight = template.points['PotBottomRight']
		if pointTopLeft == Tc2Config.PointNone:
			Tc2Config.globalObject.feedbackMessage.emit('%s: -- Point Pot Top Left Not Set -' % template.name() )
			return
		if pointBottomRight == Tc2Config.PointNone:
			Tc2Config.globalObject.feedbackMessage.emit('%s: -- Point Pot Bottom Right Not Set -' % template.name() )
			return

		# grab pot rect
		pixmap = QtGui.QPixmap.grabWindow(self.hwnd,
					pointTopLeft.x(),
					pointTopLeft.y(),
					pointBottomRight.x() - pointTopLeft.x(),
					pointBottomRight.y() - pointTopLeft.y(),
					)
		pgmImage = gocr.ImagePGM.fromQPixmap(pixmap)
		# scan pot
		num, err = gocr.scanImage(
				pgmImage=pgmImage,
				chars='0-9,.',
				dustSize=0,
				outputType=gocr.OutputTypeFloat,
				outputPattern=self.PatPot,
				)
		if num is None:
			# try again with inverted image
			num, err = gocr.scanImage(
					pgmImage=pgmImage,
					flagInvertImage=True,
					chars='0-9,.',
					dustSize=0,
					outputType=gocr.OutputTypeFloat,
					outputPattern=self.PatPot,
					)
			if num is None:
				try:
					raise ValueError('Could not scan pot\n<image>%s</image>' % base64.b64encode(pgmImage.toString()))
				except:
					Tc2Config.handleException()
					Tc2Config.globalObject.feedbackMessage.emit('%s: Error - Could not scan pot' % hotkey.action() )
					return

		newBet = hotkey.applyAction(inputEvent, blinds=(data['smallBlind'], data['bigBlind']), bet=num)
		if newBet is None:
			return
		Tc2Win32.windowSetText(data['hwndBetBox'], text=newBet, isUnicode=False)
		Tc2Config.globalObject.feedbackMessage.emit('%s - %s -- %s' % (template.name() , hotkey.action(), newBet) )

	def handleHilightBet(self, hotkey, template, inputEvent):
		data = self.readData()
		if not data: return
		hwndBetBox = data['hwndBetBox']
		if not hwndBetBox: return
		if not data['betBoxIsVisible']: return
		point = QtCore.QPoint(2, 2)
		mi = Tc2Win32.MouseInput()
		mi.leftClickDouble(point, hwnd=hwndBetBox)
		mi.send(restoreCursor=Tc2Config.globalObject.settingsGlobal.restoreMousePosition())
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name() , hotkey.action() ))

	def clickRestoreFocus(self, point, template):
		#NOTE: we always double click. not realy necessary here
		mi = Tc2Win32.MouseInput()
		mi.leftClickDouble(point, hwnd=self.hwnd)
		mi.send(restoreCursor=False)
		# replayer gains focus, so we have to wait a bit and send another click to reactivate the table.
		mi = Tc2Win32.MouseInput()
		mi.leftClickDouble(template.points['EmptySpace'], hwnd=self.hwnd)
		mi.send(restoreCursor=Tc2Config.globalObject.settingsGlobal.restoreMousePosition())

	def handleReplayer(self, hotkey, template, inputEvent):
		point = self.point('Replayer', template)
		if point is None:
			return
		self.clickRestoreFocus(point, template)
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name() , hotkey.action() ))

	def handleInstantHandHistory(self, hotkey, template, inputEvent):
		point = self.point('InstantHandHistory', template)
		if point is None:
			return
		self.clickRestoreFocus(point, template)
		Tc2Config.globalObject.feedbackMessage.emit('%s: %s' % (template.name() , hotkey.action() ))


class LogInBox(PokerStarsWindow):
	WindowTitle = 'Log In'
	WindowClassName = '#32770'
	@classmethod
	def matchesHwnd(klass, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != klass.WindowClassName: return False
		if Tc2Win32.windowGetText(hwnd, maxSize=len(klass.WindowTitle)) != klass.WindowTitle: return False
		if not PokerStarsWindow.matchesHwnd(hwnd): return False
		return True
	@classmethod
	def fromHwnd(klass, siteHandler, hwnd):
		if klass.matchesHwnd(hwnd):
			return klass(siteHandler, hwnd)
		return None
	def handleCreated(self):
		if Tc2Config.globalObject.settingsPokerStars.autoCloseLogin():
			buttons = Tc2Win32.windowGetButtons(self.hwnd)
			if sorted(buttons) == ['', 'Cancel', 'Create New Account...', 'Forgot User ID / Password...', 'OK']:
				if Tc2Win32.windowCheckboxIsChecked(buttons['']):
					if Tc2Win32.windowIsEnabled(buttons['OK']):
						Tc2Win32.windowClickButton(buttons['OK'])
						Tc2Config.globalObject.feedbackMessage.emit('Closed Log In Box')


class TableMessageBox(PokerStarsWindow):
	WindowTitle = 'PokerStars'
	WindowClassName = '#32770'
	@classmethod
	def matchesHwnd(klass, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != klass.WindowClassName: return False
		if Tc2Win32.windowGetText(hwnd, maxSize=len(klass.WindowTitle)) != klass.WindowTitle: return False
		hwndParent = Tc2Win32.windowGetParent(hwnd)
		if not Table.matchesHwnd(hwndParent): return False
		return True
	@classmethod
	def fromHwnd(klass, siteHandler, hwnd):
		if klass.matchesHwnd(hwnd):
			return klass(siteHandler, hwnd)
		return None
	def handleCreated(self):
		if Tc2Config.globalObject.settingsPokerStars.autoCloseTableMessageBoxes():
			buttons = Tc2Win32.windowGetButtons(self.hwnd)
			if len(buttons) != 1: return
			if not 'OK' in buttons: return
			Tc2Win32.windowClickButton(buttons['OK'])
			Tc2Config.globalObject.feedbackMessage.emit('Closed Table Message Box')


class TourneyRegistrationMessageBox(PokerStarsWindow):
	WindowTitle = 'Tournament Registration'
	WindowClassName = '#32770'
	@classmethod
	def matchesHwnd(klass, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != klass.WindowClassName: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(klass.WindowTitle)) == klass.WindowTitle: return False
		if not PokerStarsWindow.matchesHwnd(hwnd): return False
		return True
	@classmethod
	def fromHwnd(klass, siteHandler, hwnd):
		if klass.matchesHwnd(hwnd):
			return klass(siteHandler, hwnd)
		return None
	def handleCreated(self):
		if Tc2Config.globalObject.settingsPokerStars.autoCloseTourneyRegistrationBoxes():
			buttons = Tc2Win32.windowGetButtons(self.hwnd)
			if len(buttons) != 1: return
			if not 'OK' in buttons: return
			##windowClose(hwnd)
			Tc2Win32.windowClickButton(buttons['OK'])
			Tc2Config.globalObject.feedbackMessage.emit('Closed Tourney Registration Message Box')


class PopUpNews(PokerStarsWindow):
	WindowTitle = 'News'
	WindowClassName = '#32770'
	@classmethod
	def matchesHwnd(klass, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != klass.WindowClassName: return False
		if not Tc2Win32.windowGetText(hwnd, maxSize=len(klass.WindowTitle)) == klass.WindowTitle: return False
		if not PokerStarsWindow.matchesHwnd(hwnd): return False
		return True
	@classmethod
	def fromHwnd(klass, siteHandler, hwnd):
		if klass.matchesHwnd(hwnd):
			return klass(siteHandler, hwnd)
		return None
	def handleCreated(self):
		if Tc2Config.globalObject.settingsPokerStars.autoClosePopupNews():
			Tc2Win32.windowClose(self.hwnd)
			Tc2Config.globalObject.feedbackMessage.emit('Closed Popup News')


class InstantHandHistory(PokerStarsWindow):
	WindowTitle = 'Instant Hand History'
	WindowClassName = '#32770'
	WidgetClassName = 'PokerStarsViewClass'
	@classmethod
	def matchesHwnd(klass, hwnd):
		if Tc2Win32.windowGetClassName(hwnd) != klass.WindowClassName: return False
		if Tc2Win32.windowGetText(hwnd, maxSize=len(klass.WindowTitle)) != klass.WindowTitle: return False
		if not PokerStarsWindow.matchesHwnd(hwnd): return False
		return True
	@classmethod
	def fromHwnd(klass, siteHandler, hwnd):
		if klass.matchesHwnd(hwnd):
			return klass(siteHandler, hwnd)
		return None
	def __init__(self, *args, **kws):
		PokerStarsWindow.__init__(self, *args, **kws)
		self._timer = QtCore.QTimer(self.siteHandler)
		self._timer.setInterval(Tc2Config.HandGrabberTimeout * 1000)
		self._timer.timeout.connect(self.grabHand)
		#self._timer.setSingleShot(True)

		self._handParser = Tc2HandGrabberPokerStars.HandParser()
		self._handFormatter = Tc2HandGrabberPokerStars.HandFormatterHtmlTabular()
		self._handFormatter.onGlobalObjectInitSettingsFinished(Tc2Config.globalObject)	#NOTE: have to init here
		self._data = ''
		self._hwndEdit = None
		for hwnd in Tc2Win32.windowChildren(self.hwnd):
			if Tc2Win32.windowGetClassName(hwnd) == self.WidgetClassName:
				self._hwndEdit = hwnd
				break
		if self._hwndEdit is None:
			try:
				raise ValueError('Instant hand history edit box not found')
			except:
				Tc2Config.handleException()
		else:
			self._timer.start()

	def grabHand(self):
		#NOTE: we could be faced with an arbitrary windowat this point or an inavlid handle
		if Tc2Win32.windowGetTextLength(self._hwndEdit) > Tc2Config.MaxHandHistoryText:
			#TODO: have to find a better way to give feedback on what hapens on hand grabbing
			Tc2Config.globalObject.feedbackMessage.emit(self.parent(), 'Hand text too long')
			return
		data = Tc2Win32.windowGetText(self._hwndEdit, maxSize=Tc2Config.MaxHandHistoryText)
		if data and data != self._data:
			self._data = data
			handData = ''
			hand = Tc2HandGrabberPokerStars.Hand()
			#TODO: very sloppy test to minimize risk we are grabbing 'show summary only' in instant hand history
			if not '*** HOLE CARDS ***' in data:
				pass
			else:
				#NOTE: we are let Tc2Config handle errors because we are maybe working with arbitrary data
				# from an unknown window
				try:
					hand = self._handParser.parse(data)
				except:
					Tc2Config.handleException('\n' + data)
				else:
					handData = self._handFormatter.dump(hand)
			self.siteHandler.handGrabbed.emit(hand, handData)

#************************************************************************************
#
#************************************************************************************
class SiteHandler(QtCore.QObject):

	handGrabbed = QtCore.pyqtSignal(QtCore.QObject, QtCore.QString)

	def __init__(self, parent=None):
		QtCore.QObject.__init__(self, parent)

		self._windows ={}		# hwnd --> window

		Tc2Config.globalObject.objectCreatedSiteHandlerPokerStars.emit(self)

	def handleWindowCreated(self, hwnd):
		for windowClass in WindowClasses:
			window = windowClass.fromHwnd(self, hwnd)
			if window is not None:
				self._windows[hwnd] = window
				window.handleCreated()
				return True
		return False

	def handleWindowDestroyed(self, hwnd):
		window = self._windows.get(hwnd, None)
		if window is not None:
			window.handleDestroyed()
			del self._windows[hwnd]
			return True
		return False

	def handleWindowGainedForeground(self, hwnd):
		window = self._windows.get(hwnd, None)
		if window is not None:
			window.handleGainedForeground()
			return True
		return False

	def handleWindowLostForeground(self, hwnd):
		window = self._windows.get(hwnd, None)
		if window is not None:
			window.handleLostForeground()
			return True
		return False

	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		window = self._windows.get(hwnd, None)
		if window is not None:
			window.handleInputEvent(hotkey, inputEvent)
			return True
		return False


