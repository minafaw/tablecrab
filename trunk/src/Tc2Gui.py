
import Tc2Config
import Tc2Win32
import Tc2GuiSettings
import Tc2GuiSetup
import Tc2GuiHotkeys
import Tc2GuiHandViewer
import Tc2GuiTools
import Tc2GuiToolsClock
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

	settingGeometry = Tc2Config.settings2.ByteArray(
			'Gui/Geometry',
			defaultValue=QtCore.QByteArray()
			)
	settingTabCurrent = Tc2Config.settings2.Index(
			'Gui/TabCurrent',
			defaultValue=0
			)
	settingDialogExceptionGeometry = Tc2Config.settings2.ByteArray(
			'Gui/DialogException/Geometry',
			defaultValue=QtCore.QByteArray()
			)

	def __init__(self):
		#NOTE: have to init setting here
		setting = Tc2Config.settings2['Gui/SingleApplication/Scope']
		setting.init()
		self.singleApplication = Tc2Win32.SingleApplication(
				Tc2Config.SingleApplicationMagicString,
				scope=setting.value(),
				parent=None
				)
		try:
			self.singleApplication.start()
		except self.singleApplication.ErrorOtherInstanceRunning:
			raise RuntimeError('%s is already running' % Tc2Config.ApplicationName)

		QtGui.QMainWindow.__init__(self)

		#NOTE: have to use our own timer to not have messages cover our clock
		self._statusMessageTimer = QtCore.QTimer(self)
		self._statusMessageTimer.setSingleShot(True)
		self._statusMessageTimer.timeout.connect(self.onStatusBarTimer)

		self.setWindowTitle(Tc2Config.ReleaseName)
		self.setWindowIcon( QtGui.QIcon(Tc2Config.Pixmaps.tableCrab()) )

		self._siteManager = Tc2SiteManager.SiteManager(parent=self)

		# need to store some state data for the statusBar so we can restore on tab changes
		# error messages are displayed as longs as there is no new feedback from the current tab
		self._feedbackMessages = {	# widget/tab --> feedbackData
				None: '',		# reserved for lastError
				}

		# setup status labels
		self._labelClock = Tc2GuiToolsClock.ClockLabel(parent=self)
		self._labelStatus = ClickableLabel('Ready: ', self)
		self._labelStatus.setTextFormat(QtCore.Qt.RichText)
		self._labelStatus.doubleClicked.connect(self.onLabelFeedbackDoubleClicked)
		self.labelFeedback = QtGui.QLabel('', self)

		# setup StatusBar
		statusBar = self.statusBar()
		#BUG: QTBUG-5566 sizegrip is broken on windows
		statusBar.setSizeGripEnabled(False)
		statusBar.addWidget(self._labelClock, 0)
		statusBar.addWidget(self._labelStatus, 0)
		statusBar.addWidget(self.labelFeedback, 99)

		# setup tabs
		self._tabWidget = QtGui.QTabWidget(self)
		self.setCentralWidget(self._tabWidget)
		self._tabSetup = self._addTab(Tc2GuiSetup.FrameSetup, 'Se&tup')
		self._tabHotkeys = self._addTab(Tc2GuiHotkeys.FrameHotkeys, 'Hot&keys')
		self._tabHand = self._addTab(Tc2GuiHandViewer.FrameHandViewer, 'H&and')
		self._tabTools = self._addTab(Tc2GuiTools.FrameTools, 'Too&ls')
		self._tabSettings = self._addTab(Tc2GuiSettings.FrameSettings, 'Settin&gs')
		self._tabHelp = self._addTab(Tc2GuiHelp.FrameHelp, '&Help')
		self._tabWidget.currentChanged.connect(self.onTabCurrentChanged)

		# connect global signals
		g = Tc2Config.globalObject
		g.feedback.connect(self.onFeedback)
		g.feedbackException.connect(self.onFeedbackException)
		g.clearException.connect(self.onClearException)
		g.feedbackMessage.connect(self.onFeedbackMessage)
		g.guiInit.connect(self.onInitGui)
		Tc2Config.settings2['Gui/Tab/Position'].changed.connect(self.onSettingTabPositionChanged)

	#--------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#--------------------------------------------------------------------------------------------------------------
	def closeEvent(self, event):
		self.singleApplication.close()
		Tc2Config.globalObject.closeEvent.emit(event)
		Tc2Config.globalObject.mouseHook.stop()
		Tc2Config.globalObject.keyboardHook.stop()
		Tc2Config.globalObject.windowHook.stop()

		self.settingGeometry.setValue(self.saveGeometry())
		return QtGui.QMainWindow.closeEvent(self, event)

	def show(self):
		QtGui.QMainWindow.show(self)
		Tc2Config.globalObject.initSettings.emit()
		Tc2Config.globalObject.objectCreatedMainWindow.emit(self)
		Tc2Config.globalObject.initSettingsFinished.emit(Tc2Config.globalObject)
		#
		Tc2Config.globalObject.mouseHook.start()
		Tc2Config.globalObject.keyboardHook.start()
		Tc2Config.globalObject.windowHook.start()
		#
		Tc2Config.globalObject.guiInitFinished.emit(Tc2Config.globalObject)

		# ##################################
		Tc2Config.globalObject.guiInit.emit()
		Tc2Config.cleanSettings()
		Tc2Config.settings2.init()
		Tc2Config.globalObject.guiInited.emit()


	#--------------------------------------------------------------------------------------------------------------
	# methods
	#--------------------------------------------------------------------------------------------------------------
	def _addTab(self, widgetProto, name):
		widget = widgetProto(parent=self)
		self._tabWidget.addTab(widget, name)
		self._feedbackMessages[widget] = ''
		return widget

	def siteManager(self):
		return self._siteManager

	def tabSettings(self):
		return self._tabSettings

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onClearException(self):
		self._feedbackMessages[None] = ''
		self._labelStatus.setText('Ready: ')

	def onFeedback(self, widget, string):
		#find tab widget
		tab = None
		while True:
			if self._tabWidget.indexOf(widget) > -1:
				tab = widget
				break
			widget = widget.parent()
			if widget is None: break
		if tab is None:
			raise ValueError('widget is not on one of our tabs')
		# store data for tab changes
		self._feedbackMessages[tab] = string
		if tab is self._tabWidget.currentWidget():
			# set message to statusBar
			self.labelFeedback.setText(string)

	def onFeedbackException(self, exception):
		#NOTE: we assume "exception" is never empty string
		self._feedbackMessages[None] = Tc2Config.cleanException(exception)
		self._labelStatus.setText(ErrMessage)

	def onFeedbackMessage(self, qString):
		self.labelFeedback.setText('>>' + qString)
		self._statusMessageTimer.start(Tc2Config.StatusBarMessageTimeout * 1000)

	def onInitGui(self):
		self.settingGeometry.changed.connect(
				lambda setting: self.restoreGeometry(setting.value())
				)
		self.settingTabCurrent.setTabWidget(self._tabWidget)

	def onLabelFeedbackDoubleClicked(self):
		lastError = self._feedbackMessages[None]
		if lastError:
			dlg = Tc2DialogException.DialogException(lastError, parent=self)
			dlg.restoreGeometry(self.settingDialogExceptionGeometry.value())
			dlg.exec_()
			self.settingDialogExceptionGeometry.setValue(dlg.saveGeometry())

	def onSettingTabPositionChanged(self, setting):
		position = self._tabWidget.South if setting.value()  == Tc2Config.TabPositionBottom else self._tabWidget.North
		self._tabWidget.setTabPosition(position)

	def onTabCurrentChanged(self, index):
		if index < 0:
			return
		widget = self._tabWidget.widget(index)
		data = self._feedbackMessages[widget]
		self.labelFeedback.setText(data)

	def onStatusBarTimer(self):
		tab = self._tabWidget.currentWidget()
		lastFeedback = self._feedbackMessages.get(tab, '')
		self.labelFeedback.setText(lastFeedback)

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
				qSettings= QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
				Tc2Config.setSettings(qSettings)
				Tc2Config.settings2.setSettings(qSettings)
			else:
				raise ValueError('No such config file: %s' % fileName)

	application = QtGui.QApplication(argv)
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


