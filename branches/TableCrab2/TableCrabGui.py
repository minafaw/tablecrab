
import TableCrabConfig
from PyQt4 import QtCore, QtGui

import TableCrabGuiSettings
import TableCrabGuiWidgets
import TableCrabGuiHotkeys
import TableCrabGuiHand
import TableCrabGuiHelp

#**********************************************************************************************
#
#**********************************************************************************************
class Gui(TableCrabConfig.MainWindow):
	def __init__(self):
		TableCrabConfig.MainWindow.__init__(self)
		self.tabWidget = QtGui.QTabWidget(self)
		self.setCentralWidget(self.tabWidget)
		
		self.tabWidget.addTab(TableCrabGuiWidgets.FrameWidgets(parent=self), 'Widgets')
		self.tabWidget.addTab(TableCrabGuiHotkeys.FrameHotkeys(parent=self), 'Hotkeys')
		self.tabWidget.addTab(TableCrabGuiHand.FrameHand(parent=self), 'Hand')
		self.tabWidget.addTab(TableCrabGuiSettings.FrameSettings(parent=self), 'Settings')
		self.tabWidget.addTab(TableCrabGuiHelp.FrameHelp(parent=self), 'Help')
			
		self.tabWidget.setCurrentIndex( TableCrabConfig.settingsValue('Gui/TabCurrent', QtCore.QVariant()).toInt()[0] )
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/TabCurrent', self.tabWidget.currentIndex())
	
#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': Gui().start()
	