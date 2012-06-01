"""auto generates resource files"""
from __future__ import with_statement
import os
from PyQt4 import QtCore, QtGui

#*********************************************************************************************
#
#*********************************************************************************************
app = QtGui.QApplication([])

DirSelf = os.path.dirname( os.path.abspath(__file__) )
DirRes = DirSelf
DirPixmaps = os.path.join(DirRes, 'Pixmaps')
DirHtmlPages = os.path.join(DirRes, 'HtmlPages')

MaxChunkSize = 64
def splitIterableToChunks(iterable, n):
	return [iterable[i:i+n] for i in range(0, len(iterable), n)]


def main():

	if os.path.isdir(DirPixmaps):
		# gen Pixmaps.py
		with open(os.path.join(DirRes, 'Pixmaps.py'), 'w') as fp:
			fp.write('#WARNING: this file is auto-generated - do not edit!\n\n')
			fp.write('from PyQt4 import QtCore, QtGui\n\n')
			for name in sorted(os.listdir(DirPixmaps)):
				fileName = os.path.join(DirPixmaps, name)
				if not os.path.isfile(fileName): continue
				if not os.path.splitext(name)[1].lower() == '.png': continue
				arr = QtCore.QByteArray()
				p = QtCore.QBuffer(arr)
				p.open(p.WriteOnly)
				px = QtGui.QPixmap(fileName, 'PNG')
				px.save(p, 'png')
				data = str(arr.toBase64())
				data = splitIterableToChunks(data, MaxChunkSize)

				functionName = os.path.splitext(name)[0]
				fp.write('def pixmap%s(cache=[]):\n' % functionName)
				fp.write('\tif not cache:\n')
				fp.write('\t\tarr = QtCore.QByteArray.fromBase64(\n')
				for chunk in data:
					fp.write("\t\t\t'%s'\n" % chunk)
				fp.write('\t\t\t)\n')
				fp.write('\t\tpx = QtGui.QPixmap()\n')
				fp.write('\t\tpx.loadFromData(arr, "PNG")\n' )
				fp.write('\t\tcache.append(px)\n')
				fp.write('\treturn cache[0]\n\n')

#*********************************************************************************************
#
#*********************************************************************************************
if __name__ == '__main__': main()
