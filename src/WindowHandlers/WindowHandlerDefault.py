"""default window handler for unhandled windows
""" 
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]


from . import Registry

#******************************************************************************
class WindowHandlerDeafult(Registry.WindowHandlerBase):
	"""fallback window handler if no handler is present for a window"""
	Type = Registry.WindowHandlerType
	Site = None
	Window = None
	
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		return klass(cli, hWindow)
		
	def __init__(self, cli, hWindow):
		self.cli = cli
		self.hWindow = hWindow
	