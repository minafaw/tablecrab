
import TableCrabConfig

from PyQt4 import QtCore, QtGui
#**********************************************************************************************
#
#**********************************************************************************************

Templates = []
MaxTemplates = 64


def newValidSize(size):
	return TableCrabConfig.newSizeNone() if size is None else size

def newValidPoint(point):
	return TableCrabConfig.newPointNone() if point is None else point

class ChildItem(QtGui.QTreeWidgetItem):
	def __init__(self, text, value, parent=None):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.setText(0, text)
		self.setText(1, value)
	def toplevel(self):
		return self.parent()
	
class TemplatePokerStarsTable(QtGui.QTreeWidgetItem):
	_PointNames = ('buttonCheck', 'buttonFold', 'checkboxFold', 'checkboxCheckFold', 'betSliderStart', 'betSliderEnd', 'instantHandHistory', 'replayer')
	def __init__(self, parent=None, 
			name='',
			size=None, 
			buttonCheck=None,
			buttonFold=None,
			buttonRaise=None,
			checkboxFold=None,
			checkboxCheckFold=None,
			betSliderStart=None,
			betSliderEnd=None,
			instantHandHistory=None,
			replayer=None,
			itemIsExpanded=False,
			):
		QtGui.QTreeWidgetItem.__init__(self, parent)
		self.name = name if name else self.menuName()
		self.size = newValidSize(size)
		self.buttonCheck = newValidPoint(buttonCheck)
		self.buttonFold = newValidPoint(buttonFold)
		self.buttonRaise = newValidPoint(buttonRaise)
		self.checkboxFold = newValidPoint(checkboxFold)
		self.checkboxCheckFold = newValidPoint(checkboxCheckFold)
		self.betSliderStart = newValidPoint(betSliderStart)
		self.betSliderEnd = newValidPoint(betSliderEnd)
		self.instantHandHistory = newValidPoint(instantHandHistory)
		self.replayer = newValidPoint(replayer)
		self.itemIsExpanded = itemIsExpanded
		
		self.setFirstColumnSpanned(True)
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
		self.setIcon(0, QtGui.QIcon(TableCrabConfig.Pixmaps.stars()) )
		font = self.font(0)
		font.setBold(True)
		self.setFont(0, font)
		self.setExpanded( self.itemIsExpanded)
		self.setText(0, self.name)
		
		self.itemType = ChildItem('Type:',  self.menuName(), parent=self)
		self.itemType.setDisabled(True)
		self.itemSize = ChildItem('Size:',  TableCrabConfig.sizeToString(self.size), parent=self)
		self.itemSize.setDisabled(True)
		self.itemsPoint = []
		for pointName in self._PointNames:
			point = getattr(self, pointName)
			item = ChildItem(pointName[0].upper() + pointName[1:],  TableCrabConfig.pointToString(point), parent=self)
			item.setDisabled(True)
			self.itemsPoint.append( (pointName, item) )
	
	def toplevel(self):
		return self
	
	def handleItemChanged(self, item):
		if item is self:
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
		
	def handleScreenshotDoubleClicked(self, item, pixmap, point):
		if item.isDisabled():
			return False
		for pointName, tmp_item in self.itemsPoint:
			if tmp_item is item:
				self.size.setWidth(pixmap.width())
				self.size.setHeight(pixmap.height())
				self.itemSize.setText(1, TableCrabConfig.sizeToString(self.size) )
				myPoint = getattr(self, pointName)
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
			point = TableCrabConfig.settingsValue( (key, keyName), TableCrabConfig.newPointNone() ).toPoint()
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

