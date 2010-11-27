# -*- coding: utf-8 -*-


#TODO: hotkeys
#TODO: check calculation

import Tc2Config
import Tc2GuiHelp
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
VIPLevels = (
		('Bronce', 1.0),
		('Silver', 1.5),
		('Gold', 2.0),
		('Platinum', 2.5),
		('Supernova', 3.5),
		('Supernova-Elite', 5.0),
		)

#NOTE:  acc to [ http://www.pokerstars.com/vip/earn/ ]
# tournies and cash game (2-7 players):
#     5.5 VIPs / $1.0 rake
#     8 VIPs / €1.0 rake
# cash game (8+ players)
#     6 VIPs / $1.0 rake
#     8.5 VIPs / €1.0 rake
GameTypes = (
		('Tourney', (('$', 5.5), (u'€', 8.0)) ),
		('Cash Game (2-7 Players)', (('$', 5.5), (u'€', 8.0)) ),
		('Cash Game (8+ Players)', (('$', 6), (u'€', 8.5))),
		)
Currencies = (
		'$',
		u'€',
		)

#************************************************************************************
#
#************************************************************************************
class FrameTool(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/PokerStars/FPPs'
	SettingsKeyVIPStatus = 'Gui/Tools/PokerStars/FPPs/VIPStatus'
	SettingsKeyGameType = 'Gui/Tools/PokerStars/FPPs/GameType'
	SettingsKeyCurrency = 'Gui/Tools/PokerStars/FPPs/Currency'
	SettingsKeyConversion = 'Gui/Tools/PokerStars/FPPs/Conversion'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.label = QtGui.QLabel('FPP calculator', self)

		self.labelVIPStatus = QtGui.QLabel('VIP status:', self)
		self.comboVIPStatus = QtGui.QComboBox(self)
		for vipStatus, multiplier in VIPLevels:
			self.comboVIPStatus.addItem(vipStatus, QtCore.QVariant(multiplier))

		self.labelGameType = QtGui.QLabel('Game type:', self)
		self.comboGameType = QtGui.QComboBox(self)
		for gameType, _ in GameTypes:
			self.comboGameType.addItem(gameType)

		self.labelCurrency = QtGui.QLabel('Game currency:', self)
		self.comboCurrency = QtGui.QComboBox(self)
		for currency in Currencies:
			self.comboCurrency.addItem(currency)

		self.labelAmount = QtGui.QLabel('Amount:', self)
		self.editAmount = QtGui.QLineEdit(self)
		self.editAmount.textChanged.connect(self.onEditAmountTextChanged)
		validator = QtGui.QDoubleValidator(self)
		validator.setBottom(0)
		validator.setDecimals(2)
		validator.setNotation(validator.StandardNotation)
		self.editAmount.setValidator(validator)

		self.buttonGroupConversion = QtGui.QButtonGroup(self)
		self.buttonGroupConversion.buttonClicked.connect(self.onButtonGroupConversionButtonClicked)
		self.buttonGroupConversion.setExclusive(True)
		self.radioCash = QtGui.QRadioButton('FPPs to Cash', self)
		self.buttonGroupConversion.addButton( self.radioCash,0)
		self.radioFPPs = QtGui.QRadioButton('Cash to FPPs', self)
		self.buttonGroupConversion.addButton(self.radioFPPs , 1)

		self.buttonCalculate = QtGui.QPushButton('Calculate', self)
		self.buttonCalculate.setToolTip('Calculates FPPs (Return)')
		self.buttonCalculate.setEnabled(False)
		self.buttonCalculate.clicked.connect(self.onCalculate)
		self.editResult = QtGui.QLineEdit(self)

		self.actionCalculate = QtGui.QAction(self.buttonCalculate)
		self.actionCalculate.setShortcut(QtGui.QKeySequence('RETURN') )
		self.actionCalculate.triggered.connect(self.onCalculate)
		self.buttonCalculate.addAction(self.actionCalculate)

		self.editCache = QtGui.QPlainTextEdit(self)
		self.editCache.setReadOnly(True)

		self.buttonClearCache = QtGui.QPushButton('Clear', self)
		self.buttonClearCache.setToolTip('Clears cached results (Alt+L)')
		self.buttonClearCache.setEnabled(False)
		self.buttonClearCache.clicked.connect(self.onClearCache)

		self.actionClearCache = QtGui.QAction(self.buttonClearCache)
		self.actionClearCache.setShortcut(QtGui.QKeySequence('Alt+L') )
		self.actionClearCache.triggered.connect(self.onClearCache)
		self.buttonClearCache.addAction(self.actionClearCache)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		# connect signals
		Tc2Config.globalObject.initGui.connect(self.onInitGui)

	def toolTip(self):
		return 'FPPCalculator'

	def toolName(self):
		return 'FPPCalculator'

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
		grid.col(self.labelGameType).col(self.comboGameType).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.labelCurrency).col(self.comboCurrency).col(Tc2Config.HStretch())
		grid.row()
		grid.col(self.radioCash)
		grid.row()
		grid.col(self.radioFPPs)
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.labelAmount).col(self.editAmount).col(Tc2Config.HStretch())

		grid.row()
		grid.col(self.buttonCalculate).col(self.editResult).col(Tc2Config.HStretch())

		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.editCache, colspan=3)
		grid.row()
		grid.col(self.buttonClearCache)

		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def onInitGui(self):
		self.layout()

		vipStatus = Tc2Config.settingsValue(self.SettingsKeyVIPStatus, '').toString()
		index = self.comboVIPStatus.findText(vipStatus, QtCore.Qt.MatchExactly)
		if index >= 0:
			self.comboVIPStatus.setCurrentIndex(index)
		self.comboVIPStatus.currentIndexChanged.connect(self.onComboVIPStatusCurrentIndexChanged)

		gameType = Tc2Config.settingsValue(self.SettingsKeyGameType, '').toString()
		index = self.comboGameType.findText(gameType, QtCore.Qt.MatchExactly)
		if index >= 0:
			self.comboGameType.setCurrentIndex(index)
		self.comboGameType.currentIndexChanged.connect(self.onComboGameTypeCurrentIndexChanged)

		currency = Tc2Config.settingsValue(self.SettingsKeyCurrency, '').toString()
		index = self.comboCurrency.findText(currency, QtCore.Qt.MatchExactly)
		if index >= 0:
			self.comboCurrency.setCurrentIndex(index)
		self.comboCurrency.currentIndexChanged.connect(self.onComboCurrencyCurrentIndexChanged)

		conversion =  Tc2Config.settingsValue(self.SettingsKeyConversion, '').toString()
		if conversion == 'FPPs':
			self.radioFPPs.setChecked(True)
		else:
			self.radioCash.setChecked(True)

	def onComboVIPStatusCurrentIndexChanged(self, index):
		vipStatus = self.comboVIPStatus.itemText(index)
		Tc2Config.settingsSetValue(self.SettingsKeyVIPStatus, vipStatus)

	def onComboGameTypeCurrentIndexChanged(self, index):
		gameType = self.comboGameType.itemText(index)
		Tc2Config.settingsSetValue(self.SettingsKeyGameType, gameType)

	def onComboCurrencyCurrentIndexChanged(self, index):
		currency = self.comboCurrency.itemText(index)
		Tc2Config.settingsSetValue(self.SettingsKeyCurrency, currency)

	def onButtonGroupConversionButtonClicked(self, button):
		Tc2Config.settingsSetValue(self.SettingsKeyConversion, 'Cash' if button is self.radioCash else 'FPPs')

	def onEditAmountTextChanged(self, text):
		self.buttonCalculate.setEnabled(bool(text))

	def onCalculate(self):
		v = self.comboVIPStatus.itemData(self.comboVIPStatus.currentIndex())
		vipMultiplier = v.toDouble()[0]
		vipStatusName = self.comboVIPStatus.currentText()
		gameType =  self.comboGameType.currentText()
		gameTypeMultiplier = None
		currency = None
		for tmp_gameType, data in GameTypes:
			if tmp_gameType == gameType:
				#NOTE: fo some reason QString € does not compare equal to python string €
				currency = unicode(self.comboCurrency.currentText().toUtf8(), 'utf-8')
				for tmp_currency, tmp_multiplier in data:
					if tmp_currency == currency:
						gameTypeMultiplier = tmp_multiplier
						break
				else:
					raise ValueError('game type currency not found')
				break
		else:
			raise ValueError('game type multiplier not found')
		toCash = self.radioCash.isChecked()
		amount = float(self.editAmount.text())
		if toCash:
			result = amount / gameTypeMultiplier / vipMultiplier
		else:
			result = amount * gameTypeMultiplier * vipMultiplier
		self.editResult.setText('%.2f' % result)
		text = '%s / %s -- %s %s == %s %s' % (
				vipStatusName,
				gameType,
				'fpp' if toCash else currency,
				Tc2Config.locale.toString(amount, 'f', 2),
				currency if toCash else 'fpp',
				Tc2Config.locale.toString(result, 'f', 2),
				)
		self.editCache.appendPlainText(text)
		self.buttonClearCache.setEnabled(True)

	def onClearCache(self):
		self.editCache.clear()
		self.buttonClearCache.setEnabled(False)

	def onHelp(self):
		Tc2GuiHelp.dialogHelp('toolsFPPCalculator', parent=self)
















