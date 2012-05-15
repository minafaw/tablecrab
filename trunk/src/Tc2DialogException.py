
import Tc2Config
from PyQt4 import QtCore, QtGui

import base64, re

#************************************************************************************
#
#************************************************************************************
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

	settingDialogSaveImageState = Tc2Config.settings2.ByteArray(
			'Gui/Dialogs/DialogExceptionSaveImage/State',
			defaultValue=QtCore.QByteArray()
			)


	ImagePat = re.compile('.*(?<=$|\n)\<image\>(.+?)\<\/image\>', re.X|re.M|re.S)

	def __init__(self, info, parent=None):
		"""
		@param info: (str) err to display. may contain one base64 encoded image wrapped in <image> tags
		"""
		QtGui.QDialog. __init__(self, parent)

		self.setWindowTitle('%s - Error' % Tc2Config.ApplicationName)
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
			self.buttonSaveImage = QtGui.QPushButton('Save image..', self)
			self.buttonSaveImage.clicked.connect(self.onButtonSaveImageClicked)
			self.buttonBox.addButton(self.buttonSaveImage, self.buttonBox.ActionRole)

		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setPlainText(ErrText % (Tc2Config.ApplicationName, Tc2Config.ErrorLogName, info) )

		self.layout()

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.addWidget(self.edit, 0, 0)
		n = 1
		if self.labelPixmap is not None:
			grid.addWidget(self.labelPixmapName, 1, 0)
			grid.addWidget(self.labelPixmap, 2, 0)
			n = 3
		grid.addWidget(Tc2Config.HLine(self), n+1, 0)
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
		Tc2Config.globalObject.clearException.emit()
		self.buttonClearError.setEnabled(False)

	def onButtonSaveImageClicked(self):
		imageFormats = imageFormats = Tc2Config.readWriteImageFormats()
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Screenshot..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				defaultSuffix='png',
				setting=self.settingDialogSaveImageState,
				)
		if fileName is None:
			return
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not self.labelPixmap.pixmap().save(fileName, format):
			Tc2Config.msgWarning(self, 'Could Not Save Image')

