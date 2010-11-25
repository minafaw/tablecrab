
from PyQt4 import QtCore, QtNetwork
import re
#************************************************************************************
#
#************************************************************************************
class FetchError(Exception): pass

class ParseError(Exception): pass

#************************************************************************************
#
#************************************************************************************
class NashFetcher(QtNetwork.QNetworkAccessManager):

	requestFailed = QtCore.pyqtSignal(QtCore.QUrl, QtCore.QString)
	requestCompleted = QtCore.pyqtSignal(QtCore.QUrl, QtCore.QString)

	def __init__(self, parent=None):
		QtNetwork.QNetworkAccessManager.__init__(self, parent)
		self._reply = None
		self._data = None
		self._timer = QtCore.QTimer(self)
		self._timer.setSingleShot(True)
		self._timer.timeout.connect(self.onTimeout)
		self.finished.connect(self.onReplyFinished)
		self.defaultProxy = self.proxy()

	def abortRequest(self):
		if self._reply is not None:
			self._reply.abort()
			self._reply = None
		self._timer.stop()

	def createRequestUrl(self,
			bigBlind=None,
			smallBlind=None,
			ante=None,
			payouts=None,
			stacks=None,
			):
		ante = (0 if ante is None else ante)	# required
		url = 'http://www.holdemresources.net/hr/sngs/icmcalculator.html?action=calculate'
		url += '&bb=%s' % bigBlind
		url += '&sb=%s' % smallBlind
		url += '&ante=%s' % ante
		url += '&structure=%s' % ('%2C'.join(['%.2f' % i for i in payouts]))
		for i, stack in enumerate(stacks):
			url += '&s%s=%s' % (i+1, stack)
		#NOTE: have to use QUrl.fomEncoded() here
		return QtCore.QUrl.fromEncoded(url)

	def requestHandData(self, url, timeout=-1, proxyHostName=None, proxyPort=80, proxyUserName=None, proxyPassword=None):
		# check what proxy to use
		if not proxyHostName and not self.proxy().hostName():
			# no proxy set
			pass
		elif not proxyHostName and self.proxy().hostName():
			# reset proxy to default
			self.setProxy(self.defaultProxy)
		elif proxyHostName == self.proxy().hostName():
			# check if we have to create another proxy
			myProxy = self.proxy()
			if proxyPort != myProxy.port() or proxyUserName !=  myProxy.user() or proxyPassword != myProxy.password():
				proxy = QtNetwork.QNetworkProxy()
				proxy.setType(proxy.HttpProxy)
				proxy.setHostName(proxyHostName)
				proxy.setPort(proxyPort)
				if proxyUserName: proxy.setUser(proxyUserName)
				if proxyPassword: proxy.setPassword(proxyPassword)
				self.setProxy(proxy)
		elif proxyHostName != self.proxy().hostName():
			# create new proxy
			proxy = QtNetwork.QNetworkProxy()
			proxy.setType(proxy.HttpProxy)
			proxy.setHostName(proxyHostName)
			proxy.setPort(proxyPort)
			if proxyUserName: proxy.setUser(proxyUserName)
			if proxyPassword: proxy.setPassword(proxyPassword)
			self.setProxy(proxy)
		else:
			raise valueError('we should not have ended here!')

		if self._reply is not None:
			self._reply.abort()
		self._timer.stop()
		request = QtNetwork.QNetworkRequest(url)
		self._reply = self.get(request)
		if timeout >= 0:
			self._timer.start(timeout)

	def onTimeout(self):
		if self._reply is not None:
			url = QtCore.QUrl(self._reply.url())
			self._reply.abort()
			self.requestFailed.emit(url, 'timed out')

	def onReplyFinished(self, reply):
		arr = None
		url = QtCore.QUrl(reply.url())
		err = reply.error()
		if err == reply.NoError:
			arr = reply.readAll()
		elif err == reply.OperationCanceledError:
			pass
		else:
			self.requestFailed.emit(url, reply.errorString())
		self._reply = None
		reply.deleteLater()
		if arr is not None:
			p = QtCore.QString.fromUtf8(arr.data())
			self.requestCompleted.emit(url, p)


def test():
	import time
	from PyQt4 import QtGui

	class W(QtGui.QMainWindow):
		def __init__(self):
			QtGui.QMainWindow.__init__(self)
			self.show()
			self.f = NashFetcher()
			self.f.requestCompleted.connect(self.onRequestCompleted)
			self.f.requestFailed.connect(self.onRequestFailed)
			url = self.f.createRequestUrl(
					bigBlind=200,
					smallBlind=100,
					ante=25,
					payouts=(0.5, 0.3, 0.2),
					stacks=(1000, 1000, 2000)
					)
			self.f.requestHandData(url, timeout=1000)
		def onRequestCompleted(self, url, data):
			print '>>request completed'
			print repr(data)
		def onRequestFailed(self, url, msg):
			print '>>request failed'
			print msg
	app = QtGui.QApplication([])
	w = W()
	app.exec_()

#test()

#************************************************************************************
#
#************************************************************************************
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

	def parse(self, qString):
		p = unicode(qString.toUtf8(), 'utf-8')
		tables = self.PatTable.findall(p)
		if not tables:
			raise ParseError(p)
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

		# bring actions to normal form
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
			result += '%s %s\n' % (seat['seat'], seat['stack'])
			if seat['push']:
				result += '\x20\x20\x20\x20push: %s / %s\n' % (seat['push'][0], seat['push'][1])
			if seat['call']:
				for others, perc, rng in seat['call']:
					result += '\x20\x20\x20\x20call: %s %s / %s\n' % ('-'.join(others), perc, rng)
		return result

	def toHtml(self, blinds=None, seatSortf=None, styleSheet=None, url=None):
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

		if url is not None:
			p += '<br><b>HoldemResources url:</b><br>%s<br><br>' % url.toString()
		p += '</body></html>'
		return p

