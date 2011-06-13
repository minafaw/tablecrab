
#TODO: how to give feedback when the user types in an invalid hand pattern?

from PyQt4 import QtCore, QtGui
import PokerTools
#************************************************************************************
#
#************************************************************************************
class HandtypeButton(QtGui.QPushButton):
		
	def __init__(self, handType, parent=None):
		QtGui.QPushButton.__init__(self, handType, parent)
		self.fixedSize = None
		self.handType = handType
		type = None
		if PokerTools.handTypeIsPair(handType):
			self.setObjectName('pair')
		elif PokerTools.handTypeIsSuited(handType):
			self.setObjectName('suited')
		else:
			self.setObjectName('offsuit')
		self.setCheckable(True)
		self.setFocusPolicy(QtCore.Qt.NoFocus)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		sizePolicy.setHeightForWidth(True)
		self.setSizePolicy(sizePolicy)
			
	def sizeHint(self):
		return self.fixedSize
	
	def heightForWidth(self, width):
		return width


class HandTypesHoldemWidget(QtGui.QFrame):
	"""
	@note: call L{handleFontSizeChanged} if the font for the widget changes
	"""
	
	
	StyleSheet = '''
			QPushButton{
						border: 1px solid black;
						border-radius: 2px;	
						}
			#pair{background-color: #E3EBEE;}
			#pair:checked{background-color: #8DC6E2;}
			#suited{background-color: #FAF8E0;}
			#suited:checked{background-color:#C6B92C;}
			#offsuit{background-color: #FBDFDE;}
			#offsuit:checked{background-color: #E06D64;	}
			'''
	
	def __init__(self, parent=None, styleSheet=None):
		QtGui.QFrame.__init__(self, parent)
				
		self.lock = False
		
		self.grid = QtGui.QGridLayout(self)
		self.grid.setSpacing(0)
		self.grid.setContentsMargins(0, 0, 0, 0)
		
		font = QtGui.qApp.font()
		m = QtGui.QFontMetrics(font)
		w = m.width('AKs') +8
		h = w
		fixedSize = QtCore.QSize(w, h)
		
		self.handTypeButtons ={}	# handType --> button
		for y, row in enumerate(PokerTools.genHandTypeTable()):
			for x, handType in enumerate(row):
				btn = HandtypeButton(handType, parent=self)
				btn.setStyleSheet(self.StyleSheet if styleSheet is None else styleSheet)
				self.handTypeButtons[handType] = btn
				btn.toggled.connect(self.onRangeButtonToggled)
				self.grid.addWidget(btn, x, y, 1, 1)
				
		self.editHandRange = QtGui.QLineEdit(self)
		self.editHandRange.returnPressed.connect(self.onEditHandRangeReturnPressed)
		self.grid.addWidget(self.editHandRange, x+1, 0, 1, 13)
							
		# add v/h stretches
		s = QtGui.QHBoxLayout()
		s.addStretch(999)
		self.grid.addItem(s, 0, 14, 0, 1)
		s = QtGui.QVBoxLayout()
		s.addStretch(999)
		self.grid.addItem(s, 14, 0, 1, 1)
		
		self.handleFontChanged()
				
	def handleFontChanged(self, font=None):
		font = QtGui.qApp.font() if font is None else font
		m = QtGui.QFontMetrics(font)
		w = m.width('AKs') +8
		h = w
		fixedSize = QtCore.QSize(w, h)
		for btn in self.handTypeButtons.values():
			btn.fixedSize = fixedSize
			btn.setMinimumSize(fixedSize)
			
	def handRange(self):
		p = []
		for btn in self.handTypeButtons.values():
			if btn.isChecked():
				p.append(btn.handType)
		handRange = PokerTools.HandRangeHoldem.fromString(','.join(p))
		return handRange
				
	def onRangeButtonToggled(self, flag):
		if self.lock:
			return
		handRange = self.handRange()
		self.editHandRange.setText(handRange.toString())
		
	def onEditHandRangeReturnPressed(self):
		text = self.editHandRange.text().toUtf8()
		text = unicode(text, 'utf-8')
		try:
			handRange = PokerTools.HandRangeHoldem.fromString(text)
		except PokerTools.HandRangeHoldem.ParseError:
			#TODO: how to give feedback?
			return
				
		handTypes = {}
		for hand in handRange:
			handType = PokerTools.handTypeFromHand(hand)
			if handType not in handTypes:
				handTypes[handType] = []
			handTypes[handType].append(hand)
		
		self.lock = True
		try:
			for handType, btn in self.handTypeButtons.items():
				hands = handTypes.get(handType, None)
				if hands and PokerTools.handTypeIsPair(handType) and len(hands) == 6:
					btn.setChecked(True)
				elif hands and PokerTools.handTypeIsSuited(handType) and len(hands) == 4:
					btn.setChecked(True)
				elif hands and len(hands) == 12:
					btn.setChecked(True)
				else:
					btn.setChecked(False)
		finally:
			self.lock = False
			
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = HandTypesHoldemWidget()
	gui.show()
	application.exec_()
