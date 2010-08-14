"""window handler registry
""" 
WindowHandlerRegistry = {}
WindowHandlerType = 'WindowHandler'

class WindowHandlerMeta(type):
	"""metaclass for all window handlers
	"""
	def __new__(klass, name, bases, kws):
		newKlass = type.__new__(klass, name, bases, kws)
		if newKlass.Type is None:
			return newKlass
		newKlass.Type = klass.createTypeName(newKlass)
		WindowHandlerRegistry[newKlass.Type] = newKlass
		return newKlass
		
	@classmethod
	def createTypeName(klass, windowHandlerKlass):
		"""creates the type name for a window handler class
		@param windowHandlerKlass: class to create the type name for
		@return: (str) type name
		@note: use this method to create a unique type name for window handlers that are not intendet to be registered
		"""
		typeName = windowHandlerKlass.Type
		if windowHandlerKlass.Site is None and windowHandlerKlass.Window is not None:
			raise ValueError('if windowHandlers define Site, Window must be defined aswell')
		if windowHandlerKlass.Site is not None:
			typeName += ':%s' % windowHandlerKlass.Site
			if windowHandlerKlass.Window is not None:
				typeName += ':%s' % windowHandlerKlass.Window
		if typeName in WindowHandlerRegistry:
			raise ValueError('windowHandler already registered: %s' % typeKlass)
		return typeName
		


class WindowHandlerBase(object):
	"""base class for window handlers
	
	@cvar Type: should always be L{WindowHandlerType} to register a handler. if None, the handler is not registered. if not None, this gets filled in at 
	compile time by L{WindowHandlerMeta} to form the unique type name of the handler
	@cvar Site: (str) name of thesite to handle
	@cvar Window: (str) name of the window handled
	
	@note: the combination of Type + Site + Window is used to tell window handlers apart. so make shure it is unique
	"""
	__metaclass__ = WindowHandlerMeta
	Type = None
	Site = None
	Window = None
	
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		"""called when a new window is detected
		@param cli: client instance
		@param hWindow: handle of the window
		@return:None to not handle the window, window handler instance to handle the window
		"""
		return None
		
	def handleWindowDestroyed(self, cli, hWindow):
		"""called when a window is no longer present
		@param cli: client instance
		@param hWindow: handle of the window
		@warning: hWindow is no longer a valid handle by the time this is called
		@return: True if the handler handles the event, False otherwise
		"""
		return False
	def handleWindowGainForeground(self, cli, hWindow):
		"""called when a window gains foreground status
		@param cli: client instance
		@param hWindow: handle of the window
		@return: True if the handler handles the event, False otherwise
		"""
		return False
	def handleWindowLooseForeground(self, cli, hWindow):
		"""called when a window looses foreground status
		@param cli: client instance
		@param hWindow: handle of the window
		@return: True if the handler handles the event, False otherwise
		"""
		return False
	def handleKeyPressed(self, cli, key):
		"""called when a key is pressed while the window is the foreground window
		@param key: KeyboardManager.Key instance
		@return: True if the handler handles the event, False otherwise
		@note: if you return True, the key press is swallowed, that is, it never reaches the window
		"""
		return False
	def handleKeyReleased(self, cli, key):
		"""called when a key is released while the window is the foreground window
		@param cli: client instance
		@param key: KeyboardManager.Key instance
		@return: True if the handler handles the event, False otherwise
		@note: if you return True, the key press is swallowed, that is, it never reaches the window
		"""
		return False
	
	