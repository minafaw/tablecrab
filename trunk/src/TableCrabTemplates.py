
import TableCrabConfig

from PyQt4 import QtCore, QtGui
#**********************************************************************************************
#
#**********************************************************************************************

Templates = []

def newValidSize(size):
	return TableCrabConfig.newSizeNone() if size is None else size

def newPoint(point=None, x=None, y=None):
	point = TableCrabConfig.newPointNone() if point is None else point
	if x is not None:
		point.setX(x)
		point.setY(y)
	return point

class ChildItem(QtGui.QTreeWidgetItem):
	def __init__(self, pointName, text, value, parent=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.pointName = pointName
		self.setText(0, text)
		self.setText(1, value)
	def toplevel(self):
		return self.parent()

class TemplatePokerStarsTable(QtGui.QTreeWidgetItem):
	_PointNames = ('emptySpace', 'buttonCheck', 'buttonFold', 'buttonRaise',
			'checkboxFold', 'checkboxCheckFold', 'betSliderStart', 'betSliderEnd',
			'instantHandHistory', 'replayer', 'potTopLeft', 'potBottomRight')
	def __init__(self,
			parent=None,
			name='',
			size=None,
			emptySpace=None,
			buttonCheck=None,
			buttonFold=None,
			buttonRaise=None,
			checkboxFold=None,
			checkboxCheckFold=None,
			betSliderStart=None,
			betSliderEnd=None,
			instantHandHistory=None,
			replayer=None,
			potTopLeft=None,
			potBottomRight=None,

			itemIsExpanded=False,
			):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.name = name if name else self.menuName()
		self.size = newValidSize(size)
		self.emptySpace = newPoint(emptySpace, x=1, y=1)
		self.buttonCheck = newPoint(buttonCheck)
		self.buttonFold = newPoint(buttonFold)
		self.buttonRaise = newPoint(buttonRaise)
		self.checkboxFold = newPoint(checkboxFold)
		self.checkboxCheckFold = newPoint(checkboxCheckFold)
		self.betSliderStart = newPoint(betSliderStart)
		self.betSliderEnd = newPoint(betSliderEnd)
		self.instantHandHistory = newPoint(instantHandHistory)
		self.replayer = newPoint(replayer)
		self.potTopLeft = newPoint(potTopLeft)
		self.potBottomRight = newPoint(potBottomRight)
		self.itemIsExpanded = itemIsExpanded

		self.setFirstColumnSpanned(True)
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
		self.setIcon(0, QtGui.QIcon(TableCrabConfig.Pixmaps.stars()) )
		font = self.font(0)
		font.setBold(True)
		self.setFont(0, font)
		self.setExpanded( self.itemIsExpanded)
		self.setText(0, self.name)

		self.itemType = ChildItem(None, 'Type:',  self.menuName(), parent=self)
		self.itemType.setDisabled(True)
		self.itemSize = ChildItem(None, 'Size:',  TableCrabConfig.sizeToString(self.size), parent=self)
		self.itemSize.setDisabled(True)
		self.itemsPoint = []
		for pointName in self._PointNames:
			point = getattr(self, pointName)
			item = ChildItem(
					pointName,
					pointName[0].upper() + pointName[1:],
					TableCrabConfig.pointToString(point),
					parent=self
					)
			item.setDisabled(True)
			self.itemsPoint.append( (pointName, item) )

	def toplevel(self):
		return self

	def handleEditingFinished(self, item):
		if item is self:
			if self.text(0) != self.name:
				self.name = self.text(0)
				return True
		return False

	def handleItemExpanded(self, item):
		if item is self:
			self.itemIsExpanded = True
			return True
		return False

	def handleItemCollapsed(self, item):
		if item is self:
			self.itemIsExpanded = False
			return True
		return False

	def handleScreenshotSet(self, pixmap):
		if pixmap.isNull():
			for _, item in self.itemsPoint:
				item.setDisabled(True)
		elif pixmap.size() == self.size:
			for _, item in self.itemsPoint:
				item.setDisabled(False)
		elif self.size == TableCrabConfig.SizeNone:
			for _, item in self.itemsPoint:
				item.setDisabled(False)
		else:
			for _, item in self.itemsPoint:
				item.setDisabled(True)

	def handleScreenshotDoubleClicked(self, item, pixmap, point):
		if item.isDisabled():
			return False
		for pointName, tmp_item in self.itemsPoint:
			if tmp_item is item:
				self.size.setWidth(pixmap.width())
				self.size.setHeight(pixmap.height())
				self.itemSize.setText(1, TableCrabConfig.sizeToString(self.size) )
				myPoint = getattr(self, pointName)
				if item.pointName == 'emptySpace' and point == TableCrabConfig.PointNone:
					myPoint.setX(1)
					myPoint.setY(1)
				else:
					myPoint.setX(point.x() )
					myPoint.setY(point.y() )
				item.setText(1, TableCrabConfig.pointToString(myPoint) )
				return True
		else:
			raise ValueError('no item found')
		return False

	@classmethod
	def id(klass):
		return 'PokerStarsTable'
	@classmethod
	def menuName(klass):
		return 'PokerStars table'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+P')
	@classmethod
	def attrsFromConfig(klass, key, klassID):
		attrs = {}
		id = TableCrabConfig.settingsValue( (key, 'ID'), '').toString()
		if id != klassID: return None
		attrs['name'] = TableCrabConfig.settingsValue( (key, 'Name'), 'None').toString()
		size = TableCrabConfig.settingsValue( (key, 'Size'), TableCrabConfig.newSizeNone() ).toSize()
		if not size.isValid():
			size = TableCrabConfig.newSizeNone()
		attrs['size'] = size
		attrs['itemIsExpanded'] = TableCrabConfig.settingsValue( (key, 'ItemIsExpanded'), False).toBool()
		for pointName in klass._PointNames:
			keyName = pointName[0].upper() + pointName[1:]
			point = TableCrabConfig.settingsValue(
					(key, keyName),
					TableCrabConfig.newPointNone()
					).toPoint()
			if pointName == 'emptySpace':
					# make shure point is not empty, we need it
					if point == TableCrabConfig.PointNone:
						point = QtCore.QPoint(1, 1)
			if not TableCrabConfig.pointInSize(size, point):
				point = TableCrabConfig.newPointNone()
			attrs[pointName] = point
		return attrs
	@classmethod
	def fromConfig(klass, key):
		attrs = klass.attrsFromConfig(key, klass.id() )
		if attrs is not None:
			return klass(**attrs)
	def toConfig(self, key):
		TableCrabConfig.settingsSetValue( (key, 'ID'), self.id() )
		TableCrabConfig.settingsSetValue( (key, 'Name'), self.name)
		TableCrabConfig.settingsSetValue( (key, 'Size'), self.size)
		TableCrabConfig.settingsSetValue( (key, 'ItemIsExpanded'), self.itemIsExpanded)
		for pointName in self._PointNames:
			keyName = pointName[0].upper() + pointName[1:]
			TableCrabConfig.settingsSetValue( (key, keyName), getattr(self, pointName) )
		return True

Templates.append(TemplatePokerStarsTable)

