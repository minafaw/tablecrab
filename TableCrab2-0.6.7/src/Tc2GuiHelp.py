
import Tc2Config
from Tc2Lib import Browser
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
class FrameHelp(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Help'
	SettingsKeyZoomFactor = SettingsKeyBase + '/ZoomFactor'
	SettingsKeySplitterState = SettingsKeyBase + '/SplitterState'
	SettingsKeyHelpTopic = SettingsKeyBase + '/Topic'
	SettingsKeyTopicsCollapsed = SettingsKeyBase + '/TopicsCollapsed'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self._settingsPersistent = True

		self.browserFrame = Browser.RawBrowserFrame(self)
		self.browser = self.browserFrame.browser()
		self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)		#
		self.browser.customContextMenuRequested.connect(self.onContextMenuWebView)

		# setup tool bar
		self.toolBar = self.browserFrame.toolBar()
		self.toolBar.actionZoomIn.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierPlus() ) )
		self.toolBar.actionZoomOut.setIcon(QtGui.QIcon(Tc2Config.Pixmaps.magnifierMinus() ) )
		self.toolBar.zoomFactorChanged.connect(self.onToolBarZoomFactorChanged)

		self.tree = QtGui.QTreeWidget(self)
		self.tree.setUniformRowHeights(True)
		self.tree.setExpandsOnDoubleClick(False)
		self.tree.setRootIsDecorated(False)
		self.tree.header().setVisible(False)

		self.splitter = QtGui.QSplitter(self)
		self.splitter.addWidget(self.tree)
		self.splitter.addWidget(self.browserFrame)

		# set up actions
		self.actionCopy = self.browser.pageAction(QtWebKit.QWebPage.Copy)
		self.actionCopy.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Copy))
		self.addAction(self.actionCopy)

		self.actionSelectAll = self.browser.pageAction(QtWebKit.QWebPage.SelectAll)
		self.actionSelectAll.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.SelectAll))
		self.addAction(self.actionSelectAll)

		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.closeEvent.connect(self.onCloseEvent)
		self.tree.itemSelectionChanged.connect(self.onItemSelectionChanged)
		self.tree.itemActivated.connect(self.onItemSelectionChanged)
		self.browser.urlChanged.connect(self.onUrlChanged)
		self.browser.networkAccessManager().getData.connect(self.onNetworkGetData)

	#------------------------------------------------------------------------------------------------------------------
	# methods
	#------------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.splitter)

	def aboutHtml(self):
		import sys
		from PyQt4.QtCore import qVersion, PYQT_VERSION_STR
		import sipconfig
		from PyQt4 import QtWebKit
		from Tc2Lib.gocr import gocr

		p = '<html><head>'
		p += '<LINK REL=StyleSheet HREF="default.css" TYPE="text/css" MEDIA=screen>'
		p += '</head><body>'

		p += '<div class="textBox">'
		p += '<div class="headerBox">About TableCrab</div>'
		p += '<ul>'
		p += '<li>%s: %s' % (Tc2Config.ApplicationName, Tc2Config.Version)
		p += '<li>Author: %s' % Tc2Config.Author
		p += '<li>Mail: jUrner@arcor.de'
		p += '</ul>'

		p += '<ul>'
		p += '<li>Python: %s.%s.%s' % sys.version_info[:3]
		p += '<li>Sip: %s\n' % sipconfig.Configuration().sip_version_str
		p += '<li>Qt: %s' % qVersion()
		p += '<li>PyQt: %s' % PYQT_VERSION_STR
		p += '<li>WebKit: %s\n' % QtWebKit.qWebKitVersion()
		p += '<li>Gocr: %s\n' % gocr.version()

		p += '</ul>'
		p += '</div>'
		p += '</body></html>'
		return p

	#------------------------------------------------------------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------------------------------------------------------------
	def onCloseEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterState, self.splitter.saveState() )
		topicsCollapsed = []
		for item in Tc2Config.TreeWidgetItemIterator(self.tree):
			if not item.isExpanded():
				topic = item.data(0, QtCore.Qt.UserRole).toString()
				topicsCollapsed.append(topic)
		Tc2Config.settingsSetValue(self.SettingsKeyTopicsCollapsed, topicsCollapsed)

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.actionCopy)
		menu.addAction(self.actionSelectAll)
		point = self.browser.mapToGlobal(point)
		menu.exec_(point)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.tree.setUpdatesEnabled(False)

		self.browser.setUrl(QtCore.QUrl(''))
		#
		lastTopic = Tc2Config.settingsValue(self.SettingsKeyHelpTopic, '').toString()
		topicsCollapsed = Tc2Config.settingsValue(self.SettingsKeyTopicsCollapsed, []).toStringList()
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
			item.setExpanded(topic not in topicsCollapsed)
			##print topic not in topicsCollapsed, topic
			stack.append(item)
			if topic == lastTopic:
				lastTopicItem = item
			if firstTopicItem is None:
				firstTopicItem = item
		if lastTopicItem is None:
			lastTopicItem = firstTopicItem

		# only select topic when item is visible
		allParentsExpanded = True
		parent = lastTopicItem.parent()
		#print parent
		while parent is not None:
			if not parent.isExpanded():
				allParentsExpanded = False
				break
			parent = parent.parent()
		if allParentsExpanded:
			self.tree.setCurrentItem(lastTopicItem)
		else:
			self.tree.setCurrentItem(firstTopicItem)

		self.tree.setUpdatesEnabled(True)

		self.tree.setAlternatingRowColors(globalObject.settingsGlobal.alternatingRowColors())
		globalObject.settingsGlobal.alternatingRowColorsChanged.connect(self.tree.setAlternatingRowColors)
		self.browserFrame.layout(globalObject.settingsGlobal.toolBarPosition() == Tc2Config.ToolBarPositionTop)
		self.layout()
		self.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		globalObject.settingsGlobal.toolBarPositionChanged.connect(
				lambda position, frame=self.browserFrame: frame.layout(toolBarTop=position == Tc2Config.ToolBarPositionTop)
				)

		zoomFactor = Tc2Config.settingsValue(self.SettingsKeyZoomFactor, Browser.BrowserToolBar.ZoomFactorDefault).toDouble()[0]
		self.toolBar.setZoomFactor(zoomFactor)

	def onItemSelectionChanged(self):
		items = self.tree.selectedItems()
		if not items: return
		item = items[0]
		topic = item.data(0, QtCore.Qt.UserRole).toString()
		url = QtCore.QUrl('%s.html' % topic)
		self.browser.setUrl(url)
		if self._settingsPersistent:
			Tc2Config.settingsSetValue(self.SettingsKeyHelpTopic, topic)

	def onNetworkGetData(self, networkReply):
		# serve pages from our resource modules
		url = networkReply.url()
		if url.scheme() == 'file':
			fileInfo = QtCore.QFileInfo(url.path())
			name = str(fileInfo.baseName() )	#NOTE: we need to string it ..getattr() crasches otherwise
			ext = fileInfo.suffix()
			if ext == 'html':
				mimeType = 'text/html; charset=UTF-8'
				if name == 'About':
					data = self.aboutHtml()
				else:
					func = getattr(Tc2Config.HtmlPages, name, None)
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

	def onToolBarZoomFactorChanged(self, value):
		if self._settingsPersistent:
			Tc2Config.settingsSetValue(self.SettingsKeyZoomFactor, value)

	def setTopic(self, topic):
		for item in Tc2Config.TreeWidgetItemIterator(self.tree):
			myTopic = item.data(0, QtCore.Qt.UserRole).toString()
			if myTopic == topic:
				self.tree.setCurrentItem(item)
				break
		else:
			raise ValueError('no such topic: %s' % topic)
		if not self._settingsPersistent:
			Tc2Config.settingsSetValue(self.SettingsKeyHelpTopic, topic)

	def setSettingsPersistent(self, flag):
		self._settingsPersistent = flag

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

		self.frameHelp = FrameHelp(parent=self)
		self.layout()
		self.frameHelp.onGlobalObjectInitSettingsFinished(Tc2Config.globalObject)
		#NOTE: we do not save zoom factor on instant help. instant help settings are temporary
		self.frameHelp.setSettingsPersistent(False)
		self.restoreGeometry( Tc2Config.settingsValue(self.SettingsKeyGeometry, QtCore.QByteArray()).toByteArray() )
		self.frameHelp.splitter.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray() )
		self.frameHelp.setTopic(topic)

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
		#TODO: how to adjust tool bar position acc to SettingsGlobal?
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



