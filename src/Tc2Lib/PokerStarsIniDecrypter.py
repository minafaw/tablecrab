"""recursively encrypts / decrypts all PokerStars ini files in a directory
NOTE: this decrypter is not compatible with other decrypters

usage:

PokerStars.ini [directory]

if directory is omitted current directory is taken
"""


from __future__ import with_statement
import cStringIO, gzip, os
#************************************************************************************
#
#************************************************************************************
LenGzipHeader = 10
LookupTable= (
		0x63,0x27,0x26,0x26,0x4F,0x35,0x1D,0x07,0x19,0x45,0x59,0x21,0x37,
		0x3F,0x00,0x1B,0x1B,0x1A,0x11,0x1B,0x03,0x04,0x4C,0x65,0x37, 0x00, 
		0x1D,0x1D,0x48,0x20,0x0B,0x3D,0x45,0x7B,0x55,0x36,0x16, 0x00,0x19, 
		0x00,0x59,0x06,0x1C,0x02,0x20
		)

def decryptString(string):
	# XOR string acc to LookupTable
	data = ''
	index = 0
	for char in string:
		if not char: break
		data += chr( ord(char) ^ LookupTable[index] )
		index += 1
		if index >= len(LookupTable): index = 0
	
	# stars checks timestamp / os in header. we save original header as first comment
	# in the decrypted ini file in the following format:
	# <#31,139,8,0,0,0,0,0,0,11\n>
	# that is comma separated ordinals of the bytes surrounded by hash and newline char
	# on encryption we patch the gzip we generate with these bytes again. 
	# gzip header acc to RFC1952: [http://www.gzip.org/zlib/rfc-gzip.html]
	#+---+---+---+---+---+---+---+---+---+---+
	#|ID1|ID2|CM |FLG|     MTIME     |XFL|OS |
	#+---+---+---+---+---+---+---+---+---+---+
	header = [str(ord(i)) for i in data[:LenGzipHeader]]
	header = '#%s\n' % (','.join(header))
		
	# gunzip data
	fp = gzip.GzipFile(fileobj=cStringIO.StringIO(data), mode='rb')
	try:
		data = header + fp.read()
	finally: fp.close()
	return data


def encryptString(string):

	# remove our header data from string
	header, string = string.split('\n', 1)
	header = header.strip().replace('#', '')
	header = ''.join( [chr(int(i)) for i in header.split(',')] )
			
	# gzip data
	p = cStringIO.StringIO()
	fp = gzip.GzipFile(fileobj=p, mode='wb', compresslevel=9)
	try:
		fp.write(string)
	finally: fp.close()
	p.seek(0)
	string = p.getvalue()

	# patch the gzip with our header
	string = header + string[LenGzipHeader:]
	
	# XOR string acc to LookupTable
	data = ''
	index = 0
	for char in string:
		if not char: break
		data += chr( ord(char) ^ LookupTable[index] )
		index += 1
		if index >= len(LookupTable): index = 0

	return data


def main(filename):
	"""decrypts / encrypts a PokerStars ini file"""
	with open(filename, 'rb') as fp:
		data = fp.read()
	try:
		data = decryptString(data)
		print 'decrypted: %s' % filename
	except IOError:
		data = encryptString(data)
		print 'encrypted: %s' % filename
	with open(filename, 'wb') as fp:
		fp.write(data)

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		directory = sys.argv[1]
	else:
		directory = os.path.dirname(os.path.abspath(__file__))
	for root, dirs, files in os.walk(directory):
		for name in files:
			if os.path.splitext(name)[1].lower() == '.ini':
				filename = os.path.join(root, name)
				main(filename)

