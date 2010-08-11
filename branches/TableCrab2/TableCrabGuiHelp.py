
#TODO: disable context menu
#TODO: give feedback ++ set tree to point to current page
#TODO: save splitter state in DialogHelp()
#TODO: would be nice to auto-generate topics from disk. for now we have to keep track by hand.
# auto-generating woul drequire some naming scheme to get the hirarchy - we only support flat
# directories in our NetworkAccessmanager()  ++ some Html parsing to retrieve the desired title
# of the topic. problem is we may not get topis in a dedicated order.
#
# some sleketon code::
#
#DirHtmlPages = wherever
#TitlePat = re.compile('.*?<title>(.*?)</title>', re.I | re.M | re.S)
#topics = {}
#for name in os.listdir(DirHtmlPages):
#	fileName = os.path.join(DirHtmlPages, name)
#	if not os.path.isfile(fileName): continue
#	if not os.path.splitext(name)[1].lower() == '.html': continue
#	with open(fileName, 'r') as fp:
#		data = fp.read()
#		result = TitlePat.match(data)
#		if result is not None:
#			print result.group(1)
#		else:
#			print 'Warning: no title found in : %s' % name
#		#TODO: break fileName into pieces. something like: topic-subtopic-MyPage.html

import TableCrabConfig
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork

#**********************************************************************************************
#
#**********************************************************************************************
Topics = [
		('index', 'TableCrab'), [
			('setup', 'Setup'), [
				('screenshotInfo', 'Screenshot Info Dialog'),
				],
			('hotkeys', 'Hotkeys'), [
				('hotkeyCheck', 'Check'),
				('hotkeyFold', 'Fold'),
				('hotkeyRaise', 'Raise'),
				('hotkeyAll_In', 'All-in'),
				('hotkeyHilightBetAmount', 'Hilight Bet Amount'),
				('hotkeyMultiplyBetAmount', 'Multiply Bet Amount'),
				('hotkeyAddToBetAmount', 'Add To Bet Amount'),
				('hotkeySubtractFromBetAmount', 'Subtract From Bet Amount'),
				('hotkeyReplayer', 'Replayer'),
				('hotkeyInstantHandHistory', 'Instant Hand History'),
				('hotkeyScreenshot', 'Screenshot'),
				],
			('hand', 'Hand'),
			('settings', 'Settings'), [
				('settingsGlobal', 'Global'),
				('settingsPokerStars', 'PokerStars'),
				('settingsHand', 'Hand'),
				('settingsHandCss', 'Hand-Css'),
				],
			],
		('versionHistory.html', 'Version History'),
		]
		
def walkTopics():
	def walker(item, level=0):
		if not isinstance(item, list):
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
		
		#NOTE: from previous versions of Qt i found we can not keep the url bcause Qt nulls it on return
		url = QtCore.QUrl(request.url())
			
		# serve local files from our resource modules
		if url.scheme() == "file" and operation == self.GetOperation:
			fileInfo = QtCore.QFileInfo(url.path())
			name = str(fileInfo.baseName() )		#NOTE: we need to string it ..getattr() crasches otherwise
			ext = fileInfo.suffix()
			
			buffer = ByteArrayBuffer()
			reply = TableCrabReply(buffer, parent=self)
			reply.setUrl(url)
			
			if ext == 'html':
				reply.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant("text/html; charset=UTF-8"))
				func = getattr(TableCrabConfig.HtmlPages, name, None)
				if func is not None:
					arr = QtCore.QByteArray()
					arr+= func()
					buffer.setByteArray(arr)
				else:
					buffer.setByteArray(QtCore.QByteArray('<h2>404: File Not Found</h2>'))
				return reply
				
			elif ext == 'png':
				reply.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant("image/png"))
				func = getattr(TableCrabConfig.Pixmaps, name, None)
				if func is not None:		# let QtWebKit handle other case
					arr = QtCore.QByteArray()
					p = QtCore.QBuffer(arr)
					p.open(p.WriteOnly)
					px = func()
					px.save(p, 'png')
					buffer.setByteArray(arr)
					return reply
			
			elif ext == 'css':
				reply.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant("text/css"))
				func = getattr(TableCrabConfig.StyleSheets, name, None)
				if func is not None:		# let QtWebKit handle other case
					arr = QtCore.QByteArray()
					arr+= func()
					buffer.setByteArray(arr)
					return reply	
			
		return QtNetwork.QNetworkAccessManager.createRequest(self, operation, request, data)

#**********************************************************************************************
#
#**********************************************************************************************

class FrameHelpView(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.webView = QtWebKit.QWebView(self)
		self.webView.setUrl(QtCore.QUrl(''))
		oldManager = self.webView.page().networkAccessManager()
		self.networkAccessManager = NetworkAccessManager(oldManager, parent=self)
		self.webView.page().setNetworkAccessManager(self.networkAccessManager)
		##self.webView.page().setForwardUnsupportedContent(True)
		
		self.layout()
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.webView, 0, 0)
	def setUrl(self, url):
		self.webView.setUrl(url)
	

class FrameHelp(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.frameHelpView = FrameHelpView(self)
		
		self.tree = QtGui.QTreeWidget(self)
		self.tree.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSettingAlternatingRowColorsChanged)
		
		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.tree)
		self.splitter.addWidget(self.frameHelpView)
				
		self.tree.setExpandsOnDoubleClick(False)
		self.tree.setRootIsDecorated(False)
		self.tree.header().setVisible(False)
			
		self.toolBar = TableCrabConfig.WebViewToolBar(self.frameHelpView.webView,
				settingsKeyZoomFactor='Gui/Help/ZoomFactor',
				settingsKeyZoomIncrement='Gui/WebView/ZoomIncrement',
				)
		
		#
		lastTopic = TableCrabConfig.settingsValue('Gui/Help/Topic', '').toString()
		lastTopicItem = None
		firstTopicItem = None
		stack = []
		for level, (topic, topicName) in walkTopics():
			while len(stack) > level:
				stack.pop(-1)
			if stack:
				item = QtGui.QTreeWidgetItem(stack[-1], [topicName, ])
			else:
				item = QtGui.QTreeWidgetItem(self.tree, [topicName, ])
			item.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(topic))
			
			#TODO: for some reason DontShowIndicator items are never expanded. seems to be a but in Qt4
			#item.setChildIndicatorPolicy(item.DontShowIndicator)
			item.setExpanded(True)
			stack.append(item)
			if topic == lastTopic:
				lastTopicItem = item
			if firstTopicItem is None:
				firstTopicItem = item
			
		self.tree.itemSelectionChanged.connect(self.onItemSelectionChanged)
		self.tree.itemActivated.connect(self.onItemSelectionChanged)
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)
		if lastTopicItem is not None:
			self.tree.setCurrentItem(lastTopicItem)
		else:
			self.tree.setCurrentItem(firstTopicItem)
		
		self.layout()
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Help/SplitterState', QtCore.QByteArray()).toByteArray() )
		
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.toolBar, 0, 0)
		box.addWidget(self.splitter, 1, 0)
		
	def onItemSelectionChanged(self):
		items = self.tree.selectedItems()
		if not items: return
		item = items[0]
		topic = item.data(0, QtCore.Qt.UserRole).toString()
		#url = QtCore.QUrl('TableCrab://HtmlPage/%s' % topic)
		url = QtCore.QUrl('%s.html' % topic)
		self.frameHelpView.setUrl(url)
		TableCrabConfig.settingsSetValue('Gui/Help/Topic', topic)
		
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Help/SplitterState', self.splitter.saveState() )

	def onSettingAlternatingRowColorsChanged(self, flag):
		self.tree.setAlternatingRowColors(flag)

class _DialogHelp(QtGui.QDialog):
	def __init__(self, topic, parent=None):
		QtGui.QDialog.__init__(self, parent)
		
		self.setWindowTitle(TableCrabConfig.dialogTitle('Help') )
		self.setWindowIcon( QtGui.QIcon(TableCrabConfig.Pixmaps.tableCrab()) )
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		self.buttonBox.accepted.connect(self.accept)
		
		TableCrabConfig.settingsSetValue('Gui/Help/Topic', topic)
		self.frameHelp = FrameHelp(parent=self)
		self.layout()
		self.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogHelp/Geometry', QtCore.QByteArray()).toByteArray() )
			
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.frameHelp, 0, 0)
		box.addWidget(TableCrabConfig.HLine(self), 1, 0)
		box.addWidget(self.buttonBox, 2, 0)
	
	def hideEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/DialogHelp/Geometry', self.saveGeometry() )
		QtGui.QDialog.hideEvent(self, event)

def dialogHelp(topic, parent=None):
	dlg = _DialogHelp(topic, parent=parent)
	dlg.show()
	#TODO: how to save the splitter state? code below does not work. we may have to abstract the frame a bit more to get support for this
	##dlg.frameHelpTree.onCloseEvent(None)

#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	import TableCrabMainWindow
	g = TableCrabMainWindow.MainWindow()
	g.setCentralWidget(FrameHelp(g))
	g.start()
	
	


