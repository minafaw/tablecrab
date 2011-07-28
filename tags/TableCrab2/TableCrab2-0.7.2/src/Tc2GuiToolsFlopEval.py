
import Tc2Config
import Tc2GuiHelp
from Tc2Lib import FlopEvalWidget
from PyQt4 import QtCore, QtGui
#************************************************************************************
#
#************************************************************************************

class FrameTool(QtGui.QFrame):
	
	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.flopEvalWidget = FlopEvalWidget.FlopEvalWidget(self)
		
		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox = QtGui.QDialogButtonBox(self)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)
		
		# connect signals
		Tc2Config.globalObject.initSettingsFinished.connect(self.onGlobalObjectInitSettingsFinished)
	
	def toolTip(self):
		return 'FlopEvaluator'

	def displayName(self):
		return 'FlopEvaluator'

	def handleSetCurrent(self):
		pass
		
	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.flopEvalWidget)
		
		grid.row()
		grid.col(Tc2Config.HLine(self))
		grid.row()
		grid.col(self.buttonBox)
		
	def onGlobalObjectInitSettingsFinished(self, globalObject):
		self.layout()
		#TODO: find better placeto init our widgets?
		self.flopEvalWidget.handleFontChanged()
		globalObject.settingsGlobal.guiFontChanged.connect(self.flopEvalWidget.handleFontChanged)
		
	def onHelp(self):
		Tc2GuiHelp.dialogHelp('toolsFlopEval', parent=self)
