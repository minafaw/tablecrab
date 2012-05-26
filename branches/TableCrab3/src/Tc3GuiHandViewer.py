
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
#NOTE: mostly taken from: http://lists.qt.nokia.com/pipermail/qt-interest/2009-August/011654.html
class FilterHeader(QtGui.QHeaderView):

	filterSourcesChanged = QtCore.pyqtSignal()
	filterSitesChanged = QtCore.pyqtSignal()
	filterTablesChanged = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		QtGui.QHeaderView.__init__(self, QtCore.Qt.Horizontal, parent)
		self._comboSources =  QtGui.QComboBox(self)
		self._comboSources.currentIndexChanged.connect(self.onFilterSourcesChanged)
		self._comboSites =  QtGui.QComboBox(self)
		self._comboSites.currentIndexChanged.connect(self.onFilterSitesChanged)
		self._comboTables =  QtGui.QComboBox(self)
		self._comboTables.currentIndexChanged.connect(self.onFilterTablesChanged)

		self._filterCombos = (self._comboSources, self._comboSites, self._comboTables, None)

		self.sectionResized.connect(self.onSectionResized)
		self.sectionMoved.connect(self.onSectionMoved)

	def filterHeight(self):
		return self._comboSites.sizeHint().height()

	def sizeHint(self):
		size = QtGui.QHeaderView.sizeHint(self)
		size.setHeight(size.height() + self.filterHeight() + 2)
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
			combo = self._filterCombos[iLogical]
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
		self.repositionFilterRow(0, len(self._filterCombos))

	def filterSourceCurrent(self):
		return unicode(self._comboSources.currentText().toUtf8(), 'utf-8')

	def setFilterSources(self, filters, filterCurrent):
		self._comboSources.currentIndexChanged.disconnect(self.onFilterSourcesChanged)
		self._comboSources.clear()
		self._comboSources.addItems(filters)
		i = filters.index(filterCurrent)
		self._comboSources.setCurrentIndex(i)
		self._comboSources.currentIndexChanged.connect(self.onFilterSourcesChanged)
		self.filterSourcesChanged.emit()

	def filterSitesCurrent(self):
		return unicode(self._comboSites.currentText().toUtf8(), 'utf-8')

	def setFilterSites(self, filters, filterCurrent):
		self._comboSites.currentIndexChanged.disconnect(self.onFilterSitesChanged)
		self._comboSites.clear()
		self._comboSites.addItems(filters)
		i = filters.index(filterCurrent)
		self._comboSites.setCurrentIndex(i)
		self._comboSites.currentIndexChanged.connect(self.onFilterSitesChanged)
		self.filterSitesChanged.emit()

	def filterTablesCurrent(self):
		return unicode(self._comboTables.currentText().toUtf8(), 'utf-8')

	def setFilterTables(self, filters,filterCurrent):
		self._comboTables.currentIndexChanged.disconnect(self.onFilterTablesChanged)
		self._comboTables.clear()
		self._comboTables.addItems(filters)
		i = filters.index(filterCurrent)
		self._comboTables.setCurrentIndex(i)
		self._comboTables.currentIndexChanged.connect(self.onFilterTablesChanged)
		self.filterTablesChanged.emit()

	def onFilterSourcesChanged(self, i):
		self.filterSourcesChanged.emit()

	def onFilterSitesChanged(self, i):
		self.filterSitesChanged.emit()

	def onFilterTablesChanged(self, i):
		self.filterTablesChanged.emit()

#************************************************************************************
#
#************************************************************************************
#NOTE: too lazy to implement an editable model. create a new model every time its
# contents change instead.
class HandModel(QtCore.QAbstractTableModel):
	def __init__(self, hands, parent=None):
		QtCore.QAbstractTableModel.__init__(self, parent)
		self._hands = hands
		self._headers = ('Source:', 'Site:', 'Table:', 'Hand:')
		self._handAttrs = ('source', 'site', 'table', 'identifier')

	def rowCount(self, parent):
		return len(self._hands)

	def columnCount(self, parent):
		return len(self._headers)

	def data(self, index, role,
					QVariant=QtCore.QVariant,
					DisplayRole=QtCore.Qt.DisplayRole
					):
		if not index.isValid():
			return QVariant()
		elif role != DisplayRole:
			return QVariant()
		hand = self._hands[index.row()]
		value = getattr(hand, self._handAttrs[index.column()])
		return QVariant(value)

	def headerData(self, col, orientation, role,
					QVariant=QtCore.QVariant,
					Horizontal=QtCore.Qt.Horizontal,
					DisplayRole=QtCore.Qt.DisplayRole,
					Vertical=QtCore.Qt.Vertical
					):
		if orientation == Horizontal and role == DisplayRole:
			return QVariant(self._headers[col])
		elif orientation == Vertical and role == DisplayRole:
			return QVariant(str(col+1))
		return QVariant()

	def hand(self, i):
		return self._hands[i]

#************************************************************************************
#
#************************************************************************************
class FrameHandViewer(QtGui.QFrame):

	FilterAll = '*All'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		self._hands = []
		self._filtersOld = {
				'sites': {},
				'tables': {},
				}

		self._splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)

		self._tableHands = QtGui.QTableView(self)
		self._tableFilter = FilterHeader(self._tableHands)

		self._tableHands.setSelectionBehavior(self._tableHands.SelectRows)
		self._tableHands.setSelectionMode(self._tableHands.SingleSelection)
		self._tableFilter.setMovable(True)
		self._tableHands.setHorizontalHeader(self._tableFilter)
		self._tableFilter.setStretchLastSection(True)
		self._tableFilter.setDefaultAlignment(QtCore.Qt.AlignLeft)
		self._tableFilter.setFilterSources((self.FilterAll, ), self.FilterAll)
		self._tableFilter.setFilterSites((self.FilterAll, ), self.FilterAll)
		self._tableFilter.setFilterTables((self.FilterAll, ), self.FilterAll)

		handModel = HandModel([], self._tableHands)
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
		self._tableFilter.filterSourcesChanged.connect(self.onFilterSourcesChanged)
		self._tableFilter.filterSitesChanged.connect(self.onFilterSitesChanged)
		self._tableFilter.filterTablesChanged.connect(self.onFilterTablesChanged)

	def saveSettings(self, qSettings):
		pass

	def restoreSettings(self, qSettings):
		pass

	def addHand(self, site, table, hand):
		self._hands.append((site, table, hand))
		self.updateFilters()

	def addHands(self, hands):
		self._hands.extend(hands)
		self.updateFilters()

	def updateHands(self):
		filterSource = self._tableFilter.filterSourceCurrent()
		filterSite = self._tableFilter.filterSitesCurrent()
		filterTable = self._tableFilter.filterTablesCurrent()

		# check if a hand is selected and if it is present in new model
		handSelected = None
		rowSelected = None
		indexSelected = self._tableHands.selectionModel().currentIndex()
		if indexSelected.isValid():
			handSelected = self._tableHands.model().hand(indexSelected.row())

		# setup new model containig current hand selection
		hands = []
		i = 0
		for hand in self._hands:
			 if hand.source == filterSource or filterSource == self.FilterAll:
				 if hand.site == filterSite or filterSite == self.FilterAll:
					if hand.table == filterTable or filterTable == self.FilterAll:
						hands.append(hand)
						if handSelected is not None:
							if hand == handSelected:
								rowSelected = i
						i += 1
		handModel = HandModel(hands, self._tableHands)
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

	def updateFilters(self):
		filterSource = self._tableFilter.filterSourceCurrent()
		sources = {self.FilterAll: None}
		for hand in self._hands:
			sources[hand.source] = None
		sources = sources.keys()
		sources.sort()
		self._tableFilter.setFilterSources(sources, filterSource)

	def onFilterSourcesChanged(self):
		filterSource = self._tableFilter.filterSourceCurrent()
		filterSite = self._filtersOld['sites'].get(filterSource, self.FilterAll)
		sites = {self.FilterAll: None}
		for hand in self._hands:
			if hand.source == filterSource or filterSource == self.FilterAll:
				sites[hand.site] = None
		sites = sites.keys()
		sites.sort()
		self._tableFilter.setFilterSites(sites, filterSite)

	def onFilterSitesChanged(self):
		filterSource = self._tableFilter.filterSourceCurrent()
		filterSite = self._tableFilter.filterSitesCurrent()
		filterTable = self._filtersOld['tables'].get(filterSite, self.FilterAll)
		tables = {self.FilterAll: None}
		for hand in self._hands:
			if hand.site == filterSite or filterSite == self.FilterAll:
				tables[hand.table] = None
		tables = tables.keys()
		tables.sort()
		self._tableFilter.setFilterTables(tables, filterTable)
		self._filtersOld['sites'][filterSource] = filterSite

	def onFilterTablesChanged(self):
		filterSite = self._tableFilter.filterSitesCurrent()
		filterTable = self._tableFilter.filterTablesCurrent()
		self._filtersOld['tables'][filterSite] = filterTable
		self.updateHands()

	def onCurrentRowChanged(self, indexCurrent, indexPrev):
		pass

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	application = QtGui.QApplication([])
	w = FrameHandViewer()

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
		for i in range(2):
			for j in range(2):
				for k in range(5):
					x += 1
					hands.append(Hand('source-%s' % h, 'site-%s' % i, 'table-%s' % j, '%s' % x))

	w.addHands(hands)
	w.show()
	application.exec_()
