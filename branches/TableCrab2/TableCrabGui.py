
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

ErrText = '''An error occured and TableCrab may no longer work as expected.
To help improve TableCrab please send this message to:

mail: jUrner@arcor.de
subject: TableCrab-Exception

Notes: 
- make shure that there is is no personal data contained in the message
- not all errors a caught here. to help improve TableCrab take a look at "%s" from time to time.

--------------------------------------------------------------------------------------------------------
%s
'''
class DialogException(QtGui.QDialog):
	def __init__(self, info, parent=None):
		QtGui.QDialog. __init__(self, parent)
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setPlainText(ErrText % (TableCrabConfig.ErrorLogName, info) )
		self.layout()
	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.edit, 0, 0)
		grid.addWidget(TableCrabConfig.HLine(self), 1, 0)
		grid.addWidget(self.buttonBox, 2, 0)
		
class Gui(TableCrabMainWindow .MainWindow):
	
	# double clickabe label. we use this to trigger ExceptionDialog
	class MyLabel(QtGui.QLabel):
		def __init__(self, *args):
			QtGui.QLabel.__init__(self, *args)
			self.setMouseTracking(True)
		def mouseDoubleClickEvent(self, event):
			TableCrabConfig.signalEmit(self, 'doubleClicked()')
		
	def __init__(self):
		TableCrabMainWindow .MainWindow.__init__(self)
		self.lastError = None
		self.tabWidget = QtGui.QTabWidget(self)
		self.setCentralWidget(self.tabWidget)
		statusBar = self.statusBar()
		#BUG: QTBUG-5566 sizegrip is broken on windows
		statusBar.setSizeGripEnabled(False)
		self.labelStatus = QtGui.QLabel('Ready: ', self)
		statusBar.addWidget(self.labelStatus, 0)
		self.labelCurrentObject =  QtGui.QLabel('', self)
		statusBar.addWidget(self.labelCurrentObject, 0)
		self.labelCurrentObjectData = self.MyLabel('', self)
		statusBar.addWidget(self.labelCurrentObjectData, 99)
		
		self.tabWidget.addTab(TableCrabGuiSetup.FrameSetup(parent=self), 'Setup')
		self.tabWidget.addTab(TableCrabGuiHotkeys.FrameHotkeys(parent=self), 'Hotkeys')
		self.tabWidget.addTab(TableCrabGuiHand.FrameHand(parent=self), 'Hand')
		self.tabWidget.addTab(TableCrabGuiSettings.FrameSettings(parent=self), 'Settings')
		self.tabWidget.addTab(TableCrabGuiHelp.FrameHelp(parent=self), 'Help')
			
		# connect global signals
		TableCrabConfig.signalsConnect(None, self, 
				('feedbackException(QString)', self.onFeedbackException),
				('feedbackCurrentObject(QString)', self.onFeedbackCurrentObject),
				('feedbackCurrentObjectData(QString)', self.onFeedbackCurrentObjectData),
				('feedbackMessage(QString)', self.onFeedbackMessage),
				)
		
		# connect to our exception QLabel
		TableCrabConfig.signalConnect(self.labelCurrentObjectData, self, 'doubleClicked()', self.onLabelDoubleClicked)
		
		self.tabWidget.setCurrentIndex( TableCrabConfig.settingsValue('Gui/TabCurrent', QtCore.QVariant()).toInt()[0] )
		TableCrabConfig.signalConnect(None, self, 'closeEvent(QEvent*)', self.onCloseEvent)
	
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/TabCurrent', self.tabWidget.currentIndex())
	
	def onFeedbackException(self, exception):
		print repr(exception)
		# we clean exception here to make shure only relavant data is included + privacy issues for users
		self.lastError = TableCrabConfig.cleanException(exception)
		self.labelStatus.setText('Error: ')
		self.labelCurrentObjectData.setText('an error occured. double click me for details')
	
	def onFeedbackCurrentObject(self, qString):
		self.lastError = None
		self.labelStatus.setText('Ready: ')
		self.labelCurrentObject.setText(qString)
	
	def onFeedbackCurrentObjectData(self, qString):
		self.lastError = None
		self.labelStatus.setText('Ready: ')
		self.labelCurrentObjectData.setText(qString)
	
	def onFeedbackMessage(self, qString):
		self.statusBar().showMessage(qString, 3000)
		
	def onLabelDoubleClicked(self):
		if self.lastError is not None:
			dlg = DialogException(self.lastError, parent=self)
			dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogException/Geometry', QtCore.QByteArray()).toByteArray())
			dlg.exec_()
			TableCrabConfig.settingsSetValue('Gui/DialogException/Geometry', dlg.saveGeometry() )
	
#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': Gui().start()
	