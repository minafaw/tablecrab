
import os, sys, subprocess, array
from PyQt4 import QtCore, QtGui

#************************************************************************************
# helpers
#************************************************************************************
# locate gocr.exe in PyInstaler it is included in data dir == os.environ _MEIPASS2
DirData = os.environ.get('_MEIPASS2', None)
if DirData is None:
	DirData = os.path.dirname(os.path.abspath(__file__))
FileNameGocr = os.path.join(DirData, 'gocr049.exe')

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
	def new(klass, w, h, buff):
		if w * h != len(buff):
			raise ValueError('exepected buffer of length %s' % w * h)
		return klass('P5\n%s\x20%s\n255\n%s' % (w, h, buff))

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
				if lastChar in '\n\r\t\x20':
					continue
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

	def save(self, fileName):
		fp = open(fileName, 'wb')
		try:
			fp.write(self._buff)
		finally:
			fp.close()

#************************************************************************************
# gocr wrapper
#************************************************************************************
# see: [ http://manpages.ubuntu.com/manpages/intrepid/man1/gocr.1.html ]

OutputFormatISO8859_1 = 'ISO8859_1'
OutputFormatTeX = 'TeX'
OutputFormatHTML = 'HTML'
OutputFormatXML = 'XML'
OutputFormatUTF8 = 'UTF8'
OutputFormatASCII = 'ASCII'

VerbosityInfo = 0x1
VerbosityShapeBoxes = 0x2
VerbotityPatternBoxes = 0x4
VerbosityPatternRecognition = 0x8
VerbosityLineRecognition = 0x10
VerbosityCreateOutImages = 0x20

ModeUseDatabase = 0x2
ModeDoLayoutAnalysis = 0x4
ModeNoCompareUnrecognizedChars = 0x8
ModeNoDivideOverlappingChars = 0x10
ModeNoContextCorrection = 0x20
ModePackChars = 0x30
ModeExtendDatabase = 0x82
ModeNoRecognition = 0x100

GrayLevelMin = 1
GrayLevelMax = 255
GrayLevelAuto = 0

DustSizeMin = 0
DustSizeMax = sys.maxint
DustSizeAuto = -1

WordSpacingMin = 1
WordSpacingMax = sys.maxint
WordSpacingAuto = 0

CertaintyMin = 0
CertaintyMax = 100
CertaintyDefault = 95

FlagLayoutAnalysisDefault = False
FlagCompareUnrecognizedCharsDefault = True
FlagDivideOverlappingCharsDefault = True
FlagContextCorrectionDefault = True
FlagPackCharsDefault = False

OutputTypeString = 'string'
OutputTypeInt = 'int'
OutputTypeFloat ='float'
OutputTypeDefault = OutputTypeString
OutputTypes = (
		OutputTypeString,
		OutputTypeInt,
		OutputTypeFloat
		)

class GocrOutputTypeError(Exception): pass

def stringToInt(string):
	num = string.replace(',', '.')
	num = num.split('.')
	if len(num) > 1:
		if len(num[-1]) != 3:
			raise GocrOutputTypeError('invalidliteral for int')
		else:
			num = ''.join(num)
	else:
		num = num[0]
	try:
		num = int(num)
	except ValueError:
		raise GocrOutputTypeError('invalidliteral for int')
	return num

def stringToFloat(string):
	num = string.replace(',', '.')
	num = num.split('.')
	if len(num) > 1:
		if len(num[-1]) == 2:
			num = ''.join(num[:-1]) + '.' + num[-1]
		else:
			num = ''.join(num)
	else:
		num = num[0]
	try:
		num = float(num)
	except ValueError:
		raise GocrOutputTypeError('invalid literal for float')
	return num

def _adjustOutput(out, pattern):
	try:
		pattern = re.compile(outputPattern, re.X)
	except re.error:
		return '', 'invalid output pattern'
	m = pattern.match(out)
	if m is None:
		return '', 'no match in output pattern'
	try:
		out = m.group(1)
	except IndexError:
		return '',  'no group (1) in output pattern'
	return out, ''

#TODO: there seems to be no easy way to wrap ModeExtendDatabase. have to digg a bit
# deeper into subprocess to find out if this is possible
def scanImage(
		fileNameGocr=FileNameGocr,
		fileName=None,
		string=None,
		pgmImage=None,
		fileNameOutput=None,
		fileNameError=None,
		#TODO: not implemented. have to testif this is supported gocr.exe
		#fileNameProgress=None,	# can be: fileName, fifoName, fileDescriptor
		directoryDatabase=None,
		outputFormat=None,
		grayLevel=None,
		dustSize=None,
		wordSpacing=None,
		verbosity=None,
		verbosityChars=None,
		chars=None,
		certainty=None,

		flagExtendDatabase=False,
		flagDoRecognition=True,
		flagLayoutAnalysis=FlagLayoutAnalysisDefault,
		flagCompareUnrecognizedChars=FlagCompareUnrecognizedCharsDefault,
		flagDivideOverlappingChars=FlagDivideOverlappingCharsDefault,
		flagContextCorrection=FlagContextCorrectionDefault,
		flagPackChars=FlagPackCharsDefault,

		# custom params
		flagInvertImage=False,
		#TODO: implement
		outputPattern=None,
		#TODO: implement
		outputType=OutputTypeDefault,
		):
	'''
	@param fileNameGocr: (str) file name of the gocr executable
	@param fileName: (str) file name of the image to scan or None to scan string
	@param string: (str) if no file name is specified string to scan
	@param pgmImage: (L{PGMImage}) if no fileName and no string is specified PGMImage to scan
	@param fileNameOutput: (str) file name to dump output to or None. if None output will be returned
	@param fileNameError: (str) file name to dump errors to or None. if None errors will be returned
	@param directoryDatabase: (str) directory to hold learned chars
	@param outputFormat: (OutputFormat*)
	@param grayLevel: (int) 0 - 255, 0 == autodetect
	@param dustSize: (int) 0 - N, -1 == autodetect
	@param wordSpacing: (int) 0 - N, 0 == autodetect
	@param verbosity: (Verbosity*)
	@param verbosityChars: (str) limit verbosity to these chars
	@param chars: (str) only recognize these chars.0-9A-Z notation is ok. use '--' to specify '-'
	@param ceratinty: (int) 0 - 100. only recognize chars with certainity >= this

	@param flagExtendDatabase: (bool) not yet implemented
	@param flagDoRecognition: (bool) scan image. if False no scanning is done
	@param flagLayoutAnalysis: (bool) do layout analysis
	@param flagCompareUnrecognizedChars: (bool)
	@param flagDivideOverlappingChars: (bool)
	@param flagContextCorrection: (bool)
	@param flagPackChars: (bool)

	@param flagInvertImage: (bool) used onlxy if image is passed as pgmImage
	@param outputPatern: (regex)
	@param outputType: (OutputType*)


	@return: (tuple) (str output, str error)
	'''
	cmd = '"%s" ' % fileNameGocr
	if fileName is None:
		if string is None:
			if pgmImage is None:
				raise ValueError('no input image specified')
			if flagInvertImage:
				pgmImage = pgmImage.inverted()
			string = pgmImage.toString()
		fileName = '-'
	cmd += '-i %s ' % fileName
	if fileNameOutput is not None: cmd += '-o "%s" ' % fileNameOutput
	if fileNameError is not None: cmd += '-e "%s" ' % fileNameError
	#TODO: fileNameProgress
	#if fileNameProgress is not None: cmd += '-x "%s" ' % fileNameProgress
	if directoryDatabase is not None:
		# have to make shure directory ends with a slash
		#NOTE: looks like gocr only accepts forward slashes here
		directoryDatabase = os.path.normpath(directoryDatabase).replace('\\', '/')
		if directoryDatabase[-1] not in '/\\':
			directoryDatabase += '7'
		cmd += '-p "%s" ' % directoryDatabase
	if outputFormat is not None: cmd += '-f %s ' % outputFormat
	if grayLevel is not None: cmd += '-l %i ' % grayLevel
	if dustSize is not None: cmd += '-d %i ' % dustSize
	if wordSpacing is not None: cmd += '-s %i ' % wordSpacing
	if verbosity is not None: cmd += '-v %i ' % verbosity
	if verbosityChars is not None: cmd += '-c %s ' % verbosityChars
	if chars is not None: cmd += '-C %s ' % chars
	if certainty is not None: cmd += '-a %i ' % certainty

	mode = 0
	if directoryDatabase is not None and not flagExtendDatabase:
		mode |= ModeUseDatabase
	elif directoryDatabase is not None and flagExtendDatabase:
		mode |= ModeExtendDatabase
	if not flagDoRecognition:
		mode |= ModeNoRecognition
	if flagLayoutAnalysis:
		mode |= ModeDoLayoutAnalysis
	if not flagCompareUnrecognizedChars:
		mode |= ModeNoCompareUnrecognizedChars
	if not flagDivideOverlappingChars:
		mode |= ModeNoDivideOverlappingChars
	if not flagContextCorrection:
		mode |= ModeNoContextCorrection
	if flagPackChars:
		mode |= ModePackChars
	if mode:
		cmd += '-m %i ' % mode

	#TODO: some images break subprocess stdin. i guess ...could be larger imagres
	# breaking something in gocr or the pipe itself goes broke. error is "IOError [Errno 0] Error"
	p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = p.communicate(string)
	if not out:
		return out, err

	# clean output
	out = out.replace('\r', '')

	# do type conversions if desired
	if outputType in (OutputTypeInt, OutputTypeFloat):
		out = out[:-1]	# removes trailing \n

		if outputPattern is not None:
			out, err = _adjustOutput(out, outputPattern)
			if err:
				return '', err

		if outputType == OutputTypeInt:
			try:
				out = stringToInt(out)
			except GocrOutputTypeError:
				return out, 'type conversion error: invalid literal for int'
		elif outputType == OutputTypeFloat:
			try:
				out = stringToFloat(out)
			except GocrOutputTypeError:
				return out, 'type conversion error: invalid literal for float'

	elif outputPattern is not None:
		out, err = _adjustOutput(out, outputPattern)
		if err:
			return '', err

	return out, err

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
	pgm.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.pgm'))
	t0 = time.time()
	stdout, stderr = scanImage(
			string=pgm.toString(),
			chars='0-9,.',
			dustSize=0,
			)
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




