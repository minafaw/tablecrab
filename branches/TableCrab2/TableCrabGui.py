
import TableCrabConfig
from PyQt4 import QtCore, QtGui

import TableCrabGuiSettings
import TableCrabGuiSetup
import TableCrabGuiHotkeys
import TableCrabGuiHand
import TableCrabGuiHelp

#**********************************************************************************************
#
#**********************************************************************************************
#TODO: there seems to be no way to set the first label on status bar without frame
TableCrabConfig.application.setStyleSheet("QStatusBar::item { border: 0px solid black }; ")

class Gui(TableCrabConfig.MainWindow):
	def __init__(self):
		TableCrabConfig.MainWindow.__init__(self)
		self.tabWidget = QtGui.QTabWidget(self)
		self.setCentralWidget(self.tabWidget)
		statusBar = self.statusBar()
		#BUG: QTBUG-5566 sizegrip is broken on windows
		statusBar.setSizeGripEnabled(False)
		self.labelStatus = QtGui.QLabel('Ready: ', self)
		statusBar.addWidget(self.labelStatus, 0)
		self.labelMessage = QtGui.QLabel('', self)
		statusBar.addWidget(self.labelMessage, 99)
		
		self.tabWidget.addTab(TableCrabGuiSetup.FrameSetup(parent=self), 'Setup')
		self.tabWidget.addTab(TableCrabGuiHotkeys.FrameHotkeys(parent=self), 'Hotkeys')
		self.tabWidget.addTab(TableCrabGuiHand.FrameHand(parent=self), 'Hand')
		self.tabWidget.addTab(TableCrabGuiSettings.FrameSettings(parent=self), 'Settings')
		self.tabWidget.addTab(TableCrabGuiHelp.FrameHelp(parent=self), 'Help')
			
		TableCrabConfig.signalConnect(None, self, 'feedbackException()', self.onFeedbackException)
		TableCrabConfig.signalConnect(None, self, 'feedbackMessage(QString)', self.onFeedbackMessage)
		
		self.tabWidget.setCurrentIndex( TableCrabConfig.settingsValue('Gui/TabCurrent', QtCore.QVariant()).toInt()[0] )
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/TabCurrent', self.tabWidget.currentIndex())
	def onFeedbackException(self):
		self.labelStatus.setText('Error: ')
		#TODO: user checks errlog (if he finds it) and is lost from there on
		self.labelMessage.setText('an error occured. check "%s" for details' % TableCrabConfig.TableCrabErrorLogName)
	
	def onFeedbackMessage(self, qString):
		self.labelStatus.setText('Ready: ')
		#TODO: user checks errlog (if he finds it) and is lost from there on
		self.labelMessage.setText(qString)
		
	
#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': Gui().start()
	