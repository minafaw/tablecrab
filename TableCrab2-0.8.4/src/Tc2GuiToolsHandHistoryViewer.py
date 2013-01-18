
import Tc2Config
import Tc2SitePokerStarsHandGrabber
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
		self.handParser = Tc2SitePokerStarsHandGrabber.HandParser()

		self._frame = QtGui.QFrame(self)
		self._splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
		self._splitter.addWidget(self._frame)

		self._spinBox = QtGui.QSpinBox(self._frame)
		self._spinBox.setPrefix('Hand# ')
		self._spinBox.setRange(0, 0)
		self._spinBox.setSuffix(' /0')

		self._browserFrame = Browser.RawBrowserFrame(self._frame)
		self._browser = self._browserFrame.browser()
		self._browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self._browser.customContextMenuRequested.connect(self.onContextMenuWebView)
		self._browser.networkAccessManager().getData.connect(self.onNetworkGetData)

		self._toolBar = self._browserFrame.toolBar()
		self._toolBar.actionZoomIn.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierPlus() ) )
		self._toolBar.actionZoomOut.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierMinus() ) )
		self._toolBar.zoomFactorChanged.connect(self.onToolBarZoomFactorChanged)

		self.sideBarContainer = Tc2GuiHandViewer.BrowserSideBarContainer(self)
		self._splitter.addWidget(self.sideBarContainer)

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
		grid = Tc2Config.GridBox(self._frame)
		grid.setContentsMargins(0, 0, 0, 0)
		grid.col(self._spinBox)
		grid.row()
		grid.col(self._browserFrame)
		self.sideBarContainer.layout()

		grid = Tc2Config.GridBox(self)
		grid.col(self._splitter)

	def toolBar(self):
		return self._toolBar

	def toolTip(self):
		return 'HandHistoryViewer'

	def displayName(self):
		return 'HandHistoryViewer'

	def handleSetCurrent(self):
		pass

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self._browser.setUrl(QtCore.QUrl(''))
		self._spinBox.valueChanged.connect(self.onSpinBoxValueChanged)

		self.setSideBarPosition(globalObject.settingsHandViewer.sideBarPosition())
		globalObject.settingsHandViewer.sideBarPositionChanged.connect(self.setSideBarPosition)
		self.adjustActions()
		self._browserFrame.layout(globalObject.settingsGlobal.toolBarPosition() == Tc2Config.ToolBarPositionTop)
		self.layout()
		self._splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )

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
		fileName = fileName.toUtf8()
		fileName = unicode(fileName, 'utf-8')
		try:
			self.handHistoryFile = Tc2SitePokerStarsHandGrabber.HandHistoryFile(fileName)
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Open Hand history\n\n%s' % d)

		if self.handHistoryFile:
			self._spinBox.setRange(1, len(self.handHistoryFile))
			self._spinBox.setSuffix(' /%s' % len(self.handHistoryFile))
			if self._spinBox.value() == 1:
				self.onSpinBoxValueChanged(1)
			else:
				self._spinBox.setValue(1)
		else:
			self._spinBox.setRange(0, 0)
			self._spinBox.setSuffix(' /0' )
			self._spinBox.setValue(0)

		self._browser.clearHistory()
		self.adjustActions()

	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self._splitter.saveState())
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
		fileName = unicode(fileName.toUtf8(), 'utf-8')
		fp = None
		try:
			fp = codecs.open(fileName, 'w', encoding='utf-8')
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could not open file\n%s' % d)
			return
		try:
			fp.write(self.handHistoryFile.raw())
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
					formatter = Tc2Config.handFormatter('HtmlTabular')
					data = formatter.dump(hand)
					self.sideBarContainer.handleHandSet(hand)
				networkReply.setData(data, 'text/html; charset=UTF-8')

	def onSpinBoxValueChanged(self, handNo):
		self._browser.setUrl(QtCore.QUrl('hand:///%s' % handNo))

	def onToolBarZoomFactorChanged(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyZoomFactor, value)
		self.sideBarContainer.handleZoomFactorChanged(value)

	def zoomFactor(self):
		return self._toolBar.zoomFactor()

	def onUrlChanged(self, url):
		if url.scheme() == 'hand':
			handNo = int(url.path()[1:])
			if self._spinBox.value() != handNo:
				self._spinBox.setValue(handNo)

	def setSideBarPosition(self, position):
		if position == Tc2Config.HandViewerSideBarPositionTop:
			self._splitter.setOrientation(QtCore.Qt.Vertical)
			if self._splitter.widget(0) == self._frame:
				self._splitter.insertWidget(1, self._frame)
		elif position == Tc2Config.HandViewerSideBarPositionBottom:
			self._splitter.setOrientation(QtCore.Qt.Vertical)
			if self._splitter.widget(1) == self._frame:
				self._splitter.insertWidget(0, self._frame)
		elif position == Tc2Config.HandViewerSideBarPositionLeft:
			self._splitter.setOrientation(QtCore.Qt.Horizontal)
			if self._splitter.widget(0) == self._frame:
				self._splitter.insertWidget(1, self._frame)
		elif position == Tc2Config.HandViewerSideBarPositionRight:
			self._splitter.setOrientation(QtCore.Qt.Horizontal)
			if self._splitter.widget(1) == self._frame:
				self._splitter.insertWidget(0, self._frame)





