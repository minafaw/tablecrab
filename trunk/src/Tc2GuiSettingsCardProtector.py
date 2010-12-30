
import Tc2Config
import Tc2GuiHelp
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingsKeyBase = 'CardProtector'
	SettingsKeyGeometry = SettingsKeyBase + '/Geomatry'
	SettingsKeyshowOnStartUp = SettingsKeyBase + '/ShowOnStartUp'
	SettingsKeyBackgroundColor = SettingsKeyBase + '/BackgroundColor'
	SettingsKeyColorDialog = SettingsKeyBase + '/ColorDialog'

	showOnStartUpChanged = QtCore.pyqtSignal(bool)
	backgroundColorChanged = QtCore.pyqtSignal(QtGui.QColor)

	ColorButtonStyleSheet = 'background-color: %s;'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.checkshowOnStartUp = QtGui.QCheckBox('&Show on startup', self)
		self.labelBackgroundColor = QtGui.QLabel('Background color:')
		self.buttonBackgroundColor = QtGui.QPushButton(self)
		self._backgroundColor = QtGui.QColor()
		self.buttonBackgroundColorReset = QtGui.QPushButton('Reset', self)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		Tc2Config.globalObject.initSettings.connect(self.onInitSettings)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.checkshowOnStartUp).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelBackgroundColor).col(self.buttonBackgroundColor).col(self.buttonBackgroundColorReset)
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onInitSettings(self):
		self.layout()

		value = QtCore.Qt.Checked if Tc2Config.settingsValue(self.SettingsKeyshowOnStartUp, False).toBool() else QtCore.Qt.Unchecked
		self.checkshowOnStartUp.setCheckState(value)
		self.checkshowOnStartUp.stateChanged.connect(
				lambda value, self=self: self.setshowOnStartUp(self.checkshowOnStartUp.checkState() == QtCore.Qt.Checked)
				)

		value = Tc2Config.settingsValue(self.SettingsKeyBackgroundColor, '').toString()
		color = QtGui.QColor(value)
		if color.isValid():
			self.buttonBackgroundColor.setStyleSheet(self.ColorButtonStyleSheet % color.name() )
			self._backgroundColor = color
		self.buttonBackgroundColor.clicked.connect(self.onButtonBackgroundColorClicked)

		self.buttonBackgroundColorReset.clicked.connect(self.onButtonBackgroundColorResetClicked)

		Tc2Config.globalObject.objectCreatedSettingsCardProtector.emit(self)

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsCardProtector', parent=self)

	def showOnStartUp(self):
		return self.checkshowOnStartUp.checkState() == QtCore.Qt.Checked

	def setshowOnStartUp(self, value):
		Tc2Config.settingsSetValue(self.SettingsKeyshowOnStartUp, value)
		self.showOnStartUpChanged.emit(value)

	def backgroundColor(self):
		return self._backgroundColor

	def setBackgroundColor(self, color):
		if color.isValid():
			Tc2Config.settingsSetValue(self.SettingsKeyBackgroundColor, color.name() )
			self.buttonBackgroundColor.setStyleSheet(self.ColorButtonStyleSheet % color.name() )
		else:
			Tc2Config.settingsSetValue(self.SettingsKeyBackgroundColor, '')
			self.buttonBackgroundColor.setStyleSheet('')
		self._backgroundColor = color
		self.backgroundColorChanged.emit(color)

	def onButtonBackgroundColorClicked(self):
		color = QtGui.QColorDialog.getColor(self.backgroundColor(), self, 'Select background color')
		if color.isValid():
			self.setBackgroundColor(color)

	def onButtonBackgroundColorResetClicked(self):
		self.setBackgroundColor(QtGui.QColor())


