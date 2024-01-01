# -*- coding: utf-8 -*-
import os
import time
import shutil

import appplatform.storageutil as storageutil

import icorlib.icorinterface as ICORInterface
import icordbmain.adoutil as ADOLibInit
import icorlib.icorsecurity as ICORSecurity


class ICORDBADOFiles(object):

    def __init__(self, adb):
        self.db = adb

    def getAttachments(self, adocontext, aoid='', anoclosecontext=0, anoutf8=0):
        ret = []
        try:
            awwwmenustruct = self.db.GetWWWMenuStructByContext(adocontext)
            if awwwmenustruct is None:
                aproject = self.db.GetProjectByContext(adocontext)
                aExternalWWW = ''
                if aproject is None:
                    aProjectPath = ''
                else:
                    aProjectPath = aproject.Project
            else:
                aProjectPath = awwwmenustruct.Project.Project
                aExternalWWW = awwwmenustruct.ExternalWWWAddress
            if not aoid:
                rname, rvalue = 'RefOID', adocontext.ioid
            else:
                rname, rvalue = '_OID', aoid
            asql = '''
            SELECT 
               _OID, Name, Path, FileSize, LastModification, Description, 
               InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, 
               RefTable, RefOID, _datetime, _UID, _UserName, 
               Category, Kind, ItemKey, ItemRel, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, StatusKonwersji, ItemStatus, ItemPosition
            from %sFILEUPLOADS_0 
            WHERE 
            %s='%s'
            and Status<>'D' and Status<>'U'
            ORDER BY ItemPosition,Name
         ''' % (adocontext.basenamemodifier, rname, rvalue)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    d2 = {}
                    mf = rs.Fields.Count
                    if not anoutf8:
                        for i in range(mf):
                            d2[rs.Fields.Item(i).Name] = storageutil.CP1250_To_UTF8_Unicode(ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0))
                    else:
                        for i in range(mf):
                            d2[rs.Fields.Item(i).Name] = ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0)
                    rs.MoveNext()
                    d2['Name'] = os.path.split(d2.get('Name', ''))[1]
                    fn, fe = os.path.splitext(d2['Name'])
                    d2['FileName'] = fn
                    d2['FileExt'] = fe
                    d2['ProjectPath'] = aProjectPath
                    d2['ExternalWWW'] = aExternalWWW
                    if d2.get('Status', '') == '':
                        d2['Status'] = 'A'
                    if d2.get('StatusKonwersji', '') == '':
                        d2['StatusKonwersji'] = 'G'
                    ret.append(d2)
                rs = adocontext.CloseRS(rs)
        finally:
            if not anoclosecontext:
                adocontext.Close()
        return ret

    def getHTTPAttachments(self, adocontext, aoid='', anoclosecontext=0, anoutf8=0):
        ret = []
        try:
            awwwmenustruct = self.db.GetWWWMenuStructByContext(adocontext)
            if awwwmenustruct is None:
                aproject = self.db.GetProjectByContext(adocontext)
                aExternalWWW = ''
                if aproject is None:
                    aProjectPath = ''
                else:
                    aProjectPath = aproject.Project
            else:
                aProjectPath = awwwmenustruct.Project.Project
                aExternalWWW = awwwmenustruct.ExternalWWWAddress
            if not aoid:
                rname, rvalue = 'RefOID', adocontext.ioid
            else:
                rname, rvalue = '_OID', aoid
            asql = '''
            SELECT 
               _OID, Name, Path, FileSize, LastModification, Description, 
               InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, 
               RefTable, RefOID, _datetime, _UID, _UserName, 
               Category, Kind, ItemKey, ItemRel, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, StatusKonwersji, ItemStatus, ItemPosition
            from %sHTTPFILEUPLOADS_0 
            WHERE 
            %s='%s'
            and Status<>'D' and Status<>'U'
            ORDER BY ItemPosition,Name
         ''' % (adocontext.basenamemodifier, rname, rvalue)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    d2 = {}
                    mf = rs.Fields.Count
                    if not anoutf8:
                        for i in range(mf):
                            d2[rs.Fields.Item(i).Name] = storageutil.CP1250_To_UTF8_Unicode(ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0))
                    else:
                        for i in range(mf):
                            d2[rs.Fields.Item(i).Name] = ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0)
                    rs.MoveNext()
                    d2['Name'] = os.path.split(d2.get('Name', ''))[1]
                    fn, fe = os.path.splitext(d2['Name'])
                    d2['FileName'] = fn
                    d2['FileExt'] = fe
                    d2['ProjectPath'] = aProjectPath
                    d2['ExternalWWW'] = aExternalWWW
                    if d2.get('Status', '') == '':
                        d2['Status'] = 'A'
                    if d2.get('StatusKonwersji', '') == '':
                        d2['StatusKonwersji'] = 'G'
                    ret.append(d2)
                rs = adocontext.CloseRS(rs)
        finally:
            if not anoclosecontext:
                adocontext.Close()
        return ret

    def getMultimedia(self, adocontext, aoid='', anoclosecontext=0, anoutf8=0):
        ret = []
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            atablename = acapabilities.aTable_Multimedia
            if not atablename:
                return ret
            aProjectPath = acapabilities.WWWMenuStruct.Project.Project
            aExternalWWW = acapabilities.WWWMenuStruct.ExternalWWWAddress

            if not aoid:
                rname, rvalue = 'RefOID', adocontext.ioid
            else:
                rname, rvalue = '_OID', aoid
            # column diff from fileuploads: Path, ItemStatus
            asql = '''
            SELECT 
               _OID, Name, FileName, FileSize, FileTypePath, LastModification, Description, 
               InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, 
               RefTable, RefOID, _datetime, _UID, _UserName, 
               Category, Kind, ItemKey, ItemRel, ItemGroup, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, ItemStatus, ItemPosition
            from %s 
            WHERE 
            %s='%s'
            and Status<>'U1' and Status<>'U2'
            ORDER BY ItemPosition,Name
         ''' % (atablename, rname, rvalue)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    d2 = {}
                    mf = rs.Fields.Count
                    if not anoutf8:
                        for i in range(mf):
                            d2[rs.Fields.Item(i).Name] = storageutil.CP1250_To_UTF8_Unicode(ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0))
                    else:
                        for i in range(mf):
                            d2[rs.Fields.Item(i).Name] = ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0)
                    rs.MoveNext()
                    d2['Name'] = os.path.split(d2.get('Name', ''))[1]
                    fn, fe = os.path.splitext(d2['FileName'])
                    d2['FileName'] = fn
                    d2['FileExt'] = fe
                    d2['ProjectPath'] = aProjectPath
                    d2['ExternalWWW'] = aExternalWWW
                    #if d2.get('Status','')=='':
                    #d2['Status']='A'
                    ret.append(d2)
                rs = adocontext.CloseRS(rs)
        finally:
            if not anoclosecontext:
                adocontext.Close()
        return ret

    def addAttachment(self, adocontext, filename, data, anoclosecontext=0, anoutf8=0):
        """
         Status:
            '' - stare pliki, ok (=='A')
            'U' - aktualnie wgrywane/blad wgrywania
            'N' - gotowe do publikacji
            'B' - zablokowane
            'A' - zaktualizowane
            'D' - usuniete
      """
        ret = ''
        try:
            foid = ''
            asql = '''
            SELECT 
               _OID, Name, Path, FileSize, LastModification, Description, 
               InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, 
               RefTable, RefOID, _datetime, _UID, _UserName, 
               Category, Kind, ItemKey, ItemRel, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, StatusKonwersji, ItemStatus, ItemPosition
            from %sFILEUPLOADS_0 
            WHERE 
            _OID='-1'
         ''' % (adocontext.basenamemodifier, )
            rs = adocontext.GetRS(asql)
            if rs.EOF or rs.BOF:
                rs.AddNew()
                filename = storageutil.URI2UTF8(filename)
                rs.Fields.Item('Name').Value = storageutil.UTF8_slugify(os.path.split(filename)[1])
                rs.Fields.Item('Path').Value = storageutil.UTF8_To_CP1250(filename)
                rs.Fields.Item("RefTable").Value = adocontext.basenamemodifier + 'BZR_' + str(adocontext.toid)
                rs.Fields.Item("RefOID").Value = adocontext.ioid
                rs.Fields.Item("_UID").Value = adocontext.uid
                auser = ICORSecurity.ICORSecurityUser(adocontext.uid)
                rs.Fields.Item("_UserName").Value = auser.UserName
                rs.Fields.Item("Status").Value = 'U'
                rs.Update()
                time.sleep(0.5)
                foid = ADOLibInit.GetRSValueAsStr(rs, '_OID')
            rs = adocontext.CloseRS(rs)
            if foid:
                pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
                pobj = pclass[adocontext.poid]
                adatapath = ICORInterface.FilePathAsSystemPath(pobj.WWWDataPath, aslash='/')
                if adatapath[-1:] != '/':
                    adatapath = adatapath + '/'
                adatapath = adatapath + 'sqlfiles/'
                astatus = 'B'
                try:
                    size = self.saveFile(data.file, adatapath + foid + '.dat')
                    astatus = 'N'
                except:
                    import traceback
                    traceback.print_exc()
                adocontext.Execute("UPDATE %sFILEUPLOADS_0 SET FileSize=%d,Status='%s',StatusKonwersji='' WHERE _OID='%s'" % (adocontext.basenamemodifier, size, astatus, foid))
                if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                    rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                    rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
                ret = 'OK'
        finally:
            if not anoclosecontext:
                adocontext.Close()
        return ret

    def addHTTPAttachment(self, adocontext, filename, data, anoclosecontext=0, anoutf8=0):
        """
         Status:
            '' - stare pliki, ok (=='A')
            'U' - aktualnie wgrywane/blad wgrywania
            'N' - gotowe do publikacji
            'B' - zablokowane
            'A' - zaktualizowane
            'D' - usuniete
      """
        ret = ''
        try:
            foid = ''
            asql = '''
            SELECT 
               _OID, Name, Path, FileSize, LastModification, Description, 
               InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, 
               RefTable, RefOID, _datetime, _UID, _UserName, 
               Category, Kind, ItemKey, ItemRel, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, StatusKonwersji, ItemStatus, ItemPosition,
               ParentPath, PathLevel
            from %sHTTPFILEUPLOADS_0 
            WHERE 
            _OID='-1'
         ''' % (adocontext.basenamemodifier, )
            pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
            pobj = pclass[adocontext.poid]
            adatapath = ICORInterface.FilePathAsSystemPath(pobj.WWWDataPath, aslash='/')
            if adatapath[-1:] != '/':
                adatapath = adatapath + '/'
            adatapath = adatapath + 'httpfiles/'    #$$HTTPAttachments
            rs = adocontext.GetRS(asql)
            if rs.EOF or rs.BOF:
                rs.AddNew()
                filename = storageutil.URI2UTF8(filename)
                sfilename = storageutil.UTF8_slugify(os.path.split(filename)[1])
                rs.Fields.Item('Name').Value = sfilename
                rs.Fields.Item('Path').Value = storageutil.UTF8_To_CP1250(filename)
                rs.Fields.Item("RefTable").Value = adocontext.basenamemodifier + 'BZR_' + str(adocontext.toid)
                rs.Fields.Item("RefOID").Value = adocontext.ioid
                rs.Fields.Item("_UID").Value = adocontext.uid
                auser = ICORSecurity.ICORSecurityUser(adocontext.uid)
                rs.Fields.Item("_UserName").Value = auser.UserName
                rs.Fields.Item("ParentPath").Value = '/'
                rs.Fields.Item("Status").Value = 'U'
                rs.Update()
                time.sleep(0.5)
                foid = ADOLibInit.GetRSValueAsStr(rs, '_OID')
            rs = adocontext.CloseRS(rs)
            if foid:
                astatus = 'B'
                try:
                    size = self.saveFile(data.file, adatapath + sfilename)
                    astatus = 'N'
                except:
                    import traceback
                    traceback.print_exc()
                adocontext.Execute("UPDATE %sHTTPFILEUPLOADS_0 SET FileSize=%d,Status='%s',StatusKonwersji='' WHERE _OID='%s'" % (adocontext.basenamemodifier, size, astatus, foid))
                if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                    rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                    rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
                ret = 'OK'
        finally:
            if not anoclosecontext:
                adocontext.Close()
        return ret

    def saveFile(self, fin, afilepath):
        fout = open(afilepath, 'wb')
        size = 0
        while True:
            v = fin.read(65536)
            if not v:
                break
            size += len(v)
            fout.write(v)
        fout.close()
        return size

    def addMultimedia(self, adocontext, filename, data, anoclosecontext=0, anoutf8=0):
        """
         Status:
            '' - nowe pliki
            'P1' - w trakcie konwersji
            'Z1' - gotowe do publikacji
            'B1' - bledy konwersji
            'U1' - usuniete
            'U2' - w trakcie upload
      """
        ret = ''
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            atablename = acapabilities.aTable_Multimedia
            if not atablename:
                return ret

            limages = acapabilities.Multimedia_aAllowedImageTypes.split('|')
            laudio = acapabilities.Multimedia_aAllowedAudioTypes.split('|')
            lvideo = acapabilities.Multimedia_aAllowedVideoTypes.split('|')
            lmedias = acapabilities.Multimedia_aAllowedMediaTypes.split('|')
            lflash = ['swf', ]
            foid = ''
            asql = '''
            SELECT 
               _OID, Name, FileSize, LastModification, Description, 
               InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, 
               RefTable, RefOID, _datetime, _UID, _UserName, 
               Category, Kind, ItemKey, ItemRel, ItemGroup, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, ItemStatus, ItemPosition,
               Filename, FileTypePath, FileExtension
            from %s
            WHERE 
            _OID='-1'
         ''' % (atablename, )
            rs = adocontext.GetRS(asql)
            if rs.EOF or rs.BOF:
                rs.AddNew()
                filename = storageutil.URI2UTF8(filename)
                safefilename = storageutil.UTF8_slugify(os.path.split(filename)[1])
                rs.Fields.Item('Name').Value = safefilename
                # not in multimedia - exists in fileuploads
                #rs.Fields.Item('Path').Value=storageutil.UTF8_To_CP1250(filename)
                rs.Fields.Item("RefTable").Value = adocontext.basenamemodifier + 'BZR_' + str(adocontext.toid)
                rs.Fields.Item("RefOID").Value = adocontext.ioid
                rs.Fields.Item("_UID").Value = adocontext.uid
                auser = ICORSecurity.ICORSecurityUser(adocontext.uid)
                rs.Fields.Item("_UserName").Value = auser.UserName
                rs.Fields.Item("Status").Value = 'U2'
                # multimedia table:
                rs.Fields.Item("Filename").Value = safefilename
                sfname, sfext = os.path.splitext(safefilename.lower())
                sfext = sfext[1:]
                sServerModDir = 'file'
                if sfext in limages:
                    sServerModDir = 'image'
                elif sfext in lvideo:
                    sServerModDir = 'video'
                elif sfext in lmedias:
                    sServerModDir = 'media'
                elif sfext in laudio:
                    sServerModDir = 'audio'
                elif sfext in lflash:
                    sServerModDir = 'flash'
                rs.Fields.Item("FileTypePath").Value = sServerModDir
                rs.Fields.Item("FileExtension").Value = sfext
                rs.Update()
                time.sleep(0.5)
                foid = ADOLibInit.GetRSValueAsStr(rs, '_OID')
            rs = adocontext.CloseRS(rs)
            if foid:
                adatapath = '%sHTTPFiles/%s/_multimedia/%s' % (acapabilities.WWWMenuStruct.Project.WWWDataPath, sServerModDir, foid)
                if not os.path.exists(adatapath):
                    os.makedirs(adatapath)
                size = self.saveFile(data.file, adatapath + '/' + safefilename)
                adocontext.Execute("UPDATE %s SET FileSize=%d,Status='' WHERE _OID='%s'" % (atablename, size, foid))
                ret = 'OK'
        finally:
            if not anoclosecontext:
                adocontext.Close()
        return ret

    def getAttachmentsAutocomplete(self, adocontext, afield, avalue, asecondlabel='', aicon='', astamp=''):
        ret = []
        avalue = self.db.GetSafeSQLWhere(avalue[:14])
        try:
            sand = ''
            if len(avalue) > 1:
                sand = "%s like '%s%%' and " % (afield, avalue)
            asql = '''
            SELECT distinct top 100 %s as fvalue FROM %sFILEUPLOADS_0
            WHERE %s
            Status<>'D'
            ORDER BY %s
         ''' % (afield, adocontext.basenamemodifier, sand, afield)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    sv = storageutil.CP1250_To_UTF8_Unicode(ADOLibInit.GetRSValueAsStr(rs, 'fvalue', astype=0))
                    d2 = {'value': sv, 'label': sv, }
                    if asecondlabel:
                        d2['secondLabel'] = asecondlabel
                    if aicon:
                        d2['icon'] = aicon
                    if astamp:
                        d2['stamp'] = astamp
                    rs.MoveNext()
                    ret.append(d2)
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getHTTPAttachmentsAutocomplete(self, adocontext, afield, avalue, asecondlabel='', aicon='', astamp=''):
        ret = []
        avalue = self.db.GetSafeSQLWhere(avalue[:14])
        try:
            sand = ''
            if len(avalue) > 1:
                sand = "%s like '%s%%' and " % (afield, avalue)
            asql = '''
            SELECT distinct top 100 %s as fvalue FROM %sHTTPFILEUPLOADS_0
            WHERE %s
            Status<>'D'
            ORDER BY %s
         ''' % (afield, adocontext.basenamemodifier, sand, afield)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    sv = storageutil.CP1250_To_UTF8_Unicode(ADOLibInit.GetRSValueAsStr(rs, 'fvalue', astype=0))
                    d2 = {'value': sv, 'label': sv, }
                    if asecondlabel:
                        d2['secondLabel'] = asecondlabel
                    if aicon:
                        d2['icon'] = aicon
                    if astamp:
                        d2['stamp'] = astamp
                    rs.MoveNext()
                    ret.append(d2)
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getMultimediaAutocomplete(self, adocontext, afield, avalue, asecondlabel='', aicon='', astamp=''):
        ret = []
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            atablename = acapabilities.aTable_Multimedia
            if not atablename:
                return ret

            avalue = self.db.GetSafeSQLWhere(avalue[:14])
            sand = ''
            if len(avalue) > 1:
                sand = "%s like '%s%%' and " % (afield, avalue)
            asql = '''
            SELECT distinct top 100 %s as fvalue FROM %s
            WHERE %s
            Status<>'U1'
            ORDER BY %s
         ''' % (afield, atablename, sand, afield)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    sv = storageutil.CP1250_To_UTF8_Unicode(ADOLibInit.GetRSValueAsStr(rs, 'fvalue', astype=0))
                    d2 = {'value': sv, 'label': sv, }
                    if asecondlabel:
                        d2['secondLabel'] = asecondlabel
                    if aicon:
                        d2['icon'] = aicon
                    if astamp:
                        d2['stamp'] = astamp
                    rs.MoveNext()
                    ret.append(d2)
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getAttachmentsRemove(self, adocontext, foid, anoclosecontext=0, anoutf8=0):
        ret = 'BAD'
        try:
            asql = '''
            SELECT *
            from %sFILEUPLOADS_0 
            WHERE _OID='%s'
         ''' % (adocontext.basenamemodifier, foid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    adocontext.StoreField(rs, 'Status', 'D')
                    adocontext.UpdateRS(rs)
                    ret = 'OK'
                    rs = adocontext.CloseRS(rs)
                    self.db.dbtables.setRecordVersion(adocontext, 'FILEUPLOADS_0', 'FILEUPLOADS_V_0', foid, 'DELETE')
                    pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
                    pobj = pclass[adocontext.poid]
                    adatapath = ICORInterface.FilePathAsSystemPath(pobj.WWWDataPath, aslash='/')
                    if adatapath[-1:] != '/':
                        adatapath = adatapath + '/'
                    adatapathin = adatapath + 'sqlfiles/'
                    adatapathout = adatapath + 'sqlfilesdeleted/'
                    try:
                        os.rename(adatapathin + foid + '.dat', adatapathout + foid + '.dat')
                    except:
                        pass
                        #$$ - pliki moga nie byc kasowane - niedobrze - ret='BAD2'
                    if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                        rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                        rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return ret

    def getHTTPAttachmentsRemove(self, adocontext, foid, anoclosecontext=0, anoutf8=0):
        ret = 'BAD'
        try:
            asql = '''
            SELECT *
            from %sHTTPFILEUPLOADS_0 
            WHERE _OID='%s'
         ''' % (adocontext.basenamemodifier, foid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    adocontext.StoreField(rs, 'Status', 'D')
                    adocontext.UpdateRS(rs)
                    ret = 'OK'
                    rs = adocontext.CloseRS(rs)
                    self.db.dbtables.setRecordVersion(adocontext, 'HTTPFILEUPLOADS_0', 'HTTPFILEUPLOADS_V_0', foid, 'DELETE')
                    pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
                    pobj = pclass[adocontext.poid]
                    adatapath = ICORInterface.FilePathAsSystemPath(pobj.WWWDataPath, aslash='/')
                    if adatapath[-1:] != '/':
                        adatapath = adatapath + '/'
                    adatapathin = adatapath + 'httpfiles/'
                    sfilename = ADOLibInit.GetRSValueAsStr(rs, 'Name')
                    try:
                        os.unlink(adatapathin + sfilename)
                    except:
                        pass
                        #$$ - pliki moga nie byc kasowane - niedobrze - ret='BAD2'
                    if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                        rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                        rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return ret

    def getMultimediaRemove(self, adocontext, foid, anoclosecontext=0, anoutf8=0):
        ret = 'BAD'
        acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
        if acapabilities is None:
            return ret
        atablename = acapabilities.aTable_Multimedia
        if not atablename:
            return ret
        atablenameversion = acapabilities.aTable_MultimediaVersion

        try:
            asql = '''
            SELECT *
            from %s
            WHERE _OID='%s'
         ''' % (atablename, foid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    aFileTypePath = ADOLibInit.GetRSValueAsStr(rs, 'FileTypePath', astype=0)
                    adocontext.StoreField(rs, 'Status', 'U1')
                    adocontext.UpdateRS(rs)
                    ret = 'OK'
                    rs = adocontext.CloseRS(rs)
                    self.db.dbtables.setRecordVersion(adocontext, acapabilities.aTableOID_Multimedia, aoid=foid, aaction='DELETE')
                    srcpath = acapabilities.WWWMenuStruct.Project.WWWDataPath + 'HTTPFiles/' + aFileTypePath + '/_multimedia/' + foid
                    dstpath = acapabilities.WWWMenuStruct.Project.WWWDataPath + 'HTTPFilesDeleted/' + aFileTypePath + '/_multimedia'
                    if not os.path.exists(dstpath):
                        os.makedirs(dstpath)
                    try:
                        shutil.move(srcpath, dstpath)
                    except:
                        pass
                        #$$ zostaja pliki po usunieciu - niedobrze - ret='BAD2'
                        # import traceback
                        # traceback.print_exc()
        finally:
            adocontext.Close()
        return ret

    def setAttachmentUpdate(self, adocontext, data):
        DD={
           'Category': u'gggyy',
           'ItemKey': u'',
           'Description': u'literki',
           'InformacjaOsobaOdpowiedzialna': u'Admin',
           'InformacjaPodmiotUdostepniajacy': u'podmiot',
           'Kind': u'',
           'ItemRel': u'',
           'InformacjaOpisCzynnosci': u'',
           'InformacjaDataWytworzenia': u'2009-05-12',
           'ItemType': u'',
           'ItemTitle': u'',
           'ItemStatus': u'',

           'FileName': u'a\u0105\u0107\u0119\u0142\u0144\xf3\u015b\u017a\u017c',

           '_datetime': u'2009-05-18 13:45:48',
           '_UserName': u'PTest1Admin',
           '_UID': u'18500',
           'Status': u'A',

           'Name': u'a\u0105\u0107\u0119\u0142\u0144\xf3\u015b\u017a\u017c.txt',
           'FileExt': u'.txt',
           'ItemHeight': u'',
           'mode': u'update',
           'ItemWidth': u'',
           'RefTable': u'TMP_BZR_35000',
           'Path': u'D:\\',
           'RefOID': u'46B90CBA748E4F308BD2F0378EEE99E4',
           'LastModification': u'2008-05-15 13:56:23',
           'ItemPosition': u'0',
           'FileSize': u'48',
           '_OID': u'D700DB2890D440EC8D53C3315F920B49'
        } # yapf: disable
        lfields = ['Name', 'Category', 'ItemKey', 'Description', 'InformacjaOsobaOdpowiedzialna', 'InformacjaPodmiotUdostepniajacy', 'Kind', 'ItemRel', 'InformacjaOpisCzynnosci', 'InformacjaDataWytworzenia', 'ItemType', 'ItemTitle', 'ItemStatus', ]
        olddata = self.db.dbtables.getTableRecord(adocontext, 'FILEUPLOADS_0', lfields + ['Status', 'StatusKonwersji'], data.get('_OID', '-1'))
        ret = []
        if not olddata:
            return 'Nieprawidlowy OID'
        afilename, aext = os.path.splitext(olddata['Name'])
        sx = data.get('FileName', '')
        #sx=sx.encode('latin-1')
        #sx=sx.decode('utf-8')
        sx = storageutil.CP1250_To_UTF8_Unicode(sx)
        sx = storageutil.UTF8_slugify(sx)
        sx = sx + aext
        data['Name'] = sx
        if not self.db.dbtables.checkRecordModified(lfields, data, olddata):
            return 'Brak zmian'
        if not olddata.get('Status', ''):
            self.db.dbtables.setRecordVersion(adocontext, 'FILEUPLOADS_0', 'FILEUPLOADS_V_0', data.get('_OID', '-1'), 'UPDATE')
        try:
            asql = '''
            SELECT *
            from %sFILEUPLOADS_0 
            WHERE _OID='%s'
         ''' % (adocontext.basenamemodifier, data.get('_OID', '-1'))
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    for afieldname in lfields:
                        adocontext.StoreField(rs, afieldname, data.get(afieldname, ''))
                    adocontext.StoreField(rs, 'Status', 'A')
                    adocontext.StoreField(rs, 'StatusKonwersji', '')
                    adocontext.UpdateRS(rs)
                rs = adocontext.CloseRS(rs)
            self.db.dbtables.setRecordVersion(adocontext, 'FILEUPLOADS_0', 'FILEUPLOADS_V_0', data.get('_OID', '-1'), 'UPDATE')
            if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return 'OK'

    def setHTTPAttachmentUpdate(self, adocontext, data):
        DD={
           'Category': u'gggyy',
           'ItemKey': u'',
           'Description': u'literki',
           'InformacjaOsobaOdpowiedzialna': u'Admin',
           'InformacjaPodmiotUdostepniajacy': u'podmiot',
           'Kind': u'',
           'ItemRel': u'',
           'InformacjaOpisCzynnosci': u'',
           'InformacjaDataWytworzenia': u'2009-05-12',
           'ItemType': u'',
           'ItemTitle': u'',
           'ItemStatus': u'',

           'FileName': u'a\u0105\u0107\u0119\u0142\u0144\xf3\u015b\u017a\u017c',

           '_datetime': u'2009-05-18 13:45:48',
           '_UserName': u'PTest1Admin',
           '_UID': u'18500',
           'Status': u'A',

           'Name': u'a\u0105\u0107\u0119\u0142\u0144\xf3\u015b\u017a\u017c.txt',
           'FileExt': u'.txt',
           'ItemHeight': u'',
           'mode': u'update',
           'ItemWidth': u'',
           'RefTable': u'TMP_BZR_35000',
           'Path': u'D:\\',
           'RefOID': u'46B90CBA748E4F308BD2F0378EEE99E4',
           'LastModification': u'2008-05-15 13:56:23',
           'ItemPosition': u'0',
           'FileSize': u'48',
           '_OID': u'D700DB2890D440EC8D53C3315F920B49'
        } # yapf: disable
        lfields = ['Name', 'Category', 'ItemKey', 'Description', 'InformacjaOsobaOdpowiedzialna', 'InformacjaPodmiotUdostepniajacy', 'Kind', 'ItemRel', 'InformacjaOpisCzynnosci', 'InformacjaDataWytworzenia', 'ItemType', 'ItemTitle', 'ItemStatus', ]
        olddata = self.db.dbtables.getTableRecord(adocontext, 'HTTPFILEUPLOADS_0', lfields + ['Status', 'StatusKonwersji'], data.get('_OID', '-1'))
        ret = []
        if not olddata:
            return 'Nieprawidlowy OID'
        afilename, aext = os.path.splitext(olddata['Name'])
        #$$ HTTPAttachment - zmienic nazwe pliku
        sx = data.get('FileName', '')
        #sx=sx.encode('latin-1')
        #sx=sx.decode('utf-8')
        sx = storageutil.CP1250_To_UTF8_Unicode(sx)
        sx = storageutil.UTF8_slugify(sx)
        sx = sx + aext
        data['Name'] = sx
        if not self.db.dbtables.checkRecordModified(lfields, data, olddata):
            return 'Brak zmian'
        if not olddata.get('Status', ''):
            self.db.dbtables.setRecordVersion(adocontext, 'HTTPFILEUPLOADS_0', 'HTTPFILEUPLOADS_V_0', data.get('_OID', '-1'), 'UPDATE')
        try:
            asql = '''
            SELECT *
            from %sHTTPFILEUPLOADS_0 
            WHERE _OID='%s'
         ''' % (adocontext.basenamemodifier, data.get('_OID', '-1'))
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    for afieldname in lfields:
                        adocontext.StoreField(rs, afieldname, data.get(afieldname, ''))
                    adocontext.StoreField(rs, 'Status', 'A')
                    adocontext.StoreField(rs, 'StatusKonwersji', '')
                    adocontext.UpdateRS(rs)
                rs = adocontext.CloseRS(rs)
            self.db.dbtables.setRecordVersion(adocontext, 'HTTPFILEUPLOADS_0', 'HTTPFILEUPLOADS_V_0', data.get('_OID', '-1'), 'UPDATE')
            if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return 'OK'

    def setMultimediaUpdate(self, adocontext, data):
        ret = []
        acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
        if acapabilities is None:
            return ret
        atablename = acapabilities.aTable_Multimedia
        if not atablename:
            return ret
        atablenameversion = acapabilities.aTable_MultimediaVersion

        lfields = ['Name', 'Category', 'ItemKey', 'Description', 'InformacjaOsobaOdpowiedzialna', 'InformacjaPodmiotUdostepniajacy', 'Kind', 'ItemRel', 'ItemGroup', 'InformacjaOpisCzynnosci', 'InformacjaDataWytworzenia', 'ItemType', 'ItemTitle', 'ItemStatus', ]
        olddata = self.db.dbtables.getTableRecord(adocontext, atablename, lfields + ['Status', ], data.get('_OID', '-1'), anomodifier=1)
        if not olddata:
            return 'Nieprawidlowy OID'
        afilename, aext = os.path.splitext(olddata['Name'])
        sx = data.get('FileName', '')
        #sx=sx.encode('latin-1')
        #sx=sx.decode('utf-8')
        sx = storageutil.CP1250_To_UTF8_Unicode(sx)
        sx = storageutil.UTF8_slugify(sx)
        sx = sx + aext
        data['Name'] = sx
        lmodifiedcolumns = self.db.dbtables.checkRecordModified(lfields, data, olddata, aslist=1)
        if not lmodifiedcolumns:
            return 'Brak zmian'
        try:
            asql = '''
            SELECT *
            from %s
            WHERE _OID='%s'
         ''' % (atablename, data.get('_OID', '-1'))
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    for afieldname in lfields:
                        adocontext.StoreField(rs, afieldname, data.get(afieldname, ''))
                    if 'ItemKey' in lmodifiedcolumns:
                        adocontext.StoreField(rs, 'Status', '')
                    adocontext.UpdateRS(rs)
                rs = adocontext.CloseRS(rs)
            self.db.dbtables.setRecordVersion(adocontext, acapabilities.aTableOID_Multimedia, aoid=data.get('_OID', '-1'), aaction='UPDATE')
            if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return 'OK'

    def setAttachmentPositions(self, adocontext, lpos):
        ret = 'BAD'
        try:
            i = 10
            for foid in lpos:
                asql = '''
               UPDATE
               %sFILEUPLOADS_0 
               SET ItemPosition=%d
               WHERE _OID='%s'
            ''' % (adocontext.basenamemodifier, i, foid)
                adocontext.Execute(asql)
                self.db.dbtables.setRecordVersion(adocontext, 'FILEUPLOADS_0', 'FILEUPLOADS_V_0', foid, 'UPDATE')
                i = i + 10
            if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return 'OK'

    def setHTTPAttachmentPositions(self, adocontext, lpos):
        ret = 'BAD'
        try:
            i = 10
            for foid in lpos:
                asql = '''
               UPDATE
               %sHTTPFILEUPLOADS_0 
               SET ItemPosition=%d
               WHERE _OID='%s'
            ''' % (adocontext.basenamemodifier, i, foid)
                adocontext.Execute(asql)
                self.db.dbtables.setRecordVersion(adocontext, 'HTTPFILEUPLOADS_0', 'HTTPFILEUPLOADS_V_0', foid, 'UPDATE')
                i = i + 10
            if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return 'OK'

    def setMultimediaPositions(self, adocontext, lpos):
        ret = 'BAD'
        acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
        if acapabilities is None:
            return ret
        atablename = acapabilities.aTable_Multimedia
        if not atablename:
            return ret
        atablenameversion = acapabilities.aTable_MultimediaVersion
        try:
            i = 10
            for foid in lpos:
                asql = '''
               UPDATE
               %s
               SET ItemPosition=%d
               WHERE _OID='%s'
            ''' % (atablename, i, foid)
                adocontext.Execute(asql)
                self.db.dbtables.setRecordVersion(adocontext, acapabilities.aTableOID_Multimedia, aoid=foid, aaction='UPDATE')
                i = i + 10
            if (adocontext.cmsid >= 0) and (adocontext.coid >= 0):
                rclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                rclass.DoSetChapterState(str(adocontext.cmsid), adocontext.coid, '', adocontext.uid)
        finally:
            adocontext.Close()
        return 'OK'

    def getChapterFiles(self, adocontext, coid, UID):
        coid = storageutil.getStrAsInt(coid)
        if coid < 0:
            return '{"status":2,"info":"błędny parametr"}'
        d={
           'status':0,
           'info':'',
           'user':{},
        } # yapf: disable
        lf = []
        try:
            asql = '''
            select t1._OID,t1.Tytul,
            tf._OID as foid,tf.Name,tf.Path,tf.FileSize,tf.LastModification,tf.Description,
            tf.InformacjaPodmiotUdostepniajacy,tf.InformacjaOsobaOdpowiedzialna,tf.InformacjaDataWytworzenia,tf.InformacjaOpisCzynnosci,
            tf._datetime
            from %sBZR_6008 t1 
            left join %sFILEUPLOADS_0 tf on t1._OID=tf.RefOID
            where
            t1._ChapterID=%d
            order by tf.Name
         ''' % (adocontext.basenamemodifier, adocontext.basenamemodifier, coid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    d2 = {}
                    mf = rs.Fields.Count
                    for i in range(mf):
                        d2[rs.Fields.Item(i).Name] = storageutil.CP1250_To_UTF8_Unicode(ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0))
                    rs.MoveNext()
                    lf.append(d2)
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        d['files'] = lf
        return json.dumps(d)
