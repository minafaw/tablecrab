
this folder contains a bare bones PokerStars themes modding engine.

every image in the "StarsMods" folder is copied to its according location in the PokerStars folder.
so for example place "PokerStars/Gx/fg.bmp" in the folder, mod it and run "python/Cli.py"
to dump the file to the PokerStars directory, after the client has been started.

usage: python Cli.py path/to/PokerStarsExeFolder [path/to/folder/containing/mods]

if you have python imaging library installed you can use "AlphaBitmapsToGrayscale.py" to recursively convert
all alpha bitmaps in a folder to grayscale

usage: python AlphaBitmapsToGrayscale.py [path/to/folder/containing/bitmaps]


NOTES:
PokerStars by default updates the client at every restart if you applied mods, overwriting all mods in the process. 
you may have to run Cli.py everytime emidiately following the update. 








