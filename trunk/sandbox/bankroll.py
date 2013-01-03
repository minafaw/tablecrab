'''
Copyright (c) 20012 Juergen Urner

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

-------------------------------------------------------------------------------------
Bankroll.py - a Gui for keeping track of your sessions
-------------------------------------------------------------------------------------

WARNING: this Gui is highly experimental and very bare bones. so use at your own risk.



the Gui runs on linux only. the following packages should be installed on your machine:
- PyQt4
- PyQwt5

on ubuntu you install these by running the following command in your terminal:


sudo apt-get install python-qt4 python-qwt5-qt4


then start the Gui by running the following command:


python -B /path/to/bankroll.py

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
2 - the currency. supported is USD, EUR, BTC (bitcoin) uppercase!
3 - date and time of the session (day.month.year-hour:minute). Note that this thingy
    is very strict, it expects eactly 2 or 4 digits in date/time.
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

the Gui automatically creates backups of every file you open (20). they are stored in
a folder <YourFileName.txt.bck> in the directory the file resides. make shure nothing
evil can happen, you are on your own here.


some data needs to be stored for each file you work with. this data is associated to
the files name. so in case you work with multiple files, make shure each has a different,
unique name.


to retrieve exchange rates the Gui queries the following sites on every startup:

- https://mtgox.com/api/1/BTCEUR/ticker
  for bitcoin exchange rate. NOTE: mount gox has a limit of one query per 15 seconds.
  so don't push too hard, otherwise you may get banned.

- https://rate-exchange.appspot.com/currency?from=USD&to=EUR
  for US dollar echange rate

'''

from __future__ import with_statement
import os, calendar, operator, sys, codecs, re, json, shutil, time
from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as PyQwt
from urllib2 import urlopen

#************************************************************************************
#
#************************************************************************************

Version = '0.0.1'
Author = 'JuergenUrner'
ApplicationName = 'Bankroll'
ApplicationTitle = '%s-%s' % (ApplicationName, Version)

UrlopenTimeout = 3	# in seconds
Debug = True


def fetchBTC():
	error = ''
	result = 5.5
	if not Debug:
		try:
			p = urlopen('https://mtgox.com/api/1/BTCEUR/ticker', timeout=UrlopenTimeout).read()
		except IOError:
			error = 'Could not fetch BTC exchange rate'
		else:
			result = float(json.loads(p)['return']['high']['value'])
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
			result = json.loads(p)['rate']
	return error, result

Currencies = (
		('BTC', fetchBTC),
		('EUR', fetchEUR),
		('USD', fetchUSD),
		)
CurrencyDefault = 'EUR'

def getCurrentExchangeRates():
	rates = {}
	error = ''
	for currency, fetcher in Currencies:
		error, rate = fetcher()
		rates[currency] = rate
	return error, rates

##getCurrentExchangeRates()
class ParseError(Exception): pass


#NOTE: this thingy is dangerous!
def backupFile(fileName, n=20):
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
class SyntaxHighlighter(QtGui.QSyntaxHighlighter):

	StateNone = -1
	StateBlockComment = 1

	ColorComment = QtCore.Qt.darkGreen
	ColorBlockComment = QtCore.Qt.gray
	ColorError = QtCore.Qt.red

	def __init__( self, parent):
		QtGui.QSyntaxHighlighter.__init__( self, parent.document())
		self.errorLinenos = []

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
		if self.currentBlock().firstLineNumber() in self.errorLinenos:
			fmt = QtGui.QTextCharFormat()
			fmt.setBackground(self.ColorError)
			self.setFormat(0, text.length(), fmt)

	def setErrorLinenos(self, linenos):
		if not self.errorLinenos and not linenos:
			return
		self.errorLinenos = linenos
		self.setDocument(self.document())


class FrameBankroll(QtGui.QFrame):

	SettingsKeySplitterVState = 'Gui/SplitterVState'
	SettingsKeySplitterHState = 'Gui/SplitterHState'

	SettingsKeyTreeHeaderState = 'Gui/TreeState'
	SettingsKeySessionNamesUnchecked = 'Gui/SessionNamesUnchecked'
	SettingsKeyCurrency = 'Gui/Curreny'
	SettingsKeyFileName = 'Gui/FileName'
	SettingsKeyDlgOpenFileNameState = 'Gui/DlgOpenFileNameState'
	SettingsKeySessionStates = 'Gui/SessionStates'


	ColorCurve = '#3A39E3'
	ColorBackground = '#FFFFFF'

	ErrMessage = '<div style="color: red;background-color: white;">%s</div>'

	class ErrorLinenoTimer(QtCore.QTimer):
		def __init__(self, edit, lineno):
			QtCore.QTimer.__init__(self, edit)
			self.setSingleShot(True)
			self.timeout.connect(self.onTimeout)
			self.edit = edit
			self.lineno = lineno
			self.start(0)
		def onTimeout(self):
			cursor = self.edit.textCursor()
			cursor.movePosition(cursor.Down, cursor.MoveAnchor, self.lineno - cursor.blockNumber());
			self.edit.setTextCursor(cursor)
			self.edit.ensureCursorVisible()


	class TreeWidgetItem(QtGui.QTreeWidgetItem):

		ColorBallancePositive = '#3A39E3'
		ColorBallanceNegative = '#FF0000'

		TypeSession = 0
		TypeTotal = 1

		def __init__(self, parent, name='', type=TypeSession):
			QtGui.QTreeWidgetItem.__init__(self, parent)
			self.setText(0, name)
			self._type = type
			self._name = name
			if self._type == self.TypeSession:
				self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable)
				self.setCheckState(0, QtCore.Qt.Checked)
			else:
				self.setFlags(self.flags() &~QtCore.Qt.ItemIsUserCheckable)
			self._total = 0.0

		def addToTotal(self, n):
			self._total += n

		def setTotal(self, n):
			self._total = n
			self.setTextColor(1,
						QtGui.QColor(self.ColorBallanceNegative if self._total < 0 else self.ColorBallancePositive)
						)
			text = '%.2f' % n
			if not text.startswith('-'):
				text = '+' + text
			self.setText(1, text)

		def setChecked(self, flag):
			self.setCheckState(0, QtCore.Qt.Checked if flag else QtCore.Qt.Unchecked)

		def isChecked(self):
			return self.checkState(0) == QtCore.Qt.Checked

		def total(self):
			return self._total

		def type(self):
			return self._type

		def name(self):
			return self._name


	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.splitterV = QtGui.QSplitter(QtCore.Qt.Vertical, self)
		self.splitterH = QtGui.QSplitter(QtCore.Qt.Horizontal, self)

		# setup graph pane
		self.graph = PyQwt.QwtPlot(self)
		self.graph.setCanvasBackground(QtGui.QColor(self.ColorBackground))

		grid = PyQwt.QwtPlotGrid()
		grid.enableX(False)
		grid.setMajPen(QtGui.QPen(QtCore.Qt.lightGray, 0, QtCore.Qt.DashLine))
		grid.attach(self.graph)

		self.curve = None
		self.settings = None

		self.tree = QtGui.QTreeWidget(self)
		self.tree.setUniformRowHeights(True)
		self.tree.setIndentation(0)
		self.tree.setHeaderLabels(['SessionType', 'Ballance'])

		self.toolBar = QtGui.QToolBar(self)

		self.actionRefresh = QtGui.QAction(self)
		self.actionRefresh.setText('Refresh')
		self.actionRefresh.triggered.connect(self.refresh)
		self.toolBar.addAction(self.actionRefresh)

		self.actionSelectAll = QtGui.QAction(self)
		self.actionSelectAll.setText('SelectAll')
		self.actionSelectAll.triggered.connect(self.selectAllSessionTypes)
		self.toolBar.addAction(self.actionSelectAll)

		self.actionSelectNone = QtGui.QAction(self)
		self.actionSelectNone.setText('SelectNone')
		self.actionSelectNone.triggered.connect(self.selectNoneSessionTypes)
		self.toolBar.addAction(self.actionSelectNone)

		self.labelCurrency = QtGui.QLabel('Currency:', self)
		self.toolBar.addWidget(self.labelCurrency)

		self.comboCurrency = QtGui.QComboBox(self)
		self.toolBar.addWidget(self.comboCurrency)

		self.labelFileName = QtGui.QLabel('File:', self)
		self.toolBar.addWidget(self.labelFileName)

		self.editFileName = QtGui.QLineEdit(self)
		self.toolBar.addWidget(self.editFileName)
		self.editFileName.returnPressed.connect(self.onEditFileNameReturnPressed)


		self.actionSelectFileName = QtGui.QAction(self)
		self.actionSelectFileName.setText('..')
		self.actionSelectFileName.triggered.connect(self.onselectFileName)
		self.toolBar.addAction(self.actionSelectFileName)

		self.labelStatus = QtGui.QLabel('#Ready', self)
		self.labelInfo = QtGui.QLabel('Info', self)

		# setup editor pane
		self.editIsDirty = False
		self.edit = QtGui.QPlainTextEdit(self)
		self.syntaxHighlighter = SyntaxHighlighter(self.edit)
		self.sessions = []

		self.exchangeRates = {}
		self.exchangeRatesError = ''

		self.fileName = ''
		self.sessionStates = {}

	def layout(self):

		self.setContentsMargins(0, 0, 0, 0)

		box0 = QtGui.QVBoxLayout(self)
		box0.addWidget(self.splitterV)

		self.splitterV.addWidget(self.edit)
		self.splitterV.addWidget(self.splitterH)

		self.splitterH.addWidget(self.tree)
		self.splitterH.addWidget(self.graph)

		box0.addWidget(self.toolBar)

		box2 = QtGui.QHBoxLayout()
		box0.addLayout(box2)
		box2.addWidget(self.labelStatus)
		box2.addWidget(self.labelInfo)


	def connectTreeSignals(self, flag):
		if flag:
			self.tree.itemChanged.connect(self.onTreeItemChanged)
			self.tree.itemDoubleClicked.connect(self.onTreeItemDoubleclicked)
		else:
			self.tree.itemChanged.disconnect(self.onTreeItemChanged)
			self.tree.itemDoubleClicked.disconnect(self.onTreeItemDoubleclicked)


	def loadGraph(self):
		if self.curve is not None:
			self.curve.detach()
		currencyCurrent = str(self.comboCurrency.currentText())
		self.curve = PyQwt.QwtPlotCurve("Curve 2")
		self.curve.setRenderHint(self.curve.RenderAntialiased)
		pen = QtGui.QPen(QtGui.QColor(self.ColorCurve), 2)
		pen.setCosmetic(False)
		self.curve.setPen(pen)
		x = 0
		y = 0
		xs = [0, ]
		ys = [0, ]

		root = self.tree.invisibleRootItem()
		items = [root.child(i) for i in range(root.childCount())]
		items = [item.name() for item in items if item.type() == item.TypeSession and item.isChecked()]
		for session in self.sessions:
			if session['name'] in items:
				x += 1
				y += session[currencyCurrent]
				xs.append(x)
				ys.append(y)
		self.curve.setData(xs, ys)
		self.curve.attach(self.graph)
		self.graph.replot()



	SessionPat = re.compile('''
			^(?P<name>[^|]+?)
			\s*\|\s*
			(?P<currency>%s)
			\s*\|\s*
			(?P<day>\d\d)\.
			(?P<month>\d\d)\.
			(?P<year>\d\d\d\d)\-
			(?P<hour>\d\d)\:
			(?P<minute>\d\d)
			\s*\|\s*
			(?P<amount>[\-\+]?[\d\.]+?)
			\s*
			$
			''' % '|'.join([i[0] for i in Currencies]), re.X|re.I|re.U)
	def loadSessions(self):
		self.sessions = []
		blockComment = False
		errors = []
		text = unicode(self.edit.toPlainText().toUtf8(), 'utf-8')
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

			#TODO: errchecks here
			date = [int(m.group(i)) for i in ('year','month','day','hour','minute')] + [0, ]
			date = calendar.timegm(date)
			currency = m.group('currency')
			amount =  float(m.group('amount')) * self.exchangeRates[currency]

			data = {
					'date': date,
					'name': m.group('name'),
					'amount': amount,
					'currency': currency
					}
			self.sessions.append(data)
			eur = float(m.group('amount')) * self.exchangeRates[currency]
			for currency in sorted(self.exchangeRates):
				amount = eur / self.exchangeRates[currency]
				data[currency] = amount

		self.syntaxHighlighter.setErrorLinenos(errors)
		if errors:
			if len(errors) == 1:
				msg = '#Error: 1 invalid session entry'
			else:
				msg = '#Error: %s invalid session entries' % len(errors)
			self.feedbackError(msg)
			self.sessions = []
			#NOTE: have to use a timer here, otherwise syntax highlighter does not work
			self.ErrorLinenoTimer(self.edit, errors[0])
		else:
			self.feedbackMessage('#Ready: %s' % os.path.basename(self.fileName))
		self.sessions.sort(key=operator.itemgetter('date'))


		self.connectTreeSignals(False)
		try:
			self.tree.clear()
			sessionNames = {}	# sessionType --> [TreeWidgetItem, ballance]
			currencyCurrent = str(self.comboCurrency.currentText())
			state = self.sessionStates.get(str(hash(os.path.basename(self.fileName))), [])

			# fill tree with session names
			for session in self.sessions:
				item = sessionNames.get(session['name'], None)
				if item is None:
					item = self.TreeWidgetItem(self.tree, name=session['name'], type=self.TreeWidgetItem.TypeSession)
					#
					if hash(item.name()) in state:
						item.setCheckState(0, QtCore.Qt.Unchecked)
					else:
						item.setCheckState(0, QtCore.Qt.Checked)
					sessionNames[session['name']] = item
				item.addToTotal(session[currencyCurrent])

			for item in sessionNames.values():
				item.setTotal(item.total())

			if self.sessions:
				# add item to display total
				item = self.TreeWidgetItem(self.tree, name='#Total', type=self.TreeWidgetItem.TypeTotal)
				self.adjustTreeTotal()
			self.loadGraph()
		except ParseError, d:
			QtGui.QMessageBox.critical(self, 'ParseError', d.message)

		finally:
			self.connectTreeSignals(True)


	def loadSessionsFile(self, fileName):
		self.edit.textChanged.disconnect(self.onEditTextChanged)
		try:
			with codecs.open(fileName, 'r', 'UTF-8') as fp:
				self.edit.setPlainText(fp.read())
				self.edit.setReadOnly(False)
				self.feedbackMessage('#Ready:')
				self.loadSessions()
				backupFile(fileName)
		except IOError:
			self.edit.setPlainText('')
			self.edit.setReadOnly(True)
			self.sessions = []
			self.loadSessions()
			self.feedbackError('#Error: could not load sessions file')
		finally:
			self.edit.textChanged.connect(self.onEditTextChanged)


	def feedbackError(self, msg):
		self.labelStatus.setText(self.ErrMessage % msg)

	def feedbackMessage(self, msg):
		self.labelStatus.setText(msg)


	def setFeedbackInfo(self):
		if self.exchangeRatesError:
			msg = 'Error: %s' % self.exchangeRatesError
		else:
			currencyCurrent = str(self.comboCurrency.currentText())
			rate = self.exchangeRates[currencyCurrent]
			msg = '1%s=' % currencyCurrent
			for currency in sorted(self.exchangeRates):
				if currency == currencyCurrent:
					continue
				rate2 = self.exchangeRates[currency]
				msg += '%.2f%s,' % (rate / rate2, currency)
			msg = msg[:-1]
		self.labelInfo.setText(msg)


	def refresh(self):
		self.loadSessions()


	def selectAllSessionTypes(self):
		self.connectTreeSignals(False)
		for i in xrange(self.tree.topLevelItemCount()):
			item = self.tree.topLevelItem(i)
			if item.flags() & QtCore.Qt.ItemIsUserCheckable:
				item.setCheckState(0, QtCore.Qt.Checked)
		#self.saveSessionNamesState()
		self.loadGraph()
		self.saveSessionStates()
		self.connectTreeSignals(True)


	def selectNoneSessionTypes(self):
		self.connectTreeSignals(False)
		for i in xrange(self.tree.topLevelItemCount()):
			item = self.tree.topLevelItem(i)
			if item.flags() & QtCore.Qt.ItemIsUserCheckable:
				item.setCheckState(0, QtCore.Qt.Unchecked)
		#self.saveSessionNamesState()
		self.loadGraph()
		self.saveSessionStates()
		self.connectTreeSignals(True)


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
		# load sessions state
		p = str(self.settings.value(self.SettingsKeySessionStates, '').toString())
		try:
			self.sessionStates = json.loads(p)
		except ValueError:
			self.sessionStates = {}


	def saveSessionStates(self):
		root = self.tree.invisibleRootItem()
		items = [root.child(i) for i in range(root.childCount())]
		items = [hash(item.name()) for item in items if item.type() == item.TypeSession and not item.isChecked()]
		key = str(hash(os.path.basename(self.fileName)))
		self.sessionStates[key] = items + [str(time.time())]

		if len(self.sessionStates) > self.MaxSessionStates:
			remove = []
			for key, values in self.sessionStates.items():
				t = float(values[-1])
				remove.append((t, key))
			remove.sort()
			while len(remove) > self.MaxSessionStates:
				t, key = remove.pop(0)
				del self.sessionStates[key]

		self.settings.setValue(self.SettingsKeySessionStates, json.dumps(self.sessionStates))


	def onselectFileName(self):
		dlg = QtGui.QFileDialog(self)
		dlg.setAcceptMode(dlg.AcceptOpen)
		dlg.setWindowTitle('%s: Open sessions file' % ApplicationName)
		p = QtCore.QStringList()
		for i in ('text Files (*.txt)', 'All Files (*)'):
			p << i
		dlg.setNameFilters(p)
		dlg.restoreState(self.settings.value(self.SettingsKeyDlgOpenFileNameState, QtCore.QByteArray()).toByteArray() )
		result = dlg.exec_()
		if result == dlg.Accepted:
			self.settings.setValue(self.SettingsKeyDlgOpenFileNameState, dlg.saveState())
			self.fileName = unicode(dlg.selectedFiles()[0].toUtf8(), 'utf-8')
			self.settings.setValue(self.SettingsKeyFileName, self.fileName)
			self.editFileName.setText(self.fileName)
			self.loadSessionsFile(self.fileName)


	def onComboCurrencyCurentIndexChanged(self, i):
		currency = self.comboCurrency.currentText()
		self.settings.setValue(self.SettingsKeyCurrency, currency)
		self.loadSessions()
		self.setFeedbackInfo()


	def onEditFileNameReturnPressed(self):
		self.fileName = unicode(self.editFileName.text().toUtf8(), 'utf-8')
		self.settings.setValue(self.SettingsKeyFileName, self.fileName)
		self.loadSessionsFile(self.fileName)


	def adjustTreeTotal(self):
		root = self.tree.invisibleRootItem()
		n = root.childCount()
		if n <= 0:
			return
		items = [root.child(i) for i in range(n)]
		itemTotal = [item for item in items if item.type() == item.TypeTotal][0]
		items = [item for item in items if item.type() == item.TypeSession]
		itemTotal.setTotal(0.0)
		for item in items:
			if item.isChecked():
				itemTotal.addToTotal(item.total())
		itemTotal.setTotal(itemTotal.total())


	#NOTE: Qt does not signal check state changes of tree items. use itemChanged() instead
	#      + have to be careful here.
	def onTreeItemChanged(self, item, i):
		self.connectTreeSignals(False)
		try:
			self.loadGraph()
			self.adjustTreeTotal()
			self.saveSessionStates()
		finally:
				self.connectTreeSignals(True)


	def onTreeItemDoubleclicked(self, item, i):
		if item.checkState(0) == QtCore.Qt.Checked:
			item.setCheckState(0, QtCore.Qt.Unchecked)
		else:
			item.setCheckState(0, QtCore.Qt.Checked)


	def onEditTextChanged(self):
		self.editIsDirty = True
		with codecs.open(self.fileName, 'w', 'UTF-8') as fp:
			fp.write(unicode(self.edit.toPlainText().toUtf8(), 'utf-8'))


	def saveSettings(self):
		self.settings.setValue(self.SettingsKeySplitterVState, self.splitterV.saveState())
		self.settings.setValue(self.SettingsKeySplitterHState, self.splitterH.saveState())
		self.settings.setValue(self.SettingsKeyTreeHeaderState, self.tree.header().saveState())


	def restoreSettings(self, qSettings):
		self.settings = qSettings
		self.tree.resizeColumnToContents(0)
		self.tree.header().restoreState(self.settings.value(self.SettingsKeyTreeHeaderState).toByteArray())

		self.comboCurrency.addItems(sorted([i[0] for i in Currencies]))
		currency = self.settings.value(self.SettingsKeyCurrency, CurrencyDefault).toString()
		i = self.comboCurrency.findText(currency)
		self.comboCurrency.setCurrentIndex(i)
		self.comboCurrency.currentIndexChanged.connect(self.onComboCurrencyCurentIndexChanged)

		self.exchangeRatesError, self.exchangeRates = getCurrentExchangeRates()
		self.connectTreeSignals(True)

		self.loadSessionStates()
		self.edit.textChanged.connect(self.onEditTextChanged)
		self.fileName = unicode(self.settings.value(self.SettingsKeyFileName).toString().toUtf8(), 'utf8')
		self.editFileName.setText(self.fileName)
		self.loadSessionsFile(self.fileName)

		self.setFeedbackInfo()
		self.splitterV.restoreState(qSettings.value(self.SettingsKeySplitterVState).toByteArray())
		self.splitterH.restoreState(qSettings.value(self.SettingsKeySplitterHState).toByteArray())




class BankrollWidget(QtGui.QMainWindow):

	SettingsKeyGeometry = 'Gui/Geometry'
	SettingsKeyState = 'Gui/State'

	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.frameBankroll = FrameBankroll(self)
		self.setCentralWidget(self.frameBankroll)
		self.setWindowTitle(ApplicationTitle)
		self.settings = QtCore.QSettings(Author, ApplicationName)

		self.frameBankroll.layout()
		self.frameBankroll.restoreSettings(self.settings)
		self.restoreState(self.settings.value(self.SettingsKeyState).toByteArray())
		self.restoreGeometry(self.settings.value(self.SettingsKeyGeometry).toByteArray())

	def closeEvent(self, event):
		self.settings.setValue(self.SettingsKeyState, self.saveState())
		self.settings.setValue(self.SettingsKeyGeometry, self.saveGeometry())
		self.frameBankroll.saveSettings()
		return QtGui.QMainWindow.closeEvent(self, event)

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = BankrollWidget()
	gui.show()
	application.exec_()
