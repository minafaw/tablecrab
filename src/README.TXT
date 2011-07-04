TableCrab - Hotkeys for PokerStars and more


------------------------------------------------------------------------------------------------------------------------------------
running TableCrab from the sources
------------------------------------------------------------------------------------------------------------------------------------

this is for linux only. it seems to be a pain setting up subversion on windows.


1) install python >= 2.6 binary [ http://www.python.org/download/ ] or use winetricks to do so
2) install PyQt4 windows binary matching your python version [ http://www.riverbankcomputing.co.uk/software/pyqt/download ]
	for python 2.6 for example it's "PyQt-Py2.6-gpl-4.7.4-1.exe"
3) grab a fresh copy of TableCrab from its repository via svn export or copy: svn export http://tablecrab.googlecode.com/svn/trunk/src /path/to/my/TableCrabFolder/


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

------------------------------------------------------------------------------------------------------------------------------------
issues
------------------------------------------------------------------------------------------------------------------------------------

- wine: default GUI font may or may not not contain bold. adjust font (Tahoma, if installed, works)
- size grip is not working on windows due to a bug in Qt (QTBUG-5566). so size grip is disabled wherever possible. but some dialogs can nit be adjusted
- wine? i found that scrolling upwards via MouseWheel in QScrollArea is not working
- since setting application style we get "Could not parse application stylesheet" messages. no idea why

-----------------------------------------------------------------------------------------------------------------------------------
FAQ
-----------------------------------------------------------------------------------------------------------------------------------
why has TableCrab to be run on windows (wine)?

first late me state that TableCrab running on windows is a side effect, not a goal. it is developed
on linux/wine and the focus is on making it run in this environment. so why wine then instead
of say, X11? mainly because the more insecure windwos platform allows more tricks to be
played with other peoples widgets. some fearures of TableCrab would be very hard to
implement on native linux. add to this the fact that most poker clients run windows AND
that the focus is on PokerStars wich is very easy to extend in functionality via win32 methods,
i think this is a good decission, being lazy and all.


why not support multiple platforms?

..when python code could be easily extended to handle multiple platforms. i thought this
over and came to the conclusion that it's not worth the efford. i may be wrong, but imo
we'd either loose features and/or spend way too much time on thinking how to abstact
subtle platform differences away that maybe even a rewrite from scratch could easily be
done in less time and with less brain cell melting. imo a better way would be to simplify
TableCrab in a way that makes a rewrite an easy task.


why not support sites other than PokerStars?

first of all, with the focus being on linux/wine, only sites that run on this platform are
candidates. FullTilt is somewhat close to this .and maybe other sites i am not aware of.
taking FullTilt as an example, the client is implemented in Qt with the effect that many
win32 methods do not work on it. so this could be a candidate to implement a pure linux
version of TableCrab.




