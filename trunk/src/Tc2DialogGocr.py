"""dialog to wrap (most of) gocr
"""

#TODO: implement help
# TODO: input pipe seems to break on larger images. no idea why
#TODO: have to find a way to handle post processing of gocr output. "ouput pattern"
#           and "output type" as present in dialog is just a placeholder.
# TODO: could be possible to add database + training support. idea could be to grab
#           gocr output all at once, format as image(s) and handcraft the database.
#           problems: input pipe breaks for some reason on larger images, so could
#           output pipe?

import Tc2Config
from Tc2Lib.gocr import gocr
from PyQt4 import QtCore, QtGui, QtWebKit
import traceback, time

#************************************************************************************
#
#************************************************************************************
class Dialog(QtGui.QDialog):

	SettingsKeyBase = 'Gui/DialogOcr'
	SettingsKeyGeometry = SettingsKeyBase + '/Geometry'
	SettingsKeyDialogImageOpenState = SettingsKeyBase + '/DialogImageOpen/State'
	SettingsKeyDialogImageSaveState = SettingsKeyBase + '/DialogImageSave/State'
	SettingsKeySplitterSettingsState = SettingsKeyBase + '/SplitterSettingsState'
	SettingsKeySplitterImageState = SettingsKeyBase + '/SplitterImageState'
	SettingsKeySplitterOutputState = SettingsKeyBase + '/SplitteroutputState'

	def __init__(self, pixmap=None, gocrParams=None, gocrParamsDefault=None):
		QtGui.QDialog.__init__(self)

		self.setWindowTitle(Tc2Config.dialogTitle('Adjust Ocr'))

		self.gocrParamsDefault = gocrParamsDefault

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

		self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
		self.buttonBox.addButton(self.buttonBox.Ok).pressed.connect(self.accept)
		self.buttonBox.addButton(self.buttonBox.Cancel).pressed.connect(self.reject)
		self.buttonBox.addButton(self.buttonBox.RestoreDefaults).setEnabled(self.gocrParamsDefault is not None)

		self.splitterSettings = QtGui.QSplitter(QtCore.Qt.Horizontal, self)

		# setup settings pane
		self.frameSettings = QtGui.QFrame(self.splitterSettings)
		self.splitterSettings.addWidget(self.frameSettings)

		self.checkBoxChars = QtGui.QCheckBox('Chars', self.frameSettings)
		self.checkBoxChars.stateChanged.connect(self.onCheckBoxCharsStateChanged)
		self.editChars = QtGui.QLineEdit(self.frameSettings)

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

		self.checkBoxInvertImage = QtGui.QCheckBox('Invert image', self.frameSettings)
		self.checkBoxAnalyzeLayout = QtGui.QCheckBox('Analyze layout', self.frameSettings)
		self.checkBoxContextCorrection = QtGui.QCheckBox('Context correction', self.frameSettings)
		self.checkBoxCompareUnknownChars = QtGui.QCheckBox('Compare unknown chars', self.frameSettings)
		self.checkBoxDivideOverlappingChars = QtGui.QCheckBox('Divide overlapping chars', self.frameSettings)
		self.checkBoxPackChars = QtGui.QCheckBox('Pack chars', self.frameSettings)

		self.checkBoxOutputPattern = QtGui.QCheckBox('Output pattern', self.frameSettings)
		self.checkBoxOutputPattern.stateChanged.connect(self.onCheckBoxOutputPatternStateChanged)
		self.editOutputPattern = QtGui.QLineEdit(self.frameSettings)

		self.checkBoxOutputType = QtGui.QCheckBox('Output type', self.frameSettings)
		self.checkBoxOutputType.stateChanged.connect(self.onCheckBoxOutputTypeStateChanged)
		self.comboOutputType = QtGui.QComboBox(self.frameSettings)
		self.comboOutputType.addItems(gocr.OutputTypes)

		#
		self.splitterImage = QtGui.QSplitter(QtCore.Qt.Vertical, self.splitterSettings)
		self.splitterSettings.addWidget(self.splitterImage)

		self.scrollAreaInputImage = QtGui.QScrollArea( self.splitterImage)
		self.splitterImage.addWidget(self.scrollAreaInputImage)
		self.scrollAreaInputImage.setBackgroundRole(QtGui.QPalette.Dark)
		self.scrollAreaInputImage.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

		self.labelInputImage = QtGui.QLabel(self.scrollAreaInputImage)
		self.scrollAreaInputImage.setWidget(self.labelInputImage)

		self.splitterOutput = QtGui.QSplitter(QtCore.Qt.Horizontal, self.splitterImage)
		self.splitterImage.addWidget(self.splitterOutput)

		self.webViewOutput = QtWebKit.QWebView(self.splitterOutput)
		self.splitterOutput.addWidget(self.webViewOutput)

		self.webViewError = QtWebKit.QWebView(self.splitterOutput)
		self.splitterOutput.addWidget(self.webViewError)

		self.setPixmap(pixmap=pixmap)
		self.setGocrParams(params=gocrParams)
		self.setOutput(string='')
		self.setError(string='')
		self.layout()

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.toolBar)
		grid.row()
		grid.col(self.splitterSettings)
		grid.row()
		grid.col(Tc2Config.HLine())
		grid.row()
		grid.col(self.buttonBox)

		grid = Tc2Config.GridBox(self.frameSettings)

		grid.col(self.checkBoxChars).col(self.editChars)
		grid.row()
		grid.col(self.checkBoxGraylevel).col(self.spinGrayLevel)
		grid.row()
		grid.col(self.checkBoxDustSize).col(self.spinDustSize)
		grid.row()
		grid.col(self.checkBoxWordSpacing).col(self.spinWordSpacing)
		grid.row()
		grid.col(self.checkBoxCertainty).col(self.spinCertainty)

		grid.row()
		grid.col(Tc2Config.HLine(), colspan=2)
		grid.row()
		grid.col(self.checkBoxInvertImage)
		grid.row()
		grid.col(self.checkBoxAnalyzeLayout)
		grid.row()
		grid.col(self.checkBoxContextCorrection)
		grid.row()
		grid.col(self.checkBoxCompareUnknownChars)
		grid.row()
		grid.col(self.checkBoxDivideOverlappingChars)
		grid.row()
		grid.col(self.checkBoxPackChars)

		grid.row()
		grid.col(Tc2Config.HLine(), colspan=2)
		grid.row()
		grid.col(self.checkBoxOutputPattern).col(self.editOutputPattern)
		grid.row()
		grid.col(self.checkBoxOutputType).col(self.comboOutputType)

		grid.row()
		grid.col(Tc2Config.VStretch())

		self.restoreGeometry( Tc2Config.settingsValue(self.SettingsKeyGeometry, QtCore.QByteArray()).toByteArray())
		self.splitterSettings.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterSettingsState, QtCore.QByteArray()).toByteArray() )
		self.splitterImage.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterImageState, QtCore.QByteArray()).toByteArray() )
		self.splitterOutput.restoreState( Tc2Config.settingsValue(self.SettingsKeySplitterOutputState, QtCore.QByteArray()).toByteArray() )


	def hideEvent(self, event):
		Tc2Config.settingsSetValue(self.SettingsKeySplitterSettingsState, self.splitterSettings.saveState())
		Tc2Config.settingsSetValue(self.SettingsKeySplitterImageState, self.splitterImage.saveState())
		Tc2Config.settingsSetValue(self.SettingsKeySplitterOutputState, self.splitterOutput.saveState())
		Tc2Config.settingsSetValue(self.SettingsKeyGeometry, self.saveGeometry() )

		QtGui.QDialog.hideEvent(self, event)

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

		param = params.get('flagLayoutAnalysis', gocr.FlagLayoutAnalysisDefault)
		self.checkBoxAnalyzeLayout.setChecked(bool(param))

		param = params.get('flagContextCorrection', gocr.FlagContextCorrectionDefault)
		self.checkBoxContextCorrection.setChecked(bool(param))

		param = params.get('flagCompareUnrecognizedChars', gocr.FlagCompareUnrecognizedCharsDefault)
		print param
		self.checkBoxCompareUnknownChars.setChecked(bool(param))

		param = params.get('flagDivideOverlappingChars', gocr.FlagDivideOverlappingCharsDefault)
		self.checkBoxDivideOverlappingChars.setChecked(bool(param))

		param = params.get('flagPackChars', gocr.FlagPackCharsDefault)
		self.checkBoxPackChars.setChecked(bool(param))

		param = params.get('flagInvertImage', False)
		self.checkBoxInvertImage.setChecked(bool(param))

		param = params.get('outputPattern', None)
		self.checkBoxOutputPattern.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.editOutputPattern.setEnabled(param is not None)
		self.editOutputPattern.setText('' if param is None else '')

		param = params.get('outputType', None)
		self.checkBoxOutputType.setCheckState(QtCore.Qt.Unchecked if param is None else QtCore.Qt.Checked)
		self.comboOutputType.setEnabled(param is not None)
		if param is not None:
			if param not in gocr.OutputTypes:
				param = gocr.OutputTypeDefault
			self.comboOutputType.setCurrentIndex( self.comboOutputType.findText(param, QtCore.Qt.MatchExactly) )

	def gocrParams(self):
		pixmap = self.labelInputImage.pixmap()
		if pixmap.isNull():
			return None
		mode = 0
		mode |= gocr.ModeDoLayoutAnalysis if self.checkBoxAnalyzeLayout.checkState() == QtCore.Qt.Checked else 0
		mode |= 0 if self.checkBoxContextCorrection.checkState() == QtCore.Qt.Checked else gocr.ModeNoContextCorrection
		mode |= 0 if self.checkBoxCompareUnknownChars.checkState() == QtCore.Qt.Checked else gocr.ModeNoCompareUnrecognizedChars
		mode |= 0 if self.checkBoxDivideOverlappingChars.checkState() == QtCore.Qt.Checked else gocr.ModeNoDivideOverlappingChars
		mode |= gocr.ModeCharPacking if self.checkBoxPackChars.checkState() == QtCore.Qt.Checked else 0

		params = {
				'chars': unicode(self.editChars.text().toUtf8(), 'Utf-8') if self.editChars.isEnabled() else None,
				'grayLevel': self.spinGrayLevel.value() if  self.spinGrayLevel.isEnabled() else None,
				'dustSize': self.spinDustSize.value() if  self.spinDustSize.isEnabled() else None,
				'wordSpacing': self.spinWordSpacing.value() if  self.spinWordSpacing.isEnabled() else None,
				'certainty': self.spinCertainty.value() if  self.spinCertainty.isEnabled() else None,

				'flagLayoutAnalysis':self.checkBoxAnalyzeLayout.checkState() == QtCore.Qt.Checked,
				'flagContextCorrection':self.checkBoxContextCorrection.checkState() == QtCore.Qt.Checked,
				'flagCompareUnrecognizedChars':self.checkBoxPackChars.checkState() == QtCore.Qt.Checked,
				'flagDivideOverlappingChars':self.checkBoxDivideOverlappingChars.checkState() == QtCore.Qt.Checked,
				'flagPackChars':self.checkBoxPackChars.checkState() == QtCore.Qt.Checked,

				'flagInvertImage': self.checkBoxInvertImage.checkState() == QtCore.Qt.Checked,
				'outputPattern': unicode(self.editOutputPattern.text().toUtf8(), 'Utf-8') if self.editOutputPattern.isEnabled() else None,
				'outputType': self.comboOutputType.currentText(),
				}
		return params

	def setOutput(self, string=None, number=None, formattedString=None, timeElapsed=None):
		html = '<html>'
		html += '<head>'
		html += '<meta name="author" content="TableCrab">'
		html += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		html += '</head>'
		html += '<body>'
		html +='<h4>Output:</h4>'

		if string is not None and string:
			html += '<table border=1 cellspacing="0" cellpadding="0"><tr>'
			tdLineno = '<td style="background-color: lightgray">'
			tdText = '<td>'
			for lineno, line in enumerate(string.split('\n')):
				tdLineno += str(lineno +1).zfill(2) + '<br>'
				tdText += line + '<br>'
			tdLineno += '</td>'
			tdText += '</td>'
			html += tdLineno
			html += tdText
			html += '</tr></table>'

		elif string is not None and not string:
			pass

		elif number is not None:
			html += str(number)
		else:
			raise ValueError('no output specified')

		html +='<h4>Time elapsed:</h4>'
		html += '' if timeElapsed is None else (str(round(timeElapsed, 3)) + ' seconds')
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
		pgmImage = gocr.ImagePGM.fromQPixmap(pixmap)
		params = self.gocrParams()
		params['pgmImage'] = pgmImage
		outputPattern = params.pop('outputPattern')
		params['outputFormat'] = gocr.OutputFormatUTF8
		try:
			timeElapsed = time.time()
			out, err = gocr.scanImage(**params)
			timeElapsed = time.time() - timeElapsed
		except Exception, d:
			#TODO: how do we handle exceptions here?
			err = traceback.format_exc()
			out = ''
			timeElapsed = None

		if params['outputType'] in (gocr.OutputTypeInt, gocr.OutputTypeFloat):
			self.setOutput(number=out, timeElapsed=timeElapsed)
		else:
			self.setOutput(string=out, timeElapsed=timeElapsed)
		self.setError(string=err)

	def onActionOpenImageTriggered(self):
		imageFormats = Tc2Config.readWriteImageFormats()
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Image..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				settingsKey=self.SettingsKeyDialogImageOpenState,
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
		if self.labelInputImage.pixmap() is None:
			self.actionSaveImage.setEnabled(False)
			return
		imageFormats = imageFormats = Tc2Config.readWriteImageFormats()
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Image..',
				fileFilters=('Images (%s)' % ' '.join(['*.%s' % i for i in imageFormats]), 'All Files (*)'),
				defaultSuffix='png',
				settingsKey=self.SettingsKeyDialogImageSaveState,
				)
		if fileName is None:
			return
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not self.labelInputImage.pixmap().save(fileName, format):
			Tc2Config.msgWarning(self, 'Could Not Save Image')

	def onActionHelpTriggered(self):
		pass

	def onCheckBoxCharsStateChanged(self, state):
		self.editChars.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxGraylevelStateChanged(self, state):
		self.spinGrayLevel.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxDustSizeStateChanged(self, state):
		self.spinDustSize.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxWordSpacingStateChanged(self, state):
		self.spinWordSpacing.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxCertaintyStateChanged(self, state):
		self.spinCertainty.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxOutputPatternStateChanged(self, state):
		self.editOutputPattern.setEnabled(state == QtCore.Qt.Checked)

	def onCheckBoxOutputTypeStateChanged(self, state):
		self.comboOutputType.setEnabled(state == QtCore.Qt.Checked)

#************************************************************************************
#
#************************************************************************************
def main():
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = Dialog()
	gui.show()
	QtGui.qApp.setStyle('cleanlooks')
	application.exec_()

if __name__ == '__main__': main()



