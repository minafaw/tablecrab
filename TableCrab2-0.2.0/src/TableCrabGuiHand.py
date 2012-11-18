
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

		self.actionOpen = TableCrabConfig.Action(
				parent=self.toolBar,
				text='Open..',
				toolTip='Open a hand (Alt+O)',
				slot=self.onActionOpenTriggered,
				shortcut='Alt+O',
				)
		self.toolBar.addAction(self.actionOpen)

		self.actionSave = TableCrabConfig.Action(
				parent=self.toolBar,
				text='Save..',
				toolTip='Save hand (Alt+S)',
				slot=self.onActionSaveTriggered,
				shortcut='Alt+S',
				)
		self.toolBar.addAction(self.actionSave)

		self.actionHelp = TableCrabConfig.Action(
				parent=self.toolBar,
				text='Help',
				toolTip='Help (F1)',
				slot=self.onActionHelpTriggered,
				shortcut='F1',
				)
		self.toolBar.addAction(self.actionHelp)

		self.adjustActions()
		self.layout()
		self.pokerStarsHandGrabber.start()

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def adjustActions(self):
		self.toolBar.actionZoomIn.setEnabled(bool(self._hasHand))
		self.toolBar.actionZoomOut.setEnabled(bool(self._hasHand))
		self.actionSave.setEnabled(bool(self._hasHand))

	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.toolBar, 0,0)
		box.addWidget(self.webView, 1, 0)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onActionHelpTriggered(self, checked):
		TableCrabGuiHelp.dialogHelp('hand', parent=self)

	def onActionOpenTriggered(self):
		dlg = QtGui.QFileDialog(self)
		imageFormats = [QtCore.QString(i).toLower() for i in  QtGui.QImageReader.supportedImageFormats()]
		dlg.setFileMode(dlg.AnyFile)
		dlg.setWindowTitle('Open Hand..')
		dlg.setAcceptMode(dlg.AcceptOpen)
		filters = QtCore.QStringList()
		filters << 'Html Files (*.html *.htm)'
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue('Gui/Hand/DialogOpen/State', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Hand/DialogOpen/State', dlg.saveState() )
		if result != dlg.Accepted:
			return
		fileName = dlg.selectedFiles()[0]
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
		dlg = QtGui.QFileDialog(self)
		dlg.setWindowTitle('Save Hand..')
		dlg.setFileMode(dlg.AnyFile)
		dlg.setAcceptMode(dlg.AcceptSave)
		dlg.setConfirmOverwrite(True)
		filters = QtCore.QStringList()
		filters << 'Html Files (*.html *.htm)'
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue('Gui/Hand/DialogSave/State', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Hand/DialogSave/State', dlg.saveState() )
		if result != dlg.Accepted:
			return
		fileName = dlg.selectedFiles()[0]
		fp = open(fileName, 'w')
		try: fp.write(self.webView.page().mainFrame().toHtml().toUtf8() )
		finally: fp.close()

	def onCloseEvent(self, event):
		self.pokerStarsHandGrabber.stop()

	def onInit(self):
		self.webView.setUrl(QtCore.QUrl(''))

	def onPShandGrabberHandGrabbed(self, data):
		self._hasHand = bool(data)
		self.webView.setHtml( QtCore.QString.fromUtf8(data) )
		self.adjustActions()



