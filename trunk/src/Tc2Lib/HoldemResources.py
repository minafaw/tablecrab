
import urllib2, re
#************************************************************************************
#
#************************************************************************************
class FetchError(Exception): pass

class NashFetcher(object):

	PatTable = re.compile('<table\s .*? </table>', re.X|re.I)

	def __init__(self):
		pass

	def fetch(self, url, proxy=None):
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		if proxy is not None:
			proxy_support = urllib2.ProxyHandler({"http": "http://" + proxy})
			opener.add_handler(proxy_support)
		try:
			fp = opener.open(url)
			try:
				data = fp.read()
			finally:
				fp.close()
		except Exception, d:
			raise FetchError(d)
		return  data

	def getData(self,
			bigBlind=None,
			smallBlind=None,
			ante=None,
			payouts=None,
			stacks=None,
			proxy=None,
			):
		ante = (0 if ante is None else ante)	# required

		url = 'http://www.holdemresources.net/hr/sngs/icmcalculator.html?action=calculate'
		url += '&bb=%s' % bigBlind
		url += '&sb=%s' % smallBlind
		url += '&ante=%s' % ante
		url += '&structure=%s' % ('%2C'.join(['%.2f' % i for i in payouts]))
		for i, stack in enumerate(stacks):
			url += '&s%s=%s' % (i+1, stack)
		data = self.fetch(url, proxy=proxy)

		result = self.PatTable.findall(data)
		if len(result) > 1:
			return (url, data)
		raise FetchError('could not retrieve data: %s' % url)


class ParseError(Exception): pass

class NashFormatter(object):
	StyleSheet = '''body{}
td{text-align: left;vertical-align: text-top;}
.table{}
.header{}

.cellPlayerName{font-weight: bold;}
.cellPlayerStack{font-weight: bold;}

.cellActionMargin{}

.cellActionPush{}
.cellActionPushPercentage{}
.cellActionPushRange{}

.cellActionCall{white-space: nowrap;}
.cellActionCallPercentage{}
.cellActionCallRange{}
'''
	PatTable = re.compile('<table\s?.*?> (.*?) </table>', re.X|re.I|re.S)
	PatTr = re.compile('<tr\s?.*?> (.*?) </tr>', re.X|re.I|re.S)
	PatTd = re.compile('<td\s?.*?> (.*?) </td>', re.X|re.I|re.S)

	def __init__(self):
		self.seats = None

	def parse(self, p):
		tables = self.PatTable.findall(p)
		if not tables:
			raise ParseError()
		seats = []

		# gather sall seats from top table
		trs = self.PatTr.findall(tables[-2])
		for tr in trs:
			tds = self.PatTd.findall(tr)
			if not tds: continue
			seats.append({
					'seat': tds[0],
					'stack': tds[1][:-2],
					'push': (),		# (percentage, range)
					'call': [],		# list (seat(s)ToCall, percentage, range)
					})

		# gather all actions from bottom table
		trs = self.PatTr.findall(tables[-1])
		actions = []
		for tr in trs:
			tr = tr.replace('<td />', '<td></td>')	# makes parsing easier on us
			tds = self.PatTd.findall(tr)
			if not tds: continue
			tds.extend([i.strip() for i in tds.pop(-1).split(',')])	# add call
			actions.append(tds)

		# bring actions in normal form
		# CO
		# ---  BU
		# ---  --- SB
		# to..
		# [CO, BU, SB]
		for iAction, action in enumerate(actions):
			if iAction == 0: continue
			for iCol, col in enumerate(action[:3]):
				if col: break
				action[iCol] = actions[iAction-1][iCol]
		for iAction, action in enumerate(actions):
			actions[iAction] = [ [i for i in action[:3] if i] ] + action[3:]

		# dump actons to seats
		def sortf(x, y):
			return cmp(len(x[0]), len(y[0]))
		for seat in seats:
			for action in actions:
				if action[0][-1] == seat['seat']:
					if len(action[0]) == 1:
						seat['push'] = (action[-2], action[-1])
					else:
						seat['call'].append( (action[0][:-1], action[-2], action[-1]) )
			seat['call'].sort(cmp=sortf)

		self.seats = seats

	def toString(self, seatSortf=None):
		if self.seats is None: raise ValueError('nothing to format')
		result = ''
		seats = self.seats  if  seatSortf is None else seatSortf(self.seats)
		for seat in seats:
			#print seat
			result += '%s %s\n' % (seat['seat'], seat['stack'])
			if seat['push']:
				result += '\x20\x20\x20\x20push: %s / %s\n' % (seat['push'][0], seat['push'][1])
			if seat['call']:
				for others, perc, rng in seat['call']:
					result += '\x20\x20\x20\x20call: %s %s / %s\n' % ('-'.join(others), perc, rng)
		return result

	def toHtml(self, blinds=None, seatSortf=None, styleSheet=None):
		if self.seats is None: raise ValueError('nothing to format')

		p = '<html><head>'
		p += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		p += '<style type="text/css"><!-- %s --></style>' % (self.StyleSheet if styleSheet is None else styleSheet)
		p += '</head><body>'
		p += '<table class="table" border="1" cellspacing="0" cellpadding="0">'
		if blinds is not None:
			p += '<tr><th class="header" colspan="99">sb=%s bb=%s ante=%s</th></tr>' % (blinds[0], blinds[1], blinds[2])

		seats = self.seats  if  seatSortf is None else seatSortf(self.seats)
		for seat in seats:
			p += '<tr>'
			p += '<td class="cellPlayerName">%s</td>' % seat['seat']
			p += '<td class="cellPlayerStack" colspan="99">%s</td>' % seat['stack']
			p += '</tr>'

			if seat['push']:
				nRows = len(seat['call']) +1

				p += '<tr>'
				p += '<td class="cellActionMargin" rowspan="%s">&nbsp;</td>' % nRows
				p += '<td class="cellActionPush">push:</td>'
				p += '<td class="cellActionPushPercentage">%s</td>' % seat['push'][0]
				p += '<td class="cellActionPushRange">%s</td>' % seat['push'][1]
				p += '</tr>'

			if seat['call']:
				nRows = None
				if not seat['push']:
					nRows = len(seat['call'])

				for others, perc, rng in seat['call']:
					p += '<tr>'
					if nRows is not None:
						p += '<td class="cellActionMargin" rowspan="%s">&nbsp;</td>' % nRows
						nRows = None
					#p += '<td class="cellActionCallMargin">&nbsp;</td>'
					p += '<td class="cellActionCall">call: %s</td>' % '-'.join(others)
					p += '<td class="cellActionCallPercentage">%s</td>' % perc
					p += '<td class="cellActionCallRange">%s</td>' % rng
					p += '</tr>'

		p += '</table>'
		p += '</body></html>'
		return p

