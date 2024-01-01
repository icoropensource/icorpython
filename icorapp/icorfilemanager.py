# -*- coding: utf-8 -*-
import sys
import os
import time
import logging
import urllib
import traceback
import Queue
import threading
import shutil

import cherrypy
import cherrypy.process as process

try:
    import json
except:
    import simplejson as json
import scandir

from PIL import Image

import appplatform.startutil as startutil
import icordbmain
import appplatform.storageutil as storageutil

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.icorsecurity as ICORSecurity
import icordbmain.adoutil as ADOLibInit
import CLASSES_Library_NetBase_Utils_ImageUtil as ImageUtil

import appplatform.wserverutil.webutil as webutil

THUMB_SIZE_X, THUMB_SIZE_Y = 128, 128
THUMB_MAXSIZE_KB = 10


class FMItem(object):

    def __init__(self):
        pass


class FMItemFile(FMItem):

    def __init__(self):
        pass


class FMItemFolder(FMItem):

    def __init__(self, aparent, aid):
        self.parent = aparent
        self.id = aid
        self.iconClass = ''

    def GetPath(self, lpath=None):
        aid = self.id
        if type(aid) == type(1):
            aid = str(aid)
        if lpath is None:
            lpath = [aid]
        else:
            lpath.insert(0, aid)
        if self.parent:
            return self.parent.GetPath(lpath)
        return lpath

    def GetRec(self, aitemname):
        lpath = self.GetPath()
        apath = '/'.join(lpath)
        d={
           "id":"/%s/"%apath,
           "type":"folder",
           "attributes": {
              "name":"%s"%aitemname,
              "path":"/%s/"%apath,
              "readable":1,
              "writable":1,
              "created":"",
              "modified":"10 Mar 2017 21:58",
              "timestamp":1489183108,
           }
        } # yapf: disable
        if self.iconClass:
            d['icon_class'] = self.iconClass
        return d


class FMConstPath(FMItemFolder):

    def __init__(self, aparent, aid, atype='', adata=None):
        FMItemFolder.__init__(self, aparent, aid)
        if not atype:
            atype = aid
        self.pathtype = atype
        self.name = atype
        self.data = adata
        self.lfitems = []
        self.dfitems = {}
        self.lpath = None

    def GetBasePath(self, alocation=0):
        if alocation:
            return '', '', ''
        return ''

    def GetItemPath(self, alocation=0):
        if alocation:
            locuri, locpath, filepath = self.GetBasePath(alocation=alocation)
            return locuri, locpath, os.path.join(filepath, *self.lpath)
        bpath = self.GetBasePath(alocation=alocation)
        return os.path.join(bpath, *self.lpath)

    def AddItem(self, fitem):
        self.lfitems.append(fitem)
        self.dfitems[fitem.name] = fitem

    def SetPath(self, lpath):
        self.lpath = lpath[:]
        return self

    def GetItems(self):
        ret = []
        if self.lfitems:
            for fitem in self.lfitems:
                l = fitem.GetItems()
                ret.extend(l)
        else:
            d = self.GetRec(self.name)
            ret.append(d)
        return ret


class FMConstPathFS(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)

    def GetPathID(self):
        lpath = self.GetPath()
        apath = '/'.join(lpath)
        bpath = ''
        if self.lpath:
            bpath = os.path.normpath('/'.join(self.lpath))
            apath = os.path.join(apath, bpath)
        apath = apath.replace('\\', '/')
        return bpath, apath

    def ServeFileAccel(self, download=0):
        locuri, locpath, filepath = self.GetItemPath(alocation=1)
        fileuri = filepath[len(locpath):]
        abasepath, afilename = os.path.split(filepath)
        afilename = afilename.replace('"', "'")
        aredirect = locuri + fileuri.replace('\\', '/')
        if 0:
            print '  ServeFileAccel:    locuri: %s' % (locuri, )
            print '  ServeFileAccel:   locpath: %s' % (locpath, )
            print '  ServeFileAccel:  filepath: %s' % (filepath, )
            print '  ServeFileAccel:   fileuri: %s' % (fileuri, )
            print '  ServeFileAccel: afilename: %s' % (afilename, )
            print '  ServeFileAccel: aredirect: %s' % (aredirect, )
        cherrypy.response.headers['X-Accel-ICOR'] = 'OK'
        cherrypy.response.headers['Content-Type'] = ''
        if download:
            #cherrypy.response.headers['Content-Type']='application/x-download'
            #cherrypy.response.headers['application/x-download']='attachment'
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=%s' % storageutil.CP1250_To_UTF8(afilename)
            cherrypy.response.headers['Content-Transfer-Encoding'] = 'application/octet-stream'
        cherrypy.response.headers['X-Accel-Redirect'] = storageutil.CP1250_To_UTF8(aredirect)
        return ''

    def GetThumbnail(self):
        afilepath = self.GetItemPath()
        if '_thumbs' in afilepath:
            return
        if not ImageUtil.IsImage(afilepath):
            return
        abasepath, afilename = os.path.split(afilepath)
        athumbpath = os.path.join(abasepath, '_thumbs')
        if not os.path.exists(athumbpath):
            os.makedirs(athumbpath)
        athumbpath = os.path.join(athumbpath, afilename)
        if os.path.exists(athumbpath):    # TODO sprawdzac czas modyfikacji miniatury i oryginalu
            if os.path.getsize(athumbpath) > 0:
                self.lpath.pop()
                self.lpath.append('_thumbs')
                self.lpath.append(afilename)
        else:
            ImageUtil.ResizeImageByConstraint(afilepath, athumbpath, THUMB_SIZE_X, THUMB_SIZE_Y, amaxsizekb=THUMB_MAXSIZE_KB, acrop=1, alog=None)
            self.lpath.pop()
            self.lpath.append('_thumbs')
            self.lpath.append(afilename)

    def AddFolder(self, aname):
        if not aname:
            return None
        afilepath = self.GetItemPath()
        afolderpath = os.path.join(afilepath, aname)
        os.makedirs(afolderpath)
        self.lpath.append(aname)
        return self.GetFileInfoRec()

    def Rename(self, aname):
        if not aname:
            return None
        afilepathold = self.GetItemPath()
        aoldname = self.lpath.pop()
        self.lpath.append(aname)
        afilepathnew = self.GetItemPath()
        try:
            shutil.move(afilepathold, afilepathnew)
        except:
            return webutil.GetJSONErrorResult('filesystem', 541, 'wystąpił błąd podczas zmiany nazwy pliku')
        return self.GetFileInfoRec()

    def Move(self, aitem):
        afilepathold = aitem.GetItemPath()
        afilepathnew = self.GetItemPath()
        try:
            shutil.move(afilepathold, afilepathnew)
            self.lpath.append(aitem.lpath.pop())
        except:
            return webutil.GetJSONErrorResult('filesystem', 541, 'wystąpił błąd podczas przenoszenia pliku')
        return self.GetFileInfoRec()

    def Copy(self, aitem):
        afilepathold = aitem.GetItemPath()
        afilepathnew = self.GetItemPath()
        try:
            shutil.move(afilepathold, afilepathnew)
            afilename = aitem.lpath.pop()
            aitem.lpath.append(afilename)
            self.lpath.append(afilename)
        except:
            return webutil.GetJSONErrorResult('filesystem', 541, 'wystąpił błąd podczas kopiowania pliku')
        return self.GetFileInfoRec()

    def Upload(self, files):
        self.lpath.append(files.filename)
        afilepath = self.GetItemPath()
        fout = open(afilepath, 'wb')
        shutil.copyfileobj(files.file, fout)
        fout.close()
        return self.GetFileInfoRec()

    def SaveFile(self, acontent):
        afilepath = self.GetItemPath()
        try:
            fout = storageutil.OpenText(afilepath, 'wb')
            fout.write(acontent)
            fout.close()
        except:
            return webutil.GetJSONErrorResult('filesystem', 541, 'wystąpił błąd podczas zapisywania danych')
        return self.GetFileInfoRec()

    def Delete(self):
        afilepath = self.GetItemPath()
        ret = self.GetFileInfoRec()
        try:
            if os.path.isdir(afilepath):
                shutil.rmtree(afilepath)
            else:
                os.unlink(afilepath)
        except:
            return webutil.GetJSONErrorResult('filesystem', 541, 'wystąpił błąd podczas usuwania')
        return ret

    def GetFileInfoRec(self, acontent=0):
        afilepath = self.GetItemPath()
        abasepath, aname = os.path.split(afilepath)
        ads = os.stat(afilepath)
        d={
           "attributes": {
              "name":"%s"%aname,
              "readable":1,
              "writable":1,
           }
        } # yapf: disable
        #if self.iconClass:
        #d['icon_class']=self.iconClass
        bpath, apath = self.GetPathID()
        afilename, aext = os.path.splitext(afilepath)
        aext = aext.lower()
        if os.path.isdir(afilepath):
            d['id'] = "/%s/" % (apath, )
            d['type'] = 'folder'
            #print adirentry.name,adirentry.path,ads.st_size,ctime,mtime,ads.st_mtime
        else:
            d['id'] = "/%s" % (apath, )
            d['type'] = 'file'
            d['attributes']['extension'] = os.path.splitext(aname)[1][1:]
            d['attributes']['size'] = ads.st_size
            if aext in ['.gif', '.jpg', '.jpeg', '.png']:
                try:
                    img = Image.open(afilepath).size
                    d['attributes']['width'] = img[0]
                    d['attributes']['height'] = img[1]
                except:
                    d['attributes']['width'] = 640
                    d['attributes']['height'] = 480
        d['attributes']['path'] = d['id']
        d['attributes']['created'] = storageutil.tdatetime2fmtstr(time.localtime(ads.st_ctime)[:7])
        d['attributes']['modified'] = storageutil.tdatetime2fmtstr(time.localtime(ads.st_mtime)[:7])
        d['attributes']['timestamp'] = int(ads.st_mtime)
        if acontent:
            #print 'GetFileInfoRec: %s'%(afilepath),
            fin = open(afilepath, 'rb')
            d['attributes']['content'] = fin.read()
            fin.close()
        return d

    def GetItemsAsFiles(self, afilespath=None):
        #print '  GETITEMS self.lpath:',self.lpath
        if afilespath is None:
            afilespath = self.GetBasePath()
        if afilespath is None:
            return []
        ret = []
        if self.lpath is None:
            d = FMItemFolder.GetRec(self, self.name)
            ret.append(d)
            return ret
        bpath, apath = self.GetPathID()
        awwwpath = os.path.normpath(os.path.join(afilespath, bpath))
        #print '  GETITEMS wwwpath:',awwwpath
        if not os.path.isdir(awwwpath):
            return []
        #print '  GETITEMS:',lpath,apath,awwwpath
        for adirentry in scandir.scandir(unicode(awwwpath)):
            ads = adirentry.stat()
            d={
               "attributes": {
                  "name":"%s"%adirentry.name,
                  "readable":1,
                  "writable":1,
               }
            } # yapf: disable
            #if self.iconClass:
            #d['icon_class']=self.iconClass
            afilename, aext = os.path.splitext(adirentry.name)
            aext = aext.lower()
            if adirentry.is_dir():
                d['id'] = "/%s/%s/" % (apath, adirentry.name)
                d['type'] = 'folder'
                #print adirentry.name,adirentry.path,ads.st_size,ctime,mtime,ads.st_mtime
            elif adirentry.is_file():
                d['id'] = "/%s/%s" % (apath, adirentry.name)
                d['type'] = 'file'
                d['attributes']['extension'] = os.path.splitext(adirentry.name)[1][1:]
                d['attributes']['size'] = ads.st_size
                if aext in ['.gif', '.jpg', '.jpeg', '.png']:
                    try:
                        img = Image.open(os.path.join(awwwpath, adirentry.name)).size
                        d['attributes']['width'] = img[0]
                        d['attributes']['height'] = img[1]
                    except:
                        d['attributes']['width'] = 640
                        d['attributes']['height'] = 480
                        raise
                #print adirentry.name,adirentry.path,ads.st_size,ctime,mtime,ads.st_mtime
            d['attributes']['path'] = d['id']
            d['attributes']['created'] = storageutil.tdatetime2fmtstr(time.localtime(ads.st_ctime)[:7])
            d['attributes']['modified'] = storageutil.tdatetime2fmtstr(time.localtime(ads.st_mtime)[:7])
            d['attributes']['timestamp'] = int(ads.st_mtime)
            ret.append(d)
        return ret

    def GetItems(self):
        return self.GetItemsAsFiles()


class FMConstPathObjects(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)
        self.name = 'Załączniki'
        self.iconClass = 'silk_folder_link'


class FMConstPathProjectCDN(FMConstPathFS):

    def __init__(self, aparent, atype, adata=None):
        FMConstPathFS.__init__(self, aparent, atype, adata)
        self.name = 'CDN'
        self.iconClass = 'silk_database_copy'

    def GetBasePath(self, alocation=0):
        cobj = self.parent.Obj.CDNServers
        if not cobj:
            if alocation:
                return None, None, None
            return None
        afield = cobj.Class.FieldsByName('SMBBasePath')
        apath = afield[cobj.OID]
        if not apath:
            if alocation:
                return None, None, None
            return None
        apath = startutil.FilePathAsSystemPath(apath)
        if not os.path.exists(apath):
            os.makedirs(apath)
        if alocation:
            locuri = '/cdn/%d' % cobj.OID
            return locuri, apath, apath
        return apath


class FMConstPathProjectFiles(FMConstPathFS):

    def __init__(self, aparent, atype, adata=None):
        FMConstPathFS.__init__(self, aparent, atype, adata)
        self.name = 'Pliki'
        self.iconClass = 'silk_folder_page_white'

    def GetBasePath(self, alocation=0):
        apath = startutil.FilePathAsSystemPath(self.parent.Obj.WWWDataPath)
        apath = os.path.join(apath, 'HTTPFiles')
        if not os.path.exists(apath):
            os.makedirs(apath)
        if alocation:
            locpath = os.path.join(startutil.appconfig.ICORBaseDir, 'WWWData')
            return '/wwwdata', locpath, apath
        return apath


class FMConstPathProjectImages(FMConstPathFS):

    def __init__(self, aparent, atype, adata=None):
        FMConstPathFS.__init__(self, aparent, atype, adata)
        self.name = 'Obrazy'
        self.iconClass = 'silk_folder_palette'

    def GetBasePath(self, alocation=0):
        apath = startutil.FilePathAsSystemPath(self.parent.Obj.WWWDataPath)
        apath = os.path.join(apath, 'HTTPImages')
        if not os.path.exists(apath):
            os.makedirs(apath)
        if alocation:
            locpath = os.path.join(startutil.appconfig.ICORBaseDir, 'WWWData')
            return '/wwwdata', locpath, apath
        return apath


class FMConstPathProjectWWWSite(FMConstPathFS):

    def __init__(self, aparent, atype, adata=None):
        FMConstPathFS.__init__(self, aparent, atype, adata)
        self.name = 'Serwis'
        self.iconClass = 'silk_folder_go'

    def GetBasePath(self, alocation=0):
        apath = startutil.FilePathAsSystemPath(self.parent.Obj.AppPaths.SciezkaAplikacji)
        if alocation:
            locuri = '/wwwsite/%d' % self.parent.Obj.OID
            return locuri, apath, apath
        return apath


class FMConstPathProjectWWWFiles(FMConstPathFS):

    def __init__(self, aparent, atype, adata=None):
        FMConstPathFS.__init__(self, aparent, atype, adata)
        self.name = 'Pliki'
        self.iconClass = 'silk_folder_link'

    def GetBasePath(self, alocation=0):
        apath = startutil.FilePathAsSystemPath(self.parent.parent.parent.Obj.WWWDataPath)
        apath = os.path.join(apath, 'WWWStruct', str(self.parent.OID))
        if not os.path.exists(apath):
            os.makedirs(apath)
        if alocation:
            locpath = os.path.join(startutil.appconfig.ICORBaseDir, 'WWWData')
            return '/wwwdata', locpath, apath
        return apath


class FMConstPathProjectWWWChapterFiles(FMConstPathFS):

    def __init__(self, aparent, atype, adata=None):
        FMConstPathFS.__init__(self, aparent, atype, adata)
        self.name = 'Pliki w rozdziale'
        self.iconClass = 'silk_folder_page'

    def GetBasePath(self, alocation=0):
        apath = startutil.FilePathAsSystemPath(self.parent.parent.parent.parent.parent.Obj.WWWDataPath)
        apath = os.path.join(apath, 'WWWStruct', str(self.parent.parent.parent.OID), '_chapters', str(self.parent.OID))
        if not os.path.exists(apath):
            os.makedirs(apath)
        if alocation:
            locpath = os.path.join(startutil.appconfig.ICORBaseDir, 'WWWData')
            return '/wwwdata', locpath, apath
        return apath


class FMConstPathUser(FMConstPathFS):

    def __init__(self, aparent, atype, aobj=None):
        FMConstPathFS.__init__(self, aparent, aobj.OID, atype)
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.name = storageutil.CP1250_To_UTF8(aobj.UserName)
        self.iconClass = 'silk_folder_user'

    def GetBasePath(self, alocation=0):
        locpath = os.path.join(startutil.appconfig.ICORBaseDir, 'WWWData')
        apath = os.path.join(locpath, '_users', str(self.OID))
        if not os.path.exists(apath):
            os.makedirs(apath)
        if alocation:
            return '/wwwdata', locpath, apath
        return apath


class FMConstPathProjectWWWChapterSub(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)
        self.name = 'Podrozdziały'
        self.iconClass = 'silk_folder_bookmark'

    def SetPath(self, lpath):
        ret = self
        self.lpath = lpath[:]
        aobj = self.parent.Obj.PodRozdzialy
        while aobj:
            fitem = FMConstPathProjectWWWChapter(self.parent.parent, 'wwwchapter', aobj)
            self.AddItem(fitem)
            aobj.Next()
        return ret


class FMConstPathProjectWWWChapter(FMConstPath):

    def __init__(self, aparent, atype, aobj=None, apreid=''):
        FMConstPath.__init__(self, aparent, apreid + str(aobj.OID), atype)
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        s = aobj.Naglowek
        if not s:
            s = '--***---'
        self.name = storageutil.CP1250_To_UTF8(s)
        self.iconClass = 'silk_book_open'

    def SetPath(self, lpath):
        ret = self
        if not lpath:
            fmpath = FMConstPathProjectWWWChapterFiles(self, 'chapterfiles')
            self.AddItem(fmpath)
            if self.Obj.PodRozdzialy:
                fmpath = FMConstPathProjectWWWChapterSub(self, 'subchapters')
                self.AddItem(fmpath)
        elif lpath[0] == 'chapterfiles':
            fp = FMConstPathProjectWWWChapterFiles(self, 'chapterfiles')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        elif lpath[0] == 'subchapters':
            if self.Obj.PodRozdzialy:
                fp = FMConstPathProjectWWWChapterSub(self, 'subchapters')
                self.AddItem(fp)
                ret = fp.SetPath(lpath[1:])
        return ret


class FMConstPathProjectWWWChapters(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)
        self.name = 'Rozdziały'
        self.iconClass = 'silk_book'

    def SetPath(self, lpath):
        ret = self
        self.lpath = lpath[:]
        if lpath:
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
            try:
                aoid = int(lpath[0])
            except:
                aoid = -1
            if aclass.ObjectExists(aoid):
                aobj = aclass[aoid]
                fp = FMConstPathProjectWWWChapter(self, 'wwwchapter', aobj)
                self.AddItem(fp)
                ret = fp.SetPath(lpath[1:])
        else:
            aobj = self.parent.Obj.Rozdzialy
            while aobj:
                fitem = FMConstPathProjectWWWChapter(self, 'wwwchapter', aobj)
                self.AddItem(fitem)
                aobj.Next()
        return ret


class FMConstPathProjectWWWChapterGroup(FMConstPath):

    def __init__(self, aparent, atype, aobj=None):
        FMConstPath.__init__(self, aparent, aobj.OID, atype)
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        s = aobj.Nazwa
        if not s:
            s = '--***---'
        self.name = storageutil.CP1250_To_UTF8(s)
        self.iconClass = 'silk_book_go'

    def SetPath(self, lpath):
        ret = self
        self.lpath = lpath[:]
        aobj = self.Obj.Rozdzialy
        while aobj:
            fitem = FMConstPathProjectWWWChapter(self.parent.parent, 'wwwchapter', aobj, apreid='wwwchapters/')
            self.AddItem(fitem)
            aobj.Next()
        return ret


class FMConstPathProjectWWWChapterGroups(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)
        self.name = 'Grupy rozdziałów'
        self.iconClass = 'silk_sitemap_color'

    def SetPath(self, lpath):
        ret = self
        self.lpath = lpath[:]
        if lpath:
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_GrupaRozdzialow']
            try:
                aoid = int(lpath[0])
            except:
                aoid = -1
            if aclass.ObjectExists(aoid):
                aobj = aclass[aoid]
                if aobj.Struktura.OID == self.parent.OID:
                    fp = FMConstPathProjectWWWChapterGroup(self, 'wwwchaptergroup', aobj)
                    self.AddItem(fp)
                    ret = fp.SetPath(lpath[1:])
        else:
            aobj = self.parent.Obj.GrupyRozdzialow
            while aobj:
                fitem = FMConstPathProjectWWWChapterGroup(self, 'wwwchaptergroup', aobj)
                self.AddItem(fitem)
                aobj.Next()
        return ret


class FMConstPathProjectWWWStruct(FMConstPath):

    def __init__(self, aparent, atype, aobj=None):
        FMConstPath.__init__(self, aparent, aobj.OID, atype)
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.name = storageutil.CP1250_To_UTF8(aobj.Nazwa)
        self.iconClass = 'silk_chart_organisation'

    def SetPath(self, lpath):
        ret = self
        if not lpath:
            fmpath = FMConstPathProjectWWWFiles(self, 'wwwfiles')
            self.AddItem(fmpath)
            fmpath = FMConstPathProjectWWWSite(self, 'wwwsite')
            self.AddItem(fmpath)
            if self.Obj.GrupyRozdzialow and self.Obj.GrupyRozdzialow.Rozdzialy:
                fmpath = FMConstPathProjectWWWChapterGroups(self, 'wwwchaptergroups')
                self.AddItem(fmpath)
            fmpath = FMConstPathProjectWWWChapters(self, 'wwwchapters')
            self.AddItem(fmpath)
        elif lpath[0] == 'wwwfiles':
            fp = FMConstPathProjectWWWFiles(self, 'wwwfiles')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        elif lpath[0] == 'wwwsite':
            fp = FMConstPathProjectWWWSite(self, 'wwwsite')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        elif lpath[0] == 'wwwchapters':
            fp = FMConstPathProjectWWWChapters(self, 'wwwchapters')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        elif lpath[0] == 'wwwchaptergroups':
            if self.Obj.GrupyRozdzialow and self.Obj.GrupyRozdzialow.Rozdzialy:
                fp = FMConstPathProjectWWWChapterGroups(self, 'wwwchaptergroups')
                self.AddItem(fp)
                ret = fp.SetPath(lpath[1:])
        return ret


class FMConstPathProjectWWWStructs(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)
        self.name = 'Serwisy'
        self.iconClass = 'silk_world'

    def SetPath(self, lpath):
        ret = self
        pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        wclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
        pobj = pclass[self.parent.OID]
        if lpath:
            try:
                aoid = int(lpath[0])
            except:
                aoid = -1
            if aoid >= 0:
                if wclass.ObjectExists(aoid):
                    aobj = wclass[aoid]
                    if not aobj['SGIsDisabled'] and aobj.Projekt.OID == pobj.OID:
                        fp = FMConstPathProjectWWWStruct(self, 'wwwstruct', aobj)
                        self.AddItem(fp)
                        ret = fp.SetPath(lpath[1:])
        else:
            aobj = pobj.WWWMenuStruct
            while aobj:
                if not aobj['SGIsDisabled']:
                    fitem = FMConstPathProjectWWWStruct(self, 'wwwstruct', aobj)
                    self.AddItem(fitem)
                aobj.Next()
        return ret


class FMConstPathProject(FMConstPath):

    def __init__(self, aparent, atype, aobj=None):
        FMConstPath.__init__(self, aparent, aobj.OID, atype)
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.name = storageutil.CP1250_To_UTF8(aobj.Nazwa)
        self.iconClass = 'silk_server_connect'

    def SetPath(self, lpath):
        ret = self
        if not lpath:
            fmpath = FMConstPathProjectFiles(self, 'files')
            self.AddItem(fmpath)
            fmpath = FMConstPathProjectImages(self, 'images')
            self.AddItem(fmpath)
            fmpath = FMConstPathProjectWWWStructs(self, 'wwwstructs')
            self.AddItem(fmpath)
            fmpath = FMConstPathProjectCDN(self, 'cdn')
            self.AddItem(fmpath)
        elif lpath[0] == 'cdn':
            fp = FMConstPathProjectCDN(self, 'cdn')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        elif lpath[0] == 'files':
            fp = FMConstPathProjectFiles(self, 'files')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        elif lpath[0] == 'images':
            fp = FMConstPathProjectImages(self, 'images')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        elif lpath[0] == 'wwwstructs':
            fp = FMConstPathProjectWWWStructs(self, 'wwwstructs')
            self.AddItem(fp)
            ret = fp.SetPath(lpath[1:])
        return ret


class FMConstPathProjects(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)
        self.name = 'Projekty'
        self.iconClass = 'silk_folder_database'

    def SetPath(self, lpath):
        ret = self
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        if lpath:
            try:
                aoid = int(lpath[0])
            except:
                aoid = -1
            if aoid >= 0:
                if aclass.ObjectExists(aoid):
                    aobj = aclass[aoid]
                    if not aobj['SGIsDisabled']:
                        fp = FMConstPathProject(self, 'project', aobj)
                        self.AddItem(fp)
                        ret = fp.SetPath(lpath[1:])
        else:
            aobj = aclass.GetFirstObject()
            while aobj:
                if not aobj['SGIsDisabled']:
                    fitem = FMConstPathProject(self, 'project', aobj)
                    self.AddItem(fitem)
                aobj.Next()
        return ret


class FMConstPathUsers(FMConstPath):

    def __init__(self, aparent, atype, adata=None):
        FMConstPath.__init__(self, aparent, atype, adata)
        self.name = 'Użytkownicy'
        self.iconClass = 'silk_group_gear'

    def SetPath(self, lpath):
        ret = self
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_User']
        if lpath:
            try:
                aoid = int(lpath[0])
            except:
                aoid = -1
            if aoid > 0:
                if aclass.ObjectExists(aoid):
                    aobj = aclass[aoid]
                    fp = FMConstPathUser(self, 'user', aobj)
                    self.AddItem(fp)
                    ret = fp.SetPath(lpath[1:])
        else:
            aobj = aclass.GetFirstObject()
            while aobj:
                if aobj.OID > 0:
                    fitem = FMConstPathUser(self, 'user', aobj)
                    self.AddItem(fitem)
                aobj.Next()
        return ret


class FMRoot(object):

    def __init__(self, UID):
        self.litems = []
        self.ditems = {}
        self.UID = UID

    def AddItem(self, aitem):
        self.litems.append(aitem)
        self.ditems[aitem.id] = aitem

    def GetPath(self, lpath):
        return lpath

    def SetPath(self, apath, atype='', arefobject=None):
        # TODO obsluga atype, np. atype=='image'
        ret = self
        if arefobject:
            ret = FMConstPathObjects(self, 'refobject', adata=arefobject)
            self.AddItem(ret)
        l = filter(None, apath.split('/'))
        #print '  LSPLIT: %s'%str(l)
        if not l:
            fmpath = FMConstPathProjects(self, 'projects')
            self.AddItem(fmpath)
            fmpath = FMConstPathUsers(self, 'users')
            self.AddItem(fmpath)
        elif l[0] == 'projects':
            fp = FMConstPathProjects(self, 'projects')
            self.AddItem(fp)
            ret = fp.SetPath(l[1:])
        elif l[0] == 'users':
            fp = FMConstPathUsers(self, 'users')
            self.AddItem(fp)
            ret = fp.SetPath(l[1:])
        elif l[0] == 'objects':
            fp = FMConstPathObjects(self, 'objects')
            self.AddItem(fp)
            ret = fp.SetPath(l[1:])
        return ret

    def GetItems(self):
        l = []
        for fmpath in self.litems:
            l.extend(fmpath.GetItems())
        return l


class ICORFileManager(object):

    def __init__(self, app):
        self.app = app
        self.acnt = 0

    @cherrypy.expose
    def attachments(self, *args, **kwargs):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        ahttpmethod = cherrypy.request.method
        if hasattr(cherrypy.request, 'json'):
            kwargs = self.app.getRequestJSONAsDict()
        mode = kwargs.get('mode', '')[:30]
        self.app.dumpRequest(args, kwargs)
        ret = ''
        if ahttpmethod == 'GET':
            if mode == 'list':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                if not acontext.CheckContextAccess('table', 'AccessLevelView'):
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                ret = self.app.storeado.dbfiles.getAttachments(acontext)
                return webutil.GetJSONResult(ret)
            elif mode == 'autocomplete':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                #w=acontext.CheckContextAccess('chapter','AccessLevelView',adefault=-1)
                #if w<0:
                w = acontext.CheckContextAccess('table', 'AccessLevelView')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                field = kwargs.get('field', '')
                value = kwargs.get('value', '')
                ret = []
                if field in ['InformacjaPodmiotUdostepniajacy', 'InformacjaOsobaOdpowiedzialna', 'InformacjaOpisCzynnosci', 'Category', 'Kind', 'ItemKey', 'ItemRel', 'ItemType', 'ItemStatus']:
                    ret = self.app.storeado.dbfiles.getAttachmentsAutocomplete(acontext, field, value)
                return webutil.GetJSONResult(ret)
            elif mode == 'remove':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                if not acontext.CheckContextAccess('table', 'AccessLevelDelete'):
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Usuwanie zabronione', asstring=1)
                ret = 'EMPTY'
                foid = storageutil.getStrAsOID(kwargs.get('foid', ''))
                if foid:
                    ret = self.app.storeado.dbfiles.getAttachmentsRemove(acontext, foid)
                return webutil.GetJSONResult(status=ret)
        elif ahttpmethod == 'POST':
            if mode == 'update':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                w = acontext.CheckContextAccess('chapter', 'AccessLevelTableEdit', adefault=-1)
                if w < 0:
                    w = acontext.CheckContextAccess('table', 'AccessLevelEdit')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Aktualizacja zabroniona', asstring=1)
                ret = self.app.storeado.dbfiles.setAttachmentUpdate(acontext, kwargs)
                if ret != 'OK':
                    return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
                return webutil.GetJSONResult(status=ret)
            elif mode == 'updateposition':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                w = acontext.CheckContextAccess('chapter', 'AccessLevelTableEdit', adefault=-1)
                if w < 0:
                    w = acontext.CheckContextAccess('table', 'AccessLevelEdit')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Aktualizacja zabroniona', asstring=1)
                spos = kwargs.get('lpos', '')
                lpos = []
                lspos = spos.split('|')
                for s in lspos:
                    s = storageutil.getStrAsOID(s)
                    if s:
                        lpos.append(s)
                if not lpos:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                ret = self.app.storeado.dbfiles.setAttachmentPositions(acontext, lpos)
                if ret != 'OK':
                    return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
                return webutil.GetJSONResult(status=ret)
        return webutil.GetJSONResult(status=ret)

    @cherrypy.expose
    def httpattachments(self, *args, **kwargs):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        ahttpmethod = cherrypy.request.method
        if hasattr(cherrypy.request, 'json'):
            kwargs = self.app.getRequestJSONAsDict()
        mode = kwargs.get('mode', '')[:30]
        self.app.dumpRequest(args, kwargs)
        ret = ''
        if ahttpmethod == 'GET':
            if mode == 'list':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                if not acontext.CheckContextAccess('table', 'AccessLevelView'):
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                ret = self.app.storeado.dbfiles.getHTTPAttachments(acontext)
                return webutil.GetJSONResult(ret)
            elif mode == 'autocomplete':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                #w=acontext.CheckContextAccess('chapter','AccessLevelView',adefault=-1)
                #if w<0:
                w = acontext.CheckContextAccess('table', 'AccessLevelView')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                field = kwargs.get('field', '')
                value = kwargs.get('value', '')
                ret = []
                if field in ['InformacjaPodmiotUdostepniajacy', 'InformacjaOsobaOdpowiedzialna', 'InformacjaOpisCzynnosci', 'Category', 'Kind', 'ItemKey', 'ItemRel', 'ItemType', 'ItemStatus']:
                    ret = self.app.storeado.dbfiles.getHTTPAttachmentsAutocomplete(acontext, field, value)
                return webutil.GetJSONResult(ret)
            elif mode == 'remove':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                if not acontext.CheckContextAccess('table', 'AccessLevelDelete'):
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Usuwanie zabronione', asstring=1)
                ret = 'EMPTY'
                foid = storageutil.getStrAsOID(kwargs.get('foid', ''))
                if foid:
                    ret = self.app.storeado.dbfiles.getHTTPAttachmentsRemove(acontext, foid)
                return webutil.GetJSONResult(status=ret)
            elif mode == 'searchinit':
                ret = []
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
                pobj = aclass.GetFirstObject()
                while pobj:
                    if pobj['SGIsDisabled']:
                        pobj.Next()
                        continue
                    if ICORSecurity.CheckRecursiveAccessLevelForUser(pobj, 'AccessLevelView', UID):
                        dd = {'value': str(pobj.OID), 'label': pobj.Nazwa, }
                        ret.append(dd)
                    pobj.Next()
                return webutil.GetJSONResult(ret)
            elif mode == 'searchfiles':
                acontext = self.app.GetADOContext(kwargs, UID, abyproject=1)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                if not acontext.CheckContextAccess('project', 'AccessLevelView'):
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                ret = self.app.storeado.dbfiles.searchHTTPAttachments(acontext)
                return webutil.GetJSONResult(ret)
        elif ahttpmethod == 'POST':
            if mode == 'update':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                w = acontext.CheckContextAccess('chapter', 'AccessLevelTableEdit', adefault=-1)
                if w < 0:
                    w = acontext.CheckContextAccess('table', 'AccessLevelEdit')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Aktualizacja zabroniona', asstring=1)
                ret = self.app.storeado.dbfiles.setHTTPAttachmentUpdate(acontext, kwargs)
                if ret != 'OK':
                    return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
                return webutil.GetJSONResult(status=ret)
            elif mode == 'updateposition':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                w = acontext.CheckContextAccess('chapter', 'AccessLevelTableEdit', adefault=-1)
                if w < 0:
                    w = acontext.CheckContextAccess('table', 'AccessLevelEdit')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Aktualizacja zabroniona', asstring=1)
                spos = kwargs.get('lpos', '')
                lpos = []
                lspos = spos.split('|')
                for s in lspos:
                    s = storageutil.getStrAsOID(s)
                    if s:
                        lpos.append(s)
                if not lpos:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                ret = self.app.storeado.dbfiles.setHTTPAttachmentPositions(acontext, lpos)
                if ret != 'OK':
                    return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
                return webutil.GetJSONResult(status=ret)
        return webutil.GetJSONResult(status=ret)

    @cherrypy.expose
    def attachmentsdata(self, *args, **kwargs):
        filedata = kwargs.get('file', None)
        if filedata is None:
            return webutil.GetJSONErrorResult('no_data', 403, 'brak danych', asstring=1)
        #ioid=storageutil.UTF8_To_CP1250(kwargs.get('ioid',''))
        #tid=int(storageutil.UTF8_To_CP1250(kwargs.get('tid','-1')))
        #poid=int(storageutil.UTF8_To_CP1250(kwargs.get('poid','-1')))
        #chapterid=int(storageutil.UTF8_To_CP1250(kwargs.get('chapterid','-1')))
        #filename=storageutil.UTF8_To_CP1250(filedata.filename)
        filename = filedata.filename
        if not filename:
            return webutil.GetJSONErrorResult('no_data', 403, 'Brak pliku', asstring=1)
        #print 'FILE:',storageutil.UTF8_To_CP1250(filedata.filename)
        #print 'KWARGS:',kwargs
        args = list(args)
        asession = self.app.GetSession(args=args, kwargs=kwargs)
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            UID = int(kwargs.get('uid', '-1'))
            if UID < 0:
                return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        if kwargs.get('mode', '') != 'uploadAttachment':
            return webutil.GetJSONErrorResult('no_data', 403, 'Błędny tryb', asstring=1)
        ahttpmethod = cherrypy.request.method
        #if hasattr(cherrypy.request,'json'):
        #kwargs=self.app.getRequestJSONAsDict()
        #mode=kwargs.get('mode','')[:30]
        ret = ''
        if ahttpmethod == 'POST':
            acontext = self.app.GetADOContext(kwargs, UID)
            if acontext is None:
                return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
            if not acontext.CheckContextAccess('table', 'AccessLevelFilesUpload'):
                return webutil.GetJSONErrorResult('no_auth', 403, 'Wgrywanie zabronione', asstring=1)
            ret = self.app.storeado.dbfiles.addAttachment(acontext, filename, filedata)
            if ret != 'OK':
                return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
        return webutil.GetJSONResult(status=ret)

    @cherrypy.expose
    def httpattachmentsdata(self, *args, **kwargs):
        filedata = kwargs.get('file', None)
        if filedata is None:
            return webutil.GetJSONErrorResult('no_data', 403, 'brak danych', asstring=1)
        #ioid=storageutil.UTF8_To_CP1250(kwargs.get('ioid',''))
        #tid=int(storageutil.UTF8_To_CP1250(kwargs.get('tid','-1')))
        #poid=int(storageutil.UTF8_To_CP1250(kwargs.get('poid','-1')))
        #chapterid=int(storageutil.UTF8_To_CP1250(kwargs.get('chapterid','-1')))
        #filename=storageutil.UTF8_To_CP1250(filedata.filename)
        filename = filedata.filename
        if not filename:
            return webutil.GetJSONErrorResult('no_data', 403, 'Brak pliku', asstring=1)
        #print 'FILE:',storageutil.UTF8_To_CP1250(filedata.filename)
        #print 'KWARGS:',kwargs
        args = list(args)
        asession = self.app.GetSession(args=args, kwargs=kwargs)
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            UID = int(kwargs.get('uid', '-1'))
            if UID < 0:
                return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        if kwargs.get('mode', '') != 'uploadHTTPAttachment':
            return webutil.GetJSONErrorResult('no_data', 403, 'Błędny tryb', asstring=1)
        ahttpmethod = cherrypy.request.method
        #if hasattr(cherrypy.request,'json'):
        #kwargs=self.app.getRequestJSONAsDict()
        #mode=kwargs.get('mode','')[:30]
        ret = ''
        if ahttpmethod == 'POST':
            acontext = self.app.GetADOContext(kwargs, UID)
            if acontext is None:
                return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
            if not acontext.CheckContextAccess('table', 'AccessLevelFilesUpload'):
                return webutil.GetJSONErrorResult('no_auth', 403, 'Wgrywanie zabronione', asstring=1)
            ret = self.app.storeado.dbfiles.addHTTPAttachment(acontext, filename, filedata)
            if ret != 'OK':
                return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
        return webutil.GetJSONResult(status=ret)

    @cherrypy.expose
    def multimedia(self, *args, **kwargs):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        ahttpmethod = cherrypy.request.method
        if hasattr(cherrypy.request, 'json'):
            #self.app.dumpRequest(args,kwargs)
            kwargs = self.app.getRequestJSONAsDict()
        mode = kwargs.get('mode', '')[:30]
        ret = ''
        if ahttpmethod == 'GET':
            if mode == 'list':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                if not acontext.CheckContextAccess('table', 'AccessLevelView'):
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                ret = self.app.storeado.dbfiles.getMultimedia(acontext)
                return webutil.GetJSONResult(ret)
            elif mode == 'autocomplete':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                #w=acontext.CheckContextAccess('chapter','AccessLevelView',adefault=-1)
                #if w<0:
                w = acontext.CheckContextAccess('table', 'AccessLevelView')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                field = kwargs.get('field', '')
                value = kwargs.get('value', '')
                ret = []
                if field in ['InformacjaPodmiotUdostepniajacy', 'InformacjaOsobaOdpowiedzialna', 'InformacjaOpisCzynnosci', 'Category', 'Kind', 'ItemKey', 'ItemRel', 'ItemGroup', 'ItemType', 'ItemStatus']:
                    ret = self.app.storeado.dbfiles.getMultimediaAutocomplete(acontext, field, value)
                return webutil.GetJSONResult(ret)
            elif mode == 'remove':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                if not acontext.CheckContextAccess('table', 'AccessLevelDelete'):
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Usuwanie zabronione', asstring=1)
                ret = 'EMPTY'
                foid = storageutil.getStrAsOID(kwargs.get('foid', ''))
                if foid:
                    ret = self.app.storeado.dbfiles.getMultimediaRemove(acontext, foid)
                return webutil.GetJSONResult(status=ret)
        elif ahttpmethod == 'POST':
            if mode == 'update':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                w = acontext.CheckContextAccess('chapter', 'AccessLevelTableEdit', adefault=-1)
                if w < 0:
                    w = acontext.CheckContextAccess('table', 'AccessLevelEdit')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Aktualizacja zabroniona', asstring=1)
                ret = self.app.storeado.dbfiles.setMultimediaUpdate(acontext, kwargs)
                if ret != 'OK':
                    return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
                return webutil.GetJSONResult(status=ret)
            elif mode == 'updateposition':
                acontext = self.app.GetADOContext(kwargs, UID)
                if acontext is None:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                w = acontext.CheckContextAccess('chapter', 'AccessLevelTableEdit', adefault=-1)
                if w < 0:
                    w = acontext.CheckContextAccess('table', 'AccessLevelEdit')
                if not w:
                    return webutil.GetJSONErrorResult('no_auth', 403, 'Aktualizacja zabroniona', asstring=1)
                spos = kwargs.get('lpos', '')
                lpos = []
                lspos = spos.split('|')
                for s in lspos:
                    s = storageutil.getStrAsOID(s)
                    if s:
                        lpos.append(s)
                if not lpos:
                    return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                ret = self.app.storeado.dbfiles.setMultimediaPositions(acontext, lpos)
                if ret != 'OK':
                    return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
                return webutil.GetJSONResult(status=ret)
        return webutil.GetJSONResult(status=ret)

    @cherrypy.expose
    def multimediadata(self, *args, **kwargs):
        filedata = kwargs.get('file', None)
        if filedata is None:
            return webutil.GetJSONErrorResult('no_data', 403, 'brak danych', asstring=1)
        #ioid=storageutil.UTF8_To_CP1250(kwargs.get('ioid',''))
        #tid=int(storageutil.UTF8_To_CP1250(kwargs.get('tid','-1')))
        #poid=int(storageutil.UTF8_To_CP1250(kwargs.get('poid','-1')))
        #chapterid=int(storageutil.UTF8_To_CP1250(kwargs.get('chapterid','-1')))
        #filename=storageutil.UTF8_To_CP1250(filedata.filename)
        filename = filedata.filename
        if not filename:
            return webutil.GetJSONErrorResult('no_data', 403, 'Brak pliku', asstring=1)
        #print 'FILE:',storageutil.UTF8_To_CP1250(filedata.filename)
        #print 'KWARGS:',kwargs
        args = list(args)
        #print '$$ multimediadata 1: args: %s kwargs: %s'%(args,kwargs)
        asession = self.app.GetSession(args=args, kwargs=kwargs)
        #print '$$ multimediadata 2: args: %s kwargs: %s'%(args,kwargs)
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            UID = int(kwargs.get('uid', '-1'))
            if UID < 0:
                return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        if kwargs.get('mode', '') != 'uploadMultimedia':
            return webutil.GetJSONErrorResult('no_data', 403, 'Błędny tryb', asstring=1)
        ahttpmethod = cherrypy.request.method
        #if hasattr(cherrypy.request,'json'):
        #kwargs=self.app.getRequestJSONAsDict()
        #mode=kwargs.get('mode','')[:30]
        ret = ''
        if ahttpmethod == 'POST':
            acontext = self.app.GetADOContext(kwargs, UID)
            if acontext is None:
                return webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
            if not acontext.CheckContextAccess('table', 'AccessLevelFilesUpload'):
                return webutil.GetJSONErrorResult('no_auth', 403, 'Wgrywanie zabronione', asstring=1)
            ret = self.app.storeado.dbfiles.addMultimedia(acontext, filename, filedata)
            if ret != 'OK':
                return webutil.GetJSONErrorResult('no_data', 403, ret, asstring=1)
        return webutil.GetJSONResult(status=ret)

    @cherrypy.expose
    def api(self, *args, **kwargs):
        #print 'FILEMANAGER API:'
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        #auser=ICORSecurity.ICORSecurityUser(UID)
        #d['user']['EMail']=storageutil.CP1250_To_UTF8(auser.VCFEMail)
        #return json.dumps(d)
        #self.app.dumpRequest(args,kwargs)
        ahttpmethod = cherrypy.request.method
        ret = ''
        if hasattr(cherrypy.request, 'json'):
            kwargs = cherrypy.request.json
        mode = storageutil.UTF8_To_CP1250(kwargs.get('mode', '')[:30])
        if mode == 'initiate' and ahttpmethod == 'GET':
            ret = '''{"data":{"id":"\/","type":"initiate","attributes":{"config":[]}}}'''
        elif mode == 'getfolder' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), kwargs.get('type', ''))
            ret = afmroot.GetItems()
        elif mode == 'getimage' and ahttpmethod == 'GET':
            athumbnail = kwargs.get('thumbnail', '') == 'true'
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            if athumbnail:
                aitem.GetThumbnail()
            return aitem.ServeFileAccel()
            #afilepath=aitem.GetItemPath()
            #return cherrypy.lib.static.serve_file(afilepath) #(filename, mime, basename)
        elif mode == 'readfile':    # and ahttpmethod=='GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            return aitem.ServeFileAccel()
            #afilepath=aitem.GetItemPath()
            #return cherrypy.lib.static.serve_file(afilepath) #(filename, mime, basename)
        elif mode == 'addfolder' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            ret = aitem.AddFolder(kwargs.get('name', ''))
        elif mode == 'upload' and ahttpmethod == 'POST':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            ret = aitem.Upload(kwargs.get('files', ''))
        elif mode == 'rename' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('old', ''), '')
            ret = aitem.Rename(kwargs.get('new', ''))
        elif mode == 'move' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('old', ''), '')
            anewitem = afmroot.SetPath(kwargs.get('new', ''), '')
            ret = anewitem.Move(aitem)
        elif mode == 'copy' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('source', ''), '')
            anewitem = afmroot.SetPath(kwargs.get('target', ''), '')
            ret = anewitem.Copy(aitem)
        elif mode == 'replace' and ahttpmethod == 'POST':    # TODO
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            ret = aitem.Replace()
        elif mode == 'editfile' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            afilepath = aitem.GetItemPath()
            ret = aitem.GetFileInfoRec(acontent=1)
        elif mode == 'savefile' and ahttpmethod == 'POST':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            ret = aitem.SaveFile(kwargs.get('content', ''))
        elif mode == 'delete' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            ret = aitem.Delete()
        elif mode == 'download' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            if cherrypy.request.headers.get('X-Requested-With', '') == 'XMLHttpRequest':
                ret = aitem.GetFileInfoRec()
            else:
                return aitem.ServeFileAccel(download=1)
                #afilepath=aitem.GetItemPath()
                ##mime='application/octet-stream'
                #return cherrypy.lib.static.serve_file(afilepath,'application/x-download','attachment')
        elif mode == 'summarize' and ahttpmethod == 'GET':
            afmroot, aitem = self.GetItem(UID, kwargs.get('path', ''), '')
            ret={
               "id": "/",
               "type": "summary",
               "attributes": {
                  "size": 1545463665,
                  "files": 56,
                  "folders": 14,
                  "sizeLimit": 2000000000
               }
            } # yapf: disable
        return webutil.GetJSONResult(ret)

    def GetItem(self, UID, apath, atype=''):
        afmroot = FMRoot(UID)
        aitem = afmroot.SetPath(apath, atype)
        return afmroot, aitem
