# dascraper

##A Gallery Scraper for DeviantArt

All images are downloaded to a folder on your desktop. Feel free to move them after the download is complete, but the tool won't know
  that you've moved them. 

Although the tool is very fast, downloading large galleries can take some time. The tool will print 'Finished' to
  the console window to let you know when it's done. I've tested with galleries 200-300 images in size and it takes around a minute.
  However if the gallery images are high quality this can be increased dramatically.

If there is an error downloading, and the download is interrupted, you'll have to start the process again. 

If you like the tool and want to add to it, just let me know.

######To use:######
  1. Download the .exe file.
  2. Open up your favourite command-line tool (e.g. PowerShell on Windows, or Terminal on Mac)
  3. Run ./scraper.exe *artistname* where *artistname* is the lower-case name of the Deviant.

######Optional:######
  If you only want to download images from a certain page onwards (e.g. from page 2 to last) supply an additional integer argument
in the command line. For example running ./scraper.exe crow-god 2 will download all images from Crow-God's gallery from page 2 onwards.
