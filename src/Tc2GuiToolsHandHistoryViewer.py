
import Tc2Config
import Tc2HandGrabberPokerStars
import Tc2GuiHandViewer
import Tc2GuiHelp
from PyQt4 import QtCore, QtGui, QtWebKit
import codecs
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

		self.frameNashCalculations = Tc2GuiHandViewer.FrameNashCalculations(self,
				toolBar=self.toolBar,
				requestDelay=Tc2Config.HoldemResourcesHandHistoryViewerRequestDelay * 1000,
				)
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
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		self.webView.urlChanged.connect(self.onUrlChanged)

	def layout(self, toolBarPosition):
		grid = self.grid
		grid.clear()
		if toolBarPosition == Tc2Config.ToolBarPositionTop:
			grid.col(self.toolBar)
			grid.row()
		grid.col(self.spinBox)
		grid.row()
		grid.col(self.splitter)
		if toolBarPosition == Tc2Config.ToolBarPositionBottom:
			grid.row()
			grid.col(self.toolBar)

	def toolTip(self):
		return 'HandHistoryViewer'

	def toolName(self):
		return 'HandHistoryViewer'

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout(globalObject.settingsGlobal.toolBarPosition())
		globalObject.settingsGlobal.toolBarPositionChanged.connect(self.layout)
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





