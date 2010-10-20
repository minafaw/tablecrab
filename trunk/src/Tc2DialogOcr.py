
import Tc2Config
from Tc2Lib.gocr import gocr
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
class Dialog(QtGui.QDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)

		self.setWindowTitle(Tc2Config.dialogTitle('Adjust Ocr'))

		self.splitterVert = QtGui.QSplitter(QtCore.Qt.Horizontal, self)

		# setup settings pane
		self.frameSettings = QtGui.QFrame(self.splitterVert)
		self.splitterVert.addWidget(self.frameSettings)

		self.checkBoxChars = QtGui.QCheckBox('Chars', self.frameSettings)
		self.editChars = QtGui.QLineEdit(self.frameSettings)

		self.checkBoxOutputPattern = QtGui.QCheckBox('Output pattern', self.frameSettings)
		self.editOutputPattern = QtGui.QLineEdit(self.frameSettings)

		self.checkBoxGraylevel = QtGui.QCheckBox('Gray level', self.frameSettings)
		self.spinGrayLevel = QtGui.QSpinBox(self.frameSettings)

		self.checkBoxDustSize = QtGui.QCheckBox('Dust size', self.frameSettings)
		self.spinDustSize = QtGui.QSpinBox(self.frameSettings)

		self.checkBoxWordSpacing = QtGui.QCheckBox('Word spacing', self.frameSettings)
		self.spinWordSpacing = QtGui.QSpinBox(self.frameSettings)

		self.checkBoxCertainty = QtGui.QCheckBox('Certainty', self.frameSettings)
		self.spinCertainty = QtGui.QSpinBox(self.frameSettings)

		self.checkBoxDatabase = QtGui.QCheckBox('Database', self.frameSettings)
		self.editDatabase = QtGui.QLineEdit(self.frameSettings)

		#
		self.splitterHorz = QtGui.QSplitter(QtCore.Qt.Vertical, self.splitterVert)
		self.splitterVert.addWidget(self.splitterHorz)

		self.labelInputImage = QtGui.QLabel('- image -', self.splitterHorz)
		self.splitterHorz.addWidget(self.labelInputImage)

		self.splitterOutput = QtGui.QSplitter(QtCore.Qt.Horizontal, self.splitterHorz)
		self.splitterHorz.addWidget(self.splitterOutput)

		self.webViewOutput = QtWebKit.QWebView(self.splitterOutput)
		self.splitterOutput.addWidget(self.webViewOutput)
		self.webViewOutput.setHtml('output')

		self.editOutputErr = QtGui.QPlainTextEdit(self.splitterOutput)
		self.splitterOutput.addWidget(self.editOutputErr)
		self.editOutputErr.setPlainText('Err')

		self.layout()

	def layout(self):
		grid = Tc2Config.GridBox(self)
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
		grid.col(self.checkBoxDatabase).col(self.editDatabase)

		grid.row()
		grid.col(Tc2Config.VStretch())

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



