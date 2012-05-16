
import Tc2Config
import Tc2GuiHelp

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class DialgScreenshotInfo(QtGui.QDialog):

	settingGeometry = Tc2Config.settings2.ByteArray(
			'Gui/DialogScreenshotInfo/Geometry',
			defaultValue=QtCore.QByteArray()
			)


	def __init__(self, info, parent=None):
		QtGui.QDialog. __init__(self, parent)
		self.setWindowTitle(Tc2Config.dialogTitle('Screenshot Info') )

		self._lastScreenshotInfo = info

		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setPlainText(info)
		self.edit.setReadOnly(True)

		self.buttonRefresh = QtGui.QPushButton('Refresh', self)
		self.buttonRefresh.clicked.connect(self.onRefresh)
		self.buttonRefresh.setToolTip('Save info (Ctrl+R)')

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+R') )
		action.triggered.connect(self.onRefresh)
		self.addAction(action)

		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonSave.setToolTip('Save info (Ctrl+S)')
		self.buttonSave.clicked.connect(self.onSave)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+S') )
		action.triggered.connect(self.onSave)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		self.buttonBox.addButton(self.buttonRefresh, self.buttonBox.ActionRole)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ApplyRole )
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		self.buttonBox.accepted.connect(self.accept)

		parent.widgetScreenshotInfo.connect(self.onWidgetScreenshotInfo)

		self.restoreGeometry(self.settingGeometry.value())
		self.layout()

	#----------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#---------------------------------------------------------------------------------------------------------------
	def hideEvent(self, event):
		self.settingGeometry.setValue(self.saveGeometry())
		QtGui.QDialog.hideEvent(self, event)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.edit)
		grid.row()
		grid.col(Tc2Config.HLine(self))
		grid.row()
		grid.col(self.buttonBox)

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('screenshotInfo', parent=self)

	def onRefresh(self, *args):
		self.edit.setPlainText(self._lastScreenshotInfo)

	def onSave(self, *args):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Screenshot Info..',
				fileFilters=('TextFiles (*.txt)', 'All Files (*)'),
				settingsKey='Gui/Screenshot/DialogScreenshotInfo/DialogSave/State',
				)
		if fileName is None:
			return
		# default to '.txt'
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not format:
			fileName = fileName + '.txt'
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.edit.toPlainText() )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Screenshot Info\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onWidgetScreenshotInfo(self, info):
		self._lastScreenshotInfo = info
		self.buttonRefresh.setEnabled(bool(info))
