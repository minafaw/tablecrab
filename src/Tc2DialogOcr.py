
import Tc2Config
from Tc2Lib.gocr import gocr
from PyQt4 import QtCore, QtGui, QtWebKit
import traceback, time

#************************************************************************************
#
#************************************************************************************
class Dialog(QtGui.QDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)

		self.setWindowTitle(Tc2Config.dialogTitle('Adjust Ocr'))


		self.toolBar = QtGui.QToolBar(self)

		self.actionScanImage = QtGui.QAction(self)
		self.actionScanImage.setText('Scan image')
		#self.actionScanImage.setShortcut(QtGui.QKeySequence('F1') )
		self.actionScanImage.triggered.connect(self.onActionScanImageTriggered)
		self.toolBar.addAction(self.actionScanImage)

		self.actionOpenImage = QtGui.QAction(self)
		self.actionOpenImage.setText('Open image..')
		#self.actionOpenImage.setShortcut(QtGui.QKeySequence('F1') )
		self.actionOpenImage.triggered.connect(self.onActionOpenImageTriggered)
		self.toolBar.addAction(self.actionOpenImage)

		self.actionSaveImage = QtGui.QAction(self)
		self.actionSaveImage.setText('Save image..')
		#self.actionOpenImage.setShortcut(QtGui.QKeySequence('F1') )
		self.actionSaveImage.triggered.connect(self.onActionSaveImageTriggered)
		self.toolBar.addAction(self.actionSaveImage)

		self.actionHelp = QtGui.QAction(self)
		self.actionHelp.setText('Help')
		self.actionHelp.setShortcut(QtGui.QKeySequence('F1') )
		self.actionHelp.triggered.connect(self.onActionHelpTriggered)
		self.toolBar.addAction(self.actionHelp)


		self.splitterVert = QtGui.QSplitter(QtCore.Qt.Horizontal, self)

		# setup settings pane
		self.frameSettings = QtGui.QFrame(self.splitterVert)
		self.splitterVert.addWidget(self.frameSettings)

		self.checkBoxChars = QtGui.QCheckBox('Chars', self.frameSettings)
		self.checkBoxChars.stateChanged.connect(self.onCheckBoxCharsStateChanged)
		self.editChars = QtGui.QLineEdit(self.frameSettings)

		self.checkBoxOutputPattern = QtGui.QCheckBox('Output pattern', self.frameSettings)
		self.checkBoxOutputPattern.stateChanged.connect(self.onCheckBoxOutputPatternStateChanged)
		self.editOutputPattern = QtGui.QLineEdit(self.frameSettings)

		self.checkBoxGraylevel = QtGui.QCheckBox('Gray level', self.frameSettings)
		self.checkBoxGraylevel.stateChanged.connect(self.onCheckBoxGraylevelStateChanged)
		self.spinGrayLevel = QtGui.QSpinBox(self.frameSettings)
		self.spinGrayLevel.setRange(gocr.GrayLevelMin, gocr.GrayLevelMax)

		self.checkBoxDustSize = QtGui.QCheckBox('Dust size', self.frameSettings)
		self.checkBoxDustSize.stateChanged.connect(self.onCheckBoxDustSizeStateChanged)
		self.spinDustSize = QtGui.QSpinBox(self.frameSettings)
		self.spinDustSize.setRange(gocr.DustSizeMin, gocr.DustSizeMax)

		self.checkBoxWordSpacing = QtGui.QCheckBox('Word spacing', self.frameSettings)
		self.checkBoxWordSpacing.stateChanged.connect(self.onCheckBoxWordSpacingStateChanged)
		self.spinWordSpacing = QtGui.QSpinBox(self.frameSettings)
		self.spinWordSpacing.setRange(gocr.WordSpacingMin, gocr.WordSpacingMax)

		self.checkBoxCertainty = QtGui.QCheckBox('Certainty', self.frameSettings)
		self.checkBoxCertainty.stateChanged.connect(self.onCheckBoxCertaintyStateChanged)
		self.spinCertainty = QtGui.QSpinBox(self.frameSettings)
		self.spinCertainty.setRange(gocr.CertaintyMin, gocr.CertaintyMax)

		#
		self.splitterHorz = QtGui.QSplitter(QtCore.Qt.Vertical, self.splitterVert)
		self.splitterVert.addWidget(self.splitterHorz)

		self.scrollAreaInputImage = QtGui.QScrollArea( self.splitterHorz)
		self.splitterHorz.addWidget(self.scrollAreaInputImage)
		self.scrollAreaInputImage.setBackgroundRole(QtGui.QPalette.Dark)
		self.scrollAreaInputImage.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

		self.labelInputImage = QtGui.QLabel(self.scrollAreaInputImage)
		self.scrollAreaInputImage.setWidget(self.labelInputImage)

		self.splitterOutput = QtGui.QSplitter(QtCore.Qt.Horizontal, self.splitterHorz)
		self.splitterHorz.addWidget(self.splitterOutput)

		self.webViewOutput = QtWebKit.QWebView(self.splitterOutput)
		self.splitterOutput.addWidget(self.webViewOutput)

		self.webViewError = QtWebKit.QWebView(self.splitterOutput)
		self.splitterOutput.addWidget(self.webViewError)

		self.layout()
		self.setPixmap(pixmap=None)
		self.setGocrParams(params=None)
		self.setOutput(string=None)
		self.setError(string=None)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.splitterVert)

		grid = Tc2Config.GridBox(self.frameSettings)

		grid.col(self.checkBoxChars).col(self.editChars)
		grid.row()
		grid.col(self.checkBoxOutputPattern).col(self.editOutputPattern)
		grid.row()
		grid.col(self.checkBoxGraylevel).col(self.spinGrayLevel)
		grid.row()
		grid.col(self.checkBoxDustSize).col(self.spinDustSize)
		grid.row()
		grid.col(self.checkBoxWordSpacing).col(self.spinWordSpacing)
		grid.row()
		grid.col(self.checkBoxCertainty).col(self.spinCertainty)

		grid.row()
		grid.col(Tc2Config.VStretch())

	def setPixmap(self, pixmap=None):
		if pixmap is None:
			self.labelInputImage.setText('- image -')
			self.labelInputImage.setFrameShape(QtGui.QFrame.NoFrame)
			self.labelInputImage.setScaledContents(True)
			self.labelInputImage.resize(self.labelInputImage.parent().size())
		else:
			self.labelInputImage.setPixmap(pixmap)
			self.labelInputImage.setScaledContents(False)
			self.labelInputImage.setFrameShape(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
			self.labelInputImage.resize(pixmap.size())

		self.actionScanImage.setEnabled(pixmap is not None)
		self.actionSaveImage.setEnabled(pixmap is not None)

	def setGocrParams(self, params=None):
		if params is None:
			params = {}

		param = params.get('chars', None)
		self.checkBoxChars.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.editChars.setEnabled(param is not None)
		self.editChars.setText('' if param is None else '')

		param = params.get('outputPattern', None)
		self.checkBoxOutputPattern.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.editOutputPattern.setEnabled(param is not None)
		self.editOutputPattern.setText('' if param is None else '')

		param = params.get('grayLevel', None)
		self.checkBoxGraylevel.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.spinGrayLevel.setEnabled(param is not None)
		self.spinGrayLevel.setValue(gocr.GrayLevelMin if param is None else param)

		param = params.get('dustSize', None)
		self.checkBoxDustSize.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.spinDustSize.setEnabled(param is not None)
		self.spinDustSize.setValue(gocr.DustSizeMin if param is None else param)

		param = params.get('wordSpacing', None)
		self.checkBoxWordSpacing.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.spinWordSpacing.setEnabled(param is not None)
		self.spinWordSpacing.setValue(gocr.WordSpacingMin if param is None else param)

		param = params.get('certainty', None)
		self.checkBoxCertainty.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.spinCertainty.setEnabled(param is not None)
		self.spinCertainty.setValue(gocr.CertaintyDefault if param is None else param)

	def gocrParams(self):
		pixmap = self.labelInputImage.pixmap()
		if pixmap.isNull():
			return None
		params = {
				'chars': unicode(self.editChars.text().toUtf8(), 'Utf-8') if self.editChars.isEnabled() else None,
				'outputPattern': unicode(self.editOutputPattern.text().toUtf8(), 'Utf-8') if self.editOutputPattern.isEnabled() else None,
				'grayLevel': self.spinGrayLevel.value() if  self.spinGrayLevel.isEnabled() else None,
				'dustSize': self.spinDustSize.value() if  self.spinDustSize.isEnabled() else None,
				'wordSpacing': self.spinWordSpacing.value() if  self.spinWordSpacing.isEnabled() else None,
				'certainty': self.spinCertainty.value() if  self.spinCertainty.isEnabled() else None,
				}
		return params

	def setOutput(self, string=None, formattedString=None, timeElapsed=None):
		string = '' if string is None else string
		html = '<html>'
		html += '<head>'
		html += '<meta name="author" content="TableCrab">'
		html += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		html += '</head>'
		html += '<body>'
		html +='<h4>Raw output:</h4>'
		html += repr(string)
		html +='<h4>Time elapsed:</h4>'
		html += '' if timeElapsed is None else str(round(timeElapsed, 2))
		html += '</body>'
		html += '</html>'
		self.webViewOutput.setHtml(html)

	def setError(self, string=None):
		string = '' if string is None else string
		html = '<html>'
		html += '<head>'
		html += '<meta name="author" content="TableCrab">'
		html += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		html += '</head>'
		html += '<body>'
		html +='<h4>Error:</h4>'
		html += string
		html += '</body>'
		html += '</html>'
		self.webViewError.setHtml(html)

	def onActionScanImageTriggered(self):
		pixmap = self.labelInputImage.pixmap()
		if pixmap.isNull():
			raise ValueError('invalid or no pixmap')
		pgm = gocr.ImagePGM.fromQPixmap(pixmap)
		params = self.gocrParams()
		params['outputFormat'] = gocr.OutputFormatUTF8
		params['string'] =  pgm.toString()
		outputPattern = params.pop('outputPattern')
		try:
			timeElapsed = time.time()
			out, err = gocr.scanImage(**params)
			timeElapsed = time.time() - timeElapsed
		except Exception, d:
			#TODO: how do we handle exceptions here?
			err = traceback.format_exc()
			out = ''
			timeElapsed = None
		self.setOutput(string=out, timeElapsed=timeElapsed)
		self.setError(string=err)

	def onActionOpenImageTriggered(self):
		imageFormats = Tc2Config.readWriteImageFormats()
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Image..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				##settingsKey=self.SettingsKeyDialogOpenState,
				)
		if fileName is None:
			return
		pixmap = QtGui.QPixmap()
		if not pixmap.load(fileName):
			Tc2Config.msgWarning(self, 'Could not open image')
			return
		fileInfo = QtCore.QFileInfo(fileName)
		screenshotName = fileInfo.baseName()
		self.setPixmap(pixmap=pixmap)

	def onActionSaveImageTriggered(self):
		pass

	def onActionHelpTriggered(self):
		pass

	def onCheckBoxCharsStateChanged(self, state):
		self.editChars.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxOutputPatternStateChanged(self, state):
		self.editOutputPattern.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxGraylevelStateChanged(self, state):
		self.spinGrayLevel.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxDustSizeStateChanged(self, state):
		self.spinDustSize.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxWordSpacingStateChanged(self, state):
		self.spinWordSpacing.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxCertaintyStateChanged(self, state):
		self.spinCertainty.setEnabled(state == QtCore.Qt.Checked)



#************************************************************************************
#
#************************************************************************************
def main():
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = Dialog()
	gui.show()
	QtGui.qApp.setStyle('motif')
	application.exec_()

if __name__ == '__main__': main()



