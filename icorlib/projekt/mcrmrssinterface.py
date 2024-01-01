# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.mcrmutil as MCRMUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string
import re
import os


class RSSContext:

    def __init__(self, arssobj, alog=None, astructobj=None, aguidparamname='soid', asimplecms=None):
        self.Log = alog
        self.foutrss = None
        self.isEmpty = 0
        self.WWWMenuStruct = None
        self.SimpleCMS = asimplecms
        if type(arssobj) == type({}):
            if astructobj is None:
                self.isEmpty = 1
            else:
                self.RSSObj = None
                self.WWWMenuStruct = astructobj
                brssobj = astructobj.RSSInfo
                self.RSSOpis = arssobj.get('RSSOpis', brssobj.Nazwa)
                self.ChannelCopyright = arssobj.get('ChannelCopyright', brssobj.ChannelCopyright)
                self.ManagingEditor = arssobj.get('ManagingEditor', brssobj.ManagingEditor)
                self.WebMaster = arssobj.get('WebMaster', brssobj.WebMaster)
                self.ImageURL = arssobj.get('ImageURL', brssobj.ImageURL)
                self.ImageTitle = arssobj.get('ImageTitle', brssobj.ImageTitle)
                self.ImageLink = arssobj.get('ImageLink', brssobj.ImageLink)
                self.PICS = arssobj.get('PICS', brssobj.PICS)
        elif arssobj is None:
            self.isEmpty = 1
        else:
            self.RSSObj = arssobj
            self.WWWMenuStruct = self.RSSObj.Struktura
            apathsobj = self.WWWMenuStruct.AppPaths
            if not apathsobj.AdresZewnetrznyWWW:
                self.isEmpty = 1
            #if not apathsobj.KatalogWirtualny:
            #self.isEmpty=1
            self.RSSOpis = self.RSSObj.Nazwa
            self.ChannelCopyright = self.RSSObj.ChannelCopyright
            self.ManagingEditor = self.RSSObj.ManagingEditor
            self.WebMaster = self.RSSObj.WebMaster
            self.ImageURL = self.RSSObj.ImageURL
            self.ImageTitle = self.RSSObj.ImageTitle
            self.ImageLink = self.RSSObj.ImageLink
            self.PICS = self.RSSObj.PICS
        self.IsChapterDisabled = 0
        self.GUIDParamName = aguidparamname

    def OpenFile(self, robj, apath, atitle, acustom=0, adir='/rss/', abasename='rss_', abasenamemodifier=''):
        if type(robj) == type(1):
            rclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
            robj = rclass[robj]
        if not apath and self.WWWMenuStruct is not None:
            apath = FilePathAsSystemPath(self.WWWMenuStruct.AppPaths.SciezkaAplikacji)
        self.ChapterOID = robj.OID
        if not atitle:
            atitle = robj.Naglowek
        self.IsChapterDisabled = 0
        if not acustom:
            self.IsChapterDisabled = robj['RSSDisabled', mt_Integer]
            if self.IsChapterDisabled:
                return
        if not os.path.exists(apath + adir):
            os.makedirs(apath + adir)
        self.foutrss = XMLUtil.MXMLFile(apath + adir + abasename + '%d%s.xml' % (robj.OID, abasenamemodifier), anopl=1, aencoding='utf-8', astemp=1)
        self.OutputPath = apath
        self.OutputDir = adir
        self.OutputBaseName = abasename
        self.ItemCnt = 0
        print 'file:', apath + adir + abasename + '%d%s.xml' % (robj.OID, abasenamemodifier)
        self.foutrss.Header()
        self.foutrss.TagOpen('rss',{
           'version':'2.0',
           'xmlns:geo':"http://www.w3.org/2003/01/geo/wgs84_pos#",
           'xmlns:georss':"http://www.georss.org/georss",
        }) # yapf: disable
        self.foutrss.TagOpen('channel')
        self.foutrss.TagOpen('title', aclosetag=1, avalue=atitle)
        apathsobj = self.WWWMenuStruct.AppPaths
        if len(apathsobj.KatalogWirtualny) > 1:
            abasechapterpath = apathsobj.AdresZewnetrznyWWW + '/' + apathsobj.KatalogWirtualny + '/'
        else:
            abasechapterpath = apathsobj.AdresZewnetrznyWWW + '/'
        abasechapterurl = abasechapterpath + 'chapter_%d.asp' % robj.OID
        self.BaseChapterPath = abasechapterpath
        self.Link = abasechapterurl
        self.foutrss.TagOpen('link', aclosetag=1, avalue=abasechapterurl)
        arssopis = self.RSSOpis
        if not arssopis:
            arssopis = atitle
        self.foutrss.TagOpen('description', aclosetag=1, avalue=arssopis)
        self.foutrss.TagOpen('language', aclosetag=1, avalue='pl')
        self.foutrss.TagOpen('copyright', aclosetag=1, avalue=self.ChannelCopyright)
        self.foutrss.TagOpen('managingEditor', aclosetag=1, avalue=self.ManagingEditor)
        self.foutrss.TagOpen('webMaster', aclosetag=1, avalue=self.WebMaster)
        apubdate = ICORUtil.tdateztime()
        self.foutrss.TagOpen('pubDate', aclosetag=1, avalue=ICORUtil.tdatetime2RFC822datetime(apubdate))
        abuilddate = ICORUtil.tdatetime()
        self.PubDate = ICORUtil.tdatetime2RFC822datetime(abuilddate)
        self.foutrss.TagOpen('lastBuildDate', aclosetag=1, avalue=self.PubDate)
        if not acustom:
            l = string.split(robj.RSSKategorie, '\n')
            if l:
                for s in l:
                    s = string.strip(s)
                    if s:
                        self.foutrss.TagOpen('category', aclosetag=1, avalue=s)
        self.foutrss.TagOpen('generator', aclosetag=1, avalue='ICOR')
        self.foutrss.TagOpen('docs', aclosetag=1, avalue='http://www.rssboard.org/rss-specification')
        if self.ImageURL:
            self.foutrss.TagOpen('image', aclosetag=0)
            self.foutrss.TagOpen('url', aclosetag=1, avalue=self.ImageURL)
            if self.ImageTitle:
                self.foutrss.TagOpen('title', aclosetag=1, avalue=self.ImageTitle)
            if self.ImageLink:
                self.foutrss.TagOpen('link', aclosetag=1, avalue=self.ImageLink)
            self.foutrss.TagClose()    #image
        apics = self.PICS
        if apics:
            self.foutrss.TagOpen('rating', aclosetag=1, avalue=apics)
        self.NewLink()
        self.eventOnRSSGetLink = None
        ehrobj = MCRMUtil.EventHelper(robj, 'ChapterEvents')
        if not acustom:
            se1 = ehrobj['OnRSSGetLink']
            if se1:
                try:
                    dg1 = {'this': self, 're': re, 'string': string, 'ICORUtil': ICORUtil}
                    ICORUtil.do_exec(se1, dg1)
                    self.eventOnRSSGetLink = dg1['OnRSSGetLink']
                except:
                    self.eventOnRSSGetLink = None
                    print 'error in OnRSSGetLink event, chapter %d: "%s"' % (robj.OID, robj.Naglowek)
                    print se1
                    if self.Log:
                        self.Log.LogException('error in OnRSSGetLink event, chapter %d: "%s"' % (robj.OID, robj.Naglowek))
                    traceback.print_exc()
        self.eventOnRSSGetTitle = None
        if not acustom:
            se2 = ehrobj['OnRSSGetTitle']
            if se2:
                try:
                    dg2 = {'this': self, 're': re, 'string': string, 'ICORUtil': ICORUtil}
                    ICORUtil.do_exec(se2, dg2)
                    self.eventOnRSSGetTitle = dg2['OnRSSGetTitle']
                except:
                    self.eventOnRSSGetTitle = None
                    print 'error in OnRSSGetTitle event, chapter %d:' % robj.OID
                    print se2
                    if self.Log:
                        self.Log.LogException('error in OnRSSGetTitle event, chapter %d:' % robj.OID)
                    traceback.print_exc()
        self.eventOnRSSGetDescription = None
        if not acustom:
            se3 = ehrobj['OnRSSGetDescription']
            if se3:
                try:
                    dg3 = {'this': self, 're': re, 'string': string, 'ICORUtil': ICORUtil}
                    ICORUtil.do_exec(se3, dg3)
                    self.eventOnRSSGetDescription = dg3['OnRSSGetDescription']
                except:
                    self.eventOnRSSGetDescription = None
                    print 'error in OnRSSGetDescription event, chapter %d:' % robj.OID
                    print se3
                    if self.Log:
                        self.Log.LogException('error in OnRSSGetDescription event, chapter %d:' % robj.OID)
                    traceback.print_exc()
        if self.SimpleCMS is not None:
            dd = {'thisRSS': self, }
            try:
                ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnRSSOpen')
            except:
                if self.Log:
                    self.Log.LogException('error in OnRSSOpen event')
                import traceback
                traceback.print_exc()

    def NewLink(self):
        if self.IsChapterDisabled:
            return
        self.ItemTitle = []
        self.ItemDict = {}
        self.ItemDescription = []
        self.ItemLink = ''
        self.ItemAuthor = ''
        self.ItemGUID = ''
        self.ItemPubDate = ''

    def WriteLink(self, atableid=None):
        if self.IsChapterDisabled:
            return
        atitle = ''
        for s in self.ItemTitle:
            if len(s) == 32 and string.find(s, ' ') < 0:
                continue
            s = string.strip(s)
            if s:
                if atitle:
                    atitle = atitle + ', '
                atitle = atitle + s
                if len(atitle) > 220:
                    atitle = atitle[:218] + '...'
                    break
        alink = self.Link + '?%s=' % (self.GUIDParamName, ) + self.ItemGUID
        adescription = ''
        for s in self.ItemDescription:
            s = string.strip(ICORUtil.StripHTMLTags(s))
            if s:
                if adescription:
                    adescription = adescription + ', '
                adescription = adescription + s
                if len(adescription) > 500:
                    adescription = adescription[:496] + '...'
                    break
        adescription = '<i>' + adescription + '</i>'
        self.LinkGUID = self.Link + '?%s=' % (self.GUIDParamName, ) + self.ItemGUID
        self.GUIDPermaLink = 'false'
        if self.eventOnRSSGetLink:
            alink = self.eventOnRSSGetLink(alink)
        if self.eventOnRSSGetTitle:
            atitle = self.eventOnRSSGetTitle(atitle)
        if self.eventOnRSSGetDescription:
            adescription = self.eventOnRSSGetDescription(adescription)
        if self.ItemPubDate:
            if type(self.ItemPubDate) == type(()):
                apubdate = ICORUtil.tdatetime2RFC822datetime(self.ItemPubDate)
            else:
                apubdate = self.ItemPubDate
        else:
            apubdate = self.PubDate
        self.foutrss.TagOpen('item', aclosetag=0)
        self.foutrss.TagOpen('title', aclosetag=1, avalue=atitle)
        self.foutrss.TagOpen('link', aclosetag=1, avalue=alink)
        self.foutrss.TagOpen('description', aclosetag=1, avalue=adescription)
        if self.ItemAuthor:
            self.foutrss.TagOpen('author', aclosetag=1, avalue=self.ItemAuthor)
        self.foutrss.TagOpen('guid', {'isPermaLink': self.GUIDPermaLink}, aclosetag=1, avalue=self.LinkGUID)
        self.foutrss.TagOpen('pubDate', aclosetag=1, avalue=apubdate)
        if self.SimpleCMS is not None:
            if type(atableid) == type(1):
                dd = {'thisRSS': self, 'RSSTableID': atableid}
                try:
                    ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnRSSItem')
                except:
                    if self.Log:
                        self.Log.LogException('error in OnRSSItem event')
                    import traceback
                    traceback.print_exc()
        self.foutrss.TagClose()    #item
        self.ItemCnt = self.ItemCnt + 1

    def CloseFile(self):
        if self.IsChapterDisabled:
            return
        self.foutrss.TagClose()    #channel
        self.foutrss.TagClose()    #rss
        self.foutrss.close()
        if self.SimpleCMS is not None:
            dd = {'thisRSS': self, }
            try:
                ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnRSSClose')
            except:
                if self.Log:
                    self.Log.LogException('error in OnRSSClose event')
                import traceback
                traceback.print_exc()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    return
