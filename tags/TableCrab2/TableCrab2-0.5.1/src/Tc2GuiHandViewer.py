
import Tc2Config
import Tc2HandGrabberPokerStars
import Tc2GuiHelp

from PyQt4 import QtCore, QtGui, QtWebKit
import hashlib

#*******************************************************************************************
#
#*******************************************************************************************
class FrameHandViewer(QtGui.QFrame):
	#TODO: rename to Gui/HandViewer/ZoomFactor
	SettingsKeyBase = 'Gui/Hand'
	SettingsKeyZoomFactor = SettingsKeyBase + '/ZoomFactor'
	SettingsKeyDialogOpenState = SettingsKeyBase + '/DialogOpen/State'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self._handCache = []

		self.grid = Tc2Config.GridBox(self)

		self.webView = QtWebKit.QWebView(self)
		self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.webView.customContextMenuRequested.connect(self.onContextMenuWebView)

		#NOTE: we use a custom network manager to handle hands grabbed AND loaded from disk
		# default cache size of WebKit is 100 (self.webView.page().history().maximumItemCount() )
		# ok or not?
		oldManager = self.webView.page().networkAccessManager()
		self.networkAccessManager = Tc2Config.RawNetworkAccessManager(oldManager, parent=self)
		page = self.webView.page()
		page.setNetworkAccessManager(self.networkAccessManager)
		self.networkAccessManager.getData.connect(self.onNetworkGetData)

		self.Tc2HandGrabberPokerStars = Tc2HandGrabberPokerStars.HandGrabber(
				Tc2HandGrabberPokerStars.HandParser(),
				Tc2HandGrabberPokerStars.HandFormatterHtmlTabular(),
				parent=self,
				)
		self.Tc2HandGrabberPokerStars.handGrabbed.connect(self.onHandGrabberGrabbedHand)

		self.toolBar = Tc2Config.WebViewToolBar(self.webView,
				settingsKeyZoomFactor=self.SettingsKeyZoomFactor
				)

		# set up actions
		self.actionCopy = self.webView.pageAction(QtWebKit.QWebPage.Copy)
		self.actionCopy.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Copy))
		self.addAction(self.actionCopy)

		self.actionSelectAll = self.webView.pageAction(QtWebKit.QWebPage.SelectAll)
		self.actionSelectAll.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.SelectAll))
		self.addAction(self.actionSelectAll)

		self.actionOpen = QtGui.QAction(self)
		self.actionOpen.setText('Open..')
		self.actionOpen.setToolTip('Open a hand (Alt+O)')
		self.actionOpen.setShortcut(QtGui.QKeySequence('Alt+O') )
		self.actionOpen.triggered.connect(self.onActionOpenTriggered)
		self.toolBar.addAction(self.actionOpen)

		self.actionSave = QtGui.QAction(self)
		self.actionSave.setText('Save..')
		self.actionSave.setToolTip('Save hand (Alt+S)')
		self.actionSave.setShortcut(QtGui.QKeySequence('Alt+S') )
		self.actionSave.triggered.connect(self.onActionSaveTriggered)
		self.toolBar.addAction(self.actionSave)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self.toolBar.addAction(self.actionHelp)

		# connect global signals
		Tc2Config.globalObject.init.connect(self.onInit)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		Tc2Config.globalObject.settingToolBarPositionChanged.connect(self.onSettingToolBarPositionChanged)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def adjustActions(self):
		self.toolBar.actionZoomIn.setEnabled(bool(self._handCache))
		self.toolBar.actionZoomOut.setEnabled(bool(self._handCache))
		self.actionSave.setEnabled(bool(self._handCache))

	def layout(self,):
		toolBarPositionBottom = Tc2Config.settingsValue(Tc2Config.SettingsKeyToolBarPosition, Tc2Config.ToolBarPositionTop).toString() == Tc2Config.ToolBarPositionBottom
		grid = self.grid
		if not toolBarPositionBottom:
			grid.col(self.toolBar)
			grid.row()
		grid.col(self.webView)
		if toolBarPositionBottom:
			grid.row()
			grid.col(self.toolBar)

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
			if len(self._handCache) > self.webView.page().history().maximumItemCount():
				self._handCache.pop(0)
		self.webView.setUrl(myUrl)
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
		fp = open(fileName, 'r')
		try:
			data = QtCore.QString.fromUtf8(fp.read())
		finally:
			fp.close()
		self.setHand(data, fileName=fileName)

	def onActionSaveTriggered(self):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Save Hand..',
				fileFilters=('HtmlFiles (*.html *.htm)', 'All Files (*)'),
				#TODO: rename to Gui/HandViewer/DialogSave/State
				settingsKey=self.SettingsKeyDialogSaveState,
				defaultSuffix='html',
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.webView.page().mainFrame().toHtml().toUtf8()  )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Hand\n\n%s' % d)
		finally:
			if fp is not None: fp.close()
		#TODO: can we rename hand in cache? i font think so. no way to inform WebKit

	def onCloseEvent(self, event):
		self.Tc2HandGrabberPokerStars.stop()

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.actionCopy)
		menu.addAction(self.actionSelectAll)
		point = self.webView.mapToGlobal(point)
		menu.exec_(point)

	def onHandGrabberGrabbedHand(self, data):
		if data:
			self.setHand(data)
		else:
			Tc2Config.globalObject.feedbackMessage.emit('Could not grab hand')

	def onInit(self):
		self.webView.setUrl(QtCore.QUrl(''))
		self.adjustActions()
		self.layout()
		self.Tc2HandGrabberPokerStars.start()

	def onNetworkGetData(self, networkReply):
		url = networkReply.url()
		for myUrl, data in self._handCache:
			if myUrl == url:
				networkReply.setData(data,  'text/html; charset=UTF-8')
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

	def onSettingToolBarPositionChanged(self, position):
		self.grid.clear()
		self.layout()



