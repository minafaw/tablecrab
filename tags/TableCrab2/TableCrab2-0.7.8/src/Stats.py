"""prints out some more or less useful stats about the project"""
from __future__ import with_statement

from PyQt4 import QtCore
import os
#************************************************************************************
#
#************************************************************************************
QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates) )
locale = QtCore.QLocale()
DirSelf = os.path.dirname(os.path.abspath(__file__))

def main(directory=DirSelf):
	stats = {
			'filesSourceCode': 0,
			'linesSourceCode': 0,
			'bytesSourceCode': 0,

			'filesDocumentation': 0,
			'linesDocumentation': 0,
			'bytesDocumentation': 0,
			}

	for root, dirs,files in os.walk(directory):
		skipDirs = []
		for name in dirs:
			if name.startswith('.'):
				skipDirs.append(name)
		for name in skipDirs:
			dirs.remove(name)

		for name in files:
			fileName = os.path.join(root,name)
			if os.path.islink(fileName): continue
			ext = os.path.splitext(name)[1].lower()
			if ext not in ('.py', '.html'): continue

			if ext == '.py':
				stats['filesSourceCode'] += 1
			elif ext == '.html':
				stats['filesDocumentation'] += 1
			with open(fileName,'r') as fp:
				for line in fp:
					line = line.strip()
					if not line: continue
					if ext == '.py':
						stats['linesSourceCode'] += 1
						stats['bytesSourceCode'] += len(line)
					elif ext == '.html':
						stats['linesDocumentation'] += 1
						stats['bytesDocumentation'] += len(line)

	print 'Source code:'
	print '\x20\x20\x20\x20Files: %s' % locale.toString(stats['filesSourceCode'])
	print '\x20\x20\x20\x20Lines: %s' % locale.toString(stats['linesSourceCode'])
	print '\x20\x20\x20\x20Bytes: %s' % locale.toString(stats['bytesSourceCode'])
	print 'Documentation:'
	print '\x20\x20\x20\x20Files: %s' % locale.toString(stats['filesDocumentation'])
	print '\x20\x20\x20\x20Lines: %s' % locale.toString(stats['linesDocumentation'])
	print '\x20\x20\x20\x20Bytes: %s' % locale.toString(stats['bytesDocumentation'])




if __name__ == '__main__': main()


