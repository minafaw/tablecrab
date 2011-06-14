
from PyQt4 import QtCore, QtGui
import PokerTools
#************************************************************************************
#
#************************************************************************************

class CardButton(QtGui.QPushButton):
		
	def __init__(self, card, iRow, iCol, parent=None):
		QtGui.QPushButton.__init__(self, card.name(), parent)
		self.fixedSize = None
		self.card = card
		self.iRow = iRow
		self.iCol = iCol
		self.setObjectName(self.card.SuitNamesDict[self.card.suit()][0])
				
		self.setCheckable(True)
		self.setFocusPolicy(QtCore.Qt.NoFocus)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		sizePolicy.setHeightForWidth(True)
		self.setSizePolicy(sizePolicy)
			
	def sizeHint(self):
		return self.fixedSize
	
	def heightForWidth(self, width):
		return width

	
class CardSelectorWidget(QtGui.QFrame):
	"""
	@note: call L{handleFontSizeChanged} if the font for the widget changes
	"""
	
	
	StyleSheet = '''
			QPushButton{
						border: 1px solid black;
						}
			#diamond{background-color: #E3EBEE;}
			#diamond:checked{background-color: #378BCC; color: white;}
			#heart{background-color: #FBDFDE;}
			#heart:checked{background-color: #DF5348; color: white;}
			#club{background-color: #E5F8E6;}
			#club:checked{background-color:#518B54; color: white;}
			#spade{background-color: #F0F0F0;}
			#spade:checked{background-color: #686868; color: white;}
			'''
	
	def __init__(self, parent=None, styleSheet=None, maxCards=None, cards=None):
		QtGui.QFrame.__init__(self, parent)
				
		self._maxCards = maxCards
		self._buttonsSelected = []
				
		# add card buttons
		self._cardButtons ={}	# card --> button
		for iCol, suitName in enumerate(PokerTools.Card.SuitNames):
			for iRow, rankName in enumerate(PokerTools.Card.RankNames[::-1]):
				card = PokerTools.Card(rankName+suitName)
				btn = CardButton(card, iRow, iCol, parent=self)
				btn.setStyleSheet(self.StyleSheet if styleSheet is None else styleSheet)
				self._cardButtons[card] = btn
				btn.toggled.connect(self.onCardButtonToggled)
		
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
		for btn in self._cardButtons.values():
			grid1.addWidget(btn, btn.iRow, btn.iCol)
					
		box1.addLayout(grid1)
				
		s = QtGui.QVBoxLayout()
		s.addStretch(999)
		box1.addItem(s)
		
		# init widget with cards passed
		if cards is not None:
			for card in cards:
				self._cardButtons[card].setChecked(True)	
						
	def cards(self):
		return [btn.card for btn in self._buttonsSelected]
	
	def handleFontChanged(self, font=None):
		font = QtGui.qApp.font() if font is None else font
		m = QtGui.QFontMetrics(font)
		w = m.width('Qh') +8
		h = w
		fixedSize = QtCore.QSize(w, h)
		for btn in self._cardButtons.values():
			btn.fixedSize = fixedSize
			btn.setMinimumSize(fixedSize)
				
	def onCardButtonToggled(self, flag):
		btn = self.sender()
		if flag:
			if btn not in self._buttonsSelected:
				self._buttonsSelected.append(btn)
			if self._maxCards is not None and len(self._buttonsSelected) > self._maxCards:
				btn = self._buttonsSelected.pop(0)
				btn.setChecked(False)
		else:
			if btn in self._buttonsSelected:
				self._buttonsSelected.remove(btn)
		
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = CardSelectorWidget(
			maxCards=3, 
			cards=[PokerTools.Card('Ah'), PokerTools.Card('Kd'), PokerTools.Card('Qc')])
	gui.show()
	application.exec_()
