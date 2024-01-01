# -*- coding: utf-8 -*-
import sys
import os
import time
import traceback

try:
    import json
except:
    import simplejson as json

import appplatform.storageutil as storageutil
import icordbmain.dbaccess as dbaccess

import dbadofiles
import dbadotables

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.icorsecurity as ICORSecurity
import icordbmain.adoutil as ADOLibInit
import icorlib.projekt.mcrmbasesimple as MCRMBaseSimple


class CapabilitiesWWWMenuStruct(object):

    def __init__(self, adocontext, awwwmenustruct):
        self.WWWMenuStruct = awwwmenustruct

        aplugin = awwwmenustruct.GetPluginByTemplate('Multimedia')
        if aplugin is not None:
            self.aTableOID_Multimedia = aplugin.PluginVars.getint('aTableOID_Multimedia', -1)
            if self.aTableOID_Multimedia >= 0:
                self.aTable_Multimedia = '%sBZR_%d' % (adocontext.basenamemodifier, self.aTableOID_Multimedia)
                self.aTable_MultimediaVersion = '%sBZR_V_%d' % (adocontext.basenamemodifier, self.aTableOID_Multimedia)
            self.aTableOIDs_Allowed_Multimedia = aplugin.PluginVars.getlistint('aTableOIDs_Allowed')
            self.Multimedia_aMaxSize = aplugin.PluginVars.getint('aMaxSize', 0)
            self.Multimedia_aAllowedImageTypes = aplugin.PluginVars.get('aAllowedImageTypes', '')
            self.Multimedia_aAllowedAudioTypes = aplugin.PluginVars.get('aAllowedAudioTypes', '')
            self.Multimedia_aAllowedVideoTypes = aplugin.PluginVars.get('aAllowedVideoTypes', '')
            self.Multimedia_aAllowedMediaTypes = aplugin.PluginVars.get('aAllowedMediaTypes', '')
        else:
            self.aTableOID_Multimedia = -1
            self.aTable_Multimedia = ''
            self.aTable_MultimediaVersion = ''
            self.aTableOIDs_Allowed_Multimedia = []
            self.Multimedia_aMaxSize = 15000000
            self.Multimedia_aAllowedImageTypes = '|bmp|gif|jpeg|jpg|png|tif|tiff|'
            self.Multimedia_aAllowedAudioTypes = '|mp3|'
            self.Multimedia_aAllowedVideoTypes = '|avi|flv|mp4|wmv|mpg|mpeg|'
            self.Multimedia_aAllowedMediaTypes = '|3g2|3gp2|3gp|3gpp|aac|ac3|aif|aifc|aiff|amv|asf|asx|au|avi|bmp|cda|divx|dsm|dsv|dsa|dss|dts|fla|flac|flv|gif|jpeg|jpg|m1a|m1v|m2a|m2v|m3u|m4a|m4b|mid|midi|mka|mkv|mov|mp2|mp3|mp4|mpa|mpc|mpe|mpeg|mpg|oga|ogg|ogm|ogv|pdf|pls|png|psd|qt|ra|ram|rm|rmi|rmm|rmvb|rpm|snd|swf|tif|tiff|vob|wav|wm|wma|wmp|wmv|wmx|wvx|'

        aplugin = awwwmenustruct.GetPluginByTemplate('Kalendarium')
        if aplugin is not None:
            self.aTableOID_Kalendarium = aplugin.PluginVars.getint('aTableOID_Kalendarium', -1)
            if self.aTableOID_Kalendarium >= 0:
                self.aTable_Kalendarium = '%sBZR_%d' % (adocontext.basenamemodifier, self.aTableOID_Kalendarium)
            self.aTableOIDs_Allowed_Kalendarium = aplugin.PluginVars.getlistint('aTableOIDs_Allowed')
        else:
            self.aTableOID_Kalendarium = -1
            self.aTable_Kalendarium = ''
            self.aTableOIDs_Allowed_Kalendarium = []

        aplugin = awwwmenustruct.GetPluginByTemplate('Geolokalizacja')
        if aplugin is not None:
            self.aTableOID_Geolokalizacja = aplugin.PluginVars.getint('aTableOID_LokalizacjaGeoRSS', -1)
            if self.aTableOID_Geolokalizacja >= 0:
                self.aTable_Geolokalizacja = '%sBZR_%d' % (adocontext.basenamemodifier, self.aTableOID_Geolokalizacja)
            self.aTableOIDs_Allowed_Geolokalizacja = aplugin.PluginVars.getlistint('aTableOIDs_Allowed')
            self.Geolokalizacja_Default_Lat = aplugin.PluginVars.get('aDefault_Lat', '53.44561198555037')
            self.Geolokalizacja_Default_Lon = aplugin.PluginVars.get('aDefault_Lon', '14.51457023206054')
        else:
            self.aTableOID_Geolokalizacja = -1
            self.aTable_Geolokalizacja = ''
            self.aTableOIDs_Allowed_Geolokalizacja = []
            self.Geolokalizacja_Default_Lat = ''
            self.Geolokalizacja_Default_Lon = ''

        aplugin = awwwmenustruct.GetPluginByTemplate('Abstrakty')
        if aplugin is not None:
            self.aTableOID_Abstrakty = aplugin.PluginVars.getint('aTableOID_Abstrakty', -1)
            if self.aTableOID_Abstrakty >= 0:
                self.aTable_Abstrakty = '%sBZR_%d' % (adocontext.basenamemodifier, self.aTableOID_Abstrakty)
            self.aTableOIDs_Allowed_Abstrakty = aplugin.PluginVars.getlistint('aTableOIDs_Allowed')
            self.Abstrakty_Max_TextLength = aplugin.PluginVars.getint('aMax_TextLength', 500)
        else:
            self.aTableOID_Abstrakty = -1
            self.aTable_Abstrakty = ''
            self.aTableOIDs_Allowed_Abstrakty = []
            self.Abstrakty_Max_TextLength = 500

        aplugin = awwwmenustruct.GetPluginByTemplate(storageutil.UTF8_To_CP1250('Kategorie treści'))
        if aplugin is not None:
            self.aTableOID_Categories = aplugin.PluginVars.getint('aTableOID_Categories', -1)
            if self.aTableOID_Categories >= 0:
                self.aTable_Categories = '%sBZR_%d' % (adocontext.basenamemodifier, self.aTableOID_Categories)
            self.aTableOID_CategoriesAssigned = aplugin.PluginVars.getint('aTableOID_AssignedCategories', -1)
            if self.aTableOID_CategoriesAssigned >= 0:
                self.aTable_CategoriesAssigned = '%sBZR_%d' % (adocontext.basenamemodifier, self.aTableOID_CategoriesAssigned)
            self.aTableOIDs_Allowed_Categories = aplugin.PluginVars.getlistint('aTableOIDs_Allowed')
        else:
            self.aTableOID_Categories = -1
            self.aTable_Categories = ''
            self.aTableOID_CategoriesAssigned = -1
            self.aTable_CategoriesAssigned = ''
            self.aTableOIDs_Allowed_Categories = []

        aplugin = awwwmenustruct.GetPluginByTemplate(storageutil.UTF8_To_CP1250('Tabele w treści'))
        if aplugin is not None:
            self.aTableOID_TablesAssigned = aplugin.PluginVars.getint('aTableOID_AssignedTables', -1)
            if self.aTableOID_TablesAssigned >= 0:
                self.aTable_TablesAssigned = '%sBZR_%d' % (adocontext.basenamemodifier, self.aTableOID_TablesAssigned)
            self.aTableOIDs_Allowed_Tables = aplugin.PluginVars.getlistint('aTableOIDs_Allowed')
        else:
            self.aTableOID_TablesAssigned = -1
            self.aTable_TablesAssigned = ''
            self.aTableOIDs_Allowed_Tables = []

    def GetInfo(self, adocontext):
        ret = {}
        ret['aTableOID_Multimedia'] = self.aTableOID_Multimedia
        ret['aTableOIDs_Allowed_Multimedia'] = self.aTableOIDs_Allowed_Multimedia
        ret['aMultimedia'] = 1 if adocontext.toid in self.aTableOIDs_Allowed_Multimedia else 0
        ret['aTableOID_Kalendarium'] = self.aTableOID_Kalendarium
        ret['aTableOIDs_Allowed_Kalendarium'] = self.aTableOIDs_Allowed_Kalendarium
        ret['aKalendarium'] = 1 if adocontext.toid in self.aTableOIDs_Allowed_Kalendarium else 0
        ret['aTableOID_Geolokalizacja'] = self.aTableOID_Geolokalizacja
        ret['aTableOIDs_Allowed_Geolokalizacja'] = self.aTableOIDs_Allowed_Geolokalizacja
        ret['aGeolokalizacja'] = 1 if adocontext.toid in self.aTableOIDs_Allowed_Geolokalizacja else 0
        ret['Geolokalizacja_Default_Lat'] = self.Geolokalizacja_Default_Lat
        ret['Geolokalizacja_Default_Lon'] = self.Geolokalizacja_Default_Lon
        ret['aTableOID_Abstrakty'] = self.aTableOID_Abstrakty
        ret['aTableOIDs_Allowed_Abstrakty'] = self.aTableOIDs_Allowed_Abstrakty
        ret['aAbstrakty'] = 1 if adocontext.toid in self.aTableOIDs_Allowed_Abstrakty else 0
        ret['Abstrakty_Max_TextLength'] = self.Abstrakty_Max_TextLength
        ret['aTableOID_Categories'] = self.aTableOID_Categories
        ret['aTableOID_CategoriesAssigned'] = self.aTableOID_CategoriesAssigned
        ret['aTableOIDs_Allowed_Categories'] = self.aTableOIDs_Allowed_Categories
        ret['aCategories'] = 1 if adocontext.toid in self.aTableOIDs_Allowed_Categories else 0
        ret['aTableOID_TablesAssigned'] = self.aTableOID_TablesAssigned
        ret['aTableOIDs_Allowed_Tables'] = self.aTableOIDs_Allowed_Tables
        ret['aTables'] = 1 if adocontext.toid in self.aTableOIDs_Allowed_Tables else 0
        return ret


class ICORDBADO(object):

    def __init__(self, acominitialize=1):
        self.cominitialize = acominitialize
        self.dbfiles = dbadofiles.ICORDBADOFiles(self)
        self.dbtables = dbadotables.ICORDBADOTables(self)
        self.conncnt = 0
        self.ClearCache()

    def ClearCache(self):
        self.connectionsbypid = {}
        self.connectionsbycmsid = {}
        self.connectionsbyuid = {}
        self.cmsidbychapterid = {}
        self.capabilitiesWWWMenuStruct = {}
        self.CMS = MCRMBaseSimple.CMS()

    def GetConnectionByProject(self, poid, apublic=0, aservercursor=0):
        akey = (poid, apublic)
        aconnectionstring = ''
        if not self.connectionsbypid.has_key(akey):
            pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
            pobj = pclass[poid]
            abasenamemodifier = pobj.BaseNameModifier
            if apublic:
                dobj = pobj.DBAccessPublic
                if dobj:
                    aconnectionstring = dbaccess.GetConnectionString(dobj)
            if not aconnectionstring:
                dobj = pobj.DBAccess
                if dobj:
                    aconnectionstring = dbaccess.GetConnectionString(dobj)
            if aconnectionstring:
                self.connectionsbypid[akey] = aconnectionstring, abasenamemodifier
        aconnectionstring, abasenamemodifier = self.connectionsbypid.get(akey, ('', ''))
        if not aconnectionstring:
            return None
        try:
            aadoutil = ADOLibInit.ADOUtil(aconnectionstring, aservercursor=aservercursor, acominitialize=self.cominitialize)
        except:
            return None
        aadoutil.SetContextVars(uid=None, poid=poid, cmsid=None, toid=None, coid=None, ioid=None, basenamemodifier=abasenamemodifier, infotablessufix=None)
        return aadoutil

    def GetConnectionByCMS(self, woid, apublic=0, aprojectconnection=1, aservercursor=0):
        akey = (woid, apublic)
        aconnectionstring = ''
        poid = None
        abasenamemodifier = None
        ainfotablessufix = None
        if not self.connectionsbycmsid.has_key(akey):
            wclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
            wobj = wclass[woid]
            pobj = wobj.Projekt
            abasenamemodifier = pobj.BaseNameModifier
            poid = pobj.OID
            ainfotablessufix = wobj['InfoTablesSufix', ICORInterface.mt_Integer]
            if aprojectconnection:
                dobj = pobj.DBAccess
                if dobj:
                    aconnectionstring = dbaccess.GetConnectionString(dobj)
            elif apublic:
                dobj = wobj.DBAccessPublic
                if dobj:
                    aconnectionstring = dbaccess.GetConnectionString(dobj)
                else:
                    dobj = pobj.DBAccessPublic
                    if dobj:
                        aconnectionstring = dbaccess.GetConnectionString(dobj)
                    if not aconnectionstring:
                        dobj = pobj.DBAccess
                        if dobj:
                            aconnectionstring = dbaccess.GetConnectionString(dobj)
            else:
                dobj = wobj.DBAccess
                if dobj:
                    aconnectionstring = dbaccess.GetConnectionString(dobj)
            if aconnectionstring:
                self.connectionsbycmsid[akey] = aconnectionstring, ainfotablessufix, poid, abasenamemodifier
        aconnectionstring, ainfotablessufix, poid, abasenamemodifier = self.connectionsbycmsid.get(akey, '')
        if not aconnectionstring:
            return None
        try:
            aadoutil = ADOLibInit.ADOUtil(aconnectionstring, aservercursor=aservercursor, acominitialize=self.cominitialize)
        except:
            return None
        aadoutil.SetContextVars(uid=None, poid=poid, cmsid=woid, toid=None, coid=None, ioid=None, basenamemodifier=abasenamemodifier, infotablessufix=ainfotablessufix)
        return aadoutil

    def GetConnectionByTable(self, toid, apublic=0, aservercursor=0):
        tclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
        tobj = tclass[toid]
        aadoutil = self.GetConnectionByProject(tobj.Projekt.OID, apublic, aservercursor)
        if aadoutil is None:
            return None
        aadoutil.SetContextVars(uid=None, poid=None, cmsid=None, toid=toid, coid=None, ioid=None, basenamemodifier=None, infotablessufix=None)
        return aadoutil

    def GetCMSIDByChapterID(self, coid):
        if not self.cmsidbychapterid.has_key(coid):
            ret = -1
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
            bobj = aclass[coid]
            wobj = None
            while not wobj and bobj:
                wobj = bobj.Struktura
                if wobj:
                    ret = wobj.OID
                bobj = bobj.NadRozdzial
            self.cmsidbychapterid[coid] = ret
        return self.cmsidbychapterid[coid]

    def GetConnectionByChapter(self, coid, apublic=0, aservercursor=0):
        woid = self.GetCMSIDByChapterID(coid)
        aadoutil = self.GetConnectionByCMS(woid, apublic, aservercursor)
        if aadoutil is None:
            return None
        aadoutil.SetContextVars(uid=None, poid=None, cmsid=None, toid=None, coid=coid, ioid=None, basenamemodifier=None, infotablessufix=None)
        return aadoutil

    def GetProjectByContext(self, adocontext):
        #print 'GetProjectByContext poid=%d woid=%d toid=%d'%(adocontext.poid,adocontext.cmsid,adocontext.toid)
        if adocontext.cmsid < 0 and adocontext.coid >= 0:
            woid = self.GetCMSIDByChapterID(adocontext.coid)
            aadoutil.SetContextVars(uid=None, poid=None, cmsid=woid, toid=None, coid=None, ioid=None, basenamemodifier=None, infotablessufix=None)
        aproject = None
        if adocontext.poid < 0 and adocontext.toid >= 0:
            tclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
            tobj = tclass[adocontext.toid]
            pobj = tobj.Projekt
            if pobj.OID >= 0:
                aadoutil.SetContextVars(uid=None, poid=pobj.OID, cmsid=None, toid=None, coid=None, ioid=None, basenamemodifier=None, infotablessufix=None)
            aproject = self.CMS.GetProject(pobj)
        elif adocontext.poid >= 0:
            pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
            pobj = pclass[adocontext.poid]
            aproject = self.CMS.GetProject(pobj)
        return aproject

    def GetWWWMenuStructByContext(self, adocontext):
        if adocontext.cmsid < 0 and adocontext.coid >= 0:
            woid = self.GetCMSIDByChapterID(adocontext.coid)
            aadoutil.SetContextVars(uid=None, poid=None, cmsid=woid, toid=None, coid=None, ioid=None, basenamemodifier=None, infotablessufix=None)
        if adocontext.cmsid < 0 or adocontext.poid < 0:
            return None
        wclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
        wobj = wclass[adocontext.cmsid]
        pobj = wobj.Projekt
        aproject = self.CMS.GetProject(pobj)
        if aproject is None:
            return None
        awwwmenustruct = aproject.GetWWWMenuStruct(wobj)
        return awwwmenustruct

    def GetPluginByContext(self, adocontext, atemplate):
        awwwmenustruct = self.GetWWWMenuStructByContext(adocontext)
        if awwwmenustruct is None:
            return None
        return awwwmenustruct.GetPluginByTemplate(atemplate)

    def GetCapabilitiesWWWMenuStructByContext(self, adocontext):
        awwwmenustruct = self.GetWWWMenuStructByContext(adocontext)
        if awwwmenustruct is None:
            return None
        aCapabilitiesWWWMenuStruct = self.capabilitiesWWWMenuStruct.get(awwwmenustruct.OID, None)
        if aCapabilitiesWWWMenuStruct is None:
            aCapabilitiesWWWMenuStruct = CapabilitiesWWWMenuStruct(adocontext, awwwmenustruct)
            self.capabilitiesWWWMenuStruct[awwwmenustruct.OID] = aCapabilitiesWWWMenuStruct
        return aCapabilitiesWWWMenuStruct

    def GetSafeSQLWhere(self, avalue):
        avalue = avalue.lower()
        lb = ["select", "drop", "--", "insert", "delete", "xp_", "sp_", "dbcc", "truncate", "update", "#", "%", "&", "<", ">", "/*", "*/", "@@", "varchar", "cursor", "execute", "cast", "convert", "declare"]
        for s in lb:
            avalue = avalue.replace(s, '')
        avalue = avalue.replace("'", "''")
        return avalue

    def GetRSRowAsDict(self, rs, acontext=None, astype=0, alower=0, asutf=0):
        d2 = {}
        mf = rs.Fields.Count
        for i in range(mf):
            cname = rs.Fields.Item(i).Name
            v = ADOLibInit.GetRSValueAsStr(rs, cname, astype=astype, acontext=acontext, asutf=asutf)
            if alower:
                cname = cname.lower()
            d2[cname] = v
        return d2

    def GetRSRowAsDictByFields(self, rs, acontext=None, dmodel=None, astype=0, alower=0, asutf=0):
        if dmodel is None:
            return self.GetRSRowAsDict(rs, acontext=acontext, astype=astype, alower=alower, asutf=asutf)
        d2 = {}
        for acolumn, aattr in dmodel.items():
            if not aattr:
                aattr = acolumn
            if alower:
                aattr = aattr.lower()
            v = ADOLibInit.GetRSValueAsStr(rs, acolumn, astype=astype, acontext=acontext, asutf=asutf)
            d2[aattr] = v
        return d2
