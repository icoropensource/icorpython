# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
from CLASSES_Library_ICORBase_Interface_ICORTextFile import TextFile
import icorlib.icorsecurity as ICORSecurity
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import xmllib    #from xml.parsers
import os

import icorexceptions


class ICORXMLSecurityReplicationParser(XMLUtil.ICORBaseXMLParser):

    def Parse(self, atext='', fname=''):
        if atext:
            XMLUtil.ICORBaseXMLParser.Parse(self, atext)
        else:
            if fname != '':
                self.afile = fname
            if self.afile == '':
                raise icorexceptions.ICORExceptionReplication('No file')
            self.afile = FilePathAsSystemPath(self.afile)
            fsize = os.path.getsize(self.afile)
            f = TextFile(self.afile, 'r')
            i = 0
            try:
                s = f.readline()
                while s != '':
                    self.feed(s[:-1])
                    i = i + 1
                    if i >= 120:
                        i = 0
                        apos = f.tell()
                        SetProgress(apos, fsize)
                    s = f.readline()
                self.close()
            finally:
                f.close()
                SetProgress(0, 0)

    def start_SECURITY(self, attrs):
        self.ElementInfo()

    def end_SECURITY(self):
        pass

    def start_PROFILE(self, attrs):
        self.ElementInfo(attrs.get('Name', ''), astatus=1)
        if attrs.get('Name', ''):
            self.secprofile = ICORSecurity.ICORSecurityProfile()
            ret = self.secprofile.SetByProfileName(attrs['Name'], aexcluded=ICORSecurity.EXCLUDED_PROFILES)
            self.secprofile.AddProfile(attrs['Name'])
            self.profileAccessLevelView = attrs.get('AccessLevelView', '')
        else:
            raise icorexceptions.ICORExceptionReplication('Bad XML Profile tag. Missing name.')

    def end_PROFILE(self):
        if self.profileAccessLevelView:
            arefs = ICORSecurity.GetStringAsAccessLevelRefs(self.profileAccessLevelView, ausergroups=1)
            self.secprofile.ProfileClass.AccessLevelView[self.secprofile.ProfileOIDs[0]] = arefs.AsString()

    def start_ITEMGROUPS(self, attrs):
        pass

    def end_ITEMGROUPS(self):
        pass

    def start_ITEMGROUP(self, attrs):
        self.ElementInfo(attrs.get('Name', ''), astatus=1)
        if attrs.get('Name', ''):
            self.groupname = attrs['Name']
            self.groupcategory = attrs.get('category', '')
            self.groupkind = attrs.get('kind', '')
            self.groupaccesslevel = int(attrs.get('AccessLevel', '0'))
            self.newname = attrs.get('NewName', '')
            self.mode = attrs.get('mode', '')
            self.basegroups = []
        else:
            raise icorexceptions.ICORExceptionReplication('Bad XML ItemGroup tag. Missing name.')

    def end_ITEMGROUP(self):
        if not self.basegroups:
            self.basegroups.append(self.groupname)
        if self.mode == 'update':
            self.secprofile.UpdateItemGroup(self.groupname, self.groupaccesslevel, self.basegroups, acategory=self.groupcategory, akind=self.groupkind)
        elif self.mode == 'delete':
            if ICORUtil.strLowerPL(self.groupname) in ICORSecurity.PROTECTED_GROUPS:
                return
            self.secprofile.RemoveItemGroup(self.groupname)
        elif self.mode == 'rename':
            self.secprofile.RenameItemGroup(self.groupname, self.newname)

    def start_ITEMBASEGROUP(self, attrs):
        aname = attrs.get('Name', '')
        self.basegroups.append(aname)
        amode = attrs.get('mode', '')
        if amode == 'rename':
            self.secprofile.RenameBaseGroup(aname, attrs.get('NewName', ''))

    def end_ITEMBASEGROUP(self):
        pass

    def start_OIDRANGES(self, attrs):
        pass

    def end_OIDRANGES(self):
        pass

    def start_OIDRANGE(self, attrs):
        self.idmax = int(attrs.get('IDMax', '-1'))
        self.idmin = int(attrs.get('IDMin', '-1'))
        self.oidrangeoid = int(attrs.get('OID', '-1'))
        self.oidrangename = attrs.get('Name', '')
        if self.idmax < 0 or self.idmin < 0 or not self.oidrangename:
            raise icorexceptions.ICORExceptionReplication('Bad OIDRange parameters: idmin,idmax,name in %s - %d' % (self.oidrangename, self.oidrangeoid))
        rclass = self.secprofile.ProfileClass.OIDRange.ClassOfType
        roid = rclass.Name.Identifiers(self.oidrangename)
        if roid < 0:
            bname = rclass.Name[self.oidrangeoid]
            if bname != '' and bname != self.oidrangename:
                raise icorexceptions.ICORExceptionReplication('Bad OIDRange parameters: existing name is different in %s - %d - %s' % (self.oidrangename, self.oidrangeoid, bname))
        else:
            if roid != self.oidrangeoid:
                raise icorexceptions.ICORExceptionReplication('Bad OIDRange parameters: existing oid is different in %s - %d - %d' % (self.oidrangename, self.oidrangeoid, roid))
        self.secprofile.UpdateOIDRange(self.oidrangename, self.oidrangeoid)

    def end_OIDRANGE(self):
        pass

    def start_UIDRANGES(self, attrs):
        pass

    def end_UIDRANGES(self):
        pass

    def start_UIDRANGE(self, attrs):
        self.idmax = int(attrs.get('IDMax', '-1'))
        self.idmin = int(attrs.get('IDMin', '-1'))
        self.oidrangeoid = int(attrs.get('OID', '-1'))
        self.oidrangename = attrs.get('Name', '')
        if self.idmax < 0 or self.idmin < 0 or not self.oidrangename:
            raise icorexceptions.ICORExceptionReplication('Bad UIDRange parameters: idmin,idmax,name in %s - %d' % (self.oidrangename, self.oidrangeoid))
        rclass = self.secprofile.ProfileClass.UIDRange.ClassOfType
        roid = rclass.Name.Identifiers(self.oidrangename)
        if roid < 0:
            bname = rclass.Name[self.oidrangeoid]
            if bname != '' and bname != self.oidrangename:
                raise icorexceptions.ICORExceptionReplication('Bad UIDRange parameters: existing name is different in %s - %d - %s' % (self.oidrangename, self.oidrangeoid, bname))
        else:
            if roid != self.oidrangeoid:
                raise icorexceptions.ICORExceptionReplication('Bad UIDRange parameters: existing oid is different in %s - %d - %d' % (self.oidrangename, self.oidrangeoid, roid))
        self.secprofile.UpdateUIDRange(self.oidrangename, self.oidrangeoid)

    def end_UIDRANGE(self):
        pass

    def start_USERGROUPS(self, attrs):
        pass

    def end_USERGROUPS(self):
        pass

    def start_USERGROUP(self, attrs):
        self.ElementInfo(attrs.get('Name', ''), astatus=1)
        if attrs.get('Name', ''):
            self.groupname = attrs['Name']
            self.groupcategory = attrs.get('category', '')
            self.groupkind = attrs.get('kind', '')
            self.groupaccesslevel = int(attrs.get('AccessLevel', '0'))
            self.newname = attrs.get('NewName', '')
            self.mode = attrs.get('mode', '')
            self.basegroups = []
        else:
            raise icorexceptions.ICORExceptionReplication('Bad XML UserGroup tag. Missing name.')

    def end_USERGROUP(self):
        if not self.basegroups:
            self.basegroups.append(self.groupname)
        if self.mode == 'update':
            self.secprofile.UpdateUserGroup(self.groupname, self.groupaccesslevel, self.basegroups, acategory=self.groupcategory, akind=self.groupkind)
        elif self.mode == 'delete':
            if ICORUtil.strLowerPL(self.groupname) in ICORSecurity.PROTECTED_GROUPS:
                return
            self.secprofile.RemoveUserGroup(self.groupname)
        elif self.mode == 'rename':
            self.secprofile.RenameUserGroup(self.groupname, self.newname)

    def start_USERBASEGROUP(self, attrs):
        self.basegroups.append(attrs.get('Name', ''))

    def end_USERBASEGROUP(self):
        pass

    def start_USERS(self, attrs):
        pass

    def end_USERS(self):
        pass

    def start_USER(self, attrs):
        self.duser = {}
        self.duser.update(attrs)
        self.ugroups = ''
        self.uoidranges = []
        self.uvariables = []

    def start_USERVARIABLE(self, attrs):
        self.uvariables.append([attrs.get('Name', ''), attrs.get('Value', '')])

    def start_USEROIDRANGE(self, attrs):
        self.uoidranges.append(int(attrs.get('OID', '-1')))

    def start_USERITEMGROUP(self, attrs):
        sclass = aICORDBEngine.Classes['CLASSES_System_GroupAccessLevel']
        gname = attrs.get('Name', '')
        if not gname:
            return
        goid = sclass.Name.Identifiers(gname)
        if goid < 0:
            return
        self.ugroups = self.ugroups + '%d:%d:' % (goid, sclass.CID)

    def end_USER(self):
        self.secprofile.AddUserByAttrs(self.duser, agroups=self.ugroups, loidranges=self.uoidranges, avariables=self.uvariables)

    def start_USERVARIABLE(self, attrs):
        pass

    def end_USERVARIABLE(self):
        pass


def SecurityLoad(afile):
    afile = FilePathAsSystemPath(afile)
    aparser = ICORXMLSecurityReplicationParser()
    aparser.Parse('', afile)
