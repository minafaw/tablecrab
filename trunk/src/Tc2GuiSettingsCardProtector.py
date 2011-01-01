
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
	SettingsKeyBackgroundImage = SettingsKeyBase + '/BackgroundImage'
	SettingsKeyDialogOpenImageState = SettingsKeyBase + '/DialogOpenImage'

	showOnStartUpChanged = QtCore.pyqtSignal(bool)
	backgroundColorChanged = QtCore.pyqtSignal(QtGui.QColor)
	backgroundImageChanged = QtCore.pyqtSignal(QtGui.QPixmap)

	ColorButtonStyleSheet = 'background-color: %s;'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.checkshowOnStartUp = QtGui.QCheckBox('&Show on startup', self)

		self.labelBackgroundColor = QtGui.QLabel('Background color:')
		self.buttonBackgroundColor = QtGui.QPushButton(self)
		self._backgroundColor = QtGui.QColor()
		self.buttonBackgroundColorReset = QtGui.QPushButton('Reset', self)

		self.labelBackgroundImage = QtGui.QLabel('Background image:')
		self.buttonBackgroundImage = QtGui.QPushButton(self)
		self._backgroundImage = QtGui.QPixmap()
		self.buttonBackgroundImageReset = QtGui.QPushButton('Reset', self)

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
		grid.col(self.labelBackgroundImage).col(self.buttonBackgroundImage).col(self.buttonBackgroundImageReset)
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

		value = Tc2Config.settingsValue(self.SettingsKeyBackgroundImage, '').toString()
		if value:
			fileName, pixmap = self.imageFromFileName(value)
			self.setBackgroundImage(fileName, pixmap)
		else:
			self.setBackgroundImage(None, QtGui.QPixmap() )
		self.buttonBackgroundImage.clicked.connect(self.onButtonBackgroundImageClicked)
		self.buttonBackgroundImageReset.clicked.connect(self.onButtonBackgroundImageResetClicked)

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

	def backgroundImage(self):
		return self._backgroundImage

	def setBackgroundImage(self, fileName, pixmap):
		if fileName is not None:
			fileInfo = QtCore.QFileInfo(fileName)
			imageName = fileInfo.fileName()
			imageName = Tc2Config.truncateString(imageName, Tc2Config.MaxDisplayFileName)
			Tc2Config.settingsSetValue(self.SettingsKeyBackgroundImage, fileName)
			self.buttonBackgroundImage.setText(imageName)
		else:
			Tc2Config.settingsSetValue(self.SettingsKeyBackgroundImage, '')
			self.buttonBackgroundImage.setText('...')
		self._backgroundImage = pixmap
		self.backgroundImageChanged.emit(pixmap)

	def onButtonBackgroundImageClicked(self):
		imageFormats = Tc2Config.readWriteImageFormats()
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Background Image..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				settingsKey=self.SettingsKeyDialogOpenImageState,
				)
		if fileName is None:
			return
		imageName, pixmap = self.imageFromFileName(fileName)
		if imageName is None:
			Tc2Config.msgWarning(self, 'Could not open background image')
			return
		self.setBackgroundImage(imageName, pixmap)

	def onButtonBackgroundImageResetClicked(self):
		self.setBackgroundImage(None, QtGui.QPixmap() )

	def imageFromFileName(self, fileName):
		pixmap = QtGui.QPixmap()
		if not pixmap.load(fileName):
			return (None, pixmap)
		return (fileName, pixmap)




