#************************************************************************************
# MIT License - Copyright (c) 20012-2013 Juergen Urner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#************************************************************************************

'''-------------------------------------------------------------------------------------
Bankroll.py - a Gui for keeping track of your sessions
-------------------------------------------------------------------------------------

WARNING: this Gui is highly experimental and very bare bones. so use at your own risk.

the Gui runs on linux only. the following packages should be installed on your machine:
- PyQt4
- PyQwt5

on ubuntu you install these by running the following command in your terminal:

sudo apt-get install python-qt4 python-qwt5-qt4


then start the Gui by running the following command:

python -B /path/to/GuiSessionEditor.py

--------
Usage:
--------
- create a text file and open it in the Gui (the two little dots next to the textbox)
- start adding sessions to the text file and hit the "Refresh" button to throw out
  a graph containing your wins and losses, session types and so on

what does a session entry look like?

MyHomeGame | EUR | 12.03.2012-20:35 | +120.50


..that is 4 parameters, separated by vertical bars
1 - the session type
2 - the currency. supported is USD, EUR, BTC (bitcoin)
3 - date and time of the session (day.month.year-hour:minute). Note that this thingy
    expects 4 digits for the year.
4 - ballance of the session. +amount or -amount

an example of multiple sessions and multiple session types:


MyHomeGame Tourney $4 | USD | 12.03.2012-20:35 | +120.50
MyHomeGame Tourney $4 | USD | 11.03.2012-20:35 | -4
MyHomeGame Tourney $4 | USD | 10.03.2012-20:35 | -4.00
MyHomeGame Tourney $4 | USD | 09.03.2012-20:35 | +12
MyHomeGame CashGame $2/4 | USD | 10.03.2012-20:35 | -65.00
MyHomeGame CashGame $2/4 | USD | 09.03.2012-20:35 | +96.50

you may comment out sessions by placing a # char at the start of the line

#MyHomeGame CashGame $2/4 | USD | 10.03.2012-20:35 | -65.00

you may comment out multiple sessions at once by using ##

MyHomeGame Tourney $4 | USD | 12.03.2012-20:35 | +120.50
## the following lines are commented out
MyHomeGame Tourney $4 | USD | 11.03.2012-20:35 | -4
MyHomeGame Tourney $4 | USD | 10.03.2012-20:35 | -4.00
## the following lines are commented in again
MyHomeGame Tourney $4 | USD | 09.03.2012-20:35 | +12

that's it.

---------
Notes:
---------

the Gui automatically creates backups of every file you open (32). they are stored in
a folder <YourFileName.txt.bck> in the directory the file resides. make shure nothing
evil can happen, you are on your own here.


some data needs to be stored for each file you work with. this data is associated to
the files name. so in case you work with multiple files, make shure each has a different,
unique name.


to retrieve exchange rates the Gui queries the following sites on every startup:

- http://api.bitcoincharts.com/v1/weighted_prices.json
  for bitcoin exchange rate. NOTE: the site has a limit of one query per 15 seconds.
  so don't push too hard, otherwise you may get banned.

- https://rate-exchange.appspot.com/currency?from=USD&to=EUR
  US dollar echange rate.

'''
from __future__ import with_statement
import os, calendar, operator, sys, codecs, re, json, shutil, time
from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as PyQwt
from urllib2 import urlopen

#************************************************************************************
# TODO: keyboard shortcuts / tab order
#
#************************************************************************************
Debug = 0

Version = '0.0.4'
Author = 'JuergenUrner'
ApplicationName = 'Bankroll'
ApplicationTitle = '%s-%s' % (ApplicationName, Version)
UrlopenTimeout = 3	# in seconds

class Currencies:
	BTC = 'BTC'
	EUR = 'EUR'
	USD = 'USD'
	All = sorted([i for i in dir() if not i.startswith('_')]); del i
	Default = EUR

#************************************************************************************
#
#************************************************************************************
def fetchBTC():
	error = ''
	result = 5.5
	if not Debug:
		try:
			p = urlopen(
				'http://api.bitcoincharts.com/v1/weighted_prices.json',
				timeout=UrlopenTimeout
				).read()
		except IOError:
			error = 'Could not fetch BTC exchange rate'
		else:
			result = float(json.loads(p)['EUR']['30d'])
	return error, result

def fetchEUR():
	return '', 1

def fetchUSD():
	error = ''
	result = 0.8
	if not Debug:
		try:
			p = urlopen(
				'https://rate-exchange.appspot.com/currency?from=USD&to=EUR',
				timeout=UrlopenTimeout
				).read()
		except IOError:
			error = 'Could not fetch USD exchange rate'
		else:
			result = float(json.loads(p)['rate'])
	return error, result


def getCurrentExchangeRates():
	CurrenciesMapping = (
		(Currencies.BTC, fetchBTC),
		(Currencies.EUR, fetchEUR),
		(Currencies.USD, fetchUSD),
		)
	rates = {}
	error = ''
	for currency, fetcher in CurrenciesMapping:
		error, rate = fetcher()
		rates[currency] = rate
	return error, rates

##print getCurrentExchangeRates()


#NOTE: this thingy is dangerous!
def backupFile(fileName, n=32):
	fileName = os.path.realpath(fileName)
	directory, name = os.path.split(fileName)
	directory = os.path.join(directory, name + '.bck')
	if not os.path.isdir(directory):
		os.makedirs(directory)

	names = os.listdir(directory)
	names.sort()
	if len(names) >= n:
		os.remove(os.path.join(directory, names[0]))

	t = time.time()
	t = time.gmtime(t)
	t = time.strftime('%Y.%m.%d-%H:%M:%S', t)
	shutil.copyfile(fileName, os.path.join(directory, t))

#************************************************************************************
#
#************************************************************************************
class SessionTypesWidget(QtGui.QTreeWidget):

	sessionTypesChanged = QtCore.pyqtSignal(QtGui.QWidget)

	ColorBallancePositive = QtGui.QColor('#3A39E3')
	ColorBallanceNegative = QtGui.QColor('#FF0000')

	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		self.setUniformRowHeights(True)
		self.setIndentation(0)
		self.setHeaderLabels(['SessionType', 'Ballance', 'Sessions'])
		self._sessionTypes = {}
		self._itemTotal = None
		self._curency = None
		self._connectSignals(True)

	def _connectSignals(self, flag):
		if flag:
			self.itemChanged.connect(self.onItemChanged)
			self.itemDoubleClicked.connect(self.onItemDoubleclicked)
		else:
			self.itemChanged.disconnect(self.onItemChanged)
			self.itemDoubleClicked.disconnect(self.onItemDoubleclicked)

	def _itemSetBallance(self, item, amount):
		if amount >= 0:
			item.setTextColor(1, self.ColorBallancePositive)
		else:
			item.setTextColor(1, self.ColorBallanceNegative)
		amount = '%.2f' % amount
		if not amount.startswith('-'):
			amount = '+' + amount
		item.setText(1, amount)

	def _adjustTotal(self):
		self._connectSignals(False)
		try:
			total = 0.0
			sessions = 0
			for sessionType in self._sessionTypes:
				item = sessionType['item']
				if item.checkState(0) == QtCore.Qt.Checked:
					total += sessionType[self._currency]
					sessions += sessionType['sessions']
			self._itemTotal.setText(2, '(%s)' % sessions)
			self._itemSetBallance(self._itemTotal, total)
		finally:
			self._connectSignals(True)

	def setSessionTypes(self, sessionTypes, currency):
		self._connectSignals(False)
		try:
			self.clear()
			self._sessionTypes = sessionTypes
			self._currency = currency
			sessionTypes.sort(key=operator.itemgetter('index'))
			for sessionType in sessionTypes:
				item = QtGui.QTreeWidgetItem(self)
				item.setText(0, sessionType['name'])
				amount = sessionType[currency]
				item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
				if sessionType['active']:
					item.setCheckState(0, QtCore.Qt.Checked)
				else:
					item.setCheckState(0, QtCore.Qt.Unchecked)
				item.setText(2, '(%s)' % sessionType['sessions'])
				self._itemSetBallance(item, amount)
				sessionType['item'] = item
			# add blank item + item for total
			item = QtGui.QTreeWidgetItem(self)
			self._itemTotal = QtGui.QTreeWidgetItem(self)
			self._itemTotal.setText(0, '#Total')
		finally:
			self._connectSignals(True)
		self._adjustTotal()
		self.sessionTypesChanged.emit(self)

	def setCurrency(self, currency):
		self._connectSignals(False)
		try:
			self._currency = currency
			for sessionType in self._sessionTypes:
				item = sessionType['item']
				amount = sessionType[currency]
				self._itemSetBallance(item, amount)
		finally:
			self._connectSignals(True)
		self._adjustTotal()
		self.sessionTypesChanged.emit(self)

	def sessionNamesActive(self):
		sessionNames = []
		for sessionType in self._sessionTypes:
			if sessionType['item'].checkState(0) == QtCore.Qt.Checked:
				sessionNames.append(sessionType['name'])
		return sessionNames

	def setSessionNamesActive(self, sessionNames):
		self._connectSignals(False)
		try:
			stateChanged = False
			for sessionType in self._sessionTypes:
				if sessionType['name'] in sessionNames:
					item = sessionType['item']
					if item.checkState(0) == QtCore.Qt.Unchecked:
						item.setCheckState(0, QtCore.Qt.Checked)
						stateChanged = True
		finally:
			self._connectSignals(True)
		self._adjustTotal()
		if stateChanged:
			self.sessionTypesChanged.emit(self)

	def setSessionNamesInactive(self, sessionNames):
		self._connectSignals(False)
		try:
			stateChanged = False
			for sessionType in self._sessionTypes:
				if sessionType['name'] in sessionNames:
					item = sessionType['item']
					if item.checkState(0) == QtCore.Qt.Checked:
						item.setCheckState(0, QtCore.Qt.Unchecked)
						stateChanged = True
		finally:
			self._connectSignals(True)
		self._adjustTotal()
		if stateChanged:
			self.sessionTypesChanged.emit(self)

	def sessionNamesInactive(self):
		sessionNames = []
		for sessionType in self._sessionTypes:
			if sessionType['item'].checkState(0) == QtCore.Qt.Unchecked:
				sessionNames.append(sessionType['name'])
		return sessionNames

	def headerState(self):
		return self.header().saveState()

	def restoreHeaderState(self, state):
		self.header().restoreState(state)

	#NOTE: Qt does not signal check state changes of tree items. use itemChanged()
	# instead. have to be careful to always disconnect signals accordingly (!!)
	def onItemChanged(self, item, i):
		self._adjustTotal()
		self.sessionTypesChanged.emit(self)

	def onItemDoubleclicked(self, item, i):
		for sessionType in self._sessionTypes:
			if sessionType['item'] is item:
				if item.checkState(0) == QtCore.Qt.Checked:
					item.setCheckState(0, QtCore.Qt.Unchecked)
				else:
					item.setCheckState(0, QtCore.Qt.Checked)
				break

#************************************************************************************
#
#************************************************************************************
class GraphWidget(PyQwt.QwtPlot):

	ColorCurve = QtGui.QColor('#3A39E3')
	ColorBackground = QtGui.QColor('#FFFFFF')

	def __init__(self, parent=None):
		PyQwt.QwtPlot.__init__(self, parent)
		self.setCanvasBackground(self.ColorBackground)
		grid = PyQwt.QwtPlotGrid()
		#grid.enableX(False)
		grid.setMajPen(QtGui.QPen(QtCore.Qt.lightGray, 0, QtCore.Qt.DashLine))
		grid.attach(self)
		self._curve = PyQwt.QwtPlotCurve("Curve")
		self._curve.setRenderHint(self._curve.RenderAntialiased)
		# try to find reasonable width for the graph line
		#w = QtGui.QFontMetrics(QtGui.QApplication.font()).lineWidth()
		w = 2
		pen = QtGui.QPen(self.ColorCurve, w)
		pen.setCosmetic(False)
		self._curve.setPen(pen)
		self._curve.attach(self)

	def setPoints(self, xs, ys):
		self._curve.setData(xs, ys)
		self.replot()

	def clear(self):
		self._curve.setData([], [])
		self.replot()

#************************************************************************************
#
#************************************************************************************
class SyntaxHighlighter(QtGui.QSyntaxHighlighter):

	StateNone = -1
	StateBlockComment = 1

	ColorComment = QtCore.Qt.darkGreen
	ColorBlockComment = QtCore.Qt.gray
	ColorError = QtCore.Qt.red

	def __init__( self, parent):
		QtGui.QSyntaxHighlighter.__init__( self, parent.document())
		self._errorLinenos = []

	def highlightBlock( self, text):

		# hilight block comments
		if self.previousBlockState() == self.StateNone:
			if text.startsWith('##'):
				self.setCurrentBlockState(self.StateBlockComment)
				fmt = QtGui.QTextCharFormat()
				fmt.setForeground(self.ColorBlockComment)
				self.setFormat(0, text.length(), fmt)
				return
			else:
				self.setCurrentBlockState(self.StateNone)
		elif self.previousBlockState() == self.StateBlockComment:
			if text.startsWith('##'):
				self.setCurrentBlockState(self.StateNone)
				fmt = QtGui.QTextCharFormat()
				fmt.setForeground(self.ColorBlockComment)
				self.setFormat(0, text.length(), fmt)
				return
			else:
				self.setCurrentBlockState(self.StateBlockComment)
				fmt = QtGui.QTextCharFormat()
				fmt.setForeground(self.ColorBlockComment)
				self.setFormat(0, text.length(), fmt)
				return

		# hilight comments
		if text.startsWith('#'):
			fmt = QtGui.QTextCharFormat()
			fmt.setForeground(self.ColorComment)
			self.setFormat(0, text.length(), fmt)
			return

		# hilight errors
		if self.currentBlock().firstLineNumber() in self._errorLinenos:
			fmt = QtGui.QTextCharFormat()
			fmt.setBackground(self.ColorError)
			self.setFormat(0, text.length(), fmt)

	def setErrorLinenos(self, linenos):
		if not self._errorLinenos and not linenos:
			return
		self._errorLinenos = linenos
		self.setDocument(self.document())

#************************************************************************************
#
#************************************************************************************
class ErrorLinenoTimer(QtCore.QTimer):

		def __init__(self, edit, lineno):
			QtCore.QTimer.__init__(self, edit)
			self.setSingleShot(True)
			self.timeout.connect(self.onTimeout)
			self._edit = edit
			self.lineno = lineno
			self.start(0)

		def onTimeout(self):
			cursor = self._edit.textCursor()
			cursor.movePosition(cursor.Down, cursor.MoveAnchor, self.lineno - cursor.blockNumber());
			self._edit.setTextCursor(cursor)
			self._edit.ensureCursorVisible()

#************************************************************************************
#
#************************************************************************************
class FrameSessionEditor(QtGui.QFrame):

	SettingsKeyCurrency = 'Gui/Curreny'
	SettingsKeyDlgOpenFileNameState = 'Gui/DlgOpenFileNameState'
	SettingsKeyDlgHelpGeometry = 'Gui/DlgHelpGeometry'
	SettingsKeyFileName = 'Gui/FileName'
	SettingsKeySessionStates = 'Gui/SessionStates'
	SettingsKeySessionTypesHeaderState = 'Gui/SessionTypesHeaderState'
	SettingsKeySplitterVState = 'Gui/SplitterVState'
	SettingsKeySplitterHState = 'Gui/SplitterHState'

	ErrMessage = '<div style="color: red;background-color: white;">%s</div>'


	CURRENCIES_FMT = {
			Currencies.BTC: '%.4f',
			Currencies.EUR: '%.2f',
			Currencies.USD: '%.2f',
			}

	def __init__(self, parent=None, backupSessionsFile=True):
		QtGui.QFrame.__init__(self, parent)

		self._splitterV = QtGui.QSplitter(QtCore.Qt.Vertical, self)
		self._splitterH = QtGui.QSplitter(QtCore.Qt.Horizontal, self)

		# setup graph pane
		self._graphWidget = GraphWidget(self)
		self._sessionTypesWidget = SessionTypesWidget(self)
		self._edit = QtGui.QPlainTextEdit(self)
		self._syntaxHighlighter = SyntaxHighlighter(self._edit)

		self._toolBar = QtGui.QToolBar(self)

		self._actionRefresh = QtGui.QAction(self)
		self._actionRefresh.setText('Refresh')
		self._actionRefresh.triggered.connect(self.refresh)
		self._toolBar.addAction(self._actionRefresh)

		self._actionSelectAll = QtGui.QAction(self)
		self._actionSelectAll.setText('SelectAll')
		self._actionSelectAll.triggered.connect(self.selectAllSessionTypes)
		self._toolBar.addAction(self._actionSelectAll)

		self._actionSelectNone = QtGui.QAction(self)
		self._actionSelectNone.setText('SelectNone')
		self._actionSelectNone.triggered.connect(self.selectNoneSessionTypes)
		self._toolBar.addAction(self._actionSelectNone)

		#self._labelCurrency = QtGui.QLabel('Currency:', self)
		#self._toolBar.addWidget(self._labelCurrency)

		self.comboCurrency = QtGui.QComboBox(self)
		self._toolBar.addWidget(self.comboCurrency)

		#self._labelFileName = QtGui.QLabel('File:', self)
		#self._toolBar.addWidget(self._labelFileName)

		self._editFileName = QtGui.QLineEdit(self)
		self._toolBar.addWidget(self._editFileName)
		self._editFileName.returnPressed.connect(self.onEditFileNameReturnPressed)

		self._actionSelectFileName = QtGui.QAction(self)
		self._actionSelectFileName.setText('..')
		self._actionSelectFileName.triggered.connect(self.onSelectFileName)
		self._toolBar.addAction(self._actionSelectFileName)

		self._actionHelp = QtGui.QAction(self)
		self._actionHelp.setText('Help')
		self._actionHelp.triggered.connect(self.onHelp)
		self._toolBar.addAction(self._actionHelp)

		self._statusBar = QtGui.QStatusBar(self)
		self._labelStatus = QtGui.QLabel('#Ready', self)
		self._statusBar.addWidget(self._labelStatus, 99)
		self._labelInfo = QtGui.QLabel('Info', self)
		self._statusBar.addWidget(self._labelInfo)

		self._settings = None
		self._sessions = []
		self._exchangeRates = {}
		self._exchangeRatesError = ''
		self._fileName = ''
		self._sessionStates = {}
		self._backupSessionsFile = backupSessionsFile

	def layout(self):

		self.setContentsMargins(0, 0, 0, 0)

		box0 = QtGui.QVBoxLayout(self)

		box0.addWidget(self._splitterH)

		self._splitterH.addWidget(self._sessionTypesWidget)
		self._splitterH.addWidget(self._splitterV)

		self._splitterV.addWidget(self._graphWidget)
		self._splitterV.addWidget(self._edit)

		box0.addWidget(self._toolBar)
		box0.addWidget(self._statusBar)

		box0.setStretch(0, 99)

	def currency(self):
		return str(self.comboCurrency.currentText())

	SessionPat = re.compile('''
			^(?P<name>[^|]+?)
			\s*\|\s*
			(?P<currency>%s)
			\s*\|\s*
			(?P<day>\d{1,2})\.
			(?P<month>\d{1,2})\.
			(?P<year>\d\d\d\d)\-
			(?P<hour>\d{1,2})\:
			(?P<minute>\d{1,2})
			\s*\|\s*
			(?P<amount>[\-\+]?[\d\.\,]+?)
			\s*
			$
			''' % '|'.join(Currencies.All), re.X|re.I|re.U)
	def loadSessions(self):
		self._sessions = []
		sessionTypes = {}
		sessionTypeCount = 0
		stateInfo = self._sessionStates.get(str(hash(os.path.basename(self._fileName))), [])
		blockComment = False
		errors = []
		text = unicode(self._edit.toPlainText().toUtf8(), 'utf-8')
		for lineno, line in enumerate(text.split('\n')):
			line = line.strip()
			if not line:
				continue
			if blockComment:
				if line.startswith('##'):
					blockComment = False
				continue
			if line.startswith('##'):
				blockComment = True
				continue
			if line.startswith('#'):
				continue

			m = self.SessionPat.match(line)
			if m is None:
				errors.append(lineno)
				continue

			# errcheck session entries
			date = [int(m.group(i)) for i in ('year','month','day','hour','minute')] + [0, ]
			try:
				date = calendar.timegm(date)
			except ValueError:
				errors.append(lineno)
				continue
			amount = m.group('amount').replace(',', '.')	# allow ',' or '.' as float sep
			try:
				amount = float(amount)
			except ValueError:
				errors.append(lineno)
				continue
			currency = m.group('currency')

			# setup session item
			session = {
					'date': date,
					'name': m.group('name'),
					'amount': amount,
					'currency': currency
					}

			# setup session type item
			# NOTE: we setup these items here, not in SessionTypesWidget because we'd
			# have to iterate multiple times over our session items. uglier but faster
			# as is.
			sessionType = sessionTypes.get(session['name'], None)
			if sessionType is None:
				sessionType = {
						'name': session['name'],
						'index': sessionTypeCount,
						'active': hash(session['name']) not in stateInfo,
						'sessions': 0,
						}
				sessionTypes[session['name']] = sessionType
				sessionTypeCount += 1
			sessionType['sessions'] += 1

			# add amount/currency to each item
			eur = amount * self._exchangeRates[currency]
			for currency in self._exchangeRates:
				amount = eur / self._exchangeRates[currency]
				session[currency] = amount
				if currency not in sessionType:
					sessionType[currency] = 0.0
				sessionType[currency] += amount
			self._sessions.append(session)

		# errorcheck
		self._syntaxHighlighter.setErrorLinenos(errors)
		if errors:
			self._sessions = []
			if len(errors) == 1:
				msg = '#Error: 1 invalid session entry'
			else:
				msg = '#Error: %s invalid session entries' % len(errors)
			self.feedbackError(msg)
			self._sessions = []
			#NOTE: have to use a timer here, otherwise syntax highlighter does not work
			ErrorLinenoTimer(self._edit, errors[0])
		else:
			self.feedbackStatus('#Ready: %s' % os.path.basename(self._fileName))

		# finally
		self._sessions.sort(key=operator.itemgetter('date'))
		self._sessionTypesWidget.setSessionTypes(sessionTypes.values(), self.currency())

	def loadSessionsFile(self, fileName):

		if not fileName:
			self._edit.setReadOnly(True)
			self._edit.setPlainText('')
			self._sessionTypesWidget.clear()
			self._graphWidget.clear()
			self.feedbackStatus('#Ready:')
			return

		self._edit.textChanged.disconnect(self.onEditTextChanged)
		try:
			with codecs.open(fileName, 'r', 'UTF-8') as fp:
				self._edit.setPlainText(fp.read())
				self._edit.setReadOnly(False)
				self.feedbackStatus('#Ready:')
				self.loadSessions()
				if self._backupSessionsFile:
					backupFile(fileName)
		except IOError:
			self._edit.setPlainText('')
			self._edit.setReadOnly(True)
			self._sessions = []
			self.loadSessions()
			self.feedbackError('#Error: could not load sessions file')
		finally:
			self._edit.textChanged.connect(self.onEditTextChanged)

	def feedbackError(self, msg):
		self._labelStatus.setText(self.ErrMessage % msg)

	def feedbackStatus(self, msg):
		self._labelStatus.setText(msg)

	def feedbackInfo(self):
		if self._exchangeRatesError:
			msg = 'Error: %s' % self._exchangeRatesError
		else:
			currencyCurrent = str(self.comboCurrency.currentText())
			rate = self._exchangeRates[currencyCurrent]
			msg = '%s=' % currencyCurrent.lower()
			for currency in sorted(self._exchangeRates):
				if currency == currencyCurrent:
					continue
				rate2 = self._exchangeRates[currency]
				msg += self.CURRENCIES_FMT[currency] % (rate / rate2)
				msg += currency.lower()
			msg = msg[:-2]
		self._labelInfo.setText(msg)

	def refresh(self):
		self.loadSessions()

	def handleFontChanged(self, font):
		self._graphWidget.setAxisFont(self._graphWidget.yLeft, font)
		self._graphWidget.setAxisFont(self._graphWidget.xBottom, font)

	def selectAllSessionTypes(self):
		inactive = self._sessionTypesWidget.sessionNamesInactive()
		self._sessionTypesWidget.setSessionNamesActive(inactive)
		self.saveSessionStates()

	def selectNoneSessionTypes(self):
		active = self._sessionTypesWidget.sessionNamesActive()
		self._sessionTypesWidget.setSessionNamesInactive(active)
		self.saveSessionStates()

	#NOTE: this is a pretty crappy impl of associating state info to a file
	# main point is: i want to avoid using a database at any cost. so we associate
	# state data to a file by its file name (hash). this obv breaks when two different
	# files have the same name. but imo this is ok when a) amount of state data is minimal
	# b) not much harm is done and c) we can keep plain text files as storage.
	#
	# state data is stored as json'ed dict or lists:
	#
	# {szFileBasenameHash: [iHashUncheckedSessionName1, ..N, szTimeStamp], }
	#
	# oldest entries are removed when MaxSessionStates items is exceeded

	MaxSessionStates = 64

	def loadSessionStates(self):
		p = str(self._settings.value(self.SettingsKeySessionStates, '').toString())
		try:
			self._sessionStates = json.loads(p)
		except ValueError:
			self._sessionStates = {}

	def saveSessionStates(self):
		key = str(hash(os.path.basename(self._fileName)))
		inactive = self._sessionTypesWidget.sessionNamesInactive()
		self._sessionStates[key] = [hash(i) for i in inactive] + [str(time.time())]
		if len(self._sessionStates) > self.MaxSessionStates:
			remove = []
			for key, values in self._sessionStates.items():
				t = float(values[-1])
				remove.append((t, key))
			remove.sort()
			while len(remove) > self.MaxSessionStates:
				t, key = remove.pop(0)
				del self._sessionStates[key]
		self._settings.setValue(self.SettingsKeySessionStates, json.dumps(self._sessionStates))

	def saveSettings(self):
		self._settings.setValue(self.SettingsKeySplitterVState, self._splitterV.saveState())
		self._settings.setValue(self.SettingsKeySplitterHState, self._splitterH.saveState())
		self._settings.setValue(self.SettingsKeySessionTypesHeaderState, self._sessionTypesWidget.headerState())

	def restoreSettings(self, qSettings):
		self._settings = qSettings

		self._exchangeRatesError, self._exchangeRates = getCurrentExchangeRates()
		self._fileName = unicode(self._settings.value(self.SettingsKeyFileName).toString().toUtf8(), 'utf8')

		self._sessionTypesWidget.restoreHeaderState(self._settings.value(self.SettingsKeySessionTypesHeaderState).toByteArray())
		self._splitterV.restoreState(qSettings.value(self.SettingsKeySplitterVState).toByteArray())
		self._splitterH.restoreState(qSettings.value(self.SettingsKeySplitterHState).toByteArray())

		self.comboCurrency.addItems(Currencies.All)
		currency = self._settings.value(self.SettingsKeyCurrency, Currencies.Default).toString()
		i = self.comboCurrency.findText(currency)
		self.comboCurrency.setCurrentIndex(i)

		# connect signals
		self._edit.textChanged.connect(self.onEditTextChanged)
		self.comboCurrency.currentIndexChanged.connect(self.onComboCurrencyCurentIndexChanged)
		self._sessionTypesWidget.sessionTypesChanged.connect(self.onSessionTypesChanged)

		self.loadSessionStates()
		self._editFileName.setText(self._fileName)
		self.loadSessionsFile(self._fileName)
		self.feedbackInfo()

	def onComboCurrencyCurentIndexChanged(self, i):
		currency = self.currency()
		self._settings.setValue(self.SettingsKeyCurrency, currency)
		self._sessionTypesWidget.setCurrency(currency)
		self.feedbackInfo()

	def onEditFileNameReturnPressed(self):
		if self._fileName:
			self._fileName = unicode(self._editFileName.text().toUtf8(), 'utf-8')
			self._settings.setValue(self.SettingsKeyFileName, self._fileName)
			self.loadSessionsFile(self._fileName)

	def onEditTextChanged(self):
		if self._fileName:
			with codecs.open(self._fileName, 'w', 'UTF-8') as fp:
				fp.write(unicode(self._edit.toPlainText().toUtf8(), 'utf-8'))

	def onHelp(self):
		dlg = QtGui.QDialog(self)
		dlg.setWindowTitle('%s-Help' % ApplicationName)
		dlg.edit = QtGui.QPlainTextEdit(dlg)
		dlg.edit.setPlainText(__doc__)
		dlg.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
		dlg.buttonBox.accepted.connect(dlg.accept)
		dlg.layout = QtGui.QVBoxLayout(dlg)
		dlg.layout.addWidget(dlg.edit)
		dlg.layout.addWidget(dlg.buttonBox)
		dlg.restoreGeometry(self._settings.value(self.SettingsKeyDlgHelpGeometry, QtCore.QByteArray()).toByteArray() )
		dlg.exec_()
		self._settings.setValue(self.SettingsKeyDlgHelpGeometry, dlg.saveGeometry())

	def onSelectFileName(self):
		dlg = QtGui.QFileDialog(self)
		dlg.setAcceptMode(dlg.AcceptOpen)
		dlg.setWindowTitle('%s: Open sessions file' % ApplicationName)
		p = QtCore.QStringList()
		for i in ('text Files (*.txt)', 'All Files (*)'):
			p << i
		dlg.setNameFilters(p)
		dlg.restoreState(self._settings.value(self.SettingsKeyDlgOpenFileNameState, QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		if result == dlg.Accepted:
			self._settings.setValue(self.SettingsKeyDlgOpenFileNameState, dlg.saveState())
			self._fileName = unicode(dlg.selectedFiles()[0].toUtf8(), 'utf-8')
			self._settings.setValue(self.SettingsKeyFileName, self._fileName)
			self._editFileName.setText(self._fileName)
			self.loadSessionsFile(self._fileName)

	def onSessionTypesChanged(self, sessionTypesWidget):
		currency = self.currency()
		active = sessionTypesWidget.sessionNamesActive()
		inactive = sessionTypesWidget.sessionNamesInactive()
		xs = [0, ]
		ys = [0.0, ]
		for session in self._sessions:
			if session['name'] in active:
				amount = session[currency]
				ys.append(ys[-1] + amount)
				xs.append(len(xs))
		self._graphWidget.setPoints(xs, ys)
		self.saveSessionStates()
		self._actionSelectNone.setEnabled(bool(active))
		self._actionSelectAll.setEnabled(bool(inactive))

#************************************************************************************
#
#************************************************************************************
class SessionEditorWidget(QtGui.QMainWindow):

	SettingsKeyGeometry = 'Gui/Geometry'
	SettingsKeyState = 'Gui/State'

	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self._frameSessionEditor = FrameSessionEditor(self)
		self.setCentralWidget(self._frameSessionEditor)
		self.setWindowTitle(ApplicationTitle)
		self._settings = QtCore.QSettings(Author, ApplicationName)

		self._frameSessionEditor.layout()
		self._frameSessionEditor.restoreSettings(self._settings)
		self.restoreState(self._settings.value(self.SettingsKeyState).toByteArray())
		self.restoreGeometry(self._settings.value(self.SettingsKeyGeometry).toByteArray())

	def closeEvent(self, event):
		self._settings.setValue(self.SettingsKeyState, self.saveState())
		self._settings.setValue(self.SettingsKeyGeometry, self.saveGeometry())
		self._frameSessionEditor.saveSettings()
		return QtGui.QMainWindow.closeEvent(self, event)

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = SessionEditorWidget()
	gui.show()
	application.exec_()
