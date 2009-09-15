from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

"""homebrewn release routine
this script zips the sources from local trunk and dumps them to 'tags/ReleaseName.zip'

NOTE: this script assumes it lives in trunk/

NOTE: would love to ship the package out as executable but having troubles with py2exe (relative imports, msvcrt). 
maybe McMillian's installer [http://www.pyinstaller.org/] may be helpful some time soon.

"""

import os, zipfile

from .src import Config
#*****************************************************************************
DirSelf = os.path.dirname(os.path.abspath(__file__))
DirSrc = os.path.join(DirSelf, 'src')
DirTags = os.path.join(os.path.dirname(DirSelf), 'tags')
ReleaseName = '%s-%s' % (Config.__application_name__, Config.__version__)
DirRelease = os.path.join(DirTags, ReleaseName)

IncludeExts = ('.py', '.txt', '.cfg', '.mit')


def main():
	# some tests that we are resided in the right location
	if not os.path.basename(DirSelf) == 'trunk':
		raise ValueError('we should always be in trunk/')
	if not os.path.isdir(DirTags):
		raise ValueError('tags/ directory not found')
		
	# make shure release exists in tags/
	if not os.path.isdir(DirRelease):
		os.makedirs(DirRelease)
		
	# collect files to include
	fileList = []
	for root, dirs, files in os.walk(DirSrc):
		files = [i for i in files if os.path.splitext(i)[1].lower() in IncludeExts]
		if files:
			for file in files:
				fPath = os.path.join(root, file)
				fPathRel = fPath[len(DirSrc)+1: ]
				fileList.append( (fPath, fPathRel) )
		
	# dump files to zip
	zipName = os.path.join(DirRelease, ReleaseName + '.zip')
	zip = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
	try:
		for fPath, fPathRel in fileList:
			zip.write(fPath, fPathRel)
	finally:
		zip.close()

#***********************************************************************
if __name__ == '__main__': main()

