
import Tc2Config
import Tc2SitePokerStarsHandGrabber
import Tc2GuiHelp
from Tc2Lib import Browser
from Tc2Lib import HoldemResources

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
		fp = None
		try:
			fp = codecs.open(fileName, 'w', encoding='utf-8')
			fp.write( unicode(self._browser.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Nash Calculations\n\n%s' % d)
		finally:
			if fp is not None: fp.close()
		#TODO: can we rename hand in cache? i font think so. no way to inform WebKit

#************************************************************************************
#
#************************************************************************************
class BrowserSideBarContainer(QtGui.QFrame):
	SideBarsDefault = (
			BrowserSideBarNashCalculations,
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

		self._handCache = []

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
			myUrl  = QtCore.QUrl('cache:///' + m.hexdigest() )
		elif data and fileName is not None:
			myUrl = QtCore.QUrl('file:///' + fileName)
		else:
			myUrl = QtCore.QUrl('')
		# update our hand cache
		#TODO: check how WebKit caches urls and/or data. we have to make shure
		# our cache is <= WebKits cache
		if data:
			for i, (tmp_url, tmp_data) in enumerate(self._handCache):
				if tmp_url == myUrl:
					self._handCache[i] = (myUrl, data)
					break
			else:
				self._handCache.append( (myUrl, data) )
			if len(self._handCache) > self._browser.page().history().maximumItemCount():
				self._handCache.pop(0)
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
		fp = codecs.open(fileName, 'r', encoding='utf-8')
		raw = fp.read()
		try:
			data = QtCore.QString(raw).toUtf8()
		finally:
			fp.close()
		self.setHand(data, fileName=fileName)
		#TODO: either have to get Null hand object from a better place
		# or not set it to sidebarContainer
		hand = Tc2SitePokerStarsHandGrabber.Hand()
		for siteHandler in Tc2Config.globalObject.siteManager:
			hand = siteHandler.handFromHtml(raw)
			if hand is not None:
				break
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
		fp = None
		try:
			fp = codecs.open(fileName, 'w', encoding='utf-8')
			fp.write( unicode(self._browser.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Hand\n\n%s' % d)
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
		value, ok = Tc2Config.settingsValue(self.SettingsKeyZoomFactor, Browser.BrowserToolBar.ZoomFactorDefault).toDouble()
		if ok:
			self._toolBar.setZoomFactor(value)
		value, ok = Tc2Config.settingsValue(self.SettingsKeySideBarCurrent, 0).toInt()
		if ok:
			self.sideBarContainer.setCurrentIndex(value)

	def onNetworkGetData(self, networkReply):
		url = networkReply.url()
		for myUrl, data in self._handCache:
			if myUrl == url:
				networkReply.setData(data,  'text/html; charset=utf-8')
				# give feedback
				if url.scheme() == 'file':
					fileName = url.path()[1:]
					fileInfo = QtCore.QFileInfo(fileName)
					handName = fileInfo.baseName()
					handName = Tc2Config.truncateString(handName, Tc2Config.MaxName)
					Tc2Config.globalObject.feedback.emit(self, handName)
				else:
					Tc2Config.globalObject.feedback.emit(self, 'Grabbed hand')
				break
		else:
			#NOTE: we assert only an invalid or no-hand gets here
			pass

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





