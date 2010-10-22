
#TODO: restore collasped / expanded in topic tree. overkill?

import Tc2Config
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
class FrameHelp(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Help'
	SettingsKeyZoomFactor = SettingsKeyBase + '/ZoomFactor'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'
	SettingsKeyHelpTopic = SettingsKeyBase + '/Topic'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.webView = QtWebKit.QWebView(self)
		self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)		#
		self.webView.customContextMenuRequested.connect(self.onContextMenuWebView)
		oldManager = self.webView.page().networkAccessManager()
		self.networkAccessManager = Tc2Config.RawNetworkAccessManager(oldManager, parent=self)
		page = self.webView.page()
		page.setNetworkAccessManager(self.networkAccessManager)

		# setup tool bar
		self.toolBar = Tc2Config.WebViewToolBar(self.webView, settingsKeyZoomFactor=self.SettingsKeyZoomFactor)

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
		Tc2Config.globalObject.init.connect(self.onInit)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		Tc2Config.globalObject.settingAlternatingRowColorsChanged.connect(self.onSettingAlternatingRowColorsChanged)
		self.tree.itemSelectionChanged.connect(self.onItemSelectionChanged)
		self.tree.itemActivated.connect(self.onItemSelectionChanged)
		self.webView.urlChanged.connect(self.onUrlChanged)
		self.networkAccessManager.getData.connect(self.onNetworkGetData)


	#------------------------------------------------------------------------------------------------------------------
	# methods
	#------------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.splitter)

	#------------------------------------------------------------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------------------------------------------------------------
	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState() )

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
		self.tree.setAlternatingRowColors( Tc2Config.settingsValue(Tc2Config.SettingsKeyAlternatingRowColors, False).toBool() )
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		#
		lastTopic = Tc2Config.settingsValue(self.SettingsKeyHelpTopic, '').toString()
		lastTopicItem = None
		firstTopicItem = None
		stack = []
		for level, (topic, topicName) in Tc2Config.walkHelpTopics():
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
		Tc2Config.settingsSetValue(self.SettingsKeyHelpTopic, topic)

	def onNetworkGetData(self, networkReply):
		# serve pages from our resource modules
		url = networkReply.url()
		if url.scheme() == 'file':
			fileInfo = QtCore.QFileInfo(url.path())
			name = str(fileInfo.baseName() )	#NOTE: we need to string it ..getattr() crasches otherwise
			ext = fileInfo.suffix()
			if ext == 'html':
				func = getattr(Tc2Config.HtmlPages, name, None)
				mimeType = 'text/html; charset=UTF-8'
				if func is None:
					data = '<h2>404: File Not Found</h2>'
				else:
					data = func()
				networkReply.setData(data, mimeType)
			elif ext == 'png':
				func = getattr(Tc2Config.Pixmaps, name, None)
				mimeType = 'image/png'
				if func is not None:
					arr = QtCore.QByteArray()
					p = QtCore.QBuffer(arr)
					p.open(p.WriteOnly)
					px = func()
					px.save(p, 'png')
					networkReply.setData(p.data(), mimeType)
			elif ext == 'css':
				func = getattr(Tc2Config.StyleSheets, name, None)
				mimeType = 'text/css'
				if func is not None:
					networkReply.setData(func(), mimeType)

	def onSettingAlternatingRowColorsChanged(self, flag):
		self.tree.setAlternatingRowColors(flag)

	def onUrlChanged(self, url):
		fileInfo = QtCore.QFileInfo(url.path())
		topic = fileInfo.baseName()
		for item in Tc2Config.TreeWidgetItemIterator(self.tree):
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

	SettingsKeyBase = 'Gui/DialogHelp'
	SettingsKeyGeometry = SettingsKeyBase + '/Geometry'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'

	def __init__(self, topic, parent=None):
		QtGui.QDialog.__init__(self, parent)

		self.setWindowTitle(Tc2Config.dialogTitle('Help') )
		self.setWindowIcon( QtGui.QIcon(Tc2Config.Pixmaps.tableCrab()) )
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		self.buttonBox.accepted.connect(self.accept)

		Tc2Config.settingsSetValue(FrameHelp.SettingsKeyHelpTopic, topic)
		self.frameHelp = FrameHelp(parent=self)
		self.layout()
		self.frameHelp.onInit()
		self.frameHelp.toolBar.onInit()
		self.restoreGeometry( Tc2Config.settingsValue(self.SettingsKeyGeometry, QtCore.QByteArray()).toByteArray() )
		self.frameHelp.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )

	#------------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#------------------------------------------------------------------------------------------------------------------
	def hideEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeyGeometry, self.saveGeometry() )
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.frameHelp.splitter.saveState() )
		QtGui.QDialog.hideEvent(self, event)

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.frameHelp)
		grid.row()
		grid.col(Tc2Config.HLine(self))
		grid.row()
		grid.col(self.buttonBox)

#************************************************************************************
#
#************************************************************************************
def dialogHelp(topic, parent=None):
	dlg = _DialogHelp(topic, parent=parent)
	dlg.show()



