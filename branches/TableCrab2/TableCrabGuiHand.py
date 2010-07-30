
from PyQt4 import QtCore, QtGui, QtWebKit
import TableCrabConfig
import PSHandGrabber
import TableCrabGuiHelp

#*******************************************************************************************
#
#*******************************************************************************************

class FrameHand(QtGui.QFrame):
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
			
		self._hasHand = False
		self.webView = QtWebKit.QWebView(self)
		self.webView.setUrl(QtCore.QUrl(''))
		self.webView.setZoomFactor( TableCrabConfig.settingsValue('Gui/Hand/ZoomFactor',  self.webView.zoomFactor() ).toDouble()[0] )
		self.psHandGrabber = PSHandGrabber.HandGrabber(
				PSHandGrabber.HandParser(),
				PSHandGrabber.HandFormatterHtmlTabular(),
				parent=self,
				)
		TableCrabConfig.signalConnect(self.psHandGrabber, self, 'handGrabbed(QObject*, QString)', self.onPShandGrabberHandGrabbed)
		self.psHandGrabber.start()
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
		self.webView.setZoomFactor( TableCrabConfig.settingsValue('Gui/Hand/ZoomFactor',  self.webView.zoomFactor() ).toDouble()[0] )
		
		self.toolBar = TableCrabConfig.TableCrabWebViewToolBar(self.webView,
				settingsKeyZoomFactor='Gui/Hand/ZoomFactor',
				settingsKeyZoomIncrement='Gui/WebView/ZoomIncrement',
				)
		
		self.actionOpen = TableCrabConfig.TableCrabAction(
				parent=self.toolBar,
				text='Open..',
				slot=self.onActionOpenTriggered
				)
		self.toolBar.addAction(self.actionOpen)
		
		self.actionSave = TableCrabConfig.TableCrabAction(
				parent=self.toolBar,
				text='Save..',
				slot=self.onActionSaveTriggered
				)
		self.toolBar.addAction(self.actionSave)
		
		self.actionHelp = TableCrabConfig.TableCrabAction(
				parent=self.toolBar,
				text='Help',
				slot=self.onActionHelpTriggered
				)
		self.toolBar.addAction(self.actionHelp)
				
		self.adjustActions()
		self.layout()
		
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.toolBar, 0,0)
		box.addWidget(self.webView, 1, 0)
		
	def onCloseEvent(self, event):
		self.psHandGrabber.stop()
	
	def adjustActions(self):
		self.toolBar.actionZoomIn.setEnabled(bool(self._hasHand))
		self.toolBar.actionZoomOut.setEnabled(bool(self._hasHand))
		self.actionSave.setEnabled(bool(self._hasHand))
	
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
		try:	self.webView.setHtml(fp.read() )
		finally: fp.close()
		self._hasHand = true
		self.adjustActions()
		
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
		try: fp.write(self.webView.page().mainFrame().toHtml())
		finally: fp.close()
	
	def onActionHelpTriggered(self, checked):
		TableCrabGuiHelp.dialogHelp('hand', parent=self)		
	
	def onPShandGrabberHandGrabbed(self, hand, data):
		self.webView.setHtml(data)
		self._hasHand = True
		self.adjustButtons()
	
	

#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	g = TableCrabConfig.MainWindow()
	g.setCentralWidget(FrameHand(g))
	g.start()
	
