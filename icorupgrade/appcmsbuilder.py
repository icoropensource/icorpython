# -*- coding: utf-8 -*-
import sys
import os
import time
import traceback
import datetime
import re

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.icorsecurity as ICORSecurity
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.wwwserver.icorwwwinterface as ICORWWWInterface
import icordbmain.dbaccess as dbaccess
import icordbmain.adoutil as ADOLibInit

USER_PASSWORD_PREFIX = 'abc'


class ProjectCMSBuilder(object):

    def __init__(self, UID=0, file=None, awwweditor=None, dparams=None):
        self.UIDs = [UID, ]
        self.file = file
        if dparams is None:
            dparams = {}
        self.params = dparams
        self.aPROFILE_NAME = awwweditor.get('ProjectName', '')
        self.aDBAccess = awwweditor.get('DBAccess', None)
        self.aDBAccessPublic = awwweditor.get('DBAccessPublic', None)
        self.aOIDRange = awwweditor.get('OIDRange', None)
        self.aUIDRange = awwweditor.get('UIDRange', None)
        self.isError = 0
        self.secprofile = None
        self.PClass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        self.WClass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']

    def GetUID(self):
        if not self.UIDs:
            return 0
        return self.UIDs[len(self.UIDs) - 1]

    def WriteError(self, s):
        self.isError = 1
        if self.file:
            self.file.write('<h2 style="color:#ff0000">%s</h2>' % s)

    def WriteInfo(self, s):
        if self.file:
            self.file.write('<h3>%s</h3>' % s)

    def Impersonate(self, auid):
        self.UIDs.append(auid)

    def RevertToSelf(self):
        if self.UIDs:
            self.UIDs.pop()

    def start_OBJECT(self, sclass, aoid=-1, fieldname='', fieldvalue='', minoid=-1, check=0, parentrefs=None, searchinrefs=0, aoidrangesobj=None):
        self.objectclass = ICORInterface.aICORDBEngine.Classes[sclass]
        if self.objectclass is None:
            self.WriteError('nieznana klasa: %s' % sclass)
            return
        fieldsearch = fieldvalue
        if type(fieldvalue) == type([]):
            fieldvalue = fieldsearch[0]
        UID = self.GetUID()
        if (aoid < 0) and fieldname and fieldvalue:
            afield = self.objectclass.FieldsByName(fieldname)
            if afield is None:
                self.WriteError('nieznane pole: %s - %s' % (sclass, fieldname))
                return
            if not searchinrefs:
                aoid = afield.Identifiers(fieldvalue)
            else:
                apos, afind = parentrefs.FindRefByValue(fieldname, fieldsearch, assubstringsearch=1)
                if afind:
                    aoid = parentrefs.refs[apos][0]
        self.objectisnew = 0
        if (minoid >= 0) and fieldname and (aoid < 0):
            aoid = minoid
            while self.objectclass.ObjectExists(aoid):
                aoid = aoid + 1
            if not check:
                self.objectclass.CreateObjectByID(aoid)
                self.WriteInfo('nowy obiekt min: %s - %d' % (sclass, aoid))
                self.objectisnew = 1
        if aoid < 0 and not check:
            aoid = self.objectclass.AddObject(aoidrangesobj=aoidrangesobj)
            self.objectisnew = 1
            self.WriteInfo('nowy obiekt: %s - %d' % (sclass, aoid))
        self.objectoid = aoid
        ret = None
        if aoid >= 0:
            ret = self.objectclass[aoid]
            if parentrefs is not None:
                parentrefs.AddRef(aoid, anoduplicates=1, store=1)
        return ret

    def start_SECURITYPROFILE(self, aname):
        self.secprofile = ICORSecurity.ICORSecurityProfile()
        ret = self.secprofile.SetByProfileName(aname)
        if not ret:
            self.secprofile.AddProfile(aname)
            self.WriteInfo('nowy profil bezpieczenstwa: %s' % aname)
        else:
            self.WriteInfo('aktualny profil bezpieczenstwa: %s' % aname)

    def start_OIDRANGE(self, aname):
        return self.secprofile.UpdateOIDRange(aname, asobject=1)

    def start_UIDRANGE(self, aname):
        return self.secprofile.UpdateUIDRange(aname, asobject=1)

    def start_SECURITYITEMGROUP(self, groupname, groupaccesslevel=0, basegroups=None, groupcategory='', groupkind='', parentrefs=None):
        sobj = self.start_OBJECT('CLASSES_System_GroupItemAccessLevel', fieldname='Name', fieldvalue=groupname, check=1, parentrefs=parentrefs)
        if sobj:
            return sobj.OID
        if not basegroups:
            basegroups = [groupname[0], ]
        aoid = self.secprofile.UpdateItemGroup(groupname[0], groupaccesslevel, basegroups, acategory=groupcategory, akind=groupkind)
        if parentrefs is not None:
            parentrefs.AddRef(aoid, anoduplicates=1, store=1)
        return aoid

    def start_SECURITYUSERGROUP(self, groupname, groupaccesslevel=0, basegroups=None, groupcategory='', groupkind='', abasenameoid=-1):
        if abasenameoid >= 0:
            aname = self.secprofile.ItemGroupClass.Name[abasenameoid]
            aoid = self.secprofile.UserGroupClass.Name.Identifiers(aname)
            if aoid >= 0:
                return aoid
        if not basegroups:
            basegroups = [groupname[0], ]
        return self.secprofile.UpdateUserGroup(groupname[0], groupaccesslevel, basegroups, acategory=groupcategory, akind=groupkind)

    def start_USER(self, username, usergroups, userpassword='', userfirstname='', userlastname='', useremail='', adescription='', useruid=-1, userhash=0, useroidranges=None, userkeepoldpassword=0):
        agroups = ICORSecurity.GetStringAsAccessLevelRefs(usergroups, self.secprofile.UserGroupClass)
        ret = self.secprofile.AddUser(username, userpassword, agroups.AsString(), userfirstname, userlastname, useremail, aphone='', auid=useruid, apasswordhash=userhash, loidranges=useroidranges, akeepoldpassword=userkeepoldpassword, adescription=adescription)
        if not ret:
            self.WriteError('Nie można utworzyć użytkownika: %s' % username)

    def ValidateProject(self):
        if not ICORUtil.IsIdentifier(self.aPROFILE_NAME, asimple=1):
            self.WriteError('Nazwa CMS/Aplikacji nie jest identyfikatorem')
        if not self.aDBAccess:
            self.WriteError('Brak przypisanego dostepu do bazy danych')
        elif not self.aDBAccess.DataBaseName:
            self.WriteError('Brak nazwy bazy danych')
        if not self.aOIDRange:
            self.WriteError('Brak przypisanego zakresu OID')
        if not self.aUIDRange:
            self.WriteError('Brak przypisanego zakresu UID')
        return self.isError

    def CreateDatabase(self):
        aconnectionstring = dbaccess.GetConnectionString(self.aDBAccess, agetifdeactivated=1, aconnectiontimeout=2, adatabase='master')
        if not aconnectionstring:
            self.WriteError('Pusty connectionstring: "%s"' % (aconnectionstring, ))
            return
        werr = 0
        try:
            aadoutil = ADOLibInit.ADOUtil(aconnectionstring, aservercursor=0, acnt=1, acominitialize=1, aconnectiontimeout=2, acommandtimeout=3)
            try:
                if aadoutil:
                    adbname=startutil.GetStrEnv(self.aDBAccess.DataBaseName)
                    wcreate = 0
                    rs = aadoutil.GetRS("SELECT Name,database_id FROM sys.databases WHERE name = '%s';" % (adbname, ))
                    if rs.EOF or rs.BOF:
                        wcreate = 1
                    aadoutil.CloseRS(rs)
                    if wcreate:
                        
                        for asql in [
                           'create database %s collate Polish_CI_AS;'%(adbname,),
                           "EXEC %s.dbo.sp_fulltext_database @action = 'enable'"%(adbname,),
                           'ALTER DATABASE %s SET AUTO_SHRINK ON'%(adbname,),
                           'ALTER DATABASE %s SET AUTO_UPDATE_STATISTICS ON'%(adbname,),
                           'ALTER DATABASE %s SET RECURSIVE_TRIGGERS OFF'%(adbname,),
                           'ALTER DATABASE %s SET AUTO_UPDATE_STATISTICS_ASYNC ON '%(adbname,),
                        ]: # yapf: disable
                            aadoutil.Execute(asql)
                else:
                    werr = 1
            finally:
                aadoutil.Close()
        except:
            werr = 1
        if werr:
            self.WriteError('Brak polaczenia do DB: "%s"' % (aconnectionstring, ))

    def CreateSecurityProfile(self):
        self.aSECURITY_PROFILE_NAME = self.aPROFILE_NAME
        self.start_SECURITYPROFILE(self.aSECURITY_PROFILE_NAME)
        self.aSECURITY_PROFILE_OID = self.start_OBJECT('CLASSES_System_SystemDictionary_ProfileGroup', fieldname='Name', fieldvalue=self.aSECURITY_PROFILE_NAME)

        robj = self.aOIDRange.AsObject()
        while robj:
            self.secprofile.UpdateOIDRange(robj.Name, robj.OID)
            robj.Next()
        robj = self.aUIDRange.AsObject()
        while robj:
            self.secprofile.UpdateUIDRange(robj.Name, robj.OID)
            robj.Next()

        self.aSECURITY_ITEM_GROUP_Admin_OID = self.start_SECURITYITEMGROUP(['%s - Admin' % self.aSECURITY_PROFILE_NAME, ], parentrefs=self.aPROJECT_OID.AccessLevelView.Refs)
        self.aSECURITY_ITEM_GROUP_User_OID = self.start_SECURITYITEMGROUP(['%s - User' % self.aSECURITY_PROFILE_NAME, ], groupaccesslevel=4, parentrefs=self.aPROJECT_OID.AccessLevelView.Refs)
        self.aSECURITY_USER_GROUP_Admin_OID = self.start_SECURITYUSERGROUP(['%s - Admin' % self.aSECURITY_PROFILE_NAME, ], abasenameoid=self.aSECURITY_ITEM_GROUP_Admin_OID)
        self.aSECURITY_USER_GROUP_User_OID = self.start_SECURITYUSERGROUP(['%s - User' % self.aSECURITY_PROFILE_NAME, ], groupaccesslevel=4, abasenameoid=self.aSECURITY_ITEM_GROUP_User_OID)
        auid = self.GetUID()
        uobj = self.secprofile.UserClass[auid]
        uobj.Groups.Refs.AddRef(self.aSECURITY_USER_GROUP_Admin_OID, anoduplicates=1, store=1)
        uobj.Groups.Refs.AddRef(self.aSECURITY_USER_GROUP_User_OID, anoduplicates=1, store=1)
        ugnameadmin = self.secprofile.UserGroupClass.Name[self.aSECURITY_USER_GROUP_Admin_OID]
        ugnameuser = self.secprofile.UserGroupClass.Name[self.aSECURITY_USER_GROUP_User_OID]
        self.start_USER('%sAdmin' % self.aPROFILE_NAME, [ugnameadmin, ugnameuser, 'User Manager', ], userpassword=USER_PASSWORD_PREFIX + '%sAdmin' % self.aPROFILE_NAME, userfirstname='', userlastname='', useremail='', adescription='', useruid=-1, userhash=0, useroidranges=[], userkeepoldpassword=1)
        self.start_USER('%sUser' % self.aPROFILE_NAME, [ugnameuser, ], userpassword=USER_PASSWORD_PREFIX + '%sUser' % self.aPROFILE_NAME, userfirstname='', userlastname='', useremail='', adescription='', useruid=-1, userhash=0, useroidranges=[], userkeepoldpassword=1)
        self.aSECURITY_PROFILE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)

    def CreateAddin(self, aaddinname, anotemplate=0, aaddinvars=None):
        aaddin = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_AddIns_AddIn', fieldname='Nazwa', fieldvalue=aaddinname, parentrefs=self.aPROJECT_OID.AddIns.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        if self.objectisnew:
            aaddin.Nazwa = aaddinname
            if aaddinvars:
                aaddin.AddInVars = aaddinvars
            if not anotemplate:
                self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_AddIns_AddInTemplate', fieldname='Nazwa', fieldvalue=aaddinname, parentrefs=aaddin.AddInTemplate.Refs)
        aaddin.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        return aaddin

    def CreateProjectAddins(self):
        UID = self.GetUID()
        self.aADDIN_BIBLIOTEKA_OID = self.CreateAddin('Biblioteka standardowa')
        self.aADDIN_BIBLIOTEKA_OID = self.CreateAddin('Listy wysyłkowe')
        self.aADDIN_BIBLIOTEKA_OID = self.CreateAddin('Historia dostępu do rekordów')

    def CreateSecurityMap(self):
        UID = self.GetUID()
        asecuritymap = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_Security_SecurityMap', fieldname='Nazwa', fieldvalue=self.aPROFILE_NAME, parentrefs=self.aPROJECT_OID.SecurityMap.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        if self.objectisnew:
            asecuritymap.Nazwa = self.aPROFILE_NAME

    def CreateSzablonGenerowania(self):
        UID = self.GetUID()
        self.aSZABLON_GENEROWANIA_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SzablonGenerowania', fieldname='Nazwa', fieldvalue=self.aPROFILE_NAME, parentrefs=self.aPROJECT_OID.SzablonyGenerowania.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        if self.objectisnew:
            self.aSZABLON_GENEROWANIA_OID.Nazwa = self.aPROFILE_NAME
            self.aSZABLON_GENEROWANIA_OID.GenerujSP = '1'
            self.aSZABLON_GENEROWANIA_OID.GenerujVar = '1'
            self.aSZABLON_GENEROWANIA_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)

    def CreateProject(self):
        self.aPROJECT_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt', fieldname='Nazwa', fieldvalue='%s' % self.aPROFILE_NAME, aoidrangesobj=self.aOIDRange)
        if 1 or self.objectisnew:
            self.aPROJECT_OID.Nazwa = self.aPROFILE_NAME
            self.aPROJECT_OID.AppPath = 'appdata/%s/crm' % (self.aPROFILE_NAME, )
            self.aPROJECT_OID.BaseNameModifier = 'V01_'
            self.aPROJECT_OID.WWWDataPath = '%%ICOR%%/WWWData/%s' % (self.aPROFILE_NAME, )
            self.aPROJECT_OID.WWWDataPathUserFiles = '/%sFiles' % (self.aPROFILE_NAME, )
            self.aPROJECT_OID.WWWDataPathUserImages = '/%sImages' % (self.aPROFILE_NAME, )
            self.aPROJECT_OID.DBAccess = self.aDBAccess
            if self.aDBAccessPublic:
                self.aPROJECT_OID.DBAccessPublic = self.aDBAccessPublic
            else:
                self.aPROJECT_OID.DBAccessPublic = self.aDBAccess
            self.aPROJECT_OID.ProjectVars = 'aCgiScriptPath=\naMSSQLVersion=2008\n\n'
            self.aPROJECT_OID.OIDRange = self.aOIDRange

    def CreateProjectSetup(self):
        self.CreateProjectAddins()
        self.CreateSecurityMap()
        self.CreateSzablonGenerowania()

    def ProcessProject(self):
        if not self.isError:
            self.CreateDatabase()
        if not self.isError:
            self.CreateProject()
        if not self.isError:
            self.CreateSecurityProfile()
        if not self.isError:
            self.CreateProjectSetup()

    def Dump(self):
        alocalvars = ['aPROFILE_NAME', ]
        for alocalvar in alocalvars:
            self.file.write('<h3>%s: %s</h3>' % (alocalvar, self.__dict__[alocalvar]))


class AppCMSBuilder(ProjectCMSBuilder):

    def __init__(self, pobj, UID=0, file=None, awwweditor=None, dparams=None):
        super(self.__class__, self).__init__(UID=UID, file=file, awwweditor=awwweditor, dparams=dparams)
        self.ProjectObj = pobj.AsObject()
        self.aPROFILE_NAME = self.ProjectObj.Nazwa
        self.aCMS_NAME = awwweditor['aCMS_NAME']
        self.aPRETTY_CMS_NAME = awwweditor['aPRETTY_CMS_NAME']
        self.aHEAD_TITLE = awwweditor['aHEAD_TITLE']
        self.aMETA_AUTHOR = awwweditor.get('aMETA_AUTHOR', '')
        self.aMETA_DESCRIPTION = awwweditor.get('aMETA_DESCRIPTION', '')
        self.aMETA_KEYWORDS = awwweditor.get('aMETA_KEYWORDS', '')
        self.aEMAIL = awwweditor['aEMAIL']
        self.aHOME_PAGE_ADDRESS = awwweditor['aHOME_PAGE_ADDRESS']

    def Validate(self, anew=1):
        if not ICORUtil.IsIdentifier(self.aCMS_NAME, asimple=1):
            self.WriteError('Nazwa CMS/Aplikacji nie jest identyfikatorem')
        if anew:
            if self.WClass.Nazwa.Identifiers(self.aCMS_NAME) >= 0:
                self.WriteError('Nazwa CMS/Aplikacji już jest zajęta')
        if not self.aPRETTY_CMS_NAME:
            self.WriteError('Nazwa CMS/Aplikacji długa jest nieprawidłowa')
        if not self.aHEAD_TITLE:
            self.WriteError('Tytuł jest nieprawidłowy')
        if not self.aMETA_AUTHOR:
            self.WriteError('Autor jest nieprawidłowy')
        if not self.aMETA_DESCRIPTION:
            self.WriteError('Opis Meta jest nieprawidłowy')
        if not self.aMETA_KEYWORDS:
            self.WriteError('Słowa kluczowe są nieprawidłowe')
        if not self.aEMAIL:
            self.WriteError('E-mail jest nieprawidłowy')
        if not self.aHOME_PAGE_ADDRESS:
            self.WriteError('Nazwa w DNS jest nieprawidłowa')
        return self.isError

    def CreateDirs(self):
        #<DIRCREATE path="%ICOR%/WWWMenuStruct/%CMS_NAME%" var="DIRECTORY_WWWMENUSTRUCT"/>
        #<DIRCREATE path="%DIRECTORY_WWWMENUSTRUCT%/css" />
        #<DIRCREATE path="%DIRECTORY_WWWMENUSTRUCT%/files" />
        #<DIRCREATE path="%DIRECTORY_WWWMENUSTRUCT%/images" />
        #<DIRCREATE path="%DIRECTORY_WWWMENUSTRUCT%/img" />
        #<DIRCREATE path="%DIRECTORY_WWWMENUSTRUCT%/inc" />
        #<DIRCREATE path="%DIRECTORY_WWWMENUSTRUCT%/stats" />
        #<DIRCREATE path="%DIRECTORY_WWWMENUSTRUCT%/rss" />
        pass

    def CopyFiles(self):
        #<COPYTREE src="%WWW_FILES_SOURCE%\img" dst="%DIRECTORY_WWWMENUSTRUCT%\img" />
        #<COPYTREE src="%WWW_FILES_SOURCE%\stats" dst="%DIRECTORY_WWWMENUSTRUCT%\stats" />
        #<COPYTREE src="%WWW_FILES_SOURCE%\inc" dst="%DIRECTORY_WWWMENUSTRUCT%\inc" />
        pass

    def StartSecurity(self):
        self.aSECURITY_PROFILE_NAME = ICORSecurity.GetSecurityProfileByObj(self.ProjectObj)
        if not self.aSECURITY_PROFILE_NAME:
            self.WriteError('Brak profilu bezpieczeństwa dla projektu')
            return
        self.start_SECURITYPROFILE(self.aSECURITY_PROFILE_NAME)
        self.aSECURITY_CMS_NAME = '%s - %s' % (self.aPROFILE_NAME, self.aCMS_NAME)
        self.aOIDRange = self.start_OIDRANGE(self.aSECURITY_CMS_NAME)
        self.aUIDRange = self.start_UIDRANGE(self.aSECURITY_PROFILE_NAME)
        self.aSECURITY_PROFILE_OID = self.start_OBJECT('CLASSES_System_SystemDictionary_ProfileGroup', fieldname='Name', fieldvalue=self.aSECURITY_PROFILE_NAME)

    def CreateSecurity(self):
        self.aSECURITY_ITEM_GROUP_Admin_OID = self.start_SECURITYITEMGROUP(['%s - Admin' % self.aSECURITY_CMS_NAME, ], parentrefs=self.aWWWMENUSTRUCT_OID.AccessLevelView.Refs)
        self.aSECURITY_ITEM_GROUP_User_OID = self.start_SECURITYITEMGROUP(['%s - User' % self.aSECURITY_CMS_NAME, ], groupaccesslevel=4, parentrefs=self.aWWWMENUSTRUCT_OID.AccessLevelView.Refs)
        self.aSECURITY_USER_GROUP_Admin_OID = self.start_SECURITYUSERGROUP(['%s - Admin' % self.aSECURITY_CMS_NAME, ], abasenameoid=self.aSECURITY_ITEM_GROUP_Admin_OID)
        self.aSECURITY_USER_GROUP_User_OID = self.start_SECURITYUSERGROUP(['%s - User' % self.aSECURITY_CMS_NAME, ], groupaccesslevel=4, abasenameoid=self.aSECURITY_ITEM_GROUP_User_OID)
        auid = self.GetUID()
        uobj = self.secprofile.UserClass[auid]
        uobj.Groups.Refs.AddRef(self.aSECURITY_USER_GROUP_Admin_OID, anoduplicates=1, store=1)
        uobj.Groups.Refs.AddRef(self.aSECURITY_USER_GROUP_User_OID, anoduplicates=1, store=1)
        ugnameadmin = self.secprofile.UserGroupClass.Name[self.aSECURITY_USER_GROUP_Admin_OID]
        ugnameuser = self.secprofile.UserGroupClass.Name[self.aSECURITY_USER_GROUP_User_OID]
        self.start_USER('%sAdmin' % self.aCMS_NAME, [ugnameadmin, ugnameuser, 'User Manager', ], userpassword=USER_PASSWORD_PREFIX + '%sAdmin' % self.aCMS_NAME, userfirstname='', userlastname='', useremail=self.aEMAIL, adescription='', useruid=-1, userhash=0, useroidranges=[self.aSECURITY_CMS_NAME, ], userkeepoldpassword=1)
        self.start_USER('%sUser' % self.aCMS_NAME, [ugnameuser, ], userpassword=USER_PASSWORD_PREFIX + '%sUser' % self.aCMS_NAME, userfirstname='', userlastname='', useremail='', adescription='', useruid=-1, userhash=0, useroidranges=[self.aSECURITY_CMS_NAME, ], userkeepoldpassword=1)
        self.aSECURITY_PROFILE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)

    def ImpersonateAdmin(self):
        aname = '%sAdmin' % self.aCMS_NAME
        auid = self.secprofile.UserClass.UserName.Identifiers(aname)
        if auid < 0:
            self.WriteError('Nie można impersonifikować użytkownika: %s' % aname)
            return
        self.Impersonate(auid)

    def CreateCMS10(self):
        UID = self.GetUID()
        self.StartSecurity()
        self.aWWWMENUSTRUCT_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura', fieldname='Nazwa', fieldvalue='%s' % self.aCMS_NAME, parentrefs=self.ProjectObj.WWWMenuStruct.Refs, aoidrangesobj=self.aOIDRange)
        self.aWWWMENUSTRUCT_OID.Nazwa = self.aCMS_NAME
        self.aWWWMENUSTRUCT_OID.InfoTablesSufix = str(self.aWWWMENUSTRUCT_OID.OID)
        if self.aWWWMENUSTRUCT_OID.Title == '':
            self.aWWWMENUSTRUCT_OID.Title = self.aHEAD_TITLE
        self.CreateSecurity()
        self.ImpersonateAdmin()
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DaneRodzajowe_DefaultEncoding', fieldname='IANAName', fieldvalue='utf-8', parentrefs=self.aWWWMENUSTRUCT_OID.DefaultEncoding.Refs)
        self.aWWWMENUSTRUCT_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aWWWMENUSTRUCT_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)
        self.aWWWMENUSTRUCT_OIDRANGE_OID = self.start_OBJECT('CLASSES_System_Security_OIDRange', fieldname='Name', fieldvalue=self.aSECURITY_CMS_NAME, parentrefs=self.aWWWMENUSTRUCT_OID.OIDRange.Refs)
        self.aUSER_TSQL_1_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_UserTSQL', fieldname='Nazwa', fieldvalue=['Aktualizacja rejestru zmian - %s' % self.aCMS_NAME, 'Aktualizacja rejestru zmian'], parentrefs=self.aWWWMENUSTRUCT_OID.UserTSQL.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        self.aUSER_TSQL_1_OID.Nazwa = 'Aktualizacja rejestru zmian - %s' % self.aCMS_NAME
        self.aUSER_TSQL_1_OID.ExecuteNow = '1'
        self.aAPPPATHS_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_WWWStructAppPaths', fieldname='Nazwa', fieldvalue='%s' % self.aCMS_NAME, parentrefs=self.aWWWMENUSTRUCT_OID.AppPaths.Refs, aoidrangesobj=self.aOIDRange)
        self.aAPPPATHS_OID.Nazwa = self.aCMS_NAME
        if not self.aAPPPATHS_OID.KatalogWirtualny:
            self.aAPPPATHS_OID.KatalogWirtualny = self.aCMS_NAME
        if not self.aAPPPATHS_OID.SciezkaAplikacji:
            self.aAPPPATHS_OID.SciezkaAplikacji = '%%ICOR%%/WWWMenuStruct/%s' % self.aCMS_NAME
        if not self.aAPPPATHS_OID.AdresZewnetrznyWWW:
            self.aAPPPATHS_OID.AdresZewnetrznyWWW = self.aHOME_PAGE_ADDRESS
        if not self.aAPPPATHS_OID.AdresWewnetrznyWWW:
            self.aAPPPATHS_OID.AdresWewnetrznyWWW = '127.0.0.1'
        self.aAPPPATHS_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aMETATEMPLATE_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_MetaTemplate', fieldname='Nazwa', fieldvalue='%s' % self.aCMS_NAME, parentrefs=self.aWWWMENUSTRUCT_OID.MetaTemplate.Refs, aoidrangesobj=self.aOIDRange)
        self.aMETATEMPLATE_OID.Nazwa = self.aCMS_NAME
        if not self.aMETATEMPLATE_OID.Author:
            self.aMETATEMPLATE_OID.Author = self.aMETA_AUTHOR
        if not self.aMETATEMPLATE_OID.Description:
            self.aMETATEMPLATE_OID.Description = self.aMETA_DESCRIPTION
        if not self.aMETATEMPLATE_OID.Keywords:
            self.aMETATEMPLATE_OID.Keywords = self.aMETA_KEYWORDS
        self.aMETATEMPLATE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aPAGETEMPLATE_OID = self.aWWWMENUSTRUCT_OID.PageTemplate
        if not self.aPAGETEMPLATE_OID:
            self.aPAGETEMPLATE_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_PageTemplate', fieldname='Template', fieldvalue='%s' % self.aCMS_NAME, parentrefs=self.aWWWMENUSTRUCT_OID.PageTemplate.Refs, aoidrangesobj=self.aOIDRange)
            self.aPAGETEMPLATE_OID.Template = '%s' % self.aCMS_NAME
            self.aPAGETEMPLATE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
            self.aPAGECSSTEMPLATE_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_PageCSS', fieldname='CSSName', fieldvalue='%s' % self.aCMS_NAME, parentrefs=self.aPAGETEMPLATE_OID.PageCSSTemplate.Refs, aoidrangesobj=self.aOIDRange)
            self.aPAGECSSTEMPLATE_OID.CSSName = '%s' % self.aCMS_NAME
            self.aPAGECSSTEMPLATE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aPAGETEMPLATEQ_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_PageTemplate', fieldname='Template', fieldvalue='%s_2020Q' % self.aCMS_NAME, parentrefs=self.aWWWMENUSTRUCT_OID.PageTemplate.Refs, aoidrangesobj=self.aOIDRange)
        self.aPAGETEMPLATEQ_OID.Template = '%s_2020Q' % self.aCMS_NAME
        self.aPAGETEMPLATEQ_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aPAGETEMPLATEQ_OID.PageTop1 = '''{% include "_page_template_bip.jinja" %}
      '''
        self.aPAGETEMPLATEQ_OID.PageXML = '''<?xml version="1.0" encoding="Windows-1250"?>
<TEMPLATE>
  <VARIABLES>
    <VAR name="url_WWWSite">%s</VAR>

    <VAR name="text_Page_title"><![CDATA[%s]]></VAR>
    <VAR name="img_Page_title">/%s/image/logo.png</VAR>
    <VAR name="text_NazwaBIP"><![CDATA[Biuletyn Informacji Publicznej]]></VAR>
    <VAR name="text_TytulBIP1"><![CDATA[%s]]></VAR>
    <VAR name="text_TytulBIP2"><![CDATA[]]></VAR>

    <VAR name="email_Admin">%s</VAR>

    <!-- dalej nie zmieniac -->
    <VAR name="css_switch">contrast,font</VAR>
    <VAR name="CustomHeadSection">1</VAR>
    <VAR name="CustomBodySection">1</VAR>
    <VAR name="jinja_Libs">108004</VAR>
  </VARIABLES>
</TEMPLATE>
''' % (startutil.appconfig.IParams['builder_default_wwwsite'],self.aPRETTY_CMS_NAME,startutil.appconfig.IParams['wwwfiles_default'],self.aPRETTY_CMS_NAME, self.aEMAIL)
        self.aSZABLON_GENEROWANIA_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SzablonGenerowania', fieldname='Nazwa', fieldvalue='%s' % self.aCMS_NAME, parentrefs=self.ProjectObj.SzablonyGenerowania.Refs, aoidrangesobj=self.aOIDRange)
        self.aSZABLON_GENEROWANIA_OID.Nazwa = '%s' % self.aCMS_NAME
        self.aSZABLON_GENEROWANIA_OID.GenerujSP = '1'
        self.aSZABLON_GENEROWANIA_OID.GenerujVar = '1'
        self.aSZABLON_GENEROWANIA_OID.WWWStruktura.Refs.AddRef(self.aWWWMENUSTRUCT_OID.OID, anoduplicates=1, store=1)
        self.aSZABLON_GENEROWANIA_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)

    def CreateTable(self, tablename, aNazwaObiektu=None, aNazwaTabeli=None, aGrupa=None, accessuser=1):
        ltablename = tablename
        if type(tablename) == type([]):
            tablename = ltablename[0]
        tobj = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy', fieldname='Nazwa', fieldvalue=ltablename, parentrefs=self.aWWWMENUSTRUCT_OID.TabeleZrodlowe.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        self.ProjectObj.BazyZrodlowe.Refs.AddRef(tobj.OID, anoduplicates=1, store=1)
        tobj.Nazwa = tablename
        if aNazwaObiektu is not None:
            tobj.NazwaObiektu = aNazwaObiektu
        if aNazwaTabeli is not None:
            tobj.NazwaTabeli = aNazwaTabeli
        if aGrupa is not None:
            tobj.Grupa = aGrupa
        else:
            tobj.Grupa = self.aCMS_NAME
        tobj.IsVersionControl = '1'
        tobj.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        tobj.AccessLevelEdit.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        tobj.AccessLevelDelete.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        tobj.AccessLevelFilesUpload.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        if accessuser:
            tobj.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)
            tobj.AccessLevelEdit.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)
            tobj.AccessLevelFilesUpload.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)
        self.aSGTabIndex = 10
        return tobj

    def CreateField(self, tobj, fieldname, fieldtype=None, aFieldNameAsDisplayed=None, aSGTabIndex=None, aSGIsAliased=None, aSGIsIndexed=None, aSGIsSearch=None, aSGIsObligatory=None, aSGIsSingleViewHidden=None, aSGIsDictViewHidden=None, aWartosciSlownika=None, aZrodloDanychSlownika=None):
        fobj = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_OpisPolaDotyczy', fieldname='Nazwa', fieldvalue=fieldname, parentrefs=tobj.Pola.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        fobj.Nazwa = fieldname
        if fieldtype is not None:
            self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_TypPolaDotyczy', fieldname='Opis', fieldvalue=fieldtype, parentrefs=fobj.TypPolaDotyczy.Refs)
        if aFieldNameAsDisplayed is not None:
            fobj.NazwaWidoczna = aFieldNameAsDisplayed
        if aSGTabIndex is None:
            aSGTabIndex = self.aSGTabIndex
            self.aSGTabIndex = self.aSGTabIndex + 10
        if aSGTabIndex is not None:
            fobj.SGTabIndex = str(aSGTabIndex)
        if aSGIsAliased is not None:
            fobj.SGIsAliased = aSGIsAliased
        if aSGIsIndexed is not None:
            fobj.SGIsIndexed = aSGIsIndexed
        if aSGIsSearch is not None:
            fobj.SGIsSearch = aSGIsSearch
        if aSGIsObligatory is not None:
            fobj.SGIsObligatory = aSGIsObligatory
        if aSGIsSingleViewHidden is not None:
            fobj.SGIsSingleViewHidden = aSGIsSingleViewHidden
        if aSGIsDictViewHidden is not None:
            fobj.SGIsDictViewHidden = aSGIsDictViewHidden
        if aWartosciSlownika is not None:
            fobj.WartosciSlownika = XMLUtil.GetXMLStringAsString(aWartosciSlownika)
        if aZrodloDanychSlownika is not None:
            tobj = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy', fieldname='Nazwa', fieldvalue=aZrodloDanychSlownika, parentrefs=self.aWWWMENUSTRUCT_OID.TabeleZrodlowe.Refs, searchinrefs=1, check=1)
            if tobj:
                fobj.ZrodloDanychSlownika.Refs.AddRef(tobj.OID, anoduplicates=1, store=1)
            else:
                self.WriteError('Nieistniejaca tabela slownikowa: %s' % aZrodloDanychSlownika)
                return
        return fobj

    def AddTableCMSFields(self, tobj):
        UID = self.GetUID()
        self.CreateField(tobj, 'Informacja podmiot udostępniający', 'Ciąg znaków - 1 linia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1')
        self.CreateField(tobj, 'Informacja osoba odpowiedzialna', 'Ciąg znaków - 1 linia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1')
        self.CreateField(tobj, 'Informacja data wytworzenia', 'Data', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1')
        self.CreateField(tobj, 'Informacja opis czynności', 'Ciąg znaków - 1 linia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1')
        self.CreateField(tobj, '_OIDDictRef', 'OID', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSingleViewHidden='1')
        self.CreateField(tobj, '_ChapterID', 'Liczba całkowita', aSGIsAliased='0', aSGIsIndexed='1', aSGIsDictViewHidden='0')

    def CreateObjectsTables10(self):
        UID = self.GetUID()
        self.aTABELA_STRONYOPISOWE_OID = self.CreateTable(tablename=['Strony opisowe - %s' % self.aCMS_NAME, 'strony opisowe'], aNazwaObiektu='Strony opisowe', aNazwaTabeli='Strony opisowe', accessuser=1)
        self.CreateField(self.aTABELA_STRONYOPISOWE_OID, 'Nr kolejny', 'Liczba całkowita', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='0', aSGIsSingleViewHidden='1', aSGIsDictViewHidden='1')
        self.CreateField(self.aTABELA_STRONYOPISOWE_OID, 'Tytuł', 'Ciąg znaków - 1 długa linia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1')
        self.CreateField(self.aTABELA_STRONYOPISOWE_OID, 'Treść', 'HTML', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1')
        self.AddTableCMSFields(self.aTABELA_STRONYOPISOWE_OID)

    def CreateObjectsTables20(self):
        UID = self.GetUID()
        self.aTABELA_REJESTRZMIAN_OID = self.CreateTable(tablename=['Rejestr zmian - %s' % self.aCMS_NAME, 'rejestr zmian'], aNazwaObiektu='Rejestr zmian', aNazwaTabeli='Rejestr zmian', aGrupa='%s - Wtyczki' % self.aCMS_NAME, accessuser=0)
        self.CreateField(self.aTABELA_REJESTRZMIAN_OID, 'BZROID', 'OID', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSingleViewHidden='1')
        self.CreateField(self.aTABELA_REJESTRZMIAN_OID, 'ChapterID', 'Liczba całkowita', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSingleViewHidden='1')
        self.CreateField(self.aTABELA_REJESTRZMIAN_OID, 'TableId', 'Liczba całkowita', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSingleViewHidden='0')
        self.CreateField(self.aTABELA_REJESTRZMIAN_OID, 'ChapterName', 'Ciąg znaków - 1 długa linia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsSingleViewHidden='0')
        self.CreateField(self.aTABELA_REJESTRZMIAN_OID, 'TableName', 'Ciąg znaków - 1 linia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsSingleViewHidden='0')
        self.CreateField(self.aTABELA_REJESTRZMIAN_OID, 'Akcja', 'Ciąg znaków - 1 linia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1')
        self.AddTableCMSFields(self.aTABELA_REJESTRZMIAN_OID)

    def CreatePlugin(self, apluginname, anotemplate=0, apluginvars=None):
        aplugin = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Component_Plugin', fieldname='Nazwa', fieldvalue=apluginname, parentrefs=self.aWWWMENUSTRUCT_OID.Plugins.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        aplugin.Nazwa = apluginname
        if apluginvars is not None:
            if aplugin.PluginVars == '':
                aplugin.PluginVars = apluginvars
        aplugin.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        if not anotemplate:
            self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Component_Template', fieldname='Nazwa', fieldvalue=apluginname, parentrefs=aplugin.Template.Refs)
        return aplugin

    def CreatePlugin_BibliotekaStandardowa(self):
        UID = self.GetUID()
        apluginvars = '''aDefaultProtocol=http
aCacheDisable=1
'''
        self.aPLUGIN_BIBLIOTEKA_OID = self.CreatePlugin('Biblioteka standardowa', apluginvars=apluginvars)

    def CreatePlugin_ModulBezpieczenstwa(self):
        UID = self.GetUID()
        self.aPLUGIN_MODUL_OID = self.CreatePlugin('Moduł bezpieczeństwa')

    def CreatePluginTables(self):
        aGrupa = '%s - Wtyczki' % self.aCMS_NAME
        self.aTABELA_Abstrakty_OID = self.CreateTable(tablename='Abstrakty', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Abstrakty_OID, 'Tytuł', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Tytuł', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Abstrakty_OID, 'Treść', 'Opis', aFieldNameAsDisplayed='Treść', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Abstrakty_OID)

        self.aTABELA_Multimedia_OID = self.CreateTable(tablename='Multimedia', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Name', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Nazwa', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'FileSize', 'Liczba całkowita', aFieldNameAsDisplayed='Rozmiar', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Description', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Opis', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'LastModification', 'Data i czas', aFieldNameAsDisplayed='Ostatnia modyfikacja', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Category', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Kategoria', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Kind', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Rodzaj', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'ItemKey', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Klucz', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'ItemRel', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Rel', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'ItemTitle', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Tytuł', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'ItemType', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Typ', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'ItemWidth', 'Liczba całkowita', aFieldNameAsDisplayed='Szerokość', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'ItemHeight', 'Liczba całkowita', aFieldNameAsDisplayed='Wysokość', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Status', 'Słownik użytkownika', aFieldNameAsDisplayed='Status', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0',
                         aWartosciSlownika='&quot;&quot;,&quot;Nowy wpis&quot;&#10;&quot;P1&quot;,&quot;Oczekuje na przetworzenie&quot;,&quot;|B1|Z1&quot;&#10;&quot;B1&quot;,&quot;Błędy w przetwarzaniu&quot;,&quot;P1&quot;&#10;&quot;Z1&quot;,&quot;Wpis zatwierdzony&quot;,&quot;P1&quot;', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'RefTable', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='RefTable', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'RefOID', 'OID', aFieldNameAsDisplayed='RefOID', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'ItemGroup', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Grupa', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'FileName', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Plik', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'FileExtension', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Rozszerzenie pliku', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'FileTypePath', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Ścieżka typu pliku', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Zawartość pliku', 'Opis', aFieldNameAsDisplayed='Zawartość pliku', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Status Konwersji', 'Słownik użytkownika', aFieldNameAsDisplayed='Status Konwersji', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0',
                         aWartosciSlownika='&quot;&quot;,&quot;Nowy wpis&quot;,&quot;&quot;&#10;&quot;T&quot;,&quot;W trakcie konwersji&quot;,&quot;&quot;&#10;&quot;B&quot;,&quot;Błąd konwersji&quot;,&quot;&quot;&#10;&quot;Z&quot;,&quot;Konwersja zakończona&quot;', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Status miniatur', 'Słownik użytkownika', aFieldNameAsDisplayed='Status miniatur', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0',
                         aWartosciSlownika='&quot;&quot;,&quot;Nowy wpis&quot;,&quot;&quot;&#10;&quot;T&quot;,&quot;W trakcie generowania&quot;,&quot;&quot;&#10;&quot;B&quot;,&quot;Błąd tworzenia miniatury&quot;,&quot;&quot;&#10;&quot;Z&quot;,&quot;Tworzenie miniatury zakończone&quot;', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Info o konwersji', 'Opis', aFieldNameAsDisplayed='Info o konwersji', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Info o miniaturach', 'Opis', aFieldNameAsDisplayed='Info o miniaturach', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Ilość miniatur', 'Liczba całkowita', aFieldNameAsDisplayed='Ilość miniatur', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Counter View', 'Liczba całkowita', aFieldNameAsDisplayed='Ilość obejrzeń', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Domyślny nr miniatury', 'Liczba całkowita', aFieldNameAsDisplayed='Domyślny nr miniatury', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Item Status', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Status pozycji', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Multimedia_OID, 'Item Position', 'Liczba całkowita', aFieldNameAsDisplayed='Nr kolejny', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Multimedia_OID)
        self.aXMLDATA_Multimedia_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_XMLData_TableXMLData', fieldname='Name', fieldvalue='Lista załączników', parentrefs=self.aTABELA_Multimedia_OID.XMLData.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        if self.objectisnew:
            self.WriteInfo('pamiętaj o wkopiowaniu treści XMLData - lista załączników w tabeli Multimedia')
        self.aXMLDATA_Multimedia_OID.Name = 'Lista załączników'
        self.aXMLDATA_Multimedia_OID.AutoGenerate = '1'
        self.aXMLDATA_Multimedia_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aXMLDATA_Multimedia_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)

        self.aTABELA_Kalendarium_OID = self.CreateTable(tablename='Kalendarium', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Nazwa', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Nazwa', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Data rozpoczęcia', 'Data i czas', aFieldNameAsDisplayed='Data rozpoczęcia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Data zakończenia', 'Data i czas', aFieldNameAsDisplayed='Data zakończenia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Wyświetlaj aktualności od', 'Data', aFieldNameAsDisplayed='Wyświetlaj aktualności od', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Wyświetlaj aktualności do', 'Data', aFieldNameAsDisplayed='Wyświetlaj aktualności do', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Priorytet wyświetlania', 'Słownik użytkownika', aFieldNameAsDisplayed='Priorytet wyświetlania', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0',
                         aWartosciSlownika='&quot;N1&quot;,&quot;Normalny - poziom 1&quot;&#10;&quot;N0&quot;,&quot;Normalny - poziom 0&quot;&#10;&quot;N2&quot;,&quot;Normalny - poziom 2&quot;&#10;&quot;A0&quot;,&quot;Przypięty - poziom 0&quot;&#10;&quot;A1&quot;,&quot;Przypięty - poziom 1&quot;&#10;&quot;A2&quot;,&quot;Przypięty - poziom 2&quot;', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Priorytet aktualności', 'Słownik użytkownika', aFieldNameAsDisplayed='Priorytet aktualności', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='&quot;00&quot;,&quot;Ignorowany&quot;&#10;&quot;03&quot;,&quot;Normalny&quot;&#10;&quot;01&quot;,&quot;Niski&quot;&#10;&quot;05&quot;,&quot;Wysoki&quot;', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Miejsce wydarzenia', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Miejsce wydarzenia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Opis', 'HTML', aFieldNameAsDisplayed='Opis', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Kategoria', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Kategoria', aSGIsAliased='0', aSGIsIndexed='0', aSGIsSearch='0', aSGIsObligatory='0', aSGIsSingleViewHidden='1', aSGIsDictViewHidden='1', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Uwagi', 'Opis', aFieldNameAsDisplayed='Uwagi redaktora', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kalendarium_OID, 'Status zatwierdzenia', 'Słownik użytkownika', aFieldNameAsDisplayed='Status zatwierdzenia', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0',
                         aWartosciSlownika='&quot;T1&quot;,&quot;W trakcie pracy&quot;,&quot;|P1&quot;&#10;&quot;S1&quot;,&quot;Do sprawdzenia&quot;,&quot;|T1&quot;&#10;&quot;P1&quot;,&quot;Do poprawki&quot;,&quot;S1|Z1&quot;&#10;&quot;X1&quot;,&quot;Odrzucony&quot;,&quot;S1|Z1&quot;&#10;&quot;Z1&quot;,&quot;Zatwierdzony do publikacji&quot;,&quot;S1&quot;', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Kalendarium_OID)

        self.aTABELA_Geolokalizacja_OID = self.CreateTable(tablename='Geolokalizacja', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Geolokalizacja_OID, 'Info', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Info', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Geolokalizacja_OID, 'Lat', 'Współrzędne geograficzne', aFieldNameAsDisplayed='Lat', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Geolokalizacja_OID, 'Lon', 'Współrzędne geograficzne', aFieldNameAsDisplayed='Lon', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Geolokalizacja_OID, 'Table ID', 'Liczba całkowita', aFieldNameAsDisplayed='Table ID', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Geolokalizacja_OID)

        self.aTABELA_Kategorie_tresci_OID = self.CreateTable(tablename='Kategorie treści', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Kategorie_tresci_OID, 'Kategoria', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Kategoria', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kategorie_tresci_OID, 'Grupa', 'Ciąg znaków - 1 długa linia', aFieldNameAsDisplayed='Grupa', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Kategorie_tresci_OID, 'Rola', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Rola', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Kategorie_tresci_OID)

        self.aTABELA_Przypisane_kategorie_tresci_OID = self.CreateTable(tablename='Przypisane kategorie treści', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Przypisane_kategorie_tresci_OID, 'Kategoria', 'Słownik zewnętrzny', aFieldNameAsDisplayed='Kategoria', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='1', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika='Kategorie treści')
        self.CreateField(self.aTABELA_Przypisane_kategorie_tresci_OID, 'ID Obiektu', 'OID', aFieldNameAsDisplayed='ID Obiektu', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Przypisane_kategorie_tresci_OID)

        self.aTABELA_Przypisane_tabele_tresci_OID = self.CreateTable(tablename='Przypisane tabele w treści', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Przypisane_tabele_tresci_OID, 'Rozdział', 'Liczba całkowita', aFieldNameAsDisplayed='Rozdział', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Przypisane_tabele_tresci_OID, 'ID Obiektu', 'OID', aFieldNameAsDisplayed='ID Obiektu', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Przypisane_tabele_tresci_OID, 'XMLDataID', 'Liczba całkowita', aFieldNameAsDisplayed='XMLDataID', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Przypisane_tabele_tresci_OID, 'CMSID', 'Liczba całkowita', aFieldNameAsDisplayed='CMSID', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Przypisane_tabele_tresci_OID)

        self.aTABELA_Licznik_odwiedzin_OID = self.CreateTable(tablename='Licznik odwiedzin', aNazwaObiektu='', aNazwaTabeli='', aGrupa=aGrupa, accessuser=1)
        self.CreateField(self.aTABELA_Licznik_odwiedzin_OID, 'Rodzaj', 'Ciąg znaków - 1 linia', aFieldNameAsDisplayed='Rodzaj', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Licznik_odwiedzin_OID, 'Rozdział', 'Liczba całkowita', aFieldNameAsDisplayed='Rozdział', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Licznik_odwiedzin_OID, 'Obiekt', 'OID', aFieldNameAsDisplayed='Obiekt', aSGIsAliased='0', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.CreateField(self.aTABELA_Licznik_odwiedzin_OID, 'Licznik', 'Liczba całkowita', aFieldNameAsDisplayed='Licznik', aSGIsAliased='1', aSGIsIndexed='1', aSGIsSearch='1', aSGIsObligatory='0', aSGIsSingleViewHidden='0', aSGIsDictViewHidden='0', aWartosciSlownika='', aZrodloDanychSlownika=None)
        self.AddTableCMSFields(self.aTABELA_Licznik_odwiedzin_OID)

    def CreatePlugin_Abstrakty(self):
        UID = self.GetUID()
        apluginvars = '''aTableOIDs_Allowed=%d

aTableOID_Abstrakty=%d

aMax_TextLength=500

aDictFields_Tytul[%d]=Tytul
aDictFields_Tresc[%d]=Tresc
''' % (self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Abstrakty_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, )
        self.aPLUGIN_ABSTRAKTY_OID = self.CreatePlugin('Abstrakty', apluginvars=apluginvars)

    def CreatePlugin_Kalendarium(self):
        UID = self.GetUID()
        apluginvars = '''aTableOIDs_Allowed=%d
aTableOID_Kalendarium=%d

aMax_TextLength=500

aDictFields_Tytul[%d]=Tytul
aDictFields_Tresc[%d]=Tresc

#$$
#aChapterID_Kalendarium=201048
#aTableOID_ZgloszeniaKalendarium=108001
#aSMTPServerParametersOID=56000

#aShowDayCalendar=1

aTableOID_Multimedia=%d
aBaseURL_Multimedia=https://%s/%s/image/_multimedia/
''' % (self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Kalendarium_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Multimedia_OID.OID, self.aHOME_PAGE_ADDRESS, self.ProjectObj.WWWDataPathUserFiles)
        self.aPLUGIN_KALENDARIUM_OID = self.CreatePlugin('Kalendarium', apluginvars=apluginvars)

    def CreatePlugin_Geolokalizacja(self):
        UID = self.GetUID()
        apluginvars = '''aTableOIDs_Allowed=%d
aTableOID_LokalizacjaGeoRSS=%d

aDefault_Lat=%s
aDefault_Lon=%s
''' % (self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Geolokalizacja_OID.OID, startutil.appconfig.IParams['aDefault_Lat'], startutil.appconfig.IParams['aDefault_Lon']
)
        self.aPLUGIN_GEOLOKALIZACJA_OID = self.CreatePlugin('Geolokalizacja', apluginvars=apluginvars)

    def CreatePlugin_Wyszukiwarka(self):
        UID = self.GetUID()
        apluginvars = '''aTableOIDs_Allowed=%d

aTableOID_Multimedia=%d
aText_Search=
aSQLView_Media=

aSearchMode=fts

aDefaultImage=img/other_news_icon.jpg
#aSQLView_FromDate=2020-02-28

aMax_TextLength=500

aDictFields_Tytul[%d]=Tytul
aDictFields_Tresc[%d]=Tresc
''' % (self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Multimedia_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, )
        self.aPLUGIN_WYSZUKIWARKA_OID = self.CreatePlugin('Wyszukiwarka', apluginvars=apluginvars)

    def CreatePlugin_Multimedia(self):
        UID = self.GetUID()
        apluginvars = '''aTableOIDs_Allowed=%d

aTableOID_Multimedia=%d
aTableOID_Kalendarium=%d
aTableOID_Abstrakty=%d

aXMLDataOID_Multimedia=%d

aMaxSize=165000000

aMaxImageSizeX[lead]=200
aMaxImageSizeY[lead]=177
aImageCrop[lead]=1
aMaxImageSizeKB[lead]=160
aThumbImageCrop[lead]=1
aThumbMaxImageSizeX[lead]=200
aThumbMaxImageSizeY[lead]=177

aMaxImageSizeX[main]=800
aMaxImageSizeY[main]=438
aImageCrop[main]=1
aMaxImageSizeKB[main]=320
aThumbImageCrop[main]=1
aThumbMaxImageSizeX[main]=800
aThumbMaxImageSizeY[main]=438

aMaxImageSizeX[bookcover]=240
aMaxImageSizeY[bookcover]=340
aImageCrop[bookcover]=0
aMaxImageSizeKB[bookcover]=90
aThumbImageCrop[bookcover]=0
aThumbMaxImageSizeX[bookcover]=138
aThumbMaxImageSizeY[bookcover]=195

aMaxImageSizeX[ebook]=240
aMaxImageSizeY[ebook]=340
aImageCrop[ebook]=1
aMaxImageSizeKB[ebook]=90
aThumbImageCrop[ebook]=0
aThumbMaxImageSizeX[ebook]=138
aThumbMaxImageSizeY[ebook]=195

aMaxImageSizeX[galeria]=1600
aMaxImageSizeY[galeria]=1200
aImageCrop[galeria]=1
aMaxImageSizeKB[galeria]=400
aThumbImageCrop[galeria]=1
aThumbMaxImageSizeX[galeria]=160
aThumbMaxImageSizeY[galeria]=120

#
# App elements
#

#carousel 725x400
aMaxImageSizeX[carousel]=725
aMaxImageSizeY[carousel]=400
aImageCrop[carousel]=1
aMaxImageSizeKB[carousel]=220
aThumbImageCrop[carousel]=1
aThumbMaxImageSizeX[carousel]=242
aThumbMaxImageSizeY[carousel]=134

#baner-menu1 178x60
aMaxImageSizeX[baner-menu1]=534
aMaxImageSizeY[baner-menu1]=180
aImageCrop[baner-menu1]=1
aMaxImageSizeKB[baner-menu1]=120
aThumbImageCrop[baner-menu1]=1
aThumbMaxImageSizeX[baner-menu1]=178
aThumbMaxImageSizeY[baner-menu1]=60

#baner-menu2 178x125
aMaxImageSizeX[baner-menu2]=534
aMaxImageSizeY[baner-menu2]=375
aImageCrop[baner-menu2]=1
aMaxImageSizeKB[baner-menu2]=140
aThumbImageCrop[baner-menu2]=1
aThumbMaxImageSizeX[baner-menu2]=178
aThumbMaxImageSizeY[baner-menu2]=125

#baner-menu3 178x190
aMaxImageSizeX[baner-menu3]=534
aMaxImageSizeY[baner-menu3]=570
aImageCrop[baner-menu3]=1
aMaxImageSizeKB[baner-menu3]=160
aThumbImageCrop[baner-menu3]=1
aThumbMaxImageSizeX[baner-menu3]=178
aThumbMaxImageSizeY[baner-menu3]=190

#aktualnosc 350x220
aMaxImageSizeX[aktualnosc]=1050
aMaxImageSizeY[aktualnosc]=660
aImageCrop[aktualnosc]=1
aMaxImageSizeKB[aktualnosc]=220
aThumbImageCrop[aktualnosc]=1
aThumbMaxImageSizeX[aktualnosc]=350
aThumbMaxImageSizeY[aktualnosc]=220

#aktualnosc-list 195x120
aMaxImageSizeX[aktualnosc-list]=585
aMaxImageSizeY[aktualnosc-list]=360
aImageCrop[aktualnosc-list]=1
aMaxImageSizeKB[aktualnosc-list]=160
aThumbImageCrop[aktualnosc-list]=1
aThumbMaxImageSizeX[aktualnosc-list]=195
aThumbMaxImageSizeY[aktualnosc-list]=120

#baner-link-1 350x250
aMaxImageSizeX[baner-link-1]=350
aMaxImageSizeY[baner-link-1]=250
aImageCrop[baner-link-1]=1
aMaxImageSizeKB[baner-link-1]=160
aThumbImageCrop[baner-link-1]=1
aThumbMaxImageSizeX[baner-link-1]=350
aThumbMaxImageSizeY[baner-link-1]=250

#baner-link-2 725x250
aMaxImageSizeX[baner-link-2]=725
aMaxImageSizeY[baner-link-2]=250
aImageCrop[baner-link-2]=1
aMaxImageSizeKB[baner-link-2]=160
aThumbImageCrop[baner-link-2]=1
aThumbMaxImageSizeX[baner-link-2]=350
aThumbMaxImageSizeY[baner-link-2]=250

#baner-link-3 1100x250
aMaxImageSizeX[baner-link-3]=1100
aMaxImageSizeY[baner-link-3]=250
aImageCrop[baner-link-3]=1
aMaxImageSizeKB[baner-link-3]=160
aThumbImageCrop[baner-link-3]=1
aThumbMaxImageSizeX[baner-link-3]=350
aThumbMaxImageSizeY[baner-link-3]=250

#baner-link-4 733x112
aMaxImageSizeX[baner-link-4]=733
aMaxImageSizeY[baner-link-4]=112
aImageCrop[baner-link-4]=1
aMaxImageSizeKB[baner-link-4]=160
aThumbImageCrop[baner-link-4]=1
aThumbMaxImageSizeX[baner-link-4]=350
aThumbMaxImageSizeY[baner-link-4]=54

# galerie w tresci:
aMaxImageSizeX[galeria1]=1600
aMaxImageSizeY[galeria1]=1200
aImageCrop[galeria1]=1
aImageCropProportional[galeria1]=1
aMaxImageSizeKB[galeria1]=400
aThumbImageCrop[galeria1]=1
aThumbMaxImageSizeX[galeria1]=320
aThumbMaxImageSizeY[galeria1]=240

aMaxImageSizeX[galeria2]=1600
aMaxImageSizeY[galeria2]=1200
aImageCrop[galeria2]=1
aImageCropProportional[galeria2]=1
aMaxImageSizeKB[galeria2]=400
aThumbImageCrop[galeria2]=1
aThumbMaxImageSizeX[galeria2]=320
aThumbMaxImageSizeY[galeria2]=240

aMaxImageSizeX[galeria3]=1600
aMaxImageSizeY[galeria3]=1200
aImageCrop[galeria3]=1
aImageCropProportional[galeria3]=1
aMaxImageSizeKB[galeria3]=400
aThumbImageCrop[galeria3]=1
aThumbMaxImageSizeX[galeria3]=320
aThumbMaxImageSizeY[galeria3]=240

aMaxImageSizeX[galeria4]=1600
aMaxImageSizeY[galeria4]=1200
aImageCrop[galeria4]=1
aImageCropProportional[galeria4]=1
aMaxImageSizeKB[galeria4]=400
aThumbImageCrop[galeria4]=1
aThumbMaxImageSizeX[galeria4]=320
aThumbMaxImageSizeY[galeria4]=240

aMaxImageSizeX[galeria5]=1600
aMaxImageSizeY[galeria5]=1200
aImageCrop[galeria5]=1
aImageCropProportional[galeria5]=1
aMaxImageSizeKB[galeria5]=400
aThumbImageCrop[galeria5]=1
aThumbMaxImageSizeX[galeria5]=320
aThumbMaxImageSizeY[galeria5]=240

aMaxImageSizeX[galeria6]=1600
aMaxImageSizeY[galeria6]=1200
aImageCrop[galeria6]=1
aImageCropProportional[galeria6]=1
aMaxImageSizeKB[galeria6]=400
aThumbImageCrop[galeria6]=1
aThumbMaxImageSizeX[galeria6]=320
aThumbMaxImageSizeY[galeria6]=240

aMaxImageSizeX[galeria7]=1600
aMaxImageSizeY[galeria7]=1200
aImageCrop[galeria7]=1
aImageCropProportional[galeria7]=1
aMaxImageSizeKB[galeria7]=400
aThumbImageCrop[galeria7]=1
aThumbMaxImageSizeX[galeria7]=320
aThumbMaxImageSizeY[galeria7]=240

aMaxImageSizeX[galeria8]=1600
aMaxImageSizeY[galeria8]=1200
aImageCrop[galeria8]=1
aImageCropProportional[galeria8]=1
aMaxImageSizeKB[galeria8]=400
aThumbImageCrop[galeria8]=1
aThumbMaxImageSizeX[galeria8]=320
aThumbMaxImageSizeY[galeria8]=240

aMaxImageSizeX[galeria9]=1600
aMaxImageSizeY[galeria9]=1200
aImageCrop[galeria9]=1
aImageCropProportional[galeria9]=1
aMaxImageSizeKB[galeria9]=400
aThumbImageCrop[galeria9]=1
aThumbMaxImageSizeX[galeria9]=320
aThumbMaxImageSizeY[galeria9]=240

''' % (self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Multimedia_OID.OID, self.aTABELA_Kalendarium_OID.OID, self.aTABELA_Abstrakty_OID.OID, self.aXMLDATA_Multimedia_OID.OID)
        self.aPLUGIN_MULTIMEDIA_OID = self.CreatePlugin('Multimedia', apluginvars=apluginvars)

    def CreatePlugin_KategorieTresci(self):
        UID = self.GetUID()
        apluginvars = '''aTableOIDs_Allowed=%d

aTableOID_Categories=%d
aTableOID_AssignedCategories=%d
''' % (self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Kategorie_tresci_OID.OID, self.aTABELA_Przypisane_kategorie_tresci_OID.OID, )
        self.aPLUGIN_KATEGORIETRESCI_OID = self.CreatePlugin('Kategorie treści', apluginvars=apluginvars)
        self.WriteInfo('pamiętaj aby utworzyć nowe kategorie treści do tabeli kategorii.')

    def CreatePlugin_TabeleTresci(self):
        UID = self.GetUID()
        apluginvars = '''aTableOIDs_Allowed=%d

aTableOID_AssignedTables=%d
''' % (self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_Przypisane_tabele_tresci_OID.OID, )
        self.aPLUGIN_TABELETRESCI_OID = self.CreatePlugin('Tabele w treści', apluginvars=apluginvars)

    def CreatePlugin_NarzedziaSEO(self):
        UID = self.GetUID()
        apluginvars = '''aTableOID_LicznikOdwiedzin=%d

#$$ dodac pelen URL z https://
aImgSrc=img/logo.gif

#
aGoogleSiteVerification=
#
#aGoogleTracking=UA-xxxxxxxx-1

#
aBookmarks=facebook,twitter,linkedin
#aBookmarks=-
''' % (self.aTABELA_Licznik_odwiedzin_OID.OID, )
        self.aPLUGIN_NARZEDZIASEO_OID = self.CreatePlugin('Narzędzia SEO', apluginvars=apluginvars)
        self.WriteInfo('pamiętaj aby zarejestrować serwis w Google Analytics i wpisać kod w narzędziach SEO.')

    def CreatePlugin_WWWSite(self):
        UID = self.GetUID()
        apluginvars = '''aTableOID_Categories=%d
aTableOID_AssignedCategories=%d
aTableOID_AssignedTables=%d
aTableOID_LokalizacjaGeoRSS=%d
aTableOID_Multimedia=%d
aTableOID_Kalendarium=%d
aTableOID_Abstrakty=%d

#aTableOID_BaneryLinki=-1

aTableOID_Aktualnosci=%d
aTableOID_StronyOpisowe=%d
aChapters_Aktualnosci=-1,-1

aPageTemplateOID_Default=%d
''' % (self.aTABELA_Kategorie_tresci_OID.OID, self.aTABELA_Przypisane_kategorie_tresci_OID.OID, self.aTABELA_Przypisane_tabele_tresci_OID.OID, self.aTABELA_Geolokalizacja_OID.OID, self.aTABELA_Multimedia_OID.OID, self.aTABELA_Kalendarium_OID.OID, self.aTABELA_Abstrakty_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, self.aTABELA_STRONYOPISOWE_OID.OID, self.aPAGETEMPLATE_OID.OID,
        )
        self.aPLUGIN_WWWSITE_OID = self.CreatePlugin('WWWSite', apluginvars=apluginvars)

    def CreateRozdzialy(self):
        UID = self.GetUID()
        self.aROZDZIAL_STRONAGLOWNA_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial', fieldname='Naglowek', fieldvalue='Strona Główna', parentrefs=self.aWWWMENUSTRUCT_OID.Rozdzialy.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        self.aROZDZIAL_STRONAGLOWNA_OID.Naglowek = 'Strona Główna'
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy', fieldname='Nazwa', fieldvalue='Strony opisowe - %s' % self.aCMS_NAME, parentrefs=self.aROZDZIAL_STRONAGLOWNA_OID.TabelaZrodlowa.Refs)
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DaneRodzajowe_ZrodloDanychWzorca', fieldname='Nazwa', fieldvalue='Tabela', parentrefs=self.aROZDZIAL_STRONAGLOWNA_OID.ZrodloDanychWzorca.Refs)
        self.aROZDZIAL_STRONAGLOWNA_OID.SGTabID = '10'
        self.aROZDZIAL_STRONAGLOWNA_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aROZDZIAL_STRONAGLOWNA_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)
        self.aROZDZIAL_OSERWISIE_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial', fieldname='Naglowek', fieldvalue='O Serwisie', parentrefs=self.aWWWMENUSTRUCT_OID.Rozdzialy.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        self.aROZDZIAL_OSERWISIE_OID.Naglowek = 'O Serwisie'
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy', fieldname='Nazwa', fieldvalue='Strony opisowe - %s' % self.aCMS_NAME, parentrefs=self.aROZDZIAL_OSERWISIE_OID.TabelaZrodlowa.Refs)
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DaneRodzajowe_ZrodloDanychWzorca', fieldname='Nazwa', fieldvalue='Tabela', parentrefs=self.aROZDZIAL_OSERWISIE_OID.ZrodloDanychWzorca.Refs)
        self.aROZDZIAL_OSERWISIE_OID.SGTabID = '20'
        self.aROZDZIAL_OSERWISIE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aROZDZIAL_OSERWISIE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)
        self.aROZDZIAL_REDAKCJA_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial', fieldname='Naglowek', fieldvalue='Redakcja', parentrefs=self.aWWWMENUSTRUCT_OID.Rozdzialy.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        self.aROZDZIAL_REDAKCJA_OID.Naglowek = 'Redakcja'
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy', fieldname='Nazwa', fieldvalue='Strony opisowe - %s' % self.aCMS_NAME, parentrefs=self.aROZDZIAL_REDAKCJA_OID.TabelaZrodlowa.Refs)
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DaneRodzajowe_ZrodloDanychWzorca', fieldname='Nazwa', fieldvalue='Tabela', parentrefs=self.aROZDZIAL_REDAKCJA_OID.ZrodloDanychWzorca.Refs)
        self.aROZDZIAL_REDAKCJA_OID.SGTabID = '30'
        self.aROZDZIAL_REDAKCJA_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aROZDZIAL_REDAKCJA_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)
        self.aROZDZIAL_INFORMACJETECHNICZNE_OID = self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial', fieldname='Naglowek', fieldvalue='Informacje techniczne', parentrefs=self.aWWWMENUSTRUCT_OID.Rozdzialy.Refs, searchinrefs=1, aoidrangesobj=self.aOIDRange)
        self.aROZDZIAL_INFORMACJETECHNICZNE_OID.Naglowek = 'Informacje techniczne'
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy', fieldname='Nazwa', fieldvalue='Strony opisowe - %s' % self.aCMS_NAME, parentrefs=self.aROZDZIAL_INFORMACJETECHNICZNE_OID.TabelaZrodlowa.Refs)
        self.start_OBJECT('CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_DaneRodzajowe_ZrodloDanychWzorca', fieldname='Nazwa', fieldvalue='Tabela', parentrefs=self.aROZDZIAL_INFORMACJETECHNICZNE_OID.ZrodloDanychWzorca.Refs)
        self.aROZDZIAL_INFORMACJETECHNICZNE_OID.SGTabID = '40'
        self.aROZDZIAL_INFORMACJETECHNICZNE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_Admin_OID, anoduplicates=1, store=1)
        self.aROZDZIAL_INFORMACJETECHNICZNE_OID.AccessLevelView.Refs.AddRef(self.aSECURITY_ITEM_GROUP_User_OID, anoduplicates=1, store=1)

    def Process(self):
        if not self.isError:
            if self.params.get('CreateDirs', 0) == 1:
                self.CreateDirs()
        if not self.isError:
            if self.params.get('CopyFiles', 0) == 1:
                self.CopyFiles()
        if not self.isError:
            if self.params.get('CreateCMS10', 0) == 1:
                self.CreateCMS10()
        if not self.isError:
            if self.params.get('CreateObjectsTables10', 0) == 1:
                self.CreateObjectsTables10()
            if self.params.get('CreateObjectsTables20', 0) == 1:
                self.CreateObjectsTables20()
        if not self.isError:
            if self.params.get('CreatePlugin_BibliotekaStandardowa', 0) == 1:
                self.CreatePlugin_BibliotekaStandardowa()
            if self.params.get('CreatePlugin_ModulBezpieczenstwa', 0) == 1:
                self.CreatePlugin_ModulBezpieczenstwa()
            if self.params.get('CreatePluginTables', 0) == 1:
                self.CreatePluginTables()
            if self.params.get('CreatePlugin_Abstrakty', 0) == 1:
                self.CreatePlugin_Abstrakty()
            if self.params.get('CreatePlugin_Kalendarium', 0) == 1:
                self.CreatePlugin_Kalendarium()
            if self.params.get('CreatePlugin_Geolokalizacja', 0) == 1:
                self.CreatePlugin_Geolokalizacja()
            if self.params.get('CreatePlugin_Wyszukiwarka', 0) == 1:
                self.CreatePlugin_Wyszukiwarka()
            if self.params.get('CreatePlugin_Multimedia', 0) == 1:
                self.CreatePlugin_Multimedia()
            if self.params.get('CreatePlugin_KategorieTresci', 0) == 1:
                self.CreatePlugin_KategorieTresci()
            if self.params.get('CreatePlugin_TabeleTresci', 0) == 1:
                self.CreatePlugin_TabeleTresci()
            if self.params.get('CreatePlugin_NarzedziaSEO', 0) == 1:
                self.CreatePlugin_NarzedziaSEO()
            if self.params.get('CreatePlugin_WWWSite', 0) == 1:
                self.CreatePlugin_WWWSite()
        if not self.isError:
            if self.params.get('CreateRozdzialy', 0) == 1:
                self.CreateRozdzialy()

    def Dump(self):
        alocalvars = ['aPROFILE_NAME', 'aCMS_NAME', 'aPRETTY_CMS_NAME', 'aHEAD_TITLE', 'aMETA_AUTHOR', 'aMETA_DESCRIPTION', 'aMETA_KEYWORDS', 'aEMAIL', 'aHOME_PAGE_ADDRESS', ]
        for alocalvar in alocalvars:
            self.file.write('<h3>%s: %s</h3>' % (alocalvar, self.__dict__[alocalvar]))
