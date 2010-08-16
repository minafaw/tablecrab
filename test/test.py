
import os, sys, unittest
from PyQt4 import QtCore, QtGui

DirSelf = os.path.dirname(os.path.abspath(__file__))
DirSrc = os.path.dirname(DirSelf)
sys.path.insert(0, DirSrc)
CfgFileName = os.path.join(DirSelf,'test.ini')
# make shure config file does not exists to start clean
if os.path.isfile(CfgFileName):
	os.remove(CfgFileName)

#***************************************************************************************
# global objects
#***************************************************************************************
klassGui = None
gui = None
qApp = QtGui.qApp
class _QSettings(QtCore.QSettings):
	def __init__(self):
		QtCore.QSettings.__init__(self, CfgFileName, QtCore.QSettings.IniFormat)
		def setValues(**kws):
			for key, value in kws.items():
				self.setValue(key, QtCore.QVariant(value))
qSettings = _QSettings()

# decorator that records method names to support tests in compile time order
class Test(object):
	def __init__(self):
		self.methodNames = []
	def __call__(self, func):
		self.methodNames.append(func.__name__)
		return func

#***************************************************************************************
# tests
#***************************************************************************************
class TestAll(unittest.TestCase):

	test = Test()

	def setUp(self):
		qApp.processEvents()
		qSettings.clear()

	def tearDown(self):
		qApp.processEvents()


	@test
	def test_configFileNameNotExists(self):
		sys.argv.append('--config')
		sys.argv.append(CfgFileName)
		self.assertRaises(ValueError, __import__, 'src.TableCrabGui')

	@test
	def test_configFileName(self):
		# ..create config file
		sys.argv.append('--config')
		sys.argv.append(CfgFileName)
		open(CfgFileName, 'w').close()
		from src import TableCrabConfig
		self.assertEqual(TableCrabConfig.qSettings.format(), qSettings.IniFormat)
		self.assertEqual( os.path.normpath( unicode(TableCrabConfig.qSettings.fileName(), 'utf-8')), CfgFileName)
		# init gui
		from src import TableCrabGui
		global klassGui,gui
		klassGui = TableCrabGui.Gui
		gui = klassGui()
		gui.show()

	@test
	def test_SingleApplication(self):
		self.assertRaises(RuntimeError, klassGui)

#***************************************************************************************
# unittest
#***************************************************************************************
def test():
	# run tests
	testClasses = [
			TestAll,
			]
	for testClass in testClasses:
		runner = unittest.TextTestRunner()
		suite = unittest.TestSuite()
		tests = map(testClass, testClass.test.methodNames)
		suite.addTests(tests)
		runner.run(suite)
	# clean up
	gui.close()
	#TODO: config file gets not removed. no idea why
	if os.path.isfile(CfgFileName):
		os.remove(CfgFileName)


if __name__ == '__main__':
	test()



