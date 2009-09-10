'''client interface
'''

from __future__ import absolute_import
if __name__ == '__main__':	# see --> http://bugs.python.org/issue1510172 . works only current dir and below
	import os; __path__ = [os.path.dirname(__file__)]

import sys, traceback

from .Platform import Application
from . import Config
from . import WindowHandlers

#******************************************************************************************

# test application for all of the stuff above
class Cli(object):
	Type = 'Cli'
	
	def __init__(self, config=None):
		sys.excepthook = self._excepthook
		
		self.config = Config.Config() if config is None else config
		self.application = Application.Application(cb=self.onApplication)
		self.application.mouseManager.setCB(self.onMouseManager)
		self.application.keyboardManager.setCB(self.onKeyboardManager)
		self.application.windowManager.setCB(self.onWindowManager)
		self.log = lambda obj, msg: Config.logger.debug('%s:%s' % (obj.Type, msg))
		self.logException = lambda obj, msg: Config.logger.critical('%s:%s' % (obj.Type, msg))
				
		self.windowHandlers = {}		# hWindow --> WindowHandler*
		
		self._keyboardIsPaused = False
		self._keyboardReportIsPaused = True
		self._windowReportIsPaused = True
			
	def _excepthook(self, Type, value, tb):
		p = [Config.__application_name__, 'Version: ' + Config.__version__]
		p += traceback.format_exception(type, value, tb)
		self.logException(self, '\n'.join(p) )
		self.application.stop()
		raise Type(value)
	
	def keyboardIsPaused(self): return self._keyboardIsPaused
	def keyboardSetPaused(self, flag):
		self._keyboardIsPaused = flag
		return flag
	
	def keyboardReportIsPaused(self): return self._keyboardReportIsPaused
	def keyboardReportSetPaused(self, flag):
		self._keyboardReportIsPaused = flag
		return flag
	
	def windowReportIsPaused(self): return self._windowReportIsPaused
	def windowReportSetPaused(self, flag):
		self._windowReportIsPaused = flag
		return flag
	
	def start(self):
		self.application.start()
	def stop(self):
		self.application.stop()
	
	def onApplication(self, application, evt, arg):
		if evt in (application.EvtStart, application.EvtStop):
			if arg:
				self.log(application, '%s arg="%s"' % (evt, arg) )
			else:
				self.log(application, evt)
			return False
		return False
	
	def onMouseManager(self, mouseManager, evt, arg):
		if evt in (mouseManager.EvtStart, mouseManager.EvtStop):
			if arg:
				self.log(mouseManager, '%s arg="%s"' % (evt, arg) )
			else:
				self.log(mouseManager, evt)
			return False
		return False
	
	def onKeyboardManager(self, keyboardManager, evt, arg):
		if evt in (keyboardManager.EvtStart, keyboardManager.EvtStop):
			if arg:
				keyboardLayout = arg
				self.log(keyboardManager, '%s keyboard="%s"' % (evt, keyboardLayout) )
			else:
				self.log(keyboardManager, evt)
			return False
		
		key = arg
			
		# process cli hotkeys
				
		if key == self.config['cli']['key-report-keyboard']:	
			if evt == keyboardManager.EvtKeyReleased:
				flag = self.keyboardReportSetPaused(not self.keyboardReportIsPaused())
				self.log(self, 'keyboardReport="%s"' % ('of' if flag else 'on') )
		if evt == keyboardManager.EvtKeyPressed:	
			if not self.keyboardReportIsPaused():
				self.log(self, '%s key="%s"' % (evt, key.value) )
		
		elif key == self.config['cli']['key-pause-keyboard']:
			if evt == keyboardManager.EvtKeyReleased:
				flag = self.keyboardSetPaused(not self.keyboardIsPaused())
				self.log(self, 'keyboard="%s"' % ('of' if flag else 'on') )
			return True
		if self.keyboardIsPaused():
			return False
		
		elif key == self.config['cli']['key-report-windows']:
			if evt == keyboardManager.EvtKeyReleased:
				flag = self.windowReportSetPaused(not self.windowReportIsPaused())
				self.log(self, 'windowReport="%s"' % ('of' if flag else 'on') )
			return True

		elif key == self.config['cli']['key-info-window']:
			if evt == keyboardManager.EvtKeyReleased:
				hWindow = self.application.windowManager.windowForeground()
				if hWindow:
					self.windowInfo(hWindow, header='window info')
				return True
		
		elif key == self.config['cli']['key-info-window-under-mouse']:
			if evt == keyboardManager.EvtKeyReleased:
				self.windowInfoUnderMouse()
				return True
		
		# pass key to window handler
		hWindow = self.application.windowManager.windowForeground()
		handler = self.windowHandlers.get(hWindow, None)
		if handler is None:
			return False
		if evt == keyboardManager.EvtKeyPressed:
			return handler.handleKeyPressed(self, key)
		elif evt == keyboardManager.EvtKeyReleased:
			return handler.handleKeyReleased(self, key)
		return False
	
	def onWindowManager(self, windowManager, evt, arg):
		if evt in (windowManager.EvtStart, windowManager.EvtStop):
			if arg:
				self.log(windowManager, '%s arg="%s"' % (evt, arg) )
			else:
				self.log(windowManager, evt)
			return False
	
		hWindow = arg
		if evt == windowManager.EvtWindowCreated:
			#TODO: root window, skip it so far. win32 has 0 as hwnd and some method calls do not work like e.g. windowText() 
			if not hWindow:
				return False
			# try to find a handler for the window
			for typeKlass, klassHandler in WindowHandlers.WindowHandlerRegistry.items():
				if typeKlass is WindowHandlers.WindowHandlerType: 	# skip default window handler
					continue
				handler = klassHandler.handleWindowCreated(self, hWindow)
				if handler is not None:
					self.windowHandlers[hWindow] = handler
					if not self.windowReportIsPaused():
						self.log(self, '%s className="%s" title="%s"' % (
												evt, 
												windowManager.windowGetClassName(hWindow), 
												windowManager.windowGetText(hWindow)) 
												)
					break
			# no handler found, check if we have a default handler for the window
			else:
				klassHandler = WindowHandlers.WindowHandlerRegistry.get(WindowHandlers.WindowHandlerType, None)
				if klassHandler is not None:
					handler = klassHandler.handleWindowCreated(self, hWindow)
					if handler is not None:
						self.windowHandlers[hWindow] = handler
						if not self.windowReportIsPaused():
							self.log(self, '%s className="%s" title="%s"' % (
												evt, 
												windowManager.windowGetClassName(hWindow), 
												windowManager.windowGetText(hWindow)) 
												)
		
		elif evt == windowManager.EvtWindowDestroyed:
			handler = self.windowHandlers.get(hWindow, None)
			if handler is not None:
				del self.windowHandlers[hWindow]
				if not self.windowReportIsPaused():
					self.log(self, '%s className="" title=""' % (evt, ) )
				result = handler.handleWindowDestroyed(self, hWindow)
		elif evt == windowManager.EvtWindowGainForeground:
			handler = self.windowHandlers.get(hWindow, None)
			if handler is not None:
				result = handler.handleWindowGainForeground(self, hWindow)
				if not self.windowReportIsPaused():
					self.log(self, '%s className="%s" title="%s"' % (
												evt, 
												windowManager.windowGetClassName(hWindow), 
												windowManager.windowGetText(hWindow)) 
												)
		elif evt == windowManager.EvtWindowLooseForeground:
			handler = self.windowHandlers.get(hWindow, None)
			if handler is not None:
				result = handler.handleWindowLooseForeground(self, hWindow)
				if not self.windowReportIsPaused():
					self.log(self, '%s className="%s" title="%s"' % (
												evt, 
												windowManager.windowGetClassName(hWindow), 
												windowManager.windowGetText(hWindow)) 
												)
		
	def windowInfo(self, hwnd, header=None, nIndent=0):
		"""prints out window info 
		@param hwnd: (hwnd) hwnd of the window
		@param header: (str) if desired a header text
		@param nIndent: (int) indent the report? how many times?
		"""
		indent = '\x20' * 4 * nIndent
		ptMouseAbs = self.application.mouseManager.mouseGetPos()
		ptMouseRel = self.application.windowManager.windowScreenPointToClientPoint(hwnd, ptMouseAbs)
		if header is not None:
			self.log(self, '%s# ##############################' % indent)
			self.log(self, '%s# %s' % (indent, header))
			self.log(self, '%s# ##############################' % indent)
		self.log(self, '%shwnd: %s' % (indent, hwnd))
		self.log(self, "%stitle: '%s'" % (indent, self.application.windowManager.windowGetText(hwnd) ) )
		self.log(self, "%sclass: '%s'" % (indent, self.application.windowManager.windowGetClassName(hwnd) ) )
		self.log(self, '%srect: %s' % (indent, self.application.windowManager.windowGetRect(hwnd) ) )
		self.log(self, '%sclientSize: %s' % (indent, self.application.windowManager.windowGetClientRect(hwnd)[2:] ) )
		self.log(self, '%sisVisible: %s' % (indent, self.application.windowManager.windowIsVisible(hwnd) ) )
		self.log(self, '%smousePos(abs): %s' % (indent, ptMouseAbs) )
		self.log(self, '%smousePos(rel): %s' % (indent, ptMouseRel) )
		
	def windowInfoUnderMouse(self):
		"""prints out a report (size, mousePos, child windows (...)) of the window under the mouse pointer. see L{infoWindow}
		"""
		nIndent = 0
		pt = self.application.mouseManager.mouseGetPos()
		hwndCurrent = self.application.windowManager.windowFromPoint(pt)
		if hwndCurrent:
			self.windowInfo(hwndCurrent, header='WINDOW UNDER MOUSE', nIndent=nIndent)
								
			# print info of all parent windows (not including desktop)
			myHwndCurrent = hwndCurrent
			while True:
				nIndent += 1
				hwndParent = self.application.windowManager.windowGetParent(myHwndCurrent)
				if not hwndParent: break
				self.windowInfo(hwndParent, header='WINDOW PARENT(%s)' % nIndent, nIndent=nIndent)
				myHwndCurrent = hwndParent
		else:
			self.log(self, None)
			
		self.log(self, '')
		self.log(self, 'EXTENDED INFORMATION')
		self.log(self, '')
		for nIndent, hwnd in self.application.windowManager.windowWalkChildren(hwndCurrent, report=True):
			header = 'WINDOW' if hwnd == hwndCurrent else 'CHILD WINDOW(%s)' % nIndent
			self.windowInfo(hwnd, header=header, nIndent=nIndent)	


#********************************************************************************************
if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		filePathCf = sys.argv[1]
	else:
		filePathCfg = Config.FilePathDefaultCfg
	
	config = Config.Config(filePathCfg=filePathCfg)
	cli = Cli(config=config)
	cli.start() 
