additional hotkeys for PokerStars (and more)

WARNING: this programm is pretty alpha - use at your own risk


the program is written in python with the main intention to to add custom hotkeys to PokerStars when running
a PokerStars client in linux/wine. the programm must be run in wine (or native win32 environment, see USAGE)
and requires python >= 2.6 as interpreter.


==============================================================================
FEATURES
==============================================================================

- configurable hotkeys for table actions like fold, check, raise, alter bet amount, show replayer
- auto-close popup news
- move mouse to table that requires attention
- configurable hotkeys for PokerStars replayer


==============================================================================
USAGE
==============================================================================

-------------------------
linux/wine
-------------------------
1. install wine
2. install the windows version of python (>= 2.6) from [http://python.org/download/]
3. create your config file (see User/default.cfg) for details
4. run from commandline: 
    >> wine pathTo/pythonw.exe pathTo/Cli.py pathTo/my.cfg
	
	
--------------------------
windows
--------------------------
WARNING: nothing is tested on windows, so things may or may not work as expected

1. install the windows version of python (>= 2.6) from [http://python.org/download/]
2. create your config file (see User\default.cfg) for details
3. run from commandline: 
    >> pathTo\pythonw.exe pathTo\Cli.py pathTo\my.cfg


in case an error occurs a report should be written to User/errlog.txt. please include this file in any failure reports

==============================================================================
NOTES
==============================================================================

--------------------------
linux/wine
--------------------------

- if "Allow the window manager to control the windows" is set to False, the foreground  window may not 
   always be the active window. and because the hotkeys implemented here work only on the currently active window 
   they may not work.
    
 - on my ubuntu box wine took the first keyboard layout it could get a hold on. had to remove US keyboard 
   layout to get wine to use the desired german one.

- wine does not record all keyboard keys systemwide. there is no way to know the state of CAPITAL, NUMLOCK
   and SCROLLOCK keys. for compatibility these keys are always ignored - on wine and on native win32.

- maybe stating the obvious ..but note that keys will only be captured when a "wine window" has the keyboard
  focus. same goes for window events: they will only be captured if a "wine window" is affected.

-------------------------
windows
--------------------------


==============================================================================
VERSION HISTORY
==============================================================================

-----------------------------
0.3.0
-----------------------------
news:
    - bet amount at table can be altered now via mouse wheel
changes:
fixes:
    - sometimes the client failed because it could not retrieve the class name of a window. this is hopefuly fixed now


-----------------------------
0.2.1
-----------------------------
news:
changes:
    - for some reason "move mouse to active table" stoped working as expected with (my) latest ubuntu upgrade, so the 
	  mouse pointer is now placed relative to the client area of the window and it is possible to specify an offset to fine tune 
      its positioning.
fixes:
    - it was not possible to reasign PokerStars replayer as table via hotkey. this is working now as expected


-----------------------------
0.2.0
-----------------------------
news:
    - configurable hotkeys fror PokerStars replayer

changes:
    - table hotkeys: assigned more sensible defaults. see User/default.cfg

fixes:


-----------------------------
0.1.1
-----------------------------
news:
changes:
fixes:
    - supplying custom cofig via commandline did not work: fixed


-----------------------------
0.1.0 initial release
----------------------------
news:
changes:
fixes:

