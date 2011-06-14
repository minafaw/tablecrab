
#TODO: we are a bit off PokerStove when selecting range via percentage
#TODO: how to give feedback when the user types in an invalid hand pattern?
#TODO: slider mouse wheel-up is not working

from PyQt4 import QtCore, QtGui
import PokerTools
#************************************************************************************
#
#************************************************************************************
#TODO: 
class EvsPokerStove(object):
	"""evs according to PokerStoves method to calc hand ranks
	(hand preflop all-in vs three random hands)
	"""
	HandTypes = (	# handType, ev, nCards
			('AA', 0.638, 6),
			('KK', 0.582, 6),
			('QQ', 0.534, 6),
			('JJ', 0.491, 6),
			('TT', 0.452, 6),
			('AKs', 0.414, 4),
			('99', 0.411, 6),
			('AQs', 0.398, 4),
			('AKo', 0.385, 12),
			('AJs', 0.384, 4),
			('KQs', 0.382, 4),
			('88', 0.375, 6),
			('ATs', 0.372, 4),
			('AQo', 0.368, 12),
			('KJs', 0.368, 4),
			('KTs', 0.356, 4),
			('QJs', 0.356, 4),
			('AJo', 0.353, 12),
			('KQo', 0.351, 12),
			('A9s', 0.345, 4),
			('QTs', 0.345, 4),
			('77', 0.343, 6),
			('ATo', 0.339, 12),
			('JTs', 0.338, 4),
			('KJo', 0.336, 12),
			('A8s', 0.334, 4),
			('K9s', 0.329, 4),
			('QJo', 0.325, 12),
			('A7s', 0.324, 4),
			('KTo', 0.323, 12),
			('Q9s', 0.318, 4),
			('A5s', 0.317, 4),
			('66', 0.315, 6),
			('A6s', 0.313, 4),
			('QTo', 0.312, 12),
			('J9s', 0.311, 4),
			('A9o', 0.31, 12),
			('A4s', 0.309, 4),
			('T9s', 0.309, 4),
			('K8s', 0.307, 4),
			('JTo', 0.306, 12),
			('A3s', 0.302, 4),
			('A8o', 0.299, 12),
			('K7s', 0.299, 4),
			('Q8s', 0.297, 4),
			('A2s', 0.294, 4),
			('K9o', 0.294, 12),
			('J8s', 0.291, 4),
			('K6s', 0.29, 4),
			('T8s', 0.288, 4),
			('55', 0.288, 6),
			('A7o', 0.287, 12),
			('Q9o', 0.284, 12),
			('98s', 0.284, 4),
			('K5s', 0.282, 4),
			('A5o', 0.28, 12),
			('J9o', 0.278, 12),
			('Q7s', 0.277, 4),
			('T9o', 0.276, 12),
			('A6o', 0.275, 12),
			('K4s', 0.275, 4),
			('A4o', 0.271, 12),
			('K8o', 0.271, 12),
			('J7s', 0.271, 4),
			('Q6s', 0.27, 4),
			('K3s', 0.268, 4),
			('T7s', 0.268, 4),
			('97s', 0.266, 4),
			('87s', 0.266, 4),
			('A3o', 0.263, 12),
			('K7o', 0.262, 12),
			('K2s', 0.262, 4),
			('Q5s', 0.262, 4),
			('44', 0.262, 6),
			('Q8o', 0.261, 12),
			('Q4s', 0.255, 4),
			('J8o', 0.255, 12),
			('A2o', 0.254, 12),
			('T8o', 0.253, 12),
			('K6o', 0.252, 12),
			('J6s', 0.252, 4),
			('T6s', 0.25, 4),
			('76s', 0.25, 4),
			('98o', 0.249, 12),
			('86s', 0.249, 4),
			('Q3s', 0.248, 4),
			('96s', 0.248, 4),
			('J5s', 0.246, 4),
			('K5o', 0.243, 12),
			('Q2s', 0.242, 4),
			('Q7o', 0.239, 12),
			('J4s', 0.239, 4),
			('33', 0.239, 6),
			('65s', 0.236, 4),
			('K4o', 0.235, 12),
			('75s', 0.234, 4),
			('J7o', 0.233, 12),
			('J3s', 0.233, 4),
			('T7o', 0.232, 12),
			('T5s', 0.232, 4),
			('Q6o', 0.231, 12),
			('85s', 0.231, 4),
			('97o', 0.23, 12),
			('95s', 0.23, 4),
			('87o', 0.23, 12),
			('K3o', 0.228, 12),
			('J2s', 0.227, 4),
			('T4s', 0.227, 4),
			('54s', 0.227, 4),
			('Q5o', 0.223, 12),
			('T3s', 0.221, 4),
			('64s', 0.221, 4),
			('K2o', 0.22, 12),
			('22', 0.219, 6),
			('74s', 0.217, 4),
			('Q4o', 0.215, 12),
			('T2s', 0.214, 4),
			('84s', 0.214, 4),
			('76o', 0.214, 12),
			('J6o', 0.213, 12),
			('94s', 0.213, 4),
			('86o', 0.212, 12),
			('T6o', 0.211, 12),
			('53s', 0.211, 4),
			('96o', 0.21, 12),
			('Q3o', 0.208, 12),
			('93s', 0.208, 4),
			('J5o', 0.207, 12),
			('63s', 0.204, 4),
			('43s', 0.204, 4),
			('92s', 0.202, 4),
			('Q2o', 0.201, 12),
			('73s', 0.2, 4),
			('J4o', 0.199, 12),
			('65o', 0.199, 12),
			('83s', 0.198, 4),
			('75o', 0.196, 12),
			('52s', 0.195, 4),
			('T5o', 0.193, 12),
			('85o', 0.193, 12),
			('82s', 0.193, 4),
			('J3o', 0.192, 12),
			('95o', 0.191, 12),
			('42s', 0.189, 4),
			('62s', 0.188, 4),
			('54o', 0.188, 12),
			('T4o', 0.187, 12),
			('J2o', 0.185, 12),
			('72s', 0.184, 4),
			('64o', 0.182, 12),
			('32s', 0.181, 4),
			('T3o', 0.18, 12),
			('74o', 0.178, 12),
			('84o', 0.174, 12),
			('T2o', 0.173, 12),
			('94o', 0.172, 12),
			('53o', 0.172, 12),
			('93o', 0.167, 12),
			('63o', 0.164, 12),
			('43o', 0.163, 12),
			('92o', 0.16, 12),
			('73o', 0.16, 12),
			('83o', 0.156, 12),
			('52o', 0.154, 12),
			('82o', 0.151, 12),
			('42o', 0.147, 12),
			('62o', 0.146, 12),
			('72o', 0.142, 12),
			('32o', 0.139, 12),
			)
	@classmethod
	def handTypesFromPct(klass, pct):
		#NOTE: we implement rule: a handType is included when all* hands of that type 
		# are within % range.
		# alternatives:
		# a) a handType is included if at least one hand of that type is in % range
		# b) a handType is included if >= half of the hands of that type is in % range
		# i guess PokerStove uses either alternative a) or b) ..that's why it adjusts
		# % display at times. we could implement one or the other alternative, but can 
		# not adjust % display because slider and spinBox are interconnnected.
		total = int(round(1362 / 100.0 * pct, 0))
		n = 0
		result = []
		for handType, _, nCards in klass.HandTypes:
			n += nCards
			if n <= total:
				result.append(handType)
			elif n > total:
				break
		return result


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
				
		# pseudo lock
		self.lock = False
		
		# add range table buttons
		self.handTypeButtons ={}	# handType --> button
		for iRow, row in enumerate(PokerTools.genHandTypeTable()):
			for iCol, handType in enumerate(row):
				btn = HandtypeButton(handType, iRow, iCol, parent=self)
				btn.setStyleSheet(self.StyleSheet if styleSheet is None else styleSheet)
				self.handTypeButtons[handType] = btn
				btn.toggled.connect(self.onRangeButtonToggled)
				#grid.addWidget(btn, x, y, 1, 1)
				
		self.editHandRange = QtGui.QLineEdit(self)
		self.editHandRange.returnPressed.connect(self.onEditHandRangeReturnPressed)
		
		# add range slider
		self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.slider.setMaximum(1000)
		self.slider.setPageStep(100)
		self.slider.setTickInterval(100)
		self.slider.setTickPosition(self.slider.TicksAbove)
		self.slider.valueChanged.connect(self.onSliderValueChanged)
		self.spinSlider = QtGui.QDoubleSpinBox(self)
		self.spinSlider.setSuffix('%')
		self.spinSlider.setMaximum(100.0)
		self.spinSlider.setDecimals(1)
		self.spinSlider.setSingleStep(0.1)
		self.spinSlider.valueChanged.connect(self.onSpinSliderValueChanged)
		
		self.handleFontChanged()
		
		# layout
		
		box0 = QtGui.QHBoxLayout(self)
		box0.setSpacing(0)
		box0.setContentsMargins(0, 0, 0, 0)
		box1 = QtGui.QVBoxLayout()
		box0.addLayout(box1)
		
		s = QtGui.QHBoxLayout()
		s.addStretch(999)
		box0.addItem(s)
		
		grid1 = QtGui.QGridLayout()
		#grid1.setSpacing(0)
		#grid1.setContentsMargins(0, 0, 0, 0)
		for btn in self.handTypeButtons.values():
			grid1.addWidget(btn, btn.iRow, btn.iCol)
					
		box1.addLayout(grid1)
				
		box2 = QtGui.QHBoxLayout()
		box1.addLayout(box2)
		box2.addWidget(self.spinSlider)
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
			
	def onSpinSliderValueChanged(self, n):
		handTypes = EvsPokerStove.handTypesFromPct(n)
		self.lock = True
		try:
			for handType, btn in self.handTypeButtons.items():
				btn.setChecked(handType in handTypes)
			self.slider.setValue(int(n)*10)
			handRange = self.handRange()
			self.editHandRange.setText(handRange.toString())
		finally:
			self.lock = False
			
	def onSliderValueChanged(self, n):
		if not self.lock:
			pct = (n / 10.0)
			self.spinSlider.setValue(pct)
		
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = HandTypesHoldemWidget()
	gui.show()
	application.exec_()
