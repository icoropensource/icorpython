# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwserver.icorwwwinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import appplatform.startutil as startutil
import CLASSES_Library_NetBase_Utils_ImageUtil as ImageUtil
import CLASSES_Library_ICORBase_Interface_ICORSync as ICORSync
import icorlib.projekt.mcrmrssinterface as MCRMRSSInterface
import icorlib.projekt.mcrmbasesimple as MCRMBaseSimple
import icorlib.projekt.mcrmwwwmenumodel as MCRMWWWMenuModel
import CLASSES_Library_NetBase_Utils_Slimmer as Slimmer

import icordbmain.adoutil as ADOLibInit
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import pythoncom
#import win32com.client
import os
import shutil
import re
import time

import sys
import smtplib
import types

import traceback
import CLASSES_Library_ICORBase_External_MProfile as MProfile
#import CLASSES_Library_NetBase_Utils_SpeechUtil as SpeechUtil

import icordbmain.dbaccess as dbaccess

USER_DICT = {}
USER_EMAIL = {}
TWO32 = 2L**32

adolib, adoconst, amajor, aminor = ADOLibInit.ADOInitialize()


class DataGenerator:

    def __init__(self, aobj, alog):
        self.Obj = aobj
        self.Log = alog
        self.SimpleCMS = MCRMBaseSimple.CMS()
        acmsproject = self.SimpleCMS.GetProject(aobj.Projekt)
        self.CMSWWWMenuStruct = acmsproject.GetWWWMenuStruct(aobj)
        self.CMSWWWMenuStruct.GetEventsByName(['OnRSSItem', 'OnRSSClose', 'OnRSSOpen', 'OnXMLDataOpen', 'OnXMLDataItem', 'OnXMLDataClose', 'OnXMLDataIndex', 'OnXMLDataBeforeClose'])

        self.StructVars = ICORUtil.ParseVars(aobj.StructVars, {'aCgiScriptPath': '', 'aFileUploadsOrderInChapters': 'Description,Name', 'aHTTPFileUploadsOrderInChapters': 'Description,Name'})
        self.XMLOutputDirName = self.StructVars.get('aXMLOutputDirName', 'xml')
        self.XMLOutputByChapter = int(self.StructVars.get('aXMLOutputByChapter', '0'))
        self.NoIndexFiles = int(self.StructVars.get('aNoIndexFiles', '0'))
        self.RSSOutputDirName = self.StructVars.get('aRSSOutputDirName', 'rss')
        self.RSSOutputByChapter = int(self.StructVars.get('aRSSOutputByChapter', '0'))

        self.BaseNameModifier = aobj.Projekt.BaseNameModifier
        self.InfoTablesSufix = aobj['InfoTablesSufix', mt_Integer]

        self.Path = FilePathAsSystemPath(aobj.AppPaths.SciezkaAplikacji)
        self.FilesPath = self.Path + '/files/'

        awwwdatafilespath = FilePathAsSystemPath(aobj.Projekt.WWWDataPath)
        awwwdatafilespath = awwwdatafilespath.replace('\\', '/')
        if awwwdatafilespath[-1:] != '/':
            awwwdatafilespath = awwwdatafilespath + '/'
        self.WWWDataFilesPath = awwwdatafilespath + 'SQLFiles/'

        self.ConnectionString = dbaccess.GetConnectionString(aobj.DBAccess)
        self.SingleFileOID = ''
        self.OnGetChapterSQL = None

    def GetXMLFilePath(self, achapterid, afilenamemodifier=''):
        apath = self.Path + '/' + self.XMLOutputDirName
        if self.XMLOutputByChapter:
            apath = apath + '/' + str(achapterid)
            if not os.path.exists(apath):
                os.makedirs(apath)
        apath = apath + '/chapter_%d%s.xml' % (achapterid, afilenamemodifier)
        return apath

    def Process(self, atableoid, achapterid, aignoregeneratedisabled, anocloseconnection=0, avirtual=0):
        self.VirtualGenerate = avirtual
        lret = []
        self.Connection = adolib.Connection()
        acnt = 7
        while acnt:
            try:
                self.Connection.Open(self.ConnectionString)
                break
            except:
                if self.Log:
                    self.Log.LogException('timeout nr %d w dostepie do bazy danych' % acnt)
                acnt = acnt - 1
                if not acnt:
                    raise
                time.sleep(7)
        self.Connection.CursorLocation = adoconst.adUseClient
        self.Connection.CommandTimeout = 0
        try:
            tobj = self.Obj.UserTSQL
            while tobj:
                if tobj['ExecuteNow']:
                    if 0:
                        self.Obj.Class.MainUserTSQL('', self.Obj.OID, '')
                    else:
                        aICORDBEngine.SysBase.SetCMSData(self.Obj.OID, 'Status_UserTSQL', 'N')
                    break
#               asql=tobj.SQLSource
#               try:
#                  rs1,status=self.Connection.Execute(asql)
#                  print 'XML Gen UserTSQL execute status:',status
#               except:
#                  self.Log.LogException('Error in UserTSQL command: '+asql)
#                  print 'Error in UserTSQL command:',asql
#                  raise
                tobj.Next()
            arepldict={'this':self.Obj,'re':re,'string':string,'ICORUtil':ICORUtil,'os':os,'sys':sys,'shutil':shutil,'smtplib':smtplib,'adolib':adolib,
               'aICORDBEngine':aICORDBEngine,
               'aPath':self.Path,
               'aBaseNameModifier':self.BaseNameModifier,
               'aFilesPath':self.FilesPath,
               'aWWWDataFilesPath':self.WWWDataFilesPath,
               'aConnection':self.Connection,
               'aVirtualGenerate':self.VirtualGenerate,
               } # yapf: disable
            tobj = self.Obj.UserCode
            while tobj:
                if tobj['ExecuteNow']:
                    if 0:
                        self.Obj.Class.MainUserCode('', self.Obj.OID, '')
                    else:
                        aICORDBEngine.SysBase.SetCMSData(self.Obj.OID, 'Status_UserCode', 'N')
                    break
#               acode=tobj.SourceCode+'\n'
#               acode=string.replace(acode,chr(13),'')
#               try:
#                  print 'XML Gen UserCode execute: %s <OID:%d>'%(tobj.Nazwa,tobj.OID)
#                  ICORUtil.do_exec(acode,arepldict,arepldict)
#               except:
#                  print 'Error in UserCode command:',acode
#                  self.Log.LogException('Error in UserCode command: '+acode)
#                  raise
                tobj.Next()
#         if achapterid>=0:
#            robj=aobj.Rozdzialy.Class[achapterid]
#            ProcessChapter(robj,apath,abasenamemodifier,afilespath,awwwdatafilespath,aconnection,atableoid=atableoid,achapterid=achapterid)
#         else:
            if self.VirtualGenerate:
                self.RSSContext = None
            else:
                self.RSSContext = MCRMRSSInterface.RSSContext(self.Obj.RSSInfo, alog=self.Log, asimplecms=self.SimpleCMS)
                if self.RSSContext.isEmpty:
                    self.RSSContext = None
            if type(achapterid) == type(1) and achapterid >= 0:
                achapterid = [achapterid, ]
            if type(achapterid) == type([]):
                rclass = self.Obj.Rozdzialy.Class
                for bchapterid in achapterid:
                    robj = rclass[bchapterid]
                    try:
                        self.ProcessChapter(robj, atableoid=-1, achapterid=bchapterid, aignoregeneratedisabled=aignoregeneratedisabled, aprocesssubchapters=0)
                        lret.append(bchapterid)
                    except:
                        import traceback
                        traceback.print_exc()
                        if self.Log:
                            self.Log.LogException('$$$ Error during xmlgen for chapter: ' + str(bchapterid))
            else:
                lret.append(achapterid)
                robj = self.Obj.Rozdzialy
                while robj:
                    self.ProcessChapter(robj, atableoid=atableoid, achapterid=achapterid, aignoregeneratedisabled=aignoregeneratedisabled)
                    robj.Next()
                gobj = self.Obj.GrupyRozdzialow
                while gobj:
                    hobj = gobj.Rozdzialy
                    while hobj:
                        self.ProcessChapter(hobj, atableoid=atableoid, achapterid=achapterid, aignoregeneratedisabled=aignoregeneratedisabled)
                        hobj.Next()
                    gobj.Next()
        finally:
            if not anocloseconnection:
                self.Connection.Close()
        return lret

    def CheckTableTag(self, wtabletag, axmlmode, atableoid, atable, void, aisimage, aimgcount):
        if not wtabletag:
            if axmlmode == 1 and atableoid == 'FILE':
                d = {'OID': void, 'isimage': aisimage}
                if aisimage:
                    aimgcount['i'] = 1 + aimgcount['i']
                    d['ipos'] = aimgcount['i']
                self.fout.TagOpen(atable, d)
            else:
                self.fout.TagOpen(atable, {'OID': void})
            wtabletag = 1
        return wtabletag

    def UpdateIndexData(self, dfouttxt, void, atext):
        if len(atext) == 32 and atext.find(' ') < 0:
            return
        if not self.indexOID:
            self.indexOID = void
        l = dfouttxt.get(self.indexOID, [])
        l.append(atext)
        dfouttxt[self.indexOID] = l

    def Recordset2XML(self, rs, lfouttxt, atableoid, alevel=0, axmlmode=0, aimgcount=None, arsscontext=None, asinglefile=0):
        if aimgcount is None:
            aimgcount = {'i': 0, 'asizex': 160, 'asizey': 120, 'amaxsizex': 0, 'amaxsizey': 0, 'amaxsizekb': -1, 'przycinanie': 0}
        if type(atableoid) != type(1):
            atable = atableoid
        else:
            atable = self.BaseNameModifier + 'BZR_' + str(atableoid)
        reccount = 0
        mf = rs.Fields.Count
        while not rs.EOF and not rs.BOF:
            reccount = reccount + 1
            if not alevel:
                self.indexOID = ''
            wprocess = 0
            wtabletag = 0
            void = ''
            aisimage = 0
            if axmlmode == 1:
                v = rs.Fields.Item('_OID').Value
                void = v.encode('cp1250')
                aisimage = ImageUtil.IsImage(self.WWWDataFilesPath + void + '.dat', aignoreext=1)
    #         xx=rs.Fields.Item('Name').Value
    #         xx.encode('cp1250')
    #         print 'image:',xx,aisimage
            if 0:
                if axmlmode == 1 and atableoid == 'IMAGE' and not aisimage:
                    rs.MoveNext()
                    continue
            for i in range(mf):
                v = rs.Fields.Item(i).Value
                if v is None:
                    continue
                s = rs.Fields.Item(i).Name
                #         if type(v)==type(u""):
                wgoodfieldname = 1
                if s.lower() in ["reftable", "zdjecie", "name", "refoid", "path", 'informacjapodmiotudostepniajacy', 'informacjaosobaodpowiedzialna', 'informacjadatawytworzenia', 'informacjaopisczynnosci']:    #'bzroid',
                    wgoodfieldname = 0
                if s[:1] == '_':
                    wgoodfieldname = 0
                if s.lower() == '_username':
                    v = v.encode('cp1250')
                    ve = ''
                    if USER_DICT.has_key(v):
                        v = USER_DICT[v]
                        ve = USER_EMAIL.get(v, '')
                    else:
                        aoid = aICORDBEngine.User.UserName.Identifiers(v)
                        if aoid > 0:
                            ve = aICORDBEngine.User.VCFEMail[aoid]
                            s1 = aICORDBEngine.User.VCFFirstName[aoid] + ' ' + aICORDBEngine.User.VCFLastName[aoid]
                            s1 = s1.strip()
                            if not s1:
                                s1 = v
                            USER_DICT[v] = s1
                            USER_EMAIL[v] = ve
                            v = s1
                        else:
                            USER_DICT[v] = v
                            USER_EMAIL[v] = ve
                    if arsscontext and not alevel:
                        arsscontext.ItemAuthor = ve
                elif s.lower() == '_action':
                    v = v.encode('cp1250')
                    if v == 'UPDATE':
                        v = 'modyfikacja wartości'
                    elif v == 'INSERT':
                        v = 'nowa pozycja'
                    elif v == 'DELETE':
                        v = 'usunięcie pozycji'
                if s == '_OID':
                    wprocess = 1
                    void = v.encode('cp1250')
                    if arsscontext and not alevel:
                        arsscontext.ItemGUID = void
                elif rs.Fields.Item(i).Type in [adoconst.adDate, adoconst.adDBDate, adoconst.adDBTime, adoconst.adDBTimeStamp]:    #adDate,adDBDate,adDBTime,adDBTimeStamp
                    if wprocess:
                        try:
                            vadt = (v.year, v.month, v.day, v.hour, v.minute, v.second, v.msec)
                            v1 = ICORUtil.tdatetime2fmtstr(vadt)
                        except:
                            vadt = ICORUtil.tzerodatetime()
                            v1 = ''
                        if not self.VirtualGenerate:
                            wtabletag = self.CheckTableTag(wtabletag, axmlmode, atableoid, atable, void, aisimage, aimgcount)
                            self.fout.TagOpen(s.encode('cp1250'), anl='')
                            self.fout.write('<![CDATA[%s]]>' % XMLUtil.GetAsXMLStringCDataNoPL(v1))
                        if wgoodfieldname:
                            self.UpdateIndexData(lfouttxt, void, v1)
                            if arsscontext:
                                arsscontext.ItemTitle.append(v1)
                        if not self.VirtualGenerate:
                            self.fout.TagClose(aindent=0)
                        if arsscontext and not alevel and s.lower() == '_datetime':
                            arsscontext.ItemPubDate = ICORUtil.tdatetime2RFC822datetime(vadt)
                        if arsscontext and not alevel:
                            arsscontext.ItemDict[s] = vadt
                elif rs.Fields.Item(i).Type in [adoconst.adCurrency]:
                    if wprocess:
                        try:
                            hi, lo = v
                            if lo < 0:
                                lo += TWO32
                            v = '%0.2f' % (((long(hi) << 32) + lo) / 10000.0, )
                        except:
                            v = ''
                        if not self.VirtualGenerate:
                            wtabletag = self.CheckTableTag(wtabletag, axmlmode, atableoid, atable, void, aisimage, aimgcount)
                            self.fout.TagOpen(s.encode('cp1250'), anl='', avalue=v)
                        if wgoodfieldname:
                            self.UpdateIndexData(lfouttxt, void, v)
                        if not self.VirtualGenerate:
                            self.fout.TagClose(aindent=0)
                        if arsscontext and not alevel:
                            arsscontext.ItemDict[s] = v
                elif rs.Fields.Item(i).Type not in [adoconst.adChapter, adoconst.adLongVarChar, ]:
                    if wprocess:
                        if type(v) == type(0 == 1):
                            if v:
                                v = '1'
                            else:
                                v = '0'
                        if type(v) != type(''):
                            try:
                                v = v.encode('cp1250')
                            except:
                                #                     print '*** unknown conversion type for *** :',rs.Fields.Item(i).Type
                                v = str(v).encode('cp1250')
    #               print ' '*alevel,s,'=',v[:60]
                        if v.strip():
                            if not self.VirtualGenerate:
                                wtabletag = self.CheckTableTag(wtabletag, axmlmode, atableoid, atable, void, aisimage, aimgcount)
                                self.fout.TagOpen(s.encode('cp1250'), anl='', avalue=v)
                            if wgoodfieldname:
                                self.UpdateIndexData(lfouttxt, void, v)
                                if arsscontext:
                                    if rs.Fields.Item(i).Type not in [adoconst.adTinyInt, adoconst.adSmallInt, adoconst.adInteger, adoconst.adUnsignedTinyInt, adoconst.adUnsignedSmallInt, adoconst.adUnsignedInt, adoconst.adBigInt, adoconst.adUnsignedBigInt, adoconst.adSingle, adoconst.adDouble, adoconst.adDecimal, adoconst.adNumeric, adoconst.adBoolean, adoconst.adCurrency, adoconst.adBinary, adoconst.adVarBinary, adoconst.adLongVarBinary] and not alevel:
                                        arsscontext.ItemTitle.append(v)
                                if arsscontext and not alevel:
                                    arsscontext.ItemDict[s] = v
                            if not self.VirtualGenerate:
                                self.fout.TagClose(aindent=0)
                elif rs.Fields.Item(i).Type == adoconst.adLongVarChar:
                    if wprocess:
                        if s:
                            if type(v) != type(''):
                                v = v.encode('cp1250')    #XMLUtil.GetAsXMLStringNoPL

    #                  print ' '*alevel,s,'=',v[:60]
                            if v.strip():
                                if not self.VirtualGenerate:
                                    wtabletag = self.CheckTableTag(wtabletag, axmlmode, atableoid, atable, void, aisimage, aimgcount)
                                    wslim = 0
                                    if self.CMSWWWMenuStruct.OptimizationLevel:
                                        if v.find('<p'):
                                            wslim = 1
                                        elif v.find('<P'):
                                            wslim = 1
                                        elif v.find('<div'):
                                            wslim = 1
                                        elif v.find('<DIV'):
                                            wslim = 1
                                        elif v.find('<span'):
                                            wslim = 1
                                        elif v.find('<SPAN'):
                                            wslim = 1
                                    if wslim:
                                        v = atext = Slimmer.slimmer(v, 'html')
                                    self.fout.TagOpen(s.encode('cp1250'), {'OID': void}, anl='', avalue=v)
                                if wgoodfieldname:
                                    self.UpdateIndexData(lfouttxt, void, ICORUtil.StripHTMLTags(v))
                                    if arsscontext:
                                        arsscontext.ItemDescription.append(v)
                                        arsscontext.ItemDict[s] = v
                                if not self.VirtualGenerate:
                                    self.fout.TagClose(aindent=0)
                elif rs.Fields.Item(i).Type == adoconst.adChapter:
                    #            print ' '*alevel,s,'RECORDSET'
                    if v.RecordCount > 0:
                        if not self.VirtualGenerate:
                            wtabletag = self.CheckTableTag(wtabletag, axmlmode, atableoid, atable, void, aisimage, aimgcount)
                        self.Recordset2XML(v, lfouttxt, s, alevel + 1, aimgcount=aimgcount, arsscontext=arsscontext)
                else:
                    print ' ' * alevel, s, 'field has other type:', rs.Fields.Item(i).Type
            if axmlmode == 1 and atableoid == 'FILE' and not self.VirtualGenerate:
                aname = rs.Fields.Item("Name").Value
                anamepath, aname = os.path.split(aname.encode('cp1250'))
                afilesize = rs.Fields.Item("FileSize").Value
                self.fout.TagOpen('PrettyFileSize', anl='', avalue=ICORUtil.GetKBSize(afilesize))
                self.fout.TagClose(aindent=0)
                adstfile = self.FilesPath + void + '/' + aname
                if not os.path.exists(self.FilesPath + void):
                    try:
                        os.mkdir(self.FilesPath + void)
                    except Exception, e:
                        print str(e)
                        print 'WARNING: Bad directory name', self.FilesPath + void
                        if self.Log:
                            self.Log.LogException('WARNING: Bad directory name ' + self.FilesPath + void)
                if not os.path.exists(adstfile):
                    try:
                        if aisimage and ((aimgcount['amaxsizex'] > 0 and aimgcount['amaxsizey'] > 0) or aimgcount['amaxsizekb'] > 0):
                            ImageUtil.ResizeImageByConstraint(self.WWWDataFilesPath + void + '.dat', adstfile, aimgcount['amaxsizex'], aimgcount['amaxsizey'], aimgcount['amaxsizekb'])
                        else:
                            shutil.copyfile(self.WWWDataFilesPath + void + '.dat', adstfile)
                    except Exception, e:
                        print str(e)
                        print 'WARNING: Bad file name:', self.WWWDataFilesPath + void + '.dat', adstfile
                        if self.Log:
                            self.Log.LogException('WARNING: Bad file name: ' + self.WWWDataFilesPath + void + '.dat ' + adstfile)
                if axmlmode == 1 and aisimage:
                    aname = rs.Fields.Item("Name").Value
                    anamepath, aname = os.path.split(aname.encode('cp1250'))
                    adstfile = self.FilesPath + void + '/' + void + '.jpg'
                    if not os.path.exists(self.FilesPath + void):
                        try:
                            os.mkdir(self.FilesPath + void)
                        except Exception, e:
                            print str(e)
                            print 'WARNING: Bad directory name', self.FilesPath + void
                            if self.Log:
                                self.Log.LogException('WARNING: Bad directory name ' + self.FilesPath + void)
                    if not os.path.exists(adstfile):    #$$ brak generowania po zmianie parametrow galerii
                        try:
                            if self.Log:
                                self.Log.Log('Resize thumbnail: ' + str(aimgcount))
                            ImageUtil.ResizeImageByConstraint(self.WWWDataFilesPath + void + '.dat', adstfile, aimgcount['asizex'], aimgcount['asizey'], -1, aimgcount['przycinanie'], alog=self.Log)
                        except Exception, e:
                            print str(e)
                            print 'WARNING: Error during thumbnail name:', self.WWWDataFilesPath + void + '.dat', adstfile
                            if self.Log:
                                self.Log.LogException('WARNING: Error during thumbnail name: ' + self.WWWDataFilesPath + void + '.dat ' + adstfile)
            if wtabletag and not self.VirtualGenerate:
                if not axmlmode:
                    asql = "select _OID, Name, Path, FileSize, LastModification, Description, InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, RefTable, RefOID, _datetime, _UID, _username from %sFILEUPLOADS_0 WHERE Status not in ('D','U') and RefOID='%s' ORDER BY %s" % (self.BaseNameModifier, void, self.StructVars.get('aFileUploadsOrderInChapters', 'Description,Name'))    #InformacjaOpisCzynnosci,
                    if 0:
                        try:
                            rs1, status = self.Connection.Execute(asql)
                            if rs1.State != adoconst.adStateClosed and not rs1.EOF:
                                self.fout.TagOpen('IMAGES', {'OID': void})
                                self.Recordset2XML(rs1, lfouttxt, 'IMAGE', alevel + 1, axmlmode=1, aimgcount=aimgcount)
                                self.fout.TagClose()
                        except Exception, e:
                            print str(e)
                            print 'Error in SQL Images command:', asql
                            if self.Log:
                                self.Log.LogException('Error in SQL Images command: ' + asql)
                            raise
                    try:
                        rs1, status = self.Connection.Execute(asql)
                        if rs1.State != adoconst.adStateClosed and not rs1.EOF:
                            self.fout.TagOpen('FILES', {'OID': void})
                            alasti = aimgcount['i']
                            aimgcount['i'] = 0
                            self.Recordset2XML(rs1, lfouttxt, 'FILE', alevel + 1, axmlmode=1, aimgcount=aimgcount)
                            aimgcount['i'] = alasti
                            self.fout.TagClose()
                    except Exception, e:
                        print str(e)
                        print 'Error in SQL Files command:', asql
                        if self.Log:
                            self.Log.LogException('Error in SQL Files command: ' + asql)
                        raise
                    if not alevel:
                        if atableoid > 0:
                            asql = "select TOP 50 _OID, InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, _OIDDictRef,_ChapterID,_datetime,_username,_OIDRef,_action from %sBZR_V_%d WHERE _OIDRef='%s' ORDER BY _datetime DESC" % (self.BaseNameModifier, atableoid, void)
                            try:
                                rs1, status = self.Connection.Execute(asql)
                                if rs1.State != adoconst.adStateClosed and not rs1.EOF:
                                    if arsscontext:
                                        arsscontext.ItemGUID = rs.Fields.Item('_OID').Value.encode('cp1250')
                                    self.fout.TagOpen('VERSIONS', {'OID': void})
                                    self.Recordset2XML(rs1, lfouttxt, 'VERSION', alevel + 1, axmlmode=2, aimgcount=aimgcount)
                                    self.fout.TagClose()
                            except Exception, e:
                                print str(e)
                                print 'Error in SQL Versions command:', asql
                                if self.Log:
                                    self.Log.LogException('Error in SQL Versions command: ' + asql)
        #                  traceback.print_exc()
        #                  print '--------------'
#                        raise
                        dd = {'thisGenerator': self, 'aTable': atable, 'aTableOID': atableoid, 'aItemOID': void}
                        try:
                            ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataItem')
                        except:
                            if self.Log:
                                self.Log.LogException('error in OnXMLDataItem event')
                            import traceback
                            traceback.print_exc()
                        if arsscontext:
                            try:
                                arsscontext.WriteLink(atableid=atableoid)
                                arsscontext.NewLink()
                            except:
                                if self.Log:
                                    self.Log.LogException('Error in RSS')
                                traceback.print_exc()
                                print '--------------'
                self.fout.TagClose()
            if not asinglefile or alevel:
                rs.MoveNext()
            if asinglefile and not alevel:
                break
        return reccount

    def ProcessChapter_Old(self, robj, aindent=0, atableoid=-1, achapterid=-1, aignoregeneratedisabled=0, aprocesssubchapters=1):
        wgen = 1
        tobj = robj.TabelaZrodlowa
        if atableoid >= 0 and tobj.OID != atableoid:
            wgen = 0
        #$$ czy na pewno atableoid moze byc rozne od tobj.OID???
        if robj.SGHref:
            wgen = 0
        if achapterid >= 0:
            if robj.OID == achapterid:
                wgen = 1
            else:
                wgen = 0
        if tobj.Nazwa in ['Rejestr zmian', 'Aktualności']:
            wgen = 1
        if not wgen and robj['IsAutoGenerate', mt_Integer]:
            wgen = 1
        if wgen and not aignoregeneratedisabled and robj['IsGenerateDisabled', mt_Integer]:
            wgen = 0
#      if wgen and robj['SGIsMenuDisabled',mt_Integer]:
#         wgen=0
        wnoindex = robj['SGIsIndexDisabled', mt_Integer]
        if self.NoIndexFiles:
            wnoindex = 1
        if wgen:
            atitle = robj.Naglowek
            print '  ' * aindent, atitle
            amodels = MCRMWWWMenuModel.WWWMenuChapterModels(robj)
            amodel = amodels.GetModel('struktura', 'sqlshape')
            asql = amodel.ModelText
            gobj = robj.Galeria
            if gobj:
                aimgcount = {'i': 0, 'asizex': gobj['RozmiarX'], 'asizey': gobj['RozmiarY'], 'amaxsizex': gobj['MaksymalnyRozmiarX'], 'amaxsizey': gobj['MaksymalnyRozmiarY'], 'amaxsizekb': gobj['MaksymalnyRozmiarKB'], 'przycinanie': gobj['Przycinanie', mt_Integer]}
            else:
                aimgcount = {'i': 0, 'asizex': 160, 'asizey': 120, 'amaxsizex': 0, 'amaxsizey': 0, 'amaxsizekb': -1, 'przycinanie': 0}
    #$$ zrobic probe otwarcia co kilka sekund
            axmlfilepath = self.GetXMLFilePath(robj.OID)
            self.fout = XMLUtil.MXMLFile(axmlfilepath, anopl=1, aencoding='utf-8', astemp=1)
            brsscontext = self.RSSContext
            if self.RSSContext:
                arssdir = '/' + self.RSSOutputDirName + '/'
                if self.RSSOutputByChapter:
                    arssdir = arssdir + str(robj.OID) + '/'
                self.RSSContext.OpenFile(robj, self.Path, atitle, adir=arssdir)
                if self.RSSContext.IsChapterDisabled:
                    brsscontext = None
            dfouttxt = {}

            dd = {'thisGenerator': self, 'aTableOID': atableoid, 'aChapterObj': robj, 'aNoIndex': wnoindex}
            try:
                self.CMSWWWMenuStruct.SingleFileOID = self.SingleFileOID
                ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataOpen')
            except:
                if self.Log:
                    self.Log.LogException('error in OnXMLDataOpen event')
                import traceback
                traceback.print_exc()

            self.fout.Header()
            self.fout.TagOpen('CHAPTERDATA', {'title': atitle})
            try:
                if asql:
                    try:
                        rs, status = self.Connection.Execute(asql)
                    except Exception, e:
                        print str(e)
                        print 'Error in SQL Chapter command:', asql
                        if self.Log:
                            self.Log.LogException('Error in SQL Chapter command: ' + asql)
                        raise
                    try:
                        if rs.State != adoconst.adStateClosed:
                            self.Recordset2XML(rs, dfouttxt, robj.TabelaZrodlowa.OID, aimgcount=aimgcount, arsscontext=brsscontext)

                        if not wnoindex:
                            #                     l=os.listdir(self.Path+'/index/')
                            #                     for finame in l:
                            #                        if finame.find('chapter_%d_'%robj.OID)==0:
                            #                           try:
                            #                              os.unlink(self.Path+'/index/'+finame)
                            #                           except:
                            #                              print 'Error in XML Chapter command - delete index file: '+finame
                            for void in dfouttxt.keys():
                                lfouttxt = dfouttxt[void]
                                self.IndexTitle = atitle
                                self.IndexText = ' '.join(lfouttxt)

                                dd = {'thisGenerator': self, 'aTableOID': robj.TabelaZrodlowa.OID, 'aItemOID': void, 'aChapterObj': robj}
                                try:
                                    ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataIndex')
                                except:
                                    if self.Log:
                                        self.Log.LogException('error in OnXMLDataIndex event')
                                    import traceback
                                    traceback.print_exc()

                    except Exception, e:
                        print 'Error in XML Chapter command'
                        if self.Log:
                            self.Log.LogException('Error in XML Chapter command')
                        import traceback
                        traceback.print_exc()
                        raise

            finally:
                dd = {'thisGenerator': self, 'aTableOID': atableoid, 'aChapterObj': robj}
                try:
                    ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataBeforeClose')
                except:
                    if self.Log:
                        self.Log.LogException('error in OnXMLDataBeforeClose event')
                    import traceback
                    traceback.print_exc()

                self.fout.TagClose()
                self.fout.close()

                dd = {'thisGenerator': self, 'aTableOID': atableoid, 'aChapterObj': robj}
                try:
                    ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataClose')
                except:
                    if self.Log:
                        self.Log.LogException('error in OnXMLDataClose event')
                    import traceback
                    traceback.print_exc()

                if self.RSSContext:
                    self.RSSContext.CloseFile()

    #   if achapterid<0:
        if aprocesssubchapters:
            sobj = robj.PodRozdzialy
            while sobj:
                self.ProcessChapter(sobj, aindent + 1, atableoid=atableoid, achapterid=achapterid, aignoregeneratedisabled=aignoregeneratedisabled)
                sobj.Next()

    def ProcessFiles(self, rs, robj, atitle, atableoid, wnoindex, aimgcount, asinglefile=0):
        if not self.VirtualGenerate:
            afilenamemodifier = ''
            if rs is not None and asinglefile:
                v = rs.Fields.Item('_OID').Value
                void = v.encode('cp1250')
                afilenamemodifier = '_' + void
            axmlfilepath = self.GetXMLFilePath(robj.OID, afilenamemodifier)
            sinfo = '   XMLFilePath: ' + str(robj.OID) + ' ' + axmlfilepath
            print sinfo
            if self.Log:
                self.Log.Log(sinfo)
            self.fout = XMLUtil.MXMLFile(axmlfilepath, anopl=1, aencoding='utf-8', astemp=1)

        brsscontext = self.RSSContext
        if not self.VirtualGenerate:
            if self.RSSContext:
                arssdir = '/' + self.RSSOutputDirName + '/'
                if self.RSSOutputByChapter:
                    arssdir = arssdir + str(robj.OID) + '/'
                self.RSSContext.OpenFile(robj, self.Path, atitle, adir=arssdir, abasenamemodifier=afilenamemodifier)
                if self.RSSContext.IsChapterDisabled:
                    brsscontext = None
        dfouttxt = {}

        self.ChapterParams = ICORUtil.ParseVars(robj.ChapterParams, {})

        dd = {'thisGenerator': self, 'aTableOID': atableoid, 'aChapterObj': robj, 'aNoIndex': wnoindex, 'aChapterParams': self.ChapterParams}
        try:
            self.CMSWWWMenuStruct.SingleFileOID = self.SingleFileOID
            ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataOpen')
        except:
            if self.Log:
                self.Log.LogException('error in OnXMLDataOpen event')
            import traceback
            traceback.print_exc()

        if not self.VirtualGenerate:
            self.fout.Header()
            self.fout.TagOpen('CHAPTERDATA', {'title': atitle})
        try:
            if rs is not None:
                try:
                    if rs.State != adoconst.adStateClosed:
                        rcnt = self.Recordset2XML(rs, dfouttxt, robj.TabelaZrodlowa.OID, aimgcount=aimgcount, arsscontext=brsscontext, asinglefile=asinglefile)
                        sinfo = '   Recordset2XML cnt: ' + str(robj.OID) + ' ' + axmlfilepath + ' = ' + str(rcnt)
                        print sinfo
                        if self.Log:
                            self.Log.Log(sinfo)

                    if not wnoindex:
                        #                  l=os.listdir(self.Path+'/index/')
                        #                  for finame in l:
                        #                     if finame.find('chapter_%d_'%robj.OID)==0:
                        #                        try:
                        #                           os.unlink(self.Path+'/index/'+finame)
                        #                        except:
                        #                           print 'Error in XML Chapter command - delete index file: '+finame
                        for void in dfouttxt.keys():
                            lfouttxt = dfouttxt[void]
                            self.IndexTitle = atitle
                            self.IndexText = ' '.join(lfouttxt)

                            dd = {'thisGenerator': self, 'aTableOID': robj.TabelaZrodlowa.OID, 'aItemOID': void, 'aChapterObj': robj}
                            try:
                                ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataIndex')
                            except:
                                if self.Log:
                                    self.Log.LogException('error in OnXMLDataIndex event')
                                import traceback
                                traceback.print_exc()

                except Exception, e:
                    print 'Error in XML Chapter command'
                    if self.Log:
                        self.Log.LogException('Error in XML Chapter command')
                    import traceback
                    traceback.print_exc()
                    raise

        finally:
            dd = {'thisGenerator': self, 'aTableOID': atableoid, 'aChapterObj': robj, 'aChapterParams': self.ChapterParams}
            try:
                ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataBeforeClose')
            except:
                if self.Log:
                    self.Log.LogException('error in OnXMLDataBeforeClose event')
                import traceback
                traceback.print_exc()

            if not self.VirtualGenerate:
                self.fout.TagClose()
                self.fout.close()

            dd = {'thisGenerator': self, 'aTableOID': atableoid, 'aChapterObj': robj, 'aChapterParams': self.ChapterParams}
            try:
                ret = self.SimpleCMS.ProcessEvents(adict=dd, aname='OnXMLDataClose')
            except:
                if self.Log:
                    self.Log.LogException('error in OnXMLDataClose event')
                import traceback
                traceback.print_exc()

            if self.RSSContext:
                self.RSSContext.CloseFile()

    def ProcessChapter(self, robj, aindent=0, atableoid=-1, achapterid=-1, aignoregeneratedisabled=0, aprocesssubchapters=1):
        wgen = 1
        tobj = robj.TabelaZrodlowa
        if atableoid >= 0 and tobj.OID != atableoid:
            wgen = 0
        #$$ czy na pewno atableoid moze byc rozne od tobj.OID???
        if robj.SGHref:
            wgen = 0
        if achapterid >= 0:
            if robj.OID == achapterid:
                wgen = 1
            else:
                wgen = 0
        if tobj.Nazwa in ['Rejestr zmian', 'Aktualności']:
            wgen = 1
        if not wgen and robj['IsAutoGenerate', mt_Integer]:
            wgen = 1
        if wgen and not aignoregeneratedisabled and robj['IsGenerateDisabled', mt_Integer]:
            wgen = 0


#      if wgen and robj['SGIsMenuDisabled',mt_Integer]:
#         wgen=0
        wnoindex = robj['SGIsIndexDisabled', mt_Integer]
        if self.NoIndexFiles:
            wnoindex = 1
        if wgen:
            atitle = robj.Naglowek
            if self.Log:
                self.Log.Log(atitle)
            #print '  '*aindent,atitle
            amodels = MCRMWWWMenuModel.WWWMenuChapterModels(robj)
            amodel = amodels.GetModel('struktura', 'sqlshape')
            asql = ''
            if amodel is None:
                sinfo = 'Chapter without SQLSHAPE model: ' + str(robj.OID) + ' ' + robj.Naglowek
                print sinfo
                if self.Log:
                    self.Log.Log(sinfo)
            else:
                asql = amodel.ModelText
                if self.OnGetChapterSQL:
                    asql = self.OnGetChapterSQL(asql)

            gobj = robj.Galeria
            if gobj:
                aimgcount = {'i': 0, 'asizex': gobj['RozmiarX'], 'asizey': gobj['RozmiarY'], 'amaxsizex': gobj['MaksymalnyRozmiarX'], 'amaxsizey': gobj['MaksymalnyRozmiarY'], 'amaxsizekb': gobj['MaksymalnyRozmiarKB'], 'przycinanie': gobj['Przycinanie', mt_Integer]}
            else:
                aimgcount = {'i': 0, 'asizex': 160, 'asizey': 120, 'amaxsizex': 0, 'amaxsizey': 0, 'amaxsizekb': -1, 'przycinanie': 0}

    #$$ zrobic probe otwarcia co kilka sekund
            rs = None
            if asql:
                try:
                    rs, status = self.Connection.Execute(asql)
                except Exception, e:
                    rs = None
                    print str(e)
                    print 'Error in SQL Chapter 1 command:', asql
                    if self.Log:
                        self.Log.LogException('Error in SQL Chapter 1 command: ' + asql)
                if rs is not None:
                    try:
                        self.SingleFileOID = ''
                        self.ProcessFiles(rs, robj, atitle, atableoid, wnoindex, aimgcount, asinglefile=0)
                        if not self.VirtualGenerate:
                            rs, status = self.Connection.Execute(asql)
                            while not rs.EOF and not rs.BOF:
                                v = rs.Fields.Item('_OID').Value
                                if v is None:
                                    print 'Chapter without single file column _OID: ' + str(robj.OID) + ' ' + robj.Naglowek
                                else:
                                    self.SingleFileOID = v.encode('cp1250')
                                    self.ProcessFiles(rs, robj, atitle, atableoid, wnoindex, aimgcount, asinglefile=1)
                                rs.MoveNext()
                    except Exception, e:
                        rs = None
                        print str(e)
                        print 'Error in SQL Chapter 2 command:', asql
                        if self.Log:
                            self.Log.LogException('Error in SQL Chapter 2 command: ' + asql)
            else:
                sinfo = 'Chapter without SQL: ' + str(robj.OID) + ' ' + robj.Naglowek
                print sinfo
                if self.Log:
                    self.Log.Log(sinfo)

    #   if achapterid<0:
        if aprocesssubchapters:
            sobj = robj.PodRozdzialy
            while sobj:
                self.ProcessChapter(sobj, aindent + 1, atableoid=atableoid, achapterid=achapterid, aignoregeneratedisabled=aignoregeneratedisabled)
                sobj.Next()


def Main(aclass, aoid, atableoid=-1, achapterid=-1, aignoregeneratedisabled=0, alog=None):
    #   print 'Main:',aclass.CID,aclass.NameOfClass,aoid,atableoid,achapterid
    if alog is None:
        afname = startutil.GetLogTempFileName('xmlgen')
        alog = startutil.MLog(afname, aconsole=0)
    alog.Log('Start generate: oid: %s, tableoid: %s, chapterid: %s' % (str(aoid), str(atableoid), str(achapterid)))
    pythoncom.CoInitialize()
    try:
        aobj = aclass[aoid]
        aDataGenerator = DataGenerator(aobj, alog)
        aDataGenerator.Process(atableoid, achapterid, aignoregeneratedisabled)
    finally:
        pythoncom.CoUninitialize()
    alog.Log('End generate')


def MainChapters(aobj, lchapterids, astatusupdate=0, aoperationoid='', aignoregeneratedisabled=0, aOnGetChapterSQL=None):
    lret = []
    atableoid = -1
    aignoregeneratedisabled = aignoregeneratedisabled
    alog = None
    #   print 'MainChapters:',aclass.CID,aclass.NameOfClass,aoid,atableoid,achapterid
    if not lchapterids:
        return lret
    if alog is None:
        afname = startutil.GetLogTempFileName('xmlgen')
        alog = startutil.MLog(afname, aconsole=0)
    alog.Log('Start generate: oid: %s, tableoid: %s, chapterids: %s' % (str(aobj.OID), str(atableoid), str(lchapterids)))
    pythoncom.CoInitialize()
    try:
        aDataGenerator = DataGenerator(aobj, alog)
        aDataGenerator.OnGetChapterSQL = aOnGetChapterSQL
        try:
            adt1 = time.clock()
            lret = aDataGenerator.Process(atableoid, lchapterids, aignoregeneratedisabled, anocloseconnection=1)
            adt2 = time.clock()
            if astatusupdate and lret:
                try:
                    aTable_ChapterState = aDataGenerator.BaseNameModifier + 'CHAPTERSTATE_' + str(aDataGenerator.InfoTablesSufix)
                    asql = '''UPDATE %s SET Status1='Z' WHERE Status1='G2' and ChapterID in (%s)''' % (aTable_ChapterState, ','.join(map(repr, lret)))
                    rs, status = aDataGenerator.Connection.Execute(asql)
                except Exception, e:
                    rs = None
                    print str(e)
                    print 'Error in SQL MainChapter command:', asql
                    alog.LogException('Error in SQL MainChapter command: ' + asql)
            if aoperationoid and lret:
                aICORDBEngine.SysBase.SetCMSChapterGenerateFinished(aoperationoid, adt2 - adt1)
        finally:
            try:
                aDataGenerator.Connection.Close()
            except:
                print 'Connection string: %s' % (aDataGenerator.ConnectionString)
                raise
    finally:
        pythoncom.CoUninitialize()
    alog.Log('End generate')
    return lret


def MainChaptersVirtual(aobj, lchapterids, aignoregeneratedisabled=1, aOnGetChapterSQL=None):
    lret = []
    atableoid = -1
    aignoregeneratedisabled = aignoregeneratedisabled
    alog = None
    #   print 'MainChapters:',aclass.CID,aclass.NameOfClass,aoid,atableoid,achapterid
    if not lchapterids:
        return lret
    if alog is None:
        afname = startutil.GetLogTempFileName('xmlgen')
        alog = startutil.MLog(afname, aconsole=0)
    alog.Log('Start virtual generate: oid: %s, tableoid: %s, chapterids: %s' % (str(aobj.OID), str(atableoid), str(lchapterids)))
    pythoncom.CoInitialize()
    try:
        aDataGenerator = DataGenerator(aobj, alog)
        aDataGenerator.OnGetChapterSQL = aOnGetChapterSQL
        try:
            lret = aDataGenerator.Process(atableoid, lchapterids, aignoregeneratedisabled, anocloseconnection=1, avirtual=1)
        finally:
            aDataGenerator.Connection.Close()
    finally:
        pythoncom.CoUninitialize()
    alog.Log('End virtual generate')
    return lret


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    #   print 'icormain: c:',CID,'f:',FieldName,'o:',OID,'v:',Value,'u:',UID
    #   MProfile.Start()
    afname = startutil.GetLogTempFileName('xmlgen')
    alog = startutil.MLog(afname, aconsole=0)
    alog.Log('Main - FieldName: ' + FieldName + ', OID: ' + str(OID) + ', Value: ' + Value + ', UID: ' + str(UID))
    saveout = startutil.MemorySysOutWrapper()
    print 'generate CID:', CID, 'FieldName:', FieldName, 'OID:', OID, 'Value:', Value, 'UID:', UID
    poid = -1
    sok = 'OK'
    smessage = 'Generowanie danych zakończono powodzeniem'
    try:
        try:
            #         SpeechUtil.Powiedz('linia 298')
            ret = FieldName.find('!')
            astate = ''
            if ret >= 0:
                FieldName, astate = FieldName[:ret], FieldName[ret + 1:]
            schapterid = '-1'
            aignoregeneratedisabled = 0
            lValue = []
            if Value[:1] in ['#', '$']:
                if Value[:1] == '$':
                    aignoregeneratedisabled = 0    #1 - UWAGA - nie mozna generowac rozdzialow wylaczonych - trzeba najpierw wlaczyc
                schapterid = Value[1:100].strip()
                if schapterid == '':
                    schapterid = '-1'
                if OID < 0:
                    achapterid = int(schapterid)
                    if achapterid < 0:
                        return
                    rclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                    OID = rclass[achapterid].TabelaZrodlowa.OID
                dclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
                dobj = dclass[OID]
                wobj = dobj.Projekt.WWWMenuStruct
                if not wobj:
                    return
                while wobj:
                    trefs = wobj.Class.TabeleZrodlowe.GetRefList(wobj.OID)
                    if trefs.RefExists(OID, wobj.Class.TabeleZrodlowe.ClassOfType.CID):
                        lValue.append(wobj.Nazwa)
                    wobj.Next()
            else:
                lValue.append(Value)
            achapterid = int(schapterid)
            acreatetables = 0
            if FieldName == '1':
                acreatetables = 1
            pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
            for Value in lValue:
                poid = pclass.Nazwa.Identifiers(Value)
                if poid >= 0:
                    #               pobj=pclass[poid]
                    Main(pclass, poid, OID, achapterid, aignoregeneratedisabled=aignoregeneratedisabled, alog=alog)
        except:
            sok = 'BAD'
            smessage = 'Wystąpił błąd podczas generowania danych'
            saveout.ICORStdOutPrint = 1
            saveout.LogException()
            import win32api
            try:
                for i in range(100):
                    win32api.Beep(500 - i * 2, 2)
            except:
                pass
    finally:
        if astate:
            bstate = ICORSync.ICORState(int(astate))
            bstate.Name = smessage
            bstate.Value = sok
        if poid >= 0:
            pclass.Status[poid] = saveout.read()
            pclass.DataOstatniegoGenerowania.SetValuesAsDateTime(poid, ICORUtil.tdatetime())
        else:
            saveout.Dump()
        saveout.Restore()
        import win32api
        try:
            win32api.Beep(5000, 100)
            win32api.Beep(3000, 150)
        except:
            pass
        alog.Log('Koniec generowania')


#   adir='d:\\icor\\log'
#   afname=ICORUtil.GetRandomFileName(adir,'mprofile','.py')
#   MProfile.Stop(adir+'\\'+afname)
    return
