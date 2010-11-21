
import Tc2Config
import Tc2Win32
import Tc2GuiSettings
import Tc2GuiSetup
import Tc2GuiHotkeys
import Tc2GuiHandViewer
import Tc2GuiTools
import Tc2GuiHelp
import Tc2SiteManager
import Tc2DialogException

from PyQt4 import QtCore, QtGui
import sys, os

#************************************************************************************
#
#************************************************************************************
ErrMessage = '<div style="color: red;background-color: white;">&nbsp;Error: double click for details</div>'


# double clickabe label. we use this to trigger ExceptionDialog
class ClickableLabel(QtGui.QLabel):
	doubleClicked = QtCore.pyqtSignal()
	def __init__(self, *args):
		QtGui.QLabel.__init__(self, *args)
		self.setMouseTracking(True)
	def mouseDoubleClickEvent(self, event):
		self.doubleClicked.emit()

#************************************************************************************
#
#************************************************************************************
class Gui(QtGui.QMainWindow):

	SettingsKeyBase = 'Gui'
	SettingsKeyGeometry = SettingsKeyBase + '/Geometry'
	SettingsKeyTabCurrent =  SettingsKeyBase + '/TabCurrent'
	SettingsKeyDialogExceptionGeometry = SettingsKeyBase + '/DialogException/Geometry'


	def __init__(self):
		scope = Tc2Config.settingsValue(Tc2Config.SettingsKeySingleApplicationScope, '').toString()
		if scope not in Tc2Win32.SingleApplication.Scopes:
			scope = Tc2Config.SingleApplicationScopeDefault
		self.singleApplication = Tc2Win32.SingleApplication(
				Tc2Config.SingleApplicationMagicString,
				scope=scope,
				parent=None
				)
		try:
			self.singleApplication.start()
		except self.singleApplication.ErrorOtherInstanceRunning:
			raise RuntimeError('%s is already running' % Tc2Config.ApplicationName)

		QtGui.QMainWindow.__init__(self)

		self.setWindowTitle(Tc2Config.ReleaseName)
		self.setWindowIcon( QtGui.QIcon(Tc2Config.Pixmaps.tableCrab()) )
		self.restoreGeometry( Tc2Config.settingsValue(self.SettingsKeyGeometry, QtCore.QByteArray()).toByteArray() )

		self.siteManager = Tc2SiteManager.SiteManager(parent=self)

		# need to store some state data for the statusBar so we can restore on tab changes
		# error messages are displayed as longs as there is no new feedback from the current tab
		self._feedbackMessages = {	# widget/tab --> feedbackData
				None: '',		# reserved for lastError
				}

		# setup status labels
		self.labelStatus = ClickableLabel('Ready: ', self)
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
		self.tabSetup = self._addTab(Tc2GuiSetup.FrameSetup, 'Se&tup')
		self.tabHotkeys = self._addTab(Tc2GuiHotkeys.FrameHotkeys, 'Hot&keys')
		self.tabHand = self._addTab(Tc2GuiHandViewer.FrameHandViewer, 'H&and')
		self.tabTools = self._addTab(Tc2GuiTools.FrameTools, 'Too&ls')
		self.tabSettings = self._addTab(Tc2GuiSettings.FrameSettings, 'Settin&gs')
		self.tabHelp = self._addTab(Tc2GuiHelp.FrameHelp, '&Help')
		self.tabWidget.currentChanged.connect(self.onTabCurrentChanged)

		# connect global signals
		g = Tc2Config.globalObject
		g.init.connect(self.onInit)
		g.feedback.connect(self.onFeedback)
		g.feedbackException.connect(self.onFeedbackException)
		g.clearException.connect(self.onClearException)
		g.feedbackMessage.connect(self.onFeedbackMessage)
		g.settingTabPositionChanged.connect(self.onSettingTabPositionChanged)

	#--------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#--------------------------------------------------------------------------------------------------------------
	def closeEvent(self, event):
		self.singleApplication.close()
		Tc2Config.globalObject.closeEvent.emit(event)
		Tc2Config.mouseHook.stop()
		Tc2Config.keyboardHook.stop()
		Tc2Config.windowHook.stop()
		Tc2Config.settingsSetValue(self.SettingsKeyTabCurrent, self.tabWidget.currentIndex())
		Tc2Config.settingsSetValue(self.SettingsKeyGeometry, self.saveGeometry() )
		return QtGui.QMainWindow.closeEvent(self, event)

	def show(self):
		QtGui.QMainWindow.show(self)
		Tc2Config.mouseHook.start()
		Tc2Config.keyboardHook.start()
		Tc2Config.windowHook.start()
		hwnd = self.effectiveWinId()
		if hwnd is None:
			raise RuntimeError('main window has no valid hwnd')
		self.siteManager.tableCrabSiteHandler().setHwndMain( int(hwnd) )
		value = Tc2Config.settingsValue(Tc2Config.SettingsKeyTabPosition, Tc2Config.TabPositionDefault).toString()
		self.onSettingTabPositionChanged(value)
		Tc2Config.globalObject.init.emit()

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
		self._feedbackMessages[None] = Tc2Config.cleanException(exception)
		self.labelStatus.setText(ErrMessage)

	def onFeedbackMessage(self, qString):
		self.statusBar().showMessage('>>' + qString, Tc2Config.StatusBarMessageTimeout * 1000)

	def onInit(self):
		self.tabWidget.setCurrentIndex( Tc2Config.settingsValue(self.SettingsKeyTabCurrent, QtCore.QVariant()).toInt()[0] )

	def onLabelFeedbackDoubleClicked(self):
		lastError = self._feedbackMessages[None]
		if lastError:
			dlg = Tc2DialogException.DialogException(lastError, parent=self)
			dlg.restoreGeometry( Tc2Config.settingsValue(self.SettingsKeyDialogExceptionGeometry, QtCore.QByteArray()).toByteArray())
			dlg.exec_()
			Tc2Config.settingsSetValue(self.SettingsKeyDialogExceptionGeometry, dlg.saveGeometry() )

	def onTabCurrentChanged(self, index):
		if index < 0:
			return
		widget = self.tabWidget.widget(index)
		data = self._feedbackMessages[widget]
		self.labelFeedback.setText(data)

	def onSettingTabPositionChanged(self, position):
		position = self.tabWidget.South if position == Tc2Config.TabPositionBottom else self.tabWidget.North
		self.tabWidget.setTabPosition(position)

#************************************************************************************
#
#************************************************************************************
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
				Tc2Config.setSettings(QtCore.QSettings(fileName, QtCore.QSettings.IniFormat))
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

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__': main(sys.argv)


