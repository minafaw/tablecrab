"""sample code on how to addd a new site to TableCrab
"""

from PyQt4 import QtCore, QtGui

# import global config
import Tc2Config
# import Tc2Gui for subclassing
import Tc2Gui
# another import we need is Tc2ConfigTemplates cos we need to register a template
# for the sites table
import Tc2ConfigTemplates

#************************************************************************************
#
#************************************************************************************

# first we have to create a site handler to handle window events
class MySiteHandler(object):

	def __init__(self, parent, mySettings):
		pass

	# the site handler will be called on in the following methods whenever an event occures

	def handleWindowCreated(self, hwnd):
		# called whenever a window is created
		# return True if you handle the event
		return False

	def handleWindowDestroyed(self, hwnd):
		# called whenever a window is destroyed
		# return True if you handle the event
		return False

	def handleWindowGainedForeground(self, hwnd):
		# called whenever a window is put to the foreground
		# return True if you handle the event
		return False

	def handleWindowLostForeground(self, hwnd):
		# called whenever a window is put to the background
		# return True if you handle the event
		return False

	def handleInputEvent(self, hwnd, hotkey, inputEvent):
		# called whenever a mouse or keyboard event occures in the window
		# param hotkey: one of the hotkeys tobe found in Tc2ConfigHotkeys
		# param inputEvent: an input event as defined in Tc2Win32
		# return True if you handle the event
		# set inputEvent.accept to True to not propagate it further to the window
		return False


# we may want to add custom settings. the settings can
class MySettings(QtGui.QFrame):

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		# this is the signal we have to connect to to get informed that we should
		# now read settings values in
		Tc2Config.globalObject.initSettings.connect(self.onInitSettings)

	# read in our settings from config and initialize our widgets here
	def onInitSettings(self):
		pass



# and a custom table template which is basically a tree widget item that derrives
# from TemplateBase. template instances can be found at runtime by iterating over
# Tc2Config.globalObject.templateManager
class MyTemplate(Tc2ConfigTemplates.TemplateBase):

	# indicates theat this item is the top level item of the template
	# for all child items this has to be set to False. interaction with the tree widget
	# always goes through the top level item.
	IsTopLevel = True

	def __init__(self, parent=None):
		Tc2ConfigTemplates.TemplateBase.__init__(parent)

	@classmethod
	def fromConfig(klass, key):
		# this is the most important method of the template
		# here the template should be read from config
		# param key: the key where it is to be found
		# the method should return a new instance of this class or None if the template
		# can not be successfuly restored from the key (and subkeys)
		return None

	def toConfig(self, key):
		# the reverse method to the above
		# here the template should be saved config
		# return True if the template could be successfuly saved
		return False

	@classmethod
	def id(klass):
		# this method should return the unique name of the template
		return 'MySitesTemplate'

	@classmethod
	def menuName(klass):
		# this method should return the name of the template as it is read to the user in the menu
		return 'My Template'

	@classmethod
	def shortcut(klass):
		# this method should return the shortcut the user can hit to create a new template
		return QtGui.QKeySequence('Shift+X')


	def name(self):
		# should return the display name of the template
		return 'MyTemplate'


	# the following methods are methods to interact with the tree widget


	def handleEditInPlaceFinished(self, item):
		# this method gets called whenever in-place editing is finished
		# param item: the item that has been edited
		# return True if you handle the event. if so toConfig() will be called in response
		# to save changes to config
		return False


	def handleItemExpanded(self, item):
		# this method is called whenever an item is expanded
		# return True if you handle the event. if so toConfig() will be called in response
		# to save changes to config
		return False

	def handleItemCollapsed(self, item):
		# this method is called whenever an item is expanded
		# return True if you handle the event. if so toConfig() will be called in response
		# to save changes to config
		return False

	def handleScreenshotSet(self, pixmap):
		# this method is called whenever the user takes or opens a screenshot
		# param pixmap: the screenshot pixmap
		# here you should for example check if the screenshot is handled by your
		# template and enable / disable it accordingly
		# return value is not used
		pass

	def handleScreenshotDoubleClicked(self, item, pixmap, point):
		# this method is called whenever the user double clicks a point on the screenshot
		# return True if you handle the event. if so toConfig() will be called in response
		# to save changes to config
		return False

# finally we plug in our template
Tc2ConfigTemplates.Templates.append(MyTemplate)


# then we have to subclass the main gui to plug in our site handler and settings
class MyGui(Tc2Gui.Gui):

	def __init__(self, *args,**kws):
		Tc2Gui.Gui.__init__(self, *args,**kws)

		# next init our settings
		self.mySettings = MySettings(self)
		# plug in our settings: displayName, settingsInstance, keyboardShortcut, toolTip
		self.tabSettings().addSetting('MySettingsName', self.mySettings, 'Shift+X', 'MySettingsToolTip')

		# init our site handler
		self.mySiteHandler = MySiteHandler(self, self.mySettings)
		# plug in our site handler
		# now our site handler is plugged in and gets called on every window event
		# as soonn as the gui is up and alive
		self.siteManager().addSiteHandler(self.mySiteHandler)






















