"""generates developer documentation and dumps it to TableCrab/Doc/Devel

@requires: epydoc
@note: this script assumes it lives in TableCrab/Scripts
"""
from __future__ import with_statement

import sys, os
from epydoc import cli

#**********************************************************************
DirPackage = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))	
DirDoc = os.path.join(DirPackage, 'Doc')
DirNameDevel = 'Devel'
DirDocDevel = os.path.join(DirDoc, DirNameDevel)
FileNameIndex =  'index-devel-docs.html'

#*********************************************************************
def main():
	
	print 'generating developer documentation'
	
	# enshure all directories exist
	for d in (DirPackage, DirDoc, DirDocDevel):
		if not os.path.isdir(d):
			raise ValueError('expected directory to exist: %s' % d)
			
	# call epydoc
	sys.argv = [
			__file__, 
			'-v', 
			'-o%s' % DirDocDevel, 
			'--parse-only',		# NOTE: epydoc seems to have problems with our relative imports, so parse only
			'--src-code-tab-width', '4',
			#'--debug',
			DirPackage,
			]
	cli.cli()
	
	# create a redirect to 'epydoc/index.html'
	filePathIndex = os.path.join(DirDoc, FileNameIndex)
	print 'creating redirect: %s', filePathIndex
	with open(filePathIndex, 'w') as fp:
		fp.write('''<html>
	<head>
		<meta http-equiv="Refresh" content="0; URL=%s">
	</head>
</html>
''' % (DirNameDevel + '/' + 'index.html') 
	)	
		
	print 'done'

#********************************************************************
if __name__ == '__main__': main()
			
	
	





