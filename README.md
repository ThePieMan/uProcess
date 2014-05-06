uProcess
========

a tiny python post processor for uTorrent

About:
---------
I initially made uProcess to be a "learn by doing" project, but has this far been proven a good utility to automate downloads using uTorrent. Feel free to fork me, make changes and what not :-)

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
- [uTorrent 2.2.1 Build 25302](https://www.google.com/webhp?sourceid=chrome-instant&ion=1&ie=UTF-8#sclient=psy-ab&q=uTorrent+2.2.1+Build+25302&oq=uTorrent+2.2.1+Build+25302&gs_l=serp.12..0l2j0i30l2.6844.6844.0.8160.1.1.0.0.0.0.69.69.1.1.0...0.0...1c.1.14.psy-ab.ZcSwjn9xAbA&pbx=1&fp=1&biw=1920&bih=955&ion=1&bav=on.2,or.r_cp.r_qf.&cad=b
 "uTorrent 2.2.1 Build 25302")+ (confirmed), might work on earlier versions
- uTorrent Web UI activated
- [Python 2.7](http://www.python.org/download/releases/2.7/ "Python 2.7")

Good to know:
---------
- For uProcess to be able to send torrents containing movies to CouchPotato or series to Sick-Beard you need to match the torrent label you set in CouchPotato/Sick-Beard with the one's you set in config.cfg (eg. in Couchpotato you set label to "movie" in the uTorrent downloader, then in the config.cfg under [Couchpotato] where it says label =, make it so: label = movie)
- Links doesn't work cross partition/hard drive, use the copy or move option instead
- uProcess ONLY works with uTorrent as its heavily dependant on uTorrents Web UI API
- Although uProcess was initially programmed on Windows 8, it should work on most platforms

Usage:
---------
- Make sure you've installed uTorrent and Python correctly
- Grab uProcess [here](https://github.com/jkaberg/uProcess/archive/master.zip "here")
- Extract uProcess to any location
- Setup uTorrent to use Web UI (Options->Preferences->Advanced->Web UI), note down user/password and listening port
- Edit the config.cfg file in C:\Downloaders\uProcess to your preferences
- Goto uTorrent again, in Options->Preferences->Advanced->Run Program, where it says "run this program when torrent finishes" add: C:\Python27\pythonw.exe C:\Downloaders\uProcess\uProcess.py "%D" "%I"

NOTE: In the above example I'm assuming uProcess being extracted to C:\Downloaders\uProcess and Python 2.7 installed to its default location, C:\Python27

Not working!?
---------
- First off, check the log file located in the uProcess directory (make sure you set debug = true in config.cfg, and then run uProcess again)
- If that didn't help, create an ticket over at the [issue tracker](https://github.com/jkaberg/uProcess/issues "issue tracker")
