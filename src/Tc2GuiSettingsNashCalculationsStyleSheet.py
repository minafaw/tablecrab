
import Tc2Config
import Tc2GuiHelp
from Tc2Lib import HoldemResources
import Tc2GuiToolsHandHistoryViewer
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Settings/NashCalculationsStyleSheet'
	SettingsKeyDialogOpenState = SettingsKeyBase + '/DialogOpen/State'
	SettingsKeyDialogSaveState = SettingsKeyBase + '/DialogSave/State'
	SettingsKeyStyleSheet = SettingsKeyBase + '/StyleSheet'

	styleSheetChanged = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.edit = QtGui.QPlainTextEdit(self)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		self.buttonRestoreDefault.setToolTip('Restore Default (Ctrl+R)')
		self.buttonRestoreDefault.clicked.connect(self.onRestoreDefault)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+R') )
		action.triggered.connect(self.onRestoreDefault)
		self.addAction(action)

		self.buttonOpen = QtGui.QPushButton('Open..', self)
		self.buttonOpen.setToolTip('Open style sheet (Ctrl+O)')
		self.buttonOpen.clicked.connect(self.onOpen)
		self.buttonBox.addButton(self.buttonOpen, self.buttonBox.ActionRole)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+O') )
		action.triggered.connect(self.onOpen)
		self.addAction(action)

		self.buttonSave = QtGui.QPushButton('Save..', self)
		self.buttonSave.setToolTip('Save style sheet (Ctrl+S)')
		self.buttonSave.clicked.connect(self.onSave)
		self.buttonBox.addButton(self.buttonSave, self.buttonBox.ActionRole)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+S') )
		action.triggered.connect(self.onSave)
		self.addAction(action)

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
		grid.col(Tc2Config.HLine(self))
		grid.row()
		grid.col(self.edit)
		grid.row()
		grid.col(Tc2Config.HLine(self))
		grid.row()
		grid.col(self.buttonBox)

	def onEditTextChanged(self):
		text = self.edit.toPlainText()
		if Tc2Config.MaxHandStyleSheet >= 0:
			if text.length() > Tc2Config.MaxHandStyleSheet:
				Tc2Config.globalObject.feedback.emit(self, 'Style sheet too big -- maximum Is %s chars' % Tc2Config.MaxHandStyleSheet)
				return
		Tc2Config.globalObject.feedback.emit(self, '')
		Tc2Config.settingsSetValue(self.SettingsKeyStyleSheet, text)

	def onInitSettings(self):
		self.layout()

		#NOTE: style sheet can not be ''
		#NOTE: have to connect before setText so we can catch MaxCharsExceeded
		value = Tc2Config.settingsValue(self.SettingsKeyStyleSheet, '').toString()
		if not value:
			value = HoldemResources.NashFormatter.StyleSheet
		self.edit.setPlainText(value)
		self.edit.textChanged.connect(
				lambda self=self: self.setStyleSheet(self.edit.toPlainText())
				)

		Tc2Config.globalObject.objectCreatedSettingsNashCalculationsStyleSheet.emit(self)

	def onOpen(self, checked):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=True,
				title='Open Style Sheet..',
				fileFilters=('Style sheets (*.css)', 'All Files (*)'),
				#TODO: rename to HandViewerStyleSheet
				settingsKey=self.SettingsKeyDialogOpenState,
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = open(fileName, 'r')
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Open Style sheet\n\n%s' % d)
			return
		else:
			value = fp.read()
		finally:
			if fp is not None: fp.close()
		self.edit.setPlainText(value)

	def onSave(self, checked):
		fileName = Tc2Config.dlgOpenSaveFile(
				parent=self,
				openFile=False,
				title='Save Style Sheet..',
				fileFilters=('Stylesheets (*.css)', 'All Files (*)'),
				#TODO: rename to HandViewerStyleSheet
				settingsKey=self.SettingsKeyDialogSaveState,
				defaultSuffix='css',
				)
		if fileName is None:
			return
		fp = None
		try:
			fp = open(fileName, 'w')
			fp.write(self.edit.toPlainText() )
		except Exception, d:
			Tc2Config.msgWarning(self, 'Could Not Save Style sheet\n\n%s' % d)
		finally:
			if fp is not None: fp.close()

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsNashCalculationsStyleSheet', parent=self)

	#TODO: resetting document jumps to top of widget. store/restore position would be nice
	def onRestoreDefault(self):
		self.edit.setPlainText(HoldemResources.NashFormatter.StyleSheet)

	def styleSheet(self):
		return self.edit.toPlainText()

	def setStyleSheet(self, value):
		if Tc2Config.MaxHandStyleSheet >= 0:
			if value.length() > Tc2Config.MaxHandStyleSheet:
				Tc2Config.globalObject.feedback.emit(self, 'Style sheet too big -- maximum Is %s chars' % Tc2Config.MaxHandStyleSheet)
				return
		Tc2Config.globalObject.feedback.emit(self, '')
		Tc2Config.settingsSetValue(self.SettingsKeyStyleSheet, value)
		self.styleSheetChanged.emit(value)







