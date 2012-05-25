
from PyQt4 import QtCore, QtGui, QtWebKit

#************************************************************************************
#
#************************************************************************************
#NOTE: mostly taken from: http://lists.qt.nokia.com/pipermail/qt-interest/2009-August/011654.html
class FilterHeader(QtGui.QHeaderView):

	filterSitesChanged = QtCore.pyqtSignal()
	filterTablesChanged = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		QtGui.QHeaderView.__init__(self, QtCore.Qt.Horizontal, parent)
		self._comboSites =  QtGui.QComboBox(self)
		self._comboSites.currentIndexChanged.connect(self.onFilterSitesChanged)
		self._comboTables =  QtGui.QComboBox(self)
		self._comboTables.currentIndexChanged.connect(self.onFilterTablesChanged)

		self.sectionResized.connect(self.onSectionResized)

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
		combos = (self._comboSites, self._comboTables)
		for i in xrange(start, end+1):
			iLogical = self.logicalIndex(i)
			if self.isSectionHidden(iLogical):
				continue
			if i >= len(combos):
				continue
			combo = combos[iLogical]
			combo.move(self.sectionPosition(iLogical) - self.offset(), self.filterHeight())
			combo.resize(self.sectionSize(iLogical), self.filterHeight())

	def onSectionResized(self, iLogical, sizeOld, sizeNew):
		vg = self.viewport().geometry()
		start = self.visualIndex(iLogical)
		end = self.visualIndexAt(vg.right())
		if end < 0:
			end = self.count() -1
		self.repositionFilterRow(start, end)

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
	def __init__(self, hands, headers, parent=None):
		QtCore.QAbstractTableModel.__init__(self, parent)
		self._hands = hands
		self._headers = headers

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
		return QVariant(self._hands[index.row()][index.column()])

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

#************************************************************************************
#
#************************************************************************************
class FrameHandViewer(QtGui.QFrame):

	FilterAll = '*All'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self._headerLabels = ('Site:', 'Table:', 'Hand:')
		self._hands = []
		self._filtersOld = {
				'tables': {},
				}

		self._splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)

		self._tableHands = QtGui.QTableView(self)
		self._tableFilter = FilterHeader(self._tableHands)

		self._tableHands.setSelectionBehavior(self._tableHands.SelectRows)
		self._tableHands.setSelectionMode(self._tableHands.SingleSelection)
		self._tableHands.setHorizontalHeader(self._tableFilter)
		self._tableFilter.setStretchLastSection(True)
		self._tableFilter.setDefaultAlignment(QtCore.Qt.AlignLeft)
		self._tableFilter.setFilterSites((self.FilterAll, ), self.FilterAll)
		self._tableFilter.setFilterTables((self.FilterAll, ), self.FilterAll)

		handModel = HandModel([], self._headerLabels, self._tableHands)
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
		self._tableFilter.filterSitesChanged.connect(self.onFilterSitesChanged)
		self._tableFilter.filterTablesChanged.connect(self.onFilterTablesChanged)

	def saveSettings(self, qSettings):
		pass

	def restoreSettings(self, qSettings):
		pass

	def addHand(self, site, table, hand):
		self._hands.append((site, table, hand))
		self.updateFilters()
		self.updateHands()

	def addHands(self, hands):
		self._hands.extend(hands)
		self.updateFilters()
		self.updateHands()

	def updateHands(self):
		filterSite = self._tableFilter.filterSitesCurrent()
		filterTable = self._tableFilter.filterTablesCurrent()
		hands = []
		for site, table, hand in self._hands:
			 if site == filterSite or filterSite == self.FilterAll:
				if table == filterTable or filterTable == self.FilterAll:
					hands.append((site, table, hand))
		handModel = HandModel(hands, self._headerLabels, self._tableHands)
		self._tableHands.setModel(handModel)
		#TODO: check if we can keep selection and scroll to it

	def updateFilters(self):
		filterSite = self._tableFilter.filterSitesCurrent()
		sites = {self.FilterAll: None}
		for site, table, hand in self._hands:
			sites[site] = None
		sites = sites.keys()
		sites.sort()
		self._tableFilter.setFilterSites(sites, filterSite)

	def onFilterSitesChanged(self):
		filterSite = self._tableFilter.filterSitesCurrent()
		filterTable = self._filtersOld['tables'].get(filterSite, self.FilterAll)
		tables = {self.FilterAll: None}
		for site, table, hand in self._hands:
			if site == filterSite or filterSite == self.FilterAll:
				if table == filterTable or filterTable == self.FilterAll:
					tables[table] = None
		tables = tables.keys()
		tables.sort()
		self._tableFilter.setFilterTables(tables, filterTable)

	def onFilterTablesChanged(self):
		filterSite = self._tableFilter.filterSitesCurrent()
		filterTable = self._tableFilter.filterTablesCurrent()
		self._filtersOld['tables'][filterSite] = filterTable
		self.updateHands()

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	application = QtGui.QApplication([])
	w = FrameHandViewer()

	hands = []
	for i in range(5):
		for j in range(50):
			for k in range(50):
				hands.append(('foo-%s' % i, 'table-%s' % j, '%s' % (i*j*k)))
	w.addHands(hands)
	w.show()
	application.exec_()
