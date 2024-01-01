# -*- coding: utf-8 -*-
from icorinterface import *
from icoriterators import FieldRefIterator
import appplatform.startutil as startutil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string
import re
import types

import appplatform.storageutil as storageutil

PROTECTED_GROUPS=startutil.appconfig.IParams['security_protected_groups'] # yapf: disable
EXCLUDED_PROFILES=startutil.appconfig.IParams['security_excluded_profiles'] # yapf: disable

def GetUIDByUserPassword(auser, apassword, awwwuser=0, averbose=0):
    uclass = aICORDBEngine.Classes['CLASSES_System_User']
    if averbose:
        print 'GetUIDByUserPassword: [%s] [%s] [%s] [%s]' % (auser, apassword, type(auser), type(apassword))
    if uclass is None:
        if averbose:
            print 'GetUIDByUserPassword: uclass is None'
        return -1
    uoid = uclass.UserName.Identifiers(auser)
    if uoid < 0:
        if averbose:
            print 'GetUIDByUserPassword: uoid<0'
        return -1
    if uclass.AccountDisabled.ValuesAsInt(uoid) > 0:
        if averbose:
            print 'GetUIDByUserPassword: accountdisabled'
        return -1
    if awwwuser and uclass.WWWDisabled.ValuesAsInt(uoid) > 0:
        if averbose:
            print 'GetUIDByUserPassword: wwwdisabled'
        return -1
    upass = uclass.Password[uoid]
    hpass = aICORDBEngine.HashString(apassword + '_' + str(uoid))
    if hpass != upass:
        if averbose:
            print 'GetUIDByUserPassword: hpass:', upass, hpass
        return -1
    return uoid


def CheckRecursiveAccessLevelForUser(aobj, aacclevelname, auid=-1, aindent=0):
    if auid < 0:
        auid = GetUID()
    akey = (aobj.CID, aobj.OID, aacclevelname, auid)
    if aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE.has_key(akey):
        return aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE[akey]
    else:
        if len(aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE) > 150000:
            aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE = {}
        if not aobj.Exists():
            aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE[akey] = 0
            return 0
        aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE[akey] = 1
    facclev = aobj.Class.FieldsByName(aacclevelname)
    if facclev is not None:
        brefs = facclev.GetRefList(aobj.OID)
        if brefs:
            ret = CheckAccessLevelForUser(brefs, auid)
            aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE[akey] = ret
            return ret
    ret = 1
    bfields = aobj.Class.BackRefFields
    for bfield in bfields:
        bobj = aobj.GetFieldValue(bfield.Name)
        if bobj:
            ret1 = CheckRecursiveAccessLevelForUser(bobj, aacclevelname, auid, aindent + 1)
            ret = ret and ret1
            if not ret:
                break
    aICORDBEngine._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE[akey] = ret
    return ret


def GetRecursiveAccessLevelRefs(aobj, aacclevelname, aobjreturn=0):
    facclev = aobj.Class.FieldsByName(aacclevelname)
    if facclev is None:
        if aobjreturn:
            return None, None
        else:
            return None
    brefs = facclev.GetRefList(aobj.OID)
    if brefs:
        if aobjreturn:
            return brefs, aobj
        else:
            return brefs
    bfields = aobj.Class.BackRefFields
    for bfield in bfields:
        bobj = aobj.GetFieldValue(bfield.Name)
        if bobj:
            if aobjreturn:
                ret, cobj = GetRecursiveAccessLevelRefs(bobj, aacclevelname, aobjreturn=aobjreturn)
                if ret:
                    return ret, cobj
            else:
                ret = GetRecursiveAccessLevelRefs(bobj, aacclevelname, aobjreturn=aobjreturn)
                if ret:
                    return ret
    if aobjreturn:
        return None, None
    return None


def GetSecurityProfileByObj(aobj):
    arefs = None
    bobj = None
    for aacclevelname in ['AccessLevelView', 'AccessLevelEdit', 'AccessLevelTableEdit', 'AccessLevelDelete', 'AccessLevelFilesUpload']:
        arefs, bobj = GetRecursiveAccessLevelRefs(aobj, aacclevelname, 1)
        if bobj:
            while arefs:
                gobj = arefs.Class[arefs.OID]
                pobj = gobj.Profile
                if pobj:
                    aname = pobj.Name
                    if aname:
                        return aname
                arefs.Next()
    return ''


def CheckAccessLevelForUserMethod1(arefs, auid):
    uclass = aICORDBEngine.Classes['CLASSES_System_User']
    agroups = {}
    agroupset = set()
    arefs.First()
    while arefs.position >= 0:
        aoid = arefs.OID
        if aICORDBEngine._ACCESS_LEVEL_GROUPS_CACHE.has_key(aoid):
            glev, agroupoids = aICORDBEngine._ACCESS_LEVEL_GROUPS_CACHE[aoid]
        else:
            glev = arefs.Class.AccessLevel.ValuesAsInt(aoid)
            grefs = arefs.Class.Groups.GetRefList(aoid)
            agroupoids = grefs.AsListOID()
            aICORDBEngine._ACCESS_LEVEL_GROUPS_CACHE[aoid] = (glev, agroupoids)
        agroupset.update(agroupoids)
        for goid in agroupoids:
            agroups[goid] = max(glev, agroups.get(goid, 0))
        arefs.Next()

    if aICORDBEngine._USER_GROUPS_LEVELS_CACHE.has_key(auid):
        ugroups, ugroupset = aICORDBEngine._USER_GROUPS_LEVELS_CACHE[auid]
    else:
        urefs = uclass.Groups.GetRefList(auid)
        ugroups = {}
        ugroupset = set()
        while urefs.position >= 0:
            glev = urefs.Class.AccessLevel.ValuesAsInt(urefs.OID)
            grefs = urefs.Class.Groups.GetRefList(urefs.OID)
            ugroupoids = grefs.AsListOID()
            ugroupset.update(ugroupoids)
            for goid in ugroupoids:
                ugroups[goid] = min(glev, ugroups.get(goid, 999999))
            urefs.Next()
        aICORDBEngine._USER_GROUPS_LEVELS_CACHE[auid] = (ugroups, ugroupset)

    for goid in agroupset.intersection(ugroupset):
        if ugroups[goid] <= agroups[goid]:
            return 1
    return 0


def CheckAccessLevelForUserMethod2(arefs, auid):
    uclass = aICORDBEngine.Classes['CLASSES_System_User']
    urefs = uclass.Groups.GetRefList(auid)
    arefs.First()
    while arefs.position >= 0:
        urefs.First()
        grefs = arefs.Class.Groups.GetRefList(arefs.OID)
        glev = arefs.Class.AccessLevel.ValuesAsInt(arefs.OID)
        while urefs.position >= 0:
            ugrefs = urefs.Class.Groups.GetRefList(urefs.OID)
            if grefs.RefsExists(ugrefs):
                if urefs.Class.AccessLevel.ValuesAsInt(urefs.OID) <= glev:
                    return 1
            urefs.Next()
        arefs.Next()
    return 0


def CheckAccessLevelForUser(arefs, auid):
    if isinstance(arefs, types.StringTypes):
        akey = (arefs, auid)
        arefs = FieldRefIterator(arefs)
    else:
        akey = (arefs.AsString(), auid)
    if aICORDBEngine._ACCESS_LEVEL_FOR_USER_CACHE.has_key(akey):
        return aICORDBEngine._ACCESS_LEVEL_FOR_USER_CACHE[akey]
    aICORDBEngine._ACCESS_LEVEL_FOR_USER_CACHE[akey] = 1
    if arefs.position < 0:
        return 1
    try:
        ret1 = CheckAccessLevelForUserMethod1(arefs, auid)
        #ret2=CheckAccessLevelForUserMethod2(arefs,auid)
        #if ret1!=ret2:
        #   print '$$ACCESS',auid,arefs.AsListOID()
        if ret1:
            return 1
    except:
        #print '$$ACCESS_ERROR',auid,arefs.AsListOID()
        #raise
        aICORDBEngine._ACCESS_LEVEL_FOR_USER_CACHE[akey] = 0
        return 0
    aICORDBEngine._ACCESS_LEVEL_FOR_USER_CACHE[akey] = 0
    return 0


class ICORSecurityUser:

    def __init__(self, auid=-1, aname='', abyname=0):
        self.UserClass = aICORDBEngine.Classes['CLASSES_System_User']
        if abyname:
            auid = self.UserClass.UserName.Identifiers(aname)
        else:
            if auid < 0:
                auid = GetUID()
        self.UID = auid
        self.UserExists = self.UserClass.ObjectExists(self.UID)
        self._Groups = None
        self._WWWLoginLog = None
        if aname or not self.UserExists:
            self.UserName = aname
        else:
            self.UserName = self.UserClass.UserName[self.UID]
        self._browserVersion = None

    def GetParams(self):
        sparms = self.UserClass.Parameters[self.UID]
        dd = ICORUtil.ParseVars(sparms)
        return dd

    def __getattr__(self, name):
        if name == 'WWWDisabled':
            return self.UserClass.WWWDisabled.ValuesAsInt(self.UID)
        elif name == 'Password':
            return self.UserClass.Password[self.UID]
        elif name == 'PasswordExpiration':
            return self.UserClass.PasswordExpiration[self.UID]
        elif name == 'VCFFirstName':
            return self.UserClass.VCFFirstName[self.UID]
        elif name == 'VCFLastName':
            return self.UserClass.VCFLastName[self.UID]
        elif name == 'VCFEMail':
            return self.UserClass.VCFEMail[self.UID]
        elif name == 'VCFPhone':
            return self.UserClass.VCFPhone[self.UID]
        elif name == 'Description':
            return self.UserClass.Description[self.UID]
        elif name == 'MenuFavorites':
            return self.UserClass.MenuFavorites[self.UID]
        elif name == 'Groups':
            if self._Groups is None:
                self._Groups = self.UserClass.Groups.GetRefList(self.UID)
            self._Groups.First()
            return self._Groups
        elif name == 'WWWLoginLog':
            if self._WWWLoginLog is None:
                self._WWWLoginLog = self.UserClass.WWWLoginLog.GetRefList(self.UID)
            return self._WWWLoginLog
        elif name == 'BrowserVersion':
            if self._browserVersion is None:
                self._browserVersion = -1
                lrefs = self.UserClass.WWWLoginLog.GetRefList(self.UID)
                if lrefs:
                    sbrowserstring = lrefs.HttpUserAgent[lrefs.OID]
                    m = re.search('\; MSIE (\d)\.', sbrowserstring)
                    if m:
                        self._browserVersion = int(m.group(1))
            return self._browserVersion
        return self.__dict__[name]

    def __setattr__(self, name, value):
        if name == 'WWWDisabled':
            self.UserClass.WWWDisabled[self.UID] = str(value)
        elif name == 'Password':
            self.UserClass.Password[self.UID] = value
        elif name == 'PasswordExpiration':
            self.UserClass.PasswordExpiration[self.UID] = value
        elif name == 'VCFFirstName':
            self.UserClass.VCFFirstName[self.UID] = value
        elif name == 'VCFLastName':
            self.UserClass.VCFLastName[self.UID] = value
        elif name == 'VCFEMail':
            self.UserClass.VCFEMail[self.UID] = value
        elif name == 'VCFPhone':
            self.UserClass.VCFPhone[self.UID] = value
        elif name == 'Description':
            self.UserClass.Description[self.UID] = value
        elif name == 'MenuFavorites':
            self.UserClass.MenuFavorites[self.UID] = value
        else:
            self.__dict__[name] = value

    def Delete(self):
        self.UserClass.DeleteObject(self.UID)

    def IsInGroup(self, goid):
        if not self.Groups:
            return 0
        return self.Groups.RefExists(goid, self.Groups.CID)


class ICORSecurityUserGroup:

    def __init__(self, goid, aname=''):
        self.OID = goid
        self.UserGroupClass = aICORDBEngine.Classes['CLASSES_System_GroupAccessLevel']
        if aname:
            self.GroupName = aname
        else:
            self.GroupName = self.UserGroupClass.Name[self.OID]

    def __getattr__(self, name):
        if name == 'Category':
            return self.UserGroupClass.Category[self.OID]
        elif name == 'Kind':
            return self.UserGroupClass.Kind[self.OID]
        return self.__dict__[name]

    def __setattr__(self, name, value):
        if name == 'Category':
            self.UserGroupClass.Category[self.OID] = value
        elif name == 'Kind':
            self.UserGroupClass.Kind[self.OID] = value
        else:
            self.__dict__[name] = value

    def AddUser(self, auser):
        auser.UserClass.Groups.AddRefs(auser.UID, [self.OID, self.UserGroupClass.CID], ainsertifnotexists=1)
        self.UserGroupClass.Users.AddRefs(self.OID, [auser.UID, auser.UserClass.CID], ainsertifnotexists=1)

    def RemoveUser(self, auser):
        arefs = auser.UserClass.Groups.GetRefList(auser.UID)
        if len(arefs) <= 1:
            return 0
        auser.UserClass.Groups.DeleteRefs(auser.UID, [self.OID, self.UserGroupClass.CID])
        self.UserGroupClass.Users.DeleteRefs(self.OID, [auser.UID, auser.UserClass.CID])
        return 1


class ICORSecurityItemGroup:

    def __init__(self, goid, aname=''):
        self.OID = goid
        self.ItemGroupClass = aICORDBEngine.Classes['CLASSES_System_GroupItemAccessLevel']
        if aname:
            self.GroupName = aname
        else:
            self.GroupName = self.ItemGroupClass.Name[self.OID]

    def __getattr__(self, name):
        if name == 'Category':
            return self.ItemGroupClass.Category[self.OID]
        elif name == 'Kind':
            return self.ItemGroupClass.Kind[self.OID]
        return self.__dict__[name]

    def __setattr__(self, name, value):
        if name == 'Category':
            self.ItemGroupClass.Category[self.OID] = value
        elif name == 'Kind':
            self.ItemGroupClass.Kind[self.OID] = value
        else:
            self.__dict__[name] = value

    def GetAllowedUsers(self):
        if aICORDBEngine._ITEMS_GROUP2USERS_CACHE.has_key(self.OID):
            return aICORDBEngine._ITEMS_GROUP2USERS_CACHE[self.OID]
        grefs1 = self.ItemGroupClass.Groups.GetRefList(self.OID)
        suids = set()
        aUserGroupClass = aICORDBEngine.Classes['CLASSES_System_GroupAccessLevel']
        aobj = aUserGroupClass.GetFirstObject()
        while aobj:
            grefs2 = aobj.Class.Groups.GetRefList(aobj.OID)
            if grefs2.RefsExists(grefs1):
                urefs = aobj.Class.Users.GetRefList(aobj.OID)
                for uoid, ucid in urefs.refs:
                    suids.add(uoid)
            aobj.Next()
        aICORDBEngine._ITEMS_GROUP2USERS_CACHE[self.OID] = suids
        if 0:
            luids = []
            aUserClass = aICORDBEngine.Classes['CLASSES_System_User']
            for auid in suids:
                luids.append(aUserClass.UserName[auid])
        return suids


class ICORSecurityProfile:

    def __init__(self, aname=''):
        self.UserClass = aICORDBEngine.Classes['CLASSES_System_User']
        self.ProfileClass = aICORDBEngine.Classes['CLASSES_System_SystemDictionary_ProfileGroup']
        self.StartupClass = aICORDBEngine.Classes['CLASSES_System_Startup']
        self.BaseGroupsClass = aICORDBEngine.Classes['CLASSES_System_Group']
        self.UserGroupClass = aICORDBEngine.Classes['CLASSES_System_GroupAccessLevel']
        self.ItemGroupClass = aICORDBEngine.Classes['CLASSES_System_GroupItemAccessLevel']
        self._params = {}
        self.ProfileOIDs = []
        self.isUserManager = 0
        self.isAccessRightsManager = 0
        if aname:
            self.SetByProfileName(aname)

    def SetByUser(self, auid=-1, agroups=0, anoprofile=0):
        if auid < 0:
            auid = GetUID()
        self.ProfileOIDs = []
        self.Users = None
        self.ItemGroups = None
        self.UsersID = None
        if agroups:
            self.Groups = {}
            self.GroupsID = {}
        else:
            self.Groups = None
            self.GroupsID = None
        self.ItemGroupsID = None
        if auid < 0:
            return
        self.UID = auid
        if not anoprofile:
            if aICORDBEngine._USER_PROFILES_CACHE.has_key(auid):
                self.ProfileOIDs = aICORDBEngine._USER_PROFILES_CACHE[auid][:]
            else:
                uobj = self.UserClass[auid]
                gobj = uobj.Groups
                while gobj:
                    pobj = gobj.Profile
                    if pobj and not pobj.OID in self.ProfileOIDs:
                        self.ProfileOIDs.append(pobj.OID)
                    gobj.Next()
                aICORDBEngine._USER_PROFILES_CACHE[auid] = self.ProfileOIDs[:]
        if agroups:
            self.GetUserGroupsOnly()

    def SetByProfileName(self, aname, aexcluded=None):
        if aexcluded is None:
            aexcluded = []
        self.ProfileOIDs = []
        self.Users = None
        self.Groups = None
        self.UsersID = None
        self.GroupsID = None
        if not aname:
            return 0
        if type(aname) == type(1):
            aoid = aname
        else:
            aoid = self.ProfileClass.Name.Identifiers(aname)
        if aoid < 0:
            return 0
        if self.ProfileClass.Name[aoid] in aexcluded:
            return 0
        self.ProfileOIDs.append(aoid)
        return 1

    def SetByAll(self, aexcluded=None):
        if aexcluded is None:
            aexcluded = EXCLUDED_PROFILES[:]
        self.ProfileOIDs = []
        self.Users = None
        self.Groups = None
        self.ItemGroups = None
        self.UsersID = None
        self.GroupsID = None
        self.ItemGroupsID = None
        pobj = self.ProfileClass.GetFirstObject()
        while pobj:
            if not pobj.Name in aexcluded:
                self.ProfileOIDs.append(pobj.OID)
            pobj.Next()

    def GetParams(self):
        dd = {}
        for poid in self.ProfileOIDs:
            sparms = self.ProfileClass.Parameters[poid]
            dd = ICORUtil.ParseVars(sparms, dd)
        return dd

    def GetParam(self, avalue, adefault=''):
        if self._params.has_key(avalue):
            return self._params[avalue]
        for poid in self.ProfileOIDs:
            sparms = self.ProfileClass.Parameters[poid]
            dd = ICORUtil.ParseVars(sparms)
            if dd.has_key(avalue):
                v = dd[avalue]
                self._params[avalue] = v
                return v
        self._params[avalue] = adefault
        return adefault

    def GetProfileObj(self):
        poid = self.ProfileOIDs[0]
        pobj = self.ProfileClass[poid]
        return pobj

    def GetItemGroups(self):
        self.ItemGroups = {}
        self.ItemGroupsID = {}
        for poid in self.ProfileOIDs:
            pobj = self.ProfileClass[poid]
            gobj = pobj.ItemGroups
            while gobj:
                gname = gobj.Name
                if not self.ItemGroups.has_key(gname):
                    agroup = ICORSecurityItemGroup(gobj.OID, gname)
                    self.ItemGroups[gname] = agroup
                    self.ItemGroupsID[gobj.OID] = agroup
                gobj.Next()

    def CheckAccessByRefs(self, parefs):
        if not parefs:
            return 1
        for poid in self.ProfileOIDs:
            pbrefs = self.ProfileClass.ItemGroups.GetRefList(poid)
            if parefs.RefsExists(pbrefs):
                return 1
        return 0

    def GetItemGroupsByUser(self):
        self.ItemGroups = {}
        self.ItemGroupsID = {}
        for poid in self.ProfileOIDs:
            pobj = self.ProfileClass[poid]
            gobj = pobj.ItemGroups
            while gobj:
                if CheckAccessLevelForUser(str(gobj.OID) + ':' + str(gobj.CID) + ':', self.UID):
                    gname = gobj.Name
                    if not self.ItemGroups.has_key(gname):
                        agroup = ICORSecurityItemGroup(gobj.OID, gname)
                        self.ItemGroups[gname] = agroup
                        self.ItemGroupsID[gobj.OID] = agroup
                gobj.Next()

    def GetUserGroupsOnly(self):
        self.isUserManager = 0
        self.isAccessRightsManager = 0
        if self.UID < 0:
            return
        gobj = self.UserClass[self.UID].Groups
        while gobj:
            if not self.GroupsID.has_key(gobj.OID):
                agroup = ICORSecurityUserGroup(gobj.OID)
                self.Groups[agroup.GroupName] = agroup
                self.GroupsID[gobj.OID] = agroup
                if agroup.GroupName == 'User Manager':
                    self.isUserManager = 1
                elif agroup.GroupName == 'Access Rights Manager':
                    self.isAccessRightsManager = 1
            gobj.Next()

    def GetUserGroups(self, aincludeuser=0):
        if self.Groups is not None:
            return self.Groups
        if self.Groups is None:
            self.Groups = {}
            self.GroupsID = {}
        for poid in self.ProfileOIDs:
            pobj = self.ProfileClass[poid]
            gobj = pobj.UserGroups
            while gobj:
                if not self.GroupsID.has_key(gobj.OID):
                    agroup = ICORSecurityUserGroup(gobj.OID)
                    self.Groups[agroup.GroupName] = agroup
                    self.GroupsID[gobj.OID] = agroup
                gobj.Next()
        if aincludeuser:
            self.GetUserGroupsOnly()
        return self.Groups

    def GetUsers(self):
        if self.Users is not None:
            return self.Users
        self.Users = {}
        self.UsersID = {}
        self.Groups = {}
        self.GroupsID = {}
        for poid in self.ProfileOIDs:
            pobj = self.ProfileClass[poid]
            gobj = pobj.UserGroups
            while gobj:
                gname = gobj.Name
                if not self.Groups.has_key(gname):
                    agroup = ICORSecurityUserGroup(gobj.OID, gname)
                    self.Groups[gname] = agroup
                    self.GroupsID[gobj.OID] = agroup
                uobj = gobj.Users
                while uobj:
                    uname = uobj.UserName
                    if not self.Users.has_key(uname):
                        auser = ICORSecurityUser(uobj.OID, uname)
                        self.Users[uname] = auser
                        self.UsersID[uobj.OID] = auser
                    uobj.Next()
                gobj.Next()
        return self.Users

    def GetNextFreeUID(self):
        for poid in self.ProfileOIDs:
            pobj = self.ProfileClass[poid]
            robj = pobj.UIDRange
            while robj:
                rmin = robj.Class.IDMin.ValuesAsInt(robj.OID)
                rmax = robj.Class.IDMax.ValuesAsInt(robj.OID)
                i = self.UserClass.GetNextFreeObjectID(rmin, rmax)
                if i >= 0:
                    return i
                robj.Next()
        return -1

    def GetNextFreeOID(self, aclass, adefault=None, auseronly=0):
        uobj = self.UserClass[self.UID]
        if uobj:
            robj = uobj.OIDRange
            while robj:
                adefault = -1
                rmin = robj.Class.IDMin.ValuesAsInt(robj.OID)
                rmax = robj.Class.IDMax.ValuesAsInt(robj.OID)
                i = aclass.GetNextFreeObjectID(rmin, rmax)
                if i >= 0:
                    return i
                robj.Next()
            if auseronly:
                return -1
            gobj = uobj.Groups
            while gobj:
                robj = gobj.OIDRange
                while robj:
                    adefault = -1
                    rmin = robj.Class.IDMin.ValuesAsInt(robj.OID)
                    rmax = robj.Class.IDMax.ValuesAsInt(robj.OID)
                    i = aclass.GetNextFreeObjectID(rmin, rmax)
                    if i >= 0:
                        return i
                    robj.Next()
                gobj.Next()
        if self.ProfileOIDs and not auseronly:
            for poid in self.ProfileOIDs:
                pobj = self.ProfileClass[poid]
                robj = pobj.OIDRange
                while robj:
                    adefault = -1
                    rmin = robj.Class.IDMin.ValuesAsInt(robj.OID)
                    rmax = robj.Class.IDMax.ValuesAsInt(robj.OID)
                    i = aclass.GetNextFreeObjectID(rmin, rmax)
                    if i >= 0:
                        return i
                    robj.Next()
        return adefault

    def AddProfile(self, aname):
        if aname in EXCLUDED_PROFILES:
            self.SetByProfileName(aname, aexcluded=EXCLUDED_PROFILES)
            return 0
        ret = 1
        aoid = self.ProfileClass.Name.Identifiers(aname)
        if aoid < 0:
            aoid = self.ProfileClass.AddObject()
            self.ProfileClass.Name[aoid] = aname
            ret = 0
        soid = self.StartupClass.FirstObject()
        self.StartupClass.ProfileGroup.AddRefs(soid, [aoid, self.ProfileClass.CID], asortedreffield=self.ProfileClass.Name, dosort=1, aremoveexisting=1)
        self.SetByProfileName(aname)
        return ret

    def NewOIDRange(self, aname):
        rclass = self.ProfileClass.OIDRange.ClassOfType
        roid = rclass.Name.Identifiers(aname)
        if roid < 0:
            roid = 287
            while 1:
                avalue = rclass.Name[roid]
                if not avalue:
                    break
                roid = roid + 1
            rclass.Name[roid] = aname
        return roid, rclass.CID

    def UpdateOIDRange(self, aname, nroid=-1, asobject=0):
        roid, rcid = -1, -1
        rclass = self.ProfileClass.OIDRange.ClassOfType
        if self.ProfileOIDs:
            if nroid >= 0:
                roid = nroid
                rcid = rclass.CID
                rclass.Name[roid] = aname
            else:
                roid, rcid = self.NewOIDRange(aname)
            for poid in self.ProfileOIDs:
                self.ProfileClass.OIDRange.AddRefs(poid, [roid, rcid], ainsertifnotexists=1)
        if asobject and (roid >= 0):
            return rclass[roid]
        return roid, rcid

    def UpdateUIDRange(self, aname, nroid=-1, asobject=0):
        roid = -1
        rclass = self.ProfileClass.UIDRange.ClassOfType
        if self.ProfileOIDs:
            if nroid >= 0:
                roid = nroid
            else:
                roid = rclass.Name.Identifiers(aname)
                if roid < 0:
                    roid = 75
                    while 1:
                        avalue = rclass.Name[roid]
                        if not avalue:
                            break
                        roid = roid + 1
            rclass.Name[roid] = aname
            for poid in self.ProfileOIDs:
                self.ProfileClass.UIDRange.AddRefs(poid, [roid, rclass.CID], ainsertifnotexists=1)
        if asobject and (roid >= 0):
            return rclass[roid]
        return roid

    def UpdateItemGroup(self, aname, aaccesslevel=-1, agroups=None, acategory='', akind=''):
        if not self.ProfileOIDs:
            return -1
        if agroups is None:
            agroups = []
        poid = self.ProfileOIDs[0]
        grefs = self.ProfileClass.ItemGroups.GetRefList(poid)
        apos, afind = grefs.FindRefByValue('Name', aname)
        gclass = self.ProfileClass.ItemGroups.ClassOfType
        if not afind:
            goid = gclass.Name.Identifiers(aname)
            if goid < 0:
                goid = gclass.AddObject()
                gclass.Name[goid] = aname
            print storageutil.CP1250_To_ASCII_Default('Nowa grupa: %s' % aname)
            self.ProfileClass.ItemGroups.AddRefs(poid, [goid, gclass.CID], asortedreffield=gclass.Name, dosort=1, aremoveexisting=1)
        else:
            goid, gcid = grefs[apos]
        gclass.Category[goid] = acategory
        gclass.Kind[goid] = akind
        if aaccesslevel >= 0:
            gclass.AccessLevel[goid] = str(aaccesslevel)
        rclass = gclass.Groups.ClassOfType
        igroups = []
        for gname in agroups:
            roid = rclass.Name.Identifiers(gname)
            if roid <= 0:
                roid = rclass.AddObject()
                rclass.Name[roid] = gname
            igroups.append([roid, rclass.CID])
        gclass.Groups[goid] = igroups
        return goid

    def RenameItemGroup(self, aname, anewname):
        if not self.ProfileOIDs:
            return
        poid = self.ProfileOIDs[0]
        grefs = self.ProfileClass.ItemGroups.GetRefList(poid)
        apos, afind = grefs.FindRefByValue('Name', aname)
        gclass = self.ProfileClass.ItemGroups.ClassOfType
        if not afind:
            goid = gclass.Name.Identifiers(aname)
        else:
            goid, gcid = grefs[apos]
        if goid >= 0 and anewname:
            gclass.Name[goid] = anewname
            brefs = gclass.Groups.GetRefList(goid)
            while brefs:
                if brefs.Name[brefs.OID] == aname:
                    brefs.Name[brefs.OID] = anewname
                brefs.Next()

    def UpdateUserGroup(self, aname, aaccesslevel=0, agroups=None, acategory='', akind=''):
        if not self.ProfileOIDs:
            return -1
        if agroups is None:
            agroups = []
        poid = self.ProfileOIDs[0]
        grefs = self.ProfileClass.UserGroups.GetRefList(poid)
        apos, afind = grefs.FindRefByValue('Name', aname)
        gclass = self.ProfileClass.UserGroups.ClassOfType
        if not afind:
            goid = gclass.Name.Identifiers(aname)
            if goid < 0:
                goid = gclass.AddObject()
                gclass.Name[goid] = aname
            self.ProfileClass.UserGroups.AddRefs(poid, [goid, gclass.CID], asortedreffield=gclass.Name, dosort=1, aremoveexisting=1)
        else:
            goid, gcid = grefs[apos]
        gclass.Category[goid] = acategory
        gclass.Kind[goid] = akind
        if aaccesslevel >= 0:
            gclass.AccessLevel[goid] = str(aaccesslevel)
        rclass = gclass.Groups.ClassOfType
        igroups = []
        for gname in agroups:
            roid = rclass.Name.Identifiers(gname)
            if roid <= 0:
                roid = rclass.AddObject()
                rclass.Name[roid] = gname
            igroups.append([roid, rclass.CID])
        gclass.Groups[goid] = igroups
        return goid

    def RenameUserGroup(self, aname, anewname):
        if not self.ProfileOIDs:
            return
        poid = self.ProfileOIDs[0]
        grefs = self.ProfileClass.UserGroups.GetRefList(poid)
        apos, afind = grefs.FindRefByValue('Name', aname)
        gclass = self.ProfileClass.UserGroups.ClassOfType
        if not afind:
            goid = gclass.Name.Identifiers(aname)
        else:
            goid, gcid = grefs[apos]
        if goid >= 0 and anewname:
            gclass.Name[goid] = anewname
            brefs = gclass.Groups.GetRefList(goid)
            while brefs:
                if brefs.Name[brefs.OID] == aname:
                    brefs.Name[brefs.OID] = anewname
                brefs.Next()

    def RenameBaseGroup(self, aname, anewname):
        goid = self.BaseGroupsClass.Name.Identifiers(aname)
        if goid >= 0 and anewname:
            gclass.Name[goid] = anewname

    def RemoveItemGroup(self, aname):
        if ICORUtil.strLowerPL(aname) in PROTECTED_GROUPS:
            return
        if not self.ProfileOIDs:
            return
        poid = self.ProfileOIDs[0]
        gclass = self.ProfileClass.ItemGroups.ClassOfType
        goid = gclass.Name.Identifiers(aname)
        if goid >= 0:
            self.ProfileClass.ItemGroups.DeleteRefs(poid, [goid, gclass.CID], aobjectdelete=1)

    def RemoveUserGroup(self, aname):
        if ICORUtil.strLowerPL(aname) in PROTECTED_GROUPS:
            return
        if not self.ProfileOIDs:
            return
        poid = self.ProfileOIDs[0]
        gclass = self.ProfileClass.UserGroups.ClassOfType
        goid = gclass.Name.Identifiers(aname)
        if goid >= 0:
            self.ProfileClass.UserGroups.DeleteRefs(poid, [goid, gclass.CID], aobjectdelete=1)

    def AddUserByAttrs(self, attrs, agroups=None, loidranges=None, avariables=None):
        aname = attrs.get('UserName', '')
        apassword = attrs.get('Password', '')
        apasswordhash = 1
        afirstname = attrs.get('VCFFirstName', '')
        alastname = attrs.get('VCFLastName', '')
        aemail = attrs.get('VCFEMail', '')
        aphone = attrs.get('VCFPhone', '')
        auid = int(attrs.get('UID', '-1'))
        aexpiration = attrs.get('PasswordExpiration', '')
        adescription = attrs.get('Description', '')
        if agroups is None:
            agroups = ''
        if loidranges is None:
            loidranges = []
        aaccountdisabled = ICORUtil.str2bool(attrs.get('AccountDisabled', ''))
        awwwdisabled = ICORUtil.str2bool(attrs.get('WWWDisabled', ''))
        apasswordmustchange = ICORUtil.str2bool(attrs.get('PasswordMustChange', ''))
        alastlogin = attrs.get('LastLogin', '')
        aparameters = attrs.get('Parameters', '')
        apasswordhistory = attrs.get('PasswordHistory', '')
        apasswordlastchanged = attrs.get('PasswordLastChanged', '')
        if avariables is None:
            avariables = []
        self.AddUser(aname, apassword, agroups, afirstname=afirstname, alastname=alastname, aemail=aemail, aphone=aphone, auid=auid, apasswordhash=apasswordhash, loidranges=loidranges, akeepoldpassword=0, aexpiration=aexpiration, adescription=adescription, aaccountdisabled=aaccountdisabled, awwwdisabled=awwwdisabled, apasswordmustchange=apasswordmustchange, alastlogin=alastlogin, aparameters=aparameters, apasswordhistory=apasswordhistory,
                     apasswordlastchanged=apasswordlastchanged, avariables=avariables)

    def AddUser(self, aname, apassword, agroups, afirstname=None, alastname=None, aemail=None, aphone=None, auid=-1, apasswordhash=0, loidranges=None, akeepoldpassword=0, aexpiration=None, adescription=None, aaccountdisabled=None, awwwdisabled=None, apasswordmustchange=None, alastlogin=None, aparameters=None, apasswordhistory=None, apasswordlastchanged=None, avariables=None):
        if loidranges is None:
            loidranges = []
        if auid < 0:
            isnew = 1
            auid = self.UserClass.UserName.Identifiers(aname)
            if auid < 0:
                auid = self.GetNextFreeUID()
                if auid < 0:
                    return 0
            else:
                isnew = 0
        else:
            isnew = 0
        print storageutil.CP1250_To_ASCII_Default('NOWY UZYTKOWNIK: %d %s' % (auid, aname))
        if auid < 100:
            raise ValueError
        self.UserClass.UserName[auid] = aname
        if akeepoldpassword and not isnew:
            pass
        elif apasswordhash:
            aICORDBEngine.UserVars['PasswordChange'] = 1
            try:
                self.UserClass.Password[auid] = apassword
            finally:
                aICORDBEngine.UserVars['PasswordChange'] = 0
        elif apassword:
            self.UserClass.Password[auid] = apassword
        grefs = self.UserClass.Groups.GetRefList(auid)
        grefs.clear()
        brefs = FieldRefIterator(agroups)
        grefs.AddRefs(brefs)
        grefs.Store()
        self.UserClass.Groups.UpdateReferencedObjects(auid, aupdaterefs=1)
        if afirstname is not None:
            self.UserClass.VCFFirstName[auid] = afirstname
        if alastname is not None:
            self.UserClass.VCFLastName[auid] = alastname
        if aemail is not None:
            self.UserClass.VCFEMail[auid] = aemail
        if aphone is not None:
            self.UserClass.VCFPhone[auid] = aphone
        if adescription is not None:
            self.UserClass.Description[auid] = adescription
        if aaccountdisabled is not None:
            self.UserClass.AccountDisabled[auid] = aaccountdisabled
        if awwwdisabled is not None:
            self.UserClass.WWWDisabled[auid] = awwwdisabled
        if apasswordmustchange is not None:
            self.UserClass.PasswordMustChange[auid] = apasswordmustchange
        if alastlogin is not None:
            self.UserClass.LastLogin[auid] = alastlogin
        if aparameters is not None:
            self.UserClass.Parameters[auid] = aparameters
        if apasswordhistory is not None:
            self.UserClass.PasswordHistory[auid] = apasswordhistory
        if apasswordlastchanged is not None:
            self.UserClass.PasswordLastChanged[auid] = apasswordlastchanged
        if aexpiration is not None:
            try:
                aexpiration = int(aexpiration)
            except:
                aexpiration = 0
            self.UserClass.PasswordExpiration[auid] = aexpiration
        if loidranges:
            self.UserClass.OIDRange[auid] = ''
            rclass = self.ProfileClass.OIDRange.ClassOfType
            for aname in loidranges:
                if isinstance(aname, types.StringTypes) and aname:
                    roid, rcid = self.NewOIDRange(aname)
                elif type(aname) == type(1) and aname >= 0:
                    roid, rcid = aname, rclass.CID
                if roid >= 0:
                    self.UserClass.OIDRange.AddRefs(auid, [roid, rcid], ainsertifnotexists=1)
        if avariables:
            vrefs = self.UserClass.UserVariables.GetRefList(auid)
            self.UserClass.UserVariables.DeleteRefs(auid, vrefs.AsListOIDCID(), aobjectdelete=1)
            vclass = self.UserClass.UserVariables.ClassOfType
            for aname, avalue in avariables:
                void = vclass.AddObject()
                vclass.Name[void] = aname
                vclass.Value[void] = avalue
                self.UserClass.UserVariables.AddRefs(auid, [void, vclass.CID], ainsertifnotexists=1)
        return 1

    def DumpXML(self, afile, auidranges=0, ausers=0, aoidranges=0):
        afile = XMLUtil.MXMLFile(afile, anopl=1, pathpriority='-')
        afile.Header()
        afile.TagOpen('SECURITY')
        #      aobj=self.ProfileClass.GetFirstObject()
        for poid in self.ProfileOIDs:
            aobj = self.ProfileClass[poid]
            if aobj.Name in EXCLUDED_PROFILES:
                continue
            wp = aobj.ItemGroups.Exists() or aobj.UIDRange.Exists() or aobj.UserGroups.Exists() or aobj.OIDRange.Exists()
            d = {'Name': aobj.Name, 'Parameters': aobj.Parameters}
            d['AccessLevelView'] = GetAccessLevelRefsAsString(self.ProfileClass.AccessLevelView.GetRefList(poid))
            afile.TagOpen('PROFILE', d, aclosetag=not wp)

            if aoidranges:
                bobj = aobj.OIDRange
                w = bobj.Exists()
                if w:
                    afile.TagOpen('OIDRANGES')
                while bobj:
                    d = {'OID': bobj.OID, 'Name': bobj.Name, 'IDMin': bobj.IDMin, 'IDMax': bobj.IDMax}
                    afile.TagOpen('OIDRANGE', d, aclosetag=1)
                    bobj.Next()
                if w:
                    afile.TagClose('OIDRANGES')

            bobj = aobj.ItemGroups
            w = bobj.Exists()
            if w:
                afile.TagOpen('ITEMGROUPS')
            while bobj:
                gobj = bobj.Groups
                wclosetag = 0
                if len(gobj) == 1 and gobj.Name == bobj.Name:
                    wclosetag = 1
                d = {'Name': bobj.Name, 'AccessLevel': bobj.AccessLevel, 'mode': 'update', 'category': bobj.Category, 'kind': bobj.Kind}
                afile.TagOpen('ITEMGROUP', d, aclosetag=wclosetag)
                if not wclosetag:
                    while gobj:
                        d = {'Name': gobj.Name, }
                        afile.TagOpen('ITEMBASEGROUP', d, aclosetag=1)
                        gobj.Next()
                    afile.TagClose('ITEMGROUP')
                bobj.Next()
            if w:
                afile.TagClose('ITEMGROUPS')

            bobj = aobj.UserGroups
            w = bobj.Exists()
            if w:
                afile.TagOpen('USERGROUPS')
            while bobj:
                wclosetag = 0
                gobj = bobj.Groups
                if len(gobj) == 1 and gobj.Name == bobj.Name:
                    wclosetag = 1
                d = {'Name': bobj.Name, 'AccessLevel': bobj.AccessLevel, 'mode': 'update', 'category': bobj.Category, 'kind': bobj.Kind}
                afile.TagOpen('USERGROUP', d, aclosetag=wclosetag)
                if not wclosetag:
                    while gobj:
                        d = {'Name': gobj.Name}
                        afile.TagOpen('USERBASEGROUP', d, aclosetag=1)
                        gobj.Next()
                if not wclosetag:
                    afile.TagClose('USERGROUP')
                bobj.Next()
            if w:
                afile.TagClose('USERGROUPS')

            if auidranges:
                bobj = aobj.UIDRange
                w = bobj.Exists()
                if w:
                    afile.TagOpen('UIDRANGES')
                while bobj:
                    d = {'OID': bobj.OID, 'Name': bobj.Name, 'IDMin': bobj.IDMin, 'IDMax': bobj.IDMax}
                    afile.TagOpen('UIDRANGE', d)
                    luids = self.UserClass.GetObjectsInRange(int(bobj.IDMin), int(bobj.IDMax))
                    if luids and ausers:
                        afile.TagOpen('USERS')
                        for guoid in luids:
                            gobj = self.UserClass[guoid]
                            d={
                               'UID':gobj.OID,
                               'UserName':gobj.UserName,
                               'Password':gobj.Password,
                               'AccountDisabled':gobj.AccountDisabled,
                               'Description':gobj.Description,
                               'WWWDisabled':gobj.WWWDisabled,
                               'LastLogin':gobj.LastLogin,
                               'Parameters':gobj.Parameters,
                               'PasswordExpiration':gobj.PasswordExpiration,
                               'PasswordHistory':gobj.PasswordHistory,
                               'PasswordLastChanged':gobj.PasswordLastChanged,
                               'PasswordMustChange':gobj.PasswordMustChange,
                               'VCFEMail':gobj.VCFEMail,
                               'VCFPhone':gobj.VCFPhone,
                               'VCFFirstName':gobj.VCFFirstName,
                               'VCFLastName':gobj.VCFLastName,
                            } # yapf: disable
                            afile.TagOpen('USER', d)
                            vobj = gobj.UserVariables
                            while vobj:
                                d = {'Name': vobj.Name, 'Value': vobj.Value}
                                afile.TagOpen('USERVARIABLE', d, aclosetag=1)
                                vobj.Next()
                            vobj = gobj.OIDRange
                            while vobj:
                                d = {'OID': vobj.OID, 'Name': vobj.Name, 'IDMin': vobj.IDMin, 'IDMax': vobj.IDMax}
                                afile.TagOpen('USEROIDRANGE', d, aclosetag=1)
                                vobj.Next()
                            afile.TagOpen('USERITEMGROUPS')
                            vobj = gobj.Groups
                            while vobj:
                                d = {'Name': vobj.Name}
                                afile.TagOpen('USERITEMGROUP', d, aclosetag=1)
                                vobj.Next()
                            afile.TagClose('USERITEMGROUPS')
                            afile.TagClose('USER')
                            gobj.Next()
                        afile.TagClose('USERS')
                    afile.TagClose('UIDRANGE')
                    bobj.Next()
                if w:
                    afile.TagClose('UIDRANGES')

            if wp:
                afile.TagClose('PROFILE')


#         aobj.Next()
        afile.TagClose('SECURITY')
        afile.close()


def RepairUsersInUserGroups(alog=None):
    if alog:
        alog.Log('RepairUsersInUserGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User
    for aoid in aclass:
        arefs = aclass.Groups.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairUsersInUserGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.Groups.UpdateReferencedObjects(aoid, 'Users', aupdaterefs=1)


def RepairUserGroupsInUsers(alog=None):
    if alog:
        alog.Log('RepairUserGroupsInUsers -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType
    for aoid in aclass:
        arefs = aclass.Users.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairUserGroupsInUsers check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.Users.UpdateReferencedObjects(aoid, 'Groups', aupdaterefs=1)


def RepairGroupsInUserGroups(alog=None):
    if alog:
        alog.Log('RepairGroupsInUserGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType
    for aoid in aclass:
        alog.Log('  %d %s: %s' % (aoid, aclass.Name[aoid], aclass.Groups[aoid]))
        arefs = aclass.Groups.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairGroupsInUserGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.Groups.UpdateReferencedObjects(aoid, 'GroupAccessLevels', aupdaterefs=1)


def RepairUserGroupsInGroups(alog=None):
    if alog:
        alog.Log('RepairUserGroupsInGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType.Groups.ClassOfType
    for aoid in aclass:
        arefs = aclass.GroupAccessLevels.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairUserGroupsInGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.GroupAccessLevels.UpdateReferencedObjects(aoid, 'Groups', aupdaterefs=1)


def RepairItemGroupsInGroups(alog=None):
    if alog:
        alog.Log('RepairItemGroupsInGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType.Groups.ClassOfType
    for aoid in aclass:
        arefs = aclass.GroupItemAccessLevels.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairItemGroupsInGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.GroupItemAccessLevels.UpdateReferencedObjects(aoid, 'Groups', aupdaterefs=1)


def RepairGroupsInItemGroups(alog=None):
    if alog:
        alog.Log('RepairGroupsInItemGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType.Groups.ClassOfType.GroupItemAccessLevels.ClassOfType
    for aoid in aclass:
        arefs = aclass.Groups.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairGroupsInItemGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.Groups.UpdateReferencedObjects(aoid, 'GroupItemAccessLevels', aupdaterefs=1)


def RepairProfileInUserGroups(alog=None):
    if alog:
        alog.Log('RepairProfileInUserGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType
    for aoid in aclass:
        arefs = aclass.Profile.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairProfileInUserGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.Profile.UpdateReferencedObjects(aoid, 'UserGroups', aupdaterefs=1)


def RepairProfileInItemGroups(alog=None):
    if alog:
        alog.Log('RepairProfileInUserGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType.Groups.ClassOfType.GroupItemAccessLevels.ClassOfType
    for aoid in aclass:
        arefs = aclass.Profile.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairProfileInUserGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.Profile.UpdateReferencedObjects(aoid, 'ItemGroups', aupdaterefs=1)


def RepairUserGroupsInProfile(alog=None):
    if alog:
        alog.Log('RepairProfileInUserGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType.Profile.ClassOfType
    for aoid in aclass:
        arefs = aclass.UserGroups.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairProfileInUserGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.UserGroups.UpdateReferencedObjects(aoid, 'Profile', aupdaterefs=1)


def RepairItemGroupsInProfile(alog=None):
    if alog:
        alog.Log('RepairProfileInUserGroups -------------------', aconsole=1)
    aclass = aICORDBEngine.User.Groups.ClassOfType.Profile.ClassOfType
    for aoid in aclass:
        arefs = aclass.ItemGroups.GetRefList(aoid)
        w, l, lb = arefs.CheckRefs(aexists=1, astore=1)
        if w and alog:
            alog.Log('RepairProfileInUserGroups check: %d (%d/%d) - bad: %s !!! old: %s' % (aoid, len(lb), len(l), str(lb), str(l)))
        aclass.ItemGroups.UpdateReferencedObjects(aoid, 'Profile', aupdaterefs=1)


def RemoveUsersFromBadProfiles():
    aclass = aICORDBEngine.User
    aobj = aclass.GetFirstObject()
    while aobj.Exists():
        gobj = aobj.Groups
        while gobj:
            ugrefs = gobj.Class.Users.GetRefList(gobj.OID)
            if not ugrefs.RefExists(aobj.OID, aobj.CID):
                print storageutil.CP1250_To_ASCII_Default('uzytkownik %s nie występuje w %s' % (aobj.UserName, gobj.Name))
            gobj.Next()
        aobj.Next()


def GetAccessLevelRefsAsString(arefs, ajoinchar=chr(10)):
    lgroups = []
    while arefs:
        lgroups.append(arefs.Name[arefs.OID])
        arefs.Next()
    return string.join(lgroups, ajoinchar)


def GetStringAsAccessLevelRefs(astr, sclass=None, asplitchar=chr(10), ausergroups=0):
    if sclass is None:
        if ausergroups:
            sclass = aICORDBEngine.Classes['CLASSES_System_GroupAccessLevel']
        else:
            sclass = aICORDBEngine.Classes['CLASSES_System_GroupItemAccessLevel']
    if isinstance(astr, types.StringTypes) and (string.find(astr, ':399:') > 0 or string.find(astr, ':401:') > 0):
        arefs = FieldRefIterator(astr)
    else:
        arefs = FieldRefIterator()
        if astr:
            if isinstance(astr, types.StringTypes):
                l = string.split(astr, asplitchar)
            else:
                l = astr
        #   print 'GetStringAsAccessLevelRefs:',l,'"',astr,'"'
            for s in l:
                if s == 'Administrator Projektów':
                    s = 'Access Rights Manager'
                aoid = sclass.Name.Identifiers(s)
                if aoid >= 0:
                    arefs.AddRef(aoid, sclass.CID)
                else:
                    print storageutil.CP1250_To_ASCII_Default('Unknown reference "%s" in class "%s"' % (s, sclass.NameOfClass))
    return arefs
