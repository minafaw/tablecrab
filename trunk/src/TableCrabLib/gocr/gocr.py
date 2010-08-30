
import os, subprocess
from PyQt4 import QtCore, QtGui

#************************************************************************************
# helpers
#************************************************************************************
# locate gocr.exe in PyInstaler it is included in data dir == os.environ _MEIPASS2
DirData = os.environ.get('_MEIPASS2', None)
if DirData is None:
	DirData = os.path.dirname(os.path.abspath(__file__))
FileNameGocr = os.path.join(DirData, 'gocr048.exe')

# for testing. creates a pixmap and dumps some chars on it
def createPixmap(fontFamily, fontSize, chars):
	font = QtGui.QFont(fontFamily, fontSize)
	fm = QtGui.QFontMetrics(font)
	rc = fm.boundingRect(chars)
	offs = 10
	w = rc.size().width() + (2*offs)
	h = rc.size().height() + (2* offs)
	pixmap = QtGui.QPixmap(w, h)
	painter = QtGui.QPainter()
	painter.begin(pixmap)
	painter.fillRect(0, 0, w, h, QtCore.Qt.white)
	painter.setFont(font)
	painter.drawText(offs, h - offs, chars)
	painter.end()
	return pixmap

def imageToByteArray(image, format='PNG'):
	'''
	@param image: (QImage, QPixmap)
	'''
	arr = QtCore.QByteArray()
	p = QtCore.QBuffer(arr)
	p.open(p.WriteOnly)
	image.save(p, format)
	return arr

def imageToString(image, format='PNG'):
	return imageToByteArray(image, format=format).data()

#************************************************************************************
# gocr wrapper
#************************************************************************************
VerbosityInfo = 0x1
VerbosityShapeBoxes = 0x2
VerbotityPatternBoxes = 0x4
VerbosityPatternRecognition = 0x8
VerbosityLineRecognition = 0x10
VerbosityCreateOutImages = 0x20

ModeNoContextCorrection = 0x20
# .. more here

def scanImage(
		fileNameGocr=FileNameGocr,
		fileName=None,	# file name or None to scan string
		string=None,		# string to scan or None if a file name is specified
		fileNameOutput=None,
		chars=None, 		# limit to these chars A-Z notation is ok
		dustSize=None,	# 0-N
		#grayLevel=None,	# 0-255
		certainty=None,	# 0-100 - only recognize chars with sa certainity >= c
		mode=None,		# Mode*
		verbosity=None	# many outputs to stderr. Verbosity*
		# .. more here
		):
	'''
	@return: (tuple) (str out, str err)
	'''
	cmd = '"%s" ' % fileNameGocr
	if fileName is None:
		if string is None:
			raise ValueError('no string specified')
		fileName = '-'
	cmd += '-i %s ' % fileName
	if fileNameOutput is not None:
		cmd = '-o "%s" ' % fileNameOutput
	if chars is not None: cmd += '-C %s ' % chars
	if dustSize is not None: cmd += '-d %i ' % dustSize
	if certainty is not None: cmd += '-a %i ' % certainty
	if mode is not None: cmd += '-m %i ' % mode
	if verbosity is not None: cmd += '-v %i ' % verbosity

	p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return p.communicate(string)



def test():
	import time
	app = QtGui.QApplication([])

	pixmap = createPixmap('arial', 6, '0.1234567,89')
	buff = imageToString(pixmap, format='PBM')
	t0 = time.time()
	stdout, stderr = scanImage(string=buff, chars='0-9,.', dustSize=0)
	print 'time:', round(time.time() - t0, 3)
	print 'stdout:', stdout
	print 'stderr:', stderr

if __name__ == '__main__': test()





