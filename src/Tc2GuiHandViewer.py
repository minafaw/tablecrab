
import Tc2Config
import Tc2SitePokerStarsHandGrabber
import Tc2GuiHelp
from Tc2Lib import Browser
from Tc2Lib import HoldemResources
from Tc2Lib import PokerTools
from Tc2Lib import ICM

from PyQt4 import QtCore, QtGui, QtWebKit
import hashlib, codecs
#************************************************************************************
#
#************************************************************************************
class BrowserSideBarNashCalculations(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/NashCalculations'
	SettingsKeyCustomPayoutStructure = SettingsKeyBase + '/CustomPayoutStructure'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'

	PayoutStructures = (	# text, payoutStructure, lineEditMask
			('- Select payout structure -', '', ''),
			('PokerStars 9 man sitNgo', '50/30/20', '99/99/99'),
			('PokerStars 6 man sitNgo', '65/35', '99/99'),
			('Winner takes all', '100', '999'),
			('Custom', '', '99/99/99/99/99/99/99/99/99/99')
			)


	class RequestDelayTimer(QtCore.QTimer):
		def __init__(self, parent, requestFetcher, url):
			QtCore.QTimer.__init__(self, parent)
			self.setSingleShot(True)
			self.setInterval(Tc2Config.HoldemResourcesHandHistoryViewerRequestDelay * 1000)
			self.url = url
			self.requestFetcher = requestFetcher
			self.timeout.connect(self.onTimeout)
		def onTimeout(self):
			self.requestFetcher(self.url)

	def __init__(self, parent, zoomFactor=None):
		QtGui.QFrame.__init__(self, parent)

		self.lastHand = None
		self.lastUrl = None

		self.fetcher = HoldemResources.NashFetcher()
		self.fetcher.requestFailed.connect(self.onRequestFailed)
		self.fetcher.requestCompleted.connect(self.onRequestCompleted)

		self.formatter = HoldemResources.NashFormatter()

		self._browser = QtWebKit.QWebView(self)
		self._browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self._browser.customContextMenuRequested.connect(self.onContextMenuWebView)
		settings = self._browser.page().settings()
		settings.setAttribute(settings.AutoLoadImages, False)
		settings.setAttribute(settings.JavascriptEnabled, False)
		settings.setAttribute(settings.JavaEnabled, False)
		if zoomFactor is not None:
			self._browser.setZoomFactor(zoomFactor)

		self.comboBox = QtGui.QComboBox(self)
		for i, (text, _, _) in enumerate(self.PayoutStructures):
			self.comboBox.addItem(text, i)
		self.editPayoutStructure = QtGui.QLineEdit(self)
		self.editPayoutStructure.setEnabled(False)

		#setup actions
		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save..')
		self.actionSave.setEnabled(False)
		#self.actionSave.setToolTip('Save hand history (Alt+S)')
		#self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		#self._toolBar.addAction(self.actionSave)

		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)

	#-----------------------------------------------------------------------------------------
	# sideBar methods
	#-----------------------------------------------------------------------------------------
	def displayName(self):
		return 'Fetch nash calculations'

	def handleZoomFactorChanged(self, value):
		self._browser.setZoomFactor(value)

	def handleHandSet(self, hand):
		if hand.gameType & hand.GameTypeHoldem:
			self.setEnabled(True)
		else:
			self.setEnabled(False)
			self._browser.setHtml('<h4>Unsupported game type</h4>')
			return

		if hand is self.lastHand:
			return
		self.lastHand = hand
		if hand is None:
			return
		payoutStructure = self.payoutStructure()
		if not payoutStructure:
			return
		if not hand:
			self._browser.setHtml('<h4>Can not fetch data for the hand</h4>')
			return

		# prep seats/stacks
		seats = hand.seatsButtonOrdered()
		if len(seats) == 1:
			return
		elif len(seats) > 3:
			seats.append(seats.pop(0))
			seats.append(seats.pop(0))
			seats.append(seats.pop(0))
		stacks = [seat.stack for seat in seats]

		#TODO: should we clear out webView here?
		url = self.fetcher.createRequestUrl(
				bigBlind=hand.blindBig,
				smallBlind=hand.blindSmall,
				ante=hand.blindAnte,
				payouts=payoutStructure,
				stacks=stacks,
				)
		self.lastUrl = url
		self.fetcher.abortRequest()
		timer = self.RequestDelayTimer(self, self.fetchHandData, url)
		timer.start()

	#-----------------------------------------------------------------------------------------
	#
	#-----------------------------------------------------------------------------------------
	def onRequestFailed(self, url, msg):
		if url != self.lastUrl:
			return
		self._browser.setHtml('<h3>Request failed: %s</h3>%s' % (msg, url.toString()))

	def onRequestCompleted(self, url, qString):
		if url != self.lastUrl:
			return

	# prep seats/stacks
		seats = self.lastHand.seatsButtonOrdered()
		if len(seats) == 1:
			return
		elif len(seats) > 3:
			seats.append(seats.pop(0))
			seats.append(seats.pop(0))
			seats.append(seats.pop(0))

		try:
			self.formatter.parse(qString, len(seats))
		except HoldemResources.ParseError, details:
			self._browser.setHtml(unicode(details))
			return

		def sortf(seats, mySeats=self.lastHand.seats, mySeatsButtonOrder=seats):
			mySeats = [i for i in mySeats if i is not None]
			result = [None]* len(mySeatsButtonOrder)
			for i, seat in enumerate(seats):
				mySeat = mySeatsButtonOrder[i]
				myIndex = mySeats.index(mySeat)
				result[myIndex] = seat
			return result
		#TODO: from time to time we get strange errors here. had seats num seats as
		# returned did not match our seats so seat list could contain a None seat.
		#maybe data as returned from HoldemResources is corrupted?
		html = self.formatter.toHtml(
				seatSortf=sortf,
				styleSheet=Tc2Config.globalObject.settingsNashCalculationsStyleSheet.styleSheet(),
				url=url,
				)
		self._browser.setHtml(html)
		self.actionSave.setEnabled(True)

	def payoutStructure(self):
		return [round( int(i) / 100.0, 2) for i in str(self.editPayoutStructure.text()).split('/') if i]

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.comboBox)
		grid.col(self.editPayoutStructure)
		iRow = grid.row()
		grid.setRowStretch(iRow, 99)
		grid.col(self._browser, colspan=2)

	def fetchHandData(self, url):
			if url != self.lastUrl:
				return

			self.fetcher.requestHandData(
				url,
				timeout=Tc2Config.globalObject.settingsNetwork.fetchTimeout() * 1000,
				proxyHostName=Tc2Config.globalObject.settingsNetwork.proxyHostName(),
				proxyPort=Tc2Config.globalObject.settingsNetwork.proxyPort(),
				proxyUserName=Tc2Config.globalObject.settingsNetwork.proxyUserName(),
				proxyPassword=Tc2Config.globalObject.settingsNetwork.proxyPassword(),
				userAgent=Tc2Config.ReleaseName,
				)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		self.comboBox.currentIndexChanged.connect(self.onComboBoxCurrentIndexChanged)
		self._browser.setHtml('')

		#NOTE: editingFinished() is only emitted when the whole mask is filled in so we need to connect to textChanged()
		self.editPayoutStructure.textChanged.connect(self.onEditPayoutStructureTextChanged)

	def onComboBoxCurrentIndexChanged(self, i):
		payoutStructure, mask = self.PayoutStructures[i][1], self.PayoutStructures[i][2]
		if i == len(self.PayoutStructures) -1:
			payoutStructure = Tc2Config.settingsValue(self.SettingsKeyCustomPayoutStructure, '').toString()
		self.editPayoutStructure.setInputMask(mask)
		self.editPayoutStructure.setText(payoutStructure)
		self.editPayoutStructure.setEnabled(bool(mask))

		self.editPayoutStructure.home(False)
		hand, self.lastHand = self.lastHand, None
		self.handleHandSet(hand)

	def onZoomFactorChanged(self, factor):
		self._browser.setZoomFactor(factor)

	def onEditPayoutStructureTextChanged(self, text):
		if self.comboBox.currentIndex() == len(self.PayoutStructures) -1:
			edit = self.sender()
			Tc2Config.settingsSetValue(self.SettingsKeyCustomPayoutStructure, text)

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self._browser.pageAction(QtWebKit.QWebPage.Copy))
		menu.addAction(self._browser.pageAction(QtWebKit.QWebPage.SelectAll))
		menu.addAction(self.actionSave)
		point = self._browser.mapToGlobal(point)
		menu.exec_(point)

	def onActionSaveTriggered(self):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Nash Calculations..',
				fileFilters=('HtmlFiles (*.html *.htm)', 'All Files (*)'),
				#TODO: rename to Gui/HandViewer/DialogSave/State
				settingsKey=self.SettingsKeyDialogSaveState,
				defaultSuffix='html',
				)
		if fileName is None:
			return
		fileName = unicode(fileName.toUtf8(), 'utf-8')
		fp = None
		try:
			fp = codecs.open(fileName, 'w', encoding='utf-8')
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Nash Calculations\n\n%s' % d)
		try:
			fp.write( unicode(self._browser.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		finally:
			if fp is not None: fp.close()
		#TODO: can we rename hand in cache? i font think so. no way to inform WebKit

#************************************************************************************
#
#************************************************************************************
class BrowserSideBarICMTax(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/ICMTax'
	SettingsKeyCustomPayoutStructure = SettingsKeyBase + '/CustomPayoutStructure'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'
	SettingsKeyPayoutStructureCurrent = SettingsKeyBase + '/PayoutStructureCurrent'

	PayoutStructures = (	# text, payoutStructure, lineEditMask
			('- Select payout structure -', '', ''),
			('PokerStars 9 man sitNgo', '50/30/20', '99/99/99'),
			('PokerStars 6 man sitNgo', '65/35', '99/99'),
			('Winner takes all', '100', '999'),
			('Custom', '', '99/99/99/99/99/99/99/99/99/99')
			)

	StyleSheet = '''body{}
table{}
td{text-align: center;vertical-align: text-top;}
.title{font-weight: bold;}
.roleHero{font-weight: bold;background-color:#F0F0F0;}
.taxHero{}
.roleVillain{}
.taxVillain{}
'''


	def __init__(self, parent, zoomFactor=None):
		QtGui.QFrame.__init__(self, parent)

		self.lastHand = None

		self._browser = QtWebKit.QWebView(self)
		self._browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self._browser.customContextMenuRequested.connect(self.onContextMenuWebView)
		if zoomFactor is not None:
			self._browser.setZoomFactor(zoomFactor)

		self.comboBox = QtGui.QComboBox(self)
		for i, (text, _, _) in enumerate(self.PayoutStructures):
			self.comboBox.addItem(text, i)
		self.editPayoutStructure = QtGui.QLineEdit(self)
		self.editPayoutStructure.setEnabled(False)

		#setup actions
		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save..')
		self.actionSave.setEnabled(False)
		#self.actionSave.setToolTip('Save hand history (Alt+S)')
		#self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		#self._toolBar.addAction(self.actionSave)

		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)

	#-----------------------------------------------------------------------------------------
	# sideBar methods
	#-----------------------------------------------------------------------------------------
	def displayName(self):
		return 'ICM-tax'

	def handleZoomFactorChanged(self, value):
		self._browser.setZoomFactor(value)

	def handleHandSet(self, hand):

		if hand is self.lastHand:
			return
		self.lastHand = hand
		if hand is None:
			return
		payoutStructure = self.payoutStructure()
		if not payoutStructure:
			return
		if not hand:
			self._browser.setHtml('<h3>Can not fetch data for the hand</h3>')
			return

		# prep seats/stacks
		seats = [i for i in hand.seats if i is not None]
		if len(seats) == 1:
			return
		seatsButtonOrdered = hand.seatsButtonOrdered()
		stacks = [seat.stack for seat in seats]

		html = '<html><head>'
		html += '<style type="text/css"><!-- %s --></style>' % Tc2Config.globalObject.settingsICMTaxStyleSheet.styleSheet()
		html += '</head><body>'


		html += '<table border="1" cellspacing="0" cellpadding="0" width="100%">'

		bubbleFactors = ICM.bubbleFactors(stacks, self.payoutStructure())
		for iHero, villains in enumerate(bubbleFactors):
			seat = seats[iHero]
			role = PokerTools.Seats.seatName(len(seats), seatsButtonOrdered.index(seat))

			title = '&nbsp;'
			if iHero == 0:
				title = 'ICM-tax hero--&gt;villain (in %)'
			html += '<th class="title" colspan="99">%s</th>' % title

			tr1 = '<tr><td class="roleHero">%s</td>' % role
			tr2 = '<tr><td class="taxHero"></td>'

			# sort villains
			myVillains = []
			iHero = 0
			for iVillain, bubbleFactor in enumerate(villains):
				if bubbleFactor is None:
					iHero = iVillain
					myVillains.append(None)
				else:
					seat = seats[iVillain]
					role = PokerTools.Seats.seatName(len(seats), seatsButtonOrdered.index(seat))
					myVillains.append((role, bubbleFactor, iVillain))
			myVillains = myVillains[iHero+1:] + myVillains[:iHero]

			for role, bubbleFactor, iVillain in myVillains:
				taxHero = ICM.taxFactor(bubbleFactor)
				taxHero = int(round(taxHero*100, 0))
				bubbleFactor = bubbleFactors[iVillain][iHero]
				taxVillain = ICM.taxFactor(bubbleFactor)
				taxVillain = int(round(taxVillain*100, 0))
				tr1 += '<td class="roleVillain">%s</td>' % role
				tr2 += '<td class="taxVillain">%s/%s</td>' % (taxHero, taxVillain)

			tr1 += '</tr>'
			tr2 += '</tr>'
			html += tr1
			html += tr2

		html += '</table>'
		html += '</table></body></html>'
		self._browser.setHtml(html)
		self.actionSave.setEnabled(True)

	def payoutStructure(self):
		return [round( int(i) / 100.0, 2) for i in str(self.editPayoutStructure.text()).split('/') if i]

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.comboBox)
		grid.col(self.editPayoutStructure)
		iRow = grid.row()
		grid.setRowStretch(iRow, 99)
		grid.col(self._browser, colspan=2)

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeyPayoutStructureCurrent, self.comboBox.currentIndex())

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		self.comboBox.currentIndexChanged.connect(self.onComboBoxCurrentIndexChanged)
		self._browser.setHtml('')

		#NOTE: editingFinished() is only emitted when the whole mask is filled in so we need to connect to textChanged()
		self.editPayoutStructure.textChanged.connect(self.onEditPayoutStructureTextChanged)
		value, ok = Tc2Config.settingsValue(self.SettingsKeyPayoutStructureCurrent, 0).toInt()
		if ok:
			self.comboBox.setCurrentIndex(value)

	def onComboBoxCurrentIndexChanged(self, i):
		payoutStructure, mask = self.PayoutStructures[i][1], self.PayoutStructures[i][2]
		if i == len(self.PayoutStructures) -1:
			payoutStructure = Tc2Config.settingsValue(self.SettingsKeyCustomPayoutStructure, '').toString()
		self.editPayoutStructure.setInputMask(mask)
		self.editPayoutStructure.setText(payoutStructure)
		self.editPayoutStructure.setEnabled(bool(mask))

		self.editPayoutStructure.home(False)
		hand, self.lastHand = self.lastHand, None
		self.handleHandSet(hand)

	def onZoomFactorChanged(self, factor):
		self._browser.setZoomFactor(factor)

	def onEditPayoutStructureTextChanged(self, text):
		if self.comboBox.currentIndex() == len(self.PayoutStructures) -1:
			edit = self.sender()
			Tc2Config.settingsSetValue(self.SettingsKeyCustomPayoutStructure, text)

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self._browser.pageAction(QtWebKit.QWebPage.Copy))
		menu.addAction(self._browser.pageAction(QtWebKit.QWebPage.SelectAll))
		menu.addAction(self.actionSave)
		point = self._browser.mapToGlobal(point)
		menu.exec_(point)

	def onActionSaveTriggered(self):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save ICM-tax..',
				fileFilters=('HtmlFiles (*.html *.htm)', 'All Files (*)'),
				#TODO: rename to Gui/HandViewer/DialogSave/State
				settingsKey=self.SettingsKeyDialogSaveState,
				defaultSuffix='html',
				)
		if fileName is None:
			return
		fileName = unicode(fileName.toUtf8(), 'utf-8')
		fp = None
		try:
			fp = codecs.open(fileName, 'w', encoding='utf-8')
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save ICM tax calculations\n\n%s' % d)
		try:
			fp.write( unicode(self._browser.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		finally:
			if fp is not None: fp.close()
		#TODO: can we rename hand in cache? i font think so. no way to inform WebKit



#************************************************************************************
#
#************************************************************************************
class BrowserSideBarContainer(QtGui.QFrame):
	SideBarsDefault = (
			BrowserSideBarNashCalculations,
			BrowserSideBarICMTax,
			)

	def __init__(self, parent):
		QtGui.QFrame.__init__(self, parent)

		self.lastHand = None
		self.combo = QtGui.QComboBox(self)
		self.stack = QtGui.QStackedWidget(self)
		for sideBarClass in self.SideBarsDefault:
			self.addSideBar(sideBarClass)
		self.combo.currentIndexChanged.connect(self.onComboCurrentIndexChanged)

	def onComboCurrentIndexChanged(self, i):
		self.stack.setCurrentIndex(i)
		sideBar= self.stack.currentWidget()
		sideBar.handleHandSet(self.lastHand)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.setContentsMargins(0, 0, 0, 0)
		grid.setSpacing(0)
		grid.col(self.combo)
		grid.row()
		grid.col(self.stack)

	def handleHandSet(self, hand):
		self.lastHand = hand
		sideBar = self.stack.currentWidget()
		sideBar.handleHandSet(hand)

	def handleZoomFactorChanged(self, value):
		for i in xrange(self.stack.count()):
			sideBar = self.stack.widget(i)
			sideBar.handleZoomFactorChanged(value)

	def addSideBar(self, sideBarClass):
		sideBar = sideBarClass(self, zoomFactor=self.parent().zoomFactor() )
		self.stack.addWidget(sideBar)
		self.combo.addItem(sideBar.displayName(), QtCore.QVariant(self.stack.count() -1 ) )

	def currentIndex(self):
		return self.stack.currentIndex()

	def setCurrentIndex(self, i):
		if i > -1 and i < self.stack.count():
			self.combo.setCurrentIndex(i)
			return True
		return False

#*******************************************************************************************
#
#*******************************************************************************************
class FrameHandViewer(QtGui.QFrame):

	#TODO: rename to Gui/HandViewer/ZoomFactor
	SettingsKeyBase = 'Gui/Hand'
	SettingsKeyZoomFactor = SettingsKeyBase + '/ZoomFactor'
	SettingsKeyDialogOpenState = SettingsKeyBase + '/DialogOpen/State'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'
	SettingsKeySideBarCurrent = SettingsKeyBase + '/SideBarCurrent'


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self._handCache = {}

		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)

		#NOTE: we use a custom network manager to handle hands grabbed AND loaded from disk
		# default cache size of WebKit is 100 (self._browser.page().history().maximumItemCount() )
		# ok or not?
		self._browserFrame = Browser.RawBrowserFrame(self)
		self._browser = self._browserFrame.browser()
		self.splitter.addWidget(self._browserFrame)
		self._browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self._browser.customContextMenuRequested.connect(self.onContextMenuWebView)
		self._browser.networkAccessManager().getData.connect(self.onNetworkGetData)

		self._toolBar = self._browserFrame.toolBar()
		self._toolBar.actionZoomIn.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierPlus() ) )
		self._toolBar.actionZoomOut.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierMinus() ) )
		self._toolBar.zoomFactorChanged.connect(self.onToolBarZoomFactorChanged)

		self.sideBarContainer = BrowserSideBarContainer(self)
		self.splitter.addWidget(self.sideBarContainer)

		# set up actions
		self.actionCopy = self._browser.pageAction(QtWebKit.QWebPage.Copy)
		self.actionCopy.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Copy))
		self.addAction(self.actionCopy)

		self.actionSelectAll = self._browser.pageAction(QtWebKit.QWebPage.SelectAll)
		self.actionSelectAll.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.SelectAll))
		self.addAction(self.actionSelectAll)

		self.actionOpen = QtGui.QAction(self)
		self.actionOpen.setText('Open..')
		self.actionOpen.setToolTip('Open a hand (Alt+O)')
		self.actionOpen.setShortcut(QtGui.QKeySequence('Alt+O') )
		self.actionOpen.triggered.connect(self.onActionOpenTriggered)
		self._toolBar.addAction(self.actionOpen)

		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save..')
		self.actionSave.setToolTip('Save hand (Alt+S)')
		self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		self._toolBar.addAction(self.actionSave)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self._toolBar.addAction(self.actionHelp)

		# connect global signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def toolBar(self):
		return self._toolBar

	def adjustActions(self):
		self._toolBar.actionZoomIn.setEnabled(bool(self._handCache))
		self._toolBar.actionZoomOut.setEnabled(bool(self._handCache))
		self.actionSave.setEnabled(bool(self._handCache))

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.splitter)
		self.sideBarContainer.layout()

	def setHand(self, data, fileName=None):
		if data and fileName is None:
			m = hashlib.sha256()
			m.update(data)
			#NOTE: have to use single slash here. no idea why but tripple slash gets
			# truncated to single slash in NetworkReply. file:/// urls work as expected
			# (PyQt: 4.8.3)
			myUrl  = QtCore.QUrl('cache:/' + m.hexdigest() )
		elif data and fileName is not None:
			myUrl = QtCore.QUrl('file:///' + fileName)
		else:
			myUrl = QtCore.QUrl('')

		# update cache
		if data:
			cachedUrls = [item.url().toString() for item in self._browser.page().history().items()]
			for cachedUrl in self._handCache.keys():
				if cachedUrl not in cachedUrls:
					del self._handCache[cachedUrl]
			self._handCache[myUrl.toString()] = data

		self._browser.setUrl(myUrl)
		self.adjustActions()

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self, checked):
		Tc2GuiHelp.dialogHelp('handViewer', parent=self)

	def onActionOpenTriggered(self):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Hand..',
				fileFilters=('HtmlFiles (*.html *.htm)', 'All Files (*)'),
				#TODO: rename to Gui/HandViewer/DialogOpen/State
				settingsKey=self.SettingsKeyDialogOpenState,
				)
		if fileName is None:
			return
		#TODO: maybe limit max size of file before we read unconditionally
		fileName = fileName.toUtf8()
		fileName = unicode(fileName, 'utf-8')
		fp = codecs.open(fileName, 'r', encoding='utf-8')
		try:
			raw = fp.read()
		except UnicodeDecodeError:
			self._browser.setHtml('<h3>Could not open hand: invalid</h3>')
			return
		try:
			data = QtCore.QString(raw).toUtf8()
		finally:
			fp.close()
		hand = None
		for siteHandler in Tc2Config.globalObject.siteManager:
			hand = siteHandler.handFromHtml(raw)
			if hand:
				break
		if hand is None:
			pass
		elif not hand:
			self._browser.setHtml('<h3>Could not open hand: invalid</h3>')
		else:
			self.setHand(data, fileName=fileName)
			self.sideBarContainer.handleHandSet(hand)

	def onActionSaveTriggered(self):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Hand..',
				fileFilters=('HtmlFiles (*.html *.htm)', 'All Files (*)'),
				#TODO: rename to Gui/HandViewer/DialogSave/State
				settingsKey=self.SettingsKeyDialogSaveState,
				defaultSuffix='html',
				)
		if fileName is None:
			return
		fileName = unicode(fileName.toUtf8(), 'utf-8')
		fp = None
		try:
			fp = codecs.open(fileName, 'w', encoding='utf-8')
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Hand\n\n%s' % d)
		try:
			fp.write( unicode(self._browser.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		finally:
			if fp is not None: fp.close()
		#TODO: can we rename hand in cache? i font think so. no way to inform WebKit

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState())
		Tc2Config.settingsSetValue(self.SettingsKeySideBarCurrent, self.sideBarContainer.currentIndex())


	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.actionCopy)
		menu.addAction(self.actionSelectAll)
		point = self._browser.mapToGlobal(point)
		menu.exec_(point)

	def onHandGrabberGrabbedHand(self, hand, data):
		if data:
			self.setHand(data)
			self.sideBarContainer.handleHandSet(hand)
		else:
			Tc2Config.globalObject.feedbackMessage.emit('Could not grab hand')

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self._browser.setUrl(QtCore.QUrl(''))
		self.adjustActions()

		self.setSideBarPosition(globalObject.settingsHandViewer.sideBarPosition())
		globalObject.settingsHandViewer.sideBarPositionChanged.connect(self.setSideBarPosition)
		globalObject.siteHandlerPokerStars.handGrabbed.connect(self.onHandGrabberGrabbedHand)
		self._browserFrame.layout(globalObject.settingsGlobal.toolBarPosition() == Tc2Config.ToolBarPositionTop)
		self.layout()
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )

		globalObject.settingsGlobal.toolBarPositionChanged.connect(
				lambda position, frame=self._browserFrame: frame.layout(toolBarTop=position == Tc2Config.ToolBarPositionTop)
				)
		self._toolBar.setZoomSteps(globalObject.settingsGlobal.webViewZoomSteps())
		globalObject.settingsGlobal.webViewZoomStepsChanged.connect(self._toolBar.setZoomSteps)
		value, ok = Tc2Config.settingsValue(self.SettingsKeyZoomFactor, Browser.BrowserToolBar.ZoomFactorDefault).toDouble()
		if ok:
			self._toolBar.setZoomFactor(value)
		value, ok = Tc2Config.settingsValue(self.SettingsKeySideBarCurrent, 0).toInt()
		if ok:
			self.sideBarContainer.setCurrentIndex(value)

	def onNetworkGetData(self, networkReply):
		url = networkReply.url()
		data = self._handCache.get(url.toString(), None)
		if data is None:
			return
		networkReply.setData(data,  'text/html; charset=utf-8;')
		# give feedback
		if url.scheme() == 'file':
			fileName = url.path()[1:]
			fileInfo = QtCore.QFileInfo(fileName)
			handName = fileInfo.baseName()
			handName = Tc2Config.truncateString(handName, Tc2Config.MaxName)
			Tc2Config.globalObject.feedback.emit(self, handName)
		else:
			Tc2Config.globalObject.feedback.emit(self, 'Grabbed hand')

	def onToolBarZoomFactorChanged(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyZoomFactor, value)
		self.sideBarContainer.handleZoomFactorChanged(value)

	def zoomFactor(self):
		return self._toolBar.zoomFactor()

	def setSideBarPosition(self, position):
		if position == Tc2Config.HandViewerSideBarPositionTop:
			self.splitter.setOrientation(QtCore.Qt.Vertical)
			if self.splitter.widget(0) == self._browserFrame:
				self.splitter.insertWidget(1, self._browserFrame)
		elif position == Tc2Config.HandViewerSideBarPositionBottom:
			self.splitter.setOrientation(QtCore.Qt.Vertical)
			if self.splitter.widget(1) == self._browserFrame:
				self.splitter.insertWidget(0, self._browserFrame)
		elif position == Tc2Config.HandViewerSideBarPositionLeft:
			self.splitter.setOrientation(QtCore.Qt.Horizontal)
			if self.splitter.widget(0) == self._browserFrame:
				self.splitter.insertWidget(1, self._browserFrame)
		elif position == Tc2Config.HandViewerSideBarPositionRight:
			self.splitter.setOrientation(QtCore.Qt.Horizontal)
			if self.splitter.widget(1) == self._browserFrame:
				self.splitter.insertWidget(0, self._browserFrame)





