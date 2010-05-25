'''simple client interface for testing
'''

from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

from .Platform import Application
from . import Config

#******************************************************************************************
class CliTest(object):
	Type = 'Cli'
	
	def __init__(self, config=None):
		self.config = Config.Config() if config is None else config
		self.application = Application.Application(cb=self.onApplication)
		self.application.mouseManager.setCB(self.onMouseManager)
		self.application.keyboardManager.setCB(self.onKeyboardManager)
		self.application.windowManager.setCB(self.onWindowManager)
			
	def start(self):
		self.application.start()
	def stop(self):
		self.application.stop()
	def onApplication(self, application, evt, arg):
		print application.Type, evt, arg
	def onMouseManager(self, mouseManager, evt, arg):
		print mouseManager.Type, evt, arg
	def onKeyboardManager(self, keyboardManager, evt, arg):
		if evt in (keyboardManager.EvtKeyPressed, keyboardManager.EvtKeyReleased):
			print keyboardManager.Type, evt, arg.value
		else:
			print keyboardManager.Type, evt, arg
	def onWindowManager(self, windowManager, evt, arg):
		print windowManager.Type, evt, arg

if __name__ == '__main__':
	cli = CliTest()
	cli.start()
