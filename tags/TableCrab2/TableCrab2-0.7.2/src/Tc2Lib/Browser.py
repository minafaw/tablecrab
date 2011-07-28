
from PyQt4 import QtCore, QtGui, QtNetwork, QtWebKit


#************************************************************************************
# customized network access manager so we can serve raw data from anywhere
#
#************************************************************************************
class RawNetworkReply(QtNetwork.QNetworkReply):
	# this thingy will hand out everything you throw at it via setData()
	def __init__(self, parent=None):
		QtNetwork.QNetworkReply.__init__(self, parent)
		self._data = None
		self._dataPos = 0
		self.open(self.ReadOnly | self.Unbuffered)
		self.timer = QtCore.QTimer(self)
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.emitSignals)
		self.timer.setInterval(0)
		self.timer.start()
	def emitSignals(self):
		self.readyRead.emit()
		self.finished.emit()
	def abort(self):	pass
	def bytesAvailable(self):
		if self._data is not None:
			return len(self._data) - self._dataPos
		return 0
	def isSequential(self): return True
	def readData(self, maxSize):
		#NOTE: emitting finished() crashes in PyQt4.8.1. used to work in PyQt4-7.7 no idea why
		# maybe i am getting wrong what it is supposed to do?
		#self.finished.emit()
		#NOTE: we can not return -1 here. no idea how this is handled in PyQt
		stop = self._dataPos + maxSize
		if stop >= len(self._data):
			stop = len(self._data)
		data =  self._data[self._dataPos:stop]
		self._dataPos = stop
		arr = QtCore.QByteArray()
		arr += data
		return arr.data()
	def setData(self, data, mimeType):
		self.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant(mimeType))
		self._data = data
	def hasData(self):
		return self._data is not None

# usage:
# 1) connect to signal getData()
# 2) this thing will throw a networkReply at your slot
# 3) dump data to the reply via networkReply.setData(data, mimeType)
#     not setting data or setting data to None will serve whatever QWebKit serves as default
#NOTE: QNetworkAccessManager is quite a bitch. slightest err will segfault
class RawNetworkAccessManager(QtNetwork.QNetworkAccessManager):

	getData =  QtCore.pyqtSignal(RawNetworkReply)

	def __init__(self, oldNetworkManager, parent=None):
		QtNetwork.QNetworkAccessManager.__init__(self, parent)
		self._oldNetworkManager = oldNetworkManager
		self.setCache(self._oldNetworkManager.cache())
		self.setCookieJar(self._oldNetworkManager.cookieJar())
		self.setProxy(self._oldNetworkManager.proxy())
		self.setProxyFactory(self._oldNetworkManager.proxyFactory())

	def createRequest(self, operation, request, data):
		#NOTE: from previous versions of Qt i found we can not keep the url bcause Qt nulls it on return
		url = QtCore.QUrl(request.url())
		if operation == self.GetOperation:
			networkReply = RawNetworkReply(parent=self)
			networkReply.setUrl(url)
			self.getData.emit(networkReply)
			if networkReply.hasData():
				return networkReply
		return QtNetwork.QNetworkAccessManager.createRequest(self, operation, request, data)


class RawBrowser(QtWebKit.QWebView):

	def __init__(self, parent=None):
		QtWebKit.QWebView.__init__(self, parent)

		page = self.page()
		oldNetworkManager = page.networkAccessManager()
		self._networkAccessManager = RawNetworkAccessManager(oldNetworkManager, parent=self)
		page.setNetworkAccessManager(self._networkAccessManager)

	def networkAccessManager(self):
		return self._networkAccessManager

	def clearHistory(self):
		history = self.history()
		oldItemCount = history.maximumItemCount()
		history.setMaximumItemCount(0)
		history.clear()
		history.setMaximumItemCount(oldItemCount)


class BrowserToolBar(QtGui.QToolBar):
	ZoomFactorMin = 0.5
	ZoomFactorMax = 7
	ZoomFactorDefault = 1
	zoomFactorChanged = QtCore.pyqtSignal(float)
	ZoomStepsMin = 1
	ZoomStepsMax = 40
	ZoomStepsDefault = 40
	def __init__(self, webView):
		QtGui.QToolBar.__init__(self, webView)
		self.webView = webView
		self._zoomSteps = self.ZoomStepsDefault

		self.actionBack = self.webView.pageAction(QtWebKit.QWebPage.Back)
		self.actionBack.setShortcut(QtGui.QKeySequence.Back)
		self.actionBack.setToolTip('Back (Alt+-)')
		self.addAction(self.actionBack)
		self.actionForward = self.webView.pageAction(QtWebKit.QWebPage.Forward)
		self.actionForward.setToolTip('Forward (Alt++)')
		self.actionForward.setShortcut(QtGui.QKeySequence.Forward)
		self.addAction(self.actionForward)

		self.actionZoomIn = QtGui.QAction(self)
		self.actionZoomIn.setText('ZoomIn')
		self.actionZoomIn.setToolTip('ZoomIn (Ctrl++)')
		#TODO: find a way to set icon
		#self.actionZoomIn.setIcon(QtGui.QIcon(Pixmaps.magnifierPlus() ) )
		self.actionZoomIn.setShortcut(QtGui.QKeySequence.ZoomIn)
		self.actionZoomIn.setAutoRepeat(True)
		self.actionZoomIn.triggered.connect(self.zoomIn)
		self.addAction(self.actionZoomIn)

		self.actionZoomOut = QtGui.QAction(self)
		self.actionZoomOut.setText('ZoomOut')
		self.actionZoomOut.setToolTip('ZoomOut (Ctrl+-)')
		#TODO: find a way to set icon
		#self.actionZoomOut.setIcon(QtGui.QIcon(Pixmaps.magnifierMinus() ) )
		self.actionZoomOut.setShortcut(QtGui.QKeySequence.ZoomOut)
		self.actionZoomOut.setAutoRepeat(True)
		self.actionZoomOut.triggered.connect(self.zoomOut)
		self.addAction(self.actionZoomOut)

	def _nextZoom(self, zoomIn=True):
		factor = self.webView.zoomFactor()
		if zoomIn:
			factor += self.ZoomFactorMax / float(self.zoomSteps() )
			factor = min(factor, self.ZoomFactorMax)
		else:
			factor -= self.ZoomFactorMax / float(self.zoomSteps() )
			factor = max(factor, self.ZoomFactorMin)
		self.webView.setZoomFactor(factor)
		self.zoomFactorChanged.emit(factor)
		self.adjustActions()

	def zoomIn(self):
		self._nextZoom(zoomIn=True)

	def zoomOut(self):
		self._nextZoom(zoomIn=False)

	def adjustActions(self):
		self.actionZoomIn.setEnabled(self.webView.zoomFactor() < self.ZoomFactorMax)
		self.actionZoomOut.setEnabled( self.webView.zoomFactor() > self.ZoomFactorMin)

	def setZoomFactor(self, value):
		if value > self.ZoomFactorMax or value < self.ZoomFactorMin:
			value = self.ZoomFactorDefault
		self.webView.setZoomFactor(value)
		self.zoomFactorChanged.emit(value)
		self.adjustActions()

	def zoomFactor(self):
		return self.webView.zoomFactor()

	def setZoomSteps(self, value):
		if value > self.ZoomStepsMax or value < self.ZoomStepsMin:
			value = self.ZoomStepsDefault
		self._zoomSteps = value

	def zoomSteps(self):
		return self._zoomSteps


class BrowserSearchBar(QtGui.QToolBar):

	def __init__(self, browser):
		QtGui.QToolBar.__init__(self, browser)

		self.label = QtGui.QLabel('Search:', self)
		self.addWidget(self.label)

		self.browser = browser
		self.edit = QtGui.QLineEdit(self)
		self.addWidget(self.edit)
		self.edit.textChanged.connect(self.onEditTextChanged)

		self.actionSearchUpwards = QtGui.QAction(self)
		self.actionSearchUpwards.setText('Upwards')
		self.actionSearchUpwards.setToolTip('Search upwards (Alt+Up)')
		self.actionSearchUpwards.setShortcut(QtGui.QKeySequence('Alt+Up') )
		self.actionSearchUpwards.triggered.connect(self.onActionSearchUpwardsTriggered)
		self.addAction(self.actionSearchUpwards)

		self.actionSearchDownwards = QtGui.QAction(self)
		self.actionSearchDownwards.setText('Downwards')
		self.actionSearchDownwards.setToolTip('Search downwards (Alt+Down)')
		self.actionSearchDownwards.setShortcut(QtGui.QKeySequence('Alt+Down') )
		self.actionSearchDownwards.triggered.connect(self.onActionSearchDownwardsTriggered)
		self.addAction(self.actionSearchDownwards)

		self.checkCaseSensitive = QtGui.QCheckBox('Case sensitive', self)
		self.addWidget(self.checkCaseSensitive)

	def onEditTextChanged(self, text):
		hasText = bool(text)
		self.actionSearchUpwards.setEnabled(hasText)
		self.actionSearchDownwards.setEnabled(hasText)

	def onActionSearchUpwardsTriggered(self):
		text = self.edit.text()
		flags = QtWebKit.QWebPage.FindWrapsAroundDocument | QtWebKit.QWebPage.FindBackward
		if self.checkCaseSensitive.checkState() == QtCore.Qt.Checked:
			flags |= QtWebKit.QWebPage.FindCaseSensitively
		self.browser.findText(text, flags)

	def onActionSearchDownwardsTriggered(self):
		text = self.edit.text()
		flags = QtWebKit.QWebPage.FindWrapsAroundDocument
		if self.checkCaseSensitive.checkState() == QtCore.Qt.Checked:
			flags |= QtWebKit.QWebPage.FindCaseSensitively
		self.browser.findText(text, flags)

	def setFocus(self):
		self.edit.setFocus(QtCore.Qt.OtherFocusReason)
		self.edit.selectAll()


class RawBrowserFrame(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self._browser = RawBrowser(self)
		self._toolBar = BrowserToolBar(self._browser)
		self._searchBar = BrowserSearchBar(self._browser)
		self._searchBar.setVisible(False)
		self._layout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom, self)
		self._layout.setSpacing(0)
		self._layout.setContentsMargins(0, 0, 0, 0)

		self.actionSearch = QtGui.QAction(self)
		self.actionSearch.setText('Search text')
		self.actionSearch.setToolTip('Search text (Ctrl+F)')
		self.actionSearch.setShortcut(QtGui.QKeySequence('Ctrl+F') )
		self.actionSearch.triggered.connect(self.onActionSearchTriggered)
		self.addAction(self.actionSearch)

	def browser(self):
		return self._browser

	def toolBar(self):
		return self._toolBar

	def searchBar(self):
		return self._searchbar

	def layout(self, toolBarTop=True):
		# clear layout
		while self._layout.takeAt(0) is not None: pass
		if toolBarTop:
			self._layout.addWidget(self._toolBar)
		self._layout.addWidget(self._browser)
		self._layout.addWidget(self._searchBar)
		if not toolBarTop:
			self._layout.addWidget(self._toolBar)

	def onActionSearchTriggered(self):
		if self._searchBar.isVisible():
			self._searchBar.setVisible(False)
		else:
			self._searchBar.setVisible(True)
			self._searchBar.setFocus()














