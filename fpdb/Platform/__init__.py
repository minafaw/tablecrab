"""platform package

all platform dependend code should go into the modules in this directory
"""

import sys

if sys.platform == 'darwin':
	from PlatformMac import *
elif sys.platform == 'linux2':
	#NOTE: xlib is way faster
	try:
		from PlatformX11Xlib import *
	except OSError:
		from PlatformX11Shell import *
elif sys.platform == 'win32':
	from PlatformWin32 import *
