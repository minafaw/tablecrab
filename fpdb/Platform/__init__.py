"""platform package

all platform dependend code should go into the modules in this directory. modules
should raise OSError when something is wrong with the platform they are choossen for
"""

import sys

if sys.platform == 'darwin':
	from PlatformMac import *
elif sys.platform == 'linux2':
	# try to find a module four current linux window system
	try:
		from PlatformX11Xlib import *
	except OSError:
		try:
			from PlatformX11Shell import *
		except OSError:
			from PlatformWayland import *
elif sys.platform == 'win32':
	from PlatformWin32 import *
