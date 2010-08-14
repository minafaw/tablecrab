"""recursively converts all PokerStars *.a.bmp files to grayscale in the current directory and below

usage: python AlphaBitmapsToGrayscale.py [directory]

@requires: python imaging library
"""


import os, Image, tempfile, shutil

#****************************************************************************************************
DIR_SELF = os.path.dirname(os.path.abspath(__file__))

def main(directory=DIR_SELF):
	for root, dirs, files in os.walk(directory):
		for name in files:
			if not '.a.' in name: continue
			if os.path.splitext(name)[1].lower() != '.bmp': continue
				
			# NOTE: for some reason PIL opens indexed bmps always in grayscale mode. nice for us
			# ..but, for some reason we can not write the grayscale image to its source file. we have 
			# to use an intermediate temp file, otherwise we get obscure errors
			src = os.path.join(root, name)
			img = Image.open(src)
			if img.mode == 'L':
				fp = tempfile.NamedTemporaryFile(dir=directory, delete=True)
				try:
					img.save(fp, 'BMP')
					shutil.copyfile(fp.name, src)
				finally: fp.close()
						

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv[1])
	else:
		print __doc__

			
		
	


