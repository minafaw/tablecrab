"""window handlers
"""
from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]
	
from .Registry import WindowHandlerRegistry
from .Registry import WindowHandlerType

from . import WindowHandlerDefault

from . import PokerStarsTable
from . import PokerStarsPopupNews


