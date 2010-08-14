



import os, Image

DIR_SELF = os.path.dirname(os.path.abspath(__file__))

#*******************************************************************

#NOTE: for some reason "cardrank" and "cardsuit" are not present in size 0 and 1
CARD_SIZES = (
		{	# 0
			'cardbase': (84, 118),
			'cardface': (84, 118),
		},
		{	# 1
			'cardbase': (36, 51),
			'cardface': (36, 51),
		},
		{	# 2
			'cardbase': (42, 59),
			'cardface': (42, 59),
			'cardrank': (156, 13),
			'cardsuit': (72, 12),
		},
		{	# 3
			'cardbase': (50, 70),
			'cardface': (50, 70),
			'cardrank': (182, 15),
			'cardsuit': (84, 15),
		},
		{	# 4
			'cardbase': (60, 84),
			'cardface': (60, 84),
			'cardrank': (234, 18),
			'cardsuit': (108, 19),
		},
		{	# 5
			'cardbase': (70, 98),
			'cardface': (70, 98),
			'cardrank': (260, 21),
			'cardsuit': (120, 21),
		},
		{	# 6: our default from template
			'cardbase': (84, 118),
			'cardface': (84, 118),
			'cardrank': (325, 26),
			'cardsuit': (150, 26),
		},
	)


def main():
	print 'expanding deck/default'
	
	dirTemplate = os.path.join(DIR_SELF, '6')
	for name in os.listdir(dirTemplate):
		src = os.path.join(dirTemplate, name)
		if not os.path.isfile(src): continue
		if os.path.splitext(name)[1].lower() not in ('.bmp', '.jpg'): continue
		
		# expand cards
		img = Image.open(src)
		for n, size in enumerate(CARD_SIZES[:-1]):
			dirDst = os.path.join(DIR_SELF, str(n))
			if not os.path.isdir(dirDst): os.mkdir(dirDst)
			
			dst = os.path.join(dirDst, name)
			imgName, _ = name.split('.', 1)
			if imgName not in size: continue
			
			imgNew = img.resize(size[imgName])
			imgNew.save(dst)
		
	print 'done'
	
	pass
	
	


if __name__ == '__main__': main()

