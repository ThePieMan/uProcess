#!/usr/bin/env python

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    
#    Creator of uProcess: jkaberg, https://github.com/jkaberg

import os
import sys
import shutil
import time
import logging
import urllib
import traceback
import ConfigParser

from utorrent.client import UTorrentClient
import pyUnRAR2
from pyUnRAR2.rar_exceptions import *

class AuthURLOpener(urllib.FancyURLopener):
    def __init__(self, user, pw):
        self.username = user
        self.password = pw
        self.numTries = 0
        urllib.FancyURLopener.__init__(self)

    def prompt_user_passwd(self, host, realm):
        if self.numTries == 0:
            self.numTries = 1
            return (self.username, self.password)
        else:
            return ('', '')

    def openit(self, url):
        self.numTries = 0
        return urllib.FancyURLopener.open(self, url)

def createLink(src, dst):
    try:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.CreateHardLinkW(dst, src, 0)
        else:
            os.link(src, dst)
    except Exception, e:
        logger.error(loggerHeader + "Linking failed: %s %s", (e, traceback.format_exc()))

def processMedia(mediaProcessor, output_dest):
    if mediaProcessor == "couchpotato":
        try:
            baseURL = config.get("Couchpotato", "baseURL")
            if not baseURL == '':
                logger.debug(loggerHeader + "processMedia :: URL base: %s", baseURL)
        except ConfigParser.NoOptionError:
            baseURL = ''

        if config.getboolean("Couchpotato", "ssl"):
            protocol = "https://"
        else:
            protocol = "http://"
        url = protocol + config.get("Couchpotato", "host") + ":" + config.get("Couchpotato", "port") + "/" + baseURL + "api/" + config.get("Couchpotato", "apikey") + "/renamer.scan/?async=1&movie_folder=" + output_dest
        myOpener = AuthURLOpener(config.get("Couchpotato", "username"), config.get("Couchpotato", "password"))

    elif mediaProcessor == "sickbeard":
        try:
            baseURL = config.get("Sickbeard", "baseURL")
            if not baseURL == '':
                logger.debug(loggerHeader + "processMedia :: URL base: %s ", baseURL)
        except ConfigParser.NoOptionError:
            baseURL = ''

        if config.getboolean("Sickbeard", "ssl"):
            protocol = "https://"
        else:
            protocol = "http://"
        url = protocol + config.get("Sickbeard", "host") + ":" + config.get("Sickbeard", "port") + "/" + baseURL + "home/postprocess/processEpisode?quiet=1&dir=" + output_dest
        myOpener = AuthURLOpener(config.get("Sickbeard", "username"), config.get("Sickbeard", "password"))
    else:
        return

    try:
        urlObj = myOpener.openit(url)
        logger.debug(loggerHeader + "processMedia :: Opening URL: %s", url)
    except Exception, e:
        logger.error(loggerHeader + "processMedia :: Unable to open URL: %s %s %s", (url, e, traceback.format_exc()))
        raise

    result = urlObj.readlines()
    for line in result:
        logger.debug(loggerHeader + "processMedia :: " + line)

    # This is a ugly solution, we need a better one!!
    timeout = time.time() + 60*2 # 2 min time out
    while os.path.exists(output_dest):
        if time.time() > timeout:
            logger.debug(loggerHeader + "processMedia :: The destination directory hasn't been deleted after 2 minutes, something is wrong")
            break
        time.sleep(2)

def main(tr_dir, tr_hash):

    search_ext = tuple((config.get("Miscellaneous", "media") + config.get("Miscellaneous", "meta") + config.get("Miscellaneous", "other")).split('|'))
    archive_ext = tuple((config.get("Miscellaneous", "compressed")).split('|'))
    if not (search_ext or archive_ext):
        logger.error(loggerHeader + "Missing extensions in the config file")
        sys.exit(-1)

    ignore_words = (config.get("Miscellaneous", "ignore")).split('|')
    if not ignore_words:
        ignore_words = ''

    ignore_label = (config.get("uProcess", "ignoreLabel")).split('|')
    if not ignore_label:
        ignore_label = ''

    cp_label = (config.get("Couchpotato", "label")).split('|')
    if not cp_label:
        cp_label = ''

    sb_label = (config.get("Sickbeard", "label")).split('|')
    if not sb_label:
        sb_label = ''

    file_action = config.get("uProcess", "fileAction")
    delete_finished = config.getboolean("uProcess", "deleteFinished")
    delete_ratio = config.getint("uProcess", "deleteRatio")
    uTorrentHost = "http://" + config.get("uTorrent", "host") + ":" + config.get("uTorrent", "port") + "/gui/"

    try:
        uTorrent = UTorrentClient(uTorrentHost, config.get("uTorrent", "username"), config.get("uTorrent", "password"))
    except Exception, e:
        logger.error(loggerHeader + "Failed to connect to uTorrent: %s", (uTorrentHost, e, traceback.format_exc()))

    if uTorrent:
        foundTorrent = False

        status, torrents = uTorrent.list()  # http://www.utorrent.com/community/developers/webapi#devs6
        for torrent in torrents['torrents']:
            if torrent[0] == tr_hash:     # hash
                tr_name = torrent[2]      # name
                tr_progress = torrent[4]  # progress in mils (100% = 1000)
                tr_ratio = torrent[7]     # ratio in mils (1.292 ratio = 1292)
                tr_label = torrent[11]    # label
                foundTorrent = True

                logger.debug(loggerHeader + "Torrent Directory: %s", tr_dir)
                logger.debug(loggerHeader + "Torrent Name: %s", tr_name)
                logger.debug(loggerHeader + "Torrent Hash: %s", tr_hash)

                if tr_label:
                    logger.debug(loggerHeader + "Torrent Label: %s", tr_label)
                else:
                    tr_label = ''

                output_dest = os.path.join(config.get("uProcess", "outputDirectory"), tr_label, tr_name)

                status, data = uTorrent.getfiles(tr_hash) # http://www.utorrent.com/community/developers/webapi#devs7
                hash, files = data['files']
                if not any(word in tr_label for word in ignore_label):
                    if tr_progress == 1000:
                        for file in files:
                            fileName, fileSize, downloadedSize = file[:3]
                            fileName = fileName.lower()

                            # Check if tr_dir has been passed as a directory or file
                            if os.path.isfile(tr_dir):
                                input_file = tr_dir
                            elif os.path.isdir(tr_dir):
                                input_file = os.path.join(tr_dir, fileName)
                            else:
                                logger.error(loggerHeader + "Input file/directory doesn't exist \n")
                                sys.exit(-1)

                            output_file = os.path.join(output_dest, fileName)

                            if not any(word in fileName for word in ignore_words):
                                if fileName.endswith(search_ext):
                                    if os.path.isfile(output_file):
                                        logger.debug(loggerHeader + "File already exists in: %s, deleting the old file: %s", output_dest, fileName)
                                        os.remove(output_file)

                                    # make sure we have a directory to work with
                                    if not os.path.exists(output_dest):
                                        os.makedirs(output_dest)

                                    if file_action == "move":
                                        logger.info(loggerHeader + "Moving file %s to %s", input_file, output_file)
                                        shutil.move(input_file, output_file)
                                    elif file_action == "link":
                                        logger.info(loggerHeader + "Linking file %s to %s", input_file, output_file)
                                        createLink(input_file, output_file)
                                    elif file_action == "copy":
                                        logger.info(loggerHeader + "Copying file %s to %s", input_file, output_file)
                                        shutil.copy(input_file, output_file)
                                    else:
                                        logger.error(loggerHeader + "File action not found")

                                elif fileName.endswith(archive_ext):
                                    logger.info(loggerHeader + "Extracting %s to %s", input_file, output_dest)

                                    # make sure we have a directory to work with
                                    if not os.path.exists(output_dest):
                                        os.makedirs(output_dest)

                                    pyUnRAR2.RarFile(input_file).extract(path = output_dest, withSubpath = False, overwrite = True)

                        if (config.getboolean("Couchpotato", "active") or config.getboolean("Sickbeard", "active")) and (any(word in tr_label for word in cp_label) or any(word in tr_label for word in sb_label)):
                            if file_action == "move" or file_action == "link":
                                logger.debug(loggerHeader + "Stop seeding torrent with hash: %s", tr_hash)
                                uTorrent.stop(tr_hash)

                            if any(word in tr_label for word in cp_label):
                                processMedia("couchpotato", output_dest)

                            elif any(word in tr_label for word in sb_label):
                                processMedia("sickbeard", output_dest)
                            
                            if file_action == "move":
                                logger.debug(loggerHeader + "Removing torrent with hash: %s", tr_hash)
                                uTorrent.removedata(tr_hash)
                            elif file_action == "link":
                                logger.debug(loggerHeader + "Start seeding torrent with hash: %s", tr_hash)
                                uTorrent.start(tr_hash)

                        if delete_finished and file_action != "move":
                            logger.debug(loggerHeader + "Removing torrent with hash: %s", tr_hash)
                            uTorrent.removedata(tr_hash)

                        logger.info(loggerHeader + "Success! Everything done \n")

                    else:
                        logger.error(loggerHeader + "Download hasn't completed for torrent: %s \n", tr_name)
                        sys.exit(-1)

                else:
                    logger.error(loggerHeader + "uProcess is set to ignore label: %s \n", tr_label)
                    sys.exit(-1)

            elif torrent[7] >= delete_ratio and delete_ratio != 0 and torrent[0] != tr_hash:
                logger.info(loggerHeader + "Ratio goal achieved, deleting torrent: %s", torrent[2])
                uTorrent.removedata(torrent[0])

        if not foundTorrent:
            logger.error(loggerHeader + "Couldn't find any torrent matching hash: %s \n", tr_hash)
            sys.exit(-1)

    else:
        logger.error(loggerHeader + "Couldn't connect with uTorrent \n")
        sys.exit(-1)

if __name__ == "__main__":

    config = ConfigParser.ConfigParser()
    configFilename = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), "config.cfg"))
    config.read(configFilename)

    logfile = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), "uProcess.log"))
    loggerHeader = "uProcess :: "
    loggerFormat = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', '%b-%d %H:%M:%S')
    logger = logging.getLogger('uProcess')

    loggerStd = logging.StreamHandler()
    loggerStd.setFormatter(loggerFormat)

    loggerHdlr = logging.FileHandler(logfile)
    loggerHdlr.setFormatter(loggerFormat)
    loggerHdlr.setLevel(logging.INFO)

    if config.getboolean("uProcess", "debug"):
        logger.setLevel(logging.DEBUG)
        loggerHdlr.setLevel(logging.DEBUG)
        loggerStd.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        loggerHdlr.setLevel(logging.INFO)
        loggerStd.setLevel(logging.INFO)

    logger.addHandler(loggerStd)
    logger.addHandler(loggerHdlr)

    if not os.path.isfile(configFilename):
        logger.error(loggerHeader + "Config file not found: " + configFilename)
        raise
    else:
        logger.info(loggerHeader + "Config loaded: " + configFilename)

    # usage: uProcess.py "%D" "%I" 
    tr_dir = os.path.normpath((sys.argv[1]).lower())    # %D - The directory of the torrent, or in some cases a single file
    tr_hash = sys.argv[2]                                     # %I - The hash of the torrent

    if not tr_dir:
        logger.error(loggerHeader + "Torrent directory is missing")
    elif not len(tr_hash) == 40:
        logger.error(loggerHeader + "Torrent hash is missing, or an invalid hash value has been passed")
    else:
        main(tr_dir, tr_hash)
