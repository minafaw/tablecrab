"""auto generates resource files"""
from __future__ import with_statement
import os
from PyQt4 import QtCore, QtGui

#*********************************************************************************************
#
#*********************************************************************************************
app = QtGui.QApplication([])

DirSelf = os.path.dirname( os.path.abspath(__file__) )
DirPixmaps = os.path.join(DirSelf, 'Pixmaps')
DirHtmlPages = os.path.join(DirSelf, 'HtmlPages')

def main():
	
	# gen Pixmaps.py
	with open(os.path.join(DirSelf, 'Pixmaps.py'), 'w') as fp:
		fp.write('# auto generated resource file. WARNING: do not edit\n')
		fp.write('from PyQt4 import QtCore, QtGui\n')
		fp.write('_cache = {}\n')
		for name in os.listdir(DirPixmaps):
			fileName = os.path.join(DirPixmaps, name)
			if not os.path.isfile(fileName): continue
			if not os.path.splitext(name)[1].lower() == '.png': continue
			arr = QtCore.QByteArray()
			p = QtCore.QBuffer(arr)
			p.open(p.WriteOnly)
			px = QtGui.QPixmap(fileName, 'PNG')
			px.save(p, 'png')
			
			funtionName = os.path.splitext(name)[0]
			fp.write('def %s():\n' % funtionName)
			fp.write('\tpx = _cache.get("%s", None)\n' % funtionName)
			fp.write('\tif px is None:\n')
			fp.write('\t\tarr = QtCore.QByteArray.fromBase64("%s")\n' % arr.toBase64() )
			fp.write('\t\tpx = QtGui.QPixmap()\n')
			fp.write('\t\tpx.loadFromData(arr, "PNG")\n' )
			fp.write('\t\t_cache["%s"] = px\n' % funtionName)
			fp.write('\treturn px\n')
					
	# gen HtmlPages.py
	with open(os.path.join(DirSelf, 'HtmlPages.py'), 'w') as fp:
		fp.write('# auto generated resource file. WARNING: do not edit\n')
		fp.write('from PyQt4 import QtCore\n')
		fp.write('_cache = {}\n')
		for name in os.listdir(DirHtmlPages):
			fileName = os.path.join(DirHtmlPages, name)
			if not os.path.isfile(fileName): continue
			if not os.path.splitext(name)[1].lower() == '.html': continue
			with open(fileName, 'r') as fp2:
				arr = QtCore.QByteArray(fp2.read() )
			
			funtionName = os.path.splitext(name)[0]
			fp.write('def %s():\n' % funtionName)
			fp.write('\tarr = _cache.get("%s", None)\n' % funtionName)
			fp.write('\tif arr is None:\n')
			fp.write('\t\tarr = QtCore.QByteArray.fromBase64("%s")\n' % arr.toBase64() )
			fp.write('\t\t_cache["%s"] = arr\n' % funtionName)
			fp.write('\treturn QtCore.QString(arr)\n')
	
# gen StyleSheets.py
with open(os.path.join(DirSelf, 'StyleSheets.py'), 'w') as fp:
		fp.write('# auto generated resource file. WARNING: do not edit\n')
		fp.write('from PyQt4 import QtCore\n')
		fp.write('_cache = {}\n')
		for name in os.listdir(DirHtmlPages):
			fileName = os.path.join(DirHtmlPages, name)
			if not os.path.isfile(fileName): continue
			if not os.path.splitext(name)[1].lower() == '.css': continue
			with open(fileName, 'r') as fp2:
				arr = QtCore.QByteArray(fp2.read() )
			
			functionName = os.path.splitext(name)[0]
			fp.write('def %s():\n' % functionName)
			fp.write('\tarr = _cache.get("%s", None)\n' % functionName)
			fp.write('\tif arr is None:\n')
			fp.write('\t\tarr = QtCore.QByteArray.fromBase64("%s")\n' % arr.toBase64() )
			fp.write('\t\t_cache["%s"] = arr\n' % functionName)
			fp.write('\treturn QtCore.QString(arr)\n')
	

	
#*********************************************************************************************
#
#*********************************************************************************************	
if __name__ == '__main__': main()