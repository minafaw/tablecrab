
import Tc2Config
import Tc2GuiSettingsCardProtector
import Tc2Win32
import Tc2ConfigHotkeys

from PyQt4 import QtGui, QtCore

#************************************************************************************
#
#************************************************************************************
class CardProtector(QtGui.QWidget):

	StyleSheet = 'background-color: %s'

	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.setWindowTitle('Card Protector')
		flags = self.windowFlags()

		flags |= QtCore.Qt.Tool
		self.setWindowFlags(flags)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		self._isInited = False

		self.scrollArea = QtGui.QScrollArea(self)
		#NOTE: kind of don't like the frame here. good idea or not?
		self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
		layout= QtGui.QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.scrollArea)
		self.scrollArea.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.label = QtGui.QLabel(self.scrollArea)
		self.scrollArea.setWidget(self.label)

		self.autoToggleTimer = QtCore.QTimer(self)
		self.autoToggleTimer.setSingleShot(True)
		self.autoToggleTimer.timeout.connect(self.onAutoToggleTimer)

		Tc2Config.globalObject.closeEvent.connect(self.closeEvent)
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		self.restoreGeometry( Tc2Config.settingsValue(Tc2GuiSettingsCardProtector.FrameSettings.SettingsKeyGeometry, QtCore.QByteArray()).toByteArray() )

	def closeEvent(self, event):
		Tc2Config.settingsSetValue(Tc2GuiSettingsCardProtector.FrameSettings.SettingsKeyGeometry, self.saveGeometry() )

	def setVisible(self, flag):
		QtGui.QWidget.setVisible(self, flag)
		if not flag or self._isInited:
			return
		self._isInited = True
		hwnd = self.effectiveWinId()
		if hwnd is None:
			raise RuntimeError('main window has no valid hwnd')
		hwnd = int(hwnd)
		Tc2Win32.windowSetTopmost(hwnd)

	def setBackgroundColor(self, color):
		if color.isValid():
			self.scrollArea.viewport().setStyleSheet(self.StyleSheet % color.name() )
		else:
			self.scrollArea.viewport().setStyleSheet('')

	def setBackgroundImage(self, pixmap):
		if pixmap.isNull():
			self.label.setPixmap(QtGui.QPixmap() )
			self.label.setScaledContents(True)
			self.label.resize(self.label.parent().size())
		else:
			self.label.setPixmap(pixmap)
			self.label.setScaledContents(False)
			self.label.resize(pixmap.size() )

	#NOTE: this gets called from TableCrabSiteHander. siteHandler blocks input events
	# in our process, we have to process our own input events in onInputEvent()
	#TODO: we do not process mose events currently. so mouse wheel does not work.
	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		if inputEvent.keyIsDown:
			if Tc2Config.globalObject.settingsCardProtector.autoToggle():
				self.setVisible(False)
				self.autoToggleTimer.start(Tc2Config.globalObject.settingsCardProtector.autoToggleTimeout() * 1000)
			else:
				self.setVisible(not self.isVisible() )
		inputEvent.accept = True

	def onInputEvent(self, inputEvent):
		hwnd = self.effectiveWinId()
		if hwnd is None:
			return
		hwnd = int(hwnd)
		if hwnd == Tc2Win32.windowForeground():
				for hotkey in Tc2Config.globalObject.hotkeyManager:
					if not hotkey.key() or hotkey.key() != inputEvent.key:
						continue
					if hotkey.id() == Tc2ConfigHotkeys.HotkeyCardProtector.id():
						self.handleInputEvent(hwnd, hotkey, inputEvent)
						break

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		globalObject.keyboardHook.inputEvent.connect(self.onInputEvent)
		self.setBackgroundColor(globalObject.settingsCardProtector.backgroundColor() )
		globalObject.settingsCardProtector.backgroundColorChanged.connect(self.setBackgroundColor)
		self.setBackgroundImage(globalObject.settingsCardProtector.backgroundImage() )
		globalObject.settingsCardProtector.backgroundImageChanged.connect(self.setBackgroundImage)
		if globalObject.settingsCardProtector.showOnStartUp():
			self.setVisible(True)

	def onAutoToggleTimer(self):
		self.setVisible(True)








