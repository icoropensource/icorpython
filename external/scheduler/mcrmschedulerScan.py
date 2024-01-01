# -*- coding: utf-8 -*-
import sys
if 0:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import optparse
import os
try:
    import json
except:
    import simplejson as json

import appplatform.startutil as startutil
import icorstartinit
import appplatform.storageutil as storageutil
from icorlib.icorinterface import *
import icorlib.projekt.mcrmbasesimple as MCRMBaseSimple

from PIL import Image
import scandir


class MCRMFileScanner(object):

    def __init__(self):
        self.cms = MCRMBaseSimple.CMS(alogname='scan', aconsole=1, acominitialize=1)
        self.dbdata = {}
        self.filedata = {}

    def GetDBProjectData(self, aproject):
        aTable_HTTPFileUploads = '%shttpfileuploads_%d' % (aproject.BaseNameModifier, 0)
        asql = '''
         with t1(result) as (
            select
            _OID,Name,Path,ParentPath,PathLevel,IsDir,Checksum,FileSize,LastModification,Status,
            FileExtension,FileName,FileTypePath 
            from %s
            for json path
         )
         select cast(result as varchar(max)) result from t1
        ''' % (aTable_HTTPFileUploads, )
        ret = {}
        rs = aproject.aadoutil.GetRS(asql, aclient=1)
        if rs.State != aproject.aadoutil.adoconst.adStateClosed:
            s = aproject.aadoutil.GetRSValueAsStr(rs, 'result')
            litems = json.loads(s)
            for d in litems:
                k = os.path.join(d['ParentPath'] + d['Path'] + d['Name'])
                d['sync'] = ''
                ret[k] = d
            rs = aproject.aadoutil.CloseRS(rs)
        self.dbdata = ret

    def GetItemsAsFiles(self, abasepath, parentpath, adirpath='', pathlevel=0):
        awwwpath = os.path.join(abasepath, parentpath, adirpath)
        print 'GetItemsAsFiles: [%s] - [%s] - [%s] - awwwpath: [%s]' % (abasepath, parentpath, adirpath, awwwpath)
        if not os.path.isdir(awwwpath):
            return
        for adirentry in scandir.scandir(unicode(awwwpath)):
            ads = adirentry.stat()
            aname = adirentry.name
            if adirentry.is_dir():
                bdirpath = aname
                if adirpath:
                    adirpath[-1:] != '/'
                    bdirpath = a
                bdirpath = os.path.join(adirpath, aname)
                self.GetItemsAsFiles(abasepath, parentpath, bdirpath, pathlevel + 1)
                continue
            if not adirentry.is_file():
                continue
            aentrypath = os.path.join(awwwpath, aname)
            aext = os.path.splitext(aname)[1].lower()
            asize = ads.st_size
            amodified = storageutil.tdatetime2fmtstr(time.localtime(ads.st_mtime)[:7])
            #acreated=storageutil.tdatetime2fmtstr(time.localtime(ads.st_ctime)[:7])
            #atimestamp=int(ads.st_mtime)
            d = {"name": "%s" % aname, "basepath": abasepath, "parentpath": parentpath, "path": adirpath, "pathlevel": pathlevel, "isdir": 0, "ext": aext, "size": asize, "modified": amodified, "isimage": 0, }
            if aext in ['.gif', '.jpg', '.jpeg', '.png']:
                try:
                    img = Image.open(aentrypath).size
                    d['width'] = img[0]
                    d['height'] = img[1]
                    d['isimage'] = 1
                except:
                    pass
            self.filedata[aentrypath] = d

    def ScanProject(self, aproject):
        print 'scan project: %d - %s - %s' % (aproject.OID, aproject.Project, aproject.WWWDataPathScan, )
        adt1 = time.clock()
        for parentpath in ['httpfiles', 'httpimages']:
            self.GetItemsAsFiles(aproject.WWWDataPathScan, parentpath)
        adt2 = time.clock()
        print '  ** scan time: %0.4f' % (adt2 - adt1, )
        for fp in sorted(self.filedata.keys()):
            print fp, self.filedata[fp]
        return

    def UpdateProject(self, aproject):
        aTable_HTTPFileUploads = '%shttpfileuploads_%d' % (aproject.BaseNameModifier, 0)
        for fv in l:
            rs = aproject.aadoutil.GetRS("select * from %s t1 where Path='%s' and ParentPath='%s'" % (aTable_HTTPFileUploads, fv['name'], fv['path']), aclient=1)
            if rs.State != aproject.aadoutil.adoconst.adStateClosed:
                if rs.EOF or rs.BOF:
                    rs.AddNew()
                    rs.Fields.Item('Path').Value = fv['name']
                    rs.Fields.Item('ParentPath').Value = fv['path']
                    #rs.Fields.Item('').Value=
                    #rs.Fields.Item('').Value=
                rs.Fields.Item('ItemValue').Value = ''
                aproject.aadoutil.UpdateRS(rs)
                rs = aproject.aadoutil.CloseRS(rs)

    def Process(self):
        self.cms.GetAllProjects(adump=1)
        try:
            for aproject in self.cms.Projects.values():
                aproject.OpenConnection()
                try:
                    if 0:
                        self.GetDBProjectData(aproject)
                        self.ScanProject(aproject)
                        for awwwmenustruct in aproject.wwwmenustruct.values():
                            print '  wwwmenustruct: %d - %s' % (awwwmenustruct.OID, aproject.WWWDataPathScan)
                finally:
                    aproject.CloseConnection()
        except:
            self.cms.LogException()


def Main():
    print startutil.appconfig.HTTPFILES
    ascanner = MCRMFileScanner()
    ascanner.Process()


if __name__ == "__main__":
    ret = startutil.WaitForApp('ICOR_Scheduler_Scan', 1)
    if ret:
        optparser = optparse.OptionParser()
        optparser.add_option("-w", "--windowhide", action="store_true", dest="window_hide", help="Hide window")
        options, args = optparser.parse_args()
        if options.window_hide:
            try:
                startutil.HideWindow()
            except:
                print 'Can not hide..'
        Main()
