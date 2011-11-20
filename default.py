#/*
# *      Copyright (C) 2010 Team XBMC
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import urllib2,string,xbmc,xbmcgui,xbmcplugin, xbmcaddon
from xml.dom import minidom
from urllib import quote_plus
import unicodedata

__XBMC_Revision__ = xbmc.getInfoLabel("System.BuildVersion")
__settings__      = xbmcaddon.Addon(id = "plugin.audio.shoutcast")
__language__      = __settings__.getLocalizedString
__version__       = __settings__.getAddonInfo("version")
__cwd__           = __settings__.getAddonInfo("path")
__addonname__    = "Shoutcast"
__addonid__      = "plugin.audio.shoutcast"
__author__        = "Team XBMC"

BASE_URL = "http://www.shoutcast.com/sbin/newxml.phtml/"
HEADERS = { "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.98 Safari/534.13" }

def INDEX():
  request = urllib2.Request(BASE_URL, "", HEADERS)
  response = urllib2.urlopen(request)
  link = response.read()
  response.close()
  for stat in minidom.parseString(link).getElementsByTagName("genre"):
    name = unicodedata.normalize("NFKD", stat.attributes["name"].value).encode("ascii", "ignore")
    add_genre(name)

def RESOLVE(id):
  url = "%s?genre=%s" % (BASE_URL, quote_plus(id))
  log("RESOLVE URL: %s" % url)
  request = urllib2.Request(url, "", HEADERS)
  response = urllib2.urlopen(request)
  genre_xml = response.read()
  response.close()
  genre_node = minidom.parseString(genre_xml)
  base_url = genre_node.getElementsByTagName("tunein")[0].attributes["base"].value
  for station_node in genre_node.getElementsByTagName("station"):
    station_id = station_node.attributes["id"].value
    station_name = unicodedata.normalize("NFKD", station_node.attributes["name"].value).encode("ascii", "ignore")
    station_url = "%s?play=%s&tunein=%s" % (sys.argv[0], station_id, base_url)
    bite_rate = station_node.attributes["br"].value
    listeners = station_node.attributes["lc"].value
    add_station(station_name, station_url, bite_rate, listeners)

def PLAY(relative_url, station_id):
  url = "http://yp.shoutcast.com%s?id=%s" % (relative_url, station_id)
  log("PLAY URL: %s" % url)
  xbmc.Player().play(url)

def get_search_terms():
  kb = xbmc.Keyboard("", __language__(30092), False)
  kb.doModal()
  if (kb.isConfirmed() and len(kb.getText()) > 2):
    perform_search(kb.getText())

def perform_search(search):
  url = "%s?search=%s" % (BASE_URL, quote_plus(search))
  log("SEARCH URL: %s" % url)
  request = urllib2.Request(url, "", HEADERS)
  response = urllib2.urlopen(request)
  genre_xml = response.read()
  response.close()
  genre_node = minidom.parseString(genre_xml)
  base_url = genre_node.getElementsByTagName("tunein")[0].attributes["base"].value
  for station_node in genre_node.getElementsByTagName("station"):
    station_id = station_node.attributes["id"].value
    station_name = unicodedata.normalize("NFKD", station_node.attributes["name"].value).encode("ascii", "ignore")
    station_url = "%s?play=%s&tunein=%s" % (sys.argv[0], station_id, base_url)
    bite_rate = station_node.attributes["br"].value
    listeners = station_node.attributes["lc"].value
    add_station(station_name, station_url, bite_rate, listeners)

def add_genre(name):
  url = "%s?id=%s" % (sys.argv[0], name)
  list_item = xbmcgui.ListItem(name, iconImage = "DefaultFolder.png", thumbnailImage = "")
  ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = list_item, isFolder = True)
  return ok

def add_station(name, url, bit_rate, listeners):
  list_item = xbmcgui.ListItem(name, iconImage = "DefaultVideo.png", thumbnailImage = "")
  list_item.setInfo(type = "Music", infoLabels = { "Title": name, "Size": int(bit_rate) })
  list_item.setProperty("IsPlayable", "false");
  ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = list_item, isFolder = False)
  return ok
  
def sort(dir = False):
  if dir:
    xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_BITRATE)
    xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL)
  else:
    xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_BITRATE, label2Mask = "%X")
    xbmcplugin.addSortMethod(handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL, label2Mask = "%X")
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def get_params():
  param = []
  paramstring = sys.argv[2]
  if len(paramstring) >= 2:
    params = sys.argv[2]
    cleanedparams = params.replace("?", "")
    if (params[len(params) - 1] == "/"):
      params = params[0:len(params) - 2]
    pairsofparams = cleanedparams.split("&")
    param = {}
    for i in range(len(pairsofparams)):
      splitparams = {}
      splitparams = pairsofparams[i].split("=")
      if (len(splitparams)) == 2:
        param[splitparams[0]] = splitparams[1]
  return param

def log(msg):
  xbmc.output("### [%s] - %s" % (__addonname__,msg), level = xbmc.LOGDEBUG)
  
params = get_params()
try:
  id = params["id"]
except:
  id = "0";
try:
  initial = params["initial"]
except:
  initial = "0";
try:
  play = params["play"]
except:
  play = "0";
try:
  srch = params["search"]
except:
  srch = "0";

iid = len(id)
iplay = len(play)
iinitial = len(initial)
isearch = len(srch);

if iid > 1:
  RESOLVE(id)
  sort()

elif iinitial > 1:
  if initial == "search":
    get_search_terms()
    sort()
  else:
    INDEX()
    sort(True)
         
elif iplay > 1:
  PLAY(params["tunein"], play)
  
elif isearch > 1:
  perform_search(srch)
  sort()
  
else:
  u = "%s?initial=search" % (sys.argv[0])
  liz = xbmcgui.ListItem(__language__(30091), iconImage = "DefaultFolder.png", thumbnailImage = "")
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url = u, listitem = liz, isFolder = True)
  u = "%s?initial=list" % (sys.argv[0],)
  liz = xbmcgui.ListItem(__language__(30090), iconImage = "DefaultFolder.png", thumbnailImage = "")
  ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True)
  xbmcplugin.endOfDirectory(int(sys.argv[1]))