

------------------------------------------------------------------------------------------------------------------------------------
issues
------------------------------------------------------------------------------------------------------------------------------------

- wine: dfault GUI font may or may not not contain bold. adjust font (Tahoma, if installed, works)
- size grip is not working on windows due to a bug in Qt (QTBUG-5566). so size grip is disabled wherever possible. but some dialogs can nit be adjusted
- wine? i found that scrolling upwards via MouseWheel in QScrollArea is not working
- since setting application style we get "Could not parse application stylesheet" messages. no idea why


------------------------------------------------------------------------------------------------------------------------------------
running TableCrab from the sources
------------------------------------------------------------------------------------------------------------------------------------

this is for linux only. it seems to be a pain setting up subversion on windows. 


1) install python >= 2.6 binary [ http://www.python.org/download/ ] or use winetricks to do so
2) install Qt4 >= 4.6 windows binary [ http://qt.nokia.com/downloads/downloads#lgpl ]
3) install PyQt4 windows binary matching your python version [ http://www.riverbankcomputing.co.uk/software/pyqt/download ]
	for python 2.6 for example it's "PyQt-Py2.6-gpl-4.7.4-1.exe"

locate the python executable under wine "pythonw.exe". a good place to look for is in "/home/UserName/.wine/drive_c/python26"

now run from commandline:

>> wine /pyth/to/pythonw.exe  /path/to/my/TableCrabFolder/TableCrabGui.py


------------------------------------------------------------------------------------------------------------------------------------
compiling TableCrab from the sources
------------------------------------------------------------------------------------------------------------------------------------

PyInstaller worked wuite nicely, but i had to patch it to make it work under wine. no idea if it compliles
on native windows without problems.

on wine PyInstaller it when trying to access a temporary file it created. so i had to replace
the function exec_statement() in "PyInstaller.hooks.hookutils.py" with the following one

def exec_statement(stat):
    if stat == 'from PyQt4.QtCore import QCoreApplication; app=QCoreApplication([]); print map(unicode,app.libraryPaths())':
        from PyQt4.QtCore import QCoreApplication
        app=QCoreApplication([])
        return repr( map(unicode, app.libraryPaths()) )
    elif stat == "import xml;print xml.__file__":
        # we don't need xml, so make PyInstaller ignore it
		return ''
    raise ValueError('hack no longer working: %s' % stat)

see: http://www.pyinstaller.org/ticket/199


NOTES:
- you have to use PyInstaller from trunk
    svn co http://svn.pyinstaller.org/trunk pyinstaller-trunk /path/to/My/Dir
- you must install the msi version of Python. installing the python version python from winetricks failed on a missing Microsoft.VC90.CRT
   assembly. micros~1 at its best.








