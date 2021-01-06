:: The creation of the batch file is optional. If you intend to use the script everyday then this batch file is handy if turned into a shortcut.
:: To make a shortcut for the batch file: https://winaero.com/pin-a-batch-file-to-the-start-menu-or-taskbar-in-windows-10/
:: To change the icon of the created shortcut: https://www.computerhope.com/issues/ch001820.htm (NOTE: you can download your own .ico file, or convert .png -> .ico, and choose that instead of the default icons provided)

START "C:\Users\USERNAME\AppData\Roaming\Spotify\Spotify.exe"  
:: For above: replace and give location of the Spotify.exe itself. 
:: Spotify is started when this executable is ran.

@echo off
python C:\Users\USERNAME\main.py %* 
:: For above: replace and give location of python file. 
:: The script is now running.
pause
