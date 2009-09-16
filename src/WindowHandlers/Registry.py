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
		typeKlass = newKlass.Type
		if newKlass.Site is None and newKlass.Window is not None:
			raise ValueError('if windowHandlers define Site, Window must be defined aswell')
		if newKlass.Site is not None:
			typeKlass += ':%s' % newKlass.Site
			if newKlass.Window is not None:
				typeKlass += ':%s' % newKlass.Window
		if typeKlass in WindowHandlerRegistry:
			raise ValueError('windowHandler already registered: %s' % typeKlass)
		newKlass.Type = typeKlass
		WindowHandlerRegistry[typeKlass] = newKlass
		return newKlass


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
	
	