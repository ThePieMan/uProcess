uProcess
========

a tiny python post processor for uTorrent

About:
---------
I (edit: that is to say, **@jkaberg**) initially made uProcess to be a "learn by doing" project, but has this far been proven a good utility to automate downloads using uTorrent. Feel free to fork me, make changes and what not :-)

With uProcess you can achieve the same "seamless" experience as SABnzbd + CouchPotato + Sick-Beard

Features:
---------
- Extract downloaded content - [List of supported archives](http://www.rarlab.com/otherfmt.htm "List of supported archives")
- Move, copy or (hard)link files that doesn't need extraction
- Delete torrents which achieved certain ratio
- Ignore torrents containing a "blacklisted" label
- Multi OS compatible (Windows, Linux, OSX)
- Optionally calls CouchPotato or Sick-Beard when done (for additional post-processing)

Requirements:
---------
- uTorrent
    - [uTorrent 2.2.1 Build 25302](http://www.oldapps.com/utorrent.php?old_utorrent=8134), or;
    - [uTorrent 3.0 Build 25824](http://www.oldapps.com/utorrent.php?old_utorrent=6795) are both confirmed working
- uTorrent Web UI activated
- [Python 2.7](http://www.python.org/download/releases/2.7/ "Python 2.7")

Good to know:
---------
- For uProcess to be able to send torrents containing movies to CouchPotato or series to Sick-Beard you need to match the torrent label you set in CouchPotato/Sick-Beard with the one's you set in config.cfg (eg. in Couchpotato you set label to "movie" in the uTorrent downloader, then in the config.cfg under [Couchpotato] where it says label =, make it so: label = movie)
- Hardlink doesn't work cross partition/hard drive, use the copy or move option instead
- uProcess ONLY works with uTorrent as its heavily dependant on uTorrents Web UI API
- Although uProcess was initially programmed on Windows 8, it should work on most platforms
- **This branch may be poorly maintained**

Usage:
---------
- Make sure you've installed uTorrent and Python correctly
- Grab uProcess [here](https://github.com/ThePieMan/uProcess/archive/master.zip "here")
- Extract uProcess to any location
- Setup uTorrent to use Web UI (Options->Preferences->Advanced->Web UI), note down user/password and listening port
- Edit the config.cfg file in C:\Downloaders\uProcess to your preferences
- Goto uTorrent again, in Options->Preferences->Advanced->Run Program, where it says "run this program when torrent finishes" add: C:\Python27\pythonw.exe C:\Downloaders\uProcess\uProcess.py "%D" "%I"

NOTE: In the above example I'm assuming uProcess being extracted to C:\Downloaders\uProcess and Python 2.7 installed to its default location, C:\Python27

Not working!?
---------
- First off, check the log file located in the uProcess directory (make sure you set debug = true in config.cfg, and then run uProcess again)
- If that didn't help, create an ticket over at the [issue tracker](https://github.com/ThePieMan/uProcess/issues "issue tracker")
