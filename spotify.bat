:: The creation of the batch file is optional. If you intend to use the script everyday then this batch file is handy if turned into a shortcut.

START "C:\Users\name\AppData\Roaming\Spotify\Spotify.exe"  
:: For above: replace and give location of the Spotify.exe itself. 

@echo off
python C:\Users\name\main.py %* 
:: For above: replace and give location of python file. 
pause
