# -*- coding: utf-8 -*-
import sys
import os
import time
import traceback
import datetime
import re
try:
    import json
except:
    import simplejson as json

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil

import icorapi
import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icordbmain.dbaccess as dbaccess
import icordbmain.adoutil as ADOLibInit
import icorlib.icorsecurity as ICORSecurity

import securityload
import securityrepair
import replicationload
import appcmsbuilder
import mfdimport

UID = 0


class ICORUpgrade(object):

    def __init__(self, aICORStarter=None):
        self.aICORStarter = aICORStarter

    def SecurityRepair(self):
        afname = startutil.GetLogTempFileName('repair', aprefix='securityrepair', aext='txt')
        print 'repair raport in file: %s' % afname
        alog = startutil.MLog(afname, aconsole=0)
        securityrepair.SecurityRepair(alog=alog)

    def SecurityLoad(self, afname=None, aprofile=0):
        if afname is None:
            afname = '%ICOR%/upgradeicor_security.xml'
        if aprofile:
            import CLASSES_Library_ICORBase_External_MProfile as MProfile
            MProfile.Start()
        UID = 0
        adt1 = time.clock()
        aparser = securityload.ICORXMLSecurityReplicationParser()
        aparser.Parse('', afname)
        adt2 = time.clock()
        if aprofile:
            afname = startutil.GetLogTempFileName('profile', aprefix='securityload', aext='py')
            MProfile.Stop(afname)
            print 'profile in file: %s' % afname
        print 'Security loaded in %0.2f secs' % (adt2 - adt1, )

    def FieldReferencesColonRepair(self):
        afname = startutil.GetLogTempFileName('repair', aprefix='securityrepair', aext='txt')
        print 'repair raport in file: %s' % afname
        alog = startutil.MLog(afname, aconsole=0)
        aclass = ICORInterface.aICORDBEngine.Classes.FirstClass()
        while aclass is not None:
            lfieldnames = aclass.GetFieldsList()
            for afieldname in lfieldnames:
                afield = aclass.FieldsByName(afieldname)
                if afield.ClassOfType is not None:
                    aoid = aclass.FirstObject()
                    while aoid >= 0:
                        s = afield[aoid]
                        if s and (s[-1:] != ':'):
                            afield[aoid] = s + ':'
                            alog.Log('%d %s %d - %s' % (aclass.CID, afieldname, afield.ClassOfType.CID, s))
                        aoid = aclass.NextObject(aoid)
            aclass = ICORInterface.aICORDBEngine.Classes.NextClass(aclass)

    def ReplicationLoad(self, afname=None, aprofile=0):
        if afname is None:
            afname = '%ICOR%/upgradeicor_objects_recursive.gz'
        if aprofile:
            import CLASSES_Library_ICORBase_External_MProfile as MProfile
            MProfile.Start()
        UID = 0
        adt1 = time.clock()
        aparser = replicationload.ICORXMLReplicationParser('ICORUpgradeReceiveRecursive', adisableobjectschange=0)
        aparser.Parse()
        adt2 = time.clock()
        if aprofile:
            afname = startutil.GetLogTempFileName('profile', aprefix='replicationload', aext='py')
            MProfile.Stop(afname)
            print 'profile in file: %s' % afname
        print 'Replication loaded in %0.2f secs' % (adt2 - adt1, )

    def GetClassImportRanges(self):
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow']
        lwhere = []
        aclass.ForEachDerivedClass(self.GetClassImportRangesFunc, lwhere)
        return lwhere

    def GetClassImportRangesFunc(self, aclass, lwhere):
        methodOnClassImport = aclass.MethodsByName('OnClassImport')
        if methodOnClassImport is not None:
            dcontext = {'_AllowClassImport': 1}
            methodOnClassImport.Execute('', -1, '0', acontext=dcontext)
            if dcontext['_AllowClassImport'] != 1:
                return
        lo = []
        methodOnObjectImport = aclass.MethodsByName('OnObjectImport')
        if methodOnObjectImport is not None:
            amodule = methodOnObjectImport.AsModule()
            if hasattr(amodule, 'OIDS'):
                lo = amodule.OIDS
        #print aclass.ClassPathImport,lo
        lwhere.append([aclass.CID, lo])

    def GetSecurityImportRanges(self):
        lwhere = []
        lclasses=[
           ['CLASSES_System_Group',[[0,500],]],
           ['CLASSES_System_GroupAccessLevel',[[0,500],]],
           ['CLASSES_System_GroupItemAccessLevel',[[0,500],]],
           ['CLASSES_System_Security_OIDRange',[]],
           ['CLASSES_System_Security_UIDRange',[]],
           ['CLASSES_System_Startup',[]],
           ['CLASSES_System_SystemDictionary_ProfileGroup',[]],
           ['CLASSES_System_SystemDictionary_UserVariable',[]],
           ['CLASSES_System_User',[]],
           ['CLASSES_Library_NetBase_WWW_Log_Login',[]],
        ] # yapf: disable
        for aclasspath in lclasses:
            aclass = ICORInterface.aICORDBEngine.Classes[aclasspath]
            lwhere.append([aclass.CID, []])
        return lwhere

    def GetSecurityClearRanges(self):
        lwhere = []
        lclasses=[
           ['CLASSES_System_Group',[[0,500],]],
           ['CLASSES_System_GroupAccessLevel',[[0,500],]],
           ['CLASSES_System_GroupItemAccessLevel',[[0,500],]],
           ['CLASSES_System_SystemDictionary_ProfileGroup',[[0,5],]],
           ['CLASSES_System_SystemDictionary_UserVariable',[]],
           ['CLASSES_System_User',[[0,500],]],
           ['CLASSES_Library_NetBase_WWW_Log_Login',[]],
        ] # yapf: disable
        for aclasspath, loids in lclasses:
            aclass = ICORInterface.aICORDBEngine.Classes[aclasspath]
            lwhere.append([aclass.CID, loids])
        return lwhere

    def DBAccessMarkSimilar(self):
        self.dconnections = {}
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DBAccess']
        for aoid in aclass:
            aobj = aclass[aoid]
            sconnection = aobj.ConnectionString
            if not self.dconnections.has_key(sconnection):
                self.dconnections[sconnection] = aoid
        lc=[
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt','DBAccess'],
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt','DBAccessPublic'],
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura','DBAccess'],
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura','DBAccessPublic'],
        ] # yapf: disable
        for bclasspath, bfieldname in lc:
            bclass = ICORInterface.aICORDBEngine.Classes[bclasspath]
            bfield = bclass.FieldsByName(bfieldname)
            bobj = bclass.GetFirstObject()
            while bobj:
                lb = []
                dobj = bobj.GetFieldValue(bfieldname)
                while dobj:
                    doid = self.dconnections.get(dobj.ConnectionString, dobj.OID)
                    lb.append([doid, dobj.CID])
                    bfield.ClassOfType.InactiveCounter[doid] = 99
                    dobj.Next()
                if lb:
                    bfield[bobj.OID] = lb
                bobj.Next()
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DBAccess']
        ld = []
        aobj = aclass.GetFirstObject()
        while aobj:
            if aobj['InactiveCounter'] == 99:
                aobj['InactiveCounter'] = 0
            else:
                ld.append(aobj.OID)
            aobj.Next()
        aclass.DeleteObject(ld)

    def DBAccessUnParseConnectionString(self, aclass, OID):
        aobj = aclass[OID]
        dp = ICORUtil.ParseVars(aobj.ConnectionString, asplit1=';', asplit2='=', areplace1='', alowerkey=1)
        aprovider = dp.popItem('provider')
        if aprovider:
            toid = aclass.DBProvider.ClassOfType.Nazwa.Identifiers(aprovider)
            if toid < 0:
                toid = 1    # empty provider oid
            aobj.DBProvider = [toid, aclass.DBProvider.ClassOfType.CID]
        adriver = dp.popItem('driver')
        if adriver:
            toid = aclass.DBDriver.ClassOfType.Nazwa.Identifiers(adriver)
            if toid < 0:
                toid = 1    # empty driver oid
            aobj.DBDriver = [toid, aclass.DBDriver.ClassOfType.CID]

        # https://docs.microsoft.com/en-us/sql/ado/guide/appendixes/microsoft-ole-db-provider-for-sql-server?view=sql-server-ver15

        # DATABASE=ICORPEBR;
        # Initial Catalog
        adatabase = dp.popItem('database') or dp.popItem('initial catalog')
        aclass.DataBaseName[OID] = adatabase

        # Data Source
        aserver = dp.popItem('server') or dp.popItem('data source')

        # UID=;
        # User Id
        auid = dp.popItem('uid') or dp.popItem('user id')

        # PWD=;
        # Password
        apwd = dp.popItem('pwd') or dp.popItem('password')

        #Failover Partner
        afailoverpartner = dp.popItem('failover partner')

        # Max Pool Size=200;
        #amaxpoolsize=dp.popItem('max pool size')

        # Connection Timeout=20;
        aconnectiontimeout = storageutil.getStrAsInt(dp.popItem('connection timeout') or dp.popItem('connect timeout'), 0)
        aclass.ConnectionTimeout[OID] = aconnectiontimeout

        # Persist Security Info=True
        #apersistsecurityinfo=dp.popItem('persist security info')

        # Trusted_Connection=True

        # MultipleActiveResultSets
        # Integrated Security
        # Asynchronous Processing
        # Packet Size
        # Column Encryption Setting
        # Current Language
        # Network Address
        # Network Library
        # Auto Translate
        # Application Name
        # Workstation ID
        aobj.ConnectionStringExtra = dp.AsString(asplit1=';', asplit2='=', asorted=1)

        hclass = aclass.DBHost.ClassOfType
        d={
           'DataBaseHost':aserver,
           'DataBaseUser':auid,
           'DataBasePassword':apwd,
           'DataBaseFailoverPartner':afailoverpartner,
        } # yapf: disable
        lhoids = hclass.Identifiers(d)
        if lhoids:
            hoid = lhoids[0]
        else:
            hoid = hclass.AddObject(arangeobject=aobj)
            hobj = hclass[hoid]
            hobj.DataBaseHost = aserver
            hobj.DataBaseUser = auid
            hobj.DataBasePassword = apwd
            hobj.DataBaseFailoverPartner = afailoverpartner
            if not hobj.DataBaseRelease:
                hobj.DataBaseRelease = [4, aclass.DataBaseRelease.ClassOfType.CID]    # ms sql 2016

        aobj.DBHost = [hoid, hclass.CID]

    def DBAccessMoveHosts(self):
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DBAccess']
        for aoid in aclass:
            self.DBAccessUnParseConnectionString(aclass, aoid)

    def CheckDBAccessObj(self, aobj, verbose=0):
        aconnectionstring = dbaccess.GetConnectionString(aobj, agetifdeactivated=1, aconnectiontimeout=2)
        status = 'none'
        adt1 = time.clock()
        if aconnectionstring:
            werr = 0
            try:
                aadoutil = ADOLibInit.ADOUtil(aconnectionstring, aservercursor=0, acnt=1, acominitialize=1, aconnectiontimeout=2, acommandtimeout=3)
                if aadoutil:
                    ars = aadoutil.GetRS('select 123 as result;')
                    anum = aadoutil.GetRSValueAsStr(ars, 'result', astype=1)
                    if anum != 123:
                        werr = 1
                    aadoutil.CloseRS(ars)
                    aadoutil.Close()
            except:
                werr = 1
            if werr:
                dbaccess.RegisterConnectionError(aobj, aforce=1)
                status = 'bad'
            else:
                dbaccess.RegisterConnectionOK(aobj)
                status = 'ok'
        adt2 = time.clock()
        if verbose:
            print aobj.OID, status, adt2 - adt1, dbaccess.GetConnectionName(aobj)
        return werr

    def CheckDBAccess(self, verbose=0):
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DBAccess']
        aobj = aclass.GetFirstObject()
        while aobj:
            self.CheckDBAccessObj(aobj, verbose=verbose)
            aobj.Next()

    def CheckDBAccessByWWWMenuStruct(self, wobj, verbose=0):
        if not wobj['SGIsDisabled']:
            aobj = wobj.DBAccess
            while aobj:
                self.CheckDBAccessObj(aobj, verbose=verbose)
                aobj.Next()
            aobj = wobj.DBAccessPublic
            while aobj:
                self.CheckDBAccessObj(aobj, verbose=verbose)
                aobj.Next()

    def CheckDBAccessByProject(self, pobj, verbose=0):
        if not pobj['SGIsDisabled']:
            aobj = pobj.DBAccess
            while aobj:
                self.CheckDBAccessObj(aobj, verbose=verbose)
                aobj.Next()
            aobj = pobj.DBAccessPublic
            while aobj:
                self.CheckDBAccessObj(aobj, verbose=verbose)
                aobj.Next()
            wobj = pobj.WWWMenuStruct
            while wobj:
                self.CheckDBAccessByWWWMenuStruct(wobj, verbose=verbose)
                wobj.Next()

    def CheckDBAccessByStruct(self, verbose=0):
        pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        pobj = pclass.GetFirstObject()
        while pobj:
            self.CheckDBAccessByProject(pobj, verbose=verbose)
            pobj.Next()

    def MethodsCorrectBackTicks(self):
        d = {}
        apatt = re.compile('(\`.*?\`)', re.S + re.M)
        aident = re.compile('^[\`a-zA-Z0-9\.]+$')
        aident2 = re.compile('^[\`a-zA-Z0-9\.\_\[\]\(\)]+$')
        aident3 = re.compile('''^[\`a-zA-Z0-9\.\_\[\]\(\)\'\,]+$''')
        aident4 = re.compile('''^[\`a-zA-Z0-9\.\_\[\]\(\)\'\,\+\-\*\:]+$''')
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_ICORMethod']
        alen = 0
        aobj = aclass.GetFirstObject()
        while aobj:
            if aobj.OID in [793, 373]:
                aobj.Next()
                continue
            s = aobj.aMethodText
            alen = alen + len(s)
            l = apatt.findall(s)
            ws = 0
            for sr in l:
                w = 1
                if sr.find(chr(10)) >= 0:
                    w = 0
                #elif not aident.match(sr):
                #   w=0
                #elif not aident2.match(sr):
                #   w=0
                #elif not aident3.match(sr):
                #   w=0
                #elif not aident4.match(sr):
                #   w=0
                if w:
                    ws = 1
                    d[sr] = aobj.OID
                    #s=s.replace(sr,'str('+sr[1:-1]+')')
            #if ws:
            #   aobj.aMethodText=s
            aobj.Next()
        l = d.keys()
        l.sort()
        for s in l[:500]:
            print d[s], s, 'str(' + s[1:-1] + ')'
        print len(l)

    def RemoveUnusedItems(self, aclass, acheckclassfunc=None, acheckobjfunc=None, UID=0):
        print 'ClASS: %s' % aclass.ClassPath
        doids = {}
        lfields = aclass.GetReferencingFields()
        for afield in lfields:
            if acheckclassfunc:
                if not acheckclassfunc(afield.ClassItem):
                    continue
            #print '  ',afield.CID,afield.ClassItem.ClassPath,afield.Name
            for aoid in afield.ClassItem:
                arefs = afield.GetRefList(aoid)
                for boid, bcid in arefs.refs:
                    doids[boid] = 1
        lret = []
        for aoid in aclass:
            if acheckobjfunc:
                aobj = aclass[aoid]
                if not acheckobjfunc(aobj):
                    continue
            if not doids.has_key(aoid):
                lret.append(aoid)
        return lret

    def RemoveUnusedItemsCheckClassFuncSecurity(self, aclass):
        for bclass in self.ignoredclasses:
            if bclass.CID == aclass.CID:
                return 0
        return 1

    def RemoveUnusedItemsCheckObjFuncSecurity(self, aobj):
        if aobj.Category == 'ICOR':
            return 0
        return 1

    def SecurityRemoveUnusedItems(self):
        UID = 0
        iclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_GroupItemAccessLevel']
        uclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_GroupAccessLevel']
        if 1:
            lclasses = [
            #['CLASSES_System_GroupAccessLevel',['CLASSES_System_Group','CLASSES_System_SystemDictionary_ProfileGroup']],
                ['CLASSES_System_GroupItemAccessLevel', ['CLASSES_System_Group', 'CLASSES_System_SystemDictionary_ProfileGroup']], ]
            for classpath, lignoredclasses in lclasses:
                aclass = ICORInterface.aICORDBEngine.Classes[classpath]
                self.ignoredclasses = []
                for bclasspath in lignoredclasses:
                    bclass = ICORInterface.aICORDBEngine.Classes[bclasspath]
                    self.ignoredclasses.append(bclass)
                ldoids = self.RemoveUnusedItems(aclass, acheckclassfunc=self.RemoveUnusedItemsCheckClassFuncSecurity, acheckobjfunc=self.RemoveUnusedItemsCheckObjFuncSecurity)
                for ioid in ldoids:
                    iname = iclass.Name[ioid]
                    uoid = uclass.Name.Identifiers(iname)
                    if uoid > 0:
                        uclass.DeleteObject(uoid)
                    iclass.DeleteObject(ioid)
                print 'Deleted items:', aclass.ClassPath, len(ldoids)
        if 1:
            gclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_Group']
            lclasses = [
            #['CLASSES_System_GroupAccessLevel',['CLASSES_System_Group','CLASSES_System_SystemDictionary_ProfileGroup']],
                ['CLASSES_System_Group', []], ]
            for classpath, lignoredclasses in lclasses:
                aclass = ICORInterface.aICORDBEngine.Classes[classpath]
                self.ignoredclasses = []
                ldoids = self.RemoveUnusedItems(aclass)
                for ioid in ldoids:
                    gname = aclass.Name[ioid]
                    #print ioid,storageutil.CP1250_To_ASCII_Default(gname)
                    aclass.DeleteObject(ioid)
                print 'Deleted items:', aclass.ClassPath, len(ldoids)

    def CheckNewAPI(self):
        UID = 0
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_Security_OIDRange']
        wclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
        if 0:
            sv = 'UM'
            aoid = 999
            while aoid >= 0:
                aoid, sv, v = aclass.Name.GetNextValue(sv)
                print aoid, sv, v
        if 0:
            sv = 'UM'
            aoid = 999
            while aoid >= 0:
                aoid, sv, v = aclass.Name.GetPrevValue(sv)
                print aoid    #,sv,v
        if 0:
            sv = 65500
            aoid = 999
            while aoid >= 0:
                aoid, sv, v = aclass.IDMin.GetNextValueInt(sv)
                print aoid, sv, v
        if 0:
            sv = 65500
            aoid = 999
            while aoid >= 0:
                aoid, sv, v = aclass.IDMin.GetPrevValueInt(sv)
                print aoid, sv, v
        if 0:
            for aoid in [10, 11, 1000]:
                print aclass.GetObjectValue(aoid)
        if 0:
            aoid = 11000
            wobj = wclass[aoid]
            wrefs = wclass.TabeleZrodlowe.GetRefList(aoid)
            for lsearch in [
               ['Strony opisowe','Strony opisowe - '],
               ['rejestr zmian','rejestr zmian - '],
               [storageutil.UTF8_To_CP1250('wykazy - spółki')],
               ['xxxxx','yyyy','zzzzzzzz'],
            ]: # yapf: disable
                apos, afind = wrefs.FindRefByValue('Nazwa', lsearch, assubstringsearch=1)
                print apos, afind, lsearch
        if 1:
            tclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_TypPolaDotyczy']
            s = 'Słownik użytkownika'
            toid = tclass.Opis.Identifiers(s)
            print 'find value:', toid

    def ModernizeWebsite(self, asitename=None, wobj=None):
        ret = 1
        wclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
        if wobj is None:
            woid = wclass.Nazwa.Identifiers(asitename)
            if woid < 0:
                return ret
            wobj = wclass[woid]
        else:
            wobj = wobj.AsObject()
        acmsname = wobj.Nazwa
        print acmsname

        afname = startutil.GetLogTempFileName('modernize', aprefix=acmsname, aext='txt')
        print 'modernize raport in file: %s' % afname
        alog = startutil.MLog(afname, aconsole=0)

        awwweditor = {}
        #awwweditor.RegisterField('aCMS_NAME',adisplayed='Nazwa CMS/Aplikacji',atype=mt_String,avalue=aCMS_NAME)
        awwweditor['aCMS_NAME'] = acmsname

        atitle = wobj.Title
        if not atitle:
            atitle = acmsname

        #awwweditor.RegisterField('aPRETTY_CMS_NAME',adisplayed='Nazwa CMS/Aplikacji długa',atype=mt_String,avalue=avalue)
        awwweditor['aPRETTY_CMS_NAME'] = atitle

        #awwweditor.RegisterField('aHEAD_TITLE',adisplayed='Tytuł',atype=mt_String,avalue=avalue)
        awwweditor['aHEAD_TITLE'] = atitle

        mobj = wobj.MetaTemplate
        if mobj:
            #awwweditor.RegisterField('aMETA_AUTHOR',adisplayed='Autor',atype=mt_String,avalue=avalue)
            awwweditor['aMETA_AUTHOR'] = mobj.Author

            #awwweditor.RegisterField('aMETA_DESCRIPTION',adisplayed='Opis Meta',atype=mt_String,avalue=avalue)
            awwweditor['aMETA_DESCRIPTION'] = mobj.Description

            #awwweditor.RegisterField('aMETA_KEYWORDS',adisplayed='Słowa kluczowe',atype=mt_String,avalue=avalue)
            awwweditor['aMETA_KEYWORDS'] = mobj.Keywords

        #avalue=bwwweditor.get('aEMAIL','<email>')
        #if mobj:
        #   aUserClass=aICORDBEngine.Classes['CLASSES_System_User']
        #   uoid=aUserClass.UserName.Identifiers(aCMS_NAME+'Admin')
        #   if uoid>=0:
        #      avalue=aUserClass.VCFEMail[uoid]
        #awwweditor.RegisterField('aEMAIL',adisplayed='e-mail do Admina',atype=mt_String,avalue=avalue)
        awwweditor['aEMAIL'] = startutil.appconfig.IParams['modernize_admin_email']

        avalue = ''
        hobj = wobj.AppPaths
        if hobj:
            avalue = hobj.AdresZewnetrznyWWW
        #awwweditor.RegisterField('aHOME_PAGE_ADDRESS',adisplayed='Nazwa w DNS',atype=mt_String,avalue=avalue)
        awwweditor['aHOME_PAGE_ADDRESS'] = avalue

        dparams={
           'CreateDirs':1,
           'CopyFiles':1,
           'CreateSecurity':1,
           'ImpersonateAdmin':1,
           'CreateCMS10':1,
           'CreateObjectsTables10':1,
           'CreateObjectsTables20':1,
           'CreatePlugin_BibliotekaStandardowa':0,
           'CreatePlugin_ModulBezpieczenstwa':0,
           'CreatePluginTables':1,
           'CreatePlugin_Abstrakty':1,
           'CreatePlugin_Kalendarium':1,
           'CreatePlugin_Geolokalizacja':1,
           'CreatePlugin_Wyszukiwarka':1,
           'CreatePlugin_Multimedia':1,
           'CreatePlugin_KategorieTresci':1,
           'CreatePlugin_TabeleTresci':1,
           'CreatePlugin_NarzedziaSEO':1,
           'CreatePlugin_WWWSite':1,
           'CreateRozdzialy':0,
        } # yapf: disable

        abuilder = appcmsbuilder.AppCMSBuilder(wobj.Projekt, file=alog, awwweditor=awwweditor, dparams=dparams)
        if abuilder.Validate(anew=0):
            return ret
        try:
            abuilder.Process()
            ret = 0
        except:
            import traceback
            traceback.print_exc()
        abuilder.Dump()
        return ret

    def ModernizeWebsites(self, lexclude=None):
        if lexclude is None:
            lexclude = []
        pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        pobj = pclass.GetFirstObject()
        while pobj:
            if not pobj['SGIsDisabled']:
                wobj = pobj.WWWMenuStruct
                while wobj:
                    if not wobj['SGIsDisabled']:
                        acmsname = wobj.Nazwa
                        if acmsname not in lexclude:
                            print pobj.OID, pobj.Nazwa, wobj.OID, acmsname
                            self.ModernizeWebsite(asitename=acmsname, wobj=wobj)
                    wobj.Next()
            pobj.Next()

    def MethodsSave(self):
        pclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_ICORMethod']
        pobj = pclass.GetFirstObject()
        while pobj:
            pobj.Class.OnFieldChange('aMethodText', pobj.OID)
            pobj.Next()

    def RemoveFieldEmptyReferences(self, acpath, afieldname):
        bclass = ICORInterface.aICORDBEngine.Classes[acpath]
        bfield = bclass.FieldsByName(afieldname)
        rclass = bfield.ClassOfType
        boid = bclass.FirstObject()
        while boid >= 0:
            s, w = '', 0
            arefs = bfield.GetRefList(boid)
            while arefs:
                if rclass.ObjectExists(arefs.OID):
                    s = s + str(arefs.OID) + ':' + str(rclass.CID) + ':'
                else:
                    w = 1
                arefs.Next()
            if w:
                bfield[boid] = s
            boid = bclass.NextObject(boid)

    def RemoveEmptyReferences(self):
        lc=[
           ['CLASSES_System_Dialog_ProjectAdd','DBAccess'],
           ['CLASSES_System_Startup','ProfileGroup'],
           ['CLASSES_System_GroupAccessLevel','Users'],
           ['CLASSES_System_Dialog_ProfileAdd','WorkflowHTTPServerParameters'],
           ['CLASSES_System_User','Groups'],
           ['CLASSES_Library_NetBase_WWW_Dictionary_Menu','Profile'],
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_PluginSkin','Template'],
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Component_Effects','Skins'],
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_EffectSkin_EventValue','Effect'],
           ['CLASSES_Library_NetBase_WWW_Dictionary_Menu','AccessLevel'],
           ['CLASSES_Library_NetBase_WWW_Dictionary_Menu','WorkflowMenuStruct'],
           ['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DaneRodzajowe_EffectKind','Efekty'],
        ] # yapf: disable
        for acpath, afieldname in lc:
            self.RemoveFieldEmptyReferences(acpath, afieldname)

    def LoadUsers(self, aprofilename, afilename):
        self.secprofile = ICORSecurity.ICORSecurityProfile()
        ret = self.secprofile.SetByProfileName(aprofilename)
        if not ret:
            print 'brak profilu: %s' % aprofilename
            return
        auserpath = ICORInterface.FilePathAsSystemPath('%ICOR%/' + afilename)
        agroupspath = ICORInterface.FilePathAsSystemPath('%ICOR%/groups_' + afilename)
        print auserpath
        fin = storageutil.OpenText(auserpath)
        du = json.load(fin)
        fin.close()
        print agroupspath
        fin = storageutil.OpenText(agroupspath)
        dg = json.load(fin)
        fin.close()
        dgs = {}
        for k, v in dg.items():
            lv = [storageutil.UTF8_To_CP1250(s) for s in v]
            ur = ICORSecurity.GetStringAsAccessLevelRefs(lv, ausergroups=1)
            dgs[k] = ur.AsString()
        for k, l in du.items():
            for dui in l:
                ret = self.secprofile.AddUser(storageutil.UTF8_To_CP1250(dui['login']), storageutil.UTF8_To_CP1250(dui['password']), dgs[dui['dostep']], storageutil.UTF8_To_CP1250(dui['imie']), storageutil.UTF8_To_CP1250(dui['nazwisko']), storageutil.UTF8_To_CP1250(dui.get('email', '')))
                if not ret:
                    print 'Nie można utworzyć użytkownika: %s' % storageutil.UTF8_To_CP1250(dui['login'])

    def SearchUsers(self, astr=''):
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_User']
        l = aclass.GetObjectsValue(fields=set(['UserName', 'VCFFirstName', 'VCFLastName', 'VCFEMail', 'VCFPhone', 'Description', 'AccountDisabled', 'WWWDisabled']), autfconvert=0, aslist=1)
        aw = 1
        bstr, istr = '', ''
        if astr and astr != '*':
            aw = 0
            if astr[:1] == '#':
                istr = astr[1:]
            else:
                bstr = astr
        for du in l:
            w = aw
            if bstr:
                skey = ' '.join([du.get('UserName', ''), du.get('VCFFirstName', ''), du.get('VCFLastName', ''), du.get('VCFEMail', ''), du.get('VCFPhone', ''), du.get('Description', '')])
                if bstr.lower() in skey.lower():
                    w = 1
            elif istr:
                skey = str(du.get('_oid', ''))
                if istr in skey:
                    w = 1
            if w:
                print du

    def SetUserPassword(self, suser, spassword):
        if suser[:1] == '#':
            auid = storageutil.getStrAsInt(suser[1:], -1)
            if auid < 0:
                print 'nieprawidlowy UID'
                return
            auser = ICORSecurity.ICORSecurityUser(auid=auid)
        else:
            auser = ICORSecurity.ICORSecurityUser(aname=suser, abyname=1)
        if not auser.UserExists:
            print 'brak uzytkownika'
            return
        auser.Password = spassword
        print 'haslo zmienione:', auser.Password

    def HistoryLoad(self):
        adt1 = time.clock()
        ahistorypath = ICORInterface.FilePathAsSystemPath('%ICOR%//db/_history')
        for adir in os.listdir(ahistorypath):
            adirpath = os.path.join(ahistorypath, adir)
            if adir[:1] == '_' or not os.path.isdir(adirpath):
                continue
            adirpathout = os.path.join(ahistorypath, '_' + adir)
            atablename = storageutil.MakeIdentifier(adir, adefaultprefix='', alower=1, acapitalize=0, aproper=1)
            print 'Processing:', adirpath, 'table:', atablename
            if not os.path.exists(adirpathout):
                os.makedirs(adirpathout)
            self.aICORStarter.aICORDBData.struct.CreateHistoryTable(atablename)

            for mdir in os.listdir(adirpath):
                mdirpath = os.path.join(adirpath, mdir)
                if not os.path.isdir(mdirpath):
                    continue
                mfdimport.ImportDir(self.aICORStarter.aICORDBData, mdirpath, acopy=1, asql=0, ahistory=1)



    def HistoryStore(self):
        adt1 = time.clock()
        ahistorypath = ICORInterface.FilePathAsSystemPath('%ICOR%//db/_history')
        for adir in os.listdir(ahistorypath):
            adirpath = os.path.join(ahistorypath, adir)
            if adir[:1] == '_' or not os.path.isdir(adirpath):
                continue
            adirpathout = os.path.join(ahistorypath, '_' + adir)
            atablename = storageutil.MakeIdentifier(adir, adefaultprefix='', alower=1, acapitalize=0, aproper=1)
            print 'Processing:', adirpath, 'table:', atablename
            if not os.path.exists(adirpathout):
                os.makedirs(adirpathout)
            self.aICORStarter.aICORDBData.struct.CreateHistoryTable(atablename)
            self.aICORStarter.aICORDBData.struct.ClearHistoryTableTemp(atablename)

            for mdir in os.listdir(adirpath):
                mdirpath = os.path.join(adirpath, mdir)
                if not os.path.isdir(mdirpath):
                    continue
                mfdimport.LoadDBDir(self.aICORStarter.aICORDBData, mdirpath, ahistory=1, atablename=atablename)

            self.aICORStarter.aICORDBData.struct.StoreHistoryTableTemp(atablename)
        adt2 = time.clock()
        print 'History store in %0.2f secs' % (adt2 - adt1, )
