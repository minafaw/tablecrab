"""modifies stars themes. no XThemes bells and whistels. just pure hacks. all image files (bmp, jpg) are
copied "as is" form the PokerStars folder to stars folder.

you have to run this script everytime you updated stars. by default stars updates on every start, so you may have to 
run it everytime you start your starts client.

@note: diretories starting with '_' are skipped in the process
@requires: python imaging

usage: Cli.py path/to/PokerStarsExeFolder [path/to/ModFolder]

"""
from __future__ import absolute_import, with_statement
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]


import Image, os, shutil

#**********************************************************************************
DIR_SELF = os.path.dirname(os.path.abspath(__file__))
DIR_MODS = os.path.join(DIR_SELF, 'Mods')

def relpath(src, dst):
	return dst[len(src) +1:]


def main(dirPokerStars, dirMods=DIR_MODS):
	
	print 'copying mods'
	print '    STARS == %s' % dirPokerStars
	print '    MODS == %s' % dirMods
	
	for root, dirs, files in os.walk(dirMods):
		skipDirs = [name for name in dirs if name.startswith('_')]
		for name in skipDirs: dirs.remove(name)
			
		for name in files:
			src = os.path.join(root, name)
			if not os.path.isfile(src): continue
			if os.path.splitext(name)[1].lower() not in ('.bmp', '.jpg'): continue
			relname = relpath(dirMods, src)
			print '        --> %s' % relname
			dst = os.path.join(dirPokerStars,  relname)
			shutil.copyfile(src, dst)
			
	print 'done'
			

if __name__ == '__main__': 
	import sys
	if len(sys.argv) == 2:
		main(sys.argv[1])
	elif len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print __doc__

	
	


	



