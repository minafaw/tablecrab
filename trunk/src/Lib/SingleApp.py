"""making resonably shure only one appliaction is running at a time""" 
 

import socket
import thread
#**********************************************************************
#
#**********************************************************************
class ErrorCanNotConnect(Exception):
	"""exception raised in cace SignleApp can not connect to the socket or something unexpected happens in the communication"""
	
class ErrorOtherAppIsRunning(Exception):
	"""exception raised when SingleApp detects another application is already running"""
	

class SingleApp(object):
	"""Class doing its best to enshure only one instance of an application
	is running at the same time
	
	@note: the class uses a socket to exchange data in between applications. firewalls
	(...) may not like this. 
	@note: a carefuly chosen magic string to exchange may help to reduce the chance
	of accidential collisions with other applications
	@note: race conditions? yes
	"""
	
	def __init__(self, host=None, port=None, magicToSend=None, magicToRespond=None, userData=None):
		"""
		@param host: host to establish the connection to
		@param port: port to use for the connection
		@param magicToSend: magic string a client should send to the server
		@param magicToRespond: magic string the server should send in response
		@param userData: any data you want to associate to the SignleApp object
		"""
				
		if host is None or port is None or magicToSend is None or magicToRespond is None:
			raise ValueError('All keyword arguments except userData are mandatory. This is just for better looks')
		self.host = host
		self.port = port
		self.magicToSend = magicToSend
		self.magicToRespond = magicToRespond
		self.isServerRunning = False
		self.socket = None
		self.userData = userData
			
	def _runServer(self):
		# start server and listen to incoming connections
		while True:
			self.socket.listen(1)
			conn, addr = self.socket.accept()
			# NOTE: my best guess here is that we can not loop here to make shure we
			# get some data. maybe the other end of the pipe plays dead
			data = conn.recv(len(self.magicToSend))
			if data == self.magicToSend:
				self.onOtherAppIsStarting()
				conn.send(self.magicToRespond)
			conn.close()
		self.socket.close()
		self.socket = None
		self.isServerRunning = False
	
		
	def start(self):
		"""starts SingleApp
		
		@raise ErrorCanNotConnect:
		@raise ErrorOtherAppIsRunning:
		"""
		# try to bind socket as server
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self.socket.bind((self.host, self.port))
		except socket.error, details:
			# assume address is already in use, try to connect to it
			try:
				self.socket.connect((self.host, self.port))
			except socket.error, details:
				# ups, neither way works. we give up here
				raise ErrorCanNotConnect(details)
			try:
				# try to find out who is serving
				self.socket.settimeout(0.5)	
				self.socket.sendall(self.magicToSend)
				# NOTE: my best guess here is that we can not loop here to make shure we
				# get some data. mybe the other end of the pipe plays dead 
				data = self.socket.recv(len(self.magicToRespond))
				if data == self.magicToRespond:
					raise ErrorOtherAppIsRunning()
			except socket.timeout:
				raise ErrorCanNotConnect(details)
			finally:
				self.socket.close()
				self.socket = None
		else:
			self.isServerRunning = True
			thread.start_new_thread(self._runServer, ())
						
	def onOtherAppIsStarting(self):
		"""called when another application using the same magic string is conncting to our server"""
		print 'another app of the same kind is connecting to us'
	
	
		
	
 
