
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
		Tc2Config.globalObject.closeEvent.connect(self.closeEvent)
		Tc2Config.keyboardHook.inputEvent.connect(self.onInputEvent)

		self.restoreGeometry( Tc2Config.settingsValue(Tc2GuiSettingsCardProtector.FrameSettings.SettingsKeyGeometry, QtCore.QByteArray()).toByteArray() )
		if Tc2Config.globalObject.settingsCardProtector.showOnStartUp():
			self.setVisible(True)

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
		self.setBackgroundColor(Tc2Config.globalObject.settingsCardProtector.backgroundColor() )
		Tc2Config.globalObject.settingsCardProtector.backgroundColorChanged.connect(self.setBackgroundColor)

	def setBackgroundColor(self, color):
		if color.isValid():
			self.setStyleSheet(self.StyleSheet % color.name() )
		else:
			self.setStyleSheet('')

	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		if inputEvent.keyIsDown:
			self.setVisible(not self.isVisible() )
		inputEvent.accept = True

	def onInputEvent(self, inputEvent):
		hwnd = int(self.effectiveWinId())
		if hwnd == Tc2Win32.windowForeground():
				for hotkey in Tc2Config.hotkeyManager:
					if not hotkey.key() or hotkey.key() != inputEvent.key:
						continue
					if hotkey.id() == Tc2ConfigHotkeys.HotkeyCardProtector.id():
						self.handleInputEvent(hwnd, hotkey, inputEvent)
						break







