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
	__metaclass__ = WindowHandlerMeta
	Type = None			# should always be WindowHandlerType. if None, the class is not registered as WindowHandler
	Site = None			# site handled
	Window = None		# window handled
	
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		return None
		
	def handleWindowDestroyed(self, cli, hWindow):
		return False
	def handleWindowGainForeground(self, cli, hWindow):
		return False
	def handleWindowLooseForeground(self, cli, hWindow):
		return False
	def handleKeyPressed(self, cli, key):
		return False
	def handleKeyReleased(self, cli, key):
		return False
	
	