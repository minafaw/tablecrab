
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
		 
		
		self.lastHand = None
		self.webView = QtWebKit.QWebView(self)
		self.webView.setUrl(QtCore.QUrl(''))
		self.psHandGrabber = PSHandGrabber.HandGrabber(
				PSHandGrabber.HandParser(),
				PSHandGrabber.HandFormatterHtmlTabular(),
				parent=self,
				)
		TableCrabConfig.signalConnect(self.psHandGrabber, self, 'handGrabbed(QObject*, QString)', self.onPShandGrabberHandGrabbed)
		self.psHandGrabber.start()
		
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
		self.webView.setZoomFactor(TableCrabConfig.settingsValue('Gui/Hand/ZoomFactor', 1.0).toDouble()[0])
				
		self.webView.setZoomFactor( TableCrabConfig.settingsValue('Gui/Hand/ZoomFactor',  self.webView.zoomFactor() ).toDouble()[0] )
		self.buttonZoomIn = QtGui.QPushButton('Zoom In',self)
		TableCrabConfig.signalConnect(self.buttonZoomIn, self, 'clicked(bool)', self.onButtonZoomInClicked)
		self.buttonZoomOut = QtGui.QPushButton('Zoom Out',self)
		TableCrabConfig.signalConnect(self.buttonZoomOut, self, 'clicked(bool)', self.onButtonZoomOutClicked)
		self.buttonOpen = QtGui.QPushButton('Open..',self)
		TableCrabConfig.signalConnect(self.buttonOpen, self, 'clicked(bool)', self.onButtonOpenClicked)
		self.buttonSave = QtGui.QPushButton('Save..',self)
		TableCrabConfig.signalConnect(self.buttonSave, self, 'clicked(bool)', self.onButtonSaveClicked)
		self.buttonHelp = QtGui.QPushButton('Help', self)
		TableCrabConfig.signalConnect(self.buttonHelp, self, 'clicked(bool)', self.onButtonHelpClicked)
		
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonZoomIn, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonZoomOut, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonOpen, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)	
		
		self.adjustButtons()
		self.layout()
		
	def layout(self):
		box = TableCrabConfig.GridBox(self)
		box.addWidget(self.webView, 0, 0)
		box.addWidget(self.buttonBox, 1,0)
		
	def onCloseEvent(self, event):
		self.psHandGrabber.stop()
	
	def adjustButtons(self):
		self.buttonZoomIn.setEnabled(bool(self.lastHand))
		self.buttonZoomOut.setEnabled(bool(self.lastHand))
		self.buttonSave.setEnabled(bool(self.lastHand))
	
	def onButtonZoomInClicked(self, checked):
		zoomIncrement = TableCrabConfig.settingsValue('Gui/WebView/ZoomIncrement', 0.1).toDouble()[0]
		self.webView.setZoomFactor(self.webView.zoomFactor() + zoomIncrement)
		TableCrabConfig.settingsSetValue('Gui/Hand/ZoomFactor', self.webView.zoomFactor())
			
	def onButtonZoomOutClicked(self, checked):
		zoomIncrement = TableCrabConfig.settingsValue('Gui/WebView/ZoomIncrement', 0.1).toDouble()[0]
		zoom = self.webView.zoomFactor() - zoomIncrement
		if zoom > 0:
			self.webView.setZoomFactor(zoom)
			TableCrabConfig.settingsSetValue('Gui/Hand/ZoomFactor', self.webView.zoomFactor() )
	
	def onButtonOpenClicked(self, checked):
		dlg = QtGui.QFileDialog(self)
		imageFormats = [QtCore.QString(i).toLower() for i in  QtGui.QImageReader.supportedImageFormats()]
		dlg.setFileMode(dlg.AnyFile)
		dlg.setWindowTitle('Open Hand..')
		dlg.setAcceptMode(dlg.AcceptOpen)
		filters = QtCore.QStringList()
		filters << 'Html Files (*.html *.htm)'
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue('Gui/Hand/DialogOpenState', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Hand/DialogOpenState', dlg.saveState() )
		if result != dlg.Accepted: 
			return
		fileName = dlg.selectedFiles()[0]
		fp = open(fileName, 'r')
		try:	self.webView.setHtml(fp.read() )
		finally: fp.close()
		
	def onButtonSaveClicked(self, checked):
		dlg = QtGui.QFileDialog(self)
		dlg.setWindowTitle('Save Hand..')
		dlg.setFileMode(dlg.AnyFile)
		dlg.setAcceptMode(dlg.AcceptSave)
		dlg.setConfirmOverwrite(True)
		filters = QtCore.QStringList()
		filters << 'Html Files (*.html *.htm)'
		filters << 'All Files (*)'
		dlg.setNameFilters(filters)
		dlg.restoreState( TableCrabConfig.settingsValue('Gui/Hand/DialogSaveState', QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		TableCrabConfig.settingsSetValue('Gui/Hand/DialogSaveState', dlg.saveState() )
		if result != dlg.Accepted: 
			return
		fileName = dlg.selectedFiles()[0]
		fp = open(fileName, 'w')
		try: fp.write(self.webView.page().mainFrame().toHtml())
		finally: fp.close()
			
	def onPShandGrabberHandGrabbed(self, hand, data):
		self.lastHand = hand
		self.webView.setHtml(data)
		self.adjustButtons()
	
	def onConfigSettingChanged(self):
		if self.lastHand is not None:
			data = Config.psHandGrabber.handFormatter.dump(self.lastHand)
			self.webView.setHtml(data)
			
	def onButtonHelpClicked(self, checked):
		TableCrabGuiHelp.dialogHelp('hand', parent=self)

#**********************************************************************************************
#
#**********************************************************************************************
if __name__ == '__main__':
	g = TableCrabConfig.MainWindow()
	g.setCentralWidget(FrameHand(g))
	g.start()
	
