
import Tc2Config
import Tc2ConfigTemplates

from PyQt4 import QtCore, QtGui

#************************************************************************************
#
#************************************************************************************
class TemplatesWidget(QtGui.QTreeWidget):

	SettingsKeyTemplates = 'Templates'

	class MyDelegate(QtGui.QStyledItemDelegate):
		editingFinished = QtCore.pyqtSignal()

		def __init__(self, parent=None):
			QtGui.QStyledItemDelegate.__init__(self, parent)

			#NOTE: bit of a hack here. hitting <return> on edit ends editing, triggers
			# editingFinished() and propagates the KeyEvent to the parent. this gets us
			# into trouble one of our edit triggers is <return>. parent hast to clear this
			# flag to not retrigger editing (!!) this hack is broken if Qt stops propagating
			# <return> to parent. indicator: <return> triggers editing one time and then stops
			# working as a trigger.
			self.edReturnPressed= False

		def createEditor(self, parent, option, index):
			ed = QtGui.QLineEdit(parent)
			ed.setMaxLength(Tc2Config.MaxName)
			ed.editingFinished.connect(self.onEditingFinished)
			ed.returnPressed.connect(self.onEdReturnPressed)
			return ed
		def onEditingFinished(self):
			self.editingFinished.emit()
		def onEdReturnPressed(self):
			self.edReturnPressed= True

	class ActionNewTemplate(QtGui.QAction):
		def __init__(self, templateProto, parent=None):
			QtGui.QAction.__init__(self, parent)
			self.templateProto = templateProto
			self.setText(self.templateProto.menuName() )
			self.setShortcut(self.templateProto.shortcut() )
			self, self.triggered.connect(self.onTriggered)
		def onTriggered(self):
			self.parent().createTemplate(self.templateProto)


	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)

		#TODO: find a better way to set template manager as global
		Tc2Config.globalObject.objectCreatedTemplateManager.emit(self)

		# setup treeWidget
		self.setUniformRowHeights(True)
		self.setColumnCount(2)
		self.setExpandsOnDoubleClick(False)
		self.setSelectionBehavior(self.SelectRows)
		self.header().setVisible(False)
		self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.header().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)

		self.myDelegate = self.MyDelegate(parent=self)
		self.setItemDelegate(self.myDelegate)

		self._templatesRead = False
		self._screenshotSize = None	#  QSize

		# setup actions
		self._actions = []

		menu = QtGui.QMenu(self)
		for templateProto in Tc2ConfigTemplates.Templates:
			menu.addAction(self.ActionNewTemplate(templateProto, parent=self) )

		self.actionNew = QtGui.QAction(self)
		self.actionNew.setText('New')
		self.actionNew.setToolTip('Create a new template')
		self.actionNew.setMenu(menu)
		self._actions.append(self.actionNew)

		self.actionUp = QtGui.QAction(self)
		self.actionUp.setText('Up')
		self.actionUp.setToolTip('Move template up (Alt+Up)')
		self.actionUp.setShortcut(QtGui.QKeySequence('Alt+Up') )
		self.actionUp.triggered.connect(self.moveTemplateUp)
		self._actions.append(self.actionUp)

		self.actionDown = QtGui.QAction(self)
		self.actionDown.setText('Down')
		self.actionDown.setToolTip('Move template down (Alt+Down)')
		self.actionDown.setShortcut(QtGui.QKeySequence('Alt+Down') )
		self.actionDown.triggered.connect(self.moveTemplateDown)
		self._actions.append(self.actionDown)

		self.actionRemove = QtGui.QAction(self)
		self.actionRemove.setText('Remove')
		self.actionRemove.setToolTip('Remove template (Alt+Del)')
		self.actionRemove.setShortcut(QtGui.QKeySequence('Alt+Del') )
		self.actionRemove.triggered.connect(self.removeTemplate)
		self._actions.append(self.actionRemove)

		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
		Tc2Config.globalObject.widgetScreenshotSet.connect(self.onWidgetScreenshotSet)
		Tc2Config.globalObject.widgetScreenshotDoubleClicked.connect(self.onWidgetScreenshotDoubleClicked)

		# connect to TreeWidget signals
		self.itemDoubleClicked.connect(self.onEditItemInPlace)
		self.itemExpanded.connect(self.onItemExpanded)
		self.itemCollapsed.connect(self.onItemCollapsed)
		self.itemSelectionChanged.connect(self.adjustActions)

		# connect to ietm delegate signals
		self.myDelegate.editingFinished.connect(self.onTemplateEditInPlaceFinished)

	#----------------------------------------------------------------------------------------------------------------
	# overwritten methods
	#---------------------------------------------------------------------------------------------------------------

	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
			if self.myDelegate.edReturnPressed:
				self.myDelegate.edReturnPressed = False
			else:
				event.accept()
				item = self.currentItem()
				if item is not None:
					if item.topLevel() is item:
						self.editItem(item)
					return
		return QtGui.QTreeWidget.keyReleaseEvent(self, event)

	#----------------------------------------------------------------------------------------------------------------
	# methods
	#---------------------------------------------------------------------------------------------------------------
	def __iter__(self):
		for i in xrange(len(self)):
			yield self.topLevelItem(i)

	def __len__(self):
		return self.topLevelItemCount()

	def actions(self):
		return self._actions

	def adjustActions(self):
		self.actionNew.setEnabled(len(self) < Tc2Config.MaxTemplates)
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			self.actionDown.setEnabled(False)
			self.actionRemove.setEnabled(False)
		else:
			self.actionUp.setEnabled(self.canMoveTemplateUp() )
			self.actionDown.setEnabled(self.canMoveTemplateDown() )
			self.actionRemove.setEnabled(True)

	#TODO: there is a is a bug in Qt4.6.2. last items text(1) is never updated.
	#			[http://bugreports.qt.nokia.com/browse/QTBUG-4849]
	# looks like there is no way to workaround. tried removing / reinsterting items
	# but this runs into more bugs, resulting in loosing templates on certain occasions
	#
	# test is: open screenshot, create new item. this items flag is never set to '//Edit//'
	# move item up --> flag gets shown. guess its best to leave it as is and wait for Qt
	# fixing bugs.
	def adjustTemplates(self):
		self.setUpdatesEnabled(False)

		tmp_templates = {}
		for template in self:
			id = template.id()
			size = template.size
			templateType = '%s-%sx%s' % (id, template.size.width(), template.size.height())
			if templateType not in tmp_templates:
				tmp_templates[templateType] = [template]
			else:
				tmp_templates[templateType].append(template)

		for templateType, templates in tmp_templates.items():
			conflicts = [i for i in templates if i.size != Tc2Config.SizeNone]
			for template in templates:
				flag = 'Conflict' if len(conflicts) > 1 else None
				if flag is None:
					if self._screenshotSize == Tc2Config.SizeNone:
						pass
					elif template.size == Tc2Config.SizeNone:
						flag = 'Edit'
					elif template.size == self._screenshotSize:
						flag = 'Edit'
					else:
						pass
				if flag is None:
					template.setText(1, '')
				else:
					template.setText(1, '//%s//' % flag)

		self.setUpdatesEnabled(True)

	def canMoveTemplateUp(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(item.topLevel() ) > 0
		return False

	def canMoveTemplateDown(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
		else:
			return self.indexOfTopLevelItem(item.topLevel() ) < len(self) -1
		return False

	def createTemplate(self, templateProto):
		names = [i.name() for i in self]
		name = templateProto.menuName()
		name = Tc2Config.uniqueName(name, names)
		template = templateProto(parent=self, name=name)
		self.addTopLevelItem(template)
		self.setCurrentItem(template)
		template.setExpanded(True)
		self.dump()
		Tc2Config.globalObject.widgetScreenshotQuery.emit()

	def dump(self):
		Tc2Config.dumpPersistentItems(self.SettingsKeyTemplates, self)

	def moveTemplateDown(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(item.topLevel() )
		template = self.takeTopLevelItem(index)
		self.insertTopLevelItem(index +1, template)
		#NOTE: for some reason Qt collapses items on TakeItem()
		template.setExpanded(template.itemIsExpanded)
		self.setCurrentItem(template)
		self.dump()

	def moveTemplateUp(self):
		item = self.currentItem()
		if item is None:
			self.actionUp.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(item.topLevel() )
		template = self.takeTopLevelItem(index)
		self.insertTopLevelItem(index -1, template)
		#NOTE: for some reason Qt collapses items on TakeItem()
		template.setExpanded(template.itemIsExpanded)
		self.setCurrentItem(template)
		self.dump()

	def removeTemplate(self):
		item = self.currentItem()
		if item is None:
			self.actionRemove.setEnabled(False)
			return
		index = self.indexOfTopLevelItem(item.topLevel() )
		self.takeTopLevelItem(index)
		self.dump()
		self.adjustTemplates()

	#--------------------------------------------------------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------------------------------------------------------
	def onEditItemInPlace(self, item):
		if item.flags() & QtCore.Qt.ItemIsEditable:
			self.editItem(item)

	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.setUpdatesEnabled(False)
		self.clear()
		template = None
		for template in Tc2Config.readPersistentItems(self.SettingsKeyTemplates, maxItems=Tc2Config.MaxTemplates, itemProtos=Tc2ConfigTemplates.Templates):
			self.addTopLevelItem(template)
			template.setExpanded(template.itemIsExpanded)
		# set at least one template as default
		if template is None:
			template = Tc2ConfigTemplates.TemplatePokerStarsTable()
			self.addTopLevelItem(template)
			template.setExpanded(True)
		self._templatesRead = True
		self.setCurrentItem( self.topLevelItem(0) )
		self.setUpdatesEnabled(True)
		self.adjustActions()

		self.setAlternatingRowColors(globalObject.settingsGlobal.alternatingRowColors())
		globalObject.settingsGlobal.alternatingRowColorsChanged.connect(self.setAlternatingRowColors)
		self.setRootIsDecorated(globalObject.settingsGlobal.childItemIndicators())
		globalObject.settingsGlobal.childItemIndicatorsChanged.connect(self.setRootIsDecorated)
		globalObject.widgetScreenshotQuery.emit()

	def onItemCollapsed(self, item):
		if not self._templatesRead:
			return
		if item.topLevel().handleItemCollapsed(item):
			self.dump()

	def onItemExpanded(self, item):
		if not self._templatesRead:
			return
		if item.topLevel().handleItemExpanded(item):
			self.dump()

	def onTemplateEditInPlaceFinished(self):
		item = self.currentItem()
		if item is not None:
			if item.topLevel().handleEditInPlaceFinished(item):
				self.dump()

	def onWidgetScreenshotDoubleClicked(self, pixmap, point):
		item = self.currentItem()
		if item is None:
			return False
		if item.topLevel().handleScreenshotDoubleClicked(item, pixmap, point):
			self.dump()
			self.adjustTemplates()

	def onWidgetScreenshotSet(self, pixmap):
		for template in self:
			template.handleScreenshotSet(pixmap)
		self._screenshotSize = Tc2Config.newSizeNone() if pixmap.isNull() else QtCore.QSize(pixmap.size())
		self.adjustTemplates()
