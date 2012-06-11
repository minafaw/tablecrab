
import os
from PyQt4 import QtCore, QtGui, QtWebKit

#TODO:
# - filter history
# - remove current selection
# - sort column ascending/descending

#************************************************************************************
# resources
#************************************************************************************
def pixmapMagnifierMinus(cache=[]):
	if not cache:
		arr = QtCore.QByteArray.fromBase64(
			'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'
			'AABJRU5ErkJggg=='
			)
		px = QtGui.QPixmap()
		px.loadFromData(arr, "PNG")
		cache.append(px)
	return cache[0]

def pixmapMagnifierPlus(cache=[]):
	if not cache:
		arr = QtCore.QByteArray.fromBase64(
			'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'
			)
		px = QtGui.QPixmap()
		px.loadFromData(arr, "PNG")
		cache.append(px)
	return cache[0]

#************************************************************************************
# helper methods
#************************************************************************************
def uniqueName(names, name):
	uniqueName = name
	i = 0
	while True:
		if uniqueName not in names:
			break
		i += 1
		uniqueName = '%s (%s)' % (name, i)
	return uniqueName

#************************************************************************************
# filter header implementation
#************************************************************************************
#NOTE: mostly taken from: http://lists.qt.nokia.com/pipermail/qt-interest/2009-August/011654.html
class FilterHeader(QtGui.QHeaderView):

	FilterMargin = 1

	filterChanged = QtCore.pyqtSignal(QtCore.QString)

	class FilterComboBox(QtGui.QComboBox):
		def __init__(self, filterName, parent=None):
			QtGui.QComboBox.__init__(self, parent)
			self.filterName = filterName

	def __init__(self, filters, parent=None):
		QtGui.QHeaderView.__init__(self, QtCore.Qt.Horizontal, parent)
		self._filters = filters
		self._combos = []
		self._comboDict = {}
		self._comboForFilterHeight = None	# comboBox to determine filterbar height from
		for filterData in self._filters:
			if filterData['hasFilter']:
				combo =  self.FilterComboBox(filterData['filterName'], parent=self)
				combo.currentIndexChanged.connect(self.onFilterChanged)
				self._combos.append(combo)
				self._comboDict[filterData['filterName']] = combo
				self._comboForFilterHeight = combo
			else:
				self._combos.append(None)
				self._comboDict[filterData['filterName']] = None

		self.sectionResized.connect(self.onSectionResized)
		self.sectionMoved.connect(self.onSectionMoved)

	def filterHeight(self):
		if self._comboForFilterHeight is None:
			return 0
		return self._comboForFilterHeight.sizeHint().height()

	def sizeHint(self):
		size = QtGui.QHeaderView.sizeHint(self)
		size.setHeight(size.height() + self.filterHeight() + 2*self.FilterMargin)
		return size

	def updateGeometries(self):
		vg = self.viewport().geometry()
		self.setViewportMargins(0, 0, 0, self.filterHeight())
		QtGui.QHeaderView.updateGeometries(self)
		start = self.visualIndexAt(vg.left())
		if start < 0:
			start = 0
		end = self.visualIndexAt(vg.right())
		if end < 0:
			end = self.count() -1
		self.repositionFilterRow(start, end)

	def repositionFilterRow(self, start, end):
		for i in xrange(start, end+1):
			iLogical = self.logicalIndex(i)
			if self.isSectionHidden(iLogical):
				continue
			combo = self._combos[iLogical]
			if combo is not None:
				combo.move(self.sectionPosition(iLogical) - self.offset(), self.filterHeight())
				combo.resize(self.sectionSize(iLogical), self.filterHeight())

	def onSectionResized(self, iLogical, sizeOld, sizeNew):
		vg = self.viewport().geometry()
		start = self.visualIndex(iLogical)
		end = self.visualIndexAt(vg.right())
		if end < 0:
			end = self.count() -1
		self.repositionFilterRow(start, end)

	def onSectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
		self.repositionFilterRow(0, len(self._combos))

	def filterCurrent(self, filterName):
		combo = self._comboDict[filterName]
		if combo is not None:
			return unicode(self._comboDict[filterName].currentText().toUtf8(), 'utf-8')

	def filtersCurrent(self):
		return [
			(data['filterName'], self.filterCurrent(data['filterName']))
			for data in self._filters
			]

	def setFilterCurrent(self, filterName, value):
		combo = self._comboDict[filterName]
		if combo is not None:
			combo.currentIndexChanged.disconnect(self.onFilterChanged)
			i = combo.findText(value)
			combo.setCurrentIndex(i)
			combo.currentIndexChanged.connect(self.onFilterChanged)

	def filters(self, filterName):
		filters = []
		combo =  self._comboDict[filterName]
		if combo is not None:
			for i in xrange(combo.count()):
				text = unicode(combo.itemText(i).toUtf8(), 'utf-8')
				filters.append(text)
		return filters

	def setFilters(self, filterName, filters):
		combo = self._comboDict[filterName]
		if combo is not None:
			combo.currentIndexChanged.disconnect(self.onFilterChanged)
			combo.clear()
			combo.addItems(filters)
			combo.currentIndexChanged.connect(self.onFilterChanged)

	def onFilterChanged(self):
		combo = self.sender()
		self.filterChanged.emit(combo.filterName)

#************************************************************************************
# hand model implementation
#************************************************************************************
class HandModel(QtCore.QAbstractTableModel):
	def __init__(self, hands, filters, tableHands):
		QtCore.QAbstractTableModel.__init__(self, tableHands)
		self._tableHands = tableHands
		self._hands = hands
		self._filters = filters

	def rowCount(self, parent):
		return len(self._hands)

	def columnCount(self, parent):
		return len(self._filters)

	def data(self, index, role,
					QVariant=QtCore.QVariant,
					DisplayRole=QtCore.Qt.DisplayRole
					):
		if not index.isValid():
			return QVariant()
		elif role != DisplayRole:
			return QVariant()
		hand = self._hands[index.row()]
		value = getattr(hand, self._filters[index.column()]['filterName'])
		return QVariant(value)

	def headerData(self, col, orientation, role,
					QVariant=QtCore.QVariant,
					Horizontal=QtCore.Qt.Horizontal,
					DisplayRole=QtCore.Qt.DisplayRole,
					Vertical=QtCore.Qt.Vertical
					):
		if orientation == Horizontal and role == DisplayRole:
			return QVariant(self._filters[col]['headerText'])
		elif orientation == Vertical and role == DisplayRole:
			#NOTE: we want to display hand numbers in the vert header always starting
			# at 1. what we do here is pretty slow. have not found a cheap way to find
			# the visual index of a row.
			##return QVariant(str(col+1))	# Qts default row number handling
			n = 0
			isRowHidden = self._tableHands.isRowHidden
			for i in xrange(0, col+1):
				if not isRowHidden(i):
					n += 1
			return QVariant(str(n))
		return QVariant()

	def addHands(self, hands):
		i = len(self._hands) -1
		self.beginInsertRows(QtCore.QModelIndex(), i, i + len(hands) -1)
		self._hands.extend(hands)
		self.endInsertRows()

	def hands(self):
		return self._hands

	def hand(self, i):
		return self._hands[i]

	def indexHand(self, hand):
		return self._hands.index(hand)

#************************************************************************************
# history implementation
#************************************************************************************
class History(object):

	def __init__(self, maxItems=32):
		self._items = []
		self._currentItem = None
		self._maxItems = maxItems

	def addItem(self, item):
		if item in self._items:
			self._items.remove(item)
		self._items.append(item)
		self._currentItem = item
		self._items = self._items[-self._maxItems:]

	def currentItem(self):
		return self._currentItem

	def canGoBack(self):
		if self._items:
			i = self._items.index(self._currentItem)
			return i > 0
		return False

	def canGoForward(self):
		if self._items:
			i = self._items.index(self._currentItem)
			return i < len(self._items) -1
		return False

	def goBack(self):
		if not self._items:
			raise ValueError('can not go back in empty history')
		i = self._items.index(self._currentItem)
		if i == 0:
			raise ValueError('can not move beyound first item')
		self._currentItem = self._items[i-1]

	def goForward(self):
		if not self._items:
			raise ValueError('can not go forward in empty history')
		i = self._items.index(self._currentItem)
		if i == len(self._items) -1:
			raise ValueError('can not move beyound last item')
		self._currentItem = self._items[i+1]

	def maxItems(self):
		return self._maxItems

	def setMaxItems(self, n):
		self._maxItems = n
		self._items = self._items[-self._maxItems:]
		if self._currentItem is not None:
			if self._currentItem not in self._items:
				if self._items:
					self._currentItem = self._items[-1]
				else:
					self._currentItem = None

#************************************************************************************
# hand viewer implementation
#************************************************************************************
class FrameHandViewer(QtGui.QFrame):

	class EventFilterTableHands(QtCore.QObject):
		returnPressed = QtCore.pyqtSignal(QtCore.QModelIndex)
		def __init__(self, tableHands):
			QtCore.QObject.__init__(self, tableHands)
			self._tableHands = tableHands
			tableHands.installEventFilter(self)
		def eventFilter(self, obj, event):
			if event.type() == QtCore.QEvent.KeyPress:
				if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
					indexes = self._tableHands.selectionModel().selectedRows()
					if not indexes:
						return False
					self.returnPressed.emit(indexes[0])
					return True
			return False


	SettingsKeyBase = 'HandViewer/'
	SettingsKeySplitterState = SettingsKeyBase + 'SplitterState'
	SettingsKeyFilterHeaderState = SettingsKeyBase + 'FilterHeaderState'

	FilterAll = '*All'
	FilterReview = 'Review'
	FilterNoReview = 'NoReview'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self._hands = []
		self._history = History()
		self._sourceIdentifiers = {}
		self._sourceNames = {}
		self._filters = (
				{'filterName': '_handViewer_review', 'headerText': 'Review:', 'hasFilter': True},
				{'filterName': 'source', 'headerText': 'Source:', 'hasFilter': True},
				{'filterName': 'site', 'headerText': 'Site:', 'hasFilter': True},
				{'filterName': 'table', 'headerText': 'Table:', 'hasFilter': True},
				{'filterName': 'identifier', 'headerText': 'Hand:', 'hasFilter': False},
				)

		self._splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)

		self._tableHands = QtGui.QTableView(self)
		self._tableHands.setSelectionBehavior(self._tableHands.SelectRows)
		self._tableHands.setSelectionMode(self._tableHands.SingleSelection)
		self._filterHeader = FilterHeader(self._filters, parent=self._tableHands)
		self._tableHandsEventFilter = self.EventFilterTableHands(self._tableHands)
		self._filterHeader.setMovable(True)
		self._tableHands.setHorizontalHeader(self._filterHeader)
		self._filterHeader.setStretchLastSection(True)
		self._filterHeader.setDefaultAlignment(QtCore.Qt.AlignLeft)
		for filterData in self._filters:
			self._filterHeader.setFilters(filterData['filterName'], (self.FilterAll, ))

		self._handModel = HandModel([], self._filters, self._tableHands)
		self._tableHands.setModel(self._handModel)

		#
		self._handViewer = QtWebKit.QWebView(self)
		self._handViewer.setHtml('')

		# setup actions
		action = QtGui.QAction(self)
		action.setText('Back')
		keySequence = QtGui.QKeySequence(QtGui.QKeySequence.Back)
		action.setToolTip('Back (%s)' % keySequence.toString())
		action.setIcon(self._handViewer.pageAction(QtWebKit.QWebPage.Back).icon())
		action.setShortcut(keySequence)
		action.triggered.connect(self.onActionPreviousTriggered)
		self.addAction(action)
		self._actionPrevious = action

		action = QtGui.QAction(self)
		action.setText('Forward')
		keySequence = QtGui.QKeySequence(QtGui.QKeySequence.Forward)
		action.setToolTip('Forward (%s)' % keySequence.toString())
		action.setIcon(self._handViewer.pageAction(QtWebKit.QWebPage.Forward).icon())
		action.setShortcut(keySequence)
		action.triggered.connect(self.onActionNextTriggered)
		self.addAction(action)
		self._actionNext = action

		action = QtGui.QAction(self)
		action.setText('ZoomIn')
		action.setToolTip('ZoomIn (Ctrl++)')
		action.setIcon(QtGui.QIcon(pixmapMagnifierPlus()))
		action.setShortcut(QtGui.QKeySequence.ZoomIn)
		action.setAutoRepeat(True)
		action.triggered.connect(self.zoomIn)
		self.addAction(action)

		action = QtGui.QAction(self)
		action.setText('ZoomOut')
		action.setToolTip('ZoomOut (Ctrl+-)')
		action.setIcon(QtGui.QIcon(pixmapMagnifierMinus()))
		action.setShortcut(QtGui.QKeySequence.ZoomOut)
		action.setAutoRepeat(True)
		action.triggered.connect(self.zoomOut)
		self.addAction(action)

		# layout
		self._splitter.addWidget(self._tableHands)
		self._splitter.addWidget(self._handViewer)
		b = QtGui.QHBoxLayout(self)
		b.addWidget(self._splitter)

		# connect signals
		self._tableHandsEventFilter.returnPressed.connect(self.onItemDoubleClicked)
		self._tableHands.doubleClicked.connect(self.onItemDoubleClicked)
		self._tableHands.selectionModel().selectionChanged.connect(self.onSelectionChanged)
		self._filterHeader.filterChanged.connect(self.onFilterChanged)

		# init gui
		self.adjustActions()

	def addHand(self, hand):
		return self.addHands((hand, ))

	def addHands(self, hands):
		self._hands.extend(hands)
		# update our filters
		filterList = [(i['filterName'], [self.FilterAll, ]) for i in self._filters if i['hasFilter']]
		for filterName, filters in filterList:
			if filterName == '_handViewer_review':
				filters.extend((self.FilterReview, self.FilterNoReview))
				for hand in hands:
					hand._handViewer_review = ''
			else:
				myFilters = []
				for hand in hands:
					value = getattr(hand, filterName)
					if filterName == 'source':
						if hand.sourceType == hand.SourceTypeFile:
							myName = self._sourceNames.get(value, None)
							if myName is None:
								myName = 'file: ' + os.path.basename(value)
								myName = uniqueName(self._sourceIdentifiers, myName)
								self._sourceIdentifiers[myName] = value
								self._sourceNames[value] = myName
								value = myName
							else:
								value = myName
					if value not in myFilters:
						myFilters.append(value)
				myFilters.sort()
				filters.extend(myFilters)
			filterCurrent = self._filterHeader.filterCurrent(filterName)
			self._filterHeader.setFilters(filterName, filters)
			if filterCurrent in filters:
				self._filterHeader.setFilterCurrent(filterName, filterCurrent)
		self._handModel.addHands(hands)
		self.filterHands()

	def adjustActions(self):
		self._actionPrevious.setEnabled(self._history.canGoBack())
		self._actionNext.setEnabled(self._history.canGoForward())

	def filterHands(self):
		self._tableHands.setUpdatesEnabled(False)
		try:
			i = 0
			filtersCurrent = self._filterHeader.filtersCurrent()
			for i, hand in enumerate(self._handModel.hands()):
				handIsOk = True
				for filterName, filterCurrent in filtersCurrent:
					if filterCurrent is None:
						continue
					elif filterCurrent == self.FilterAll:
						continue
					elif filterName == '_handViewer_review':
						if filterCurrent == self.FilterNoReview and not hand._handViewer_review:
							continue
					elif filterName == 'source':
						myName = self._sourceIdentifiers.get(filterCurrent, None)
						if myName is not None:
							filterCurrent = myName
					if filterCurrent == getattr(hand, filterName):
						continue
					handIsOk = False
					break
				if handIsOk:
					self._tableHands.showRow(i)
				else:
					self._tableHands.hideRow(i)
		finally:
			self._tableHands.setUpdatesEnabled(True)

	def maxHistoryItems(self):
		return self._history.maxItems()

	def restoreSettings(self, qSettings):
		arr = qSettings.value(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray()
		self._splitter.restoreState(arr)
		arr = qSettings.value(self.SettingsKeyFilterHeaderState, QtCore.QByteArray()).toByteArray()
		self._filterHeader.restoreState(arr)

	def saveSettings(self, qSettings):
		qSettings.setValue(self.SettingsKeySplitterState, self._splitter.saveState())
		qSettings.setValue(self.SettingsKeyFilterHeaderState, self._filterHeader.saveState())

	def setMaxHistoryItems(self, n):
		return self._history.setMaxItems(n)

	def zoomIn(self):
		pass

	def zoomOut(self):
		pass

	def onActionNextTriggered(self):
		self._history.goForward()
		hand = self._history.currentItem()
		self._handViewer.setHtml('Hand: ' + hand.identifier)
		self.adjustActions()

	def onActionPreviousTriggered(self):
		self._history.goBack()
		hand = self._history.currentItem()
		self._handViewer.setHtml('Hand: ' + hand.identifier)
		self.adjustActions()

	def onFilterChanged(self, name):
		self.filterHands()

	def onItemDoubleClicked(self, index):
		hand = self._handModel.hand(index.row())
		if hand._handViewer_review:
			hand._handViewer_review = ''
		else:
			hand._handViewer_review = self.FilterReview
		self.filterHands()

	def onSelectionChanged(self, selection):
		#FIX: QTableView row only selection is broken on Qt4. only available workaround
		# seems to be to force a redraw by resizing the widget. downside off cause is
		# that it slows things down noticably.
		self._tableHands.setUpdatesEnabled(False)
		try:
			sizeOld = self._tableHands.geometry().size()
			sizeNew = QtCore.QSize(sizeOld)
			sizeNew.setHeight(sizeNew.height()+1)
			self._tableHands.resize(sizeNew)
			self._tableHands.resize(sizeOld)
		finally:
			self._tableHands.setUpdatesEnabled(True)
		#/FIX:

		indexes = selection.indexes()
		if not indexes:
			return
		row = indexes[0].row()
		hand = self._handModel.hand(row)
		self._handViewer.setHtml('Hand: ' + hand.identifier)
		self._history.addItem(hand)
		self.adjustActions()

#************************************************************************************
# test code
#************************************************************************************
if __name__ == '__main__':
	import os
	fileNameIni = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.ini')
	settings = QtCore.QSettings(fileNameIni, QtCore.QSettings.IniFormat)

	application = QtGui.QApplication([])
	handViewer = FrameHandViewer()

	class Hand(object):
		SourceTypeNone = 0
		SourceTypeFile = 1
		SourceTypeOther = 99
		def __init__(self, source, sourceType, site, table, identifier):
			self.source = source
			self.sourceType = sourceType
			self.site = site
			self.table = table
			self.identifier = identifier
		def __eq__(self, other):
			if self.source == other.source:
				if self.site == other.site:
					if self.table == other.table:
						if self.identifier == other.identifier:
							return True
			return False
		def __ne__(self, other): return not self.__eq__(other)

	hands = []
	x = 0
	for h in range(2):
		source = '/foo/bar-%s/source' % h
		sourceType = Hand.SourceTypeFile
		for i in range(2):
			for j in range(2):
				for k in range(5):
					x += 1
					hands.append(Hand(source, sourceType, 'site-%s' % i, 'table-%s' % j, '%s' % x))

	w = QtGui.QMainWindow()
	w.setCentralWidget(handViewer)
	toolBar = w.addToolBar('')
	map(toolBar.addAction, handViewer.actions())
	handViewer.restoreSettings(settings)
	handViewer.addHands(hands)
	w.show()
	application.exec_()
	handViewer.saveSettings(settings)
