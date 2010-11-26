
import Tc2Config
import Tc2HandGrabberPokerStars
import Tc2GuiHelp
from Tc2Lib import HoldemResources
from PyQt4 import QtCore, QtGui, QtWebKit
import codecs
#************************************************************************************
#
#************************************************************************************
class FrameNashCalculations(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/PHandHistoryViewer/NashCalculations'
	SettingsKeyCustomPayoutStructure = SettingsKeyBase + '/CustomPayoutStructure'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'

	PayoutStructures = (	# text, payoutStructure, lineEditMask
			('None', '', ''),
			('PokerStars 9 man sitNgo', '50/30/20', '99/99/99'),
			('PokerStars 6 man sitNgo', '65/35', '99/99'),
			('Winner takes all', '100', '999'),
			('Custom', '', '99/99/99/99/99/99/99/99/99/99')
			)

	def __init__(self, parent, toolBar=None):
		QtGui.QFrame.__init__(self, parent)

		self.lastHand = None
		self.settingsNetwork = None
		self.settingsNashCalculationsStyleSheet = None

		parent.handSet.connect(self.onHandSet)
		if toolBar is not None:
			toolBar.zoomFactorChanged.connect(self.onZoomFactorChanged)

		self.fetcher = HoldemResources.NashFetcher()
		self.fetcher.requestFailed.connect(self.onRequestFailed)
		self.fetcher.requestCompleted.connect(self.onRequestCompleted)

		self.formatter = HoldemResources.NashFormatter()

		self.webView = QtWebKit.QWebView(self)
		self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.webView.customContextMenuRequested.connect(self.onContextMenuWebView)
		settings = self.webView.page().settings()
		settings.setAttribute(settings.AutoLoadImages, False)
		settings.setAttribute(settings.JavascriptEnabled, False)
		settings.setAttribute(settings.JavaEnabled, False)

		self.label = QtGui.QLabel('Select payout to fetch nash calculations', self)
		self.comboBox = QtGui.QComboBox(self)
		for i, (text, _, _) in enumerate(self.PayoutStructures):
			self.comboBox.addItem(text, i)
		self.editPayoutStructure = QtGui.QLineEdit(self)
		self.editPayoutStructure.setEnabled(False)

		#setup actions
		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save..')
		#self.actionSave.setToolTip('Save hand history (Alt+S)')
		#self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		#self.toolBar.addAction(self.actionSave)

		# connect signals
		Tc2Config.globalObject.init.connect(self.onInit)
		Tc2Config.globalObject.objectCreatedSettingsNetwork.connect(self.onObjectCreatedSettingsNetwork)
		Tc2Config.globalObject.objectCreatedSettingsNashCalculationsStyleSheet.connect(self.onObjectCreatedSettingsNashCalculationsStyleSheet)

	def onRequestFailed(self, url, msg):
		self.webView.setHtml('<h3>Request failed: %s</h3>%s' % (msg, url.toString()))

	def onRequestCompleted(self, url, qString):

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
			self.webView.setHtml(unicode(details))
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
				styleSheet=self.settingsNashCalculationsStyleSheet.styleSheet(),
				url=url,
				)
		self.webView.setHtml(html)

	def payoutStructure(self):
		return [round( int(i) / 100.0, 2) for i in str(self.editPayoutStructure.text()).split('/') if i]

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.label, colspan=2)
		grid.row()
		grid.col(self.comboBox)
		grid.col(self.editPayoutStructure)
		iRow = grid.row()
		grid.setRowStretch(iRow, 99)
		grid.col(self.webView, colspan=2)

	def setHand(self, hand):
		self.lastHand = hand
		if hand is None:
			return
		payoutStructure = self.payoutStructure()
		if not payoutStructure:
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

		self.fetcher.abortRequest()
		#TODO: should we clear out webView here?
		url = self.fetcher.createRequestUrl(
				bigBlind=hand.blindBig,
				smallBlind=hand.blindSmall,
				ante=hand.blindAnte,
				payouts=payoutStructure,
				stacks=stacks,
				)
		self.fetcher.requestHandData(
				url,
				timeout=self.settingsNetwork.fetchTimeout() * 1000,
				proxyHostName=self.settingsNetwork.proxyHostName(),
				proxyPort=self.settingsNetwork.proxyPort(),
				proxyUserName=self.settingsNetwork.proxyUserName(),
				proxyPassword=self.settingsNetwork.proxyPassword(),
				)

	def onInit(self):
		self.layout()
		self.comboBox.currentIndexChanged.connect(self.onComboBoxCurrentIndexChanged)
		self.webView.setHtml('')

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
		self.setHand(self.lastHand)

	def onHandSet(self, hand):
		self.setHand(hand)

	def onZoomFactorChanged(self, factor):
		self.webView.setZoomFactor(factor)

	def onEditPayoutStructureTextChanged(self, text):
		if self.comboBox.currentIndex() == len(self.PayoutStructures) -1:
			edit = self.sender()
			Tc2Config.settingsSetValue(self.SettingsKeyCustomPayoutStructure, text)

	def onObjectCreatedSettingsNetwork(self, obj):
		self.settingsNetwork = obj

	def onObjectCreatedSettingsNashCalculationsStyleSheet(self, obj):
		self.settingsNashCalculationsStyleSheet = obj

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.webView.pageAction(QtWebKit.QWebPage.Copy))
		menu.addAction(self.webView.pageAction(QtWebKit.QWebPage.SelectAll))
		menu.addAction(self.actionSave)
		point = self.webView.mapToGlobal(point)
		menu.exec_(point)

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
			fp.write( unicode(self.webView.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Nash Calculations\n\n%s' % d)
		finally:
			if fp is not None: fp.close()
		#TODO: can we rename hand in cache? i font think so. no way to inform WebKit

#************************************************************************************
#
#************************************************************************************
class FrameTool(QtGui.QFrame):

	handSet = QtCore.pyqtSignal(QtCore.QObject)

	SettingsKeyBase = 'Gui/Tools/PHandHistoryViewer'
	SettingsKeyZoomFactor = SettingsKeyBase + '/ZoomFactor'
	SettingsKeyDialogOpenState = SettingsKeyBase + '/DialogOpen/State'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'
	SettingsKeyDialogSaveHandState = SettingsKeyBase + '/DialogSaveHand/State'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.handHistoryFile = None
		self.handParser = Tc2HandGrabberPokerStars.HandParser()
		self.handFormatter = Tc2HandGrabberPokerStars.HandFormatterHtmlTabular()

		self.grid = Tc2Config.GridBox(self)

		self.spinBox = QtGui.QSpinBox(self)
		self.spinBox.setPrefix('Hand# ')
		self.spinBox.setRange(0, 0)
		self.spinBox.setSuffix(' /0')


		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)

		self.webView = QtWebKit.QWebView(self)
		self.splitter.addWidget(self.webView)
		self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.webView.customContextMenuRequested.connect(self.onContextMenuWebView)

		oldManager = self.webView.page().networkAccessManager()
		self.networkAccessManager = Tc2Config.RawNetworkAccessManager(oldManager, parent=self)
		page = self.webView.page()
		page.setNetworkAccessManager(self.networkAccessManager)
		self.networkAccessManager.getData.connect(self.onNetworkGetData)

		self.toolBar = Tc2Config.WebViewToolBar(self.webView,
				settingsKeyZoomFactor=self.SettingsKeyZoomFactor
				)

		self.frameNashCalculations = FrameNashCalculations(self, toolBar=self.toolBar)
		self.splitter.addWidget(self.frameNashCalculations)

		# set up actions
		self.actionCopy = self.webView.pageAction(QtWebKit.QWebPage.Copy)
		self.actionCopy.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Copy))
		self.addAction(self.actionCopy)

		self.actionSelectAll = self.webView.pageAction(QtWebKit.QWebPage.SelectAll)
		self.actionSelectAll.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.SelectAll))
		self.addAction(self.actionSelectAll)

		self.actionOpen = QtGui.QAction(self)
		self.actionOpen.setText('Open..')
		self.actionOpen.setToolTip('Open a hand history (Alt+O)')
		self.actionOpen.setShortcut(QtGui.QKeySequence('Alt+O') )
		self.actionOpen.triggered.connect(self.onActionOpenTriggered)
		self.toolBar.addAction(self.actionOpen)

		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save..')
		self.actionSave.setToolTip('Save hand history (Alt+S)')
		self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		self.toolBar.addAction(self.actionSave)

		self.actionSaveHand = QtGui.QAction(self)
		self.actionSaveHand.setText('Save hand..')
		self.actionSaveHand.setToolTip('Save hand (Alt+N)')
		self.actionSaveHand.setShortcut(QtGui.QKeySequence('Alt+N') )
		self.actionSaveHand.triggered.connect(self.onActionSaveHandTriggered)
		self.toolBar.addAction(self.actionSaveHand)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self.toolBar.addAction(self.actionHelp)


		# connect signals
		Tc2Config.globalObject.init.connect(self.onInit)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		self.webView.urlChanged.connect(self.onUrlChanged)
		Tc2Config.globalObject.settingToolBarPositionChanged.connect(self.onSettingToolBarPositionChanged)

	def layout(self):
		toolBarPositionBottom = Tc2Config.settingsValue(Tc2Config.SettingsKeyToolBarPosition, Tc2Config.ToolBarPositionTop).toString() == Tc2Config.ToolBarPositionBottom
		grid = self.grid
		if not toolBarPositionBottom:
			grid.col(self.toolBar)
			grid.row()
		grid.col(self.spinBox)
		grid.row()
		grid.col(self.splitter)
		if toolBarPositionBottom:
			grid.row()
			grid.col(self.toolBar)

	def toolTip(self):
		return 'HandHistoryViewer'

	def toolName(self):
		return 'HandHistoryViewer'

	def onInit(self):
		self.layout()
		self.webView.setUrl(QtCore.QUrl(''))
		self.spinBox.valueChanged.connect(self.onSpinBoxValueChanged)
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		self.adjustActions()

	def adjustActions(self):
		self.toolBar.actionZoomIn.setEnabled(bool(self.handHistoryFile))
		self.toolBar.actionZoomOut.setEnabled(bool(self.handHistoryFile))
		self.actionSave.setEnabled(bool(self.handHistoryFile))
		self.actionSaveHand.setEnabled(bool(self.handHistoryFile))

	def onActionHelpTriggered(self, checked):
		Tc2GuiHelp.dialogHelp('toolsHandHistoryViewer', parent=self)

	def onActionOpenTriggered(self):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Hand..',
				fileFilters=('HandHistories (*.txt)', 'All Files (*)'),
				settingsKey=self.SettingsKeyDialogOpenState,
				)
		if fileName is None:
			return
		#TODO: make failsave
		try:
			self.handHistoryFile = Tc2HandGrabberPokerStars.HandHistoryFile(fileName)
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Open Hand history\n\n%s' % d)

		if self.handHistoryFile:
			self.spinBox.setRange(1, len(self.handHistoryFile))
			self.spinBox.setValue(1)
			self.spinBox.setSuffix(' /%s' % len(self.handHistoryFile))
		else:
			self.spinBox.setRange(0, 0)
			self.spinBox.setSuffix(' /0' )
		self.adjustActions()

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState())

	def onActionSaveTriggered(self):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Hand history..',
				fileFilters=('HandHistories (*.txt)', 'All Files (*)'),
				#TODO: rename to Gui/HandViewer/DialogSave/State
				settingsKey=self.SettingsKeyDialogSaveState,
				defaultSuffix='txt',
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = codecs.open(fileName, 'w', encoding='utf-8')
			fp.write(self.handHistoryFile.raw())
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Hand history\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onActionSaveHandTriggered(self):
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
			fp.write( unicode(self.webView.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Hand\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.actionCopy)
		menu.addAction(self.actionSelectAll)
		point = self.webView.mapToGlobal(point)
		menu.exec_(point)

	def onNetworkGetData(self, networkReply):
		url = networkReply.url()
		if url.scheme() == 'hand':
			handNo = int(url.path()[1:])
			if handNo > 0:
				data = self.handHistoryFile[handNo -1]
				try:
					hand = self.handParser.parse(data)
				except:
					Tc2Config.handleException('\n' + data)
					#TODO: data = ?
				else:
					data = self.handFormatter.dump(hand)
					self.handSet.emit(hand)
				networkReply.setData(data, 'text/html; charset=UTF-8')


	def onSpinBoxValueChanged(self, handNo):
		self.webView.setUrl(QtCore.QUrl('hand:///%s' % handNo))

	def onUrlChanged(self, url):
		if url.scheme() == 'hand':
			handNo = int(url.path()[1:])
			if self.spinBox.value() != handNo:
				self.spinBox.setValue(handNo)

	def onSettingToolBarPositionChanged(self, position):
		self.grid.clear()
		self.layout()





