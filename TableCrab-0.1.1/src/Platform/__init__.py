from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]


import sys
if sys.platform == 'win32':
	from .Win32 import Application
else:
	raise ValueError('unsupported OS: %s' % sys.platform)
