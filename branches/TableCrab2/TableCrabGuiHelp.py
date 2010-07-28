
import TableCrabConfig
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork

#**********************************************************************************************
#
#**********************************************************************************************

Topics = (
		'index', (
			'widgets', (
				'screenshotInfo',
				),
			'hotkeys', (
				'hotkeyAlterBetAmount',
				'hotkeyCheck',
				'hotkeyFold',
				'hotkeyHilightBetAmount',
				'hotkeyInstantHandHistory',
				'hotkeyRaise',
				'hotkeyReplayer',
				'hotkeyScreenshot',
				),
			'hand',
			'settings', (
				'settingsGlobal',
				'settingsHand',
				'settingsHandCss',
				'settingsPokerStars',
				),
			),
		)
		
def walkTopics():
	def walker(item, level=0):
		if not isinstance(item, tuple):
			yield level -1, item
		else:
			for child in item:
				for x in walker(child, level=level +1):
					yield x
	return walker(Topics)

#**********************************************************************************************
# customize network access of QWebView so we can serve pages (and pixmap) from our resource modules
#
#**********************************************************************************************
class ByteArrayBuffer(object):
	def __init__(self, byteArray=None):
		self._byteArray = byteArray
		self._pos = 0
	def __len__(self): 
		if self._byteArray is None: return 0
		return len(self._byteArray)
	def setByteArray(self, byteArray=None):
		self._byteArray = byteArray
		self._pos = 0
	def tell(self): return self._pos
	def hasMore(self): return  self._pos < len(self) -1
	def read(self, size):
		if self.tell() >= len(self) -1:
			return None
		stop = self.tell() + size
		if stop > len(self):
			stop = len(self) -1
		arr = self._byteArray[self.tell():stop]
		self._pos = stop
		return arr.data()

class TableCrabReply(QtNetwork.QNetworkReply):
	# this thingy will hand out everything you throw at it via ByteArrayBuffer()
	def __init__(self, buffer, parent=None):
		QtNetwork.QNetworkReply.__init__(self, parent)
		self._buffer = buffer
		##self.setHeader(QtNetwork.QNetworkRequest.ContentLengthHeader, QtCore.QVariant(len(self.content)))
		QtCore.QTimer.singleShot(0, self, QtCore.SIGNAL("readyRead()"))
		self.open(self.ReadOnly | self.Unbuffered)
	def abort(self):	pass
	def bytesAvailable(self):	return len(self._buffer)
	def isSequential(self):	return True
	def readData(self, maxSize):
		data = self._buffer.read(maxSize)
		if not self._buffer.hasMore():
			self.finished.emit()
		return data

class NetworkAccessManager(QtNetwork.QNetworkAccessManager):
	def __init__(self, oldManager, parent=None):
		QtNetwork.QNetworkAccessManager.__init__(self, parent)
		##self.oldManager = oldManager
		self.setCache(oldManager.cache())
		self.setCookieJar(oldManager.cookieJar())
		self.setProxy(oldManager.proxy())
		self.setProxyFactory(oldManager.proxyFactory())
	def createRequest(self, operation, request, data):
		if request.url().scheme() == "TableCrab" and operation == self.GetOperation:
			
			buffer = ByteArrayBuffer()
			reply = TableCrabReply(buffer, parent=self)
			reply.setUrl(request.url() )
			if request.url().authority() == 'htmlpage':
				reply.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant("text/html; charset=UTF-8"))
				name = str( request.url().path() ).lstrip('/')
				func = getattr(TableCrabConfig.HtmlPages, name, None)
				if func is None:
					buffer.setByteArray(QtCore.QByteArray('<h2>404: File Not Found</h2>'))
				else:
					arr = QtCore.QByteArray()
					arr+= func()
					buffer.setByteArray(arr)
				
			elif request.url().authority() == 'pixmap':
				reply.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant("image/png"))
				name = str( request.url().path() ).lstrip('/')
				func = getattr(TableCrabConfig.Pixmaps, name, None)
				if func is None:
					#TODO: ...
					pass
				else:
					arr = QtCore.QByteArray()
					p = QtCore.QBuffer(arr)
					p.open(p.WriteOnly)
					px = func()
					px.save(p, 'png')
					buffer.setByteArray(arr)
			
			return reply
			
		return QtNetwork.QNetworkAccessManager.createRequest(self, operation, request, data)

#**********************************************************************************************
#
#**********************************************************************************************
class FrameHelpTree(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.webView = QtWebKit.QWebView(self)
		self.webView.setUrl(QtCore.QUrl(''))
		self.tree = QtGui.QTreeWidget(self)
		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.tree)
		self.splitter.addWidget(self.webView)
				
		self.tree.setExpandsOnDoubleClick(False)
		self.tree.setRootIsDecorated(False)
		self.tree.header().setVisible(False)
		
		oldManager = self.webView.page().networkAccessManager()
		self.networkAccessManager = NetworkAccessManager(oldManager, parent=self)
		##self.webView.page().setForwardUnsupportedContent(True)
		self.webView.page().setNetworkAccessManager(self.networkAccessManager)
		
		
		#
		lastTopic = TableCrabConfig.settingsValue('Gui/Help/Topic', '').toString()
		lastTopicItem = None
		firstTopicItem = None
		stack = []
		for level, topic in walkTopics():
			while len(stack) > level:
				stack.pop(-1)
			if stack:
				item = QtGui.QTreeWidgetItem(stack[-1], [topic, ])
			else:
				item = QtGui.QTreeWidgetItem(self.tree, [topic, ])
			
			#TODO: for some reason DontShowIndicator items are never expanded. seems to be a but in Qt4
			#item.setChildIndicatorPolicy(item.DontShowIndicator)
			item.setExpanded(True)
			stack.append(item)
			if topic == lastTopic:
				lastTopicItem = item
			if firstTopicItem is None:
				firstTopicItem = item
				
		self.webView.setZoomFactor( TableCrabConfig.settingsValue('Gui/Help/ZoomFactor',  self.webView.zoomFactor() ).toDouble()[0] )
		TableCrabConfig.signalConnect(self.tree, self, 'itemSelectionChanged()', self.onItemSelectionChanged)
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
		if lastTopicItem is not None:
			self.tree.setCurrentItem(lastTopicItem)
		else:
			self.tree.setCurrentItem(firstTopicItem)
		
		self.layout()
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Help/SplitterState', QtCore.QByteArray()).toByteArray() )
		
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.splitter, 0, 0)
	
	def zoomIn(self,):
		zoomIncrement = TableCrabConfig.settingsValue('Gui/WebView/ZoomIncrement', 0.1).toDouble()[0]
		self.webView.setZoomFactor(self.webView.zoomFactor() + zoomIncrement)
		TableCrabConfig.settingsSetValue('Gui/Help/ZoomFactor', self.webView.zoomFactor())
			
	def zoomOut(self):
		zoomIncrement = TableCrabConfig.settingsValue('Gui/WebView/ZoomIncrement', 0.1).toDouble()[0]
		zoom = self.webView.zoomFactor() - zoomIncrement
		if zoom > 0:
			self.webView.setZoomFactor(zoom)
			TableCrabConfig.settingsSetValue('Gui/Help/ZoomFactor', self.webView.zoomFactor() )
		
	def onItemSelectionChanged(self):
		items = self.tree.selectedItems()
		if not items: return
		item = items[0]
		topic =  str(item.text(0))
		url = QtCore.QUrl('TableCrab://HtmlPage/%s' % topic)
		self.webView.setUrl(url)
		TableCrabConfig.settingsSetValue('Gui/Help/Topic', topic)
		
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Help/SplitterState', self.splitter.saveState() )



class FrameHelp(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.frameHelpTree = FrameHelpTree(parent=self)
		
		self.buttonZoomIn = QtGui.QPushButton('Zoom In',self)
		TableCrabConfig.signalConnect(self.buttonZoomIn, self, 'clicked(bool)', self.frameHelpTree.zoomIn)
		self.buttonZoomOut = QtGui.QPushButton('Zoom Out',self)
		TableCrabConfig.signalConnect(self.buttonZoomOut, self, 'clicked(bool)', self.frameHelpTree.zoomOut)
		
		self.layout()
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.frameHelpTree, 0, 0, 1, 6)
		box.addWidget(self.buttonZoomIn, 1,0)
		box.addWidget(self.buttonZoomOut, 1, 1)
		box.addLayout(TableCrabConfig.HStretch(), 1, 5)



class _DialogHelp(QtGui.QDialog):
	def __init__(self, topic, parent=None):
		QtGui.QDialog.__init__(self, parent)
		
		self.setWindowTitle(TableCrabConfig.TableCrabApplicationName + ' - Help')
		self.setWindowIcon( QtGui.QIcon(TableCrabConfig.Pixmaps.tableCrab()) )
		
		TableCrabConfig.settingsSetValue('Gui/Help/Topic', topic)
		self.frameHelpTree = FrameHelpTree(parent=self)
			
		self.buttonZoomIn = QtGui.QPushButton('Zoom In',self)
		TableCrabConfig.signalConnect(self.buttonZoomIn, self, 'clicked(bool)', self.frameHelpTree.zoomIn)
		self.buttonZoomOut = QtGui.QPushButton('Zoom Out',self)
		TableCrabConfig.signalConnect(self.buttonZoomOut, self, 'clicked(bool)', self.frameHelpTree.zoomOut)
		
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.setStandardButtons(self.buttonBox.Ok)
		self.buttonBox.addButton(self.buttonZoomIn, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonZoomOut, self.buttonBox.ActionRole)
		self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
		self.layout()
				
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.frameHelpTree, 0, 0)
		box.addWidget(TableCrabConfig.HLine(self), 1, 0)
		box.addWidget(self.buttonBox, 2, 0)


def dialogHelp(topic, parent=None):
	dlg = _DialogHelp(topic, parent=parent)
	dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHelp/Geometry', QtCore.QByteArray()).toByteArray() )
	dlg.show()
	TableCrabConfig.settingsSetValue('Gui/DialogHelp/Geometry', dlg.saveGeometry() )

#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	g = TableCrabConfig.MainWindow()
	g.setCentralWidget(FrameHelp(g))
	g.start()
	
	


