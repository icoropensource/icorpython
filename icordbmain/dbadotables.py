# -*- coding: utf-8 -*-
import os
import time

import appplatform.storageutil as storageutil

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.icorsecurity as ICORSecurity
import icordbmain.adoutil as ADOLibInit


class ICORTableHelper(object):

    def __init__(self, toid):
        self.tclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
        self.toid = toid
        #tobj=tclass[adocontext.toid]
        self._fieldsbyname = None

    def getIsVersionControl(self):
        return self.tclass.IsVersionControl.ValuesAsInt(self.toid)

    def getFieldExists(self, afieldname):
        if self._fieldsbyname is None:
            self._fieldsbyname = {}
            bobj = self.tclass[self.toid]
            fobj = bobj.Pola
            while fobj:
                afn = fobj.NazwaID
                self._fieldsbyname[afn.lower()] = afn
                fobj.Next()
        return self._fieldsbyname.has_key(afieldname.lower())


class ICORDBADOTables(object):

    def __init__(self, adb):
        self.db = adb

    def getDataAccessHistory(self, adocontext):
        ret = []
        avtablename = '%sACCESSHISTORY_0' % (adocontext.basenamemodifier, )
        try:
            asql = '''
            select top 1000 _OID,Action,RefTable,RefItem,RefOID,RemoteAddr,HttpUserAgent,_DateTime,_UserName,
            case 
               when Action='SO' then 'Obejrzenie rekordu' 
               when  Action='DD' then 'Skasowano wpis' 
               else 'Inna akcja' 
            end ActionTxt 
            from %s
            WHERE RefOID='%s' 
            order by _DateTime desc
         ''' % (avtablename, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    d2 = self.db.GetRSRowAsDict(rs, acontext=adocontext)
                    ret.append(d2)
                    rs.MoveNext()
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getDataVersionHistory(self, adocontext):
        ret = []
        atable = ICORTableHelper(adocontext.toid)
        if not atable.getIsVersionControl():
            adocontext.Close()
            return ret
        saddfields = ''
        avtablename = '%sBZR_V_%d' % (adocontext.basenamemodifier, adocontext.toid)
        pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        aprojectname = pclass.Nazwa[adocontext.poid]
        if atable.getFieldExists('InformacjaPodmiotUdostepniajacy') and atable.getFieldExists('InformacjaOsobaOdpowiedzialna') and atable.getFieldExists('InformacjaDataWytworzenia') and atable.getFieldExists('InformacjaOpisCzynnosci'):
            saddfields = ',InformacjaPodmiotUdostepniajacy,InformacjaOsobaOdpowiedzialna,InformacjaDataWytworzenia,InformacjaOpisCzynnosci'
        else:
            saddfields = ",'' as InformacjaPodmiotUdostepniajacy,'' as InformacjaOsobaOdpowiedzialna,'' as InformacjaDataWytworzenia,'' as InformacjaOpisCzynnosci"
        try:
            asql = '''
            select top 1000
            _OID,_datetime,_UserName,_OIDRef, 
            case 
               when _action='insert' then 'Dodano wpis' 
               when _action='delete' then 'Skasowano wpis' 
               when _action='update' then 'Zaktualizowano wpis' 
               else 'Inna akcja' 
            end Akcja
            %s
            from %s
            WHERE 
            _OIDRef='%s' 
            order by _datetime desc
         ''' % (saddfields, avtablename, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    d2 = self.db.GetRSRowAsDict(rs, acontext=adocontext)
                    d2['_URL'] = 'appdata/%s/crm/BZR_V_%d_so.asp?ioid=%s' % (aprojectname, adocontext.toid, adocontext.ioid)
                    ret.append(d2)
                    rs.MoveNext()
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getTableCapabilities(self, adocontext):
        ret = {}
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is not None:
                ret = acapabilities.GetInfo(adocontext)
        finally:
            adocontext.Close()
        return ret

    def getTableColumns(self, adocontext, tablename, anoutf8=1, anomodifier=0):
        if not anomodifier:
            tablename = '%s%s' % (adocontext.basenamemodifier, tablename)
        ret = ''
        try:
            asql = '''
            select substring(
            (select ','+COLUMN_NAME AS 'data()' 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='%s' and COLUMN_NAME not in ('_OID','_timestamp') 
            for xml path(''))
            ,2,8000) as result
         ''' % (tablename, )
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not anoutf8:
                    ret = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'result', astype=0))
                else:
                    ret = ADOLibInit.GetRSValueAsStr(rs, 'result', astype=0)
                rs = adocontext.CloseRS(rs)
        finally:
            pass
        return ret

    def setRecordVersion(self, adocontext, tableid, versiontablename='', aoid='', aaction=''):
        if type(tableid) == type(1):
            tablename = '%sBZR_%d' % (adocontext.basenamemodifier, tableid)
            versiontablename = '%sBZR_V_%d' % (adocontext.basenamemodifier, tableid)
        else:
            tablename = '%s%s' % (adocontext.basenamemodifier, tableid)
            versiontablename = '%s%s' % (adocontext.basenamemodifier, versiontablename)
        aaction = aaction.upper()
        scolumns = self.getTableColumns(adocontext, tablename, anomodifier=1)
        asql = '''
         insert into %s
         (
         %s
         ,_action,_oidref
         )
         select
         %s
         ,'%s' as _action,_OID as _OIDRef from %s
         WHERE _OID='%s'
      ''' % (versiontablename, scolumns, scolumns, aaction, tablename, aoid)
        try:
            adocontext.Execute(asql)
        except:
            print 'ERROR: ' + asql
            raise

    def getTableRecord(self, adocontext, tablename, fields, aoid, anoclosecontext=1, anoutf8=1, anomodifier=0):
        ret = {}
        if not anomodifier:
            tablename = '%s%s' % (adocontext.basenamemodifier, tablename)
        sfields = ','.join(fields)
        try:
            asql = '''
            SELECT TOP 1 
            %s
            from %s
            WHERE 
            _OID='%s'
         ''' % (sfields, tablename, aoid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    mf = rs.Fields.Count
                    if not anoutf8:
                        for i in range(mf):
                            ret[rs.Fields.Item(i).Name] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0))
                    else:
                        for i in range(mf):
                            ret[rs.Fields.Item(i).Name] = ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0)
                    rs.MoveNext()
                rs = adocontext.CloseRS(rs)
        finally:
            if not anoclosecontext:
                adocontext.Close()
        return ret

    def checkRecordModified(self, lfields, data, olddata, aslist=0):
        if aslist:
            ret = []
        for afieldname in lfields:
            if olddata[afieldname] != data[afieldname]:
                if not aslist:
                    return 1
                else:
                    ret.append(afieldname)
        if aslist:
            return ret
        return 0

    def getAbstraktLoad(self, adocontext):
        ret = {'tytul': '', 'tresc': ''}
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Abstrakty:
                return ret
            asql = '''
            select top 1 tytul, tresc
            FROM %s
            WHERE _OIDDictRef='%s'
            order by _DateTime desc
         ''' % (acapabilities.aTable_Abstrakty, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    ret['tytul'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'tytul', astype=0))
                    ret['tresc'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'tresc', astype=0))
                    rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getAbstraktSave(self, adocontext, atytul, atresc):
        ret = 'BAD'
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Abstrakty:
                return ret
            asql = '''
            select top 1 _OID,tytul,tresc,_OIDDictRef,_UID,_UserName,_DateTime
            FROM %s
            WHERE _OIDDictRef='%s'
            order by _DateTime desc
         ''' % (acapabilities.aTable_Abstrakty, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.EOF or rs.BOF:
                rs.AddNew()
                rs.Fields.Item("_OIDDictRef").Value = adocontext.ioid
            rs.Fields.Item('tytul').Value = atytul
            rs.Fields.Item('tresc').Value = atresc
            rs.Fields.Item("_UID").Value = adocontext.uid
            auser = ICORSecurity.ICORSecurityUser(adocontext.uid)
            rs.Fields.Item("_UserName").Value = auser.UserName
            rs.Fields.Item("_DateTime").Value = storageutil.tdatetime2fmtstr()
            rs.Update()
            ret = 'OK'
            time.sleep(0.5)
            foid = adocontext.GetRSValueAsStr(rs, '_OID')
            rs = adocontext.CloseRS(rs)
            if foid:
                self.setRecordVersion(adocontext, acapabilities.aTableOID_Kalendarium, aoid=foid, aaction='UPDATE')
        finally:
            adocontext.Close()
        return ret

    def getKalendariumLoad(self, adocontext):
        ret={
          'nazwa': '',
          'dataRozpoczecia': '',
          'dataZakonczenia': '',
          'wyswietlajAktualnosciOd': '',
          'wyswietlajAktualnosciDo': '',
          'opis': '',
          'uwagi': '',
          'priorytetWyswietlania': 'N1',
          'priorytetAktualnosci': '03',
          'statusZatwierdzenia': 'T1'
        } # yapf: disable
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Kalendarium:
                return ret
            asql = '''
            select top 1 _OID,Nazwa,DataRozpoczecia,DataZakonczenia,WyswietlajAktualnosciDo,PriorytetAktualnosci,Opis,WyswietlajAktualnosciOd,Uwagi,StatusZatwierdzenia,PriorytetWyswietlania,
               _ChapterID,_OIDDictRef,InformacjaOpisCzynnosci,InformacjaDataWytworzenia,InformacjaOsobaOdpowiedzialna,InformacjaPodmiotUdostepniajacy,_datetime,_UID,_UserName
            FROM %s
            WHERE _OIDDictRef='%s'
            order by _datetime desc
         ''' % (acapabilities.aTable_Kalendarium, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    ret['nazwa'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'Nazwa', astype=0))
                    ret['dataRozpoczecia'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'DataRozpoczecia', astype=0))
                    ret['dataZakonczenia'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'DataZakonczenia', astype=0))
                    ret['wyswietlajAktualnosciOd'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'WyswietlajAktualnosciOd', astype=0))
                    ret['wyswietlajAktualnosciDo'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'WyswietlajAktualnosciDo', astype=0))
                    ret['opis'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'Opis', astype=0))
                    ret['uwagi'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'Uwagi', astype=0))
                    ret['priorytetWyswietlania'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'PriorytetWyswietlania', astype=0))
                    ret['priorytetAktualnosci'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'PriorytetAktualnosci', astype=0))
                    ret['statusZatwierdzenia'] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, 'StatusZatwierdzenia', astype=0))
                    rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getKalendariumSave(self, adocontext, anazwa, adataRozpoczecia, adataZakonczenia, awyswietlajAktualnosciOd, awyswietlajAktualnosciDo, aopis, auwagi, apriorytetWyswietlania, apriorytetAktualnosci, astatusZatwierdzenia):
        ret = 'BAD'
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Kalendarium:
                return ret
            asql = '''
            select top 1 _OID,Nazwa,DataRozpoczecia,DataZakonczenia,WyswietlajAktualnosciDo,PriorytetAktualnosci,Opis,WyswietlajAktualnosciOd,Uwagi,StatusZatwierdzenia,PriorytetWyswietlania,
               _ChapterID,_OIDDictRef,InformacjaOpisCzynnosci,InformacjaDataWytworzenia,InformacjaOsobaOdpowiedzialna,InformacjaPodmiotUdostepniajacy,_datetime,_UID,_UserName
            FROM %s
            WHERE _OIDDictRef='%s'
            order by _datetime desc
         ''' % (acapabilities.aTable_Kalendarium, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.EOF or rs.BOF:
                rs.AddNew()
                rs.Fields.Item("_OIDDictRef").Value = adocontext.ioid
            rs.Fields.Item('Nazwa').Value = anazwa
            rs.Fields.Item('DataRozpoczecia').Value = adataRozpoczecia
            rs.Fields.Item('DataZakonczenia').Value = adataZakonczenia
            rs.Fields.Item('WyswietlajAktualnosciOd').Value = awyswietlajAktualnosciOd
            rs.Fields.Item('WyswietlajAktualnosciDo').Value = awyswietlajAktualnosciDo
            rs.Fields.Item('PriorytetAktualnosci').Value = apriorytetAktualnosci
            rs.Fields.Item('Opis').Value = aopis
            rs.Fields.Item('Uwagi').Value = auwagi
            rs.Fields.Item('StatusZatwierdzenia').Value = astatusZatwierdzenia
            rs.Fields.Item('PriorytetWyswietlania').Value = apriorytetWyswietlania
            rs.Fields.Item("_UID").Value = adocontext.uid
            auser = ICORSecurity.ICORSecurityUser(adocontext.uid)
            rs.Fields.Item("_UserName").Value = auser.UserName
            rs.Fields.Item("_DateTime").Value = storageutil.tdatetime2fmtstr()
            rs.Update()
            ret = 'OK'
            time.sleep(0.5)
            foid = adocontext.GetRSValueAsStr(rs, '_OID')
            rs = adocontext.CloseRS(rs)
            if foid:
                self.setRecordVersion(adocontext, acapabilities.aTableOID_Kalendarium, aoid=foid, aaction='UPDATE')
        finally:
            adocontext.Close()
        return ret

    def getGeolokalizacjaLoad(self, adocontext):
        ret = []
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Geolokalizacja:
                return ret
            asql = '''
            select _oid,
               info,lat,lon,tableid,
               _ChapterID,_OIDDictRef,InformacjaOpisCzynnosci,InformacjaDataWytworzenia,InformacjaOsobaOdpowiedzialna,InformacjaPodmiotUdostepniajacy,_datetime,_UID,_UserName
            FROM %s
            WHERE _OIDDictRef='%s'
            order by info
         ''' % (acapabilities.aTable_Geolokalizacja, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                dmodel={
                  '_oid': '',
                  'info': 'title',
                  'lat': '',
                  'lon': 'lng',
                } # yapf: disable
                while not rs.EOF and not rs.BOF:
                    d2 = self.db.GetRSRowAsDictByFields(rs, acontext=adocontext, dmodel=dmodel, astype=1, asutf=1)
                    d2['mid'] = -1
                    ret.append(d2)
                    rs.MoveNext()
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getGeolokalizacjaSave(self, adocontext, aoid, atitle, alat, alng):
        ret = {}
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Geolokalizacja:
                return ret
            asql = '''
            select top 1 _oid,
               info,lat,lon,tableid,
               _ChapterID,_OIDDictRef,InformacjaOpisCzynnosci,InformacjaDataWytworzenia,InformacjaOsobaOdpowiedzialna,InformacjaPodmiotUdostepniajacy,_datetime,_UID,_UserName
            FROM %s
            WHERE _OID='%s'
            order by _datetime desc
         ''' % (acapabilities.aTable_Geolokalizacja, aoid)
            rs = adocontext.GetRS(asql)
            if rs.EOF or rs.BOF:
                rs.AddNew()
                rs.Fields.Item("_OIDDictRef").Value = adocontext.ioid
                rs.Fields.Item("tableid").Value = adocontext.toid
            rs.Fields.Item('info').Value = atitle
            rs.Fields.Item('lat').Value = str(alat)
            rs.Fields.Item('lon').Value = str(alng)
            rs.Fields.Item("_UID").Value = adocontext.uid
            auser = ICORSecurity.ICORSecurityUser(adocontext.uid)
            rs.Fields.Item("_UserName").Value = auser.UserName
            rs.Fields.Item("_DateTime").Value = storageutil.tdatetime2fmtstr()
            rs.Update()
            time.sleep(0.5)
            boid = adocontext.GetRSValueAsStr(rs, '_oid')
            rs = adocontext.CloseRS(rs)
            if boid:
                self.setRecordVersion(adocontext, acapabilities.aTableOID_Geolokalizacja, aoid=boid, aaction='UPDATE')
            ret['_oid'] = boid
        finally:
            adocontext.Close()
        return ret

    def getGeolokalizacjaDelete(self, adocontext, aoid):
        ret = 'BAD'
        try:
            if not aoid:
                return ret
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Geolokalizacja:
                return ret
            self.setRecordVersion(adocontext, acapabilities.aTableOID_Geolokalizacja, aoid=aoid, aaction='DELETE')
            asql = '''
            delete %s WHERE _OID='%s'
         ''' % (acapabilities.aTable_Geolokalizacja, aoid)
            adocontext.Execute(asql)
            ret = 'OK'
        finally:
            adocontext.Close()
        return ret

    def getCategoriesLoad(self, adocontext):
        ret = []
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Categories:
                return ret
            asql = '''
            select 
            t1._oid,t1.kategoria,t1.rola,t1.grupa,
            coalesce(t2._oid,'') as koid, CASE WHEN t2._oid IS NULL THEN 0 ELSE 1 END kchecked
            from %s t1
            left join %s t2 on t2.IdObiektu='%s' and t1._oid=t2.kategoria
            order by t1.Kategoria,t1.Rola,t1.Grupa
         ''' % (acapabilities.aTable_Categories, acapabilities.aTable_CategoriesAssigned, adocontext.ioid)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                dmodel={
                  '_oid': '',
                  'kategoria': '',
                  'rola': '',
                  'grupa': '',
                  'koid': '',
                  'kchecked': '',
                } # yapf: disable
                while not rs.EOF and not rs.BOF:
                    d2 = self.db.GetRSRowAsDictByFields(rs, acontext=adocontext, dmodel=dmodel, astype=1, asutf=1)
                    ret.append(d2)
                    rs.MoveNext()
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        return ret

    def getCategoriesSave(self, adocontext, aoid, kchecked):
        ret = 'BAD'
        try:
            if not aoid:
                return ret
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_Categories:
                return ret
            asql = '''
            delete %s WHERE kategoria='%s' and idobiektu='%s'
         ''' % (acapabilities.aTable_CategoriesAssigned, aoid, adocontext.ioid)
            adocontext.Execute(asql)
            if kchecked:
                asql = '''
               insert into %s (kategoria,idobiektu) values ('%s','%s')
            ''' % (acapabilities.aTable_CategoriesAssigned, aoid.upper(), adocontext.ioid.upper())
                adocontext.Execute(asql)
            ret = 'OK'
        finally:
            adocontext.Close()
        return ret

    def getTablesLoad(self, adocontext, ioid):
        ret = []
        dxml = {}
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_TablesAssigned:
                return ret
            asql = '''
            SELECT Rozdzial,IdObiektu,Xmldataid,CMSID FROM %s where IdObiektu='%s' and CMSID=%d
         ''' % (acapabilities.aTable_TablesAssigned, adocontext.ioid, acapabilities.WWWMenuStruct.MenuStructObj.OID)
            rs = adocontext.GetRS(asql)
            if rs.State != adocontext.adoconst.adStateClosed:
                dmodel={
                  'Rozdzial': '',
                  'IdObiektu': '',
                  'Xmldataid': '',
                } # yapf: disable
                while not rs.EOF and not rs.BOF:
                    d2 = self.db.GetRSRowAsDictByFields(rs, acontext=adocontext, dmodel=dmodel, astype=1, asutf=1)
                    dxml[d2['Xmldataid']] = d2
                    rs.MoveNext()
                rs = adocontext.CloseRS(rs)
        finally:
            adocontext.Close()
        tobj = acapabilities.WWWMenuStruct.MenuStructObj.TabeleZrodlowe
        lret = []
        while tobj:
            xobj = tobj.XMLData
            while xobj:
                atext = xobj.XMLSource
                if atext.find('iscmspublic="1"') > 0:
                    if ICORSecurity.CheckRecursiveAccessLevelForUser(xobj, 'AccessLevelView', auid=adocontext.uid):
                        d2 = {
                            'name': storageutil.CP1250_To_UTF8(xobj.Name),
                            'oid': xobj.OID,
                            'table': storageutil.CP1250_To_UTF8(tobj.Nazwa),
                            'checked': dxml.has_key(xobj.OID),
                        } # yapf: disable
                        lret.append([d2['name'], d2['table'], d2['oid'], d2])
                xobj.Next()
            tobj.Next()
        lret.sort()
        for aname, atable, aoid, d2 in lret:
            ret.append(d2)
        return ret

    def getTablesSave(self, adocontext, ioid, chapterid, xmlid, checked):
        ret = 'BAD'
        if not ioid or chapterid<0 or xmlid<0:
            return ret
        try:
            acapabilities = self.db.GetCapabilitiesWWWMenuStructByContext(adocontext)
            if acapabilities is None:
                return ret
            if not acapabilities.aTable_TablesAssigned:
                return ret
            asql = '''
            delete %s WHERE xmldataid=%d and idobiektu='%s' and cmsid=%d
         ''' % (acapabilities.aTable_TablesAssigned, xmlid, ioid, acapabilities.WWWMenuStruct.MenuStructObj.OID)
            adocontext.Execute(asql)
            if checked:
                asql = '''
               insert into %s (rozdzial,xmldataid,idobiektu,cmsid) values (%d,%d,'%s',%d)
            ''' % (acapabilities.aTable_TablesAssigned, chapterid, xmlid, ioid.upper(), acapabilities.WWWMenuStruct.MenuStructObj.OID)
                adocontext.Execute(asql)
            ret = 'OK'
        finally:
            adocontext.Close()
        return ret
