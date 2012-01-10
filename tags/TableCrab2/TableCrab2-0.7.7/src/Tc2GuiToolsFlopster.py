
import Tc2Config
import Tc2GuiHelp
from Tc2Lib import PokerTools
from Tc2Lib import ColorButton
from PyQt4 import QtCore, QtGui
import os
#************************************************************************************
#
#************************************************************************************
class BoardWidget(QtGui.QWidget):
	
	ColorFelt = QtGui.QColor('lightgray')
	ColorCardBorder = QtGui.QColor('black')
	CardFrame = 5
	CardOffset = 10
	CardWidth = 80
	CardHeight = 100
	
	RankOffsetY = -11
	
	CardSuitColors = {	# colorText, colorBackground
			'h': (QtGui.QColor('#E8E1E1'), QtGui.QColor('#9E5250')),
			's': (QtGui.QColor('#EBE6E6'), QtGui.QColor('#6E6E6E')),
			'c': (QtGui.QColor('#D7DDD7'), QtGui.QColor('#4C8049')),
			'd': (QtGui.QColor('#E1E5EF'), QtGui.QColor('#4D609D')),
			}
			
	CardRanks = {	# x-offset
			'2': 15,
			'3': 15,
			'4': 15,
			'5': 15,
			'6': 15,
			'7': 15,
			'8': 15,
			'9': 15,
			'T': 11,
			'J': 13,
			'Q': 6,
			'K': 8,
			'A': 9,
			}
			
	ZoomMin = 10
	ZoomMax = 100
	ZoomDefault = 100
	
	
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		
		self._cards = []
		self._colorFelt = self.ColorFelt
		self._colorCardBorder = self.ColorCardBorder
		self._pixmap = None
		self._pixmaps = []
		self._zoom = 100
		self.setCards(())
		
	def zoom(self):
		return self._zoom
		
	def setZoom(self, n):
		"""
		@param f: (float) zoom factor (10 - 100)
		"""
		if n < self.ZoomMin:
			self._zoom = self.ZoomMin
		elif n > self.ZoomMax:
			self._zoom = self.ZoomMax
		else:
			self._zoom = n
		if self._pixmaps:
			self.setPixmaps(self._pixmaps)
		else:
			self.setCards(self._cards)
		
	def feltColor(self):
		return self._colorFelt
		
	def setFeltColor(self, color):
		self._colorFelt = color
		if self._pixmaps:
			self.setPixmaps(self._pixmaps)
		else:
			self.setCards(self._cards)
	
	def cardBorderColor(self):
		return self._colorCardBorder
		
	def setCardBorderColor(self, color):
		self._colorCardBorder = color
		if self._pixmaps:
			self.setPixmaps(self._pixmaps)
		else:
			self.setCards(self._cards)	
	
	def cards(self):
		return [i for i in self._cards if i is not None]
		
	def setPixmaps(self, cards):
		"""
		@param cards: (tuple) (card, pixmap) for each card 
		"""
		self._cards = [i[0] for i in cards]
		while len(self._cards) < 5:
			self._cards.append(None)
		self._pixmaps = cards
		
		# prep pixmap
		px = QtGui.QPixmap(
				(self.CardFrame*2) + (self.CardWidth*5) + (self.CardOffset*4),
				(self.CardFrame*2) + (self.CardHeight)
				)
		px.fill(self._colorFelt)
		
		# draw cards
		p = QtGui.QPainter(px)
		p.setRenderHint(p.Antialiasing)
		
		# draw cards
		offsX = self.CardFrame
		for i in range(5):
			pixmap = None
			try: pixmap = cards[i][1]
			except IndexError: pass
			
			rc = QtCore.QRect(offsX, self.CardFrame, self.CardWidth, self.CardHeight)
			if pixmap is None:
				brush = QtGui.QBrush(self._colorFelt)
				p.setBrush(brush)
				p.setPen(self._colorCardBorder)
				p.drawRoundedRect(rc, 6, 6)
			else:
				pixmap = pixmap.scaled(rc.size(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
				
				p.drawPixmap(rc, pixmap, QtCore.QRect(0, 0, pixmap.width(), pixmap.height()))
					
			offsX += self.CardOffset + self.CardWidth
		
		p.end()
		self._pixmap = px
		self.update()
		
	
	def setCards(self, cards):
		self._cards = list(cards)
		while len(self._cards) < 5:
			self._cards.append(None)
		self._pixmaps = []
		
		# prep pixmap
		px = QtGui.QPixmap(
				(self.CardFrame*2) + (self.CardWidth*5) + (self.CardOffset*4),
				(self.CardFrame*2) + (self.CardHeight)
				)
		px.fill(self._colorFelt)
		
		# draw cards
		p = QtGui.QPainter(px)
		p.setRenderHint(p.Antialiasing)
		p.setRenderHint(p.TextAntialiasing)
			
		font = QtGui.QFont(p)
		font.setFamily('arial')
		font.setBold(True)
		font.setPointSize(50)
		p.setFont(font)
		fm = QtGui.QFontMetrics(font)
		fontHeight = fm.height()
				
		offsX = self.CardFrame
		for i in range(5):
			card = None
			try: card = self._cards[i]
			except IndexError: pass
			
			colorFG = None
			if card is None:
				colorBG = self._colorFelt
			else:
				colorFG, colorBG = self.CardSuitColors[card.suitName()]
					
			# draw card background
			rc = QtCore.QRect(offsX, self.CardFrame, self.CardWidth, self.CardHeight)
			brush = QtGui.QBrush(colorBG)
			p.setBrush(brush)
			p.setPen(self._colorCardBorder)
			p.drawRoundedRect(rc, 6, 6)
			
			if card is not None:
				# draw card rank
				rank = card.rankName()
				p.setPen(colorFG)
				rankOffsetX = self.CardRanks[rank]
				pt = QtCore.QPoint(offsX + rankOffsetX, self.CardFrame + fontHeight + self.RankOffsetY)
				p.drawText(pt, rank)
													
			offsX += self.CardOffset + self.CardWidth
			
		p.end()
		self._pixmap = px
		self.update()
	
	
	def paintEvent(self, event):
		rc = self.geometry()
		p = QtGui.QPainter(self)
		
		# draw background
		p.setBrush(QtGui.QBrush(self._colorFelt))
		p.drawRect(rc)
						
		# draw pixmap
		borderW = 1
		rc.adjust(borderW, borderW, -borderW, -borderW)
		
		# calc zoom factor
		size = QtCore.QSize(rc.width(), rc.height())
		zoomFactor = self._zoom / 100.0
		w = rc.width() * zoomFactor
		h = rc.height() * zoomFactor
		if w < rc.width() and h < rc.height():
			size.setWidth(w)
			size.setHeight(h)
		
		px = self._pixmap.scaled(size, QtCore.Qt.KeepAspectRatio, )
		rcDst = QtCore.QRect(
				rc.left() + ((rc.width() - px.width()) / 2),
				rc.top() + ((rc.height() - px.height()) / 2),
				px.width(),
				px.height()
				)
		p.drawPixmap(rcDst, px, QtCore.QRect(0, 0, px.width(), px.height()))
		
		# finally
		p.end()
		
	
class FlopsterWidget(QtGui.QFrame):
		
	feltColorChanged = QtCore.pyqtSignal(QtGui.QColor)
	cardBorderColorChanged = QtCore.pyqtSignal(QtGui.QColor)
	directoryChanged = QtCore.pyqtSignal(QtCore.QString)
	zoomChanged = QtCore.pyqtSignal(int)
		
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		
		self.deck = PokerTools.CardDeck()
		self.deck.shuffle()
		
		self.boardWidget = BoardWidget(self)
		
		self.buttonNext = QtGui.QPushButton('Next', self)
		self.buttonNext.clicked.connect(self.onButtonNextClicked)
		self.buttonNext.setToolTip('Next street (Right)')
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Right') )
		action.triggered.connect(self.onButtonNextClicked)
		self.addAction(action)
		
		self.buttonRandom = QtGui.QPushButton('Random', self)
		self.buttonRandom.clicked.connect(self.onbuttonRandomClicked)
		self.buttonRandom.setToolTip('Random card(s) on current street (Left)')
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Left') )
		action.triggered.connect(self.onbuttonRandomClicked)
		self.addAction(action)
		
		self.editCards = QtGui.QLineEdit(self)
		self.editCards.returnPressed.connect(self.onEditCardsReturnPressed)
		
		self.labelDirectory = QtGui.QLabel('Custom cards:', self)
		self.editDirectory = QtGui.QLineEdit(self)
		self.editDirectory.returnPressed.connect(self.onEditDirectoryReturnPressed)
		self.editDirectory.textEdited.connect(self.onEditDirectoryTextEdited)
		self.buttonDirectory = QtGui.QPushButton('...', self)
		self.buttonDirectory.clicked.connect(self.onButtonDirectoryClicked)
		
		self.colorButtonFelt = ColorButton.GroupColorButton(
				parent=self, 
				text='Felt color:', 
				defaultColor=self.boardWidget.ColorFelt,
				)
		self.colorButtonFelt.colorChanged.connect(self.onColorButtonFeltColorChanged)
		self.colorButtonCardBorder = ColorButton.GroupColorButton(
				parent=self, 
				text='Border color:', 
				defaultColor=self.boardWidget.ColorCardBorder,
				)
		self.colorButtonCardBorder.colorChanged.connect(self.onColorButtonCardBorderColorChanged)
		
		self.labelZoom = QtGui.QLabel('Zoom:', self)
		self.spinZoom = QtGui.QSpinBox(self)
		self.spinZoom.setRange(self.boardWidget.ZoomMin, self.boardWidget.ZoomMax)
		self.spinZoom.setValue( self.boardWidget.ZoomDefault)
		self.spinZoom.valueChanged.connect(self.onZoomValueChanged)
				
		self.layout()
	
		
	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.boardWidget, colspan=3)
		grid.row()
		grid.col(self.buttonNext)
		grid.col(self.editCards)
		grid.col(self.buttonRandom)
		grid.row()
		grid.col(self.labelDirectory)
		grid.col(self.editDirectory)
		grid.col(self.buttonDirectory)
		grid.row()
		grid.col(self.labelZoom)
		grid.col(self.spinZoom)
		grid.row()
		grid.col(self.colorButtonFelt.label())
		grid.col(self.colorButtonFelt.colorButton())
		grid.col(self.colorButtonFelt.resetButton())
		grid.row()
		grid.col(self.colorButtonCardBorder.label())
		grid.col(self.colorButtonCardBorder.colorButton())
		grid.col(self.colorButtonCardBorder.resetButton())
				
	def directory(self):
		directory = self.editDirectory.text().toUtf8()
		return unicode(directory, 'utf-8')
		
	def setDirectory(self, directory):
		self.editDirectory.setText(directory)
		cards = self.boardWidget.cards()
		self.setCards(cards)
		
	def feltColor(self):
		return self.boardWidget.feltColor()
		
	def setFeltColor(self, color):
		self.boardWidget.setFeltColor(color)
		self.colorButtonFelt.setColor(color)
			
	def cardBorderColor(self):
		return self.boardWidget.cardBorderColor()
		
	def setCardBorderColor(self, color):
		self.boardWidget.setCardBorderColor(color)
		self.colorButtonCardBorder.setColor(color)
		
	def zoom(self):
		return self.boardWidget.zoom()
		
	def setZoom(self, n):
		self.boardWidget.setZoom(n)
		self.spinZoom.setValue(self.boardWidget.zoom())
		
	def setCards(self, cards):
		self.editCards.setText(', '.join([card.name() for card in cards]))
		
		directory = self.directory()
		#NOTE: we draw cards directly if no cards are specified to avoid
		# the nasty error messages below on startup
		if not directory or not cards:
			self.boardWidget.setCards(cards)
			return
				
		if not os.path.isdir(directory):
			Tc2Config.msgWarning(self, 'Invalid directory')
			return
			
		fmts = ('.png', '.jpg', '.svg', '.bmp')
		pixmaps = [[i, None] for i in cards]
		for name in os.listdir(directory):
			myName, ext = os.path.splitext(name.lower())
			if ext not in fmts: continue
			if len(myName) != 2: continue
			myName = myName[0].upper() + myName[1].lower()
					
			try: card = PokerTools.Card(myName)
			except ValueError: continue
						
			try: i = cards.index(card)
			except ValueError: continue
					
			# load pixmap
			fileName = os.path.normpath(os.path.join(directory, name))
			px = QtGui.QPixmap()
			if px.load(fileName):
				pixmaps[i][1] = px
		
		# errcheck
		for card, px in pixmaps:
			if px is None:
				Tc2Config.msgWarning(self, 'Could not load card: %s' % card.name())
				return
				
		self.boardWidget.setPixmaps(pixmaps)
	
		
	def onButtonNextClicked(self):
		cards = self.boardWidget.cards()
		if len(cards) == 5:
			self.deck = PokerTools.CardDeck()
			self.deck.shuffle()
			cards = []
			self.boardWidget.setCards(cards)
			self.editCards.setText('')
			return
			
		if len(cards) == 0:
			cards = [self.deck.nextCard() for i in range(3)]
		elif len(cards) >= 3:
			cards.append(self.deck.nextCard())
		self.setCards(cards)
	
	def onbuttonRandomClicked(self):
		cards = self.boardWidget.cards()
		if len(cards) <= 3:
			self.deck = PokerTools.CardDeck()
			self.deck.shuffle()
			cards = [self.deck.nextCard() for i in range(3)]
			self.setCards(cards)
		elif len(cards) > 3:
			card = cards.pop(-1)
			cards.append(self.deck.nextCard())
			self.deck.cards.append(card)
			self.setCards(cards)
			
	def onButtonDirectoryClicked(self):
		dlg = QtGui.QFileDialog(self, 'Select directory containing custom cards..')
		dlg.setFileMode(dlg.Directory)
		if dlg.exec_() == dlg.Reject:
			return
		directory = dlg.directory().absolutePath()
		self.setDirectory(directory)
		self.directoryChanged.emit(directory)
				
	def onEditCardsReturnPressed(self):
		text = self.editCards.text().toUtf8()
		text = unicode(text, 'utf-8')
		cards = [i.strip() for i in text.split(',')]
		try:
			cards = [PokerTools.Card(i) for i in cards]
		except ValueError:
			Tc2Config.msgWarning(self, 'Invalid cards')
			return
		#NOTE: we don't care about duplicate cards here. ok?	
		self.setCards(cards)
		
	def onEditDirectoryReturnPressed(self):
		cards = self.boardWidget.cards()
		self.setCards(cards)
			
	def onEditDirectoryTextEdited(self, text):
		directory = self.editDirectory.text()
		self.directoryChanged.emit(directory)
		
	def onColorButtonFeltColorChanged(self, color):
		self.boardWidget.setFeltColor(color)
		self.feltColorChanged.emit(color)	
		
	def onColorButtonCardBorderColorChanged(self, color):
		self.boardWidget.setCardBorderColor(color)
		self.cardBorderColorChanged.emit(color)
		
	def onZoomValueChanged(self, n):
		self.boardWidget.setZoom(n)
		self.zoomChanged.emit(n)
		
		
		
		
	
class FrameTool(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/Flopster'
	SettingsKeyDirectory = SettingsKeyBase + '/Directory'
	SettingsKeyFeltColor = SettingsKeyBase + '/ColorFelt'
	SettingsKeyCardBorderColor = SettingsKeyBase + '/ColorCardBorder'
	SettingsKeyZoom = SettingsKeyBase + '/Zoom'
	

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.flopsterWidget = FlopsterWidget(parent=self)
		self.flopsterWidget.feltColorChanged.connect(self.onFeltColorChanged)
		self.flopsterWidget.cardBorderColorChanged.connect(self.onCardBorderColorChanged)
		self.flopsterWidget.directoryChanged.connect(self.onDirectoryChanged)
		self.flopsterWidget.zoomChanged.connect(self.onZoomChanged)
				
		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)
		
		self.layout()
		
		# init flopster widget
		self.flopsterWidget.setUpdatesEnabled(False)
		directory = Tc2Config.settingsValue(self.SettingsKeyDirectory, '').toString()
		self.flopsterWidget.setDirectory(directory)
		colorName = Tc2Config.settingsValue(self.SettingsKeyFeltColor, '').toString()
		color = QtGui.QColor(colorName)
		if color.isValid():
			self.flopsterWidget.setFeltColor(color)
		colorName = Tc2Config.settingsValue(self.SettingsKeyCardBorderColor, '').toString()
		color = QtGui.QColor(colorName)
		if color.isValid():
			self.flopsterWidget.setCardBorderColor(color)
		self.flopsterWidget.setUpdatesEnabled(True)
		n, ok = Tc2Config.settingsValue(self.SettingsKeyZoom, self.flopsterWidget.zoom()).toInt()
		if ok:
			self.flopsterWidget.setZoom(n)
		
		
	def toolTip(self):
		return 'Flopster'

	def displayName(self):
		return 'Flopster'
		
	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.flopsterWidget)
		grid.row()
		grid.col(Tc2Config.HLine(self), colspan=3)
		grid.row()
		grid.col(self.buttonBox, colspan=3)

	def handleSetCurrent(self):
		pass
		
	def onHelp(self):
		Tc2GuiHelp.dialogHelp('toolsFlopster', parent=self)
	
	def onFeltColorChanged(self, color):
		Tc2Config.settingsSetValue(self.SettingsKeyFeltColor, color.name())
		
	def onCardBorderColorChanged(self, color):
		Tc2Config.settingsSetValue(self.SettingsKeyCardBorderColor, color.name())
		
	def onDirectoryChanged(self, directory):
		Tc2Config.settingsSetValue(self.SettingsKeyDirectory, directory)
		
	def onZoomChanged(self, n):
		Tc2Config.settingsSetValue(self.SettingsKeyZoom, n)
		
#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = FlopsterWidget()
	#gui = BoardWidget()
	gui.show()
	application.exec_()
