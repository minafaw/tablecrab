"""window handler for PokerStars table message boxes
""" 
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

from . import Registry
from . import PokerStarsWindowBase

#********************************************************************************************

# other message boxes seen..
#title: 'Tournament 289169082 Lobby', class:'#32770'


class PokerStarsTableMessageBox(PokerStarsWindowBase.PokerStarsWindowBase):
	""""""
	Type = Registry.WindowHandlerType
	Site = 'PokerStars'
	Window = 'TableMessageBox'
		
	@classmethod
	def handleWindowCreated(klass, cli, hWindow):
		if klass.psIsTableMessageBox(cli, hWindow):
			return klass(cli, hWindow)
		return None
	
	def __init__(self, cli, hWindow):
		self.cli = cli
		self.hWindow = hWindow
		if cli.config['pokerstars']['bool-auto-ok-table-message-boxes']:
			self.cli.log(self, 'click OK="%s"' % self.hWindow)
			if not cli.application.windowManager.windowClickButton(self.hWindow, 'OK'):
				self.cli.log(self, 'click OK failed="%s"' % self.hWindow)
			
	def handleWindowDestroyed(self, cli, hWindow):
		return False	
		