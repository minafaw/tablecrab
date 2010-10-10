
import TableCrabConfig
import TableCrabGuiHelp
import PokerStarsHandGrabber
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.edit = TableCrabConfig.PlainTextEdit(
				settingsKey='PokerStarsHandGrabber/handFornmatterHtmlTabular/StyleSheet',
				default=PokerStarsHandGrabber.HandFormatterHtmlTabular.StyleSheet,
				maxChars=TableCrabConfig.MaxHandStyleSheet,
				)
		self.edit.maxCharsExceeded.connect(self.onMaxCharsExceeded)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		self.buttonRestoreDefault.setToolTip('Restore Default (Ctrl+R)')
		self.buttonRestoreDefault.clicked.connect(self.onRestoreDefault)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='Ctrl+R',
				slot=self.onRestoreDefault,
				)
		self.addAction(action)

		self.buttonOpen = QtGui.QPushButton('Open..', self)
		self.buttonOpen.setToolTip('Open style sheet (Ctrl+O)')
		self.buttonOpen.clicked.connect(self.onOpen)
		self.buttonBox.addButton(self.buttonOpen, self.buttonBox.ActionRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='Ctrl+O',
				slot=self.onOpen,
				)
		self.addAction(action)

		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonSave.setToolTip('Save style sheet (Ctrl+S)')
		self.buttonSave.clicked.connect(self.onSave)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ActionRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='Ctrl+S',
				slot=self.onSave,
				)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		action = TableCrabConfig.Action(
				parent=self,
				shortcut='F1',
				slot=self.onHelp,
				)
		self.addAction(action)

		self.layout()

	def layout(self):
		grid = TableCrabConfig.GridBox(self)
		grid.col(TableCrabConfig.HLine(self))
		grid.row()
		grid.col(self.edit)
		grid.row()
		grid.col(TableCrabConfig.HLine(self))
		grid.row()
		grid.col(self.buttonBox)

	def onOpen(self, checked):
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Style Sheet..',
				fileFilters=('Style sheets (*.css)', 'All Files (*)'),
				settingsKey='Gui/Settings/HandStyleSheet/DialogOpen/State',
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = open(fileName, 'r')
			self.edit.setPlainText(fp.read() )
		except Exception, d:
			TableCrabConfig.msgWarning(self, 'Could Not Open Style sheet\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onSave(self, checked):
		fileName = TableCrabConfig.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Style Sheet..',
				fileFilters=('Stylesheets (*.css)', 'All Files (*)'),
				settingsKey='Gui/Settings/HandStyleSheet/DialogSave/State',
				)
		if fileName is None:
			return
		# default to '.css'
		fileInfo = QtCore.QFileInfo(fileName)
		format = fileInfo.suffix().toLower()
		if not format:
			fileName = fileName + '.css'
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.edit.toPlainText() )
		except Exception, d:
			TableCrabConfig.msgWarning(self, 'Could Not Save Style sheet\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onHelp(self, *args):
		TableCrabGuiHelp.dialogHelp('settingsHandStyleSheet', parent=self)

	#TODO: resetting document jumps to top of widget. store/restore position would be nice
	def onRestoreDefault(self):
		self.edit.setPlainText(PokerStarsHandGrabber.HandFormatterHtmlTabular.StyleSheet)

	def onMaxCharsExceeded(self, flag):
		TableCrabConfig.globalObject.feedback.emit(self, ('Style sheet too big -- maximum Is %s chars' % TableCrabConfig.MaxHandStyleSheet) if flag else '')
