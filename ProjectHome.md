yet another `PokerStars` hotkey manager - written in python

the program is developed and tested on linux/wine and runs well on windowsXP and other flavors of windows.

features:
  * configurable hotkeys for common table actions like check, fold, raise, bet pot (...)
  * resize tables via hotkey
  * block popup news
  * built in hand viewer and hand history file browser for all common poker variants (holdem, omaha, stud, draw, ..)
  * FPP calculator
  * fetch icm nash calculations from [HoldemResources.net](http://www.HoldemResources.net)
  * card protector to cover pocket cards in training sessions
  * tool to evaluate hand ranges against flops
  * tool for training board card reading
  * (..)

get the newest release from the Donwloads section, unzip and run `TableCrab2-xxx.exe`. if you have any questions, hints ... feel free to post at `TableCrabs` 2+2 thread: `[`http://forumserver.twoplustwo.com/45/software/tablecrab2-pokerstars-hotkeys-linux-windows-855744`]`


---

**News: `TableCrab2-0.8.4` released**


---

**Donate:** if you want to support this project feel free to send some [bitcoins](http://blockchain.info/) to the following address: 1Ga8ftNuuiuMdk62YEFotA4K19VKEGEZCB


---


Some screenshots of `TableCrab` in action
|![http://tablecrab.googlecode.com/svn/trunk/web/TC-screen-2.png](http://tablecrab.googlecode.com/svn/trunk/web/TC-screen-2.png)| ![http://tablecrab.googlecode.com/svn/trunk/web/TC-screen-3.png](http://tablecrab.googlecode.com/svn/trunk/web/TC-screen-3.png)| ![http://tablecrab.googlecode.com/svn/trunk/web/TC-screen-1.png](http://tablecrab.googlecode.com/svn/trunk/web/TC-screen-1.png)|
|:------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------|


---

### `TableCrab` does not run on my windows! ###

---

..or you prefer to run `TableCrab` from its sources.

to do so you can always install the components `TableCrab` is based upon and then run it from its source code following these instructions:

  1. download and unpack the source release of `TableCrab` `(TableCrab2-xyz-src.zip)` to a directory of your choice.
  1. install python from here: http://python.org/download/. you need the 2.6 or 2.7 windows installer (not 3.x!).
  1. install `PyQt4` from here: http://www.riverbankcomputing.co.uk/software/pyqt/download. you need the windows installer according to the python version you installed. if you installed python 2.7 you need `PyQt4-Py2.7-xyz.exe`.
  1. install `numpy` and `PyQwt` from this page: http://www.lfd.uci.edu/~gohlke/pythonlibs
  1. now locate a file named _pythonw.exe_ in your file system. usually it is to be found in _c:\Python26_ or _c:\Python27_ according to the python version you installed. `TableCrab` has to be run through this executable.
  1. back to the _`TableCrab2-xyz`_ directory you unzipped _`tableCrab`_ to. locate _`Tc2Gui.py`_ and create a link to it. edit the link and prefix the path to _`Tc2Gui.py`_ with the path you found _pythonw.exe_ at. the commandline for the link should now look like this: _`c:\Python27\pythonw.exe "path\to\TableCrab2-xyz\Tc2Gui.py"`_

if everything went well you should now be able to run `TableCrab` from its source code instead of running it from the executable.


---

### FAQ ###

---



### Why must `TableCrab` be run on wine under linux? ###

`TableCrab` is a windows application for the fact that..
  1. most (all?) poker sites run windows
  1. it is easier to play tricks on the sites in windows environments

site policy may change and so may `TableCrab`.



---

### Other stuff ###

---

Currently i am working on a side project: `HandHistoryCrab` https://code.google.com/p/hand-history-crab/ a python package for parsing hand history files. feel free to test, comment, contribute or report bugs.




