"""platform package

all platform dependend code should go into the modules in this directory
"""

import sys

if sys.platform == 'darwin':
	from PlatformMac import *
elif sys.platform == 'linux2':
	from PlatformX11 import *
elif sys.platform == 'win32':
	from PlatformWin32 import *
