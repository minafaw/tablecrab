
import os, subprocess, array
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
def createQPixmap(fontFamily, fontSize, chars):
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

class ImagePGM(object):
	def __init__(self, buff):
		self._buff = buff
		self._header = None
		self._minGray = None
		self._maxGray = None

	@classmethod
	def fromQPixmap(klass, image):
		'''
		@param image: (QImage, QPixmap)
		'''
		arr = QtCore.QByteArray()
		p = QtCore.QBuffer(arr)
		p.open(p.WriteOnly)
		image.save(p, format='PGM')
		return klass(arr.data())

	def toQPixmap(self):
		pixmap = QtGui.QPixmap()
		if not pixmap.loadFromData(self.toString(), 'PGM', QtCore.Qt.MonoOnly):
			raise ValueError('could not load self to pixmap')
		return pixmap


	def _grayLevels(self):
		if self._maxGray is None or self._minGray is None:
			header = self.header()
			minGray = 256
			maxGray = -1
			for i in xrange(header['offset'], len(self._buff)):
				byte = ord(self._buff[i])
				minGray = min(minGray, byte)
				maxGray = max(maxGray, byte)
			if minGray > 255: minGray = 0
			if maxGray < 0: maxGray = 0
			self._minGray = minGray
			self._maxGray = maxGray
		return self._minGray, self._maxGray

	def header(self):
		if self._header is not None:
			return self._header
		magic = ''
		width = ''
		height = ''
		gray = ''
		offset = 0
		lineno = 0
		lastChar = ''
		for i, char in enumerate(self._buff):
			if char in '\n\r\t\x20':
				if lastChar not in '\n\r\t\x20':
					lineno += 1
			if lineno >= 4:
				offset = i +1
				break
			if lineno == 0: magic += char
			elif lineno == 1: width += char
			elif lineno == 2: height += char
			elif lineno == 3: gray += char
			lastChar = char
		if magic != 'P5':
			raise ValueError('invalid pgm')
		if int(gray) > 255:
			raise NotImplementedError('2bpp pgms not yet supported')
		self._header = {
				'w': int(width),		# width of image
				'h': int(height),		# height of image
				'gray': int(gray),	# max gray level
				'offset': offset,		# offset of image data
				}
		return self._header

	def inverted(self):
		header = self.header().copy()
		bitsPerPixel =  1 if header['gray'] < 256 else 2
		if bitsPerPixel > 1:
			raise NotImplementedError('2bpp pgms not yet supported')
		maxGray = -1
		minGray = 256
		buff = 'P5\n%s %s\n255\n' % (header['w'], header['h'])
		for i in xrange(header['offset'], len(self._buff)):
			char = self._buff[i]
			byte = 255 - ord(char)
			maxGray = max(maxGray, byte)
			minGray = min(minGray, byte)
			buff += chr(byte)
		if minGray > 255: minGray = 0
		if maxGray < 0: mayGray = 0
		newPGM = self.__class__(buff)
		newPGM._header = header
		newPGM._minGray = minGray
		newPGM._maxGray = maxGray
		return newPGM

	def minGray(self):
		return self._grayLevels()[0]

	def maxGray(self):
		return self._grayLevels()[1]

	def toString(self): return self._buff

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
		grayLevel=None,	# 0-255
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
	if grayLevel is not None: cmd += '-l %i ' % grayLevel
	if certainty is not None: cmd += '-a %i ' % certainty
	if mode is not None: cmd += '-m %i ' % mode
	if verbosity is not None: cmd += '-v %i ' % verbosity

	p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	return p.communicate(string)

#************************************************************************************
# some code for playing around
#************************************************************************************
def _testBuffer():
	buff = ''	# paste image here

	pgm = ImagePGM(buff)
	header = pgm.header()
	print header, pgm.minGray(), pgm.maxGray()
	pgm = pgm.inverted()
	header = pgm.header()
	print header, pgm.minGray(), pgm.maxGray()

	stdout, stderr = scanImage(
		string=pgm.toString(),
		chars='0-9.,',
		grayLevel=pgm.maxGray(),
		#verbosity=VerbosityInfo,
		)
	print 'stdout:', stdout, repr(stdout)
	print 'stderr:', stderr, repr(stderr)
	app = QtGui.QApplication([])
	f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.pgm')
	px = QtGui.QImage(buff, header['w'], header['h'], QtGui.QImage.Format_Indexed8)
	print px.save(f, 'pgm', 100)

#_testBuffer()


def _testFont():
	import time
	app = QtGui.QApplication([])
	pixmap = createQPixmap('arial', 6, '0.1234567,89')
	pgm = ImagePGM.fromQPixmap(pixmap)
	t0 = time.time()
	stdout, stderr = scanImage(string=pgm.toString(), chars='0-9,.', dustSize=0)
	print 'time:', round(time.time() - t0, 3)
	print 'stdout:', stdout, repr(stdout)
	print 'stderr:', stderr, repr(stderr)

#_testFont()


def _testWin32():
	Hwnd = 0						# handle of the window
	Rect = 0, 0, 0, 0			# rect to grab and scan

	app = QtGui.QApplication([])
	import ctypes

	pixmap = QtGui.QPixmap.grabWindow(Hwnd, *Rect)
	pgm = ImagePGM.fromQPixmap(pixmap)
	result, err = scanImage(
								string=pgm.toString(),
								fileNameOutput=None,
								chars=None, 		# limit to these chars A-Z notation is ok
								dustSize=None,	# 0-N
								grayLevel=None,	# 0-255
								certainty=None,	# 0-100 - only recognize chars with sa certainity >= c
								mode=None,		# Mode*
								verbosity=None	# many outputs to stderr. Verbosity*
								)

	print 'result: %s' % result
	print 'err: %s' % err


 #_testWin32()




