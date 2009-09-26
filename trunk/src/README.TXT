additional hotkeys for PokerStars and more

WARNING: this thing is pretty alpha - so use at your own risk

--------------------------
features:
--------------------------

- configurable hotkeys for table actions like fold, check, raise, alter bet amount, show replayer
- auto-close popup news
- move mouse to table that requires attention
- configurable hotkeys for PokerStars replayer

---------------------------
usage:
---------------------------

linux:
1. install wine
2. install the windows version of python (>= 2.6) from [http://python.org/download/]
3. create your config file (see User/default.cfg) for details
4. run from commandline: 
    >> wine pathTo/pythonw.exe pathTo/Cli.py pathTo/my.cfg
	
	in case an error occurs a report should be written to User/errlog.txt. please include
	this file in any failure reports

win32:
- not tested, but may work as expected


--------------------------
notes:
--------------------------

- wine specific: if "Allow the window manager to control the windows" is set to False, the foreground 
   window may not always be the active window. and because the hotkeys implemented here work 
   only on the currently active window they may not work.
    
 - wine specific: on my ubuntu box wine took the first keyboard layout it could get a hold on. had
    to remove US keyboard layout to get wine to use the desired german one.

- wine specific: wine does not record all keyboard keys systemwide. there is no way to know
   the state of CAPITAL, NUMLOCK and SCROLLOCK keys. for compatibility these keys are always 
   ignored - on wine and on native win32.

-------------------------
version history:

-----------------------------
0.2.1
-----------------------------
news:
changes:
fixes:
    - it was not possible to reasign PokerStars replayer as table via hotkey. this is fixed now 

-----------------------------
0.2.0
-----------------------------
news:
    - configurable hotkeys fror PokerStars replayer

changes:
    - table hotkeys: assigned more sensible defaults. see User/default.cfg

fixes:


-----------------------------
0.1.1 bugfix release
-----------------------------
news:
changes:
fixes:
     - supplying custom cofig via commandline did not work: fixed


--------------------------
0.1.0 initial release
--------------------------
news:
changes:
fixes:

