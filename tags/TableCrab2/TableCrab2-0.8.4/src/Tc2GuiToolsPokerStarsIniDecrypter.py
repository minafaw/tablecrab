# -*- coding: utf-8 -*-
#TODO: we may have to use QDir for file operations (unicode issues).

from __future__ import with_statement

import Tc2Config
import Tc2GuiHelp
from Tc2Lib import PokerStarsIniDecrypter
from PyQt4 import QtCore, QtGui, QtWebKit
import os
#************************************************************************************
#
#************************************************************************************
class FrameTool(QtGui.QFrame):

	SettingsKeyBase = 'Gui/Tools/PokerStars/IniDecrypter'
	SettingsKeyDialogDecryptState = SettingsKeyBase + '/DialogDecryptState'
	SettingsKeyDialogEncryptState = SettingsKeyBase + '/DialogEncryptState'

	Magic = '-Tc2'

	def __init__(self, parent=None):
		QtGui.QFrame.__init__(self, parent)

		self.lastDirectory = None

		self.edit = QtGui.QPlainTextEdit(self)
		self.edit.setReadOnly(True)

		self.buttonBox = QtGui.QDialogButtonBox(self)

		self.buttonDecrypt = QtGui.QPushButton('Decrypt directory..', self)
		self.buttonDecrypt.setToolTip('Decrypt directory (Ctrl+D)')
		self.buttonDecrypt.clicked.connect(self.onDecrypt)
		self.buttonBox.addButton(self.buttonDecrypt, self.buttonBox.ActionRole)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+D') )
		action.triggered.connect(self.onDecrypt)
		self.addAction(action)

		self.buttonEncrypt = QtGui.QPushButton('Encrypt', self)
		self.buttonEncrypt.setToolTip('Encrypt directory (Ctrl+E)')
		self.buttonEncrypt.clicked.connect(self.onEncrypt)
		self.buttonBox.addButton(self.buttonEncrypt, self.buttonBox.ActionRole)
		self.actionEncrypt = QtGui.QAction(self)
		self.actionEncrypt.setShortcut(QtGui.QKeySequence('Ctrl+E') )
		self.actionEncrypt.triggered.connect(self.onEncrypt)
		self.addAction(self.actionEncrypt)

		self.buttonEncryptDirectory = QtGui.QPushButton('Encrypt directory..', self)
		self.buttonEncryptDirectory.setToolTip('Encrypt directory (Ctrl+R)')
		self.buttonEncryptDirectory.clicked.connect(self.onEncryptDirectory)
		self.buttonBox.addButton(self.buttonEncryptDirectory, self.buttonBox.ActionRole)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('Ctrl+R') )
		action.triggered.connect(self.onEncryptDirectory)
		self.addAction(action)

		self.buttonHelp = QtGui.QPushButton('Help', self)
		self.buttonHelp.setToolTip('Help (F1)')
		self.buttonHelp.clicked.connect(self.onHelp)
		self.buttonBox.addButton(self.buttonHelp, self.buttonBox.HelpRole)

		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence('F1') )
		action.triggered.connect(self.onHelp)
		self.addAction(action)

		self.layout()
		self.adjustActions()


	def adjustActions(self):
		self.buttonEncrypt.setEnabled(self.lastDirectory is not None)
		self.actionEncrypt.setEnabled(self.lastDirectory is not None)


	def layout(self):
		grid = Tc2Config.GridBox(self)
		grid.col(self.buttonBox)
		grid.row()
		grid.col(Tc2Config.HLine(self))
		grid.row()
		grid.col(self.edit)

	def toolTip(self):
		return 'PokerStars ini decrypter'

	def displayName(self):
		return 'PokerStarsIniDecrypter'

	def handleSetCurrent(self=False):
		pass

	def onHelp(self):
		Tc2GuiHelp.dialogHelp('toolsPokerStarsIniDecrypter', parent=self)

	def onDecrypt(self, checked):

		dlg = QtGui.QFileDialog(self)
		dlg.setWindowTitle('Chosse directory to decrypt ini files..')
		dlg.setFileMode(dlg.Directory)
		dlg.restoreState( Tc2Config.settingsValue(self.SettingsKeyDialogDecryptState, QtCore.QByteArray()).toByteArray() )
		if dlg.exec_() == dlg.Rejected:
			return
		Tc2Config.settingsSetValue(self.SettingsKeyDialogDecryptState, dlg.saveState() )
		directory = dlg.directory().canonicalPath()
		directory = directory.toUtf8()
		directory = unicode(directory, 'utf-8')

		self.edit.setPlainText('')
		self.edit.insertPlainText('Decrypting ini files\n')
		self.edit.insertPlainText('------------------------------\n')
		for root, dirs, files in os.walk(directory):
			self.edit.insertPlainText('Enter directory: %s\n' % root)
			for name in files:
				myName, ext = os.path.splitext(name)
				if ext.lower() != '.ini': continue
				if myName.endswith(self.Magic): continue

				fileName = os.path.join(root, name)
				with open(fileName, 'rb') as fp:
					data = fp.read()
					try:
						data = PokerStarsIniDecrypter.decryptString(data)
					except PokerStarsIniDecrypter.Error, d:
						self.edit.insertPlainText('Error: could not decrypt: %s\n' % name)
						continue

				print '\r\n' in data
				myName = myName + self.Magic + ext
				fileName = os.path.join(root, myName)
				with open(fileName, 'wb') as fp:
					fp.write(data)
				self.edit.insertPlainText('Decrypted: %s --> %s\n' % (name, myName) )
		self.edit.insertPlainText('Done\n')
		self.lastDirectory = directory
		self.adjustActions()


	def onEncrypt(self, checked=False):
		if self.lastDirectory is None:
			return

		self.edit.setPlainText('')
		self.edit.insertPlainText('Encrypting ini files\n')
		self.edit.insertPlainText('------------------------------\n')
		for root, dirs, files in os.walk(self.lastDirectory):
			self.edit.insertPlainText('Enter directory: %s\n' % root)
			for name in files:
				myName, ext = os.path.splitext(name)
				if ext.lower() != '.ini': continue
				if not myName.endswith(self.Magic): continue

				fileName = os.path.join(root, name)
				with open(fileName, 'r') as fp:
					data = fp.read()
					try:
						data = PokerStarsIniDecrypter.encryptString(data)
					except PokerStarsIniDecrypter.Error, d:
						self.edit.insertPlainText('Error: could not encrypt: %s\n' % name)
						continue

				myName = myName[:len(myName)-len(self.Magic)] + ext
				fileName = os.path.join(root, myName)
				with open(fileName, 'wb') as fp:
					fp.write(data)
				self.edit.insertPlainText('Encrypted: %s --> %s\n' % (name, myName) )
		self.edit.insertPlainText('Done\n')

	def onEncryptDirectory(self, checked=False):
		dlg = QtGui.QFileDialog(self)
		dlg.setWindowTitle('Chosse directory to enecrypt ini files..')
		dlg.setFileMode(dlg.Directory)
		dlg.restoreState( Tc2Config.settingsValue(self.SettingsKeyDialogEncryptState, QtCore.QByteArray()).toByteArray() )
		if dlg.exec_() == dlg.Rejected:
			return
		Tc2Config.settingsSetValue(self.SettingsKeyDialogEncryptState, dlg.saveState() )

		directory = dlg.directory().canonicalPath()
		directory = directory.toUtf8()
		directory = unicode(directory, 'utf-8')
		self.lastDirectory = directory
		self.onEncrypt()
		self.adjustActions()

#************************************************************************************
#
#************************************************************************************
if __name__ == '__main__':
	import sys
	application = QtGui.QApplication(sys.argv)
	gui = FrameTool()
	gui.show()
	application.exec_()
















