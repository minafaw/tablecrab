

import TableCrabConfig
import TableCrabSiteManager

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		self._singleApplication = TableCrabConfig.SingleApplication()
			
		QtGui.QMainWindow.__init__(self)
		self.setWindowTitle(TableCrabConfig.ReleaseName)
		self.setWindowIcon( QtGui.QIcon(TableCrabConfig.Pixmaps.tableCrab()) )
		font = QtGui.QFont()
		if font.fromString(TableCrabConfig.settingsValue('Gui/Font', '').toString() ):
			QtGui.qApp.setFont(font)
		self.restoreGeometry( TableCrabConfig.settingsValue('Gui/Geometry', QtCore.QByteArray()).toByteArray() )
		self.siteManager = TableCrabSiteManager.SiteManager(parent=self)
	def show(self):
		style = TableCrabConfig.settingsValue('Gui/Style', '').toString()
		QtGui.qApp.setStyle(QtGui.QStyleFactory.create(style))
		QtGui.QMainWindow.show(self)
		TableCrabConfig.mouseHook.start()
		TableCrabConfig.keyboardHook.start()
		TableCrabConfig.windowHook.start()
		if TableCrabConfig.hotkeyManager is not None:
			TableCrabConfig.hotkeyManager.read()
		if TableCrabConfig.templateManager is not None:
			TableCrabConfig.templateManager.read()
		self.siteManager.tableCrabActionHandler().setHwndMain(self.effectiveWinId() )
	def closeEvent(self, event):
		TableCrabConfig.globalObject.closeEvent.emit(event)
		TableCrabConfig.mouseHook.stop()
		TableCrabConfig.keyboardHook.stop()
		TableCrabConfig.windowHook.stop()
		TableCrabConfig.settingsSetValue('Gui/Geometry', self.saveGeometry() )
		return QtGui.QMainWindow.closeEvent(self, event)
	def start(self):
		self.show()
		TableCrabConfig.application.exec_()
	
#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': MainWindow().start()
	