
#TODO: restore collasped / expanded in topic tree. overkill?

import TableCrabConfig
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
class FrameHelp(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.webView = QtWebKit.QWebView(self)
		self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)		#
		self.webView.customContextMenuRequested.connect(self.onContextMenuWebView)
		oldManager = self.webView.page().networkAccessManager()
		self.networkAccessManager = TableCrabConfig.RawNetworkAccessManager(oldManager, parent=self)
		page = self.webView.page()
		page.setNetworkAccessManager(self.networkAccessManager)

		# setup tool bar
		self.toolBar = TableCrabConfig.WebViewToolBar(self.webView,
				settingsKeyZoomFactor='Gui/Help/ZoomFactor',
				settingsKeyZoomSteps='Gui/WebView/ZoomSteps',
				)

		self.tree = QtGui.QTreeWidget(self)
		self.tree.setUniformRowHeights(True)
		self.tree.setExpandsOnDoubleClick(False)
		self.tree.setRootIsDecorated(False)
		self.tree.header().setVisible(False)

		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.tree)
		self.splitter.addWidget(self.webView)

		# set up actions
		self.actionCopy = self.webView.pageAction(QtWebKit.QWebPage.Copy)
		self.actionCopy.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Copy))
		self.addAction(self.actionCopy)

		self.actionSelectAll = self.webView.pageAction(QtWebKit.QWebPage.SelectAll)
		self.actionSelectAll.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.SelectAll))
		self.addAction(self.actionSelectAll)

		# connect signals
		TableCrabConfig.globalObject.init.connect(self.onInit)
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)
		TableCrabConfig.globalObject.settingAlternatingRowColorsChanged.connect(self.onSettingAlternatingRowColorsChanged)
		self.tree.itemSelectionChanged.connect(self.onItemSelectionChanged)
		self.tree.itemActivated.connect(self.onItemSelectionChanged)
		self.webView.urlChanged.connect(self.onUrlChanged)
		self.networkAccessManager.getData.connect(self.onNetworkGetData)


	#------------------------------------------------------------------------------------------------------------------
	# methods
	#------------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.splitter)

	#------------------------------------------------------------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------------------------------------------------------------
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/Help/SplitterState', self.splitter.saveState() )

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.actionCopy)
		menu.addAction(self.actionSelectAll)
		point = self.webView.mapToGlobal(point)
		menu.exec_(point)

	def onInit(self):
		self.layout()
		self.tree.setUpdatesEnabled(False)

		self.webView.setUrl(QtCore.QUrl(''))
		self.tree.setAlternatingRowColors( TableCrabConfig.settingsValue('Gui/AlternatingRowColors', False).toBool() )
		self.splitter.restoreState( TableCrabConfig.settingsValue('Gui/Help/SplitterState', QtCore.QByteArray()).toByteArray() )
		#
		lastTopic = TableCrabConfig.settingsValue('Gui/Help/Topic', '').toString()
		lastTopicItem = None
		firstTopicItem = None
		stack = []
		for level, (topic, topicName) in TableCrabConfig.walkHelpTopics():
			while len(stack) > level:
				stack.pop(-1)
			if stack:
				item = QtGui.QTreeWidgetItem(stack[-1], [topicName, ])
			else:
				item = QtGui.QTreeWidgetItem(self.tree, [topicName, ])
			item.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(topic))

			#TODO: for some reason items are never expanded. seems to be a bug in Qt4
			#item.setChildIndicatorPolicy(item.DontShowIndicator)
			item.setExpanded(True)
			stack.append(item)
			if topic == lastTopic:
				lastTopicItem = item
			if firstTopicItem is None:
				firstTopicItem = item
		if lastTopicItem is not None:
			self.tree.setCurrentItem(lastTopicItem)
		else:
			self.tree.setCurrentItem(firstTopicItem)

		self.tree.setUpdatesEnabled(True)

	def onItemSelectionChanged(self):
		items = self.tree.selectedItems()
		if not items: return
		item = items[0]
		topic = item.data(0, QtCore.Qt.UserRole).toString()
		url = QtCore.QUrl('%s.html' % topic)
		self.webView.setUrl(url)
		TableCrabConfig.settingsSetValue('Gui/Help/Topic', topic)

	def onNetworkGetData(self, networkReply):
		# serve pages from our resource modules
		url = networkReply.url()
		if url.scheme() == 'file':
			fileInfo = QtCore.QFileInfo(url.path())
			name = str(fileInfo.baseName() )	#NOTE: we need to string it ..getattr() crasches otherwise
			ext = fileInfo.suffix()
			if ext == 'html':
				func = getattr(TableCrabConfig.HtmlPages, name, None)
				mimeType = 'text/html; charset=UTF-8'
				if func is None:
					data = '<h2>404: File Not Found</h2>'
				else:
					data = func()
				networkReply.setData(data, mimeType)
			elif ext == 'png':
				func = getattr(TableCrabConfig.Pixmaps, name, None)
				mimeType = 'image/png'
				if func is not None:
					arr = QtCore.QByteArray()
					p = QtCore.QBuffer(arr)
					p.open(p.WriteOnly)
					px = func()
					px.save(p, 'png')
					networkReply.setData(p.data(), mimeType)
			elif ext == 'css':
				func = getattr(TableCrabConfig.StyleSheets, name, None)
				mimeType = 'text/css'
				if func is not None:
					networkReply.setData(func(), mimeType)

	def onSettingAlternatingRowColorsChanged(self, flag):
		self.tree.setAlternatingRowColors(flag)

	def onUrlChanged(self, url):
		fileInfo = QtCore.QFileInfo(url.path())
		topic = fileInfo.baseName()
		for item in TableCrabConfig.TreeWidgetItemIterator(self.tree):
			myTopic = item.data(0, QtCore.Qt.UserRole).toString()
			if myTopic == topic:
				self.tree.setCurrentItem(item)
				break
		else:
			raise ValueError('no topic found for url: %s' % url.path())

#************************************************************************************
#
#************************************************************************************
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
		self.frameHelp.splitter.restoreState( TableCrabConfig.settingsValue('Gui/DialogHelp/SplitterState', QtCore.QByteArray()).toByteArray() )
		self.frameHelp.onInit()
		self.frameHelp.toolBar.onInit()

	#------------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#------------------------------------------------------------------------------------------------------------------
	def hideEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/DialogHelp/Geometry', self.saveGeometry() )
		TableCrabConfig.settingsSetValue('Gui/Help/SplitterState', self.frameHelp.splitter.saveState() )
		QtGui.QDialog.hideEvent(self, event)

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.frameHelp)
		grid.row()
		grid.col(TableCrabConfig.HLine(self))
		grid.row()
		grid.col(self.buttonBox)

#************************************************************************************
#
#************************************************************************************
def dialogHelp(topic, parent=None):
	dlg = _DialogHelp(topic, parent=parent)
	dlg.show()



