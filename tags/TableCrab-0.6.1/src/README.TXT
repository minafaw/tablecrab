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
- PokerStars instant hand history grabber

==============================================================================
USAGE
==============================================================================

-----------------------------------------------
1a) install and run on linux/wine
-----------------------------------------------
1. install wine
2. install the windows version of python (>= 2.6) from [http://python.org/download/] or use "wintricks" to do so
3. create your config file (see User/default.cfg) for details
4. run from commandline: 
    >> wine pathTo/pythonw.exe pathTo/TableCrab/Cli.py pathTo/my.cfg
	
	
---------------------------------------------
1b) install and run on windows
---------------------------------------------
WARNING: nothing is tested on windows, so things may or may not work as expected

1. install the windows version of python (>= 2.6) from [http://python.org/download/]
2. create your config file (see User\default.cfg) for details
3. run from commandline: 
    >> pathTo\pythonw.exe pathTo\TableCrab\Cli.py pathTo\my.cfg


..next is configuring TableCrab through "User/default.cfg". you best make adjustenents in your own newly created config and use 
default.cfg as lookup.

-------------------------------------
2) setup tables
-------------------------------------
TableCrab is most likely is not working out of the box. you have to adjust its config (TableCrab/User/default.cfg).
to get table hotkeys working you have to tell TableCrab what size your table(s) are and what points to click inside the tables.
the best way to do so i found was taking a scrennshot of a table and load it into an image editor. the size of the screenshot
image obviously is the size of the table. your image editor hopefuly shows the coordinates of the cursor, so it should be easy
to locate the points to click for buttons like "fold", "call" (...). from these coordinates you have to subtract the height title bar
and width the borders because TableCrab assumes them to be in coordinates relative to the client area of the window. that
is the window without borders and title bar.

note that TableCrab only works on tables having exactly the size you specified. so best use PokerStars custom layouts to
remember and restore tables to the specified sizes.

-------------------------------------
3) configure hotkeys
-------------------------------------
TableCrab has preconfigured hotkeys you may change at any time. to do so take a look at "key-report-keyboard" in "default.cfg".
hit this key combination when the PokerStars client is in the foreground. untill you hit that key again TableCrab will report
any key combination pressed. something like:

Cli:keyPressed key=F LCONTROL

hitting left control key and the "F" key simultaniously.  "F LCONTROL" is the hotkey we may want copy into our config. 

------------------------------------------------
4) in case something goes wrong
-----------------------------------------------
TableCrab may crash. please report. there is a file "errlog.txt" in every User directory conatining potentially useful information.
please include this file in any failure reports



==============================================================================
ADD ONS
==============================================================================
TableCrab comes equipped with some additional tools described here

----------------------------------------------
PokerStars hand history grabber
----------------------------------------------
PokerStars hand replayer is not very handy. so i coded a grabber for its "instant hand history". the grabber will dump the current hand
as a html file to a directory of your choice. set your favourite browser to reload this file at certain intervals, assign a hotkey in TableCrab
to update "instant hand history" and you get a nicely formatted overview of a hand how it played out.

usage: wine pathTo/pythonw.exe pathTo/TableCrab/Scripts/PokerStarsHandHistoryGrabber.py pathTo/my.cfg

for the default config take a look at TableCrab/Scripts/User/PokerStarsHandHistoryGrabber.cfg


----------------------------------------------
generating developer docs
----------------------------------------------
if you are a python developer you may be interested in the source code documentation. format used is epydoc, so you may have to install
epydoc. and for me being lazy i wrote a script that generates the documentation and dumps it to TableCrab/Doc/Devel. 

usage (no wine required this time): python path/to/TableCrab/Scripts/GenDevelDocs.py 


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

- on ubuntu lucid resizing of tables does not work (no idea why so far). so you have to make use of PokerStars custom layouts

-------------------------
windows
--------------------------

none so far


==============================================================================
FAQ
==============================================================================

why does TableCrab need to be run through wine?
   
   everything TableCrab does could be done running easily on linux aswell - except two things:
        1) retrieving the contents of child widgets
        2) setting them

    as an example: alter the current bet amount. this is easily done on win32 (get editbox text --> alter it --> dump it back
    to the editbox). on linux on the other han the contents of the box would have to be screenscraped, that is messing around
    with some sort of optical char recognition. not a thing you want to do unless you absolutely have to.


TableCrab is not easy to use - why?
	
	1) because you most likely run linux and linux has to be pain
	2) i am too lazy to write a nice an user friendly GUI. i'd rather kick PokerStars butts to implement all these features into their client
		where they belong


==============================================================================
VERSION HISTORY
==============================================================================

----------------------------
0.7.1a - test version
-----------------------------
fixes:
	- an invalid method call TableCrab stopped TableCrab from working at the tables, this is fixed now

----------------------------
0.7.0a - test version
-----------------------------
news:
	- popup news got only closed in the lobby - they will now get closed anywhere
	- new flag in TableCrab config: bool-auto-ok-tourney-registration-message-boxes . this will automatically hit 'OK' in all 'Tourney Registration' dialogs popping up 
		WARNING: this feature is	experimental. use at you own risk
	- new flag in TableCrab config: bool-auto-ok-table-message-boxes . this will automatically hit 'OK' in all message boxes popping up on tables. WARNING: this feature is
		experimental. use at you own risk

fixes:
	- PokerStarsHandHistoryGrabber.py: 
		° in generated Html table cell borders are now adjusted via Css. you may have to adjust your Css to make the hand history look like expected

----------------------------
0.6.0
-----------------------------
news: 
	- 
fixes:
	- PokerStarsHandHistoryGrabber.py: 
		° utf-8 encoding and proper escaping for generated html

new:
	- PokerStarsHandHistoryGrabber.py: 
			° added "playerActionPostBlindBig", "playerActionPostBlindSmall", "cards" and "cardCell" as CSS properties
			° added support for bet amount postfixes
			° you can dump Omaha hand histories now aswell
			° the script now has a real config. it is located in Scripts/User. usage: wine path/to/pythonw.exe path/to/PokerStarsHandHistoryGrabber.py path/to/your/config.cfg
			
-----------------------------
0.5.0
-----------------------------
news:
    - you can now assign a hotkey to update instand hand history
	- added a standalone script to grab PokerStars instant hand history and dump it to a nicely formatted html file
changes:
fixes:
	- on ubuntu lucid resizing of tables does not work (maybe due to some kernel update, no idea) and breaks TableCrab.
	  fixed it so TableCrab does not break, but to resize tables to a desired size you may have to use PokerStars custom layouts


-----------------------------
0.4.0
-----------------------------
news:
    - you can now alter bet amount with a base value of 'x'. this makes it possible for example to 2 1/2x the current value in the bet amount box
changes:
fixes:

----------------------------
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

