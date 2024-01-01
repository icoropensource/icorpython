# -*- coding: utf-8 -*-
import os
import re
import string
import xmllib    #from xml.parsers

from icorlib.icorinterface import *
from CLASSES_Library_ICORBase_Interface_ICORUtil import *
from icorlib.icoriterators import FieldRefIterator
from CLASSES_Library_NetBase_Utils_XMLUtil import *
from CLASSES_Library_ICORBase_Interface_ICORTextFile import TextFile
import icorlib.icorsecurity as ICORSecurity

import icorexceptions

NO_STRUCTURE_IMPORT = 1

TRANSLATE_OID = [
    #[51000,52000,11000],
]

TRANSLATE_VALUE = [
    #['from','to'],
]


def GetListAsDateTuple(alist, x=0):
    return (int(alist[x]), int(alist[x + 1]), int(alist[x + 2]), int(alist[x + 3]), int(alist[x + 4]), int(alist[x + 5]), int(alist[x + 6]))


class CacheItem(object):

    def __init__(self):
        pass


class ICORXMLReplicationParser(xmllib.XMLParser):

    def __init__(self, aprofile, adisableobjectschange=0):
        xmllib.XMLParser.__init__(self, accept_utf8=1, accept_unquoted_attributes=1, accept_missing_endtag_name=1)
        self.ProfileClass = aICORDBEngine.Classes['CLASSES/Library/ICORBase/Replication/Receive']
        if self.ProfileClass is None:
            raise icorexceptions.ICORExceptionReplication('Profile class does not exists')
        if type(aprofile) == type(1):
            self.OID = aprofile
        else:
            self.OID = self.ProfileClass.Name.Identifiers(aprofile)
        if self.OID < 0:
            raise icorexceptions.ICORExceptionReplication('Profile does not exists')
        self.disableobjectschange = adisableobjectschange
        c1 = aICORDBEngine.Classes['CLASSES_System_GroupAccessLevel']
        c2 = aICORDBEngine.Classes['CLASSES_System_GroupItemAccessLevel']
        self.dACL_CIDs = {c1.CID: c1, c2.CID: c2}
        self.afile = self.ProfileClass.InputFile[self.OID]
        self._cacheitems = {}

    def Parse(self, fname=''):
        self.reset()
        self.elements = {}
        self.elements['REPLICATION'] = (self.start_REPLICATION, self.end_REPLICATION)
        self.elements['HEADER'] = (self.start_HEADER, self.end_HEADER)
        self.elements['DATA'] = (self.start_DATA, self.end_DATA)
        self.elements['FIELDVALUE'] = (self.start_FIELDVALUE, self.end_FIELDVALUE)
        if fname != '':
            self.afile = fname
        if not self.afile:
            raise icorexceptions.ICORExceptionReplication('No file')
        self.afile = FilePathAsSystemPath(self.afile)
        if self.afile[-3:] != '.gz':
            self.afile = self.afile + '.gz'
        self.avalueline = ''
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

    def start_REPLICATION(self, attrs):
        pass

    def end_REPLICATION(self):
        pass

    def start_HEADER(self, attrs):
        pass

    def end_HEADER(self):
        pass

    def start_CLASS(self, attrs):
        acpath, acid = attrs.get('ClassPath', ''), int(attrs['CID'])
        self.classcacheitem = self._cacheitems.get(acpath, None)
        if self.classcacheitem is None:
            self.classcacheitem = CacheItem()
            self._cacheitems[acpath] = self.classcacheitem
            self.classcacheitem.aclass = aICORDBEngine.Classes[acpath]
            if self.classcacheitem.aclass is None:
                print '*** Class: %s [%d] is None! ***' % (acpath, acid)
                return
            self.classcacheitem.methodOnClassImport = self.classcacheitem.aclass.MethodsByName('OnClassImport')
            if self.classcacheitem.methodOnClassImport is not None:
                dcontext = {'_AllowClassImport': 1}
                self.classcacheitem.methodOnClassImport.Execute('', -1, '0', acontext=dcontext)
                if dcontext['_AllowClassImport'] != 1:
                    self.classcacheitem.aclass = None
                    self.classcacheitem.methodOnClassImport = None
                    return
            self.classcacheitem.methodOnFieldImport = self.classcacheitem.aclass.MethodsByName('OnFieldImport')
            self.classcacheitem.methodOnObjectImport = self.classcacheitem.aclass.MethodsByName('OnObjectImport')

    def start_FIELD(self, attrs):
        if self.classcacheitem.aclass is None:
            return
        fname = attrs['Name']
        if fname == 'Password' and self.classcacheitem.aclass.CID == aICORDBEngine.User.CID:
            aICORDBEngine.UserVars['PasswordChange'] = 1
        else:
            aICORDBEngine.UserVars['PasswordChange'] = 0
        fkey = (self.classcacheitem.aclass.CID, fname)
        self.fieldcacheitem = self._cacheitems.get(fkey, None)
        if self.fieldcacheitem is None:
            self.fieldcacheitem = CacheItem()
            self._cacheitems[fkey] = self.fieldcacheitem
            self.fieldcacheitem.afield = self.classcacheitem.aclass.FieldsByName(fname)
            if self.fieldcacheitem.afield is not None:
                self.fieldcacheitem.wupdaterefs = 0
                if self.classcacheitem.methodOnFieldImport is not None:
                    dcontext = {'_AllowFieldImport': 1}
                    self.classcacheitem.methodOnFieldImport.Execute(FieldName=self.fieldcacheitem.afield.Name, acontext=dcontext)
                    if dcontext['_AllowFieldImport'] != 1:
                        self.fieldcacheitem.afield = None
                        return
                    ret = self.classcacheitem.methodOnFieldImport.Execute(FieldName=self.fieldcacheitem.afield.Name, Value='updaterefs')
                    if type(ret) == type(1) and ret == 1:
                        self.fieldcacheitem.wupdaterefs = 1

    def TranslateOID(self, aoid):
        for aoidmin, aoidmax, aadd in TRANSLATE_OID:
            if aoid >= aoidmin and aoid < aoidmax:
                aoid = aoid + aadd
                break
        return aoid

    def TranslateValue(self, avalue):
        for s1, s2 in TRANSLATE_VALUE:
            avalue = avalue.replace(s1, s2)
        return avalue

    def start_OBJECT(self, attrs):
        if self.fieldcacheitem.afield is None:
            return
        self.aoid = self.TranslateOID(int(attrs['OID']))
        #alm=string.split(attrs['LastModification'],' ')
        #self.adtobject=GetListAsDateTuple(alm)
        self.avalue = ''

    def start_FIELDVALUE(self, attrs):
        self.start_CLASS(attrs)
        self.start_FIELD(attrs)
        self.start_OBJECT(attrs)

    def start_DATA(self, attrs):
        self.avalueline = ''

    def handle_data(self, data):
        self.avalueline = self.avalueline + data

    def end_DATA(self):
        if self.avalue == '':
            self.avalue = self.avalueline
        else:
            self.avalue = self.avalue + '\n' + self.avalueline

    def end_OBJECT(self):
        if self.classcacheitem.aclass is None:
            return
        if self.fieldcacheitem.afield is None:
            return
        if self.fieldcacheitem.afield.ClassOfType is not None and self.dACL_CIDs.has_key(self.fieldcacheitem.afield.ClassOfType.CID):
            arefs = ICORSecurity.GetStringAsAccessLevelRefs(self.avalue, self.dACL_CIDs[self.fieldcacheitem.afield.ClassOfType.CID])
            self.avalue = arefs.AsString()
        elif self.fieldcacheitem.afield.ClassOfType is not None:
            acid = self.fieldcacheitem.afield.ClassOfType.CID
            arefs = FieldRefIterator(self.avalue)
            for i in range(len(arefs.refs)):
                arefs.refs[i][0] = self.TranslateOID(arefs.refs[i][0])
                arefs.refs[i][1] = acid
            self.avalue = arefs.AsString()
        else:
            self.avalue = self.TranslateValue(self.avalue)
        wu = 1
        if wu and (self.classcacheitem.methodOnObjectImport is not None):
            dcontext = {
                '_AllowObjectImport': 1,
                '_ObjectImportValue': self.avalue,
            #'_ObjectImportDate':tdatetime2fmtstr(self.adtobject),
            }
            self.classcacheitem.methodOnObjectImport.Execute(self.fieldcacheitem.afield.Name, self.aoid, acontext=dcontext)
            if dcontext['_AllowObjectImport'] != 1:
                wu = 0
            else:
                self.avalue = dcontext['_ObjectImportValue']
        if self.disableobjectschange:
            return
        if wu:
            if not self.classcacheitem.aclass.ObjectExists(self.aoid):
                self.classcacheitem.aclass.CreateObjectByID(self.aoid)
            if self.fieldcacheitem.wupdaterefs and self.fieldcacheitem.afield.ClassOfType is not None:
                self.fieldcacheitem.afield.AddRefs(self.aoid, arefs.refs, ainsertifnotexists=1)
            else:
                try:
                    self.fieldcacheitem.afield[self.aoid] = self.avalue
                except UnicodeDecodeError:
                    print 'VALUE UNICODE ERROR: %s - %s - %d' % (self.classcacheitem.aclass.ClassPath, self.fieldcacheitem.afield.Name, self.aoid)
                except:
                    print 'VALUE ERROR: %s - %s - %d' % (self.classcacheitem.aclass.ClassPath, self.fieldcacheitem.afield.Name, self.aoid)

    def end_FIELDVALUE(self):
        self.end_OBJECT()
        self.end_FIELD()
        self.end_CLASS()

    def end_FIELD(self):
        pass

    def end_CLASS(self):
        aICORDBEngine.UserVars['PasswordChange'] = 0

    def syntax_error(self, lineno, message):
        print 'error in data at line %d:' % lineno, message

    def unknown_starttag(self, tag, attrs):
        print 'unknown starttag:', tag

    def unknown_endtag(self, tag):
        print 'unknown endtag:', tag

    def unknown_entityref(self, ref):
        print 'unknown entityref:', ref

    def unknown_charref(self, ref):
        print 'unknown charref:', ref
