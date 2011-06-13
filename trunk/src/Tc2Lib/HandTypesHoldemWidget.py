
#TODO: how to give feedback when the user types in an invalid hand pattern?
#TODO: slider functionality

from PyQt4 import QtCore, QtGui
import PokerTools
#************************************************************************************
#
#************************************************************************************
class HandtypeButton(QtGui.QPushButton):
		
	def __init__(self, handType, iRow, iCol, parent=None):
		QtGui.QPushButton.__init__(self, handType, parent)
		self.fixedSize = None
		self.handType = handType
		self.iRow = iRow
		self.iCol = iCol
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

class FixedSizedEdit(QtGui.QLineEdit):
	def __init__(self, parent=None):
		QtGui.QLineEdit.__init__(self, parent)
		self.fixedSize = None
	
	def sizeHint(self):
		return self.fixedSize
	
	
class HandTypesHoldemWidget(QtGui.QFrame):
	"""
	@note: call L{handleFontSizeChanged} if the font for the widget changes
	"""
	
	
	StyleSheet = '''
			QPushButton{
						border: 1px solid black;
						}
			#pair{background-color: #E3EBEE;}
			#pair:checked{background-color: #8DC6E2;}
			#suited{background-color: #FBDFDE;}
			#suited:checked{background-color: #E06D64;	}
			#offsuit{background-color: #FAF8E0;}
			#offsuit:checked{background-color:#C6B92C;}
			'''
	
	def __init__(self, parent=None, styleSheet=None):
		QtGui.QFrame.__init__(self, parent)
				
		self.lock = False
		
		self.editHandRange = QtGui.QLineEdit(self)
		self.editHandRange.returnPressed.connect(self.onEditHandRangeReturnPressed)
				
		self.handTypeButtons ={}	# handType --> button
		for iRow, row in enumerate(PokerTools.genHandTypeTable()):
			for iCol, handType in enumerate(row):
				btn = HandtypeButton(handType, iRow, iCol, parent=self)
				btn.setStyleSheet(self.StyleSheet if styleSheet is None else styleSheet)
				self.handTypeButtons[handType] = btn
				btn.toggled.connect(self.onRangeButtonToggled)
				#grid.addWidget(btn, x, y, 1, 1)
				
		# add range slider
		self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.editSlider = FixedSizedEdit(self)
									
		
		self.handleFontChanged()
		
		# layout
		
		box0 = QtGui.QHBoxLayout(self)
		box1 = QtGui.QVBoxLayout()
		box0.addLayout(box1)
		
		s = QtGui.QHBoxLayout()
		s.addStretch(999)
		box0.addItem(s)
		
		grid1 = QtGui.QGridLayout()
		grid1.setSpacing(0)
		grid1.setContentsMargins(0, 0, 0, 0)
		for btn in self.handTypeButtons.values():
			grid1.addWidget(btn, btn.iRow, btn.iCol)
					
		box1.addLayout(grid1)
		
		box2 = QtGui.QHBoxLayout()
		box1.addLayout(box2)
		box2.addWidget(self.editSlider)
		box2.addWidget(self.slider)
		box2.setStretch(1, 99)
		
		box1.addWidget(self.editHandRange)
		
		s = QtGui.QVBoxLayout()
		s.addStretch(999)
		box1.addItem(s)
					
	def handleFontChanged(self, font=None):
		font = QtGui.qApp.font() if font is None else font
		m = QtGui.QFontMetrics(font)
		w = m.width('AKs') +8
		h = w
		fixedSize = QtCore.QSize(w, h)
		for btn in self.handTypeButtons.values():
			btn.fixedSize = fixedSize
			btn.setMinimumSize(fixedSize)
		
		w = m.width('100.00%') + 20
		fixedSize = QtCore.QSize(w, self.editSlider.height())
		self.editSlider.fixedSize = fixedSize
		self.editSlider.setMinimumSize(fixedSize)
				
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
