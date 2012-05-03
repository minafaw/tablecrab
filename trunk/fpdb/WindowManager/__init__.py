"""platform package

all platform dependend code should go into the modules in this directory. modules
should raise OSError when something is wrong with the platform they are choossen for
"""

import sys

if sys.platform == 'darwin':
	from WindowManagerMac import *
elif sys.platform == 'linux2':
	# try to find a module four current linux window system
	try:
		from WindowManagerX11Xlib import *
	except OSError:
		try:
			from WindowManagerX11Shell import *
		except OSError:
			from WindowManagerWayland import *
elif sys.platform == 'win32':
	from WindowManagerWin32 import *

