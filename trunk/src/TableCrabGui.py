
import TableCrabConfig
import TableCrabWin32
import TableCrabGuiSettings
import TableCrabGuiSetup
import TableCrabGuiHotkeys
import TableCrabGuiHandViewer
import TableCrabGuiHelp
import TableCrabSiteManager

from PyQt4 import QtCore, QtGui
import sys, os, re, base64

#*******************************************************************************************
#
#*******************************************************************************************
ErrMessage = '<div style="color: red;background-color: white;">&nbsp;Error: double click for details</div>'
ErrText = '''An error occured and TableCrab may no longer work as expected.
To help improve TableCrab please send this message to:

mail: jUrner@arcor.de
subject: %s-Error

Notes:
- make shure that there is is no personal data contained in the message below
- not all errors a caught here. to help improve TableCrab take a look at "%s" from time to time.

--------------------------------------------------------------------------------------------------------
%s
'''
class DialogException(QtGui.QDialog):

	ImagePat = re.compile('.*(?<=$|\n)\<image\>(.+?)\<\/image\>', re.X|re.M|re.S)

	def __init__(self, info, parent=None):
		"""
		@param info: (str) err to display. may contain one base64 encoded image wrapped in <image> tags
		"""
		QtGui.QDialog. __init__(self, parent)

		self.setWindowTitle('%s - Error' % TableCrabConfig.ApplicationName)
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		self.buttonBox.accepted.connect(self.accept)

		self.buttonClearError = QtGui.QPushButton('Clear Error', self)
		self.buttonClearError.setToolTip('Clear error message in main window (Ctrl+L)')
		self.buttonClearError.clicked.connect(self.onClearError)
		self.buttonBox.addButton(self.buttonClearError, self.buttonBox.ActionRole)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+L'))
		action.triggered.connect(self.onClearError)
		self.addAction(action)

		info, pixmap = self.embeddedImage(info)
		self.labelPixmap = None
		self.labelPixmapName = None
		if pixmap is not None:
			self.labelPixmapName = QtGui.QLabel('Image:', self)
			self.labelPixmap = QtGui.QLabel(self)
			self.labelPixmap.setPixmap(pixmap)

		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setPlainText(ErrText % (TableCrabConfig.ApplicationName, TableCrabConfig.ErrorLogName, info) )

		self.layout()

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.addWidget(self.edit, 0, 0)
		n = 1
		if self.labelPixmap is not None:
			grid.addWidget(self.labelPixmapName, 1, 0)
			grid.addWidget(self.labelPixmap, 2, 0)
			n = 3
		grid.addWidget(TableCrabConfig.HLine(self), n+1, 0)
		grid.addWidget(self.buttonBox, n+2, 0)

	def embeddedImage(self, info):
		pixmap = None
		match = self.ImagePat.match(info)
		if match is not None:
			tmp_pixmap = QtGui.QPixmap()
			data = match.group(1)
			data = base64.b64decode(data)
			#info = info.replace(data, repr(data))
			if tmp_pixmap.loadFromData(data):
				pixmap = tmp_pixmap
		return info, pixmap

	def onClearError(self, *args):
		TableCrabConfig.globalObject.clearException.emit()
		self.buttonClearError.setEnabled(False)

#*******************************************************************************************
#
#*******************************************************************************************
class Gui(QtGui.QMainWindow):

	# double clickabe label. we use this to trigger ExceptionDialog
	class ClickableLabel(QtGui.QLabel):
		doubleClicked = QtCore.pyqtSignal()
		def __init__(self, *args):
			QtGui.QLabel.__init__(self, *args)
			self.setMouseTracking(True)
		def mouseDoubleClickEvent(self, event):
			self.doubleClicked.emit()

	def __init__(self):
		scope = TableCrabConfig.settingsValue('Gui/SingleApplication/Scope', '').toString()
		if scope not in TableCrabWin32.SingleApplication.Scopes:
			scope = TableCrabConfig.SingleApplicationScopeDefault
		self.singleApplication = TableCrabWin32.SingleApplication(
				TableCrabConfig.SingleApplicationMagicString,
				scope=scope,
				parent=None
				)
		try:
			self.singleApplication.start()
		except self.singleApplication.ErrorOtherInstanceRunning:
			#TODO: give feedback here, usual stuff like bring other to top, flash window, whatevs
			#			x. FlashWindow() does not work in wine
			# 			x. FlashWindowEx() is not implemented in wine
			#			x. in wine there is no way to put a window to the foreground
			# none of the above is save anyways. only way to make this a bit more secure would
			# be to start a conversation via WM_COPYDATA, trying to find out who is holding the mutex.
			# i'd say ..not worth the efford.
			raise RuntimeError('%s is already running' % TableCrabConfig.ApplicationName)

		QtGui.QMainWindow.__init__(self)

		self.setWindowTitle(TableCrabConfig.ReleaseName)
		self.setWindowIcon( QtGui.QIcon(TableCrabConfig.Pixmaps.tableCrab()) )
		self.restoreGeometry( TableCrabConfig.settingsValue('Gui/Geometry', QtCore.QByteArray()).toByteArray() )

		self.siteManager = TableCrabSiteManager.SiteManager(parent=self)

		# need to store some state data for the statusBar so we can restore on tab changes
		# error messages are displayed as longs as there is no new feedback from the current tab
		self._feedbackMessages = {	# widget/tab --> feedbackData
				None: '',		# reserved for lastError
				}

		# setup status labels
		self.labelStatus = self.ClickableLabel('Ready: ', self)
		self.labelStatus.setTextFormat(QtCore.Qt.RichText)
		self.labelStatus.doubleClicked.connect(self.onLabelFeedbackDoubleClicked)
		self.labelFeedback = QtGui.QLabel('', self)

		# setup StatusBar
		statusBar = self.statusBar()
		#BUG: QTBUG-5566 sizegrip is broken on windows
		statusBar.setSizeGripEnabled(False)
		statusBar.addWidget(self.labelStatus, 0)
		statusBar.addWidget(self.labelFeedback, 99)

		# setup tabs
		self.tabWidget = QtGui.QTabWidget(self)
		self.setCentralWidget(self.tabWidget)
		self.tabSetup = self._addTab(TableCrabGuiSetup.FrameSetup, 'Se&tup')
		self.tabHotkeys = self._addTab(TableCrabGuiHotkeys.FrameHotkeys, 'Hot&keys')
		self.tabHand = self._addTab(TableCrabGuiHandViewer.FrameHandViewer, 'H&and')
		self.tabSettings = self._addTab(TableCrabGuiSettings.FrameSettings, 'Settin&gs')
		self.tabHelp = self._addTab(TableCrabGuiHelp.FrameHelp, '&Help')
		self.tabWidget.currentChanged.connect(self.onTabCurrentChanged)

		# connect global signals
		g = TableCrabConfig.globalObject
		g.init.connect(self.onInit)
		g.feedback.connect(self.onFeedback)
		g.feedbackException.connect(self.onFeedbackException)
		g.clearException.connect(self.onClearException)
		g.feedbackMessage.connect(self.onFeedbackMessage)

	#--------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#--------------------------------------------------------------------------------------------------------------
	def closeEvent(self, event):
		self.singleApplication.close()
		TableCrabConfig.globalObject.closeEvent.emit(event)
		TableCrabConfig.mouseHook.stop()
		TableCrabConfig.keyboardHook.stop()
		TableCrabConfig.windowHook.stop()
		TableCrabConfig.settingsSetValue('Gui/TabCurrent', self.tabWidget.currentIndex())
		TableCrabConfig.settingsSetValue('Gui/Geometry', self.saveGeometry() )
		return QtGui.QMainWindow.closeEvent(self, event)

	def show(self):
		QtGui.QMainWindow.show(self)
		TableCrabConfig.mouseHook.start()
		TableCrabConfig.keyboardHook.start()
		TableCrabConfig.windowHook.start()
		hwnd = self.effectiveWinId()
		if hwnd is None:
			raise RuntimeError('main window has no valid hwnd')
		self.siteManager.tableCrabActionHandler().setHwndMain( int(hwnd) )
		TableCrabConfig.globalObject.init.emit()

	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def _addTab(self, widgetProto, name):
		widget = widgetProto(parent=self)
		self.tabWidget.addTab(widget, name)
		self._feedbackMessages[widget] = ''
		return widget

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onClearException(self):
		self._feedbackMessages[None] = ''
		self.labelStatus.setText('Ready: ')

	def onFeedback(self, widget, string):
		#find tab widget
		tab = None
		while True:
			if self.tabWidget.indexOf(widget) > -1:
				tab = widget
				break
			widget = widget.parent()
			if widget is None: break
		if tab is None:
			raise ValueError('widget is not on one of our tabs')
		# store data for tab changes
		self._feedbackMessages[tab] = string
		if tab is self.tabWidget.currentWidget():
			# set message to statusBar
			self.labelFeedback.setText(string)

	def onFeedbackException(self, exception):
		#NOTE: we assume "exception" is never empty string
		self._feedbackMessages[None] = TableCrabConfig.cleanException(exception)
		self.labelStatus.setText(ErrMessage)

	def onFeedbackMessage(self, qString):
		self.statusBar().showMessage('>>' + qString, TableCrabConfig.StatusBarMessageTimeout * 1000)

	def onInit(self):
		self.tabWidget.setCurrentIndex( TableCrabConfig.settingsValue('Gui/TabCurrent', QtCore.QVariant()).toInt()[0] )

	def onLabelFeedbackDoubleClicked(self):
		lastError = self._feedbackMessages[None]
		if lastError:
			dlg = DialogException(lastError, parent=self)
			dlg.restoreGeometry( TableCrabConfig.settingsValue('Gui/DialogException/Geometry', QtCore.QByteArray()).toByteArray())
			dlg.exec_()
			TableCrabConfig.settingsSetValue('Gui/DialogException/Geometry', dlg.saveGeometry() )

	def onTabCurrentChanged(self, index):
		if index < 0:
			return
		widget = self.tabWidget.widget(index)
		data = self._feedbackMessages[widget]
		self.labelFeedback.setText(data)

#*******************************************************************************************
#
#*******************************************************************************************
def main(argv=None, run=True):
	argv = [] if argv is None else argv
	if '--config' in argv:
		i = argv.index('--config')
		del argv[i]
		try:
			fileName = argv[i]
		except IndexError:
			raise ValueError('Option --config present but no config file specified')
		else:
			del argv[i]
			if os.path.isfile(fileName) or os.path.islink(fileName):
				TableCrabConfig.setSettings(QtCore.QSettings(fileName, QtCore.QSettings.IniFormat))
			else:
				raise ValueError('No such config file: %s' % fileName)

	application = QtGui.QApplication(argv)
	#TODO: StatusBar seems to be no way to have first label without frame
	application.setStyleSheet("QStatusBar::item{ border: 0px solid black }; ")
	gui = Gui()
	gui.show()
	if run:
		application.exec_()
	else:
		return gui

#*******************************************************************************************
#
#*******************************************************************************************
if __name__ == '__main__': main(sys.argv)


