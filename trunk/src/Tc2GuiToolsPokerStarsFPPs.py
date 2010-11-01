#TODO: hotkeys
#TODO: check calculation

import Tc2Config
import Tc2GuiHelp
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
FPPMultipliers = (
		('Bronce', 1.0),
		('Silver', 1.5),
		('Gold', 2.0),
		('Platinum', 2.5),
		('Supernova', 3.5),
		('Supernova-Elite', 5.0),
		)

#************************************************************************************
#
#************************************************************************************
class FrameTool(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/PokerStars/FPPs'
	SettingsKeyVIPStatus = 'Gui/Tools/PokerStars/FPPs/VIPStatus'
	SettingsKeyConversion = 'Gui/Tools/PokerStars/FPPs/Conversion'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.label = QtGui.QLabel('Calculate PokerStars FPPs', self)

		self.labelVIPStatus = QtGui.QLabel('VIP-Status:', self)
		self.comboVIPStatus = QtGui.QComboBox(self)
		for vipStatus, multiplier in FPPMultipliers:
			self.comboVIPStatus.addItem(vipStatus, QtCore.QVariant(multiplier))

		self.labelAmount = QtGui.QLabel('Amount:', self)
		self.editAmount = QtGui.QLineEdit(self)
		self.editAmount.textChanged.connect(self.onEditAmountTextChanged)
		validator = QtGui.QDoubleValidator(self)
		validator.setBottom(0)
		validator.setDecimals(2)
		self.editAmount.setValidator(validator)

		self.buttonGroupConversion = QtGui.QButtonGroup(self)
		self.buttonGroupConversion.buttonClicked.connect(self.onButtonGroupConversionButtonClicked)
		self.buttonGroupConversion.setExclusive(True)
		self.radioCash = QtGui.QRadioButton('FPPs to Cash', self)
		self.buttonGroupConversion.addButton( self.radioCash,0)
		self.radioFPPs = QtGui.QRadioButton('Cash to FPPs', self)
		self.buttonGroupConversion.addButton(self.radioFPPs , 1)

		self.buttonCalculate = QtGui.QPushButton('Calculate', self)
		self.buttonCalculate.setEnabled(False)
		self.buttonCalculate.clicked.connect(self.onButtonCalculateClicked)
		self.editResult = QtGui.QLineEdit(self)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)
		self.addAction(action)

		Tc2Config.globalObject.init.connect(self.onInit)

	def toolTip(self):
		return 'PokerStars - FPPs'

	def toolName(self):
		return 'PokerStars - FPPs'

	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.label, colspan=3)
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelVIPStatus).col(self.comboVIPStatus).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelAmount).col(self.editAmount, colspan=2)
		grid.row()
		grid.col(self.radioCash)
		grid.row()
		grid.col(self.radioFPPs)

		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonCalculate).col(self.editResult, colspan=2)

		grid.row()
		grid.col(Tc2Config.VStretch())

		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onInit(self):
		self.layout()

		vipStatus = Tc2Config.settingsValue(self.SettingsKeyVIPStatus, '').toString()
		index = self.comboVIPStatus.findText(vipStatus, QtCore.Qt.MatchExactly)
		if index >= 0:
			self.comboVIPStatus.setCurrentIndex(index)
		self.comboVIPStatus.currentIndexChanged.connect(self.onComboVIPStatusCurrentIndexChanged)

		conversion =  Tc2Config.settingsValue(self.SettingsKeyConversion, '').toString()
		if conversion == 'FPPs':
			self.radioFPPs.setChecked(True)
		else:
			self.radioCash.setChecked(True)

	def onComboVIPStatusCurrentIndexChanged(self, index):
		vipStatus = self.comboVIPStatus.itemText(index)
		Tc2Config.settingsSetValue(self.SettingsKeyVIPStatus, vipStatus)

	def onButtonGroupConversionButtonClicked(self, button):
		Tc2Config.settingsSetValue(self.SettingsKeyConversion, 'Cash' if button is self.radioCash else 'FPPs')

	def onEditAmountTextChanged(self, text):
		self.buttonCalculate.setEnabled(bool(text))

	def onButtonCalculateClicked(self):
		v = self.comboVIPStatus.itemData(self.comboVIPStatus.currentIndex())
		multiplier = v.toDouble()[0]
		toCash = self.radioCash.isChecked()
		amount = float(self.editAmount.text())
		if toCash:
			result = amount / 5.5 / multiplier
		else:
			result = amount * 5.5 * multiplier
		self.editResult.setText('%.2f' % result)

	def onHelp(self):
		Tc2GuiHelp.dialogHelp('toolsPokerStarsFPPs', parent=self)















