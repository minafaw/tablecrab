
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
subject: %s-Error

Notes: 
- make shure that there is is no personal data contained in the message
- not all errors a caught here. to help improve TableCrab take a look at "%s" from time to time.

--------------------------------------------------------------------------------------------------------
%s
'''
class DialogException(QtGui.QDialog):
	def __init__(self, info, parent=None):
		QtGui.QDialog. __init__(self, parent)
		self.setWindowTitle('%s - Error' % TableCrabConfig.ApplicationName)
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		TableCrabConfig.signalConnect(self.buttonBox, self, 'accepted()', self.accept)
		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setPlainText(ErrText % (TableCrabConfig.ApplicationName, TableCrabConfig.ErrorLogName, info) )
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
		
		# need to store some state data for the statusBar so we can restore on tab changes
		# error messages are displayed as longs as there is no new feedback from the current tab
		self._feedbackMessages = {	# widget/tab --> {'currentObject': str, 'objectData': str}
				None: {'lastError': ''},	# reserved for lastError
				}		
			
		# setup StatusBar
		statusBar = self.statusBar()
		#BUG: QTBUG-5566 sizegrip is broken on windows
		statusBar.setSizeGripEnabled(False)
		self.labelStatus = QtGui.QLabel('Ready: ', self)
		statusBar.addWidget(self.labelStatus, 0)
		self.labelCurrentObject =  QtGui.QLabel('', self)
		statusBar.addWidget(self.labelCurrentObject, 0)
		self.labelCurrentObjectData = self.MyLabel('', self)
		statusBar.addWidget(self.labelCurrentObjectData, 99)
		
		# setup TabWidget
		self.tabWidget = QtGui.QTabWidget(self)
		self.setCentralWidget(self.tabWidget)
		for widgetProto, name in (
					(TableCrabGuiSetup.FrameSetup, 'Setup'),
					(TableCrabGuiHotkeys.FrameHotkeys, 'Hotkeys'),
					(TableCrabGuiHand.FrameHand, 'Hand'),
					(TableCrabGuiSettings.FrameSettings, 'Settings'),
					(TableCrabGuiHelp.FrameHelp, 'Help'),
					):
			self._addTab(widgetProto, name)
				
		# connect global signals
		TableCrabConfig.signalsConnect(None, self, 
				('closeEvent(QEvent*)', self.onCloseEvent),
				('feedbackException(QString)', self.onFeedbackException),
				('feedbackCurrentObject(QString)', self.onFeedbackCurrentObject),
				('feedbackCurrentObjectData(QString)', self.onFeedbackCurrentObjectData),
				('feedbackMessage(QString)', self.onFeedbackMessage),
				)
		
		# connect to our double clickable label label
		TableCrabConfig.signalConnect(self.labelCurrentObjectData, self, 'doubleClicked()', self.onLabelDoubleClicked)
		
		# connect to TabWidget
		TableCrabConfig.signalConnect(self.tabWidget, self, 'currentChanged(int)', self.onTabCurrentChanged)
		
		# restore last selected tab
		self.tabWidget.setCurrentIndex( TableCrabConfig.settingsValue('Gui/TabCurrent', QtCore.QVariant()).toInt()[0] )
		
	def _addTab(self, widgetProto, name):
		widget = widgetProto(parent=self)
		self.tabWidget.addTab(widget, name)
		self._feedbackMessages[widget] = {'currentObject': '', 'objectData': ''}
	
	def onCloseEvent(self, event):
		TableCrabConfig.settingsSetValue('Gui/TabCurrent', self.tabWidget.currentIndex())
	
	def onTabCurrentChanged(self, index):
		if index < 0:
			return
		# check if we got an error to display
		if self._feedbackMessages[None]['lastError']:
			pass
		else:
			widget = self.tabWidget.widget(index)
			data = self._feedbackMessages[widget]
			self.labelCurrentObject.setText(data['currentObject'])
			self.labelCurrentObjectData.setText(data['objectData'])
		
	def onFeedbackException(self, exception):
		#NOTE: we assume "exception" is never empty string
		# clean exception here to make shure only relavant data is included + privacy issues for users
		self._feedbackMessages[None]['lastError'] = TableCrabConfig.cleanException(exception)
		self.labelStatus.setText('Error: ')
		# hide label CurrentObject so it does not interfere with the error message
		self.labelCurrentObject.setVisible(False)
		self.labelCurrentObjectData.setText('an error occured. double click me for details')
	
	def onFeedbackCurrentObject(self, qString):
		# clear last error
		self._feedbackMessages[None]['lastError'] = ''
		# store data for tab changes
		widget = self.tabWidget.currentWidget()
		data = self._feedbackMessages[widget]
		data['currentObject'] = qString
		# set message to statusBar
		self.labelStatus.setText('Ready: ')
		self.labelCurrentObject.setVisible(True)
		self.labelCurrentObject.setText(qString)
	
	def onFeedbackCurrentObjectData(self, qString):
		# clear last error
		self._feedbackMessages[None]['lastError'] = ''
		# store data for tab changes
		widget = self.tabWidget.currentWidget()
		data = self._feedbackMessages[widget]
		data['objectData'] = qString
		# set message to statusBar
		self.labelStatus.setText('Ready: ')
		self.labelCurrentObject.setVisible(True)
		self.labelCurrentObjectData.setText(qString)
	
	def onFeedbackMessage(self, qString):
		self.statusBar().showMessage(qString, 3000)
		
	def onLabelDoubleClicked(self):
		lastError = self._feedbackMessages[None]['lastError']
		if lastError:
			dlg = DialogException(lastError, parent=self)
			dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogException/Geometry', QtCore.QByteArray()).toByteArray())
			dlg.exec_()
			TableCrabConfig.settingsSetValue('Gui/DialogException/Geometry', dlg.saveGeometry() )
	
#***********************************************************************************
#
#***********************************************************************************
if __name__ == '__main__': Gui().start()
	