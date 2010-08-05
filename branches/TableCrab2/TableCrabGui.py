
import TableCrabConfig
import TableCrabMainWindow 
import TableCrabGuiSettings
import TableCrabGuiSetup
import TableCrabGuiHotkeys
import TableCrabGuiHand
import TableCrabGuiHelp

from PyQt4 import QtCore, QtGui

#**********************************************************************************************
#
#**********************************************************************************************
#TODO: there seems to be no way to set the first label on status bar without frame
TableCrabConfig.application.setStyleSheet("QStatusBar::item { border: 0px solid black }; ")

class Gui(TableCrabMainWindow .MainWindow):
	def __init__(self):
		TableCrabMainWindow .MainWindow.__init__(self)
		self.tabWidget = QtGui.QTabWidget(self)
		self.setCentralWidget(self.tabWidget)
		statusBar = self.statusBar()
		#BUG: QTBUG-5566 sizegrip is broken on windows
		statusBar.setSizeGripEnabled(False)
		self.labelStatus = QtGui.QLabel('Ready: ', self)
		statusBar.addWidget(self.labelStatus, 0)
		self.labelCurrentObject = QtGui.QLabel('', self)
		statusBar.addWidget(self.labelCurrentObject, 0)
		self.labelCurrentObjectData = QtGui.QLabel('', self)
		statusBar.addWidget(self.labelCurrentObjectData, 99)
		
		self.tabWidget.addTab(TableCrabGuiSetup.FrameSetup(parent=self), 'Setup')
		self.tabWidget.addTab(TableCrabGuiHotkeys.FrameHotkeys(parent=self), 'Hotkeys')
		self.tabWidget.addTab(TableCrabGuiHand.FrameHand(parent=self), 'Hand')
		self.tabWidget.addTab(TableCrabGuiSettings.FrameSettings(parent=self), 'Settings')
		self.tabWidget.addTab(TableCrabGuiHelp.FrameHelp(parent=self), 'Help')
			
		TableCrabConfig.signalConnect(None, self, 'feedbackException()', self.onFeedbackException)
		TableCrabConfig.signalConnect(None, self, 'feedbackCurrentObject(QString)', self.onFeedbackCurrentObject)
		TableCrabConfig.signalConnect(None, self, 'feedbackCurrentObjectData(QString)', self.onFeedbackCurrentObjectData)
		TableCrabConfig.signalConnect(None, self, 'feedbackMessage(QString)', self.onFeedbackMessage)
		
		self.tabWidget.setCurrentIndex( TableCrabConfig.settingsValue('Gui/TabCurrent', QtCore.QVariant()).toInt()[0] )
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/TabCurrent', self.tabWidget.currentIndex())
	def onFeedbackException(self):
		self.labelStatus.setText('Error: ')
		#TODO: user checks errlog (if he finds it) and is lost from there on
		self.labelCurrentObjectData.setText('an error occured. check "%s" for details' % TableCrabConfig.ErrorLogName)
	
	def onFeedbackCurrentObject(self, qString):
		self.labelStatus.setText('Ready: ')
		self.labelCurrentObject.setText(qString)
	
	def onFeedbackCurrentObjectData(self, qString):
		self.labelStatus.setText('Ready: ')
		self.labelCurrentObjectData.setText(qString)
	
	def onFeedbackMessage(self, qString):
		self.statusBar().showMessage(qString, 2000)		
	

#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': Gui().start()
	