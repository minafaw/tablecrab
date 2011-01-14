
from PyQt4 import QtCore, QtNetwork, QtWebKit


#************************************************************************************
# customized network access manager so we can serve raw data from anywhere
#
#************************************************************************************
class RawNetworkReply(QtNetwork.QNetworkReply):
	# this thingy will hand out everything you throw at it via setData()
	def __init__(self, parent=None):
		QtNetwork.QNetworkReply.__init__(self, parent)
		self._data = None
		self._dataPos = 0
		self.open(self.ReadOnly | self.Unbuffered)
		self.timer = QtCore.QTimer(self)
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.emitSignals)
		self.timer.setInterval(0)
		self.timer.start()
	def emitSignals(self):
		self.readyRead.emit()
		self.finished.emit()
	def abort(self):	pass
	def bytesAvailable(self):
		if self._data is not None:
			return len(self._data) - self._dataPos
		return 0
	def isSequential(self): return True
	def readData(self, maxSize):
		#NOTE: emitting finished() crashes in PyQt4.8.1. used to work in PyQt4-7.7 no idea why
		# maybe i am getting wrong what it is supposed to do?
		#self.finished.emit()
		#NOTE: we can not return -1 here. no idea how this is handled in PyQt
		stop = self._dataPos + maxSize
		if stop >= len(self._data):
			stop = len(self._data)
		data =  self._data[self._dataPos:stop]
		self._dataPos = stop
		arr = QtCore.QByteArray()
		arr += data
		return arr.data()
	def setData(self, data, mimeType):
		self.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant(mimeType))
		self._data = data
	def hasData(self):
		return self._data is not None

# usage:
# 1) connect to signal getData()
# 2) this thing will throw a networkReply at your slot
# 3) dump data to the reply via networkReply.setData(data, mimeType)
#     not setting data or setting data to None will serve whatever QWebKit serves as default
#NOTE: QNetworkAccessManager is quite a bitch. slightest err will segfault
class RawNetworkAccessManager(QtNetwork.QNetworkAccessManager):

	getData =  QtCore.pyqtSignal(RawNetworkReply)

	def __init__(self, oldNetworkManager, parent=None):
		QtNetwork.QNetworkAccessManager.__init__(self, parent)
		self._oldNetworkManager = oldNetworkManager
		self.setCache(self._oldNetworkManager.cache())
		self.setCookieJar(self._oldNetworkManager.cookieJar())
		self.setProxy(self._oldNetworkManager.proxy())
		self.setProxyFactory(self._oldNetworkManager.proxyFactory())

	def createRequest(self, operation, request, data):
		#NOTE: from previous versions of Qt i found we can not keep the url bcause Qt nulls it on return
		url = QtCore.QUrl(request.url())
		if operation == self.GetOperation:
			networkReply = RawNetworkReply(parent=self)
			networkReply.setUrl(url)
			self.getData.emit(networkReply)
			if networkReply.hasData():
				return networkReply
		return QtNetwork.QNetworkAccessManager.createRequest(self, operation, request, data)


class RawBrowser(QtWebKit.QWebView):

	def __init__(self, parent=None):
		QtWebKit.QWebView.__init__(self, parent)

		page = self.page()
		oldNetworkManager = page.networkAccessManager()
		self._networkAccessManager = RawNetworkAccessManager(oldNetworkManager, parent=self)
		page.setNetworkAccessManager(self._networkAccessManager)

	def networkAccessManager(self):
		return self._networkAccessManager





