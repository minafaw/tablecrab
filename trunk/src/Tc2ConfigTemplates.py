
import Tc2Config

from PyQt4 import QtCore, QtGui
#**********************************************************************************************
#
#**********************************************************************************************

Templates = []

def newValidSize(size):
	return Tc2Config.newSizeNone() if size is None else size

def newPoint(point=None, x=None, y=None):
	point = Tc2Config.newPointNone() if point is None else point
	if x is not None:
		point.setX(x)
		point.setY(y)
	return point


class ItemBase(QtGui.QTreeWidgetItem):
	def topLevel(self):
		parent = self
		while True:
			if parent.IsTopLevel:
				return parent
			parent = parent.parent()
			if parent is None:
				raise ValueError('no top level item found')

class PointItem(ItemBase):
	IsTopLevel = False
	def __init__(self, pointName, point, parent=None):
		ItemBase.__init__(self, parent)
		self.point = None
		self.pointName = pointName
		self.setText(0, self.pointName)
		self.setPoint(point)
		self.setDisabled(True)
	def setPoint(self, point):
		if self.pointName == 'EmptySpace' and point == Tc2Config.PointNone:
			# make shure point is not empty, we need it
			point = QtCore.QPoint(1, 1)
		self.point = point
		self.setText(1, Tc2Config.pointToString(self.point) )

class TemplatePokerStarsTable(ItemBase):
	IsTopLevel = True
	PointNames = (
		'EmptySpace',
		'ButtonCheck',
		'ButtonFold',
		'ButtonRaise',
		'CheckboxFold',
		'CheckboxCheckFold',
		'BetSliderStart',
		'BetSliderEnd',
		'PotTopLeft',
		'PotBottomRight',
		'InstantHandHistory',
		'Replayer',
		)
	def __init__(self,
			parent=None,
			name='',
			size=None,
			itemIsExpanded=False,
			**kws
			):
		ItemBase.__init__(self, parent)
		self.name = name if name else self.menuName()
		self.size = newValidSize(size)
		self.itemIsExpanded = itemIsExpanded

		self.setFirstColumnSpanned(True)
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
		self.setIcon(0, QtGui.QIcon(Tc2Config.Pixmaps.stars()) )
		font = self.font(0)
		font.setBold(True)
		self.setFont(0, font)
		self.setExpanded( self.itemIsExpanded)
		self.setText(0, self.name)

		self.itemType = QtGui.QTreeWidgetItem(self, ['Type:',  self.menuName()])
		self.itemType.setDisabled(True)
		self.itemSize = QtGui.QTreeWidgetItem(self, ['Size:',  Tc2Config.sizeToString(self.size)])
		self.itemSize.setDisabled(True)

		self.points = {}
		self.pointItems = []
		for pointName in self.PointNames:
			#NOTE: we have to make shure points in out point dict are the same as
			# points points in our tree items
			point = newPoint(kws.get(pointName, None))
			item = PointItem(pointName, point, parent=self)
			self.points[pointName] = item.point
			self.pointItems.append(item)

	def handleEditInPlaceFinished(self, item):
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
			for item in self.pointItems:
				item.setDisabled(True)
		elif pixmap.size() == self.size:
			for item in self.pointItems:
				item.setDisabled(False)
		elif self.size == Tc2Config.SizeNone:
			for item in self.pointItems:
				item.setDisabled(False)
		else:
			for item in self.pointItems:
				item.setDisabled(True)

	def handleScreenshotDoubleClicked(self, item, pixmap, point):
		if item.isDisabled():
			return False
		if item not in self.pointItems:
			return False
		self.size.setWidth(pixmap.width())
		self.size.setHeight(pixmap.height())
		self.itemSize.setText(1, Tc2Config.sizeToString(self.size) )
		point = QtCore.QPoint(point)
		item.setPoint(point)
		self.points[item.pointName] = item.point
		return True

	@classmethod
	def id(klass):
		return 'PokerStarsTable'
	@classmethod
	def menuName(klass):
		return 'PokerStars table'
	@classmethod
	def shortcut(klass): return QtGui.QKeySequence('Shift+P')
	@classmethod
	def fromConfig(klass, key):
		kws = {}
		id = Tc2Config.settingsValue( (key, 'ID'), '').toString()
		if id != klass.id():
			return None
		kws['name'] = Tc2Config.settingsValue( (key, 'Name'), 'None').toString()
		size = Tc2Config.settingsValue( (key, 'Size'), Tc2Config.newSizeNone() ).toSize()
		if not size.isValid():
			size = Tc2Config.newSizeNone()
		kws['size'] = size
		kws['itemIsExpanded'] = Tc2Config.settingsValue( (key, 'ItemIsExpanded'), False).toBool()
		for pointName in klass.PointNames:
			point = Tc2Config.settingsValue((key, pointName), Tc2Config.newPointNone()).toPoint()
			if not Tc2Config.pointInSize(size, point):
				point = Tc2Config.newPointNone()
			kws[pointName] = point
		return klass(**kws)

	def toConfig(self, key):
		Tc2Config.settingsSetValue( (key, 'ID'), self.id() )
		Tc2Config.settingsSetValue( (key, 'Name'), self.name)
		Tc2Config.settingsSetValue( (key, 'Size'), self.size)
		Tc2Config.settingsSetValue( (key, 'ItemIsExpanded'), self.itemIsExpanded)
		for pointName, point in self.points.items():
			Tc2Config.settingsSetValue( (key, pointName), point)
		return True

Templates.append(TemplatePokerStarsTable)

