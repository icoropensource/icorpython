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

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.icorsecurity as ICORSecurity
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.wwwserver.icorwwwinterface as ICORWWWInterface


class CacheItem(object):

    def __init__(self):
        pass


class ImpExJSONIterator(object):

    def __init__(self, aindent=0, abackref=0, UID=-1):
        if aindent:
            self.indent = 2
        else:
            self.indent = None
        self.backref = abackref
        self.uid = UID
        self.info = {}
        self.data = []
        self.drecur = {}
        self._cacheitems = {}

    def AsString(self):
        d = {'info': self.info, 'data': self.data}
        s = json.dumps(d, sort_keys=True, indent=self.indent)
        return s

    def ProcessExport(self, aobj):
        if not aobj:
            return
        self.info['_OID'] = aobj.OID
        self.info['_CID'] = aobj.CID
        self.GetObjectAsJSON(aobj)

    def GetObjectAsJSON(self, aobj):
        UID = self.uid
        aoid = aobj.OID
        acid = aobj.CID
        vk = '%d:%d:' % (aobj.CID, aoid)
        if self.drecur.has_key(vk):
            return
        self.drecur[vk] = 1
        aclass = aobj.Class

        classcacheitem = self._cacheitems.get(acid, None)
        if classcacheitem is None:
            classcacheitem = CacheItem()
            self._cacheitems[acid] = classcacheitem
            classcacheitem.aclass = aclass
            classcacheitem.methodOnClassImport = classcacheitem.aclass.MethodsByName('OnClassImport')
            if classcacheitem.methodOnClassImport is not None:
                dcontext = {'_AllowClassImport': 1}
                classcacheitem.methodOnClassImport.Execute('', -1, '0', acontext=dcontext)
                if dcontext['_AllowClassImport'] != 1:
                    classcacheitem.aclass = None
                    classcacheitem.methodOnClassImport = None
                    return
            classcacheitem.methodOnFieldImport = classcacheitem.aclass.MethodsByName('OnFieldImport')
            classcacheitem.methodOnObjectImport = classcacheitem.aclass.MethodsByName('OnObjectImport')
        if classcacheitem.aclass is None:
            return

        d = {'_CID': aobj.CID, '_OID': aoid, '_ClassPath': aobj.Class.ClassPath}
        for fname in aclass.GetFieldsList():
            afield = aclass.FieldsByName(fname)
            if afield.IsVirtual == '1':
                continue

            if fname == 'Password' and classcacheitem.aclass.CID == ICORInterface.aICORDBEngine.User.CID:
                ICORInterface.aICORDBEngine.UserVars['PasswordChange'] = 1
            else:
                ICORInterface.aICORDBEngine.UserVars['PasswordChange'] = 0
            fkey = (classcacheitem.aclass.CID, fname)
            fieldcacheitem = self._cacheitems.get(fkey, None)
            if fieldcacheitem is None:
                fieldcacheitem = CacheItem()
                self._cacheitems[fkey] = fieldcacheitem
                fieldcacheitem.afield = afield
                fieldcacheitem.wupdaterefs = 0
                if classcacheitem.methodOnFieldImport is not None:
                    dcontext = {'_AllowFieldImport': 1}
                    classcacheitem.methodOnFieldImport.Execute(FieldName=fieldcacheitem.afield.Name, acontext=dcontext)
                    if dcontext['_AllowFieldImport'] != 1:
                        fieldcacheitem.afield = None
                        continue
                    ret = classcacheitem.methodOnFieldImport.Execute(FieldName=fieldcacheitem.afield.Name, Value='updaterefs')
                    if type(ret) == type(1) and ret == 1:
                        fieldcacheitem.wupdaterefs = 1

            v = afield.ValuesAsComp(aoid, ajsonfriendly=1)

            wu = 1
            if wu and (classcacheitem.methodOnObjectImport is not None):
                dcontext = {'_AllowObjectImport': 1, '_ObjectImportValue': v, }
                classcacheitem.methodOnObjectImport.Execute(fieldcacheitem.afield.Name, aoid, acontext=dcontext)
                if dcontext['_AllowObjectImport'] != 1:
                    wu = 0
                    continue
                else:
                    v = dcontext['_ObjectImportValue']

            if type(v) in [type(''), type(u'')]:
                v = storageutil.ASCII_CP1250_To_UTF8(v)
            d[fname] = v

            if not self.backref and afield.WWWBackRefField:
                continue
            if afield.FieldTID > ICORInterface.MAX_ICOR_SYSTEM_TYPE:
                bobj = afield.GetRefList(aoid).AsObject()
                while bobj:
                    self.GetObjectAsJSON(bobj)
                    bobj.Next()
        self.data.append(d)

    def ProcessImport(self, aobj, afilename, file):
        UID = self.uid
        afpath = startutil.appconfig.ICORBaseDir + '/wwwroot/output/' + afilename
        try:
            dd = storageutil.JSONLoad(afpath)
        except:
            file.write('<h3>błąd dostępu do pliku</h3>')
            import traceback
            file.write('<pre>')
            traceback.print_exc(file=file)
            file.write('</pre>')
            return
        dinfo = dd['info']
        ldata = dd['data']
        lfieldupdates = []
        file.write('<h3>Import: cid=%d, oid=%d</h3>\n' % (dinfo['_CID'], dinfo['_OID']))
        for d in ldata:
            aclass = ICORInterface.aICORDBEngine.Classes[d['_ClassPath']]
            acid, aoid = d['_CID'], d['_OID']
            if not aclass.ObjectExists(aoid):
                file.write('<h4>----object does not exists: cid=%d, oid=%d</h4>\n' % (dinfo['_CID'], dinfo['_OID']))
            for afieldname in d.keys():
                if afieldname[:1] == '_':
                    continue
                afield = aclass.FieldsByName(afieldname)
                vo = afield.ValuesAsComp(aoid, ajsonfriendly=1)
                vn = d[afieldname]
                if vo != vn:
                    file.write('<h4>----field value different: cid=%d, oid=%d, field: %s</h4>\n' % (acid, aoid, afieldname))

    def Dump(self):
        v = self.AsString()
        fname = startutil.GetLogTempFileName('output', aprefix='objexport', asufix='', avalue=v, atrace=0, abasedir=startutil.appconfig.ICORBaseDir + '/wwwroot', aext='json', returnfilenameonly=1)
        return fname


def ExportJSON(aobj=None, UID=-1, aindent=0, abackref=0, file=None):
    if file is None:
        return
    if aobj is None:
        file.write('Nieprawidłowy obiekt')
        return
    if UID < 0:
        file.write('Nieprawidłowy użytkownik')
        return
    aiterator = ImpExJSONIterator(aindent=aindent, abackref=abackref, UID=UID)
    aiterator.ProcessExport(aobj)
    afname = aiterator.Dump()
    file.write('<br><br>Plik JSON z danymi: <a target="_blank" href="/icormanager/output/%s">%s</a><hr>' % (afname, afname))
    #file.write('<textarea rows="40" cols="80">')
    #file.write(aiterator.AsString())
    #file.write('</textarea>')


def ImportJSON(aobj=None, UID=-1, afilename='', abackref=0, file=None):
    if file is None:
        return
    if aobj is None:
        file.write('Nieprawidłowy obiekt')
        return
    if UID < 0:
        file.write('Nieprawidłowy użytkownik')
        return
    aiterator = ImpExJSONIterator(abackref=abackref, UID=UID)
    aiterator.ProcessImport(aobj, afilename, file)
    #file.write('<br><br>Plik JSON z danymi: <a target="_blank" href="/icormanager/output/%s">%s</a><hr>'%(afname,afname))
