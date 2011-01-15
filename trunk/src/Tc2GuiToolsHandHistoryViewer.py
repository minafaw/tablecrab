
import Tc2Config
import Tc2HandGrabberPokerStars
import Tc2GuiHandViewer
import Tc2GuiHelp
from Tc2Lib import Browser
from PyQt4 import QtCore, QtGui, QtWebKit
import codecs
#************************************************************************************
#
#************************************************************************************
class FrameTool(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/PHandHistoryViewer'
	SettingsKeyZoomFactor = SettingsKeyBase + '/ZoomFactor'
	SettingsKeyDialogOpenState = SettingsKeyBase + '/DialogOpen/State'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'
	SettingsKeyDialogSaveHandState = SettingsKeyBase + '/DialogSaveHand/State'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'
	SettingsKeySideBarCurrent = SettingsKeyBase + '/SideBarCurrent'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.handHistoryFile = None
		self.handParser = Tc2HandGrabberPokerStars.HandParser()
		self.handFormatter = Tc2HandGrabberPokerStars.HandFormatterHtmlTabular()

		self.frame = QtGui.QFrame(self)
		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self.splitter.addWidget(self.frame)

		self.spinBox = QtGui.QSpinBox(self.frame)
		self.spinBox.setPrefix('Hand# ')
		self.spinBox.setRange(0, 0)
		self.spinBox.setSuffix(' /0')

		self._browserFrame = Browser.RawBrowserFrame(self.frame)
		self._browser = self._browserFrame.browser()
		self._browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self._browser.customContextMenuRequested.connect(self.onContextMenuWebView)
		self._browser.networkAccessManager().getData.connect(self.onNetworkGetData)

		self._toolBar = self._browserFrame.toolBar()
		self._toolBar.actionZoomIn.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierPlus() ) )
		self._toolBar.actionZoomOut.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierMinus() ) )
		self._toolBar.zoomFactorChanged.connect(self.onToolBarZoomFactorChanged)

		self.sideBarContainer = Tc2GuiHandViewer.BrowserSideBarContainer(self)
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
		self.actionOpen.setToolTip('Open a hand history (Alt+O)')
		self.actionOpen.setShortcut(QtGui.QKeySequence('Alt+O') )
		self.actionOpen.triggered.connect(self.onActionOpenTriggered)
		self._toolBar.addAction(self.actionOpen)

		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save..')
		self.actionSave.setToolTip('Save hand history (Alt+S)')
		self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		self._toolBar.addAction(self.actionSave)

		self.actionSaveHand = QtGui.QAction(self)
		self.actionSaveHand.setText('Save hand..')
		self.actionSaveHand.setToolTip('Save hand (Alt+N)')
		self.actionSaveHand.setShortcut(QtGui.QKeySequence('Alt+N') )
		self.actionSaveHand.triggered.connect(self.onActionSaveHandTriggered)
		self._toolBar.addAction(self.actionSaveHand)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self._toolBar.addAction(self.actionHelp)

		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		self._browser.urlChanged.connect(self.onUrlChanged)

	def layout(self):
		grid = Tc2Config.GridBox(self.frame)
		grid.setContentsMargins(0, 0, 0, 0)
		grid.col(self.spinBox)
		grid.row()
		grid.col(self._browserFrame)
		self.sideBarContainer.layout()

		grid = Tc2Config.GridBox(self)
		grid.col(self.splitter)

	def toolBar(self):
		return self._toolBar

	def toolTip(self):
		return 'HandHistoryViewer'

	def toolName(self):
		return 'HandHistoryViewer'

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self._browser.setUrl(QtCore.QUrl(''))
		self.spinBox.valueChanged.connect(self.onSpinBoxValueChanged)
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		self.adjustActions()

		self._browserFrame.layout(globalObject.settingsGlobal.toolBarPosition() == Tc2Config.ToolBarPositionTop)
		self.layout()
		globalObject.settingsGlobal.toolBarPositionChanged.connect(
				lambda position, frame=self._browserFrame: frame.layout(toolBarTop=position == Tc2Config.ToolBarPositionTop)
				)

		value, ok = Tc2Config.settingsValue(self.SettingsKeyZoomFactor, Browser.BrowserToolBar.ZoomFactorDefault).toDouble()
		if ok:
			self._toolBar.setZoomFactor(value)
		value, ok = Tc2Config.settingsValue(self.SettingsKeySideBarCurrent, 0).toInt()
		if ok:
			self.sideBarContainer.setCurrentIndex(value)

	def adjustActions(self):
		self._toolBar.actionZoomIn.setEnabled(bool(self.handHistoryFile))
		self._toolBar.actionZoomOut.setEnabled(bool(self.handHistoryFile))
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
		Tc2Config.settingsSetValue(self.SettingsKeySideBarCurrent, self.sideBarContainer.currentIndex())

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
			fp.write( unicode(self._browser.page().mainFrame().toHtml().toUtf8(), 'utf-8')  )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Hand\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.actionCopy)
		menu.addAction(self.actionSelectAll)
		point = self._browser.mapToGlobal(point)
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
					self.sideBarContainer.handleHandSet(hand)
				networkReply.setData(data, 'text/html; charset=UTF-8')

	def onSpinBoxValueChanged(self, handNo):
		self._browser.setUrl(QtCore.QUrl('hand:///%s' % handNo))

	def onToolBarZoomFactorChanged(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyZoomFactor, value)

	def onUrlChanged(self, url):
		if url.scheme() == 'hand':
			handNo = int(url.path()[1:])
			if self.spinBox.value() != handNo:
				self.spinBox.setValue(handNo)





