
#TODO: we are a bit off PokerStove when selecting range via percentage
#TODO: how to give feedback when the user types in an invalid hand pattern?
#TODO: slider mouse wheel up is not working

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
	HandTypes = (
			('AA', 0.638),
			('KK', 0.582),
			('QQ', 0.535),
			('JJ', 0.491),
			('TT', 0.451),
			('AKs', 0.414),
			('99', 0.411),
			('AQs', 0.398),
			('AKo', 0.385),
			('AJs', 0.384),
			('KQs', 0.381),
			('88', 0.375),
			('ATs', 0.372),
			('AQo', 0.368),
			('KJs', 0.368),
			('KTs', 0.356),
			('QJs', 0.356),
			('AJo', 0.353),
			('KQo', 0.351),
			('QTs', 0.345),
			('A9s', 0.344),
			('77', 0.343),
			('ATo', 0.339),
			('JTs', 0.338),
			('KJo', 0.336),
			('A8s', 0.334),
			('K9s', 0.329),
			('QJo', 0.325),
			('A7s', 0.323),
			('KTo', 0.323),
			('Q9s', 0.318),
			('A5s', 0.317),
			('66', 0.314),
			('A6s', 0.313),
			('QTo', 0.312),
			('J9s', 0.312),
			('A9o', 0.31),
			('A4s', 0.309),
			('T9s', 0.309),
			('K8s', 0.308),
			('JTo', 0.307),
			('A3s', 0.302),
			('A8o', 0.299),
			('K7s', 0.299),
			('Q8s', 0.297),
			('A2s', 0.294),
			('K9o', 0.294),
			('J8s', 0.291),
			('K6s', 0.29),
			('T8s', 0.288),
			('55', 0.288),
			('A7o', 0.287),
			('Q9o', 0.284),
			('98s', 0.284),
			('K5s', 0.282),
			('A5o', 0.28),
			('J9o', 0.278),
			('Q7s', 0.276),
			('T9o', 0.276),
			('A6o', 0.275),
			('K4s', 0.275),
			('A4o', 0.271),
			('K8o', 0.271),
			('J7s', 0.271),
			('Q6s', 0.27),
			('K3s', 0.268),
			('T7s', 0.268),
			('97s', 0.266),
			('87s', 0.266),
			('A3o', 0.263),
			('44', 0.263),
			('K7o', 0.262),
			('Q5s', 0.262),
			('K2s', 0.261),
			('Q8o', 0.26),
			('Q4s', 0.255),
			('J8o', 0.255),
			('A2o', 0.254),
			('T8o', 0.253),
			('K6o', 0.252),
			('J6s', 0.252),
			('T6s', 0.25),
			('76s', 0.25),
			('98o', 0.249),
			('86s', 0.249),
			('Q3s', 0.248),
			('96s', 0.248),
			('J5s', 0.246),
			('K5o', 0.243),
			('Q2s', 0.242),
			('Q7o', 0.239),
			('J4s', 0.239),
			('33', 0.239),
			('65s', 0.236),
			('K4o', 0.235),
			('J7o', 0.234),
			('75s', 0.234),
			('J3s', 0.233),
			('T7o', 0.232),
			('T5s', 0.232),
			('Q6o', 0.231),
			('85s', 0.231),
			('97o', 0.23),
			('95s', 0.23),
			('87o', 0.23),
			('K3o', 0.228),
			('J2s', 0.227),
			('T4s', 0.227),
			('54s', 0.227),
			('Q5o', 0.223),
			('K2o', 0.221),
			('T3s', 0.221),
			('64s', 0.221),
			('22', 0.218),
			('74s', 0.217),
			('Q4o', 0.215),
			('T2s', 0.214),
			('84s', 0.214),
			('76o', 0.214),
			('J6o', 0.213),
			('94s', 0.213),
			('86o', 0.212),
			('T6o', 0.211),
			('53s', 0.211),
			('96o', 0.21),
			('93s', 0.209),
			('Q3o', 0.208),
			('J5o', 0.207),
			('63s', 0.204),
			('43s', 0.204),
			('92s', 0.202),
			('Q2o', 0.201),
			('73s', 0.2),
			('J4o', 0.199),
			('65o', 0.199),
			('83s', 0.198),
			('75o', 0.196),
			('52s', 0.195),
			('T5o', 0.193),
			('85o', 0.193),
			('82s', 0.193),
			('J3o', 0.192),
			('95o', 0.191),
			('62s', 0.188),
			('54o', 0.188),
			('42s', 0.188),
			('T4o', 0.187),
			('J2o', 0.185),
			('72s', 0.184),
			('64o', 0.182),
			('32s', 0.181),
			('T3o', 0.179),
			('74o', 0.178),
			('84o', 0.174),
			('T2o', 0.173),
			('94o', 0.172),
			('53o', 0.172),
			('93o', 0.167),
			('63o', 0.164),
			('43o', 0.163),
			('92o', 0.161),
			('73o', 0.159),
			('83o', 0.156),
			('52o', 0.154),
			('82o', 0.151),
			('42o', 0.147),
			('62o', 0.146),
			('72o', 0.142),
			('32o', 0.139),
			)
	@classmethod
	def handTypesFromPct(klass, pct):
		n = len(klass.HandTypes) / 100.0 *pct
		n = int(round(n, 0))
		return [handType for (handType, ev) in klass.HandTypes[:n]]
		

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
