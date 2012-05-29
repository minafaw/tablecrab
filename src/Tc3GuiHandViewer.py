
import os
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
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
#
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
#
#************************************************************************************
#NOTE: too lazy to implement an editable model. create a new model every time its
# contents change instead.
class HandModel(QtCore.QAbstractTableModel):
	def __init__(self, hands, filters, parent=None):
		QtCore.QAbstractTableModel.__init__(self, parent)
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
			return QVariant(str(col+1))
		return QVariant()

	def hand(self, i):
		return self._hands[i]

#************************************************************************************
#
#************************************************************************************
class FrameHandViewer(QtGui.QFrame):

	SettingsKeyBase = 'HandViewer/'
	SettingsKeySplitterState = SettingsKeyBase + 'SplitterState'
	SettingsKeyFilterHeaderState = SettingsKeyBase + 'FilterHeaderState'

	FilterAll = '*All'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self._hands = []
		self._sourceIdentifiers = {}
		self._sourceNames = {}
		self._filters = (
				{'filterName': 'source', 'headerText': 'Source:', 'hasFilter': True},
				{'filterName': 'site', 'headerText': 'Site:', 'hasFilter': True},
				{'filterName': 'table', 'headerText': 'Table:', 'hasFilter': True},
				{'filterName': 'identifier', 'headerText': 'Hand:', 'hasFilter': False},
				)

		self._splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)

		self._tableHands = QtGui.QTableView(self)
		self._filterHeader = FilterHeader(self._filters, parent=self._tableHands)

		self._tableHands.setSelectionBehavior(self._tableHands.SelectRows)
		self._tableHands.setSelectionMode(self._tableHands.SingleSelection)
		self._filterHeader.setMovable(True)
		self._tableHands.setHorizontalHeader(self._filterHeader)
		self._filterHeader.setStretchLastSection(True)
		self._filterHeader.setDefaultAlignment(QtCore.Qt.AlignLeft)
		for filterData in self._filters:
			self._filterHeader.setFilters(filterData['filterName'], (self.FilterAll, ))

		handModel = HandModel([], self._filters, self._tableHands)
		self._tableHands.setModel(handModel)

		#
		self._handViewer = QtWebKit.QWebView(self)
		self._handViewer.setHtml('')

		# layout
		self._splitter.addWidget(self._tableHands)
		self._splitter.addWidget(self._handViewer)
		b = QtGui.QHBoxLayout(self)
		b.addWidget(self._splitter)

		# connect signals
		self._tableHands.selectionModel().currentRowChanged.connect(self.onCurrentRowChanged)
		self._filterHeader.filterChanged.connect(self.onFilterChanged)

	def saveSettings(self, qSettings):
		qSettings.setValue(self.SettingsKeySplitterState, self._splitter.saveState())
		qSettings.setValue(self.SettingsKeyFilterHeaderState, self._filterHeader.saveState())

	def restoreSettings(self, qSettings):
		arr = qSettings.value(self.SettingsKeySplitterState, QtCore.QByteArray()).toByteArray()
		self._splitter.restoreState(arr)
		arr = qSettings.value(self.SettingsKeyFilterHeaderState, QtCore.QByteArray()).toByteArray()
		self._filterHeader.restoreState(arr)

	def addHand(self, hand):
		return self.addHands((hand, ))

	def addHands(self, hands):
		self._hands.extend(hands)
		# update our filters
		filterList = [
				(filterData['filterName'], self._filterHeader.filters(filterData['filterName']))
				for	filterData in self._filters
				if filterData['hasFilter']
				]
		for filterName, filters in filterList:
			for hand in hands:
				value = getattr(hand, filterName)
				if filterName == 'source':
					myName = self._sourceNames.get(value, None)
					if myName is not None:
						value = myName
				if value not in filters:
					filters.append(value)
			filters.sort()
			filterCurrent = self._filterHeader.filterCurrent(filterName)
			self._filterHeader.setFilters(filterName, filters)
			if filterCurrent in filters:
				self._filterHeader.setFilterCurrent(filterName, filterCurrent)
		self.updateHands()

	def registerSource(self, name):
		"""registers a source to the hand viewer
		@param name: (str) name of the source to register
		@return: (str) adjusted name
		@note: registering a source makes shure it is unique in the hand viewer.
		@note: you should prefix file names to be registered with "file:" to enshure
		propper	handling in the gui. the prefix is removed from the name returned.
		"""
		if name.startswith('file:'):
			name = name[5:]
			myName = 'file:' + os.path.basename(name)
		else:
			myName = name
		myName = uniqueName(self._sourceIdentifiers, myName)
		self._sourceIdentifiers[myName] = name
		self._sourceNames[name] = myName
		return name

	def updateHands(self):

		# check if a hand is selected and if it is present in new model
		handSelected = None
		rowSelected = None
		indexSelected = self._tableHands.selectionModel().currentIndex()
		if indexSelected.isValid():
			handSelected = self._tableHands.model().hand(indexSelected.row())

		# setup new model containing currently selected hands
		hands = []
		i = 0
		filtersCurrent = [
				(data['filterName'], self._filterHeader.filterCurrent(data['filterName']))
				for data in self._filters
				]
		for hand in self._hands:
			handIsOk = True
			for filterName, filterCurrent in filtersCurrent:
				if filterCurrent is None: continue
				if filterCurrent == self.FilterAll: continue
				value = getattr(hand, filterName)
				if filterName == 'source':
					myName = self._sourceIdentifiers.get(filterCurrent, None)
					if myName is not None:
						filterCurrent = myName
				if filterCurrent == getattr(hand, filterName): continue
				handIsOk = False
				break
			if handIsOk:
				hands.append(hand)
				if handSelected is not None and hand == handSelected:
					rowSelected = i
				i += 1
		handModel = HandModel(hands, self._filters, self._tableHands)
		self._tableHands.setModel(handModel)
		#NOTE: acc to docs each model gets a new selection model assigned so we have to reconnect here
		self._tableHands.selectionModel().currentRowChanged.connect(self.onCurrentRowChanged)

		# reselect hand if possible
		#NOTE: we lose selection if the last selected hand is not present in the new model
		# one alternative would be to store selection for every filter combination, but
		# this may get to confusing.
		if rowSelected is not None:
			self._tableHands.selectRow(rowSelected)
			indexSelected = self._tableHands.selectionModel().currentIndex()
			if indexSelected.isValid():
				self._tableHands.scrollTo(indexSelected, self._tableHands.PositionAtCenter)

	def onFilterChanged(self, name):
		self.updateHands()

	def onCurrentRowChanged(self, indexCurrent, indexPrev):
		pass

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import os
	fileNameIni = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.ini')
	settings = QtCore.QSettings(fileNameIni, QtCore.QSettings.IniFormat)

	application = QtGui.QApplication([])
	w = FrameHandViewer()
	w.restoreSettings(settings)

	class Hand(object):
		def __init__(self, source, site, table, identifier):
			self.source = source
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
		source = w.registerSource('file:/foo/bar-%s/source' % h)
		for i in range(2):
			for j in range(2):
				for k in range(5):
					x += 1
					hands.append(Hand(source, 'site-%s' % i, 'table-%s' % j, '%s' % x))

	w.addHands(hands)
	w.show()
	application.exec_()
	w.saveSettings(settings)
