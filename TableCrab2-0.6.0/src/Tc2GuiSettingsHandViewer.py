
import Tc2Config
import Tc2GuiHelp
import Tc2HandGrabberPokerStars
from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class FrameSettings(QtGui.QFrame):

	class ActionLineEdit(QtGui.QLineEdit):
		def __init__(self, parent=None, text='', settingsKey=None, default=None):
			QtGui.QLineEdit.__init__(self, text, parent)
			self.settingsKey = settingsKey
			self.default = default

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self.labelPrefix = QtGui.QLabel('<i>Prefix</i>', self)
		self.labelAction = QtGui.QLabel('<i>Action</i>', self)
		self.labelPostfix = QtGui.QLabel('<i>Postfix</i>', self)

		self.actionWidgets = []
		for (actionName, settingsKeyPrefix, defaultPrefix, settingsKeyPostfix, defaultPostfix) in Tc2HandGrabberPokerStars.HandFormatterHtmlTabular.ActionPrefixes:
			editPrefix = self.ActionLineEdit(parent=self, settingsKey= settingsKeyPrefix, default=defaultPrefix)
			editPrefix.setMaxLength(Tc2Config.MaxHandGrabberPrefix)
			labelAction = QtGui.QLabel('<i>' + actionName + '</i>', self)
			labelAction.setBuddy(editPrefix)
			if settingsKeyPostfix is not None:
				editPostfix =  self.ActionLineEdit(parent=self, settingsKey= settingsKeyPostfix, default=defaultPostfix)
				editPostfix.setMaxLength(Tc2Config.MaxHandGrabberPrefix)
			else:
				editPostfix = None
			self.actionWidgets.append({'EditPrefix': editPrefix, 'LabelAction': labelAction, 'EditPostfix': editPostfix})

		self.comboSideBarPosition = QtGui.QComboBox(self)
		self.comboSideBarPosition.addItems(Tc2Config.HandViewerSideBarPositions)
		self.labelSideBarPosition = QtGui.QLabel('&Side bar position:', self)
		self.labelSideBarPosition.setBuddy(self.comboSideBarPosition)

		self.spinMaxPlayerName = QtGui.QSpinBox(self)
		self.spinMaxPlayerName.setRange(-1, 999)
		self.labelMaxPlayerName = QtGui.QLabel('Ma&x Player Name:', self)
		self.labelMaxPlayerName.setBuddy(self.spinMaxPlayerName)

		self.checkNoFloatingPoint = QtGui.QCheckBox('Floating &Point To Integer', self)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonRestoreDefault = QtGui.QPushButton('Restore Default', self)
		self.buttonRestoreDefault.setToolTip('Restore Default (Ctrl+R)')
		self.buttonRestoreDefault.clicked.connect(self.onRestoreDefault)
		self.buttonBox.addButton(self.buttonRestoreDefault, self.buttonBox.ResetRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+R') )
		action.triggered.connect(self.onRestoreDefault)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		Tc2Config.globalObject.init.connect(self.onInit)

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelSideBarPosition).col(self.comboSideBarPosition)
		grid.row()
		grid.col(self.labelMaxPlayerName).col(self.spinMaxPlayerName)
		grid.row()
		grid.col(self.checkNoFloatingPoint, colspan=3)
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelPrefix).col(self.labelAction).col(self.labelPostfix)
		for data in self.actionWidgets:
			grid.row()
			grid.col(data['EditPrefix']).col(data['LabelAction'])
			if data['EditPostfix'] is not None:
				grid.col(data['EditPostfix'])
		grid.row()
		grid.col(Tc2Config.VStretch())
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onRestoreDefault(self, *args):
		for data in self.actionWidgets:
			editPrefix = data['EditPrefix']
			editPrefix.setText(editPrefix.default)
			editPrefix.editingFinished.emit()
			editPostfix = data['EditPostfix']
			if editPostfix is not None:
				editPostfix.setText(editPostfix.default)
				editPostfix.editingFinished.emit()

	def onHelp(self, *args):
		Tc2GuiHelp.dialogHelp('settingsHandViewer', parent=self)

	def onSpinMaxPlayerNameValueChanged(self, value):
		Tc2Config.settingsSetValue(Tc2HandGrabberPokerStars.HandFormatterHtmlTabular.SettingsKeyMaxPlayerName, value)

	def onNoFloatingPointChanged(self, state):
		flag = state == QtCore.Qt.Checked
		Tc2Config.settingsSetValue(Tc2HandGrabberPokerStars.HandFormatterHtmlTabular.SettingsKeyNoFloatingPoint, flag)

	def onActionWidgetValueChanged(self):
		edit = self.sender()
		Tc2Config.settingsSetValue(edit.settingsKey, edit.text())

	def onComboSideBarPositionCurrentIndexChanged(self, index):
		value = self.comboSideBarPosition.itemText(index)
		Tc2Config.settingsSetValue(Tc2Config.SettingsKeyHandViewerSideBarPosition, value)
		Tc2Config.globalObject.settingHandViewerSideBarPositionChanged.emit(value)

	def onInit(self):
		self.layout()

		value= Tc2Config.settingsValue(Tc2Config.SettingsKeyHandViewerSideBarPosition, '').toString()
		if value not in Tc2Config.HandViewerSideBarPositions:
			value = Tc2Config.HandViewerSideBarPositionDefault
		self.comboSideBarPosition.setCurrentIndex( self.comboSideBarPosition.findText(value, QtCore.Qt.MatchExactly) )
		self.comboSideBarPosition.currentIndexChanged.connect(self.onComboSideBarPositionCurrentIndexChanged)

		maxPlayerName = Tc2Config.settingsValue(Tc2HandGrabberPokerStars.HandFormatterHtmlTabular.SettingsKeyMaxPlayerName, -1).toInt()[0]
		self.spinMaxPlayerName.setValue(maxPlayerName)
		self.spinMaxPlayerName.valueChanged.connect(self.onSpinMaxPlayerNameValueChanged)

		state = QtCore.Qt.Checked if Tc2Config.settingsValue(Tc2HandGrabberPokerStars.HandFormatterHtmlTabular.SettingsKeyNoFloatingPoint, False).toBool() else QtCore.Qt.Unchecked
		self.checkNoFloatingPoint.setCheckState(state)
		self.checkNoFloatingPoint.stateChanged.connect(self.onNoFloatingPointChanged)

		for data in self.actionWidgets:
			editPrefix = data['EditPrefix']
			text = Tc2Config.settingsValue(editPrefix.settingsKey, editPrefix.default).toString()
			editPrefix.setText(text)
			editPrefix.editingFinished.connect(self.onActionWidgetValueChanged)
			editPostfix = data['EditPostfix']
			if editPostfix is not None:
				text = Tc2Config.settingsValue(editPostfix.settingsKey, editPostfix.default).toString()
				editPostfix.setText(text)
				editPostfix.editingFinished.connect(self.onActionWidgetValueChanged)




