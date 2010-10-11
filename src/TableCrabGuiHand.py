
#TODO: when opening a hand - enable navigate back?

import TableCrabConfig
import PokerStarsHandGrabber
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui, QtWebKit

#*******************************************************************************************
#
#*******************************************************************************************
class FrameHand(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self._hasHand = False

		self.webView = QtWebKit.QWebView(self)
		self.webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.webView.customContextMenuRequested.connect(self.onContextMenuWebView)

		self.pokerStarsHandGrabber = PokerStarsHandGrabber.HandGrabber(
				PokerStarsHandGrabber.HandParser(),
				PokerStarsHandGrabber.HandFormatterHtmlTabular(),
				parent=self,
				)
		self.pokerStarsHandGrabber.handGrabbed.connect(self.onPShandGrabberHandGrabbed)
		TableCrabConfig.globalObject.init.connect(self.onInit)
		TableCrabConfig.globalObject.closeEvent.connect(self.onCloseEvent)

		self.toolBar = TableCrabConfig.WebViewToolBar(self.webView,
				settingsKeyZoomFactor='Gui/Hand/ZoomFactor',
				settingsKeyZoomSteps='Gui/WebView/ZoomSteps',
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

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def adjustActions(self):
		self.toolBar.actionZoomIn.setEnabled(bool(self._hasHand))
		self.toolBar.actionZoomOut.setEnabled(bool(self._hasHand))
		self.actionSave.setEnabled(bool(self._hasHand))

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.webView)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self, checked):
		TableCrabGuiHelp.dialogHelp('hand', parent=self)

	def onActionOpenTriggered(self):
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Hand..',
				fileFilters=('HtmlFiles (*.html *.htm)', 'All Files (*)'),
				settingsKey='Gui/Hand/DialogOpen/State',
				)
		if fileName is None:
			return
		fp = open(fileName, 'r')
		try:	self.webView.setHtml( QtCore.QString.fromUtf8(fp.read()) )
		finally: fp.close()
		self._hasHand = True
		self.adjustActions()
		# give feedback
		if self.isVisible():
			fileInfo = QtCore.QFileInfo(fileName)
			handName = fileInfo.baseName()
			handName = TableCrabConfig.truncateString(handName, TableCrabConfig.MaxName)
			TableCrabConfig.globalObject.feedback.emit(self, handName)

	def onActionSaveTriggered(self):
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Save Hand..',
				fileFilters=('HtmlFiles (*.html *.htm)', 'All Files (*)'),
				settingsKey='Gui/Hand/DialogSave/State',
				defaultSuffix='html',
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.webView.page().mainFrame().toHtml().toUtf8()  )
		except Exception, d:
			TableCrabConfig.msgWarning(self, 'Could Not Save Hand\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onCloseEvent(self, event):
		self.pokerStarsHandGrabber.stop()

	def onContextMenuWebView(self, point):
		menu = QtGui.QMenu(self)
		menu.addAction(self.actionCopy)
		menu.addAction(self.actionSelectAll)
		point = self.webView.mapToGlobal(point)
		menu.exec_(point)

	def onInit(self):
		self.webView.setUrl(QtCore.QUrl(''))
		self.adjustActions()
		self.layout()
		self.pokerStarsHandGrabber.start()

	def onPShandGrabberHandGrabbed(self, data):
		self._hasHand = bool(data)
		self.webView.setHtml( QtCore.QString.fromUtf8(data) )
		self.adjustActions()




