#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# import urllib
try:
    import urlparse as urlparse # Python 2
except ImportError:
    import urllib.parse as urlparse # Python 3
try:
    from urllib import quote as urlquote # Python 2
except ImportError:
    from urllib.parse import quote as urlquote # Python 3
try:
    from urllib import quote_plus as urlquoteplus # Python 2
except ImportError:
    from urllib.parse import quote_plus as urlquoteplus # Python 3
try:
    from urllib import urlencode as urlencode # Python 2
except ImportError:
    from urllib.parse import urlencode as urlencode # Python 3

import requests
import mechanize
try: # python 3
    import http.cookiejar as cookielib
except ImportError: # python 2
    import cookielib as cookielib
import sys
import re
import os
import json
import shutil
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
from bs4 import BeautifulSoup
import datetime
import math
import random

NODEBUG = False

class AmazonMedia():
    __slots__ = ['addon','addonId','addonName','addonFolder','addonUDatFo','addonBaseUrl','addonHandle','addonArgs','addonMode','siteVerList','siteVersion','logonURL',
        'musicURL','confFile','userEmail','userPassword','userAgent','deviceId','csrf_token','csrf_ts','csrf_rnd','customerId','marketplaceId','deviceType','musicTerritory','locale',
        'region','url','access','accessType','maxResults','audioQualist','audioQuality','cj','logging','showimages','showUnplayableSongs','showcolentr','sPlayLists','sAlbums','sSongs',
        'sStations','sArtists','addonFolRes','addonIcon','defFanart','cookieFile','br','content',
        'API_getBrowseRecommendations','API_lookup','API_getAddToLibraryRecommendations','API_getSimilarityRecommendations','API_getMusicStoreRecommendations',
        'API_artistDetailCatalog','API_getStationSections','API_artistDetailsMetadata','API_getTopMusicEntities','API_browseHierarchyV2','API_seeMore',
        'API_lookupStationsByStationKeys','API_createQueue','API_QueueGetNextTracks',
        'API_stream','API_streamHLS','API_streamDash','API_LicenseForPlaybackV2','API_search','API_cirrus','API_cirrusV1','API_cirrusV2','API_cirrusV3',
        'API_V3getTracksByAsin','API_V3getTracks','API_V3getTracksById',
        'API_getPlaylistsByIdV2','API_getPubliclyAvailablePlaylistsById','API_sociallySharePlaylist','API_getConfigurationV2','API_getFollowedPlaylistsInLibrary','API_getOwnedPlaylistsInLibrary',
        'API_GetRecentTrackActivity','API_GetRecentActivity',
        'API_GetSoccerMain','API_GetSoccerProgramDetails','API_GetSoccerStreamingURLs',
        'Q_getServerSongs','Q_getAllDataCountByMetaType','Q_getAllDataByMetaType','Q_getAlbumsCountForMetatype','Q_getAlbumsForMetatype','Q_getSongForPlayerBySearchLibrary',
        'Q_getTracks','Q_getTracksByAlbum','Q_getServerListSongs']
    def __init__(self):
        self.setVariables()
        self.prepFolder()
        self.prepBrowser()
        self.setAPIConstants()
        self.setQueryConstants()
        if self.logging == 'true':
            self.log( '\nhandle: ' + self.addonHandle.__str__()
                    + '\nArgs: ' + self.addonArgs.__str__()
                    + '\nmode: ' + self.addonMode.__str__())
    def setVariables(self):
        self.addon        = xbmcaddon.Addon()
        self.addonId      = self.getInfo('id')
        self.addonName    = self.getInfo('name')
        self.addonFolder  = self.getFolder("special://home/addons/" + self.addonId)
        self.addonUDatFo  = self.getFolder("special://profile/addon_data/" + self.addonId)
        self.addonBaseUrl = sys.argv[0]
        self.addonHandle  = int(sys.argv[1])
        self.addonArgs    = urlparse.parse_qs(sys.argv[2][1:])
        self.addonMode    = self.addonArgs.get('mode', None)
        self.siteVerList  = ["com", "co.uk", "de"]
        self.siteVersion  = self.getSetting("siteVersion")
        self.logonURL     = 'https://www.amazon.{}/gp/aw/si.html'.format(self.siteVerList[int(self.siteVersion)])
        self.musicURL     = 'https://music.amazon.{}'.format(self.siteVerList[int(self.siteVersion)])
        self.confFile     = self.getSetting("confFile")
        self.userEmail    = '' #self.getSetting("userEmail")
        self.userPassword = '' #self.getSetting("userPassword")
        self.userAgent    = self.getSetting("userAgent")

        self.deviceId     = self.getSetting("deviceId")
        self.csrf_token   = self.getSetting("csrf_token")
        self.csrf_ts      = self.getSetting("csrf_ts")
        self.csrf_rnd     = self.getSetting("csrf_rnd")
        self.customerId   = self.getSetting("customerId")
        self.marketplaceId= self.getSetting("marketplaceId")
        self.deviceType   = self.getSetting("deviceType")
        self.musicTerritory = self.getSetting("musicTerritory")
        self.locale       = self.getSetting("locale")
        self.region       = self.getSetting("region")
        self.url          = self.getSetting("url")
        self.access       = self.getSetting("access")
        self.accessType   = self.getSetting("accessType")
        self.maxResults   = 50
        self.audioQualist = ["HIGH","MEDIUM","LOW"]
        self.audioQuality = self.audioQualist[int(self.getSetting("quality"))]
        self.cj           = cookielib.MozillaCookieJar()
        self.logging      = self.getSetting("logging")
        self.showimages   = self.getSetting("showimages")
        self.showUnplayableSongs= self.getSetting("showUnplayableSongs")
        self.showcolentr  = self.getSetting("showcolentr")

        self.sPlayLists   = ["search1PlayLists","search2PlayLists","search3PlayLists"]
        self.sAlbums      = ["search1Albums","search2Albums","search3Albums"]
        self.sSongs       = ["search1Songs","search2Songs","search3Songs"]
        self.sStations    = ["search1Stations","search2Stations","search3Stations"]
        self.sArtists     = ["search1Artists","search2Artists","search3Artists"]
    def prepFolder(self):
        if not xbmcvfs.exists(self.addonUDatFo):
            xbmcvfs.mkdirs(self.addonUDatFo)
        self.addonFolRes  = os.path.join(self.addonFolder, "resources")
        self.addonIcon    = os.path.join(self.addonFolder, "icon.png")
        self.defFanart    = os.path.join(self.addonFolRes, "fanart.png")
        self.cookieFile   = os.path.join(self.addonUDatFo, self.siteVerList[int(self.siteVersion)] + ".cookies")
        if os.path.isfile(self.cookieFile):
            self.cj.load(self.cookieFile)
        if os.path.exists(os.path.join(self.addonUDatFo, "cookies")):
            os.rename(os.path.join(self.addonUDatFo, "cookies"), self.cookieFile)
    def reqDispatch(self):
        # reset addon
        if self.addonMode is not None and self.addonMode[0] == 'resetAddon':
            self.resetAddon()
            return
        # logon
        if self.access == 'false':
            if not self.amazonLogon():
                xbmc.executebuiltin(unicode('XBMC.Notification("Error:","Logon was not possible.",5000,)').encode("utf-8"))
                return False
        # main menu
        if self.addonMode is None:
            self.menuHome()
        elif self.addonMode[0] == 'menuPlaylists':
            self.menuPlaylists()
        elif self.addonMode[0] == 'menuAlbums':
            self.menuAlbums()
        elif self.addonMode[0] == 'menuSongs':
            self.menuSongs()
        elif self.addonMode[0] == 'menuStations':
            self.menuStations()
        elif self.addonMode[0] == 'menuArtists':
            self.menuArtists()
        # search - 'resultSpecs' needs a combination of label : type
        # playlists : catalog_playlist
        # albums : catalog_album
        # tracks : catalog_track
        # artists : catalog_artist
        # stations : catalog_station
        # requestedContent = [UNLIMITED, FULL, PRIME]
        # set to dynamic
        elif self.addonMode[0] == 'searchPlayLists':
            self.searchItems(['playlists','catalog_playlist'],30013)
        elif self.addonMode[0] == 'search1PlayLists':
            self.searchItems(['playlists','catalog_playlist'],None,self.getSetting("search1PlayLists"))
        elif self.addonMode[0] == 'search2PlayLists':
            self.searchItems(['playlists','catalog_playlist'],None,self.getSetting("search2PlayLists"))
        elif self.addonMode[0] == 'search3PlayLists':
            self.searchItems(['playlists','catalog_playlist'],None,self.getSetting("search3PlayLists"))

        elif self.addonMode[0] == 'searchAlbums':
            self.searchItems(['albums','catalog_album'],30010)
        elif self.addonMode[0] == 'search1Albums':
            self.searchItems(['albums','catalog_album'],None,self.getSetting("search1Albums"))
        elif self.addonMode[0] == 'search2Albums':
            self.searchItems(['albums','catalog_album'],None,self.getSetting("search2Albums"))
        elif self.addonMode[0] == 'search3Albums':
            self.searchItems(['albums','catalog_album'],None,self.getSetting("search3Albums"))

        elif self.addonMode[0] == 'searchSongs':
            self.searchItems(['tracks','catalog_track'],30011)
        elif self.addonMode[0] == 'search1Songs':
            self.searchItems(['tracks','catalog_track'],None,self.getSetting("search1Songs"))
        elif self.addonMode[0] == 'search2Songs':
            self.searchItems(['tracks','catalog_track'],None,self.getSetting("search2Songs"))
        elif self.addonMode[0] == 'search3Songs':
            self.searchItems(['tracks','catalog_track'],None,self.getSetting("search3Songs"))

        elif self.addonMode[0] == 'searchArtist':
            self.searchItems(['artists','catalog_artist'],30014)
        elif self.addonMode[0] == 'search1Artists':
            self.searchItems(['artists','catalog_artist'],None,self.getSetting("search1Artists"))
        elif self.addonMode[0] == 'search2Artists':
            self.searchItems(['artists','catalog_artist'],None,self.getSetting("search2Artists"))
        elif self.addonMode[0] == 'search3Artists':
            self.searchItems(['artists','catalog_artist'],None,self.getSetting("search3Artists"))

        elif self.addonMode[0] == 'searchStations':
            self.searchItems(['stations','catalog_station'],30016)
        elif self.addonMode[0] == 'search1Stations':
            self.searchItems(['stations','catalog_station'],None,self.getSetting("search1Stations"))
        elif self.addonMode[0] == 'search2Stations':
            self.searchItems(['stations','catalog_station'],None,self.getSetting("search2Stations"))
        elif self.addonMode[0] == 'search3Stations':
            self.searchItems(['stations','catalog_station'],None,self.getSetting("search3Stations"))

        elif self.addonMode[0] == 'getArtistDetails':
            asin = self.addonArgs.get('asin', [None])
            self.getArtistDetails(asin[0])

        elif self.addonMode[0] == 'getRecentlyPlayed':
            self.getRecentlyPlayed('PLAYED')
        elif self.addonMode[0] == 'getRecentlyAddedSongs':
            self.getRecentlyAddedSongs()
        # playlists - different types of playlists
        # popularity-rank
        # newly-released
        # requestedContent = [FULL_CATALOG, KATANA, MUSIC_SUBSCRIPTION, PRIME_UPSELL_MS, ALL_STREAMABLE, PRIME]
        # set to 'PRIME'
        elif self.addonMode[0] == 'getPopularPlayLists':
            self.getPlayLists('popularity-rank')
        elif self.addonMode[0] == 'getNewPlayLists':
            self.getPlayLists('newly-released')
        elif self.addonMode[0] == 'getFollowedPlayLists':
            self.getFollowedPlayLists()
        elif self.addonMode[0] == 'getOwnedPlaylists':
            self.getOwnedPlaylists()
        elif self.addonMode[0] == 'getPlaylistsByIdV2':
            asin = self.addonArgs.get('asin', [None])
            self.getPlaylistsByIdV2(asin[0])
        # recommendations
        # mediatypes:
        # mp3-prime-browse-carousels_playlistStrategy
        # mp3-prime-browse-carousels_mp3PrimeAlbumsStrategy
        # mp3-prime-browse-carousels_mp3PrimeTracksStrategy
        # mp3-prime-browse-carousels_mp3ArtistStationStrategy
        elif self.addonMode[0] == 'getRecomPlayLists':
            self.getRecommendations('playlists','mp3-prime-browse-carousels_playlistStrategy')
        elif self.addonMode[0] == 'getRecomAlbums':
            self.getRecommendations('albums','mp3-prime-browse-carousels_mp3PrimeAlbumsStrategy')
        elif self.addonMode[0] == 'getRecomStations':
            self.getRecommendations('stations','mp3-prime-browse-carousels_mp3ArtistStationStrategy')
        # get own music, differentiate betwenn purchased and own lib
        # param: searchReturnType , caller, sortCriteriaList.member.1.sortColumn
        elif self.addonMode[0] == 'getPurAlbums':
            self.getPurchased(['ALBUMS','getAllDataByMetaType','sortAlbumName'],'albums')
        elif self.addonMode[0] == 'getAllAlbums':
            self.getPurchased(['ALBUMS','getAllDataByMetaType','sortAlbumName'],'albums')
        elif self.addonMode[0] == 'getAllSongs':
            self.getPurchased(['TRACKS','getServerSongs','sortTitle'],'songs')
        elif self.addonMode[0] == 'getPurSongs':
            self.getPurchased(['TRACKS','getServerSongs','sortTitle'],'songs')
        # get amazon stations
        elif self.addonMode[0] == 'getStations':
            self.getStations('stations')
        elif self.addonMode[0] == 'getAllArtistsStations':
            self.getStations('stationsallartists')
        elif self.addonMode[0] == 'getGenres':
            self.getStations('genres') # 1st level
        elif self.addonMode[0] == 'getGenres2':
            self.getStations('genres2') # 2nd level
        elif self.addonMode[0] == 'getGenrePlaylist':
            asin = self.addonArgs.get('asin', None)
            self.getGenrePlaylist(asin[0]) # get genre playlist
        elif self.addonMode[0] == 'createQueue':
            asin = self.addonArgs.get('asin', None)
            self.createQueue(asin[0])
        # get song lists
        elif self.addonMode[0] == 'lookup':
            asin = self.addonArgs.get('asin', None)
            self.lookup(asin)
        # play the song
        elif self.addonMode[0] == 'getTrack':
            asin = self.addonArgs.get('asin', [None])[0]
            objectId = self.addonArgs.get('objectId', [None])[0]
            self.getTrack(asin,objectId)
        # Amazon Soccer Live
        elif self.addonMode[0] == 'menuSoccer':
            self.menuSoccer()
        elif self.addonMode[0] == 'soccerBUND':
            self.getSoccerFilter('BUND')
        elif self.addonMode[0] == 'soccerBUND2':
            self.getSoccerFilter('BUND2')
        elif self.addonMode[0] == 'soccerCHAMP':
            self.getSoccerFilter('CHAMP')
        elif self.addonMode[0] == 'soccerDFBPOKAL':
            self.getSoccerFilter('DFBPOKAL')
        elif self.addonMode[0] == 'soccerSUPR':
            self.getSoccerFilter('SUPR')
        elif self.addonMode[0] == 'getSoccerDetail':
            objectId = self.addonArgs.get('objectId', [None])[0]
            self.getSoccerDetail(objectId)
    def translation(self,oId):
        return self.addon.getLocalizedString(oId).encode('utf-8')
    def getInfo(self,oProp):
        return self.addon.getAddonInfo(oProp)
    def getSetting(self,oProp):
        return self.addon.getSetting(oProp)
    def setSetting(self,oProp,val):
        self.addon.setSetting(oProp,val)
    def setContent(self,cont):
        xbmcplugin.setContent(int(sys.argv[1]), cont)
    def setCookie(self):
        self.cj.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
    def setSearch(self,item,query):
        q = []
        update = True
        if   item == 'playlists':
            q = self.sPlayLists
        elif item == 'albums':
            q = self.sAlbums
        elif item == 'tracks':
            q = self.sSongs
        elif item == 'stations':
            q = self.sStations
        elif item == 'artists':
            q = self.sArtists
        for i in q:
            if self.getSetting(i) == query:
                update = False
                break
        if update:
            self.setSetting(q[2],self.getSetting(q[1]))
            self.setSetting(q[1],self.getSetting(q[0]))
            self.setSetting(q[0],query)
    def getFolder(self,oPath):
        return xbmc.translatePath(oPath) #.decode('utf-8')
    def getUserInput(self,title,txt,hidden=False,uni=False): # uni=True
        kb = xbmc.Keyboard()
        kb.setHeading(title)
        kb.setDefault(txt)
        kb.setHiddenInput(hidden)
        kb.doModal()
        if kb.isConfirmed() and kb.getText():
            if uni:
                try:
                    return unicode(kb.getText(), "utf-8")
                except:
                    return str(kb.getText(), encoding = 'utf-8')
            else:
                return kb.getText() # for password needed, due to encryption
        else:
            return False
    def log(self, msg, level=xbmc.LOGNOTICE):
        log_message = '{0}: {1}'.format(self.addonId, msg).encode("utf-8")
        xbmc.log(log_message, level) #.encode("utf-8")
    # read / write config file
    def appConfig(self,app_config):
        if app_config is None:
            return False
        self.deviceId       = app_config['deviceId']
        self.csrf_token     = app_config['CSRFTokenConfig']['csrf_token']
        self.csrf_ts        = app_config['CSRFTokenConfig']['csrf_ts']
        self.csrf_rnd       = app_config['CSRFTokenConfig']['csrf_rnd']
        self.customerId     = app_config['customerId']
        self.marketplaceId  = app_config['marketplaceId']
        self.deviceType     = app_config['deviceType']
        self.musicTerritory = app_config['musicTerritory']
        self.locale         = app_config['i18n']['locale']
        self.region         = app_config['realm'][:2]
        self.url            = 'https://{}'.format(app_config['serverInfo']['returnUrlServer'])
        self.access         = 'true'
        #if app_config['customerBenefits']['primeAccess'] == 1:
        #    self.accessType = 'PRIME'
        #if app_config['customerBenefits']['hawkfireAccess'] == 1:
        #    self.accessType = 'UNLIMITED'
        self.accessType = app_config['customerBenefits']['tier']
        self.setSetting('deviceId',         self.deviceId)
        self.setSetting('csrf_token',       self.csrf_token)
        self.setSetting('csrf_ts',          self.csrf_ts)
        self.setSetting('csrf_rnd',         self.csrf_rnd)
        self.setSetting('customerId',       self.customerId)
        self.setSetting('marketplaceId',    self.marketplaceId)
        self.setSetting('deviceType',       self.deviceType)
        self.setSetting('musicTerritory',   self.musicTerritory)
        self.setSetting('locale',           self.locale)
        self.setSetting('region',           self.region)
        self.setSetting('url',              self.url)
        self.setSetting('access',           self.access)
        self.setSetting('accessType',       self.accessType)
        return True
    # cleanup
    def delCookies(self):
        if os.path.exists(self.cookieFile):
            os.remove(self.cookieFile)
        self.setSetting('csrf_ts', "")
        self.setSetting('csrf_rnd', "")
        self.setSetting('csrf_token', "")
        self.setSetting('customerId', "")
        self.setSetting('marketplaceId', "")
        self.setSetting('deviceId', "")
        self.setSetting('deviceType', "")
        self.setSetting('musicTerritory', "")
        self.setSetting('locale', "")
        self.setSetting('region', "")
        self.setSetting('url', "")
        self.setSetting('access', "false")
        self.setSetting('logging', "false")
        self.setSetting('showimages', "false")
        self.setSetting('showUnplayableSongs', "false")
        self.setSetting('showcolentr', "true")
        self.setSetting('accessType', "")
        self.setSetting('search1', "")
        self.setSetting('search2', "")
        self.setSetting('search3', "")
        self.access = 'false'
    def resetAddon(self):
        self.deviceId = ''
        self.csrf_token = ''
        self.csrf_ts = ''
        self.csrf_rnd = ''
        self.customerId = ''
        self.deviceType = ''
        self.musicTerritory = ''
        self.locale = ''
        self.region = ''
        self.url = ''
        self.access = 'false'
        self.logging = 'false'
        self.showimages = 'false'
        self.showUnplayableSongs = 'false'
        self.showcolentr = 'true'
        self.delCookies()
        if os.path.exists(self.addonUDatFo):
            try:
                shutil.rmtree(self.addonUDatFo)
            except:
                shutil.rmtree(self.addonUDatFo)
            xbmc.executebuiltin(unicode('XBMC.Notification("Information:","Addon reset successful",5000,)').encode("utf-8"))
    def delCredentials(self):
        self.userEmail = ''
        self.userPassword = ''
    def getCredentials(self):
        status = True
        if not self.userEmail or not self.userPassword:
            user = self.getUserInput(self.translation(30030),'', hidden=False, uni=False) # get Email
            if user:
                pw = self.getUserInput(self.translation(30031),'', hidden=True, uni=False) # get Password
                if pw:
                    self.userEmail = user
                    self.userPassword = pw
                    status = True
                else:
                    status = False
            else:
                status = False
        return status
    # web communication
    def parseHTML(self,resp):
        resp = re.sub(r'(?i)(<!doctype \w+).*>', r'\1>', resp)
        soup = BeautifulSoup(resp, 'html.parser')
        return soup
    ################################################################################
    def setAPIConstants(self):
        """
        Amazon API definitions
        amzUrl      = AmazonBaseUrl + region + /api/ + path
        amzTarget   = target
        """
        base = 'com.amazon.musicensembleservice.MusicEnsembleService.'
        self.API_getBrowseRecommendations = {
            'path':   'muse/legacy/getBrowseRecommendations',
            'target': '{}{}'.format(base,'getBrowseRecommendations')
        }
        self.API_lookup = {
            'path':   'muse/legacy/lookup',
            'target': '{}lookup'.format(base)
        }
        self.API_getAddToLibraryRecommendations = {
            'path':   'muse/legacy/getAddToLibraryRecommendations',
            'target': '{}getAddToLibraryRecommendations'.format(base)
        }
        self.API_getSimilarityRecommendations = {
            'path':   'muse/legacy/getSimilarityRecommendations',
            'target': '{}getSimilarityRecommendations'.format(base)
        }
        self.API_getMusicStoreRecommendations = {
            'path':   'muse/legacy/getMusicStoreRecommendations',
            'target': '{}getMusicStoreRecommendations'.format(base)
        }
        self.API_artistDetailCatalog = {
            'path':   'muse/artistDetailCatalog',
            'target': '{}artistDetailCatalog'.format(base),
            'method': 'POST'
        }
        self.API_getStationSections = {
            'path':   'muse/stations/getStationSections',
            'target': '{}getStationSectionsGet'.format(base),
            'method': 'GET'
        }
        self.API_artistDetailsMetadata = {
            'path':   'muse/artistDetailsMetadata',
            'target': '{}artistDetailsMetadata'.format(base)
        }
        self.API_getTopMusicEntities = { # playlists
            'path':   'muse/getTopMusicEntities',
            'target': '{}getTopMusicEntities'.format(base)
        }
        self.API_browseHierarchyV2 = {
            'path':   'muse/browseHierarchyV2',
            'target': '{}browseHierarchyV2'.format(base)
        }
        self.API_seeMore = {
            'path':   'muse/seeMore',
            'target': '{}seeMore'.format(base)
        }
        self.API_lookupStationsByStationKeys = {
            'path':   'muse/stations/lookupStationsByStationKeys',
            'target': '{}lookupStationsByStationKeys'.format(base)
        }
        base = 'com.amazon.musicplayqueueservice.model.client.external.voiceenabled.MusicPlayQueueServiceExternalVoiceEnabledClient.'
        self.API_createQueue = { # genres
            'path':   'mpqs/voiceenabled/createQueue',
            'target': '{}createQueue'.format(base)
        }
        self.API_QueueGetNextTracks = { # genres
            'path':   'mpqs/voiceenabled/getNextTracks',
            'target': '{}getNextTracks'.format(base)
        }
        # get streaming url
        base = 'com.amazon.digitalmusiclocator.DigitalMusicLocatorServiceExternal.'
        self.API_stream  = { # ASIN / COID
            'path':   'dmls/',
            'target': '{}getRestrictedStreamingURL'.format(base)
        }
        self.API_streamHLS = { # ASIN (hlsVersion:V3)
            'path':   'dmls/',
            'target': '{}getHLSManifest'.format(base)
        }
        self.API_streamDash = { # ASIN (musicDashVersionList: ["V1", "V2"])
            'path':   'dmls/',
            'target': '{}getDashManifestsV2'.format(base)
        }
        self.API_LicenseForPlaybackV2 = {
            'path':   'dmls/',
            'target': '{}getLicenseForPlaybackV2'.format(base)
        }
        self.API_search = {
            'path':   'textsearch/search/v1_1/',
            'target': 'com.amazon.tenzing.textsearch.v1_1.TenzingTextSearchServiceExternalV1_1.search'
        }
        # cirrus
        base = 'com.amazon.cirrus.libraryservice.'
        self.API_cirrus   = {
            'path'  : 'cirrus/',
            'target': None
        }
        self.API_cirrusV1 = {
            'path':   'cirrus/',
            'target': '{}CirrusLibraryServiceExternal.'.format(base)
        }
        self.API_cirrusV2 = {
            'path':   'cirrus/2011-06-01/',
            'target': '{}v2.CirrusLibraryServiceExternalV2.'.format(base)
        }
        self.API_cirrusV3 = {
            'path':   'cirrus/v3/',
            'target': '{}v3.CirrusLibraryServiceExternalV3.'.format(base)
        }
        self.API_V3getTracksByAsin = {
            'path':   'cirrus/v3/',
            'target': '{}getTracksByAsin'.format(self.API_cirrusV3['target'])
        }
        self.API_V3getTracks = {
            'path':   'cirrus/v3/',
            'target': '{}getTracks'.format(self.API_cirrusV3['target']),
            'operation': 'getTracks'
        }
        self.API_V3getTracksById = {
            'path':   'cirrus/v3/',
            'target': '{}getTracksById'.format(self.API_cirrusV3['target']),
            'operation': 'getTracksById'
        }
        # default
        base = 'com.amazon.musicplaylist.model.MusicPlaylistService.'
        self.API_getPlaylistsByIdV2 = {
            'path':   'playlists/',
            'target': '{}getPlaylistsByIdV2'.format(base)
        }
        self.API_getPubliclyAvailablePlaylistsById = {
            'path':   'playlists/',
            'target': '{}getPubliclyAvailablePlaylistsById'.format(base)
        }
        self.API_sociallySharePlaylist = {
            'path':   'playlists/',
            'target': '{}sociallySharePlaylist'.format(base)
        }
        self.API_getConfigurationV2 = {
            'path':   'playlists/',
            'target': '{}getConfigurationV2'.format(base)
        }
        self.API_getFollowedPlaylistsInLibrary = {
            'path':   'playlists/',
            'target': '{}getFollowedPlaylistsInLibrary'.format(base)
        }
        self.API_getOwnedPlaylistsInLibrary = {
            'path':   'playlists/',
            'target': '{}getOwnedPlaylistsInLibrary'.format(base)
        }
        base = 'com.amazon.nimblymusicservice.NimblyMusicService.'
        self.API_GetRecentTrackActivity = {
            'path':   'nimbly/',
            'target': '{}GetRecentTrackActivity'.format(base)
        }
        self.API_GetRecentActivity = {
            'path':   'nimbly/',
            'target': '{}GetRecentActivity'.format(base)
        }
        # soccer live
        base = 'com.amazon.eventvendingservice.EventVendingService.getProgramDetails'
        self.API_GetSoccerMain = {
            'path':   'eve/getPrograms',
            'target': base
        }
        self.API_GetSoccerProgramDetails = {
            'path':   'eve/getProgramDetails',
            'target': base
        }
        self.API_GetSoccerStreamingURLs = {
            'path':   'amals/getOnDemandStreamingURLs',
            'target': 'com.amazon.amazonmusicaudiolocatorservice.model.AmazonMusicAudioLocatorServiceExternal.GetOnDemandStreamingURLs'
        }
    def setQueryConstants(self):
        self.Q_getServerSongs = {
            'Operation'         : 'searchLibrary',
            'caller'            : 'getServerSongs',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : '' # 'sortTitle'
        }
        self.Q_getAllDataCountByMetaType = {
            'Operation'         : 'searchLibrary',
            'caller'            : 'getAllDataCountByMetaType',
            'searchReturnType'  : 'ALBUMS',
            'sortColumn'        : 'sortAlbumName'
        }
        self.Q_getAllDataByMetaType = {
            'Operation'         : 'searchLibrary',
            'caller'            : 'getAllDataByMetaType',
            'searchReturnType'  : 'ALBUMS',
            'sortColumn'        : 'sortAlbumName'
        }
        self.Q_getAlbumsCountForMetatype = {
            'Operation'         : 'searchLibrary',
            'caller'            : 'getAlbumsCountForMetatype',
            'searchReturnType'  : 'ALBUMS',
            'sortColumn'        : 'sortAlbumName'
        }
        self.Q_getAlbumsForMetatype = {
            'Operation'         : 'searchLibrary',
            'caller'            : 'getAlbumsForMetatype',
            'searchReturnType'  : 'ALBUMS',
            'sortColumn'        : 'sortAlbumName'
        }
        self.Q_getSongForPlayerBySearchLibrary = {
            'Operation'         : 'searchLibrary',
            'caller'            : 'getSongForPlayerBySearchLibrary',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : '' # 'sortTitle'
        }
        self.Q_getTracks = {
            'Operation'         : 'getTracks',
            'caller'            : 'dataServices.getTracks',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : 'sortTitle'
        }
        self.Q_getTracksByAlbum = {
            'Operation'         : 'selectTracks',
            'caller'            : 'dataServices.getTracksByAlbum',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : 'sortTitle'
        }
        """
        self.Q_getSongForDowloadBySelectTrackMetadata = {
            'Operation'         : 'selectTrackMetadata',
            'caller'            : 'getSongForDowload',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : '' # 'sortTitle'
        }
        self.Q_getSongForPlayerBySelectTrackMetadata = {
            'Operation'         : 'selectTrackMetadata',
            'caller'            : 'getSongForPlayerBySelectTrackMetadata',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : 'sortTitle'
        }
        self.Q_getSongForPlayerFromSmartList = {
            'Operation'         : 'selectTrackMetadata',
            'caller'            : 'getSongForPlayerFromSmartList',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : 'sortTitle'
        }
        self.Q_getServerSmartList = { # done
            'Operation'         : 'selectTrackMetadata',
            'caller'            : 'getServerSmartList',
            'searchReturnType'  : '',
            'sortColumn'        : 'creationDate'
        }
        """
        self.Q_getServerListSongs = {
            'Operation'         : 'getPlaylists',
            'caller'            : 'getServerListSongs',
            'searchReturnType'  : '', # 'ALBUMS',
            'sortColumn'        : ''  # 'sortAlbumName'
        }
        """
        self.Q_getServerAlbumData = { # done
            'Operation'         : 'selectTrackMetadata',
            'caller'            : 'getServerData',
            'searchReturnType'  : 'TRACKS',
            'sortColumn'        : 'trackNum'
        }
        self.Q_getServerData = { # done
            'Operation'         : 'selectTrackMetadata',
            'caller'            : 'getServerData',
            'searchReturnType'  : '',
            'sortColumn'        : 'sortAlbumName' # discNum + trackNum
        }
        """
    ################################################################################
    def amzCall(self,amzUrl,mode,referer=None,asin=None,mediatype=None):
        url = '{}/{}/api/{}'.format(self.url, self.region, amzUrl['path'])
        head = self.prepReqHeader(amzUrl['target'],referer)
        data = self.prepReqData(mode,asin,mediatype)
        resp = requests.post(url=url, data=data, headers=head, cookies=self.cj)
        self.setCookie()
        if resp.status_code == 401 :
            self.delCookies()
            self.amazonLogon()
        if self.logging == 'true':
            self.log(resp.text)
        if mode == 'getTrack' or mode == 'getTrackHLS' or mode == 'getTrackDash':
            return resp
        else:
            return resp.json()
    def prepBrowser(self):
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.set_handle_gzip(False)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_equiv(True)
        self.br.set_cookiejar(self.cj)
        self.br.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
             ('Accept-Encoding', 'deflate,br'), #gzip,
             ('Accept-Language', 'de,en-US;q=0.7,en;q=0.3'),
             ('Cache-Control', 'no-cache'),
             ('Connection', 'keep-alive'),
             ('Content-Type', 'application/x-www-form-urlencoded'),
             ('User-Agent', self.userAgent),
             ('csrf-token', self.csrf_token),
             ('csrf-rnd',   self.csrf_rnd),
             ('csrf-ts',    self.csrf_ts),
             ('Upgrade-Insecure-Requests', '1')]
    def prepReqHeader(self, amzTarget, referer=None):
        head = { 'Accept' : 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding' : 'deflate,br,gzip',
                'Accept-Language' : 'de,en-US,en;q=0.9',
                'csrf-rnd' :        self.csrf_rnd,
                'csrf-token' :      self.csrf_token,
                'csrf-ts' :         self.csrf_ts,
                'Host' :            'music.amazon.{}'.format(self.siteVerList[int(self.siteVersion)]),
                'Origin' :          self.musicURL,
                'User-Agent' :      self.userAgent,
                'X-Requested-With' : 'XMLHttpRequest'
                }
        if amzTarget is not None:
            head['Content-Encoding'] = 'amz-1.0'
            head['content-type'] = 'application/json'
            head['X-Amz-Target'] = amzTarget
        if referer == 'soccer':
            head['Content-Encoding'] = None
        return head
    def prepReqData(self,mode,asin=None,mediatype=None):
        #data = json.dumps(data)
        #data = json.JSONEncoder().encode(data)
        """
        rankType:           newly-added, popularity-rank, top-sellers, newly-released
        requestedContent:   FULL_CATALOG, KATANA, MUSIC_SUBSCRIPTION, PRIME_UPSELL_MS, ALL_STREAMABLE, PRIME
        features:           fullAlbumDetails, playlistLibraryAvailability, childParentOwnership, trackLibraryAvailability,
                            hasLyrics, expandTracklist, ownership, popularity, albumArtist, collectionLibraryAvailability
        types:              artist, track, album, similarArtist, playlist, station
        """
        token = self.addonArgs.get('token', [''])
        if   mode == 'searchItems':
            if self.addonArgs.get('token', [None])[0] == None:
                prop = 'maxResults'
                val = self.maxResults
            else:
                prop = 'pageToken'
                val = self.addonArgs.get('token', [None])[0]
            data = {
                'customerIdentity': {
                    'deviceId': self.deviceId,
                    'deviceType': self.deviceType,
                    'sessionId': '',
                    'customerId': self.customerId
                },
                'features': {
                    'spellCorrection': {
                        'allowCorrection': 'true'
                    }
                },
                'locale': self.locale,
                'musicTerritory': self.musicTerritory,
                'query': asin,
                'requestContext': 'true',
                'resultSpecs': [{
                    'label': mediatype[0], #'albums',
                    'documentSpecs': [{
                        'type': mediatype[1], #'catalog_album',
                        'fields': [
                            '__DEFAULT',
                            'artOriginal',
                            'artMedium',
                            'artLarge',
                            'artFull',
                            'isMusicSubscription',
                            'primeStatus',
                            'albumName',
                            'albumReleaseDate'
                        ]
                    }],
                    prop : val,
                    'contentRestrictions': {
                        'allowedParentalControls': {
                            'hasExplicitLanguage': 'true'
                        },
                        'eligibility': {
                            'tier': self.accessType
                        }
                    }
                }]
            }
            data = json.JSONEncoder().encode(data)
        elif mode == 'getArtistDetails':
            data  = {
                'requestedContent': 'PRIME', #self.accessType,
                'asin': asin,
                'types':[{
                    'sortBy':'popularity-rank',
                    'type':'album',
                    'maxCount':     self.maxResults,
                    'nextToken':    self.addonArgs.get('token', [''])[0]
                }],
                'features':[
                    #'expandTracklist',
                    #'collectionLibraryAvailability',
                    'popularity'
                ],
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId
            }
            data = json.dumps(data)
        elif mode == 'recentlyplayed':
            data = {
                'activityTypeFilters': [mediatype],
                'pageToken':        token[0],
                'lang':             self.locale,
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId,
            }
            data = json.dumps(data)
        elif mode == 'getMetaTracks':
            """
            available fields in attributeList:
            ['uploaded', 'composer', 'primaryGenre', 'albumArtistName', 'albumCoverImageFull', 'sortAlbumArtistName', 'purchased', 'fileExtension', 'albumReleaseDate',
            'albumAsin', 'fileName', 'albumCoverImageXL', 'albumContributors', 'songWriter', 'albumCoverImageMedium', 'albumCoverImageLarge', 'orderId', 'assetType',
            'parentalControls', 'marketplace', 'lyricist', 'localFilePath', 'albumRating', 'creationDate', 'bitrate', 'albumArtistAsin', 'performer', 'purchaseDate',
            'sortArtistName', 'albumPrimaryGenre', 'primeStatus', 'discNum', 'status', 'rogueBackfillDate', 'physicalOrderId', 'artistName', 'lastUpdatedDate', 'albumCoverImageTiny',
            'duration', 'audioUpgradeDate', 'albumCoverImageSmall', 'errorCode', 'asin', 'title', 'isMusicSubscription', 'contributors', 'sortTitle', 'objectId', 'albumName',
            'trackNum', 'sortAlbumName', 'publisher', 'fileSize', 'rating', 'md5', 'artistAsin']
            """
            data = {
                'filterList':[
                    {
                        'attributeName':'albumAsin',
                        'comparisonType':'EQUALS',
                        'attributeValue':asin
                    },
                    {
                        'attributeName':'status',
                        'comparisonType':'EQUALS',
                        'attributeValue':'AVAILABLE'
                    }
                ],
                'attributeList':[
                    'trackNum',
                    'discNum',
                    'duration',
                    'albumReleaseDate',
                    'primaryGenre',
                    'albumName',
                    'artistName',
                    'title',
                    'asin',
                    'objectId',

                    'albumAsin',
                    'artistAsin',
                    'purchased',
                    'status',
                    'primeStatus'
                ],
                'sortOrder':{
                    'sort':'albumName',
                    'order':'ASC'
                },
                'maxResults':       self.maxResults,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId,
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType
            }
            data = json.JSONEncoder().encode(data)
        elif mode == 'recentlyaddedsongs':
            data = {
                'selectCriteria': None,
                'albumArtUrlsRedirects': 'false',
                'distinctOnly': 'false',
                'countOnly': 'false',
                'sortCriteriaList': None,
                'maxResults': self.maxResults,
                'nextResultsToken': self.addonArgs.get('token', [0])[0],
                'selectCriteriaList.member.1.attributeName': 'status',
                'selectCriteriaList.member.1.comparisonType': 'EQUALS',
                'selectCriteriaList.member.1.attributeValue': 'AVAILABLE',
                'selectCriteriaList.member.2.attributeName': 'creationDate',
                'selectCriteriaList.member.2.comparisonType': 'GREATER_THAN',
                'selectCriteriaList.member.2.attributeValue': datetime.date.today()-datetime.timedelta(days=90),
                'sortCriteriaList.member.1.sortColumn': 'creationDate',
                'sortCriteriaList.member.1.sortType': 'DESC',
                'Operation': 'selectTrackMetadata',
                'caller': 'getServerSmartList',
                'ContentType': 'JSON',
                'customerInfo.customerId':  self.customerId,
                'customerInfo.deviceId':    self.deviceId,
                'customerInfo.deviceType':  self.deviceType
            }
        elif mode == 'followedplaylists':
            data = {
                'optIntoSharedPlaylists': 'true',
                'entryOffset':      0, # todo
                'pageSize':         self.maxResults,
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId
            }
            data = json.dumps(data)
        elif mode == 'getownedplaylists':
            data = {
                'entryOffset':      0, #todo
                'pageSize':         self.maxResults,
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId
            }
            data = json.dumps(data)
        elif mode == 'getplaylistsbyid':
            data = {
                'playlistIds':      [asin],
                'requestedMetadata':['asin','albumName','sortAlbumName','artistName','primeStatus','isMusicSubscription','duration','sortArtistName','sortAlbumArtistName','objectId','title','status','assetType','discNum','trackNum','instantImport','purchased'],
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId
            }
            data = json.dumps(data)
        elif mode == 'playlist':
            data  = {
                'rankType':         mediatype,
                'requestedContent': 'PRIME',#self.accessType,
                'features':         ['playlistLibraryAvailability','collectionLibraryAvailability'],
                'types':            ['playlist'],
                'nextTokenMap':     {'playlist' : token[0]},
                'maxCount':         self.maxResults,
                'lang':             self.locale,
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId
            }
            data = json.dumps(data)
        elif mode == 'recommendations':
            # mediatypes:
            # mp3-prime-browse-carousels_playlistStrategy
            # mp3-prime-browse-carousels_mp3PrimeAlbumsStrategy
            # mp3-prime-browse-carousels_mp3PrimeTracksStrategy
            # mp3-prime-browse-carousels_mp3ArtistStationStrategy
            token = self.addonArgs.get('token', [0])
            data  = {
                'maxResultsPerWidget' : self.maxResults,
                'minResultsPerWidget' : 1,
                'lang' :                self.locale,
                'requestedContent' :    'PRIME', #self.accessType,
                'musicTerritory' :      self.musicTerritory,
                'deviceId' :            self.deviceId,
                'deviceType' :          self.deviceType,
                'customerId' :          self.customerId,
                'widgetIdTokenMap' : { mediatype : int(token[0]) }
            }
            data = json.dumps(data)
        elif mode == 'getPurchased': # purchased and all Songs / purchased Albums
            if self.addonMode[0] == 'getPurSongs' or self.addonMode[0] == 'getPurAlbums':
                filter = ['purchased','EQUALS','true']
            else:
                #filter = ['purchased','LIKE','%']
                filter = ['primeStatus','NOT_EQUALS','NOT_PRIME']
            data = {
                'searchReturnType': mediatype[0],
                'searchCriteria.member.1.attributeName': 'assetType',
                'searchCriteria.member.1.comparisonType': 'EQUALS',
                'searchCriteria.member.1.attributeValue': 'AUDIO',
                'searchCriteria.member.2.attributeName':  'status',
                'searchCriteria.member.2.comparisonType': 'EQUALS',
                'searchCriteria.member.2.attributeValue': 'AVAILABLE',
                'searchCriteria.member.3.attributeName':  filter[0],
                'searchCriteria.member.3.comparisonType': filter[1],
                'searchCriteria.member.3.attributeValue': filter[2],
                'albumArtUrlsRedirects': 'false',
                'distinctOnly': 'false',
                'countOnly': 'false',
                'selectedColumns.member.1': 'trackNum',
                'selectedColumns.member.2': 'discNum',
                'selectedColumns.member.3': 'duration',
                'selectedColumns.member.4': 'albumReleaseDate',
                'selectedColumns.member.5': 'primaryGenre',
                'selectedColumns.member.6': 'albumName',
                'selectedColumns.member.7': 'artistName',
                'selectedColumns.member.8': 'title',
                'selectedColumns.member.9': 'asin',
                'selectedColumns.member.10': 'objectId',
                'selectedColumns.member.11': 'albumCoverImageFull',
                'selectedColumns.member.12': 'purchased',
                'selectedColumns.member.13': 'status',
                'selectedColumns.member.14': 'primeStatus',
                'selectedColumns.member.15': 'sortAlbumName',
                'selectedColumns.member.16': 'sortTitle',
                'sortCriteriaList': None,
                'maxResults': self.maxResults,
                'nextResultsToken': token[0],
                'Operation': 'searchLibrary',
                'caller': mediatype[1],
                'sortCriteriaList.member.1.sortColumn': mediatype[2],
                'sortCriteriaList.member.1.sortType': 'ASC',
                'ContentType': 'JSON',
                'customerInfo.customerId': self.customerId,
                'customerInfo.deviceId': self.deviceId,
                'customerInfo.deviceType': self.deviceType
            }
        elif mode == 'songs':
            data  = {
                'asins' : [ asin ],
                'features' : [ 'collectionLibraryAvailability','expandTracklist','playlistLibraryAvailability','trackLibraryAvailability','hasLyrics'],
                'requestedContent' : 'MUSIC_SUBSCRIPTION',
                'deviceId' : self.deviceId,
                'deviceType' : self.deviceType,
                'musicTerritory' : self.musicTerritory,
                'customerId' : self.customerId
            }
            data = json.dumps(data)
        elif mode == 'itemLookup':
            data = {
                'asins': asin, # [asin], is an array!!
                'features': mediatype, # is an array!!
                'requestedContent': 'MUSIC_SUBSCRIPTION',
                'deviceId': self.deviceId,
                'deviceType': self.deviceType,
                'musicTerritory': self.musicTerritory,
                'customerId': self.customerId
            }
            data = json.JSONEncoder().encode(data)
        elif mode == 'itemLookup2ndRound':
            data = {
                'selectCriteriaList.member.1.attributeName':'status',
                'selectCriteriaList.member.1.comparisonType':'EQUALS',
                'selectCriteriaList.member.1.attributeValue':'AVAILABLE',
                'selectCriteriaList.member.2.attributeName':'trackStatus',
                'selectCriteriaList.member.2.comparisonType':'IS_NULL',
                'selectCriteriaList.member.2.attributeValue':'',
                'selectCriteriaList.member.3.attributeName':'albumAsin',
                'selectCriteriaList.member.3.comparisonType':'EQUALS',
                'selectCriteriaList.member.3.attributeValue':asin,
                'sortCriteriaList':'',
                'albumArtUrlsSizeList.member.1':'FULL',
                'albumArtUrlsSizeList.member.2':'LARGE',
                'albumArtUrlsRedirects':'false',
                'maxResults':   self.maxResults,
                'nextResultsToken':0,
                'Operation':'selectTrackMetadata',
                'distinctOnly':'false',
                'countOnly':'false',
                'caller':'getServerData',
                'selectedColumns.member.1':'albumArtistName',
                'selectedColumns.member.2':'albumAsin',
                'selectedColumns.member.3':'albumName',
                'selectedColumns.member.4':'albumReleaseDate',
                'selectedColumns.member.5':'artistAsin',
                'selectedColumns.member.6':'artistName',
                'selectedColumns.member.7':'asin',
                'selectedColumns.member.8':'assetType',
                'selectedColumns.member.9':'creationDate',
                'selectedColumns.member.10':'discNum',
                'selectedColumns.member.11':'duration',
                'selectedColumns.member.12':'extension',
                'selectedColumns.member.13':'purchased',
                'selectedColumns.member.14':'lastUpdatedDate',
                'selectedColumns.member.15':'name',
                'selectedColumns.member.16':'objectId',
                'selectedColumns.member.17':'orderId',
                'selectedColumns.member.18':'primaryGenre',
                'selectedColumns.member.19':'purchaseDate',
                'selectedColumns.member.20':'size',
                'selectedColumns.member.21':'sortAlbumArtistName',
                'selectedColumns.member.22':'sortAlbumName',
                'selectedColumns.member.23':'sortArtistName',
                'selectedColumns.member.24':'sortTitle',
                'selectedColumns.member.25':'status',
                'selectedColumns.member.26':'title',
                'selectedColumns.member.27':'trackNum',
                'selectedColumns.member.28':'trackStatus',
                'selectedColumns.member.29':'payerId',
                'selectedColumns.member.30':'physicalOrderId',
                'selectedColumns.member.31':'primeStatus',
                'selectedColumns.member.32':'purchased',
                'selectedColumns.member.33':'uploaded',
                'selectedColumns.member.34':'instantImport',
                'selectedColumns.member.35':'parentalControls',
                'selectedColumns.member.36':'albumCoverImageFull',
                'selectedColumns.member.37':'albumCoverImageLarge',
                'selectedColumns.member.38':'albumCoverImageMedium',
                'selectedColumns.member.39':'albumCoverImageSmall',
                'selectedColumns.member.40':'isMusicSubscription',
                'sortCriteriaList.member.1.sortColumn':'discNum',
                'sortCriteriaList.member.1.sortType':'ASC',
                'sortCriteriaList.member.2.sortColumn':'trackNum',
                'sortCriteriaList.member.2.sortType':'ASC',
                'ContentType':'JSON',
                'customerInfo.customerId':  self.customerId,
                'customerInfo.deviceId':    self.deviceId,
                'customerInfo.deviceType':  self.deviceType
            }
        elif mode == 'getStations':
            data = {
                'requestedContent': 'PRIME', #self.accessType,
                'lang':             self.locale,
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId
            }
            data = json.dumps(data)
        elif mode == 'createQueue':
            data = {
                'identifier': asin,
                'identifierType':'STATION_KEY',
                'customerInfo': {
                    'deviceId':     self.deviceId,
                    'deviceType':   self.deviceType,
                    'musicTerritory':self.musicTerritory,
                    'customerId':   self.customerId
                },
                'allowedParentalControls':{}
            }
            data = json.dumps(data)
        elif mode == 'getNextTracks':
            data = {
                'pageToken' : mediatype,
                'numberOfTracks':10,
                'customerInfo': {
                    'deviceId':     self.deviceId,
                    'deviceType':   self.deviceType,
                    'musicTerritory':self.musicTerritory,
                    'customerId':   self.customerId
                },
                'allowedParentalControls':{}
            }
            data = json.dumps(data)
        elif mode == 'getGenrePlaylist':
            data = {
                'identifier': asin,
                'identifierType': 'STATION_KEY',
                'customerInfo': {
                    'deviceId':     self.deviceId,
                    'deviceType':   self.deviceType,
                    'musicTerritory':self.musicTerritory,
                    'customerId':   self.customerId
                },
                'allowedParentalControls': {}
            }
        elif mode == 'getMetaData':
            data = {
                'trackIdList': asin,
                'attributeList': [
                    'albumCoverImageFull',
                    'albumCoverImageLarge',
                    'albumCoverImageMedium',
                    'albumCoverImageSmall',
                    'albumName',
                    'albumAsin',
                    'sortAlbumName',
                    'artistName',
                    'artistAsin',
                    'sortArtistName',
                    'sortAlbumArtistName',
                    'objectId',
                    'asin',
                    'title',
                    'status',
                    'primeStatus',
                    'isMusicSubscription',
                    'assetType',
                    'duration',
                    'discNum',
                    'trackNum',
                    'instantImport',
                    'purchased',
                    'uploaded',
                    'albumReleaseDate'
                ],
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId,
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType
            }
            data = json.dumps(data)
        elif mode == 'getTrack':
            data = {
                'customerId' : self.customerId,
                'deviceToken' : {
                    'deviceTypeId': self.deviceType,
                    'deviceId' :    self.deviceId
                },
                'bitRate' : self.audioQuality,
                'appMetadata' : { 'https' : 'true' },
                'clientMetadata' : { 'clientId' : 'WebCP' },
                'contentId' : {
                    'identifier' : asin,
                    'identifierType' : mediatype #, # 'ASIN',
                    #'bitRate' : self.audioQuality
                }
            }
            data = json.dumps(data)
        elif mode == 'getTrackHLS':
            data = {
                'customerId' : self.customerId,
                'deviceToken' : {
                    'deviceTypeId': self.deviceType,
                    'deviceId' :    self.deviceId
                },
                'bitRate' : self.audioQuality,
                'appMetadata' : { 'https' : 'true' },
                'clientMetadata' : { 'clientId' : 'WebCP' },
                'contentId' : {
                    'identifier' : asin,
                    'identifierType' : mediatype #, # 'ASIN',
                },
                'bitRateList' : [ self.audioQuality ],
                'hlsVersion': 'V3'
            }
            data = json.dumps(data)
        elif mode == 'getTrackDash':
            mID = self.getMaestroID()
            data = {
                'customerId' :          self.customerId,
                'deviceToken' : {
                    'deviceTypeId' :    self.deviceType,
                    'deviceId' :        self.deviceId
                },
                'contentIdList' : [{
                    'identifier' :      asin,
                    'identifierType' :  mediatype
                }],
                'bitrateTypeList' : [ self.audioQuality ],
                'musicDashVersionList' : [ 'V2' ],
                'appInfo' : {
                    'musicAgent': mID # 'Maestro/1.0 WebCP/1.0.202513.0 (9a46-5ad0-dmcp-8d19-ee5c6)'
                },
                'customerInfo' : {
                    'marketplaceId' :   self.marketplaceId,
                    'customerId' :      self.customerId,
                    'territoryId' :     self.musicTerritory,
                    'entitlementList' : [ 'HAWKFIRE' ]
                }
            }
            data = json.dumps(data)
        elif mode == 'getLicenseForPlaybackV2':
            """
            license_key must be a string template with 4 | separated fields: [license-server url]|[Header]|[Post-Data]|[Response] in which [license-server url]
            allows B{SSM} placeholder and [Post-Data] allows [b/B/R]{SSM} and [b/B/R]{SID} placeholders to transport the widevine challenge and if required the
            DRM SessionId in base64NonURLencoded, Base64URLencoded or Raw format.
            [Response] can be a.) empty or R to specify that the response payload of the license request is binary format, b.) B if the response payload is base64
            encoded or c.) J[licensetoken] if the license key data is located in a JSON struct returned in the response payload.
            inputstream.adaptive searches for the key [licensetoken] and handles the value as base64 encoded data.
            """
            mID = self.getMaestroID()
            # 'b{SSM}' base64NonURLencoded
            # 'B{SSM}' Base64URLencoded
            # 'R{SSM}' Raw format.
            data = {
                'DrmType':'WIDEVINE',
                'licenseChallenge':'b{SSM}',
                'customerId':self.customerId,
                'deviceToken':{
                    'deviceTypeId':self.deviceType,
                    'deviceId':self.deviceId
                },
                'appInfo':{
                    'musicAgent':mID
                }
            }
            data = json.dumps(data)
        elif mode == 'getSoccerMain':
            data = { # TODO
                'competitionId':    mediatype,
                'localTimeOffset': '+02:00',
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId,
                'lang':             self.locale
            }
            data = json.dumps(data)
        elif mode == 'getSoccerProgramDetails':
            data = { # TODO
                'programId':        mediatype,
                'localTimeOffset': '+02:00',
                'deviceId':         self.deviceId,
                'deviceType':       self.deviceType,
                'musicTerritory':   self.musicTerritory,
                'customerId':       self.customerId,
                'lang':             self.locale
            }
            data = json.dumps(data)
        elif mode == 'getSoccerStreamingURL':
            data = {
                'Operation':'com.amazon.amazonmusicaudiolocatorservice.model.getondemandstreamingurls#GetOnDemandStreamingURLs',
                'Service':'com.amazon.amazonmusicaudiolocatorservice.model#AmazonMusicAudioLocatorServiceExternal',
                'Input':{
                    'customerId':self.customerId,
                    'deviceToken':{
                        'deviceTypeId':self.deviceType,
                        'deviceId':self.deviceId
                    },
                    'appMetadata':{'appId':'WebCP'},
                    'clientMetadata':{
                        'clientId':self.deviceType,
                        'clientIpAddress':''},
                    'contentIdList':[{
                        'identifier':mediatype,
                        'identifierType':'MCID'}],
                    'protocol':'DASH'
                }
            }
            data = json.dumps(data)
        return data
    def amazonLogon(self):
        app_config = None
        while app_config is None:
            if os.path.isfile(self.cookieFile): # logon via cookie
                self.cj.load(self.cookieFile)
                head = self.prepReqHeader('')
                resp = requests.post(self.musicURL, data=None, headers=head, cookies=self.cj)
                for line in resp.iter_lines(decode_unicode=True):
                    if 'applicationContextConfiguration =' in line or 'amznMusic.appConfig =' in line:
                        app_config = json.loads(re.sub(r'^[^{]*', '', re.sub(r';$', '', line)))
                        break
                if app_config is None or app_config['isRecognizedCustomer'] == 0:
                    app_config = None
                    self.delCookies()
                    self.delCredentials()
                else:
                    self.appConfig(app_config)
                    self.setCookie()
                    break
            else: # logon via user password
                self.delCookies()
                if not self.getCredentials():
                    return False # user input missing
                self.br.open(self.logonURL)
                self.br.select_form(name="signIn")
                if not self.br.find_control("email").readonly:
                    #self.br["email"] = self.deEncrypt('de',self.userEmail)
                    self.br["email"] = self.userEmail
                #self.br["password"] = self.deEncrypt('de',self.userPassword)
                self.br["password"] = self.userPassword
                self.br.submit()
                resp = self.br.response()
                try:
                    self.content = unicode(resp.read(), "utf-8") # for kodi 18
                except:
                    self.content = str(resp.read(), encoding = 'utf-8') # for kodi 19
                #error_str = 'message error'
                if 'message error' in self.content:
                    xbmcgui.Dialog().ok(self.addonName, 'Logon issue')
                    return False
                self.setCookie()
                # self.cj.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
                # MFA check
                while 'action="verify"' in self.content or 'id="auth-mfa-remember-device' in self.content:
                    soup = self.parseHTML(self.content)
                    if 'cvf-widget-form cvf-widget-form-dcq fwcim-form a-spacing-none' in self.content:
                        # step 0 - account name
                        form = soup.find('form', class_="cvf-widget-form cvf-widget-form-dcq fwcim-form a-spacing-none")
                        # msgheading = 'Enter Account Name'
                        #self.log('### Account Name ###############')
                        #self.log(form)
                        msgheading = form.find('label', class_="a-form-label").getText().strip()
                        msgtxt = ""
                        inp = self.getUserInput(msgheading, msgtxt)
                        if inp:
                            self.br.select_form(nr=0)
                            self.br['dcq_question_subjective_1'] = inp
                        else:
                            return False
                    elif 'name="claimspicker"' in self.content:
                        # step 1
                        #self.log('MFA - form step 1')
                        form = soup.find_all('form', attrs={'name':'claimspicker'})
                        #self.log('### claimspicker ###############')
                        #self.log(form)
                        msgheading = form[0].find('h1').renderContents().strip()
                        msgtxt = form[0].findAll('div', class_='a-row')[1].renderContents().strip()
                        if xbmcgui.Dialog().yesno(msgheading, msgtxt):
                            self.br.select_form(nr=0)
                        else:
                            return False
                    elif 'name="code"' in self.content: # sms info
                        # step 2
                        #self.log('MFA - form step 2')
                        form = soup.find_all('form', class_='cvf-widget-form fwcim-form a-spacing-none')
                        #self.log('### CODE ###############')
                        #self.log(form)
                        #msgheading = form[0].find('div', class_='a-row a-spacing-none').renderContents().strip()
                        msgheading = form[0].findAll(lambda tag: tag.name == 'span' and not tag.attrs)
                        msgheading = msgheading[1].text + '\n' + msgheading[2].text
                        msgtxt = ''
                        inp = self.getUserInput(msgheading, msgtxt)
                        if inp:
                            self.br.select_form(nr=0)
                            self.br['code'] = inp
                        else:
                            return False
                    elif 'auth-mfa-form' in self.content:
                        msg = soup.find('form', id='auth-mfa-form')
                        #self.log('### MFA ###############')
                        #self.log(msg)
                        msgheading = msg.p.renderContents().strip()
                        msgtxt = ''
                        inp = self.getUserInput(msgheading, msgtxt)
                        if inp:
                            xbmc.executebuiltin('ActivateWindow(busydialog)')
                            self.br.select_form(nr=0)
                            self.br['otpCode'] = inp
                        else:
                            return False
                    else: # Unknown form
                        return False
                    self.br.submit()
                    resp = self.br.response()
                    try:
                        self.content = unicode(resp.read(), "utf-8") # for kodi 18
                    except:
                        self.content = str(resp.read(), encoding = 'utf-8') # for kodi 19
                self.content = self.content.replace("\\","")
                captcha_match = re.compile('ap_captcha_title', re.DOTALL).findall(self.content)
                if captcha_match:
                    xbmc.executebuiltin(unicode('XBMC.Notification("Error:","Captcha required! Logon is not possible.",5000,)').encode("utf-8"))
                    self.log("ERROR: Captcha required!")
                    return False
        return True
    # music content
    def menuHome(self):
        self.createList([   {'txt':30023,'fct':'menuPlaylists','img':'playlists.jpg'},
                            {'txt':30024,'fct':'menuAlbums','img':'albums.jpg'},
                            {'txt':30022,'fct':'menuSongs','img':'songs.jpg'},
                            {'txt':30008,'fct':'menuStations','img':'stations.jpg'},
                            {'txt':30015,'fct':'getGenres','img':'genres.jpg'},
                            {'txt':30027,'fct':'menuArtists','img':'artists.jpg'},
                            {'txt':30035,'fct':'menuSoccer','img':'soccer.jpg'}
        ])
    def menuPlaylists(self):
        self.createList([   {'txt':30013,'fct':'searchPlayLists','img':'search.png'},
                            {'txt':30032,'fct':'search1PlayLists','img':'search.png','search':self.getSetting(self.sPlayLists[0])},
                            {'txt':30033,'fct':'search2PlayLists','img':'search.png','search':self.getSetting(self.sPlayLists[1])},
                            {'txt':30034,'fct':'search3PlayLists','img':'search.png','search':self.getSetting(self.sPlayLists[2])},
                            {'txt':30003,'fct':'getRecomPlayLists','img':'playlists.jpg'},
                            {'txt':30002,'fct':'getNewPlayLists','img':'playlists.jpg'},
                            {'txt':30001,'fct':'getPopularPlayLists','img':'playlists.jpg'},
                            {'txt':30018,'fct':'getFollowedPlayLists','img':'playlists.jpg'},
                            {'txt':30019,'fct':'getOwnedPlaylists','img':'playlists.jpg'}
        ],True)
    def menuAlbums(self):
        self.createList([   {'txt':30010,'fct':'searchAlbums','img':'search.png'},
                            {'txt':30032,'fct':'search1Albums','img':'search.png','search':self.getSetting(self.sAlbums[0])},
                            {'txt':30033,'fct':'search2Albums','img':'search.png','search':self.getSetting(self.sAlbums[1])},
                            {'txt':30034,'fct':'search3Albums','img':'search.png','search':self.getSetting(self.sAlbums[2])},
                            {'txt':30004,'fct':'getRecomAlbums','img':'albums.jpg'},
                            {'txt':30012,'fct':'getPurAlbums','img':'albums.jpg'},
                            {'txt':30007,'fct':'getAllAlbums','img':'albums.jpg'}
        ],True)
    def menuSongs(self):
        self.createList([   {'txt':30011,'fct':'searchSongs','img':'search.png'},
                            {'txt':30032,'fct':'search1Songs','img':'search.png','search':self.getSetting(self.sSongs[0])},
                            {'txt':30033,'fct':'search2Songs','img':'search.png','search':self.getSetting(self.sSongs[1])},
                            {'txt':30034,'fct':'search3Songs','img':'search.png','search':self.getSetting(self.sSongs[2])},
                            {'txt':30009,'fct':'getPurSongs','img':'songs.jpg'},
                            {'txt':30006,'fct':'getAllSongs','img':'songs.jpg'},
                            {'txt':30017,'fct':'getRecentlyPlayed','img':'songs.jpg'},
                            {'txt':30021,'fct':'getRecentlyAddedSongs','img':'songs.jpg'}
        ],True)
    def menuStations(self):
        self.createList([   {'txt':30016,'fct':'searchStations','img':'search.png'},
                            {'txt':30032,'fct':'search1Stations','img':'search.png','search':self.getSetting(self.sStations[0])},
                            {'txt':30033,'fct':'search2Stations','img':'search.png','search':self.getSetting(self.sStations[1])},
                            {'txt':30034,'fct':'search3Stations','img':'search.png','search':self.getSetting(self.sStations[2])},
                            {'txt':30005,'fct':'getRecomStations','img':'stations.jpg'},
                            {'txt':30026,'fct':'getStations','img':'stations.jpg'},
                            {'txt':30025,'fct':'getAllArtistsStations','img':'stations.jpg'}
        ],True)
    def menuArtists(self):
        self.createList([   {'txt':30014,'fct':'searchArtist','img':'search.png'},
                            {'txt':30032,'fct':'search1Artists','img':'search.png','search':self.getSetting(self.sArtists[0])},
                            {'txt':30033,'fct':'search2Artists','img':'search.png','search':self.getSetting(self.sArtists[1])},
                            {'txt':30034,'fct':'search3Artists','img':'search.png','search':self.getSetting(self.sArtists[2])}
        ],True)
    def menuSoccer(self):
        self.createList([   {'txt':30036,'fct':'soccerBUND','img':'soccer_BUND.jpg'},
                            {'txt':30037,'fct':'soccerBUND2','img':'soccer_BUND2.jpg'},
                            {'txt':30038,'fct':'soccerDFBPOKAL','img':'soccer_DFBPOKAL.jpg'},
                            {'txt':30039,'fct':'soccerCHAMP','img':'soccer_CHAMP.jpg'},
                            {'txt':30040,'fct':'soccerSUPR','img':'soccer_SUPR.jpg'}
        ])
    def createList(self,data,dynentry=False,soccer=False):
        itemlist = []
        url = None
        for item in data:
            isFolder = True
            if dynentry and 'search' in item and item['search'] == '':
                continue
            if soccer:
                title = item['txt']
            else:
                title = self.translation(item['txt'])
            if dynentry and 'search' in item:
                title += str(item['search'])
            li = xbmcgui.ListItem(label=title)
            li.setInfo(type="music", infoLabels={"title": title})
            if 'img' in item:
                if 'http' in item['img']:
                    url = item['img']
                else:
                    url = '{}/resources/images/{}'.format(self.addonFolder, item['img'])
                li.setArt({'icon':url,'thumb':url,'fanart':url,'poster':url,'banner':url,'landscape':url})
            url = '{}?mode={}'.format(self.addonBaseUrl,str(item['fct']))
            if soccer:
                url+="&objectId={}".format(str(item['target']))
                li.setProperty('IsPlayable', 'true')
                isFolder = False
            itemlist.append((url, li, isFolder))
        xbmcplugin.setContent(self.addonHandle, 'albums')
        xbmcplugin.addDirectoryItems(self.addonHandle, itemlist, len(itemlist))
        xbmcplugin.endOfDirectory(self.addonHandle)
    # get music information
    def lookup(self,asin):
        mediatype = ['playlistLibraryAvailability','expandTracklist','trackLibraryAvailability','collectionLibraryAvailability']
        data = self.amzCall( self.API_lookup,'itemLookup',None,asin,mediatype)
        sel = ''
        if   data['metadata']['albumList'] is not None:
            sel = 'albumList'
        elif data['metadata']['artistList'] is not None:
            sel = 'artistList'
        elif data['metadata']['playlistList'] is not None:
            sel = 'playlistList'
        elif data['metadata']['trackList'] is not None:
            sel = 'trackList'
        else:
            data = self.amzCall(self.API_cirrus, 'itemLookup2ndRound', '/my/albums', [asin], None)['selectTrackMetadataResponse']['selectTrackMetadataResult']
            sel = 'trackInfoList'
        self.setAddonContent(sel,data[sel],'songs')
    def getRecentlyPlayed(self,mediatype):
        items = self.amzCall(self.API_GetRecentTrackActivity,'recentlyplayed',None,None,mediatype)['recentActivityMap']['PLAYED']
        self.setAddonContent('recentlyplayed',items,'songs')
    def getRecentlyAddedSongs(self):
        items = self.amzCall(self.API_cirrus,'recentlyaddedsongs',None,None,None)['selectTrackMetadataResponse']['selectTrackMetadataResult']
        self.setAddonContent('recentlyaddedsongs',items,'songs')
    def getPlayLists(self,mediatype):
        items = self.amzCall(self.API_getTopMusicEntities,'playlist',None,None,mediatype)
        # data structure is similar to lookup
        self.setAddonContent('playlists',items,'albums')
    def getFollowedPlayLists(self):
        items = self.amzCall(self.API_getFollowedPlaylistsInLibrary,'followedplaylists',None,None,None)
        self.setAddonContent('followedplaylists',items,'albums')
    def getOwnedPlaylists(self):
        items = self.amzCall(self.API_getOwnedPlaylistsInLibrary,'getownedplaylists',None,None,None)
        self.setAddonContent('ownedplaylists',items,'albums')
    def getPlaylistsByIdV2(self,asin):
        items = self.amzCall(self.API_getPlaylistsByIdV2,'getplaylistsbyid',None,asin,None)
        self.setAddonContent('getplaylistsbyid',items,'songs')
    def getStations(self,mediatype):
        items = self.amzCall(self.API_getStationSections,'getStations','/stations')
        self.setAddonContent(mediatype,items,'albums')
    def getGenrePlaylist(self,asin):
        items = self.amzCall(self.API_createQueue,'getGenrePlaylist',None,asin)
        self.setAddonContent('genreplaylist',items,'albums')
    def getRecommendations(self,mode,mediatype):
        resp = self.amzCall(self.API_getBrowseRecommendations,'recommendations',None,None,mediatype)
        sel = ''
        if   resp['recommendations'][0]['recommendationType'] == 'PLAYLIST':
            sel = 'recplaylists'
        elif resp['recommendations'][0]['recommendationType'] == 'ALBUM':
            sel = 'recalbums'
        elif resp['recommendations'][0]['recommendationType'] == 'STATION':
            sel = 'recstations'
        self.setAddonContent(sel,resp['recommendations'][0],'albums')
    def getPurchased(self,mode,ctype):
        resp = self.amzCall(self.API_cirrus,'getPurchased',None,None,mode)
        items = resp['searchLibraryResponse']['searchLibraryResult']
        if ctype == 'songs':
            mode = 'purchasedsongs'
        elif ctype == 'albums':
            mode = 'purchasedalbums'
        self.setAddonContent(mode,items,ctype)
    def searchItems(self,mode=None,txt=None,query=None):
        if query == None:
            if self.addonArgs.get('token', False):
                query = self.addonArgs.get('query', [''])[0]
            else:
                query = self.getUserInput(self.translation(txt), '')
                if not query:
                    return
        resp = self.amzCall( self.API_search , 'searchItems' , '/search' , query,mode )
        items = resp['results'][0]
        if   mode[0] == 'albums':
            if not txt == None:
                self.setSearch('albums',query)
            self.setAddonContent('searchitems',items,'albums','albums',query)
        elif mode[0] == 'tracks':
            if not txt == None:
                self.setSearch('tracks',query)
            self.setAddonContent('searchitems',items,'songs','tracks',query)
        elif mode[0] == 'playlists':
            if not txt == None:
                self.setSearch('playlists',query)
            self.setAddonContent('searchplaylists',items,'albums',None,query)
        elif mode[0] == 'artists':
            if not txt == None:
                self.setSearch('artists',query)
            self.setAddonContent('searchartists',items,'songs',None,query)
        elif mode[0] == 'stations':
            if not txt == None:
                self.setSearch('stations',query)
            self.setAddonContent('searchstations',items,'albums',None,query)
    def getArtistDetails(self,asin):
        resp = self.amzCall(self.API_artistDetailsMetadata,'getArtistDetails',None,asin,None)
        items = resp
        self.setAddonContent('artistdetails',items,'albums',None,asin)
    def createQueue(self,asin):
        resp = self.amzCall(self.API_createQueue,'createQueue',None,asin,None)
        token = resp['queue']['pageToken']
        tracklist = resp['trackMetadataList']
        i = 1
        while token: # 5 songs per loop
            resp = self.amzCall(self.API_QueueGetNextTracks,'getNextTracks',None,asin,token)
            token = resp['nextPageToken']
            for item in resp['trackMetadataList']:
                tracklist.append(item)
            if i == 10:
                break
            i += 1
        self.setAddonContent('stationList',tracklist,'songs')
    # kodi visualization
    def getMeta(self,resp,filter):
        meta = []
        for item in resp:
            if len(filter) == 1:
                meta.append(item[filter['array1']])
            else:
                meta.append(item[filter['array1']][filter['array2']])
        seen = set()
        uniq = [x for x in meta if x not in seen and not seen.add(x)] # make it unique
        return self.amzCall(self.API_lookup,'itemLookup',None,uniq,['fullAlbumDetails'])#['albumList']
    def getMetaTracks(self,filter):
        return self.amzCall(self.API_V3getTracks,'getMetaTracks',None,filter,None)
    def setData(self,item,filter):
        if 'update' in filter and filter['update']:
            info = filter['info']
            meta = filter['meta']
        else:
            info = {
                'tracknumber':  None,
                'discnumber':   None,
                'duration':     None,
                'year':         None,
                'genre':        None,
                'album':        None,
                'artist':       None,
                'title':        None,
                'rating':       None
            }
            meta = {
                'mode':         None,
                'asin':         None,
                'objectId':     '',
                'thumb':        None,
                'purchased':    False,
                'isPrime':      False,
                'isUnlimited':  False,
                'color':        '%s',
                'isPlayable':   'true'
            }
            meta['mode'] = filter['mode']
        # tracknumber : discnumber : duration : year : genre : album : artist : title : rating
        if 'isAlbum' in filter and filter['isAlbum']:
            filter['isAlbum'] = filter['isAlbum']
        else:
            if 'trackNum' in item:
                info['tracknumber'] = item['trackNum']
            if 'trackCount' in item:
                info['tracknumber'] = item['trackCount']

        if 'discNum' in item:
            info['discnumber'] = item['discNum']

        if 'duration' in item:
            info['duration'] = item['duration']
        elif 'durationSeconds' in item:
            info['duration'] = item['durationSeconds']

        if 'albumReleaseDate' in item:
            info['year'] = item['albumReleaseDate'][:4]

        if 'primaryGenre' in item:
            info['genre'] = item['primaryGenre']
        elif 'genreName' in item:
            info['genre'] = item['genreName']
        elif 'productDetails' in item:
            info['genre'] = item['productDetails']['primaryGenreName']

        if 'albumName' in item:
            info['album'] = item['albumName']
        if 'description' in item:
            info['album'] = item['description']
        if 'stationTitle' in item:
            info['album'] = item['stationTitle']
        if 'album' in item:
            try:
                info['album'] = item['album']['name']
            except:
                info['album'] = item['album']['title']

        if 'albumArtistName' in item:
            info['artist'] = item['albumArtistName']
        if 'artist' in item:
            info['artist'] = item['artist']['name']
        if 'artistName' in item:
            info['artist'] = item['artistName']

        if 'stationTitle' in item:
            info['title'] = item['stationTitle']
        if 'displayName' in item:
            info['title'] = item['displayName']

        if 'isAlbum' in filter and filter['isAlbum']:
            if info['title'] == None and 'albumName' in item:
                info['title'] = item['albumName']
        else:
            if 'title' in item:
                info['title'] = item['title']
            if info['title'] == None and 'name' in item:
                info['title'] = item['name']

        if 'reviews' in item:
            info['rating'] = item['reviews']['average']
        if 'rating' in item:
            info['rating'] = item['rating']
        if 'averageOverallRating' in item:
            info['rating'] = item['averageOverallRating']

        # mode : asin : objectId : thumb : purchased : isPrime : isUnlimited
        # order of 'playlistId' and 'asin' is important. Do not change the order -> reason: followed playlists
        if 'playlistId' in item:
            meta['asin'] = item['playlistId']
        if 'asin' in item:
            meta['asin'] = item['asin']
        if 'seedId' in item:
            meta['asin'] = item['seedId']
        if 'categoryId' in item:
            meta['asin'] = item['categoryId']
        if 'stationKey' in item:
            meta['asin'] = item['stationKey']
        if 'identifier' in item:
            meta['asin'] = item['identifier']
        if 'isAlbum' in filter and filter['isAlbum']:
            if 'albumAsin' in item:
                meta['asin'] = item['albumAsin']

        if 'trackId' in item:
            meta['objectId'] = item['trackId']
        if 'objectId' in item:
            meta['objectId'] = item['objectId']
        if 'stationSeedId' in item:
            meta['objectId'] = item['stationSeedId']

        if 'image' in item:
            meta['thumb'] = item['image']
        if 'imageFull' in item:
            meta['thumb'] = item['imageFull']
        if 'albumCoverImageFull' in item:
            meta['thumb'] = item['albumCoverImageFull']
        if 'albumArtImageUrl' in item:
            meta['thumb'] = item['albumArtImageUrl']
        if 'stationImageUrl' in item and item['stationImageUrl'] is not None:
            meta['thumb'] = item['stationImageUrl']
        if 'foregroundImageUrl' in item and item['foregroundImageUrl'] is not None:
            meta['thumb'] = item['foregroundImageUrl']
        if 'artOriginal' in item:
            meta['thumb'] = item['artOriginal']['URL']
        if 'artFull' in item:
            meta['thumb'] = item['artFull']['URL']
        if 'artUrlMap' in item:
            meta['thumb'] = item['artUrlMap']['FULL']
        if 'fourSquareImage' in item:
            meta['thumb'] = item['fourSquareImage']['url']
        try:
            meta['thumb'] = item['album']['image']
        except:
            pass

        if (('purchased' in item and (item['purchased'] == True or item['purchased'] == 'true')) or
            ('isPurchased' in item and (item['isPurchased'] == True or item['isPurchased'] == 'true'))):
            meta['purchased'] = True

        if (('isPrime' in item and (item['isPrime'] == True or item['isPrime'] == 'true')) or
            ('primeStatus' in item and item['primeStatus'] == 'PRIME') or
            ('serviceTier' in item and item['serviceTier'] == 'PRIME') or
            ('playlistId' in item) or
            ('isStation' in filter and filter['isStation'] == True)):
            meta['isPrime'] = True

        if ('isMusicSubscription' in item and (item['isMusicSubscription'] == True or item['isMusicSubscription'] == 'true')):
            meta['isUnlimited'] = True

        if self.showcolentr == 'true':
            if meta['purchased']:
                meta['color'] = '[COLOR gold]%s[/COLOR]'
            elif meta['isPrime'] or 'stationMapIds' in item:
                meta['color'] = '%s'
            elif meta['isUnlimited']:
                meta['color'] = '[COLOR blue]%s[/COLOR]'
            else:
                meta['color'] = '[COLOR red]%s[/COLOR]'

        if ((self.accessType == 'PRIME'     and not meta['isPrime'] and not meta['purchased']) or
            (self.accessType == 'UNLIMITED' and not meta['isPrime'] and not meta['purchased'] and not meta['isUnlimited'] )):
            meta['isPlayable'] = 'false'
        else:
            meta['isPlayable'] = 'true'
        #self.log(info)
        #self.log(meta)
        return (info,meta)
    def setItem(self,inf,met):
        li = xbmcgui.ListItem(label=met['color'] % (inf['title']))
        if not met['thumb'] == None:
            li.setArt(self.setImage(met['thumb']))
        li.setInfo(type="music", infoLabels=inf)
        if met['isPlayable'] == 'false': # workaround for unplayable items
            met['mode'] = '1234'
        url = self.setUrl(inf,met)
        li.setProperty('IsPlayable', met['isPlayable'])
        # self.log(url)
        # self.log(inf)
        # self.log(met)
        return (url,li)
    def setImage(self,img):
        if self.showimages == 'true':
            return ({'icon':img,'thumb':img,'fanart':img,'poster':img,'banner':img,'landscape':img})
        else:
            return ({'thumb':img}) # there is a bug in the listitems, after setting multiple arts, setInfo shows the Genre only
    def setPaginator(self,nextToken,query=None,asin=None):
        li = xbmcgui.ListItem(label=self.translation(30020))
        li.setProperty('IsPlayable', 'false')
        url = "{}?mode={}&token={}".format(self.addonBaseUrl,str(self.addonMode[0]),str(nextToken))
        if query:
            #url += "&query={}".format(urllib.quote_plus(query.encode("utf8")))
            url += "&query={}".format(urlquoteplus(query.encode("utf8"))) # python 3 correction
        if asin:
            #url += "&asin={}".format(urllib.quote_plus(asin.encode("utf8")))
            url += "&asin={}".format(urlquoteplus(asin.encode("utf8"))) # python 3 correction
        return (url, li, True)
    def setUrl(self,inf,met):
        url = {
            'mode':     met['mode'],
            'asin':     met['asin']
            #'objectId': met['objectId']
            #'title':    inf['title'].encode("utf8"),
            #'thumb':    met['thumb']
        }
        if met['objectId'] is not None:
            url['objectId'] = met['objectId']
        #return '{}?{}'.format(self.addonBaseUrl,urllib.urlencode(url))
        return '{}?{}'.format(self.addonBaseUrl,urlencode(url)) # python 3 correction
    def setAddonContent(self,mode,param,ctype,stype=None,query=None):
        itemlist = []
        meta = []
        mediatype = ['playlistLibraryAvailability','expandTracklist','trackLibraryAvailability','collectionLibraryAvailability']
        if   mode == 'albumList' or mode == 'playlistList':
            meta = self.getMetaTracks(param[0]['asin'])['resultList']
            for item in param[0]['tracks']:
                inf, met = self.setData(item,{'mode':'getTrack'})
                for i in meta:
                    if item['asin'] == i['metadata']['asin']:
                        inf, met = self.setData(i['metadata'],{'info':inf,'meta':met,'update':True})
                    else:
                        continue
                inf['album'] = param[0]['title']
                inf['rating'] = param[0]['reviews']['average']
                met['thumb'] = param[0]['image']
                met['album'] = param[0]['title']
                url, li  = self.setItem(inf,met)
                if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                    continue
                itemlist.append((url, li, False))
        elif mode == 'artistList':      # no content at the moment
            self.log('artistList')
        elif mode == 'trackInfoList':           # track info list
            for item in param:
                meta.append(item['metadata']['asin'])
            meta = self.amzCall(self.API_lookup,'itemLookup',None,meta,mediatype)['trackList']
            for item in param:
                inf, met = self.setData(item['metadata'],{'mode':'getTrack'})
                for i in meta:
                    if item['metadata']['asin'] == i['asin']:
                        inf, met = self.setData(i,{'info':inf,'meta':met,'update':True})
                    else:
                        continue
                url, li  = self.setItem(inf,met)
                if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                    continue
                itemlist.append((url, li, False))
        elif mode == 'stationList':             # station playlist
            for item in param:
                meta.append(item['identifier'])
            meta = self.amzCall(self.API_lookup,'itemLookup',None,meta,mediatype)['trackList']
            for item in param:
                inf, met = self.setData(item,{'mode':'getTrack'})
                for i in meta:
                    if item['identifier'] == i['asin']:
                        inf, met = self.setData(i,{'info':inf,'meta':met,'update':True})
                    else:
                        continue
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, False))
        elif mode == 'playlists':               # playlists
            for item in param['playlistList']:
                inf, met = self.setData(item,{'mode':'lookup'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            if not param['nextTokenMap']['playlist'] == None and not len(param['playlistList']) < self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextTokenMap']['playlist']))
        elif mode == 'followedplaylists':       # followed playlists
            for item in param['playlists']:
                inf, met = self.setData(item,{'mode':'lookup'})
                url, li  = self.setItem(inf,met)
            #if not param['nextTokenMap']['playlist'] == None and not len(param['playlistList']) < self.maxResults: # next page
            #    itemlist.append(self.setPaginator(param['nextTokenMap']['playlist']))
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
        elif mode == 'ownedplaylists':          # owned playlists
            for item in param['playlists']:
                inf, met = self.setData(item,{'mode':'getPlaylistsByIdV2'})
                url, li  = self.setItem(inf,met)
            #if not param['nextTokenMap']['playlist'] == None and not len(param['playlistList']) < self.maxResults: # next page
            #    itemlist.append(self.setPaginator(param['nextTokenMap']['playlist']))
                if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                    continue
                itemlist.append((url, li, True))
        elif mode == 'getplaylistsbyid':        # playlists by Id
            for item in param['playlists']:
                for track in item['tracks']:
                    meta.append(track['metadata']['requestedMetadata']['asin'])
            meta = self.amzCall(self.API_lookup,'itemLookup',None,meta,mediatype)['trackList']
            for item in param['playlists']:
                for track in item['tracks']:
                    inf, met = self.setData(track['metadata']['requestedMetadata'],{'mode':'getTrack'})
                    for i in meta:
                        if track['metadata']['requestedMetadata']['asin'] == i['asin']:
                            inf, met = self.setData(i,{'info':inf,'meta':met,'update':True})
                        else:
                            continue
                    url, li  = self.setItem(inf,met)
                #if not param['nextTokenMap']['playlist'] == None and not len(param['playlistList']) < self.maxResults: # next page
                #    itemlist.append(self.setPaginator(param['nextTokenMap']['playlist']))
                    if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                        continue
                    itemlist.append((url, li, False))
        elif mode == 'recplaylists':            # recommended playlists
            for item in param['playlists']:
                inf, met = self.setData(item,{'mode':'lookup'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            if not param['nextResultsToken'] == None and len(param['playlists']) <= self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextResultsToken']))
        elif mode == 'recalbums':               # recommended albums
            for item in param['albums']:
                inf, met = self.setData(item,{'mode':'lookup','isAlbum':True})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            if not param['nextResultsToken'] == None and len(param['albums']) <= self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextResultsToken']))
        elif mode == 'recstations':             # recommended stations
            for item in param['stations']:
                inf, met = self.setData(item,{'mode':'createQueue'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            if not param['nextResultsToken'] == None and len(param['stations']) <= self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextResultsToken']))
        elif mode == 'recentlyplayed':          # recently played songs
            for item in param['recentTrackList']:
                inf, met = self.setData(item,{'mode':'getTrack'})
                url, li  = self.setItem(inf,met)
                if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                    continue
                itemlist.append((url, li, False))
            if not param['nextToken'] == None and len(param['recentTrackList']) <= self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextToken']))
        elif mode == 'recentlyaddedsongs':      # recently added songs
            for item in param['trackInfoList']:
                meta.append(item['metadata']['asin'])
            meta = self.amzCall(self.API_lookup,'itemLookup',None,meta,mediatype)['trackList']
            for item in param['trackInfoList']:
                inf, met = self.setData(item['metadata'],{'mode':'getTrack'})
                for i in meta:
                    if item['metadata']['asin'] == i['asin']:
                        inf, met = self.setData(i,{'info':inf,'meta':met,'update':True})
                    else:
                        continue
                url, li  = self.setItem(inf,met)
                if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                    continue
                itemlist.append((url, li, False))
            if not param['nextResultsToken'] == None and len(param['trackInfoList']) <= self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextResultsToken']))
        elif mode == 'stations':                # (all) stations
            items = param['categories'].get('allStations')['stationMapIds']
            for item in items:
                inf, met = self.setData(param['stations'].get(item),{'mode':'createQueue'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
        elif mode == 'stationsallartists':      # (all artists) stations
            items = param['categories'].get('artistsAZ')['stationMapIds']
            for item in items:
                inf, met = self.setData(param['stations'].get(item),{'mode':'createQueue'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
        elif mode == 'genres':                  # genre 1st level
            for sec in param['sections']:
                if sec['sectionId'] == 'genres':
                    for item in sec['categoryMapIds']:
                        inf, met = self.setData(param['categories'].get(item),{'mode':'getGenres2','isStation':True})
                        url, li  = self.setItem(inf,met)
                        #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                        #    continue
                        itemlist.append((url, li, True))
                else:
                    continue
        elif mode == 'genres2':                 # genres 2nd level
            asin = self.addonArgs.get('asin', None)[0]
            items = param['categories'].get(asin)['stationMapIds']
            for item in items:
                inf, met = self.setData(param['stations'].get(item),{'mode':'createQueue'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
        elif mode == 'purchasedalbums':         # purchased and owned albums
            for item in param['searchReturnItemList']:
                meta.append(item['metadata']['asin'])
            meta = self.amzCall(self.API_lookup,'itemLookup',None,meta,['fullAlbumDetails'])['albumList']
            for item in param['searchReturnItemList']:
                inf, met = self.setData(item['metadata'],{'mode':'lookup','isAlbum':True})
                for i in meta:
                    if item['metadata']['albumAsin'] == i['asin']:
                        inf, met = self.setData(i,{'info':inf,'meta':met,'isAlbum':True,'update':True})
                    else:
                        continue
                url, li  = self.setItem(inf,met)
                itemlist.append((url, li, True))
            if not param['nextResultsToken'] == None and len(param['searchReturnItemList']) <= self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextResultsToken']))
        elif mode == 'purchasedsongs':          # purchased and owned songs
            meta = self.getMeta(param['searchReturnItemList'],{'array1':'metadata','array2':'albumAsin'})['albumList']
            for item in param['searchReturnItemList']:
                inf, met = self.setData(item['metadata'],{'mode':'getTrack'})
                #for i in meta:
                #    if item['metadata']['albumAsin'] == i['asin']:
                #        inf, met = self.setData(i,{'info':inf,'meta':met,'update':True})
                #    else:
                #        continue
                url, li  = self.setItem(inf,met)
                if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                    continue
                itemlist.append((url, li, False))
            if not param['nextResultsToken'] == None and len(param['searchReturnItemList']) <= self.maxResults: # next page
                itemlist.append(self.setPaginator(param['nextResultsToken']))
        elif mode == 'searchitems':             # search items (songs / albums)
            for item in param['hits']:
                if stype == 'albums':
                    mode = {'mode':'lookup'}
                    fold = True
                elif stype == 'tracks' or stype == 'artists':
                    mode = {'mode':'getTrack'}
                    fold = False
                inf, met = self.setData(item['document'],mode)
                url, li  = self.setItem(inf,met)
                if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false' and mode['mode'] == 'getTrack':
                    continue
                itemlist.append((url, li, fold))
            try:
                if not param['nextPage'] == None and len(param['hits']) <= self.maxResults: # next page
                    itemlist.append(self.setPaginator(param['nextPage'],query))
            except:
                pass
        elif mode == 'searchplaylists':         # search playlists
            for item in param['hits']:
                inf, met = self.setData(item['document'],{'mode':'lookup'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            try:
                if not param['nextPage'] == None and len(param['hits']) <= self.maxResults: # next page
                    itemlist.append(self.setPaginator(param['nextPage'],query))
            except:
                pass
        elif mode == 'searchartists':           # search artists
            for item in param['hits']:
                inf, met = self.setData(item['document'],{'mode':'getArtistDetails'})#,'isAlbum':True})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            try:
                if not param['nextPage'] == None and len(param['hits']) <= self.maxResults: # next page
                    itemlist.append(self.setPaginator(param['nextPage'],query))
            except:
                pass
        elif mode == 'searchstations':          # search stations
            for item in param['hits']:
                inf, met = self.setData(item['document'],{'mode':'createQueue','query':query})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            try:
                if not param['nextPage'] == None and len(param['hits']) <= self.maxResults: # next page
                    itemlist.append(self.setPaginator(param['nextPage'],query))
            except:
                pass
        elif mode == 'artistdetails':           # artitist details (albums)
            for item in param['albumList']:
                inf, met = self.setData(item,{'mode':'lookup'})
                url, li  = self.setItem(inf,met)
                #if self.showUnplayableSongs == 'false' and met['isPlayable'] == 'false':
                #    continue
                itemlist.append((url, li, True))
            try:
                if len(param['albumList']) == self.maxResults:
                    itemlist.append(self.setPaginator(param['nextTokenMap']['album'],None,query))
                    itemlist.append((url, li, True))
            except:
                pass
        xbmcplugin.addDirectoryItems(self.addonHandle, itemlist, len(itemlist))
        xbmcplugin.setContent(self.addonHandle, ctype)
        xbmcplugin.endOfDirectory(self.addonHandle)
        xbmc.sleep(100)
    # play music
    def getTrack(self,asin,objectId):
        song = self.tryGetStream(asin,objectId)
        if song == None:
            song = self.tryGetStreamHLS(asin,objectId)
        if song == None:
            song = self.tryGetStreamDash(asin,objectId)
            return
        if song == None:
            xbmc.PlayList(0).clear()
            xbmc.Player().stop()
            xbmc.executebuiltin(unicode('XBMC.Notification("Information:","Playback not possible! Cannot find streaming URL.",10000,)').encode("utf-8"))
            return False
        li = xbmcgui.ListItem(path=song)
        li.setContentLookup(False)
        li.setInfo('video', '')
        xbmcplugin.setResolvedUrl(self.addonHandle, True, listitem=li)
    def tryGetStream(self,asin,objectId):
        if objectId == None:
            resp = self.amzCall(self.API_stream,'getTrack',None,asin,'ASIN')
            obj = json.loads(resp.text)
            if 'statusCode' in obj and obj['statusCode'] == 'MAX_CONCURRENCY_REACHED':
                xbmc.PlayList(0).clear()
                xbmc.Player().stop()
                xbmc.executebuiltin(unicode('XBMC.Notification("Information:","Playback not possible! Another instance is running.",10000,)').encode("utf-8"))
                return None
            try:
                song = obj['contentResponse']['urlList'][0]
            except:
                return None
        else:
            resp = self.amzCall(self.API_stream,'getTrack',None,objectId,'COID')
            obj = json.loads(resp.text)
            if 'statusCode' in obj and obj['contentResponse']['statusCode'] == 'CONTENT_NOT_ELIGIBLE' or obj['contentResponse']['statusCode'] == 'BAD_REQUEST':
                return None
            try:
                song = obj['contentResponse']['urlList'][0]
            except:
                return None
        return song
    def tryGetStreamHLS(self,asin,objectId):
        resp = self.amzCall(self.API_streamHLS,'getTrackHLS',None,asin,'ASIN')
        manifest = re.compile('manifest":"(.+?)"',re.DOTALL).findall(resp.text)
        if manifest:
            return self.writeSongFile(manifest,'m3u8')
        else:
            return None
    def tryGetStreamDash(self,asin,objectId):
        resp = self.amzCall(self.API_streamDash,'getTrackDash',None,asin,'ASIN')
        manifest = json.loads(resp.text)['contentResponseList'][0]['manifest']
        if manifest:
            lic = self.getLicenseKey()
            song = self.writeSongFile(manifest,'mpd')
            li = xbmcgui.ListItem(path=song)
            li.setProperty('inputstreamaddon', 'inputstream.adaptive')
            li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            li.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            li.setProperty('inputstream.adaptive.license_key', lic)
            li.setInfo('video', '')
            li.setMimeType('application/dash+xml')
            li.setContentLookup(False)
            xbmcplugin.setResolvedUrl(self.addonHandle, True, listitem=li)
        else:
            return None
    def writeSongFile(self,manifest,ftype='m3u8'):
        song = '{}/song.{}'.format(self.addonUDatFo,ftype) # '/song.mp4'
        m3u_string = ''
        temp_file = xbmcvfs.File(song, 'w')
        if ftype == 'm3u8':
            m3u_string = manifest[0]
        if ftype == 'mpd':
            m3u_string = manifest
            song = '{}/song.{}'.format(self.addonUDatFo,ftype)
        # m3u_string = m3u_string.replace("\\n", os.linesep)
        m3u_string = str(m3u_string.replace("\\n", os.linesep)) # python 3 correction
        temp_file.write(m3u_string.encode("ascii"))
        temp_file.close()
        return song
    ############# SOCCER LIVE ##############
    #def getSoccer(self):
    #    resp = self.amzCall(self.API_GetSoccerMain,'getSoccerMain')
    #    menuEntries = []
    #    for item in resp['blocks'][0]['filterSelector']['filterOptions']:
    #        menuEntries.append({'txt':item['text'],'fct':'getSoccerFilter','target':item['value'],'img':item['image']})
    #    self.createList(menuEntries,False,True)
    def getSoccerFilter(self,target=None): # 'BUND', 'BUND2', 'CHAMP', 'DFBPOKAL', 'SUPR'
        menuEntries = []
        resp = self.amzCall(self.API_GetSoccerMain,'getSoccerMain',None,None,target)
        idx = resp['blocks'][0]['positionSelector']['currentPosition']['blockIndex'] # current matchday
        param = resp['blocks'][0]['positionSelector']['positionOptions']
        idx1 = 0
        for item in param: # find last matchday based on current matchday
            if item['blockIndex'] < idx:
                idx1+=1
                continue
            break
        idx1-= 1 # todo can be set as user input variable / currently last matchday
        if idx1 < 0:
            idx1 = 0
        idx1 = resp['blocks'][0]['positionSelector']['positionOptions'][idx1]['blockIndex'] # last matchday index
        while idx1 <= idx:
            dat = resp['blocks'][0]['blocks'][idx1]['title'] # day of matchday
            for item in resp['blocks'][0]['blocks'][idx1]['blocks']:
                img = None
                if 'programHint' in item: # show matches only
                    target = item['programHint']['programId']
                else:
                    target = None
                    continue
                title = '{}  {}'.format(dat,item['title'])
                if 'decorator1' in item and item['decorator1'] is not None:
                    if len(str(item['decorator1'])) > 0:
                        title+= '   {}:{}'.format(str(item['decorator1']),str(item['decorator2']))
                if 'title1' in item:
                    title+= '   {}'.format(item['title1'])
                if 'title2' in item and item['title2'] is not None:
                    title+= ' - {}'.format(item['title2'])
                if 'image3' in item:
                    img = item['image3']['IMAGE_PROGRAM_COVER']
                else:
                    img = item['image']
                menuEntries.append({'txt':title,'fct':'getSoccerDetail','target':target,'img':img})
            idx1 += 1
        self.createList(menuEntries,False,True)
    def getSoccerDetail(self,target=None):
        resp = self.amzCall(self.API_GetSoccerProgramDetails,'getSoccerProgramDetails',None,None,target)
        try:
            target = resp['program']['mediaContentList'][0]['mediaContentId']
        except:
            return False
        # target for xml source
        resp = self.amzCall(self.API_GetSoccerStreamingURLs,'getSoccerStreamingURL','soccer',None,target)
        target = resp['Output']['contentResponseList'][0]['urlList'][0] # link to mpd file
        # get the xml file and extract the source
        if not self.isInputStream():
            return False
        li = xbmcgui.ListItem(path=target)
        li.setProperty('inputstreamaddon', 'inputstream.adaptive')
        li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        li.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        li.setInfo('video', '')
        li.setMimeType('application/dash+xml')
        li.setContentLookup(False)
        xbmcplugin.setResolvedUrl(self.addonHandle, True, listitem=li)
    def getLicenseKey(self):
        amzUrl = self.API_LicenseForPlaybackV2
        url = '{}/{}/api/{}'.format(self.url, self.region, amzUrl['path'])
        head = self.prepReqHeader(amzUrl['target'])

        cookiedict = {}
        for cookie in self.cj:
            cookiedict[cookie.name] = cookie.value
        cj_str = ';'.join(['%s=%s' % (k, v) for k, v in cookiedict.items()])

        head['Cookie'] = cj_str
        #licHeaders = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k, v in head.items()])
        licHeaders = '&'.join(['%s=%s' % (k, urlquote(v)) for k, v in head.items()]) # python 3 correction
        licBody = self.prepReqData('getLicenseForPlaybackV2')
        # licURL expected (req / header / body / response)
        return '{}|{}|{}|JBlicense'.format(url,licHeaders,licBody)
    def getMaestroID(self):
        return 'Maestro/1.0 WebCP/1.0.202638.0 ({})'.format(self.generatePlayerUID())
    def generatePlayerUID(self):
        # a = str(math.floor(16 * (1 + random.random())).hex())[4:5]
        a = str(float.hex(math.floor(16 * (1 + random.random()))))[4:5] # python 3 correction
        return '{}-{}-dmcp-{}-{}{}'.format(self.doCalc(),self.doCalc(),self.doCalc(),self.doCalc(),a)
    def doCalc(self):
        # return str(math.floor(65536 * (1 + random.random())).hex())[4:8]
        return str(float.hex(math.floor(65536 * (1 + random.random()))))[4:8] # python 3 correction
    def isInputStream(self): # helper to activate InputStream if available
        verifyISA = '{"jsonrpc":"2.0","id":1,"method":"Addons.GetAddonDetails","params":{"addonid":"inputstream.adaptive"}}'
        if 'error' in xbmc.executeJSONRPC(verifyISA):
            xbmc.executebuiltin('UpdateAddonRepos', True)
            xbmc.executebuiltin('InstallAddon(inputstream.adaptive)', True)
            if 'error' in xbmc.executeJSONRPC(verifyISA):
                self.log('InputStream.Adaptive addon is not installed')
                return False
            else:
                self.log('InputStream.Adaptive activated')
                return True
        else:
            return True

# method:POST
if __name__ == '__main__':
    am = AmazonMedia()
    am.reqDispatch()